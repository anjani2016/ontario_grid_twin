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
    show_subs = st.sidebar.toggle("Substations", value=True)
    
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
        
    # ... (Rest of your toggle logic for gen and dc)

    # Render Map
    st.pydeck_chart(pdk.Deck(
        layers=map_layers,
        initial_view_state=pdk.ViewState(latitude=43.9, longitude=-79.4, zoom=8, pitch=45)
    ))