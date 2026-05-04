import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np

# Ensure data is loaded
if 'data_loaded' not in st.session_state:
    st.error("Please return to the [Home Page](../main.py) to initialize the application data.")
    st.stop()

# Retrieve shared data
subs = st.session_state['subs']
gen = st.session_state['gen']
dc = st.session_state['dc']
grid_nodes = st.session_state['grid_nodes']

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
theme_mapping = {"Dark (Default)": "dark", "Streets/Places": "road", "Satellite": "satellite", "Light": "light"}

# Substation data extraction
sub_info = subs[subs['name'] == target_sub].iloc[0]
node = grid_nodes[target_sub]

reliability = node.calculate_reliability(new_load_mw=dc_load, iterations=1000)
losses = node.estimate_losses(load_mw=dc_load)
remaining_headroom = sub_info.get('headroom_mw', node.capacity_mw - node.base_load_mw) - dc_load

# Reliability Status
if reliability >= 99:
    status, color_text = "EXCELLENT", "Green Zone"
elif reliability >= 90:
    status, color_text = "FEASIBLE", "Requires IESO connection assessment"
else:
    status, color_text = "HIGH RISK", "Transformer upgrade likely required"

# Build Map Layers
map_layers = []

def get_substation_color(sub_name):
    n = grid_nodes.get(sub_name)
    if not n: return [150, 150, 150, 150]
    rel = n.calculate_reliability(new_load_mw=dc_load, iterations=200)
    if rel >= 99: return [0, 255, 0, 150]
    elif rel >= 90: return [255, 165, 0, 150]
    else: return [255, 0, 0, 150]

subs_display = subs.copy()
subs_display['color'] = subs_display['name'].apply(get_substation_color)

if show_subs:
    map_layers.append(pdk.Layer("ScatterplotLayer", subs_display, id="substations", get_position="[lon, lat]", get_color="color", get_radius=500, pickable=True))
if show_gen and gen is not None:
    map_layers.append(pdk.Layer("ScatterplotLayer", gen, id="generation", get_position="[lon, lat]", get_color="[255, 200, 0, 200]", get_radius=2000, pickable=True))
if show_dc and dc is not None:
    map_layers.append(pdk.Layer("ColumnLayer", dc, id="data-centres", get_position="[lon, lat]", get_elevation="load_mw * 10", elevation_scale=1, get_fill_color="[200, 30, 30, 150]", radius=800, pickable=True))

proposed_dc_loc = pd.DataFrame([{'name': 'Proposed DC Site', 'lat': sub_info['lat'] + 0.01, 'lon': sub_info['lon'] + 0.01, 'load_mw': dc_load}])
map_layers.append(pdk.Layer("ScatterplotLayer", proposed_dc_loc, id="proposed-dc", get_position="[lon, lat]", get_color="[0, 255, 100, 255]", get_radius=1000))

if show_flow and gen is not None:
    flow_lines = [{'start': [g.lon, g.lat], 'end': [sub_info.lon, sub_info.lat]} for _, g in gen.iterrows()]
    map_layers.append(pdk.Layer("ArcLayer", pd.DataFrame(flow_lines), id="flow-arcs", get_source_position="start", get_target_position="end", get_source_color="[255, 200, 0]", get_target_color="[0, 200, 255]", width=2))

st.pydeck_chart(pdk.Deck(
    map_style=theme_mapping[map_theme],
    initial_view_state=pdk.ViewState(latitude=sub_info['lat'], longitude=sub_info['lon'], zoom=8, pitch=45),
    layers=map_layers,
    tooltip={"html": "<b>{name}</b><br/>Capacity/Load: {capacity_mw}{load_mw} MW<br/>Headroom: {headroom_mw} MW", "style": {"backgroundColor": "steelblue", "color": "white", "maxWidth": "300px", "wordWrap": "break-word"}}
))

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("#### Node Analysis")
    st.markdown(f"**Target Node:** `{target_sub}`")
    st.metric("Net Headroom (MW)", f"{remaining_headroom:.2f}", delta=-dc_load)
    st.markdown(f"**Reliability Probability:** `{reliability:.2f}%`")
    st.markdown(f"**Status:** `{status}` - *{color_text}*")
    st.markdown("---")
    if status == "HIGH RISK": st.error("**Recommendation:** Transformer Upgrade Required for 2026 Capacity.")
    elif status == "FEASIBLE": st.warning("**Recommendation:** Viable, but grid stress observed. Requires IESO connection assessment.")
    else: st.success("**Recommendation:** Grid Node appears highly viable for development.")
        
with col2:
    with st.expander("🗺️ Map Legend", expanded=True):
        st.markdown("""
        - 🟩 **Substation (Green):** Highly Viable / Excellent Headroom
        - 🟧 **Substation (Orange):** Feasible / Moderate Stress
        - 🟥 **Substation (Red):** High Risk / Upgrade Required
        - 🟡 **Generation Source:** Existing Power Generation
        - 🟥 **Column (Dark Red):** Existing Data Centres
        - 🟢 **Pulse Point (Bright Green):** Proposed Data Centre Location
        - 🟡 〰️ 🔵 **Arc Lines:** Network Flow
        """)

st.markdown("---")
st.caption(f"**Technical Note:** Calculations incorporate a 1.15 Safety Factor and I²R Estimated Heat Loss of **{losses:.4f} MW**, alongside a Monte Carlo simulation using a Triangular Distribution (40% min, 70% typical, 100% peak ambient load).")
