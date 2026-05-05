# Ontario Grid Digital Twin

Capacity-demand digital twin for screening large new electrical loads (e.g., data centres) against Ontario grid constraints.

## Purpose

This project provides a planning-grade interactive environment to evaluate:

- substation headroom and reliability under incremental load
- regional generation visibility and capacity context
- portfolio-level data-centre demand outlooks

The app is intended for scenario screening, not final interconnection approval.

## Current Capabilities

- **Interactive Grid Map** (`src/pages/1_Interactive_Grid_Map.py`)
  - Substation selection with simulated added MW load
  - Reliability status, headroom metrics, and map-based overlays
  - Generation source category filters with dynamic capacity display
  - Region filter that scopes both substations and generation layers
- **Monte Carlo Analytics** (`src/pages/2_Monte_Carlo_Analytics.py`)
  - Triangular-distribution load simulation and risk visualization
- **Data Centre Outlook** (`src/pages/3_Data_Centres_Projected.py`)
  - Pipeline filtering by region/year/status/type
- **Project Charter** (`src/pages/0_Project_Charter.py`)
  - Updated methodology, assumptions, and source references

## Technical Stack

- **Language:** Python 3.11
- **App/UI:** Streamlit multi-page app
- **Data + Simulation:** Pandas, NumPy
- **Geospatial:** GeoPandas, Shapely, PyDeck
- **Storage:** Parquet / GeoParquet (`pyarrow`)
- **Runtime:** local virtual environment (`etrans_env`)

## Methodology Snapshot

- **Reliability modeling:** Monte Carlo simulation with triangular load profile
- **Headroom logic:** `capacity_mw - (current_load_mw * safety_factor)`
- **Loss proxy:** I2R-style incremental stress estimate
- **Cooling context:** non-linear free-cooling logic with fixed minimum floor
- **Regional coherence:** shared region filter across substation and generation layers

## Data Sources (Current Project State)

- **IESO public reports** (transmission limits XML feed) for demo substation synthesis
- **Local generation source dataset** (`data/raw/generation_sources.parquet`)
- **Data-centre project datasets** (Baxtel and National Observer-derived)
- **IESO planning context** (`data/raw/ieso_2026_forecast.csv`)
- **IESO technical reference**: Large Step Loads paper (Figure 3 integrated in charter page)
- **Open-Meteo** for climate context

## Demo Substation Data Note

The project currently supports a demo IESO-derived substation dataset:

- Builder: `data/raw/build_ieso_substations_demo.py`
- Output: `data/raw/ieso_substations_demo.parquet`

This dataset triangulates coordinates from inferred region/city context because IESO public feeds do not provide a clean geocoded station master in the current integration path.

When clean geocoded substation data becomes available, replace the demo parquet and keep the same required fields:

- `name`, `region`, `capacity_mw`, `current_load_mw`, `headroom_mw`, `geometry` (EPSG:4326)

## Running the App

From repo root:

```bash
source etrans_env/bin/activate
streamlit run src/app.py
```

## Repository Structure

```text
ontario_grid_twin/
├── data/
│   ├── raw/                # source and intermediate datasets
│   └── processed/          # analyzed/derived datasets
├── src/
│   ├── app.py              # Streamlit entrypoint
│   ├── engine/             # loaders and simulation engine
│   ├── pages/              # Streamlit pages
│   └── utils/              # data harvesters and helpers
├── tests/
├── requirements.txt
└── CHANGELOG.md
```
