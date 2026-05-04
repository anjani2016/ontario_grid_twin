import streamlit as st
import pandas as pd

# Check if data is loaded (optional for this static-ish page, but good for consistency)
if 'data_loaded' not in st.session_state:
    st.warning("Application data is not yet initialized. Return to Home to load data if needed.")

def render_project_charter():
    st.title("📋 Project Charter: Ontario Grid Digital Twin")
    st.subheader("Substation Reliability & Data Centre Impact Analysis")
    
    st.markdown("""
    **Purpose:** To provide a high-fidelity simulation environment for evaluating the 
    interconnection of hyperscale data centres within the Ontario power grid.
    """)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🛠️ Technical Stack")
        st.write("- **Language:** Python 3.11")
        st.write("- **Simulation:** NumPy (Monte Carlo)")
        st.write("- **GIS:** GeoPandas & PyDeck")
    
    with col2:
        st.markdown("### 📊 Methodology")
        st.write("- Probabilistic Risk Assessment")
        st.write("- Non-Linear Cooling Efficiency")
        st.write("- Multi-Source Data Harmonization")

    st.divider()

    st.markdown("### 🔍 Verified Data Sources")
    sources_data = {
        "Category": ["Project Locations", "Project Demand", "Grid Capacity", "Climate Data"],
        "Source": ["Baxtel.com", "National Observer", "IESO Projections", "Open-Meteo API"],
        "Details": ["Verified Site Maps", "2,202 MW Proposed", "2026 Peak Projections", "Historical Temp Profiles"]
    }
    st.table(pd.DataFrame(sources_data))

    st.divider()
    st.markdown("### ❄️ Cooling Efficiency Reference")
    st.info("Model: Non-Linear Evaporative Cooling with an 8% Fixed Cooling Floor.")
    
    efficiency_data = [
        {"Range": "10 to 20°C", "Savings": "10%", "Mode": "Evaporative Support"},
        {"Range": "0 to 10°C", "Savings": "30%", "Mode": "Partial Free Cooling"},
        {"Range": "-10 to 0°C", "Savings": "50%", "Mode": "Full Free Cooling"},
        {"Range": "-20 to -10°C", "Savings": "70%", "Mode": "Peak Efficiency"}
    ]
    st.dataframe(pd.DataFrame(efficiency_data), use_container_width=True)

    st.caption("Developed by: Centauri Research / Advanced Grid Engineering")

if __name__ == "__main__":
    render_project_charter()