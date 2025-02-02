import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
from config import DATA_DIR
import os
from sqlalchemy import create_engine
import time

logger = logging.getLogger(__name__)

class NBADataCollector:
    """
    Collects NBA data from balldontlie.io API
    Handles game schedules, player stats, and team performance
    """

    def __init__(self):
        self.base_url = "https://www.balldontlie.io/api/v1"
        os.makedirs(DATA_DIR, exist_ok=True)
        self.games_file = os.path.join(DATA_DIR, 'nba_games.csv')
        self.player_stats_file = os.path.join(DATA_DIR, 'player_stats.csv')
        self.engine = create_engine(os.environ['DATABASE_URL'])
        self.rate_limit_delay = 1.0  # Delay between API calls

    def _handle_api_call(self, url, params=None):
        """Handle API calls with rate limiting and error handling"""
        try:
            time.sleep(self.rate_limit_delay)  # Rate limiting
            response = requests.get(url, params=params)

            if response.status_code == 429:  # Rate limited
                logger.warning("Rate limited, increasing delay")
                self.rate_limit_delay *= 2
                time.sleep(5)
                return self._handle_api_call(url, params)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None

    def fetch_upcoming_games(self, days_ahead=7):
        """Fetch upcoming NBA games for the next week"""
        try:
            start_date = datetime.now().strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

            params = {
                'start_date': start_date,
                'end_date': end_date,
                'per_page': 100
            }

            logger.info(f"Fetching games from {start_date} to {end_date}")
            data = self._handle_api_call(f"{self.base_url}/games", params)

            if not data:
                logger.error("No data received from API")
                return pd.DataFrame()

            games = []
            for game in data['data']:
                if self._validate_game_data(game):
                    games.append({
                        'id': game['id'],
                        'date': game['date'],
                        'home_team': game['home_team']['full_name'],
                        'away_team': game['visitor_team']['full_name'],
                        'home_team_id': game['home_team']['id'],
                        'away_team_id': game['visitor_team']['id'],
                        'status': game['status']
                    })

            if games:
                games_df = pd.DataFrame(games)
                # Ensure data directory exists
                os.makedirs(DATA_DIR, exist_ok=True)
                games_df.to_csv(self.games_file, index=False)
                logger.info(f"Successfully fetched {len(games)} upcoming games")

                # Store in database with proper error handling
                try:
                    with self.engine.begin() as conn:
                        # First clear out old future games to avoid duplicates
                        conn.execute("""
                            DELETE FROM games 
                            WHERE date >= CURRENT_DATE
                        """)
                        # Insert new games
                        games_df.to_sql('games', conn, 
                                    if_exists='append', 
                                    index=False,
                                    method='multi')
                    logger.info("Successfully stored games in database")
                except Exception as db_error:
                    logger.error(f"Database error: {db_error}")

                return games_df

            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error fetching upcoming games: {e}")
            return pd.DataFrame()

    def _validate_game_data(self, game):
        """Validate game data structure"""
        required_fields = ['id', 'date', 'home_team', 'visitor_team', 'status']
        return all(field in game for field in required_fields)

    def get_player_stats(self, player_name):
        """Get stats for a specific player"""
        try:
            params = {'search': player_name}
            player_data = self._handle_api_call(f"{self.base_url}/players", params)

            if not player_data or not player_data['data']:
                logger.warning(f"No player found: {player_name}")
                return pd.DataFrame()

            player = player_data['data'][0]
            player_id = player['id']

            # Get player's stats
            stats_params = {
                'player_ids[]': [player_id],
                'seasons[]': [2023],  # Current season
                'per_page': 100
            }

            stats_data = self._handle_api_call(f"{self.base_url}/stats", stats_params)
            if not stats_data:
                return pd.DataFrame()

            stats = []
            for stat in stats_data['data']:
                if self._validate_stat_data(stat):
                    stats.append({
                        'player_id': player_id,
                        'player_name': f"{player['first_name']} {player['last_name']}",
                        'game_id': stat['game']['id'],
                        'game_date': stat['game']['date'],
                        'points': stat['pts'],
                        'rebounds': stat['reb'],
                        'assists': stat['ast'],
                        'minutes': stat['min'],
                        'field_goal_percentage': stat.get('fg_pct', 0),
                        'three_point_percentage': stat.get('fg3_pct', 0)
                    })

            if stats:
                stats_df = pd.DataFrame(stats)

                # Store in player_performance table
                with self.engine.begin() as conn:
                    stats_df.to_sql('player_performance', conn, 
                                  if_exists='append', 
                                  index=False,
                                  method='multi')

                return stats_df

            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error fetching player stats: {e}")
            return pd.DataFrame()

    def _validate_stat_data(self, stat):
        """Validate player stat data structure"""
        required_fields = ['pts', 'reb', 'ast', 'min']
        return all(field in stat for field in required_fields)

    def update_all_data(self):
        """Update all NBA data"""
        try:
            # Fetch upcoming games
            games_df = self.fetch_upcoming_games()

            if not games_df.empty:
                logger.info("Successfully updated games data")

                # Get stats for players in upcoming games
                for _, game in games_df.iterrows():
                    # Fetch home team stats
                    home_stats = self.get_player_stats(game['home_team'])
                    if not home_stats.empty:
                        logger.info(f"Updated stats for {game['home_team']}")

                    # Fetch away team stats
                    away_stats = self.get_player_stats(game['away_team'])
                    if not away_stats.empty:
                        logger.info(f"Updated stats for {game['away_team']}")

                    # Rate limiting
                    time.sleep(self.rate_limit_delay)

                return True

            return False

        except Exception as e:
            logger.error(f"Error updating all data: {e}")
            return False