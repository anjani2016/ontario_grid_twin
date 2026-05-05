# Project Charter: Ontario Grid Digital Twin

## Mission

Build and maintain a practical digital twin to screen large electrical load interconnections in Ontario using transparent assumptions, traceable data sources, and reproducible workflows.

## Scope

In scope:

- substation reliability screening under incremental load
- headroom and stress indicators for planning scenarios
- regional generation visibility and capacity context
- data-centre project demand outlook integration

Out of scope:

- final interconnection approval studies
- full power-flow or transient stability studies
- market dispatch optimization

## Current Architecture

- `src/app.py` initializes shared datasets into Streamlit session state
- `src/engine/data_loader.py` handles grid/project data loading and normalization
- `src/pages/1_Interactive_Grid_Map.py` provides node-level map simulation
- `src/pages/2_Monte_Carlo_Analytics.py` provides reliability distribution analysis
- `src/pages/3_Data_Centres_Projected.py` provides project pipeline outlook
- `src/pages/0_Project_Charter.py` documents methodology and planning references

## Technical Stack

- Python 3.11
- Streamlit (multi-page)
- Pandas, NumPy
- GeoPandas, Shapely, PyDeck
- Parquet/GeoParquet storage

## Methodology

- Monte Carlo reliability simulation with triangular demand assumptions
- headroom estimation with safety-factor-adjusted baseline loading
- I2R-based loss proxy to indicate incremental electrical stress
- climate-aware cooling context with non-linear efficiency and floor
- regional coherence via shared region filters for substation + generation views

## Data Sources and Provenance

- IESO public transmission limits feed (XML) for demo substation synthesis
- local generation fleet parquet (`data/raw/generation_sources.parquet`)
- data-centre project datasets (Baxtel + National Observer path)
- project planning context (`data/raw/ieso_2026_forecast.csv`)
- IESO Large Step Loads technical paper (Figure 3 used in charter page)
- Open-Meteo context for cooling interpretation

## Demo Data Constraint

Current IESO-linked substation dataset is demo-oriented:

- builder: `data/raw/build_ieso_substations_demo.py`
- output: `data/raw/ieso_substations_demo.parquet`
- coordinates are triangulated from inferred region/city cues for visualization only

### Migration Path to Production-Grade Substation Data

When clean geocoded station data is available:

1. replace demo parquet with validated geospatial station source
2. preserve required fields: `name`, `region`, `capacity_mw`, `current_load_mw`, `headroom_mw`, `geometry`
3. retire/archive triangulation logic from demo builder
4. keep loader defaults aligned to the clean source

## Quality and Change Management

- keep assumptions explicit in code comments and charter sections
- reflect material model/data changes in `CHANGELOG.md`
- keep `readme.md` synced with current implementation, not legacy plans
