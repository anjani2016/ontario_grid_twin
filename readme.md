help file to execute the project

# Ontario Data Centre & Grid Capacity Digital Twin


# Project Framework: Ontario Grid Digital Twin

## Purpose
The purpose of this project is to assist in high‑level engineering tasks including writing, fixing, and understanding code for power‑grid simulations.  
The assistant supports the development of code required to model the impact of hyperscale data centres on the Ontario power grid.

## Goals
- **Code Creation:** Generate complete, functional code to achieve simulation goals.  
- **Education:** Explain the steps involved in code development to enhance user understanding.  
- **Clear Instructions:** Provide easy‑to‑understand implementation guides for building and running the code.  
- **Thorough Documentation:** Document each part of the code and logic clearly.

---

## 1. Project Overview
This project is a **Capacity-Demand Digital Twin** designed to evaluate the feasibility of connecting high-load Data Centres to Ontario's electrical grid. By intersecting 2026 IESO (Independent Electricity System Operator) forecast data with geospatial infrastructure maps, the tool identifies "Optimal Zones" where high headroom, low transmission loss, and grid reliability align.

---

## Key Development Pillars

### 1. Probabilistic Modeling
Transitioning from hardcoded peak loads to **Triangular Distributions**  


\[
(min,\ mode,\ max)
\]

  
to more accurately reflect grid reliability and uncertainty.

### 2. Real‑World Data Integration
Replacing synthetic dummy data with real project data from:
- **Baxtel** (data centre locations)
- **National Observer** (demand figures and reporting)

### 3. Climate Efficiency Modeling
Implementing **non‑linear cooling models** for evaporative systems based on ambient temperature brackets.

### 4. Grid Reliability
Calculating:
- **Available Headroom**  
- **Risk probabilities**  
for substations such as the **Claireville–York Junction** and others.

---

## Technical Stack & Sources

### Languages & Libraries
- **Python**
  - NumPy  
  - Pandas  
  - GeoPandas  
  - Streamlit  

### Data Sources
- **Project Locations:** Baxtel.com/map  
- **Demand Figures:** National Observer  
- **Weather Data:** Open‑Meteo API  
- **Efficiency Logic:** ASHRAE TC 9.9 Thermal Guidelines  

---

## Cooling Efficiency Reference Table

| Temperature Range (°C) | Cooling Mode             | Savings Factor |
|------------------------|--------------------------|----------------|
| 10 to 20               | Evaporative Support      | 10%            |
| 0 to 10                | Partial Free Cooling     | 30%            |
| -10 to 0               | Full Free Cooling        | 50%            |
| -20 to -10             | Peak Efficiency          | 70%            |

**Engineering Note:**  
A mandatory **8% cooling floor** is integrated into the code to account for internal fan power and heat rejection, even in extreme cold.

---



### 2. Overview the Solution
Review:
- development steps  
- mathematical assumptions  
- reliability logic  
before running the simulation.

### 3. Deploy Code
Copy the modular blocks for:
- Monte Carlo sampling  
- Climate ingestion  
- Headroom calculation  
into your `app.py` environment.

---





### Key Features
*   **Geospatial Mapping:** Visualization of 230kV and 500kV transmission infrastructure in the York Region.
*   **Headroom Engine:** Regional load distribution based on the IESO 2026 Annual Planning Outlook (APO).
*   **Stochastic Simulation:** 1,000-iteration Monte Carlo stress tests to determine node reliability.
*   **Loss Analysis:** Real-time calculation of $I^2R$ transmission losses.

---

## 2. Technical Stack
*   **Language:** Python 3.11+
*   **GIS Libraries:** `GeoPandas`, `Shapely`, `Pydeck`
*   **Data Science:** `Pandas`, `NumPy`
*   **Dashboard:** `Streamlit`
*   **Storage:** `Apache Parquet` (via `pyarrow`) for high-performance geospatial querying.

---

## 3. Project Structure
```text




- **Notes**
### Folder Structure

ontario_grid_twin/
├── setup_workspace.py   <-- Save the code here
├── data/
│   ├── raw/            # NRCan, IESO, and OSM files
│   └── processed/      # Cleaned GeoParquet files for DuckDB
├── src/
│   ├── engine/         # Headroom and Loss calculation logic
│   ├── utils/          # GIS and distance helpers
│   └── app.py          # Streamlit Dashboard
├── requirements.txt
└── .env                # For API keys (if using Mapbox for Lonboard)





- 





