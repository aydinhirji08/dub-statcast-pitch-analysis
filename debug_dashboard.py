import streamlit as st
import pandas as pd

st.set_page_config(page_title="MLB Statcast Debug", layout="wide")

st.markdown("# Debug: Checking CSV Columns from Google Drive")

# Google Drive FILE IDs
statcast_id = "1jxHScV07VtIvLjqZrct5zBJQYDnBwYKj"
batter_id = "15sCrSvg_b1_pW8piY6PNhoCpBhs529ra"

st.write("Attempting to load statcast_2026.csv...")
try:
    df = pd.read_csv(f"https://drive.google.com/uc?id={statcast_id}")
    st.success(f"✓ Successfully loaded statcast CSV with {len(df)} rows and {len(df.columns)} columns")
    
    st.markdown("### Columns in statcast_2026.csv:")
    st.write(list(df.columns))
    
    st.markdown("### First few rows:")
    st.dataframe(df.head())
    
except Exception as e:
    st.error(f"✗ Error loading statcast CSV: {e}")

st.divider()

st.write("Attempting to load batter_names.csv...")
try:
    batter_names = pd.read_csv(f"https://drive.google.com/uc?id={batter_id}")
    st.success(f"✓ Successfully loaded batter_names CSV with {len(batter_names)} rows and {len(batter_names.columns)} columns")
    
    st.markdown("### Columns in batter_names.csv:")
    st.write(list(batter_names.columns))
    
    st.markdown("### First few rows:")
    st.dataframe(batter_names.head())
    
except Exception as e:
    st.error(f"✗ Error loading batter_names CSV: {e}")