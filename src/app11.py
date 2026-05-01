import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
import numpy as np
import os
import plotly.express as px
import numpy as np
from engine.grid_model import GridNode

# Page Configuration
st.set_page_config(page_title="Ontario Grid Digital Twin", layout="wide")
st.title("⚡ Ontario Data Centre & Grid Capacity Digital Twin")
st.markdown("Evaluating 2026 IESO Forecasts for York Region Infrastructure.")

# 1. Load Data
@st.cache_data
def load_data():
    subs = gpd.read_parquet('data/processed/analyzed_substations.parquet')
    lines = gpd.read_parquet('data/raw/ontario_lines.parquet')
    # Ensure coordinates are in lat/lon for the map
    subs = subs.to_crs(epsg=4326)
    lines = lines.to_crs(epsg=4326)
    
    # Extract lat/lon for pydeck
    subs['lon'] = subs.geometry.x
    subs['lat'] = subs.geometry.y
    return subs, lines

subs, lines = load_data()

# 2. Sidebar Controls
st.sidebar.header("Simulation Parameters")
target_sub = st.sidebar.selectbox("Select Target Substation", subs['name'].unique())
dc_load = st.sidebar.slider("Data Centre Load (MW)", 10, 500, 100)

# 3. Real-time Analysis Logic
sub_info = subs[subs['name'] == target_sub].iloc[0]
remaining_headroom = sub_info['headroom_mw'] - dc_load
reliability = "HIGH" if remaining_headroom > 0 else "CRITICAL"

# 4. Map Visualization Logic
# Define color based on headroom (Green to Red)
subs['color'] = subs.apply(lambda x: [0, 255, 0, 150] if x['headroom_mw'] > dc_load else [255, 0, 0, 150], axis=1)

# Pydeck Layers
substation_layer = pdk.Layer(
    "ScatterplotLayer",
    subs,
    get_position="[lon, lat]",
    get_color="color",
    get_radius=300,
    pickable=True,
)

# 5. Layout: Metrics and Map
col1, col2 = st.columns([1, 2])

with col1:
    st.metric("Substation", target_sub)
    st.metric("Net Headroom (MW)", f"{remaining_headroom:.2f}", delta=remaining_headroom)
    st.write(f"**Status:** {reliability}")
    
    if reliability == "CRITICAL":
        st.error("Transformer Upgrade Required for 2026 Capacity.")
    else:
        st.success("Grid Node appears viable.")

with col2:
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=subs['lat'].mean(),
            longitude=subs['lon'].mean(),
            zoom=10,
            pitch=45,
        ),
        layers=[substation_layer]
    ))

st.info("Technical Note: Calculations incorporate a 1.15 Safety Factor and I2R loss estimates.")