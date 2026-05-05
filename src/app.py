import streamlit as st
from engine.data_loader import load_base_grid, load_dc_projects, get_grid_nodes
from utils.ui_branding import apply_branding

# 1. Page Configuration
st.set_page_config(
    page_title="Ontario Grid Digital Twin",
    page_icon="⚡",
    layout="wide"
)

# 2. Global branding
apply_branding()

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

# 4. Landing Page: Home
st.title("⚡ Ontario Grid Digital Twin")
st.subheader("Interactive planning workspace for substation reliability and large step load assessment")

st.markdown("""
Use this dashboard to evaluate where large new loads are most feasible by combining:
- substation headroom and probabilistic reliability modeling
- generation-source visibility and regional filtering
- project portfolio views for planned data-centre demand

Navigate from the sidebar to:
- **Interactive Grid Map** for node-level simulation and map overlays
- **Monte Carlo Risk Analytics** for reliability distribution analysis
- **Data Centre Project Outlook** for project pipeline and growth views
- **Project Charter** for methodology, assumptions, and source references
""")

st.divider()

st.info("💡 **Getting Started:** Open `Interactive Grid Map`, select a region and target substation, then tune simulated load to compare reliability outcomes.")

st.caption("Developed by: Centauri Research / Advanced Grid Engineering")
st.caption("Reference Date: May 2026")
