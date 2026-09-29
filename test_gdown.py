import streamlit as st
import gdown
import tempfile
import os
import pandas as pd

st.title("Test gdown Download")

statcast_id = "1jxHScV07VtIvLjqZrct5zBJQYDnBwYKj"

st.write("Attempting to download with gdown...")

with tempfile.TemporaryDirectory() as tmpdir:
    statcast_path = os.path.join(tmpdir, 'statcast.csv')
    
    # Download
    gdown.download(f'https://drive.google.com/uc?id={statcast_id}', statcast_path, quiet=False)
    
    # Check file size
    file_size = os.path.getsize(statcast_path)
    st.write(f"Downloaded file size: {file_size:,} bytes")
    
    # Try to read it
    try:
        df = pd.read_csv(statcast_path, nrows=5)
        st.success(f"✓ Successfully read CSV with {len(df.columns)} columns")
        st.write("Columns:")
        st.write(list(df.columns))
        st.write("First few rows:")
        st.dataframe(df)
    except Exception as e:
        st.error(f"✗ Error reading CSV: {e}")
        
        # Show first 500 chars of file
        with open(statcast_path, 'r') as f:
            content = f.read(500)
        st.write("First 500 characters of file:")
        st.code(content)