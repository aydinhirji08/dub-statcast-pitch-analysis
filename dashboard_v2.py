import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import warnings
import gdown
import tempfile
import os

warnings.filterwarnings('ignore')

st.set_page_config(page_title="MLB Statcast Pitch Analysis", layout="wide", initial_sidebar_state="expanded")

# Professional MLB Analytics Theme
st.markdown("""
<style>
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-tertiary: #1a202c;
        --border-color: #2d3748;
        --text-primary: #e2e8f0;
        --text-secondary: #cbd5e0;
        --text-muted: #a0aec0;
        --accent-blue: #3b82f6;
        --accent-red: #ef4444;
        --accent-green: #10b981;
        --accent-orange: #f97316;
    }
    
    body { background-color: var(--bg-primary); color: var(--text-primary); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif; }
    .main { background-color: var(--bg-primary); }
    .stApp { background-color: var(--bg-primary); }
    h1 { color: var(--text-primary); font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 0.5rem; }
    h2 { color: var(--text-primary); font-size: 1.5rem; font-weight: 600; letter-spacing: -0.3px; margin-top: 1.5rem; margin-bottom: 0.75rem; }
    h3 { color: var(--text-primary); font-size: 1.125rem; font-weight: 600; letter-spacing: -0.2px; margin-top: 1rem; margin-bottom: 0.5rem; }
    h4, h5, h6 { color: var(--text-primary); font-weight: 600; }
    [data-testid="stSidebar"] { background-color: var(--bg-secondary); border-right: 1px solid var(--border-color); }
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBuilderId"] { gap: 0.75rem; }
    [data-testid="stSidebar"] label { color: var(--text-primary); font-weight: 500; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem; }
    [data-testid="stSidebar"] hr { border-color: var(--border-color); margin: 1rem 0; }
    hr { border-color: var(--border-color); margin: 1.5rem 0; }
    p { color: var(--text-primary); line-height: 1.6; }
    .stInfo { background-color: rgba(59, 130, 246, 0.1); border-left: 4px solid var(--accent-blue); color: var(--text-primary); }
    .stWarning { background-color: rgba(249, 115, 22, 0.1); border-left: 4px solid var(--accent-orange); color: var(--text-primary); }
    a { color: var(--accent-blue); text-decoration: none; }
    a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    statcast_id = "1jxHScV07VtIvLjqZrct5zBJQYDnBwYKj"
    batter_id = "15sCrSvg_b1_pW8piY6PNhoCpBhs529ra"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        statcast_path = os.path.join(tmpdir, 'statcast.csv')
        batter_path = os.path.join(tmpdir, 'batter.csv')
        
        gdown.download(f'https://drive.google.com/uc?id={statcast_id}', statcast_path, quiet=True)
        gdown.download(f'https://drive.google.com/uc?id={batter_id}', batter_path, quiet=True)
        
        df = pd.read_csv(statcast_path)
        batter_names = pd.read_csv(batter_path)
    
    batter_map = dict(zip(batter_names['batter_id'], batter_names['batter_name']))
    
    df['batter_name'] = df['batter'].apply(lambda x: batter_map.get(int(x), 'Unknown') if pd.notna(x) else 'Unknown')
    df['pitcher_name'] = df['player_name'].fillna('Unknown')
    df['game_date'] = pd.to_datetime(df['game_date'])
    
    df['pitch_type'] = df['pitch_type'].fillna('UN')
    df['plate_x'] = df['plate_x'].fillna(0)
    df['plate_z'] = df['plate_z'].fillna(2)
    df['release_speed'] = df['release_speed'].fillna(0)
    df['release_spin_rate'] = df['release_spin_rate'].fillna(0)
    df['pfx_x'] = df['pfx_x'].fillna(0)
    df['pfx_z'] = df['pfx_z'].fillna(0)
    df['release_pos_x'] = df['release_pos_x'].fillna(0)
    df['release_pos_y'] = df['release_pos_y'].fillna(0)
    df['release_pos_z'] = df['release_pos_z'].fillna(0)
    
    return df, batter_map

df, batter_map = load_data()

st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="margin: 0; font-size: 2.25rem;">⚾ MLB Statcast Pitch Analysis</h1>
    <p style="margin: 0.5rem 0 0 0; color: #a0aec0; font-size: 0.95rem; letter-spacing: 0.3px;">2026 Season • Interactive Strike Zone Visualization</p>
</div>
""", unsafe_allow_html=True)
st.divider()

# SIDEBAR FILTERS
st.sidebar.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h3 style="margin: 0; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 1px; color: #a0aec0;">🎯 Filters</h3>
</div>
""", unsafe_allow_html=True)

all_pitchers = sorted(df[df['pitcher_name'] != 'Unknown']['pitcher_name'].unique())
selected_pitcher = st.sidebar.selectbox("Select Pitcher", all_pitchers, index=0 if len(all_pitchers) > 0 else None)

pitcher_data = df[df['pitcher_name'] == selected_pitcher]
pitcher_batters = sorted(pitcher_data[pitcher_data['batter_name'] != 'Unknown']['batter_name'].unique())

selected_batter = st.sidebar.selectbox("Select Batter (Optional - Strike Zone Only)", ['All'] + pitcher_batters, index=0)

batter_handedness = st.sidebar.radio("Batter Handedness", ['All', 'Left', 'Right'], index=0)

pitch_types = sorted([p for p in df['pitch_type'].unique() if p != 'UN'])
selected_pitches = st.sidebar.multiselect("Pitch Types", pitch_types, default=pitch_types)

st.sidebar.markdown("---")
compare_pitchers = st.sidebar.checkbox("Compare Multiple Pitchers")
if compare_pitchers:
    pitcher_2 = st.sidebar.selectbox("Select Second Pitcher to Compare", [p for p in all_pitchers if p != selected_pitcher], index=0 if len([p for p in all_pitchers if p != selected_pitcher]) > 0 else None)
else:
    pitcher_2 = None

show_count_filter = st.sidebar.checkbox("Filter by Count")
if show_count_filter:
    selected_balls = st.sidebar.slider("Balls", 0, 3, (0, 3))
    selected_strikes = st.sidebar.slider("Strikes", 0, 2, (0, 2))
else:
    selected_balls = (0, 3)
    selected_strikes = (0, 2)

# DATA FILTERING
filtered_df = df[
    (df['pitcher_name'] == selected_pitcher) &
    (df['pitch_type'].isin(selected_pitches)) &
    (df['pitch_type'] != 'UN') &
    (df['plate_x'].notna()) &
    (df['plate_z'].notna())
].copy()

if show_count_filter:
    filtered_df = filtered_df[
        (filtered_df['balls'] >= selected_balls[0]) &
        (filtered_df['balls'] <= selected_balls[1]) &
        (filtered_df['strikes'] >= selected_strikes[0]) &
        (filtered_df['strikes'] <= selected_strikes[1])
    ]

if batter_handedness == 'Left':
    filtered_df_with_hand = filtered_df[filtered_df['stand'] == 'L'].copy()
elif batter_handedness == 'Right':
    filtered_df_with_hand = filtered_df[filtered_df['stand'] == 'R'].copy()
else:
    filtered_df_with_hand = filtered_df.copy()

filtered_df_vs_batter = filtered_df.copy()
if not compare_pitchers and selected_batter != 'All':
    filtered_df_vs_batter = filtered_df_vs_batter[filtered_df_vs_batter['batter_name'] == selected_batter]

if compare_pitchers and pitcher_2:
    filtered_df_pitcher2 = df[
        (df['pitcher_name'] == pitcher_2) &
        (df['pitch_type'].isin(selected_pitches)) &
        (df['pitch_type'] != 'UN') &
        (df['plate_x'].notna()) &
        (df['plate_z'].notna())
    ].copy()
    
    if show_count_filter:
        filtered_df_pitcher2 = filtered_df_pitcher2[
            (filtered_df_pitcher2['balls'] >= selected_balls[0]) &
            (filtered_df_pitcher2['balls'] <= selected_balls[1]) &
            (filtered_df_pitcher2['strikes'] >= selected_strikes[0]) &
            (filtered_df_pitcher2['strikes'] <= selected_strikes[1])
        ]
    
    if batter_handedness == 'Left':
        filtered_df_pitcher2 = filtered_df_pitcher2[filtered_df_pitcher2['stand'] == 'L'].copy()
    elif batter_handedness == 'Right':
        filtered_df_pitcher2 = filtered_df_pitcher2[filtered_df_pitcher2['stand'] == 'R'].copy()
else:
    filtered_df_pitcher2 = None

# MAIN STRIKE ZONE
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h3 style="margin: 0 0 0.5rem 0; font-size: 1.125rem;">Strike Zone Heat Map</h3>
    </div>
    """, unsafe_allow_html=True)
    
    context_text = f"**{selected_pitcher}** • {len(filtered_df_vs_batter):,} pitches"
    if selected_batter != 'All' and not compare_pitchers:
        context_text += f" • vs **{selected_batter}**"
    st.markdown(f'<p style="margin: 0 0 1rem 0; color: #cbd5e0; font-size: 0.95rem;">{context_text}</p>', unsafe_allow_html=True)
    
    fig_heatmap = go.Figure()
    
    if len(filtered_df_vs_batter) > 0:
        fig_heatmap.add_trace(go.Histogram2d(
            x=filtered_df_vs_batter['plate_x'],
            y=filtered_df_vs_batter['plate_z'],
            nbinsx=20,
            nbinsy=20,
            colorscale='Reds',
            colorbar=dict(title="Pitch Count"),
            hovertemplate='<b>Count:</b> %{z}<extra></extra>'
        ))
    
    fig_heatmap.add_shape(
        type="rect",
        x0=-0.83, y0=1.6,
        x1=0.83, y1=3.5,
        line=dict(color="black", width=2),
        fillcolor="rgba(0,0,0,0)"
    )
    
    fig_heatmap.update_layout(
        title=dict(text="Pitches Thrown", x=0, xanchor='left', font=dict(size=14, color='#1a202c')),
        xaxis_title="Horizontal Location (ft)",
        yaxis_title="Vertical Location (ft)",
        width=700,
        height=600,
        template="plotly",
        hovermode='closest',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='system-ui, -apple-system, sans-serif', size=11, color='#1a202c'),
        xaxis=dict(gridcolor='#e0e0e0', zeroline=False),
        yaxis=dict(gridcolor='#e0e0e0', zeroline=False)
    )
    fig_heatmap.update_xaxes(range=[-3, 3], showgrid=False)
    fig_heatmap.update_yaxes(range=[0, 5], showgrid=False)
    
    st.plotly_chart(fig_heatmap, width='content', key="main_heatmap")

with col2:
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h3 style="margin: 0 0 0.5rem 0; font-size: 1.125rem;">📊 Quick Stats</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if len(filtered_df_with_hand) > 0:
        st.markdown(f"""
        <div style="background-color: #1a202c; border: 1px solid #2d3748; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem;">
            <div style="color: #a0aec0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">Total Pitches</div>
            <div style="color: #3b82f6; font-size: 1.875rem; font-weight: 700;">{len(filtered_df_with_hand):,}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-bottom: 1rem;">
            <div style="color: var(--text-secondary); font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 0.75rem;">Pitch Type Breakdown</div>
        </div>
        """, unsafe_allow_html=True)
        
        pitch_counts = filtered_df_with_hand['pitch_type'].value_counts()
        for pitch, count in pitch_counts.items():
            pct = (count / len(filtered_df_with_hand)) * 100
            st.markdown(f'<div style="color: #e2e8f0; font-size: 0.875rem; margin-bottom: 0.25rem;"><span style="color: #10b981; font-weight: 600;">{pitch}</span> {count:,} <span style="color: #a0aec0;">({pct:.1f}%)</span></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 1rem; margin-bottom: 0.5rem;">
            <div style="color: var(--text-secondary); font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Velocity (mph)</div>
        </div>
        """, unsafe_allow_html=True)
        
        vel_df = filtered_df_with_hand[filtered_df_with_hand['release_speed'] > 0]
        if len(vel_df) > 0:
            avg_vel = vel_df['release_speed'].mean()
            min_vel = vel_df['release_speed'].min()
            max_vel = vel_df['release_speed'].max()
            st.markdown(f'''
            <div style="font-size: 0.875rem;">
                <div style="margin-bottom: 0.25rem;"><span style="color: #cbd5e0;">Avg:</span> <span style="color: #f97316; font-weight: 600;">{avg_vel:.1f}</span></div>
                <div style="margin-bottom: 0.25rem;"><span style="color: #cbd5e0;">Min:</span> <span style="color: #10b981;">{min_vel:.1f}</span></div>
                <div><span style="color: #cbd5e0;">Max:</span> <span style="color: #ef4444;">{max_vel:.1f}</span></div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 1rem; margin-bottom: 0.5rem;">
            <div style="color: var(--text-secondary); font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Spin Rate (rpm)</div>
        </div>
        """, unsafe_allow_html=True)
        
        spin_df = filtered_df_with_hand[filtered_df_with_hand['release_spin_rate'] > 0]
        if len(spin_df) > 0:
            avg_spin = spin_df['release_spin_rate'].mean()
            min_spin = spin_df['release_spin_rate'].min()
            max_spin = spin_df['release_spin_rate'].max()
            st.markdown(f'''
            <div style="font-size: 0.875rem;">
                <div style="margin-bottom: 0.25rem;"><span style="color: #cbd5e0;">Avg:</span> <span style="color: #f97316; font-weight: 600;">{avg_spin:.0f}</span></div>
                <div style="margin-bottom: 0.25rem;"><span style="color: #cbd5e0;">Min:</span> <span style="color: #10b981;">{min_spin:.0f}</span></div>
                <div><span style="color: #cbd5e0;">Max:</span> <span style="color: #ef4444;">{max_spin:.0f}</span></div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.warning("No pitches match the selected filters.")

st.divider()

# ANALYSIS SECTION
st.markdown("""
<div style="margin: 2rem 0 1.5rem 0;">
    <h2 style="margin: 0; font-size: 1.25rem; color: #e2e8f0;">Analysis</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="margin-bottom: 0.75rem;">
        <h3 style="margin: 0; font-size: 1rem; color: #e2e8f0;">Velocity Distribution</h3>
    </div>
    """, unsafe_allow_html=True)
    
    vel_df = filtered_df_with_hand[filtered_df_with_hand['release_speed'] > 0]
    if len(vel_df) > 0 and len(vel_df['pitch_type'].unique()) > 0:
        fig_vel = px.box(vel_df, x='pitch_type', y='release_speed', color='pitch_type', title='', labels={'release_speed': 'Velocity (mph)', 'pitch_type': 'Pitch Type'})
        fig_vel.update_layout(template="plotly_dark", height=400, showlegend=False, plot_bgcolor='#111827', paper_bgcolor='#0a0e17', font=dict(family='system-ui', size=11, color='#e2e8f0'), xaxis=dict(gridcolor='#1a202c', zeroline=False), yaxis=dict(gridcolor='#1a202c', zeroline=False))
        st.plotly_chart(fig_vel, width='stretch', key="vel_distribution")
    else:
        st.info("No velocity data available for selected filters")

with col2:
    st.markdown("""
    <div style="margin-bottom: 0.75rem;">
        <h3 style="margin: 0; font-size: 1rem; color: #e2e8f0;">Spin Rate Distribution</h3>
    </div>
    """, unsafe_allow_html=True)
    
    spin_df = filtered_df_with_hand[filtered_df_with_hand['release_spin_rate'] > 0]
    if len(spin_df) > 0 and len(spin_df['pitch_type'].unique()) > 0:
        fig_spin = px.box(spin_df, x='pitch_type', y='release_spin_rate', color='pitch_type', title='', labels={'release_spin_rate': 'Spin Rate (rpm)', 'pitch_type': 'Pitch Type'})
        fig_spin.update_layout(template="plotly_dark", height=400, showlegend=False, plot_bgcolor='#111827', paper_bgcolor='#0a0e17', font=dict(family='system-ui', size=11, color='#e2e8f0'), xaxis=dict(gridcolor='#1a202c', zeroline=False), yaxis=dict(gridcolor='#1a202c', zeroline=False))
        st.plotly_chart(fig_spin, width='stretch', key="spin_distribution")
    else:
        st.info("No spin rate data available for selected filters")

st.divider()

# PITCH MOVEMENT
st.markdown("""
<div style="margin: 2rem 0 1.5rem 0;">
    <h2 style="margin: 0; font-size: 1.25rem; color: #e2e8f0;">Pitch Movement</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="margin-bottom: 0.75rem;">
        <h3 style="margin: 0; font-size: 1rem; color: #e2e8f0;">Horizontal vs Vertical Break</h3>
    </div>
    """, unsafe_allow_html=True)
    
    move_df = filtered_df_with_hand[(filtered_df_with_hand['pfx_x'].notna()) & (filtered_df_with_hand['pfx_z'].notna())]
    if len(move_df) > 0:
        fig_move = px.scatter(move_df, x='pfx_x', y='pfx_z', color='pitch_type', title='', labels={'pfx_x': 'Horizontal Break (in)', 'pfx_z': 'Induced Vertical Break (in)'}, hover_data=['release_speed', 'release_spin_rate'])
        fig_move.update_layout(template="plotly_dark", height=500, plot_bgcolor='#111827', paper_bgcolor='#0a0e17', font=dict(family='system-ui', size=11, color='#e2e8f0'), xaxis=dict(gridcolor='#1a202c', zeroline=True, zerolinecolor='#2d3748'), yaxis=dict(gridcolor='#1a202c', zeroline=True, zerolinecolor='#2d3748'))
        fig_move.update_xaxes(zeroline=True)
        fig_move.update_yaxes(zeroline=True)
        st.plotly_chart(fig_move, width='stretch', key="movement_scatter")
    else:
        st.info("No movement data available for selected filters")

with col2:
    st.markdown("""
    <div style="margin-bottom: 0.75rem;">
        <h3 style="margin: 0; font-size: 1rem; color: #e2e8f0;">Velocity by Pitch Type</h3>
    </div>
    """, unsafe_allow_html=True)
    
    vel_type_df = filtered_df_with_hand[filtered_df_with_hand['release_speed'] > 0]
    if len(vel_type_df) > 0 and len(vel_type_df['pitch_type'].unique()) > 0:
        fig_vel_type = px.violin(vel_type_df, x='pitch_type', y='release_speed', color='pitch_type', title='')
        fig_vel_type.update_layout(template="plotly_dark", height=500, showlegend=False, plot_bgcolor='#111827', paper_bgcolor='#0a0e17', font=dict(family='system-ui', size=11, color='#e2e8f0'), xaxis=dict(gridcolor='#1a202c', zeroline=False), yaxis=dict(gridcolor='#1a202c', zeroline=False))
        st.plotly_chart(fig_vel_type, width='stretch', key="velocity_violin")
    else:
        st.info("No velocity data available for selected filters")

st.divider()

# PITCH CONTEXT
st.markdown("""
<div style="margin: 2rem 0 1.5rem 0;">
    <h2 style="margin: 0; font-size: 1.25rem; color: #e2e8f0;">Pitch Context</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="margin-bottom: 0.75rem;">
        <h3 style="margin: 0; font-size: 1rem; color: #e2e8f0;">Velocity by Count</h3>
    </div>
    """, unsafe_allow_html=True)
    
    vel_count_df = filtered_df_with_hand[filtered_df_with_hand['release_speed'] > 0].copy()
    vel_count_df['count'] = vel_count_df['balls'].astype(str) + '-' + vel_count_df['strikes'].astype(str)
    
    if len(vel_count_df) > 0:
        fig_vel_count = px.box(vel_count_df, x='count', y='release_speed', color='count', title='')
        fig_vel_count.update_layout(template="plotly_dark", height=400, showlegend=False, plot_bgcolor='#111827', paper_bgcolor='#0a0e17', font=dict(family='system-ui', size=11, color='#e2e8f0'), xaxis=dict(gridcolor='#1a202c', zeroline=False), yaxis=dict(gridcolor='#1a202c', zeroline=False))
        st.plotly_chart(fig_vel_count, width='stretch', key="vel_by_count")
    else:
        st.info("No velocity data available for selected filters")

with col2:
    st.markdown("""
    <div style="margin-bottom: 0.75rem;">
        <h3 style="margin: 0; font-size: 1rem; color: #e2e8f0;">Pitch Type Distribution</h3>
    </div>
    """, unsafe_allow_html=True)
    
    pitch_type_df = filtered_df_with_hand.copy()
    pitch_dist_pitcher = pitch_type_df['pitch_type'].value_counts().reset_index()
    pitch_dist_pitcher.columns = ['Pitch Type', 'Count']
    
    if len(pitch_dist_pitcher) > 0:
        fig_pitch = px.pie(pitch_dist_pitcher, values='Count', names='Pitch Type', title='')
        fig_pitch.update_layout(template="plotly_dark", plot_bgcolor='#111827', paper_bgcolor='#0a0e17', font=dict(family='system-ui', size=11, color='#e2e8f0'))
        st.plotly_chart(fig_pitch, width='stretch', key="pitch_distribution")
    else:
        st.info("No pitch data available for selected filters")

st.divider()

# COMPARISON PITCHERS
if compare_pitchers and pitcher_2 and filtered_df_pitcher2 is not None and len(filtered_df_pitcher2) > 0:
    st.markdown(f"""
    <div style="margin: 2rem 0 1.5rem 0;">
        <h2 style="margin: 0; font-size: 1.25rem; color: #e2e8f0;">Pitcher Comparison</h2>
        <p style="margin: 0.5rem 0 0 0; color: #a0aec0; font-size: 0.95rem;">{selected_pitcher} <span style="color: #cbd5e0;">vs</span> {pitcher_2}</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # COMPARISON STRIKE ZONES
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h3 style="margin: 0; font-size: 1.125rem; color: #e2e8f0;">Strike Zones</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div style="margin-bottom: 0.75rem;"><span style="color: #e2e8f0; font-weight: 600;">{selected_pitcher}</span> <span style="color: #a0aec0;">•</span> <span style="color: #cbd5e0;">{len(filtered_df_with_hand):,} pitches</span></div>', unsafe_allow_html=True)
        
        fig_heatmap1 = go.Figure()
        if len(filtered_df_with_hand) > 0:
            fig_heatmap1.add_trace(go.Histogram2d(x=filtered_df_with_hand['plate_x'], y=filtered_df_with_hand['plate_z'], nbinsx=20, nbinsy=20, colorscale='Blues', colorbar=dict(title="Pitch Count")))
        fig_heatmap1.add_shape(type="rect", x0=-0.83, y0=1.6, x1=0.83, y1=3.5, line=dict(color="black", width=2), fillcolor="rgba(0,0,0,0)")
        fig_heatmap1.update_layout(height=500, template="plotly", plot_bgcolor='white', paper_bgcolor='white', font=dict(family='system-ui', size=11, color='#1a202c'), xaxis=dict(gridcolor='#e0e0e0', zeroline=False, range=[-3, 3]), yaxis=dict(gridcolor='#e0e0e0', zeroline=False, range=[0, 5]))
        st.plotly_chart(fig_heatmap1, width='stretch', key="comp_heatmap1")
    
    with col2:
        st.markdown(f'<div style="margin-bottom: 0.75rem;"><span style="color: #e2e8f0; font-weight: 600;">{pitcher_2}</span> <span style="color: #a0aec0;">•</span> <span style="color: #cbd5e0;">{len(filtered_df_pitcher2):,} pitches</span></div>', unsafe_allow_html=True)
        
        fig_heatmap2 = go.Figure()
        if len(filtered_df_pitcher2) > 0:
            fig_heatmap2.add_trace(go.Histogram2d(x=filtered_df_pitcher2['plate_x'], y=filtered_df_pitcher2['plate_z'], nbinsx=20, nbinsy=20, colorscale='Reds', colorbar=dict(title="Pitch Count")))
        fig_heatmap2.add_shape(type="rect", x0=-0.83, y0=1.6, x1=0.83, y1=3.5, line=dict(color="black", width=2), fillcolor="rgba(0,0,0,0)")
        fig_heatmap2.update_layout(height=500, template="plotly", plot_bgcolor='white', paper_bgcolor='white', font=dict(family='system-ui', size=11, color='#1a202c'), xaxis=dict(gridcolor='#e0e0e0', zeroline=False, range=[-3, 3]), yaxis=dict(gridcolor='#e0e0e0', zeroline=False, range=[0, 5]))
        st.plotly_chart(fig_heatmap2, width='stretch', key="comp_heatmap2")
    
    st.divider()

    # COMPARISON VELOCITY
    st.markdown("""
    <div style="margin: 2rem 0 1.5rem 0;">
        <h2 style="margin: 0; font-size: 1.25rem; color: #e2e8f0;">Velocity Comparison</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        vel_p1 = filtered_df_with_hand[filtered_df_with_hand['release_speed'] > 0]
        if len(vel_p1) > 0 and len(vel_p1['pitch_type'].unique()) > 0:
            fig_vel1 = px.box(vel_p1, x='pitch_type', y='release_speed', color='pitch_type', title=f'{selected_pitcher}')
            fig_vel1.update_layout(template="plotly_dark", height=400, showlegend=False, plot_bgcolor='#111827', paper_bgcolor='#0a0e17', font=dict(size=11, color='#e2e8f0'))
            st.plotly_chart(fig_vel1, width='stretch', key="comp_vel1")
    
    with col2:
        vel_p2 = filtered_df_pitcher2[filtered_df_pitcher2['release_speed'] > 0]
        if len(vel_p2) > 0 and len(vel_p2['pitch_type'].unique()) > 0:
            fig_vel2 = px.box(vel_p2, x='pitch_type', y='release_speed', color='pitch_type', title=f'{pitcher_2}')
            fig_vel2.update_layout(template="plotly_dark", height=400, showlegend=False, plot_bgcolor='#111827', paper_bgcolor='#0a0e17', font=dict(size=11, color='#e2e8f0'))
            st.plotly_chart(fig_vel2, width='stretch', key="comp_vel2")
    
    st.divider()

    # COMPARISON SPIN RATE
    st.markdown("""
    <div style="margin: 2rem 0 1.5rem 0;">
        <h2 style="margin: 0; font-size: 1.25rem; color: #e2e8f0;">Spin Rate Comparison</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        spin_p1 = filtered_df_with_hand[filtered_df_with_hand['release_spin_rate'] > 0]
        if len(spin_p1) > 0 and len(spin_p1['pitch_type'].unique()) > 0:
            fig_spin1 = px.box(spin_p1, x='pitch_type', y='release_spin_rate', color='pitch_type', title=f'{selected_pitcher}')
            fig_spin1.update_layout(template="plotly_dark", height=400, showlegend=False, plot_bgcolor='#111827', paper_bgcolor='#0a0e17', font=dict(size=11, color='#e2e8f0'))
            st.plotly_chart(fig_spin1, width='stretch', key="comp_spin1")
    
    with col2:
        spin_p2 = filtered_df_pitcher2[filtered_df_pitcher2['release_spin_rate'] > 0]
        if len(spin_p2) > 0 and len(spin_p2['pitch_type'].unique()) > 0:
            fig_spin2 = px.box(spin_p2, x='pitch_type', y='release_spin_rate', color='pitch_type', title=f'{pitcher_2}')
            fig_spin2.update_layout(template="plotly_dark", height=400, showlegend=False, plot_bgcolor='#111827', paper_bgcolor='#0a0e17', font=dict(size=11, color='#e2e8f0'))
            st.plotly_chart(fig_spin2, width='stretch', key="comp_spin2")
    
    st.divider()

st.markdown("""
<div style="margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #2d3748; text-align: center;">
    <p style="margin: 0; color: #a0aec0; font-size: 0.875rem; letter-spacing: 0.3px;">MLB Statcast 2026 Season • Interactive Pitch Analysis Dashboard</p>
</div>
""", unsafe_allow_html=True)