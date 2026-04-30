import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd

st.set_page_config(page_title="Ontario Grid Digital Twin 2.0", layout="wide")
st.title("⚡ Ontario Grid Digital Twin 2.0")

# Load All Layers
@st.cache_data
def load_all_layers():
    subs = gpd.read_parquet('data/processed/analyzed_substations.parquet').to_crs(epsg=4326)
    lines = gpd.read_parquet('data/raw/ontario_lines.parquet').to_crs(epsg=4326)
    gen = gpd.read_parquet('data/raw/generation_sources.parquet').to_crs(epsg=4326)
    dc = gpd.read_parquet('data/raw/existing_dc.parquet').to_crs(epsg=4326)
    
    for df in [subs, gen, dc]:
        df['lon'] = df.geometry.x
        df['lat'] = df.geometry.y
    return subs, lines, gen, dc

subs, lines, gen, dc = load_all_layers()

# Sidebar: Interactive Simulation
st.sidebar.header("Data Centre Simulation")
target_sub = st.sidebar.selectbox("Select Interconnection Point", subs['name'].unique())
dc_load = st.sidebar.slider("Proposed Load (MW)", 0, 500, 100)

# Logic for "Imaginary" Data Centre Placement
selected_sub_geom = subs[subs['name'] == target_sub].iloc[0]
proposed_dc_loc = pd.DataFrame([{
    'name': 'Proposed DC Site',
    'lat': selected_sub_geom['lat'] + 0.01, # Offset slightly for visibility
    'lon': selected_sub_geom['lon'] + 0.01,
    'load_mw': dc_load
}])

# --- Pydeck Layers ---
# 1. Substations (Nodes)
sub_layer = pdk.Layer(
    "ScatterplotLayer", subs, get_position="[lon, lat]",
    get_color="[0, 200, 255, 160]", get_radius=500, pickable=True
)

# 2. Generation Sources (Large Yellow Points)
gen_layer = pdk.Layer(
    "ScatterplotLayer", gen, get_position="[lon, lat]",
    get_color="[255, 200, 0, 200]", get_radius=2000, pickable=True
)

# 3. Existing Data Centres (Red Cubes)
dc_layer = pdk.Layer(
    "ColumnLayer", dc, get_position="[lon, lat]",
    get_elevation="load_mw * 10", elevation_scale=1,
    get_fill_color="[200, 30, 30, 150]", radius=800, pickable=True
)

# 4. Proposed Data Centre (Pulse Effect)
proposed_layer = pdk.Layer(
    "ScatterplotLayer", proposed_dc_loc, get_position="[lon, lat]",
    get_color="[0, 255, 100, 200]", get_radius=1000,
)

# 5. Energy Flow (Lines from Generation to Substation)
flow_lines = []
for _, g in gen.iterrows():
    flow_lines.append({'start': [g.lon, g.lat], 'end': [selected_sub_geom.lon, selected_sub_geom.lat]})

flow_layer = pdk.Layer(
    "ArcLayer", flow_lines, get_source_position="start", get_target_position="end",
    get_source_color="[255, 200, 0]", get_target_color="[0, 200, 255]", width=2
)

# Render Map
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(latitude=43.9, longitude=-79.4, zoom=8, pitch=45),
    layers=[sub_layer, gen_layer, dc_layer, proposed_layer, flow_layer],
    tooltip={"text": "{name}\nType: {type}\nLoad/Capacity: {load_mw}{capacity_mw} MW"}
))

# Metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Grid Headroom", f"{selected_sub_geom['headroom_mw']:.1f} MW")
with col2:
    st.metric("Proposed Impact", f"-{dc_load} MW", delta_color="inverse")



















    ------







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