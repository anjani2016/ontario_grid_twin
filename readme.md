help file to execute the project

# Ontario Data Centre & Grid Capacity Digital Twin

## 1. Project Overview
This project is a **Capacity-Demand Digital Twin** designed to evaluate the feasibility of connecting high-load Data Centres to Ontario's electrical grid. By intersecting 2026 IESO (Independent Electricity System Operator) forecast data with geospatial infrastructure maps, the tool identifies "Optimal Zones" where high headroom, low transmission loss, and grid reliability align.

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
ontario_grid_twin/
├── data/
│   ├── raw/            # IESO forecasts and raw GIS Parquet files
│   └── processed/      # Analyzed substation data with headroom metrics
├── src/
│   ├── engine/         # Logic for Capacity Analysis and DC Simulation
│   ├── utils/          # Data harvesting and grid generation scripts
│   └── app.py          # Streamlit Dashboard UI
├── README.md
└── requirements.txt



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



### Notes on requirements.txt 

- include libraries needed

### Virtual Environment - creation , activation and installation of requirments

- check pyenv python versions ```pyenv versions```

- Navigate to your project ```cd path/to/your/project```

- Set the local version for this folder ```pyenv local 3.11.9``` . select the version needed. the requirements need 3.11+

- 

- Create the environment folder with a specific version of python (<3.11>) to ensure ydata-profiling runs ``` python3.11 -m venv etrans_env```

- Activate it (Windows) ``` .\energy_env_p3.11\Scripts\activate```

- OR Activate it (Mac/Linux) ``` source etrans_env/bin/activate ```

- install your requirements: ``` pip install -r requirements.txt```

- check dependancies installed ```pip list```

- check installation of specific library ```pip show pandas```

- Clean Up if needed: Run this to clear out any half-installed junk: ```pip cache purge

- Re-install your requirements: ```pip install --force-reinstall -r requirements.txt


- virtual environment

- Create a virtual environment: Open your terminal, navigate to your project directory and run ``` python3 -m venv .venv ```

- Activate the environment:  ``` source risk_env/bin/activate ```



- Install packages with a requirements.txt file - preferable  ``` pip install -r requirements.txt ```


- Run ```python setup_workspace.py``` to setup the work folders

- extract data . Run ```python src/utils/data_harvester.py```

- Verify: Check your data/raw/ folder. You should now see:

    - ontario_lines.parquet

    - york_substations.parquet

    - ieso_2026_forecast.csv

