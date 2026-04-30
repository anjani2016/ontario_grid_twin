import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
import os


import plotly.express as px
import numpy as np

# --- 1. Robust Data Loading ---
@st.cache_data
def load_data():
    try:
        # Using engine='pyogrio' is faster and more reliable on cloud deployments
        subs = gpd.read_parquet('data/processed/analyzed_substations.parquet')
        
        # Ensure CRS is correct for mapping (WGS84)
        if subs.crs != "EPSG:4326":
            subs = subs.to_crs(epsg=4326)
            
        subs['lon'] = subs.geometry.x
        subs['lat'] = subs.geometry.y
        
        # Proposed Data Centre Projects (from your specs)
        projects = pd.DataFrame([
            {'name': f'DC Project {i+1}', 'capacity_mw': np.random.choice([10, 50, 150, 300, 550]), 
             'year': np.random.choice([2026, 2027, 2028, 2029]), 'status': 'Proposed'}
            for i in range(15)
        ])
        return subs, projects
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

subs, projects = load_data()

import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="Ontario Grid & Data Centre Twin", layout="wide")

# --- 1. Shared Data Loading ---
@st.cache_data
def load_data():
    # Load your existing analyzed substations
    subs = gpd.read_parquet('data/processed/analyzed_substations.parquet').to_crs(epsg=4326)
    subs['lon'] = subs.geometry.x
    subs['lat'] = subs.geometry.y
    
    # Create synthetic "Proposed Projects" based on your provided data
    projects = pd.DataFrame([
        {'name': f'Project {i+1}', 'capacity_mw': np.random.choice([10, 50, 150, 300, 550]), 
         'year': np.random.choice([2026, 2027, 2028, 2029]), 'status': 'Identified'}
        for i in range(15)
    ])
    return subs, projects

subs, projects = load_data()

# --- 2. Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Interactive Grid Map", "Proposed Projects Outlook"])

# --- PAGE 1: GRID MAP ---
if page == "Interactive Grid Map":
    st.title("⚡ Interactive Grid Digital Twin")
    
    # Restore Substation Selection
    st.sidebar.header("Simulation Parameters")
    target_sub = st.sidebar.selectbox("Select Interconnection Substation", subs['name'].unique())
    dc_load = st.sidebar.slider("Simulated DC Load (MW)", 0, 600, 100)
    
    # Map Layer Toggles
    st.sidebar.header("Map Layers")
    show_subs = st.sidebar.toggle("Show Substations", value=True)
    
    selected_sub_data = subs[subs['name'] == target_sub].iloc[0]
    
    # Layer Logic
    layers = []
    if show_subs:
        layers.append(pdk.Layer(
            "ScatterplotLayer", subs,
            get_position="[lon, lat]",
            get_color="[0, 200, 255, 160]",
            get_radius=500, pickable=True
        ))
    
    # Highlight Selected Substation
    layers.append(pdk.Layer(
        "ScatterplotLayer", pd.DataFrame([selected_sub_data]),
        get_position="[lon, lat]",
        get_color="[255, 0, 0, 255]",
        get_radius=800,
    ))

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state=pdk.ViewState(
            latitude=selected_sub_data['lat'], 
            longitude=selected_sub_data['lon'], 
            zoom=10, pitch=45),
        layers=layers,
        tooltip={"text": "{name}\nHeadroom: {headroom_mw} MW"}
    ))
    
    st.metric("Net Headroom (Post-Simulation)", f"{selected_sub_data['headroom_mw'] - dc_load:.1f} MW")

# --- PAGE 2: PROPOSED PROJECTS ---
else:
    st.title("📈 Ontario Data Centre Market Outlook")
    
    # --- 1. Filter Implementation ---
    st.sidebar.header("Outlook Filters")
    
    # Filter by Year (Commencement Year)
    years = sorted(projects['year'].unique())
    selected_years = st.sidebar.multiselect("Commencement Year", years, default=years)
    
    # Filter by Data Centre Type
    types = projects['Type'].unique().tolist()
    selected_types = st.sidebar.multiselect("Project Type", types, default=types)
    
    # Filter by Capacity Range (MW)
    min_cap = int(projects['capacity_mw'].min())
    max_cap = int(projects['capacity_mw'].max())
    cap_range = st.sidebar.slider("Capacity Range (MW)", min_cap, max_cap, (min_cap, max_cap))

    # --- 2. Apply Filters to Data ---
    filtered_df = projects[
        (projects['year'].isin(selected_years)) &
        (projects['Type'].isin(selected_types)) &
        (projects['capacity_mw'] >= cap_range[0]) &
        (projects['capacity_mw'] <= cap_range[1])
    ]

    # --- 3. Dynamic Metrics & Charts ---
    total_mw = filtered_df['capacity_mw'].sum()
    st.metric("Total Filtered Demand", f"{total_mw:,} MW")

    if filtered_df.empty:
        st.warning("No projects match the selected filters.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Filtered Size Distribution")
            # Grouping for the Bar Chart
            dist_df = filtered_df.groupby('Type', observed=False).size().reset_index(name='Count')
            fig_size = px.bar(dist_df, x='Type', y='Count', color='Type', 
                              color_discrete_map={'Legacy (1-10MW)': '#1f77b4', 'Mid-Tier': '#87ceeb', 'Hyperscale (50-300MW)': '#ff3131'})
            st.plotly_chart(fig_size, use_container_width=True)

        with col2:
            st.subheader("Filtered Commencement Timeline")
            # Cumulative capacity over time for filtered projects
            timeline_df = filtered_df.groupby('year')['capacity_mw'].sum().reset_index()
            fig_time = px.area(timeline_df, x='year', y='capacity_mw', 
                               labels={'capacity_mw': 'Commencing Capacity (MW)'},
                               title="Capacity entering grid per year")
            st.plotly_chart(fig_time, use_container_width=True)

        # --- 4. Interactive Data Table ---
        st.subheader("Identified Project Queue (Filtered)")
        st.dataframe(filtered_df.sort_values(['year', 'capacity_mw'], ascending=[True, False]), 
                     use_container_width=True)

