import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import os
from engine.grid_model import GridNode

@st.cache_data
def load_base_grid():
    """
    Loads substation, line, generation, and existing DC data.
    """
    subs_path = 'data/processed/analyzed_substations.parquet'
    lines_path = 'data/raw/ontario_lines.parquet'
    gen_path = 'data/raw/generation_sources.parquet'
    dc_path = 'data/raw/existing_dc.parquet'
    
    # Substations
    subs = gpd.read_parquet(subs_path).to_crs(epsg=4326)
    subs['lon'] = subs.geometry.x
    subs['lat'] = subs.geometry.y
    
    # Optional files
    lines = gpd.read_parquet(lines_path).to_crs(epsg=4326) if os.path.exists(lines_path) else None
    
    gen = None
    if os.path.exists(gen_path):
        gen = gpd.read_parquet(gen_path).to_crs(epsg=4326)
        gen['lon'] = gen.geometry.x
        gen['lat'] = gen.geometry.y
        
    dc = None
    if os.path.exists(dc_path):
        dc = gpd.read_parquet(dc_path).to_crs(epsg=4326)
        dc['lon'] = dc.geometry.x
        dc['lat'] = dc.geometry.y
    
    return subs, lines, gen, dc

@st.cache_data
def load_dc_projects():
    """
    Loads Ontario data centre project data (Baxtel or National Observer).
    """
    PROVINCIAL_INTEREST_MW = 6500.0
    BAXTEL_PATH = 'data/raw/baxtel_projects.parquet'

    def categorize_type(mw):
        if pd.isna(mw):      return 'Unknown'
        if mw <= 50:         return 'Mid-Tier (≤50 MW)'
        if mw <= 150:        return 'Large (50–150 MW)'
        return 'Hyperscale (>150 MW)'

    if os.path.exists(BAXTEL_PATH):
        try:
            gdf = gpd.read_parquet(BAXTEL_PATH)
            df = pd.DataFrame(gdf.drop(columns='geometry', errors='ignore'))
            for col, default in [('capacity_mw', float('nan')), ('status', 'Identified'),
                                  ('year', 2026), ('region', 'Ontario')]:
                if col not in df.columns:
                    df[col] = default
            df['year'] = df['year'].fillna(2026).astype(int)
            df['capacity_mw'] = pd.to_numeric(df['capacity_mw'], errors='coerce')
            df['Type'] = df['capacity_mw'].apply(categorize_type)
            return df, PROVINCIAL_INTEREST_MW, 'Baxtel'
        except Exception:
            pass

    # Fallback: National Observer
    TOTAL_PROPOSED_CAPACITY_MW = 2202.0
    avg = round((TOTAL_PROPOSED_CAPACITY_MW - 217) / 11, 1)
    
    # Construction of project list (Fixed + Simulated)
    real_projects = [
        {'name': 'Cambridge Data Centre 1',     'capacity_mw': 45.0,  'region': 'Cambridge', 'year': 2026, 'status': 'Proposed'},
        {'name': 'Cambridge Data Centre 2',     'capacity_mw': 45.0,  'region': 'Cambridge', 'year': 2026, 'status': 'Proposed'},
        {'name': 'Microsoft Vaughan Expansion', 'capacity_mw': 100.0, 'region': 'York',      'year': 2026, 'status': 'Under Review'},
        {'name': 'Yondr Toronto',               'capacity_mw': 27.0,  'region': 'Toronto',   'year': 2027, 'status': 'Proposed'}
    ] + [
        {'name': f'Observer Project {i} (Avg)', 'capacity_mw': avg,   'region': 'Various',   'year': 2027 if i<3 else (2028 if i<7 else 2029), 'status': 'Identified'}
        for i in range(1, 12)
    ]
    
    df = pd.DataFrame(real_projects)
    df['Type'] = df['capacity_mw'].apply(categorize_type)
    return df, PROVINCIAL_INTEREST_MW, 'National Observer (Mar 2026)'

def get_grid_nodes(subs):
    """
    Initializes GridNode objects for all substations.
    """
    grid_nodes = {}
    for idx, row in subs.iterrows():
        v_val = 230
        if 'voltage' in row and pd.notnull(row['voltage']):
            try:
                v_val = int(str(row['voltage']).replace('kV', '').strip())
            except ValueError:
                pass
        cap = float(row.get('capacity_mw', 1000))
        b_load = cap - row['headroom_mw'] if 'headroom_mw' in row else float(row.get('current_load_mw', 800))
        grid_nodes[row['name']] = GridNode(name=row['name'], capacity_mw=cap, base_load_mw=b_load, voltage_kv=v_val)
    return grid_nodes
