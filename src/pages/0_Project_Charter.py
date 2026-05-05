import streamlit as st
import pandas as pd
from utils.ui_branding import apply_branding

apply_branding()

# Check if data is loaded (optional for this static-ish page, but good for consistency)
if 'data_loaded' not in st.session_state:
    st.warning("Application data is not yet initialized. Return to Home to load data if needed.")

def render_project_charter():
    st.title("📋 Project Charter: Ontario Grid Digital Twin")
    st.subheader("Capacity-demand digital twin for large step load interconnection screening")
    
    st.markdown("""
    **Purpose:** Provide a practical planning-grade sandbox to evaluate where large
    new loads (e.g., data centres) can be connected with acceptable reliability risk,
    available headroom, and transparent engineering assumptions.
    """)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🛠️ Technical Stack")
        st.write("- **Language:** Python 3.11")
        st.write("- **App Framework:** Streamlit multi-page architecture")
        st.write("- **Data + Analytics:** Pandas, NumPy")
        st.write("- **Geospatial:** GeoPandas, Shapely, PyDeck")
        st.write("- **Storage:** Parquet/GeoParquet")
        st.write("- **Data Ingestion:** IESO public XML feeds + local curated datasets")
    
    with col2:
        st.markdown("### 📊 Methodology")
        st.write("- **Probabilistic Reliability:** Monte Carlo simulation with triangular load profile")
        st.write("- **Electrical Stress Proxy:** I²R-based loss estimation for incremental load impact")
        st.write("- **Headroom Logic:** Capacity minus safety-adjusted base load")
        st.write("- **Cooling Context:** Non-linear free-cooling efficiency with 8% floor")
        st.write("- **Regional Planning Lens:** Linked substation + generation filtering by region")

    st.divider()

    st.markdown("### 🔍 Verified Data Sources")
    sources_data = {
        "Category": [
            "Substation/Transmission Operating Context",
            "Generation Fleet Layer",
            "Data Centre Project Pipeline",
            "Regional Demand Outlook",
            "Planning Method Reference",
            "Climate Context",
        ],
        "Source": [
            "IESO Public Reports (Tx Limits XML)",
            "IESO-aligned generation source dataset (local curated parquet)",
            "Baxtel + National Observer",
            "IESO 2026 forecast template (project data file)",
            "IESO Large Step Loads Technical Paper (Jul 2025)",
            "Open-Meteo API",
        ],
        "Details": [
            "Transmission interface limits used for demo substation synthesis",
            "Category/fuel/capacity map layer used in network visualization",
            "Project-level capacity and status used in outlook analytics",
            "Regional peak demand/capacity assumptions for scenario framing",
            "Figure 3 schematic embedded for planning process reference",
            "Temperature context used for cooling-efficiency interpretation",
        ]
    }
    st.table(pd.DataFrame(sources_data))

    st.divider()
    st.markdown("### 🧭 IESO Large Step Loads Schematic")
    st.caption(
        "Reference: IESO Demand & Conservation Planning Technical Paper - Large Step Loads (July 2025), "
        "Figure 3 (page 7)."
    )
    # Internal note: this image is rendered from a local PDF snapshot for demo reproducibility.
    # Replace with a clean, versioned asset workflow if/when IESO provides a canonical image endpoint.
    st.image(
        "data/assets/datacentre_components.png",
        caption="Figure 3 - Large Step Loads planning schematic (IESO, Jul 2025)",
        use_container_width=True,
    )
    st.markdown(
        "[View source document (IESO PDF)]"
        "(https://www.ieso.ca/-/media/Files/IESO/Document-Library/planning-forecasts/demand-research/"
        "Demand-Conservation-Planning-Technical-Paper-Large-Step-Loads-202507.pdf)"
    )

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