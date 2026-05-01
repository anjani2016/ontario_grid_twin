import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd

# 1. UI Setup - Sidebar
st.sidebar.header("Map Layers")
show_subs = st.sidebar.toggle("Substations", value=True)
show_gen = st.sidebar.toggle("Generation Sources", value=True)
show_dc = st.sidebar.toggle("Existing Data Centres", value=True)
show_flow = st.sidebar.toggle("Energy Flow Arcs", value=True)

# 2. Layer Assembly Logic
# We initialize an empty list and only add layers if the toggle is ON
map_layers = []

if show_subs:
    sub_layer = pdk.Layer(
        "ScatterplotLayer", subs, 
        id="substations", # ID is helpful for state persistence
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