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
    
    return subs, lines, gen, dc

@st.cache_data
def load_dc_projects():
    """
    Loads Ontario data centre project data.
    Priority:
      1. data/raw/baxtel_projects.parquet  (run src/utils/baxtel_harvester.py to generate)
      2. National Observer (March 2026) hardcoded fallback
    """
    PROVINCIAL_INTEREST_MW = 6500.0
    BAXTEL_PATH = 'data/raw/baxtel_projects.parquet'

    def categorize_type(mw):
        if pd.isna(mw):      return 'Unknown'
        if mw <= 50:         return 'Mid-Tier (≤50 MW)'
        if mw <= 150:        return 'Large (50–150 MW)'
        return 'Hyperscale (>150 MW)'

    # --- Try Baxtel first ---
    if os.path.exists(BAXTEL_PATH):
        try:
            gdf = gpd.read_parquet(BAXTEL_PATH)
            df = pd.DataFrame(gdf.drop(columns='geometry', errors='ignore'))

            # Ensure required columns exist with sensible defaults
            for col, default in [('capacity_mw', float('nan')), ('status', 'Identified'),
                                  ('year', 2026), ('region', 'Ontario')]:
                if col not in df.columns:
                    df[col] = default

            df['year'] = df['year'].fillna(2026).astype(int)
            df['capacity_mw'] = pd.to_numeric(df['capacity_mw'], errors='coerce')
            df['Type'] = df['capacity_mw'].apply(categorize_type)
            df['source'] = 'Baxtel'
            return df, PROVINCIAL_INTEREST_MW, 'Baxtel'
        except Exception as e:
            pass  # fall through to hardcoded data

    # --- Fallback: National Observer (March 2026) ---
    TOTAL_PROPOSED_CAPACITY_MW = 2202.0
    avg = round((TOTAL_PROPOSED_CAPACITY_MW - 217) / 11, 1)

    real_projects = [
        {'name': 'Cambridge Data Centre 1',     'capacity_mw': 45.0,  'region': 'Cambridge', 'year': 2026, 'status': 'Proposed'},
        {'name': 'Cambridge Data Centre 2',     'capacity_mw': 45.0,  'region': 'Cambridge', 'year': 2026, 'status': 'Proposed'},
        {'name': 'Microsoft Vaughan Expansion', 'capacity_mw': 100.0, 'region': 'York',      'year': 2026, 'status': 'Under Review'},
        {'name': 'Yondr Toronto',               'capacity_mw': 27.0,  'region': 'Toronto',   'year': 2027, 'status': 'Proposed'},
        {'name': 'Observer Project 1 (Avg)',    'capacity_mw': avg,   'region': 'Various',   'year': 2027, 'status': 'Identified'},
        {'name': 'Observer Project 2 (Avg)',    'capacity_mw': avg,   'region': 'Various',   'year': 2027, 'status': 'Identified'},
        {'name': 'Observer Project 3 (Avg)',    'capacity_mw': avg,   'region': 'Various',   'year': 2028, 'status': 'Identified'},
        {'name': 'Observer Project 4 (Avg)',    'capacity_mw': avg,   'region': 'GTA',       'year': 2028, 'status': 'Identified'},
        {'name': 'Observer Project 5 (Avg)',    'capacity_mw': avg,   'region': 'GTA',       'year': 2028, 'status': 'Identified'},
        {'name': 'Observer Project 6 (Avg)',    'capacity_mw': avg,   'region': 'Various',   'year': 2028, 'status': 'Identified'},
        {'name': 'Observer Project 7 (Avg)',    'capacity_mw': avg,   'region': 'Various',   'year': 2029, 'status': 'Identified'},
        {'name': 'Observer Project 8 (Avg)',    'capacity_mw': avg,   'region': 'Various',   'year': 2029, 'status': 'Identified'},
        {'name': 'Observer Project 9 (Avg)',    'capacity_mw': avg,   'region': 'Various',   'year': 2029, 'status': 'Identified'},
        {'name': 'Observer Project 10 (Avg)',   'capacity_mw': avg,   'region': 'York',      'year': 2029, 'status': 'Identified'},
        {'name': 'Observer Project 11 (Avg)',   'capacity_mw': avg,   'region': 'York',      'year': 2029, 'status': 'Identified'},
    ]

    df = pd.DataFrame(real_projects)
    df['Type'] = df['capacity_mw'].apply(categorize_type)
    df['source'] = 'National Observer (Mar 2026)'
    return df, PROVINCIAL_INTEREST_MW, 'National Observer (Mar 2026)'

# Single execution of data loading
subs, lines, gen, dc = load_data()
projects, provincial_interest_mw, dc_data_source = load_dc_projects()

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
try:
    st.sidebar.image("data/assets/CR_logo.png", use_container_width=True)
except Exception:
    pass
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Interactive Grid Map", "Monte Carlo Analytics", "Data Centres (Projected)"])

# --- PAGE 1: GRID MAP ---
if page == "Interactive Grid Map":
    st.markdown("## ⚡ Ontario Data Centre & Grid Capacity Digital Twin")
    st.markdown("##### Substation Simulation: Evaluating 2026 IESO Forecasts for York Region Infrastructure.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sidebar Inputs
    st.sidebar.header("Simulation Parameters")
    target_sub = st.sidebar.selectbox("Select Target Substation", subs['name'].unique())
    dc_load = st.sidebar.slider("Simulated Data Centre Load (MW)", 0, 600, 100)
    
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

    # 1. Map in the top half (full width)
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

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Lower half: Text on the left, Legend on the right
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Node Analysis")
        st.markdown(f"**Target Node:** `{target_sub}`")
        st.metric("Net Headroom (MW)", f"{remaining_headroom:.2f}", delta=-dc_load)
        
        st.markdown(f"**Reliability Probability:** `{reliability:.2f}%`")
        st.markdown(f"**Status:** `{status}` - *{color}*")
        
        st.markdown("---")
        
        if status == "HIGH RISK":
            st.error("**Recommendation:** Transformer Upgrade Required for 2026 Capacity.")
        elif status == "FEASIBLE":
            st.warning("**Recommendation:** Viable, but grid stress observed. Requires IESO connection assessment.")
        else:
            st.success("**Recommendation:** Grid Node appears highly viable for development.")
            
    with col2:
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

    st.markdown("---")
    st.caption(f"**Technical Note:** Calculations incorporate a 1.15 Safety Factor and I²R Estimated Heat Loss of **{losses:.4f} MW**, alongside a Monte Carlo simulation using a Triangular Distribution (40% min, 70% typical, 100% peak ambient load).")

# --- PAGE 2: MONTE CARLO ANALYTICS ---
elif page == "Monte Carlo Analytics":
    st.markdown("## 🎲 Monte Carlo Risk Analytics")
    st.markdown("##### Probabilistic Distribution of Grid Load Scenarios")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Simulation Parameters")
        target_sub = st.selectbox("Select Target Substation", subs['name'].unique(), key="mc_sub")
        dc_load = st.slider("Simulated Data Centre Load (MW)", 0, 600, 100, key="mc_slider")
        iterations = st.slider("Simulation Iterations", 1000, 10000, 5000, step=1000)
        
        node = grid_nodes[target_sub]
        simulated_loads = node.simulate_loads(new_load_mw=dc_load, iterations=iterations)
        reliability = (np.sum(simulated_loads <= node.capacity_mw) / iterations) * 100
        
        st.markdown("---")
        st.markdown(f"**Target Node:** `{target_sub}`")
        st.markdown(f"**Base Capacity:** `{node.capacity_mw} MW`")
        st.markdown(f"**Proposed Load:** `+{dc_load} MW`")
        st.markdown(f"**Reliability Probability:** `{reliability:.2f}%`")
        
        if reliability < 100:
            st.warning(f"**Risk Detected:** There is a `{100-reliability:.2f}%` chance that the grid will exceed maximum capacity under peak conditions.")
        else:
            st.success("**Safe:** The grid is projected to handle the load without exceeding capacity under all simulated scenarios.")
            
    with col2:
        fig = px.histogram(
            x=simulated_loads, 
            nbins=50, 
            title=f"Load Distribution for {target_sub} (+ {dc_load} MW)",
            labels={'x': 'Total Projected Load (MW)', 'y': 'Frequency (Scenarios)'},
            color_discrete_sequence=['#1f77b4']
        )
        
        # Add vertical line for capacity
        fig.add_vline(x=node.capacity_mw, line_dash="dash", line_color="red", 
                      annotation_text=f"Max Capacity ({node.capacity_mw} MW)", annotation_position="top right")
        
        fig.update_layout(xaxis_title="Total Projected Load (MW)", yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True)

# --- PAGE 3: DATA CENTRES (PROJECTED) ---
elif page == "Data Centres (Projected)":
    st.markdown("## 🏢 Ontario Data Centres (Projected)")
    st.markdown("##### Proposed hyperscale and large-format data centre projects in Ontario's grid footprint.")
    st.markdown("<br>", unsafe_allow_html=True)

    st.sidebar.header("Filters")
    st.sidebar.caption(f"📡 Data source: **{dc_data_source}**")
    st.sidebar.caption("Run `src/utils/baxtel_harvester.py` to refresh live data.")

    # Filter by Region
    regions = sorted(projects['region'].unique())
    selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

    # Filter by Status
    statuses = sorted(projects['status'].unique())
    selected_statuses = st.sidebar.multiselect("Status", statuses, default=statuses)

    # Filter by Capacity Range (MW)
    min_cap = int(projects['capacity_mw'].min())
    max_cap = int(projects['capacity_mw'].max())
    cap_range = st.sidebar.slider("Capacity Range (MW)", min_cap, max_cap, (min_cap, max_cap))

    # Apply Filters
    filtered_df = projects[
        (projects['region'].isin(selected_regions)) &
        (projects['status'].isin(selected_statuses)) &
        (projects['capacity_mw'] >= cap_range[0]) &
        (projects['capacity_mw'] <= cap_range[1])
    ]

    # --- KPI row ---
    total_proposed = filtered_df['capacity_mw'].sum()
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Proposed Demand (filtered)",  f"{total_proposed:,.0f} MW")
    k2.metric("Total Proposed (all projects)",      f"2,202 MW")
    k3.metric("Total Provincial Interest",          f"{provincial_interest_mw:,.0f} MW")

    if filtered_df.empty:
        st.warning("No projects match the selected filters.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Data Centre Type")
            dist_df = filtered_df.groupby('Type', observed=False).size().reset_index(name='Count')
            fig_size = px.bar(dist_df, x='Type', y='Count', color='Type',
                              color_discrete_map={
                                  'Mid-Tier (≤50 MW)':   '#1f77b4',
                                  'Large (50–150 MW)':   '#87ceeb',
                                  'Hyperscale (>150 MW)':'#ff3131'
                              })
            fig_size.update_layout(showlegend=False)
            st.plotly_chart(fig_size, use_container_width=True)

        with col2:
            st.subheader("Timeline")
            timeline_df = filtered_df.copy()
            timeline_df['year'] = timeline_df['year'].astype(int).astype(str)
            timeline_df = timeline_df.groupby('year')['capacity_mw'].sum().reset_index()
            fig_time = px.area(timeline_df, x='year', y='capacity_mw',
                               labels={'capacity_mw': 'Projected Capacity (MW)', 'year': 'Year'})
            fig_time.update_xaxes(type='category')
            st.plotly_chart(fig_time, use_container_width=True)

        st.subheader("Project Details")
        st.dataframe(
            filtered_df[['name','region','capacity_mw','year','status','Type']]
            .rename(columns={'name':'Project','region':'Region','capacity_mw':'Capacity (MW)','year':'Year','status':'Status','Type':'Type'})
            .sort_values(['Year','Capacity (MW)'], ascending=[True, False]),
            use_container_width=True
        )

    # --- CLIMATE EFFICIENCY SECTION ---
    st.markdown("---")
    st.subheader("❄️ Climate-Based Cooling Efficiency")
    st.markdown("Ontario's cold climate allows for 'Free Cooling', significantly reducing the energy required for data centre operations.")

    # 1. Regional Temperature Mapping (Approximate Annual Averages)
    region_temps = {
        'Toronto': 9.2, 'GTA': 8.5, 'York': 7.8, 'Cambridge': 8.1, 'Various': 7.5
    }

    def get_realistic_savings(temp):
        """
        Conservative tiered savings based on ASHRAE TC 9.9 and M-Cycle benchmarks.
        """
        if temp < -10:         return 0.70, "Max Free-Cooling Utilization"
        if -10 <= temp < 0:    return 0.50, "Compressors Disabled; Fans Only"
        if 0 <= temp < 10:     return 0.30, "Partial Evaporative Support"
        return 0.10, "Mechanical Rejection Active"

    # 2. Project-Specific Climate Table
    climate_data = []
    for _, row in filtered_df.iterrows():
        avg_t = region_temps.get(row['region'], 7.5)
        savings, note = get_realistic_savings(avg_t)
        
        # Calculate Effective PUE for technical depth
        # Formula: 1.0 (IT) + 0.30*(1-savings) (Variable) + 0.08 (Floor)
        effective_pue = 1.0 + (0.30 * (1 - savings)) + 0.08
        
        climate_data.append({
            "Project": row['name'],
            "Region": row['region'],
            "Avg Annual Temp": f"{avg_t}°C",
            "Cooling Note": note,
            "Effective PUE": f"{effective_pue:.2f}",
            "Savings Factor": f"{savings * 100:.0f}%"
        })
    
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("**Projected Cooling Efficiency by Location**")
        st.table(pd.DataFrame(climate_data))

    with c2:
        st.markdown("**Tiered Efficiency Reference**")
        temp_tiers = [
            {"Range": "-20 to -10°C", "Savings": "70%", "Note": "Max Free-Cooling"},
            {"Range": "-10 to 0°C",   "Savings": "50%", "Note": "Fans Only (No Compressors)"},
            {"Range": "0 to 10°C",    "Savings": "30%", "Note": "Partial Evaporative"},
            {"Range": "10 to 20°C",   "Savings": "10%", "Note": "Mechanical Rejection"}
        ]
        st.table(pd.DataFrame(temp_tiers))

    st.markdown("---")
    st.caption("**Efficiency References:**")
    st.caption("1. **M-Cycle Efficiency:** International Institute of Refrigeration - Notes 80% theoretical reduction (70% applied here for conservative safety).")
    st.caption("2. **Thermal Guidelines:** ASHRAE TC 9.9 (2021) - Standards for inlet temperatures and cooling classes.")
    st.caption("3. **Energy Consumption:** Wikipedia/Data Center - Cooling accounts for ~30% energy in enterprise sites vs ~7-10% in optimized hyperscale.")
    
    st.markdown("---")
    st.caption("**Data Source:** National Observer, March 2026 — *'One data centre or one million homes? Mapping Ontario's proposed hyperscaler boom.'* Total reported proposed capacity: 2,202 MW. Total provincial interest: 6,500 MW (Ontario government).")