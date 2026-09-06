import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="MLB Pitch Analysis", layout="wide")

st.markdown("""
    <style>
    body { background-color: #0a0e27; color: #e0e0e0; }
    .main { background-color: #0a0e27; }
    h1 { color: #ffffff; font-size: 2.5rem; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>MLB STATCAST PITCH ANALYSIS</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #a0a0a0;'>2026 Season | Advanced Pitcher Analytics</div>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    np.random.seed(42)
    return pd.DataFrame({
        'player_name': np.random.choice(['Varland, Louis', 'Cole, Gerrit', 'Rodon, Carlos'], 500),
        'pitch_type': np.random.choice(['FF', 'SL', 'CH', 'CU'], 500),
        'release_speed': np.random.normal(93, 2.5, 500),
        'release_spin_rate': np.random.normal(2300, 300, 500),
        'pfx_x': np.random.normal(0, 10, 500),
        'pfx_z': np.random.normal(20, 8, 500),
    })

df = load_data()

st.sidebar.title("Settings")
pitcher = st.sidebar.selectbox("Select Pitcher", sorted(df['player_name'].unique()))

data = df[df['player_name'] == pitcher]

st.subheader(pitcher)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Pitches", len(data))
with col2:
    st.metric("Avg Velocity", f"{data['release_speed'].mean():.1f} mph")
with col3:
    st.metric("Avg Spin Rate", f"{data['release_spin_rate'].mean():.0f} RPM")

st.markdown("---")
st.subheader("Pitch Type Distribution")
pitch_mix = data['pitch_type'].value_counts()
fig = px.pie(values=pitch_mix.values, names=pitch_mix.index, height=400)
fig.update_layout(template='plotly_dark', paper_bgcolor='#0f1429')
st.plotly_chart(fig, use_container_width=True)

st.subheader("Velocity vs Spin Rate")
fig2 = px.scatter(data, x='release_speed', y='release_spin_rate', color='pitch_type', height=400)
fig2.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429')
st.plotly_chart(fig2, use_container_width=True)

st.markdown("<p style='text-align: center; color: #666;'>MLB Statcast | 2026 Season</p>", unsafe_allow_html=True)