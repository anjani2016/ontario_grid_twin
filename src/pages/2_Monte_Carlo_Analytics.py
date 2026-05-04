import streamlit as st
import plotly.express as px
import numpy as np

if 'data_loaded' not in st.session_state:
    st.error("Please return to the [Home Page](../main.py) to initialize the application data.")
    st.stop()

subs = st.session_state['subs']
grid_nodes = st.session_state['grid_nodes']

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
    fig.add_vline(x=node.capacity_mw, line_dash="dash", line_color="red", 
                  annotation_text=f"Max Capacity ({node.capacity_mw} MW)", annotation_position="top right")
    fig.update_layout(xaxis_title="Total Projected Load (MW)", yaxis_title="Frequency")
    st.plotly_chart(fig, use_container_width=True)
