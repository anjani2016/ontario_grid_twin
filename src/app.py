import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
import numpy as np
import os
import plotly.express as px
from engine.grid_model import GridNode

# Page Configuration
st.set_page_config(page_title="Ontario Grid Digital Twin", layout="wide")

# --- 1. Shared Data Loading ---
@st.cache_data
def load_data():
    subs_path = 'data/processed/analyzed_substations.parquet'
    lines_path = 'data/raw/ontario_lines.parquet'
    gen_path = 'data/raw/generation_sources.parquet'
    dc_path = 'data/raw/existing_dc.parquet'
    
    # Substations (Always required)
    subs = gpd.read_parquet(subs_path).to_crs(epsg=4326)
    subs['lon'] = subs.geometry.x
    subs['lat'] = subs.geometry.y
    
    # Optional files but critical for full functionality
    if os.path.exists(lines_path):
        lines = gpd.read_parquet(lines_path).to_crs(epsg=4326)
    else:
        lines = None
        
    if os.path.exists(gen_path):
        gen = gpd.read_parquet(gen_path).to_crs(epsg=4326)
        gen['lon'] = gen.geometry.x
        gen['lat'] = gen.geometry.y
    else:
        gen = None
        
    if os.path.exists(dc_path):
        dc = gpd.read_parquet(dc_path).to_crs(epsg=4326)
        dc['lon'] = dc.geometry.x
        dc['lat'] = dc.geometry.y
    else:
        dc = None
    
    # Create "Proposed Projects" (Commencement Data)
    projects = pd.DataFrame([
        {'name': f'Project {i+1}', 'capacity_mw': np.random.choice([10, 50, 150, 300, 550]), 
         'year': np.random.choice([2026, 2027, 2028, 2029]), 'status': 'Identified'}
        for i in range(15)
    ])

    def categorize_type(mw):
        if mw <= 10: return 'Legacy (1-10MW)'
        if mw <= 50: return 'Mid-Tier'
        return 'Hyperscale (50-300MW)'

    projects['Type'] = projects['capacity_mw'].apply(categorize_type)
    projects.columns = projects.columns.str.strip()
    
    return subs, lines, gen, dc, projects

# Single execution of data loading
subs, lines, gen, dc, projects = load_data()

# ---------------------------------------------------------
# Dynamic GridNode Instantiation (Scaling)
# ---------------------------------------------------------
grid_nodes = {}
for idx, row in subs.iterrows():
    v_val = 230
    if 'voltage' in row and pd.notnull(row['voltage']):
        try:
            v_val = int(str(row['voltage']).replace('kV', '').strip())
        except ValueError:
            pass
    
    cap = float(row.get('capacity_mw', 1000))
    b_load = cap - row['headroom_mw'] if 'headroom_mw' in row else float(row.get('current_load_mw', 800))
    
    grid_nodes[row['name']] = GridNode(
        name=row['name'],
        capacity_mw=cap,
        base_load_mw=b_load,
        voltage_kv=v_val
    )
# ---------------------------------------------------------

# --- 2. Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Interactive Grid Map", "Proposed Projects Outlook"])

# --- PAGE 1: GRID MAP ---
if page == "Interactive Grid Map":
    st.markdown("## ⚡ Ontario Data Centre & Grid Capacity Digital Twin")
    st.markdown("##### Substation Simulation: Evaluating 2026 IESO Forecasts for York Region Infrastructure.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sidebar Inputs
    st.sidebar.header("Simulation Parameters")
    target_sub = st.sidebar.selectbox("Select Target Substation", subs['name'].unique())
    dc_load = st.sidebar.slider("Simulated DC Load (MW)", 0, 600, 100)
    
    st.sidebar.header("Map Layers")
    show_subs = st.sidebar.toggle("Substations", value=True)
    show_gen = st.sidebar.toggle("Generation Sources", value=True)
    show_dc = st.sidebar.toggle("Existing Data Centres", value=False)
    show_flow = st.sidebar.toggle("Network Flow", value=True)
    
    st.sidebar.header("Base Map")
    map_theme = st.sidebar.selectbox("Geography Layer Style", ["Dark (Default)", "Streets/Places", "Satellite", "Light"])
    # Using Pydeck's built-in CartoDB basemaps which don't require an API key
    theme_mapping = {
        "Dark (Default)": "dark",
        "Streets/Places": "road",
        "Satellite": "satellite",
        "Light": "light"
    }
    
    # Substation data extraction
    sub_info = subs[subs['name'] == target_sub].iloc[0]
    
    # Digital Twin Engine (GridNode) - utilizing our scaled list
    node = grid_nodes[target_sub]
    
    reliability = node.calculate_reliability(new_load_mw=dc_load, iterations=1000)
    losses = node.estimate_losses(load_mw=dc_load)
    remaining_headroom = sub_info.get('headroom_mw', node.capacity_mw - node.base_load_mw) - dc_load
    
    # Reliability Status
    if reliability >= 99:
        status = "EXCELLENT"
        color = "Green Zone"
    elif reliability >= 90:
        status = "FEASIBLE"
        color = "Requires IESO connection assessment"
    else:
        status = "HIGH RISK"
        color = "Transformer upgrade likely required"
        
    # Build Map Layers
    map_layers = []
    
    # Scaled Simulation: Evaluate reliability for ALL substations
    def get_substation_color(sub_name):
        n = grid_nodes.get(sub_name)
        if not n:
            return [150, 150, 150, 150]
        # Use fewer iterations for the map to keep UI responsive
        rel = n.calculate_reliability(new_load_mw=dc_load, iterations=200)
        if rel >= 99:
            return [0, 255, 0, 150]      # Green
        elif rel >= 90:
            return [255, 165, 0, 150]    # Orange
        else:
            return [255, 0, 0, 150]      # Red

    # Color logic for substations based on dynamic Monte Carlo reliability
    subs['color'] = subs['name'].apply(get_substation_color)

    if show_subs:
        map_layers.append(pdk.Layer(
            "ScatterplotLayer",
            subs,
            id="substations",
            get_position="[lon, lat]",
            get_color="color",
            get_radius=500,
            pickable=True,
        ))
        
    if show_gen and gen is not None:
        map_layers.append(pdk.Layer(
            "ScatterplotLayer", gen, 
            id="generation",
            get_position="[lon, lat]",
            get_color="[255, 200, 0, 200]", 
            get_radius=2000, 
            pickable=True
        ))

    if show_dc and dc is not None:
        map_layers.append(pdk.Layer(
            "ColumnLayer", dc, 
            id="data-centres",
            get_position="[lon, lat]",
            get_elevation="load_mw * 10", 
            elevation_scale=1,
            get_fill_color="[200, 30, 30, 150]", 
            radius=800, 
            pickable=True
        ))
        
    # Proposed DC logic (pulse effect visually indicated)
    proposed_dc_loc = pd.DataFrame([{
        'name': 'Proposed DC Site',
        'lat': sub_info['lat'] + 0.01, # Offset slightly for visibility
        'lon': sub_info['lon'] + 0.01,
        'load_mw': dc_load
    }])
    
    map_layers.append(pdk.Layer(
        "ScatterplotLayer", proposed_dc_loc, 
        id="proposed-dc",
        get_position="[lon, lat]",
        get_color="[0, 255, 100, 255]", 
        get_radius=1000,
    ))

    # Energy Flow lines (Arcs)
    if show_flow and gen is not None:
        flow_lines = []
        for _, g in gen.iterrows():
            flow_lines.append({'start': [g.lon, g.lat], 'end': [sub_info.lon, sub_info.lat]})
        
        map_layers.append(pdk.Layer(
            "ArcLayer", pd.DataFrame(flow_lines), 
            id="flow-arcs",
            get_source_position="start", 
            get_target_position="end",
            get_source_color="[255, 200, 0]", 
            get_target_color="[0, 200, 255]", 
            width=2
        ))

    # Layout: Metrics & Map
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Node Analysis")
        st.markdown(f"**Target Node:** `{target_sub}`")
        st.metric("Net Headroom (MW)", f"{remaining_headroom:.2f}", delta=-dc_load)
        
        st.markdown(f"**Reliability Probability:** `{reliability:.2f}%`")
        st.markdown(f"**Estimated Heat Loss (I²R):** `{losses:.4f} MW`")
        st.markdown(f"**Status:** `{status}` - *{color}*")
        
        st.markdown("---")
        
        if status == "HIGH RISK":
            st.error("**Recommendation:** Transformer Upgrade Required for 2026 Capacity.")
        elif status == "FEASIBLE":
            st.warning("**Recommendation:** Viable, but grid stress observed. Requires IESO connection assessment.")
        else:
            st.success("**Recommendation:** Grid Node appears highly viable for development.")
            
        st.caption("**Technical Note:** Calculations incorporate a 1.15 Safety Factor and I²R loss estimates, alongside a Monte Carlo simulation (1000 iterations) with +/- 10% ambient grid fluctuation.")

    with col2:
        st.pydeck_chart(pdk.Deck(
            map_style=theme_mapping[map_theme],
            initial_view_state=pdk.ViewState(
                latitude=sub_info['lat'],
                longitude=sub_info['lon'],
                zoom=8,
                pitch=45,
            ),
            layers=map_layers,
            tooltip={"html": "<b>{name}</b><br/>Capacity/Load: {capacity_mw}{load_mw} MW<br/>Headroom: {headroom_mw} MW", "style": {"backgroundColor": "steelblue", "color": "white", "maxWidth": "300px", "wordWrap": "break-word"}}
        ))
        
        # Add a custom Legend below the map
        with st.expander("🗺️ Map Legend", expanded=True):
            st.markdown("""
            - 🟩 **Substation (Green):** Highly Viable / Excellent Headroom
            - 🟧 **Substation (Orange):** Feasible / Moderate Stress
            - 🟥 **Substation (Red):** High Risk / Upgrade Required
            - 🟡 **Generation Source:** Existing Power Generation (Nuclear, Hydro, Gas, etc.)
            - 🟥 **Column (Dark Red):** Existing Data Centres
            - 🟢 **Pulse Point (Bright Green):** Proposed Data Centre Location
            - 🟡 〰️ 🔵 **Arc Lines:** Network Flow (Generation -> Substation)
            """)

# --- PAGE 2: PROPOSED PROJECTS ---
else:
    st.title("📈 Ontario Data Centre Market Outlook")
    
    st.sidebar.header("Outlook Filters")
    
    # Filter by Year (Expected Commencement)
    years = sorted(projects['year'].unique())
    selected_years = st.sidebar.multiselect("Commencement Year", years, default=years)
    
    # Filter by Data Centre Type
    types = sorted(projects['Type'].unique().tolist())
    selected_types = st.sidebar.multiselect("Project Type", types, default=types)
    
    # Filter by Capacity Range (MW)
    min_cap = int(projects['capacity_mw'].min())
    max_cap = int(projects['capacity_mw'].max())
    cap_range = st.sidebar.slider("Capacity Range (MW)", min_cap, max_cap, (min_cap, max_cap))

    # Apply Filters
    filtered_df = projects[
        (projects['year'].isin(selected_years)) &
        (projects['Type'].isin(selected_types)) &
        (projects['capacity_mw'] >= cap_range[0]) &
        (projects['capacity_mw'] <= cap_range[1])
    ]

    total_mw = filtered_df['capacity_mw'].sum()
    st.metric("Total Filtered Demand", f"{total_mw:,} MW")

    if filtered_df.empty:
        st.warning("No projects match the selected filters.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Filtered Size Distribution")
            dist_df = filtered_df.groupby('Type', observed=False).size().reset_index(name='Count')
            fig_size = px.bar(dist_df, x='Type', y='Count', color='Type', 
                              color_discrete_map={
                                  'Legacy (1-10MW)': '#1f77b4', 
                                  'Mid-Tier': '#87ceeb', 
                                  'Hyperscale (50-300MW)': '#ff3131'
                              })
            st.plotly_chart(fig_size, use_container_width=True)

        with col2:
            st.subheader("Filtered Commencement Timeline")
            timeline_df = filtered_df.groupby('year')['capacity_mw'].sum().reset_index()
            fig_time = px.area(timeline_df, x='year', y='capacity_mw', 
                               labels={'capacity_mw': 'Commencing Capacity (MW)'})
            st.plotly_chart(fig_time, use_container_width=True)

        st.subheader("Identified Project Queue (Filtered)")
        st.dataframe(filtered_df.sort_values(['year', 'capacity_mw'], ascending=[True, False]), 
                     use_container_width=True)