import streamlit as st
import pandas as pd
from engine.data_loader import load_base_grid, load_dc_projects, get_grid_nodes

# 1. Page Configuration
st.set_page_config(
    page_title="Ontario Grid Digital Twin",
    page_icon="⚡",
    layout="wide"
)

# 2. Sidebar Branding
try:
    st.sidebar.image("data/assets/CR_logo.png", use_container_width=True)
except Exception:
    pass
st.sidebar.title("Digital Twin Navigation")

# 3. Global Data Initialization (Loaded into Session State for cross-page access)
if 'data_loaded' not in st.session_state:
    with st.spinner("Initializing Digital Twin Engine..."):
        subs, lines, gen, dc = load_base_grid()
        projects, provincial_interest_mw, dc_source = load_dc_projects()
        grid_nodes = get_grid_nodes(subs)
        
        st.session_state['subs'] = subs
        st.session_state['lines'] = lines
        st.session_state['gen'] = gen
        st.session_state['dc'] = dc
        st.session_state['projects'] = projects
        st.session_state['provincial_interest_mw'] = provincial_interest_mw
        st.session_state['dc_source'] = dc_source
        st.session_state['grid_nodes'] = grid_nodes
        st.session_state['data_loaded'] = True

# 4. Landing Page: Project Charter
st.title("📋 Project Charter: Ontario Grid Digital Twin")
st.subheader("Substation Reliability & Data Centre Impact Analysis")

st.markdown("""
**Purpose:** To provide a high-fidelity simulation environment for evaluating the 
interconnection of hyperscale data centres within the Ontario power grid, 
specifically focusing on the York Region.

Use the sidebar to navigate between the **Interactive Grid Map**, **Monte Carlo Risk Analytics**, 
and **Data Centre Project Outlook**.
""")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🛠️ Technical Stack")
    st.write("- **Language:** Python 3.11")
    st.write("- **Simulation:** NumPy (Monte Carlo / Triangular Distribution)")
    st.write("- **GIS:** GeoPandas, PyDeck (CartoDB Spatial Engine)")
    st.write("- **UI:** Streamlit Multi-Page Architecture")

with col2:
    st.markdown("### 📊 Methodology")
    st.write("- **Reliability:** Probabilistic Risk Assessment (Monte Carlo)")
    st.write("- **Cooling:** Non-Linear Climate Efficiency (ASHRAE TC 9.9)")
    st.write("- **Data:** Real-world National Observer & Baxtel Integration")

st.divider()

st.markdown("### 🔍 Verified Data Sources")
sources_data = {
    "Category": ["Project Locations", "Project Demand", "Grid Capacity", "Climate Data"],
    "Source": ["Baxtel.com", "National Observer", "IESO Projections", "Open-Meteo API"],
    "Details": ["Verified Site Maps", "2,202 MW Proposed", "2026 Peak Projections", "Historical Temp Profiles"]
}
st.table(pd.DataFrame(sources_data))

st.info("💡 **Getting Started:** Select 'Interactive Grid Map' from the sidebar to begin simulating grid impact.")

st.caption("Developed by: Centauri Research / Advanced Grid Engineering")
st.caption("Reference Date: May 2026")
