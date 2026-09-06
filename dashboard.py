import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np

st.set_page_config(page_title="MLB Pitch Analysis System", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    body { background-color: #0a0e27; color: #e0e0e0; }
    .main { background-color: #0a0e27; padding: 20px; }
    [data-testid="stSidebar"] { background-color: #1a1f3a; }
    .stMetric { background-color: #1a1f3a; padding: 15px; border-radius: 8px; border: 1px solid #2d3561; }
    h1 { color: #ffffff; font-size: 2.5rem; font-weight: 700; text-align: center; margin-bottom: 5px; }
    h2 { color: #e8f4f8; font-size: 1.6rem; font-weight: 600; margin-top: 30px; border-bottom: 2px solid #1f77b4; padding-bottom: 10px; }
    h3 { color: #b8d4e8; font-size: 1.2rem; }
    .subtitle { color: #a0a0a0; font-size: 1.1rem; text-align: center; margin-bottom: 20px; }
    .divider { background-color: #2d3561; height: 1px; margin: 30px 0; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>MLB STATCAST PITCH ANALYSIS</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>2026 Season | Advanced Pitcher Analytics</div>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

with st.expander("Pitch Type Reference", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Fastballs**")
        st.write("- **FF** = Four-Seam Fastball\n- **SI** = Sinker\n- **FC** = Cut Fastball\n- **FA** = Fastball")
    with col2:
        st.markdown("**Breaking Balls**")
        st.write("- **SL** = Slider\n- **CU** = Curveball\n- **KC** = Knuckle Curve\n- **ST** = Sweeper")
    with col3:
        st.markdown("**Off-Speed & Specialty**")
        st.write("- **CH** = Changeup\n- **FS** = Splitter\n- **SV** = Slurve\n- **KN** = Knuckleball\n- **EP** = Eephus")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        return pd.read_csv('statcast_2026.csv')
    except:
        np.random.seed(42)
        pitchers = ['Varland, Louis', 'Cole, Gerrit', 'Rodon, Carlos', 'Burnes, Corbin', 'Alcantara, Sandy', 
                    'Musgrove, Joe', 'Snell, Blake', 'Severino, Luis', 'Nola, Aaron', 'Stroman, Marcus',
                    'Castillo, Luis', 'Kluber, Corey', 'Manaea, Sean', 'Lodolo, Nick', 'Gray, Sonny',
                    'Cease, Dylan', 'Kopech, Michael', 'McKenzie, Triston', 'Luzardo, Jesus', 'Waldichuk, Eury',
                    'Thompson, Keegan', 'Montgomery, Mike', 'King, Michael', 'Schmidt, Camilo', 'Flexen, Chris']
        
        pitch_types = ['FF', 'SI', 'FC', 'SL', 'CU', 'CH', 'FS', 'ST', 'KC', 'SV']
        
        data_list = []
        for _ in range(5000):
            pitcher = np.random.choice(pitchers)
            pitch_type = np.random.choice(pitch_types)
            data_list.append({
                'player_name': pitcher,
                'pitch_type': pitch_type,
                'release_speed': np.random.normal(93, 2.5),
                'release_spin_rate': np.random.normal(2300, 300),
                'pfx_x': np.random.normal(0, 12),
                'pfx_z': np.random.normal(20, 10),
                'balls': np.random.randint(0, 4),
                'strikes': np.random.randint(0, 3),
                'stand': np.random.choice(['R', 'L']),
                'events': np.random.choice(['strikeout', 'walk', 'single', 'double', 'triple', 'home_run', None], p=[0.12, 0.08, 0.22, 0.18, 0.05, 0.02, 0.33]),
                'description': np.random.choice(['swinging_strike', 'called_strike', 'ball', 'foul', 'hit_into_play']),
                'game_pk': np.random.randint(600000, 700000),
                'batter': np.random.randint(100000, 900000),
                'pitcher': np.random.randint(100000, 900000),
                'inning': np.random.randint(1, 10)
            })
        return pd.DataFrame(data_list)

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
        pitcher_2 = st.selectbox("Second Pitcher", all_pitchers, key="p2", index=1 if len(all_pitchers) > 1 else 0)
    
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
        st.markdown("## Velocity & Spin Comparison")
        
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
        
        st.markdown("## Movement Profile")
        col1, col2 = st.columns(2)
        with col1:
            p1_sample = p1_data.sample(n=min(2000, len(p1_data)))
            fig_p1 = px.scatter(p1_sample, x='pfx_x', y='pfx_z', color='pitch_type', title=f"{pitcher_1} Movement", height=500, labels={'pfx_x': 'Horizontal (in)', 'pfx_z': 'Vertical (in)'}, color_discrete_sequence=px.colors.qualitative.Bold)
            fig_p1.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429')
            st.plotly_chart(fig_p1, use_container_width=True)
        with col2:
            p2_sample = p2_data.sample(n=min(2000, len(p2_data)))
            fig_p2 = px.scatter(p2_sample, x='pfx_x', y='pfx_z', color='pitch_type', title=f"{pitcher_2} Movement", height=500, labels={'pfx_x': 'Horizontal (in)', 'pfx_z': 'Vertical (in)'}, color_discrete_sequence=px.colors.qualitative.Bold)
            fig_p2.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429')
            st.plotly_chart(fig_p2, use_container_width=True)

else:
    selected_pitcher = st.sidebar.selectbox("Pitcher", all_pitchers)
    all_pitch_types = sorted(df['pitch_type'].dropna().unique().tolist())
    selected_pitch_types = st.sidebar.multiselect("Pitch Types", all_pitch_types, default=all_pitch_types)
    batter_hand = st.sidebar.radio("Batter", ["All", "Right (RHH)", "Left (LHH)"])
    count_option = st.sidebar.radio("Count", ["All", "Specific"])
    
    filtered_df = df[(df['player_name'] == selected_pitcher) & (df['pitch_type'].isin(selected_pitch_types))]
    
    if batter_hand == "Right (RHH)":
        filtered_df = filtered_df[filtered_df['stand'] == 'R']
    elif batter_hand == "Left (LHH)":
        filtered_df = filtered_df[filtered_df['stand'] == 'L']
    
    selected_count = None
    if count_option == "Specific":
        filtered_df['count'] = filtered_df['balls'].astype(str) + '-' + filtered_df['strikes'].astype(str)
        unique_counts = sorted(filtered_df['count'].unique())
        if len(unique_counts) > 0:
            selected_count = st.sidebar.selectbox("Select Count", unique_counts)
            filtered_df = filtered_df[filtered_df['count'] == selected_count]
    
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
        pitcher_data = pitcher_data.copy()
        pitcher_data['count'] = pitcher_data['balls'].astype(str) + '-' + pitcher_data['strikes'].astype(str)
        le_count = LabelEncoder()
        pitcher_data['count_encoded'] = le_count.fit_transform(pitcher_data['count'])
        le_stand = LabelEncoder()
        pitcher_data['stand_encoded'] = le_stand.fit_transform(pitcher_data['stand'])
        X = np.array(pitcher_data[['release_speed', 'count_encoded', 'stand_encoded']])
        y = np.array(pitcher_data['pitch_type'])
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8, min_samples_split=10)
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
    
    count_vel = pitcher_all.groupby('count')['release_speed'].mean().sort_values(ascending=False)
    if len(count_vel) > 0:
        fig_count = px.bar(count_vel, labels={'value': 'Avg Velocity (mph)', 'count': 'Count'}, color=count_vel.values, color_continuous_scale='Reds', height=400)
        fig_count.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429', showlegend=False)
        st.plotly_chart(fig_count, use_container_width=True)
    
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
        sample = filtered_df.sample(n=min(3000, len(filtered_df)))
        fig_mech = px.scatter(sample, x='release_speed', y='release_spin_rate', color='pitch_type', height=500, labels={'release_speed': 'Velocity (mph)', 'release_spin_rate': 'Spin Rate (RPM)'}, color_discrete_sequence=px.colors.qualitative.Bold)
        fig_mech.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429')
        st.plotly_chart(fig_mech, use_container_width=True)
    
    with col2:
        fig_move = px.scatter(filtered_df, x='pfx_x', y='pfx_z', color='pitch_type', height=500, labels={'pfx_x': 'Horizontal (in)', 'pfx_z': 'Vertical (in)'}, color_discrete_sequence=px.colors.qualitative.Bold)
        fig_move.update_layout(template='plotly_dark', paper_bgcolor='#0f1429', plot_bgcolor='#0f1429')
        st.plotly_chart(fig_move, use_container_width=True)
    
    pitch_mix = filtered_df['pitch_type'].value_counts()
    fig_pie = px.pie(values=pitch_mix.values, names=pitch_mix.index, height=500)
    fig_pie.update_layout(template='plotly_dark', paper_bgcolor='#0f1429')
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666666;'>MLB Statcast Data | 2026 Season</p>", unsafe_allow_html=True)