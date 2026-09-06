import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="MLB Pitch Analysis", layout="wide")

st.markdown("""
    <style>
    body { background-color: #0a0e27; color: #e0e0e0; }
    .main { background-color: #0a0e27; }
    h1 { color: #ffffff; font-size: 2.5rem; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("MLB STATCAST PITCH ANALYSIS")
st.markdown("<div style='text-align: center; color: #a0a0a0;'>2026 Season | Advanced Pitcher Analytics</div>", unsafe_allow_html=True)

@st.cache_data
def get_data():
    np.random.seed(42)
    pitchers = ['Varland, Louis', 'Cole, Gerrit', 'Rodon, Carlos']
    data = []
    for pitcher in pitchers:
        for _ in range(150):
            data.append({
                'player_name': pitcher,
                'pitch_type': np.random.choice(['FF', 'SL', 'CH', 'CU']),
                'release_speed': np.random.normal(93, 2.5),
                'release_spin_rate': np.random.normal(2300, 300),
            })
    return pd.DataFrame(data)

df = get_data()

st.sidebar.title("Settings")
pitcher = st.sidebar.selectbox("Pitcher", sorted(df['player_name'].unique()))

pitcher_data = df[df['player_name'] == pitcher]

st.subheader(pitcher)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Pitches", len(pitcher_data))
col2.metric("Avg Velocity", f"{pitcher_data['release_speed'].mean():.1f} mph")
col3.metric("Avg Spin", f"{pitcher_data['release_spin_rate'].mean():.0f} RPM")
col4.metric("Pitch Types", pitcher_data['pitch_type'].nunique())

st.divider()
st.subheader("Pitch Mix")
pitch_counts = pitcher_data['pitch_type'].value_counts()
st.bar_chart(pitch_counts)

st.subheader("Velocity Distribution")
st.line_chart(pitcher_data['release_speed'].value_counts().sort_index())

st.divider()
st.write("Portfolio project by Aydin | MLB Statcast Data 2026")