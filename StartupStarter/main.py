import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from odds_history import OddsHistory
from alerts import AlertSystem
from sqlalchemy import create_engine
import logging
from holzhauer_strategy import HolzhauerStrategy
from nba_analyzer import NBAAnalyzer
from nba_data_collector import NBADataCollector

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Sports Betting Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS with enhanced styling
st.markdown("""
<style>
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
        transform: translateY(-2px);
    }
    .metric-card {
        background: linear-gradient(135deg, #1E1E1E 0%, #262730 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 75, 75, 0.1);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .stat-container {
        background: linear-gradient(45deg, #262730, #1E1E1E);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 75, 75, 0.1);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        color: #FAFAFA;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #FF4B4B;
        border-radius: 10px;
        transform: translateY(-2px);
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    .heat-map {
        background: linear-gradient(135deg, #262730 0%, #1E1E1E 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 75, 75, 0.1);
    }
    .value-card {
        background: linear-gradient(135deg, #2E2E3E 0%, #1E1E2E 100%);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border: 1px solid rgba(255, 75, 75, 0.15);
        transition: all 0.3s ease;
    }
    .value-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    .trend-indicator {
        font-size: 1.2rem;
        font-weight: bold;
        padding: 0.3rem 0.8rem;
        border-radius: 8px;
        display: inline-block;
    }
    .trend-up {
        background-color: rgba(0, 255, 0, 0.1);
        color: #00FF00;
    }
    .trend-down {
        background-color: rgba(255, 0, 0, 0.1);
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
odds_history = OddsHistory()
alert_system = AlertSystem()
holzhauer = HolzhauerStrategy()
nba_analyzer = NBAAnalyzer()
nba_collector = NBADataCollector()

# Database connection
def get_db_connection():
    return create_engine(os.environ['DATABASE_URL'])

# Title and description with custom styling
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='color: #FF4B4B;'>🎯 Sports Betting Analytics Dashboard</h1>
    <p style='font-size: 1.2rem; color: #FAFAFA;'>
        Advanced analytics and insights for sports betting
    </p>
</div>
""", unsafe_allow_html=True)

# Create main tabs with custom styling
tabs = st.tabs([
    "📊 Live Dashboard",
    "📈 Performance Analysis",
    "🎯 Shot Analytics",
    "📊 Betting Insights",
    "🧮 Holzhauer Analysis",
    "🏀 NBA Games"
])

# Update the live games section
with tabs[0]:
    st.markdown("<h2 style='color: #FF4B4B;'>Live Games and Analytics</h2>", unsafe_allow_html=True)
    try:
        engine = get_db_connection()
        # Modified query to include both live and upcoming games
        games_df = pd.read_sql("""
            SELECT * FROM games 
            WHERE date >= CURRENT_DATE 
            ORDER BY date ASC, id ASC
            LIMIT 10
        """, engine)

        if not games_df.empty:
            for _, game in games_df.iterrows():
                game_date = pd.to_datetime(game['date']).strftime('%Y-%m-%d')
                st.markdown(f"""
                <div class='stat-container'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='text-align: center; flex: 1;'>
                            <h3 style='color: #FF4B4B;'>{game['home_team']}</h3>
                            <p style='color: #888;'>Home</p>
                        </div>
                        <div style='text-align: center; flex: 0.5;'>
                            <h3 style='color: #FAFAFA;'>VS</h3>
                            <p style='color: #888;'>{game_date}</p>
                        </div>
                        <div style='text-align: center; flex: 1;'>
                            <h3 style='color: #FF4B4B;'>{game['away_team']}</h3>
                            <p style='color: #888;'>Away</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            if st.button("🔄 Fetch Latest Games"):
                with st.spinner("Fetching latest NBA data..."):
                    if nba_collector.update_all_data():
                        st.success("Games data updated successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Error updating games data")
            else:
                st.info("🏀 No upcoming games found. Click the refresh button to fetch latest data.")

    except Exception as e:
        logger.error(f"Error in live dashboard: {e}")
        st.error("Error loading games data. Please try refreshing the data.")

with tabs[1]:
    st.header("Historical Odds Analysis")
    try:
        # Get historical odds data
        odds_data = odds_history.get_odds_history(hours=24)
        if odds_data:
            # Convert to DataFrame
            hist_df = pd.DataFrame(odds_data)

            # Create time series plot
            fig = go.Figure()
            for match in hist_df['match'].unique():
                match_data = hist_df[hist_df['match'] == match]
                fig.add_trace(go.Scatter(
                    x=match_data['timestamp'],
                    y=match_data['odds'],
                    name=match,
                    mode='lines+markers'
                ))

            fig.update_layout(
                title='Odds Movement (Last 24 Hours)',
                xaxis_title='Time',
                yaxis_title='Odds'
            )
            st.plotly_chart(fig, key="odds_movement_chart")

            # Show trend analysis
            st.subheader("Trend Analysis")
            trends = odds_history.get_trend_analysis()
            if trends:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Increasing Trends", len(trends.get('increasing', [])))
                with col2:
                    st.metric("Decreasing Trends", len(trends.get('decreasing', [])))
                with col3:
                    st.metric("Volatile Markets", len(trends.get('volatile', [])))
        else:
            st.info("No historical data available")

    except Exception as e:
        logger.error(f"Error in odds analysis: {e}")
        st.error("Error loading historical odds data")

with tabs[2]:
    st.header("Player Performance Analysis")
    try:
        engine = get_db_connection()
        players_df = pd.read_sql("SELECT * FROM players", engine)

        if not players_df.empty:
            # Player selector
            selected_player = st.selectbox("Select Player", players_df['name'].unique())

            if selected_player:
                player_data = players_df[players_df['name'] == selected_player].iloc[0]

                # Player stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Points", f"{player_data['avg_points']:.1f}")
                with col2:
                    st.metric("Form Rating", f"{player_data['form_rating']:.1f}")
                with col3:
                    st.metric("Consistency", f"{player_data['consistency']:.1%}")

                # Performance trend
                st.subheader("Performance Trend")
                performance_df = pd.read_sql(
                    f"SELECT * FROM player_performance WHERE player_id = '{player_data['id']}' ORDER BY game_date DESC LIMIT 10",
                    engine
                )
                if not performance_df.empty:
                    fig = px.line(performance_df, 
                                 x='game_date', 
                                 y='points',
                                 title='Recent Performance')
                    st.plotly_chart(fig, key="player_performance_chart")
        else:
            st.info("No player data available")

    except Exception as e:
        logger.error(f"Error in player analysis: {e}")
        st.error("Error loading player data")

with tabs[3]:
    st.header("Betting Insights")
    try:
        engine = get_db_connection()
        insights_df = pd.read_sql("""
            SELECT g.home_team, g.away_team, o.home_odds, o.away_odds,
                   o.prediction, o.confidence
            FROM odds o
            JOIN games g ON o.game_id = g.id
            WHERE o.timestamp >= NOW() - INTERVAL '24 hours'
        """, engine)

        if not insights_df.empty:
            # High confidence predictions
            st.subheader("High Confidence Predictions")
            high_conf = insights_df[insights_df['confidence'] >= 0.75]
            if not high_conf.empty:
                st.dataframe(high_conf)
            else:
                st.info("No high confidence predictions at the moment")

            # Value bets
            st.subheader("Potential Value Bets")
            fig = px.scatter(insights_df,
                           x='confidence',
                           y='home_odds',
                           size='confidence',
                           hover_data=['home_team', 'away_team'],
                           title='Value Bet Analysis')
            st.plotly_chart(fig, key="value_bet_chart")
        else:
            st.info("No betting insights available")

    except Exception as e:
        logger.error(f"Error in betting insights: {e}")
        st.error("Error loading betting insights")

with tabs[4]:
    st.markdown("<h2 style='color: #FF4B4B;'>Holzhauer Strategy Analysis</h2>", unsafe_allow_html=True)

    # High-confidence opportunities section
    st.subheader("High-Confidence Opportunities")

    try:
        engine = get_db_connection()
        current_games = pd.read_sql("SELECT * FROM games WHERE status = 'live'", engine)

        if not current_games.empty:
            for _, game in current_games.iterrows():
                # Game header
                st.markdown(f"""
                <div class='stat-container'>
                    <h3 style='color: #FF4B4B;'>{game['home_team']} vs {game['away_team']}</h3>
                    <p style='color: #888;'>Quarter: {game.get('quarter', '1st')} | Time: {game.get('time_remaining', '12:00')}</p>
                </div>
                """, unsafe_allow_html=True)

                # Value bets grid
                st.markdown("<div class='stats-grid'>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("True Probability", "76%", "+2.3%")
                with col2:
                    st.metric("Market Odds", "2.10", "-0.05")
                with col3:
                    st.metric("Value Rating", "8.5", "+0.3")

                # Detailed analysis
                with st.expander("View Detailed Analysis"):
                    # Player props analysis
                    props_df = pd.read_sql(f"""
                        SELECT p.name, pp.prop_type, pp.line, pp.odds
                        FROM player_props pp
                        JOIN players p ON pp.player_id = p.id
                        WHERE pp.game_id = '{game['id']}'
                    """, engine)

                    if not props_df.empty:
                        for _, prop in props_df.iterrows():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"""
                                <div class='metric-card'>
                                    <h4>{prop['name']} - {prop['prop_type']}</h4>
                                    <p>Line: {prop['line']} @ {prop['odds']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            with col2:
                                if float(prop['odds']) > 2.0:
                                    st.markdown("🎯 **Value Bet**")

                # Historical performance chart
                st.subheader("Performance Trend")
                history_df = pd.read_sql(f"""
                    SELECT date, actual_value, line
                    FROM player_prop_history
                    WHERE game_id = '{game['id']}'
                    ORDER BY date DESC
                    LIMIT 10
                """, engine)

                if not history_df.empty:
                    fig = px.line(history_df,
                                x='date',
                                y=['actual_value', 'line'],
                                title='Historical Performance vs Lines')

                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#FAFAFA',
                        showlegend=True,
                        legend=dict(
                            bgcolor='rgba(0,0,0,0)',
                            bordercolor='rgba(255,255,255,0.1)'
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True, key="historical_performance_chart")

        else:
            st.info("No live games available for analysis")

    except Exception as e:
        logger.error(f"Error in Holzhauer analysis: {e}")
        st.error("Error loading Holzhauer analysis")

with tabs[5]:
    st.markdown("<h2 style='color: #FF4B4B;'>NBA Games Analysis</h2>", unsafe_allow_html=True)

    # Refresh button for NBA data
    if st.button("🔄 Refresh NBA Data"):
        with st.spinner("Fetching latest NBA data..."):
            if nba_collector.update_all_data():
                st.success("NBA data updated successfully!")
            else:
                st.error("Error updating NBA data")

    # Display upcoming games
    try:
        DATA_DIR = 'data'
        games_df = pd.read_csv(os.path.join(DATA_DIR, 'nba_games.csv'))
        if not games_df.empty:
            st.subheader("Upcoming Games")

            for _, game in games_df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class='stat-container'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div style='text-align: center; flex: 1;'>
                                <h3 style='color: #FF4B4B;'>{game['home_team']}</h3>
                                <p style='color: #888;'>Home</p>
                            </div>
                            <div style='text-align: center; flex: 0.5;'>
                                <h3 style='color: #FAFAFA;'>VS</h3>
                                <p style='color: #888;'>{game['date']}</p>
                            </div>
                            <div style='text-align: center; flex: 1;'>
                                <h3 style='color: #FF4B4B;'>{game['away_team']}</h3>
                                <p style='color: #888;'>Away</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Add player stats analysis button
                    if st.button(f"Analyze {game['home_team']} vs {game['away_team']}", key=f"analyze_{game['id']}"):
                        with st.spinner("Analyzing game..."):
                            # Get stats for both teams
                            home_stats = nba_collector.get_player_stats(game['home_team'])
                            away_stats = nba_collector.get_player_stats(game['away_team'])

                            if not home_stats.empty and not away_stats.empty:
                                st.write("Player Performance Analysis")

                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"{game['home_team']} Stats")
                                    st.dataframe(home_stats[['player_name', 'points', 'rebounds', 'assists']].head())

                                with col2:
                                    st.write(f"{game['away_team']} Stats")
                                    st.dataframe(away_stats[['player_name', 'points', 'rebounds', 'assists']].head())
        else:
            st.info("No upcoming games found. Click refresh to fetch latest data.")

    except Exception as e:
        logger.error(f"Error displaying NBA games: {e}")
        st.error("Error loading NBA games data")

# Sidebar with enhanced styling
st.sidebar.markdown("<h2 style='color: #FF4B4B;'>System Status</h2>", unsafe_allow_html=True)

# Current time with enhanced styling
st.sidebar.markdown(f"""
<div class='metric-card'>
    <p style='color: #FAFAFA; margin-bottom: 0.5rem;'>Last Update</p>
    <h3 style='color: #FF4B4B; margin: 0;'>{datetime.now().strftime('%H:%M:%S')}</h3>
</div>
""", unsafe_allow_html=True)

# Alert System Status with enhanced styling
alert_status = "🟢 Active" if alert_system.is_running else "🔴 Inactive"
st.sidebar.markdown(f"""
<div class='metric-card'>
    <p style='color: #FAFAFA; margin-bottom: 0.5rem;'>Alert System</p>
    <h3 style='color: #FF4B4B; margin: 0;'>{alert_status}</h3>
</div>
""", unsafe_allow_html=True)

# Enhanced refresh button
if st.sidebar.button("🔄 Refresh Dashboard"):
    st.experimental_rerun()