import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
import os
import plotly.express as px
import numpy as np

# --- 1. Shared Data Loading ---
@st.cache_data
def load_data():
    # Load substation data
    # Note: Ensure data/processed/analyzed_substations.parquet exists in your repo
    subs = gpd.read_parquet('data/processed/analyzed_substations.parquet').to_crs(epsg=4326)
    subs['lon'] = subs.geometry.x
    subs['lat'] = subs.geometry.y
    
    # Create "Proposed Projects" (Commencement Data)
    projects = pd.DataFrame([
        {'name': f'Project {i+1}', 'capacity_mw': np.random.choice([10, 50, 150, 300, 550]), 
         'year': np.random.choice([2026, 2027, 2028, 2029]), 'status': 'Identified'}
        for i in range(15)
    ])

    # Logic to categorize by Type (Matches Screenshot 2026-04-30 at 3.10.36 PM.png)
    def categorize_type(mw):
        if mw <= 10: return 'Legacy (1-10MW)'
        if mw <= 50: return 'Mid-Tier'
        return 'Hyperscale (50-300MW)'

    projects['Type'] = projects['capacity_mw'].apply(categorize_type)
    
    # Clean column names to prevent KeyErrors
    projects.columns = projects.columns.str.strip()
    
    return subs, projects

# Single execution of data loading
subs, projects = load_data()

# --- 2. Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Interactive Grid Map", "Proposed Projects Outlook"])

# --- PAGE 1: GRID MAP ---
if page == "Interactive Grid Map":
    st.title("⚡ Interactive Grid Digital Twin")
    
    st.sidebar.header("Simulation Parameters")
    target_sub = st.sidebar.selectbox("Select Interconnection Substation", subs['name'].unique())
    dc_load = st.sidebar.slider("Simulated DC Load (MW)", 0, 600, 100)
    
    st.sidebar.header("Map Layers")
    show_subs = st.sidebar.toggle("Show Substations", value=True)
    
    selected_sub_data = subs[subs['name'] == target_sub].iloc[0]
    
    layers = []
    if show_subs:
        layers.append(pdk.Layer(
            "ScatterplotLayer", subs,
            get_position="[lon, lat]",
            get_color="[0, 200, 255, 160]",
            get_radius=500, pickable=True
        ))
    
    layers.append(pdk.Layer(
        "ScatterplotLayer", pd.DataFrame([selected_sub_data]),
        get_position="[lon, lat]",
        get_color="[255, 0, 0, 255]",
        get_radius=800,
    ))

    # --- This goes inside the "Interactive Grid Map" section ---

    # 1. We build the list of layers based on user selection
    layers = []
    if show_subs:
        layers.append(pdk.Layer(
            "ScatterplotLayer", 
            subs,
            get_position="[lon, lat]",
            get_color="[0, 200, 255, 160]", # Light Blue
            get_radius=500, 
            pickable=True
        ))

    # 2. We add a special layer for the selected substation (Red)
    layers.append(pdk.Layer(
        "ScatterplotLayer", 
        pd.DataFrame([selected_sub_data]),
        get_position="[lon, lat]",
        get_color="[255, 0, 0, 255]", 
        get_radius=800,
    ))

    # 3. This is the part you shared, optimized to render the layers above
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state=pdk.ViewState(
            latitude=selected_sub_data['lat'],  # Dynamic: Focuses on selection
            longitude=selected_sub_data['lon'], 
            zoom=10, 
            pitch=45
        ),
        layers=layers, # Uses the list we built in Step 1 & 2
        tooltip={"text": "{name}\nHeadroom: {headroom_mw} MW"}
    ))
    
    st.metric("Net Headroom (Post-Simulation)", f"{selected_sub_data['headroom_mw'] - dc_load:.1f} MW")

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