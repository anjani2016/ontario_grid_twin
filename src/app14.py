import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
import os



# 1. Data Loading Function
@st.cache_data
def load_all_layers():
    # Define paths
    subs_path = 'data/processed/analyzed_substations.parquet'
    gen_path = 'data/raw/generation_sources.parquet'
    dc_path = 'data/raw/existing_dc.parquet'
    
    # Verify files exist to avoid silent failures
    if not all(os.path.exists(p) for p in [subs_path, gen_path, dc_path]):
        st.error("Missing data files. Please run the Harvester and Analyzer scripts first.")
        return None, None, None, None

    # Load and Project to Lat/Lon
    subs_df = gpd.read_parquet(subs_path).to_crs(epsg=4326)
    gen_df = gpd.read_parquet(gen_path).to_crs(epsg=4326)
    dc_df = gpd.read_parquet(dc_path).to_crs(epsg=4326)
    
    # Prepare coordinates for Pydeck
    for df in [subs_df, gen_df, dc_df]:
        df['lon'] = df.geometry.x
        df['lat'] = df.geometry.y
        
    return subs_df, gen_df, dc_df

# 2. Execute Loading (This MUST happen before the UI logic)
subs, gen, dc = load_all_layers()


# 3. UI Logic - Only proceed if data loaded successfully
if subs is not None:
    st.sidebar.header("Map Layers")


    # --- FIX: Define all toggles first ---
    show_subs = st.sidebar.toggle("Substations", value=True)
    show_gen = st.sidebar.toggle("Generation Sources", value=False)
    show_dc = st.sidebar.toggle("Existing Data Centres", value=False)
    # Note: 'show_flow' is commented out until you define the flow_lines logic
    show_flow = st.sidebar.toggle("Network Flow", value=False)
    
    map_layers = []

    if show_subs:
        sub_layer = pdk.Layer(
            "ScatterplotLayer", 
            subs,  # Now 'subs' is defined globally in this script
            id="substations",
            get_position="[lon, lat]",
            get_color="[0, 200, 255, 160]", 
            get_radius=500, 
            pickable=True
        )
        map_layers.append(sub_layer)
        

if show_gen:
    gen_layer = pdk.Layer(
        "ScatterplotLayer", gen, 
        id="generation",
        get_position="[lon, lat]",
        get_color="[255, 200, 0, 200]", 
        get_radius=2000, 
        pickable=True
    )
    map_layers.append(gen_layer)

if show_dc:
    dc_layer = pdk.Layer(
        "ColumnLayer", dc, 
        id="data-centres",
        get_position="[lon, lat]",
        get_elevation="load_mw * 10", 
        elevation_scale=1,
        get_fill_color="[200, 30, 30, 150]", 
        radius=800, 
        pickable=True
    )
    map_layers.append(dc_layer)

if show_flow:
    # (Assuming flow_lines calculation from previous turn)
    flow_layer = pdk.Layer(
        "ArcLayer", flow_lines, 
        id="flow-arcs",
        get_source_position="start", 
        get_target_position="end",
        get_source_color="[255, 200, 0]", 
        get_target_color="[0, 200, 255]", 
        width=2
    )
    map_layers.append(flow_layer)

# 3. Render the Map with the dynamic list
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(latitude=43.9, longitude=-79.4, zoom=8, pitch=45),
    layers=map_layers, # This list now only contains the toggled layers
    tooltip={"text": "{name}\nLoad/Capacity: {load_mw}{capacity_mw} MW"}
))