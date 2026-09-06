import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="MLB Pitch Analysis System", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    body { background-color: #0a0e27; color: #e0e0e0; }
    .main { background-color: #0a0e27; padding: 20px; }
    [data-testid="stSidebar"] { background-color: #1a1f3a; }
    h1 { color: #ffffff; font-size: 2.5rem; font-weight: 700; text-align: center; }
    h2 { color: #e8f4f8; font-size: 1.6rem; font-weight: 600; margin-top: 30px; border-bottom: 2px solid #1f77b4; padding-bottom: 10px; }
    .divider { background-color: #2d3561; height: 1px; margin: 30px 0; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>MLB STATCAST PITCH ANALYSIS</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #a0a0a0;'>2026 Season | Advanced Pitcher Analytics</div>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    np.random.seed(42)
    pitchers = ['Varland, Louis', 'Cole, Gerrit', 'Rodon, Carlos', 'Burnes, Corbin', 'Alcantara, Sandy']
    pitch_types = ['FF', 'SL', 'CH', 'CU', 'SI']
    
    data = {
        'player_name': np.random.choice(pitchers, 1500),
        'pitch_type': np.random.choice(pitch_types, 1500),
        'release_speed': np.random.normal(93, 2.5, 1500),
        'release_spin_rate': np.random.normal(2300, 300, 1500),
        'pfx_x': np.random.normal(0, 10, 1500),
        'pfx_z': np.random.normal(20, 8, 1500),
        'balls': np.random.randint(0, 4, 1500),
        'strikes': np.random.randint(0, 3, 1500),
        'stand': np.random.choice(['R', 'L'], 1500),
        'events': np.random.choice(['strikeout', 'walk', 'single', 'double', None], 1500, p=[0.15, 0.1, 0.25, 0.2, 0.3]),
        'description': np.random.choice(['swinging_strike', 'called_strike', 'ball', 'foul'], 1500),
        'game_pk': np.random.randint(600000, 700000, 1500),
        'batter': np.random.randint(100000, 900000, 1500),
        'pitcher': np.random.randint(100000, 900000, 1500),
        'inning': np.random.randint(1, 10, 1500)
    }
    return pd.DataFrame(data)

df = load_data()

def calculate_metrics(data):
    total_pitches = len(data)
    k_atbats = data[data['events'].str.contains('strikeout', case=False, na=False)].groupby(['game_pk', 'pitcher', 'batter', 'inning']).size()
    k_count = len(k_atbats)
    total_atbats = data[data['events'].notna()].groupby(['game_pk', 'pitcher', 'batter', 'inning']).size()
    total_ab_count = len(total_atbats)
    k_rate = (k_count / total_ab_count * 100) if total_ab_count > 0 else 0
    bb_atbats = data[data['events'].str.contains('walk', case=False, na=False)].groupby(['game_pk', 'pitcher', 'batter', 'inning']).size()
    bb_count = len(bb_atbats)
    bb_rate = (bb_count / total_ab_count * 100) if total_ab_count > 0 else 0
    whiff_count = len(data[data['description'].str.contains('swinging_strike', case=False, na=False)])
    whiff_rate = (whiff_count / total_pitches * 100) if total_pitches > 0 else 0
    return {'total_pitches': total_pitches, 'total_atbats': total_ab_count, 'k_rate': k_rate, 'walk_rate': bb_rate, 'whiff_rate': whiff_rate}

st.sidebar.markdown("## Analysis Settings")
all_pitchers = sorted(df['player_name'].dropna().unique())
analysis_mode = st.sidebar.radio("Mode", ["Single Pitcher", "Compare Pitchers"])

if analysis_mode == "Compare Pitchers":
    st.markdown("<h2>Pitcher Comparison</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        pitcher_1 = st.selectbox("First Pitcher", all_pitchers, key="p1")
    with col2:
        pitcher_2 = st.selectbox("Second Pitcher", all_pitchers, key="p2", index=1)
    
    if pitcher_1 == pitcher_2:
        st.warning("Select two different pitchers")
    else:
        p1_data = df[df['player_name'] == pitcher_1].dropna(subset=['release_speed', 'pitch_type', 'balls', 'strikes', 'stand'])
        p2_data = df[df['player_name'] == pitcher_2].dropna(subset=['release_speed', 'pitch_type', 'balls', 'strikes', 'stand'])
        p1_metrics = calculate_metrics(p1_data)
        p2_metrics = calculate_metrics(p2_data)
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pitches", f"{p1_metrics['total_pitches']:,} vs {p2_metrics['total_pitches']:,}")
        with col2:
            st.metric("K Rate", f"{p1_metrics['k_rate']:.1f}% vs {p2_metrics['k_rate']:.1f}%")
        with col3:
            st.metric("BB Rate", f"{p1_metrics['walk_rate']:.1f}% vs {p2_metrics['walk_rate']:.1f}%")
        with col4:
            st.metric("Whiff Rate", f"{p1_metrics['whiff_rate']:.1f}% vs {p2_metrics['whiff_rate']:.1f}%")
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown("## Velocity & Spin")
        col1, col2 = st.columns(2)
        with col1:
            vel_data = pd.DataFrame({'Pitcher': [pitcher_1, pitcher_2], 'Velocity': [p1_data['release_speed'].mean(), p2_data['release_speed'].mean()]})
            fig_vel = px.bar(vel_data, x='Pitcher', y='Velocity', color='Velocity', color_continuous_scale='Reds', height=400)
            fig_vel.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429')
            st.plotly_chart(fig_vel, use_container_width=True)
        with col2:
            spin_data = pd.DataFrame({'Pitcher': [pitcher_1, pitcher_2], 'Spin Rate': [p1_data['release_spin_rate'].mean(), p2_data['release_spin_rate'].mean()]})
            fig_spin = px.bar(spin_data, x='Pitcher', y='Spin Rate', color='Spin Rate', color_continuous_scale='Blues', height=400)
            fig_spin.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429')
            st.plotly_chart(fig_spin, use_container_width=True)

else:
    selected_pitcher = st.sidebar.selectbox("Pitcher", all_pitchers)
    all_pitch_types = sorted(df['pitch_type'].dropna().unique().tolist())
    selected_pitch_types = st.sidebar.multiselect("Pitch Types", all_pitch_types, default=all_pitch_types)
    batter_hand = st.sidebar.radio("Batter", ["All", "Right (RHH)", "Left (LHH)"])
    
    filtered_df = df[(df['player_name'] == selected_pitcher) & (df['pitch_type'].isin(selected_pitch_types))]
    
    if batter_hand == "Right (RHH)":
        filtered_df = filtered_df[filtered_df['stand'] == 'R']
    elif batter_hand == "Left (LHH)":
        filtered_df = filtered_df[filtered_df['stand'] == 'L']
    
    league_df = df[df['pitch_type'].isin(selected_pitch_types)]
    
    st.markdown(f"<h2>{selected_pitcher}</h2>", unsafe_allow_html=True)
    pitcher_metrics = calculate_metrics(filtered_df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pitches", f"{pitcher_metrics['total_pitches']:,}")
    with col2:
        st.metric("K Rate", f"{pitcher_metrics['k_rate']:.1f}%")
    with col3:
        st.metric("BB Rate", f"{pitcher_metrics['walk_rate']:.1f}%")
    with col4:
        st.metric("Whiff Rate", f"{pitcher_metrics['whiff_rate']:.1f}%")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("## Pitch Prediction")
    
    @st.cache_resource
    def train_predictor(pitcher_name):
        pitcher_data = df[df['player_name'] == pitcher_name].dropna(subset=['release_speed', 'pitch_type', 'balls', 'strikes', 'stand'])
        if len(pitcher_data) < 50:
            return None
        pitcher_data['count'] = pitcher_data['balls'].astype(str) + '-' + pitcher_data['strikes'].astype(str)
        le_count = LabelEncoder()
        pitcher_data['count_encoded'] = le_count.fit_transform(pitcher_data['count'])
        le_stand = LabelEncoder()
        pitcher_data['stand_encoded'] = le_stand.fit_transform(pitcher_data['stand'])
        X = np.array(pitcher_data[['release_speed', 'count_encoded', 'stand_encoded']])
        y = np.array(pitcher_data['pitch_type'])
        model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=8)
        model.fit(X, y)
        return {'model': model, 'le_count': le_count, 'le_stand': le_stand}
    
    predictor = train_predictor(selected_pitcher)
    if predictor:
        col1, col2 = st.columns(2)
        with col1:
            all_pitcher_data = df[df['player_name'] == selected_pitcher].copy()
            all_pitcher_data['count'] = all_pitcher_data['balls'].astype(str) + '-' + all_pitcher_data['strikes'].astype(str)
            unique_counts = sorted(all_pitcher_data['count'].unique())
            pred_count = st.selectbox("Count", unique_counts, key="pred_count")
            pred_vel = st.slider("Velocity (mph)", 70, 105, 95, key="pred_vel")
            pred_hand = st.radio("Batter", ["Right", "Left"], key="pred_hand")
        with col2:
            if st.button("Predict"):
                count_enc = predictor['le_count'].transform([pred_count])[0]
                stand_enc = predictor['le_stand'].transform(['R' if pred_hand == "Right" else 'L'])[0]
                pred_input = np.array([[pred_vel, count_enc, stand_enc]])
                pred_pitch = predictor['model'].predict(pred_input)[0]
                pred_proba = predictor['model'].predict_proba(pred_input)[0]
                st.markdown(f"### **{pred_pitch}**")
                st.markdown(f"Confidence: {pred_proba.max() * 100:.1f}%")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("## vs League Average")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        league_metrics = calculate_metrics(league_df)
        k_data = pd.DataFrame({'Pitcher': [selected_pitcher, 'League'], 'K Rate': [pitcher_metrics['k_rate'], league_metrics['k_rate']]})
        fig_k = px.bar(k_data, x='Pitcher', y='K Rate', color='K Rate', color_continuous_scale='Blues', height=400)
        fig_k.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429', showlegend=False)
        st.plotly_chart(fig_k, use_container_width=True)
    
    with col2:
        bb_data = pd.DataFrame({'Pitcher': [selected_pitcher, 'League'], 'BB Rate': [pitcher_metrics['walk_rate'], league_metrics['walk_rate']]})
        fig_bb = px.bar(bb_data, x='Pitcher', y='BB Rate', color='BB Rate', color_continuous_scale='Reds', height=400)
        fig_bb.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429', showlegend=False)
        st.plotly_chart(fig_bb, use_container_width=True)
    
    with col3:
        whiff_data = pd.DataFrame({'Pitcher': [selected_pitcher, 'League'], 'Whiff Rate': [pitcher_metrics['whiff_rate'], league_metrics['whiff_rate']]})
        fig_whiff = px.bar(whiff_data, x='Pitcher', y='Whiff Rate', color='Whiff Rate', color_continuous_scale='Purples', height=400)
        fig_whiff.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429', showlegend=False)
        st.plotly_chart(fig_whiff, use_container_width=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("## Arsenal")
    arsenal = filtered_df.groupby('pitch_type').agg({'release_speed': 'mean', 'release_spin_rate': 'mean', 'pitch_type': 'count'}).round(1)
    arsenal.columns = ['Velocity', 'Spin', 'Count']
    st.dataframe(arsenal.sort_values('Count', ascending=False), use_container_width=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("## Velocity by Count")
    
    pitcher_all = df[(df['player_name'] == selected_pitcher) & (df['pitch_type'].isin(selected_pitch_types))]
    pitcher_all['count'] = pitcher_all['balls'].astype(str) + '-' + pitcher_all['strikes'].astype(str)
    
    count_stats = pitcher_all.groupby('count').agg({'release_speed': ['mean', 'count'], 'release_spin_rate': 'mean'}).round(1)
    count_stats.columns = ['Avg Velocity', 'Pitch Count', 'Avg Spin Rate']
    count_stats = count_stats.sort_values('Pitch Count', ascending=False)
    
    st.dataframe(count_stats, use_container_width=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("## Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        vel_by_type = filtered_df.groupby('pitch_type')['release_speed'].mean().sort_values(ascending=False)
        fig_vel = px.bar(vel_by_type, color=vel_by_type.values, color_continuous_scale='Reds', height=400, labels={'value': 'Velocity (mph)'})
        fig_vel.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429', showlegend=False)
        st.plotly_chart(fig_vel, use_container_width=True)
    
    with col2:
        spin_by_type = filtered_df.groupby('pitch_type')['release_spin_rate'].mean().sort_values(ascending=False)
        fig_spin = px.bar(spin_by_type, color=spin_by_type.values, color_continuous_scale='Blues', height=400, labels={'value': 'Spin Rate (RPM)'})
        fig_spin.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429', showlegend=False)
        st.plotly_chart(fig_spin, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        sample = filtered_df.sample(n=min(200, len(filtered_df)))
        fig_mech = px.scatter(sample, x='release_speed', y='release_spin_rate', color='pitch_type', height=400, labels={'release_speed': 'Velocity (mph)', 'release_spin_rate': 'Spin Rate (RPM)'})
        fig_mech.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429')
        st.plotly_chart(fig_mech, use_container_width=True)
    
    with col2:
        fig_move = px.scatter(filtered_df, x='pfx_x', y='pfx_z', color='pitch_type', height=400, labels={'pfx_x': 'Horizontal (in)', 'pfx_z': 'Vertical (in)'})
        fig_move.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429')
        st.plotly_chart(fig_move, use_container_width=True)
    
    pitch_mix = filtered_df['pitch_type'].value_counts()
    fig_pie = px.pie(values=pitch_mix.values, names=pitch_mix.index, height=400)
    fig_pie.update_layout(template='plotly_dark', paper_bgcolor='#0f1429')
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666666;'>MLB Statcast Data | 2026 Season</p>", unsafe_allow_html=True)