import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os
from config import DATA_DIR, ODDS_FILE
import time
import threading

logger = logging.getLogger(__name__)

class OddsCollector:
    def __init__(self):
        self.is_running = False
        self.collection_thread = None
        self.current_odds = pd.DataFrame()
        self.last_update = None
        
    def start_collection(self):
        """Inicia a coleta de odds em uma thread separada"""
        if not self.is_running:
            self.is_running = True
            self.collection_thread = threading.Thread(target=self._collection_loop)
            self.collection_thread.daemon = True
            self.collection_thread.start()
            logger.info("Iniciou coleta de odds")
    
    def stop_collection(self):
        """Para a coleta de odds"""
        self.is_running = False
        if self.collection_thread:
            self.collection_thread.join()
            logger.info("Parou coleta de odds")
    
    def _collection_loop(self):
        """Loop principal de coleta"""
        while self.is_running:
            try:
                self.collect_odds()
                time.sleep(30)  # Coleta a cada 30 segundos
            except Exception as e:
                logger.error(f"Erro no loop de coleta: {e}")
                time.sleep(5)
    
    def collect_odds(self):
        """Coleta odds das diferentes casas de apostas"""
        try:
            # Gera dados de exemplo mais realistas
            odds_data = self._generate_sample_data()
            
            # Atualiza dados em memória
            self.current_odds = pd.DataFrame(odds_data)
            self.last_update = datetime.now()
            
            # Tenta salvar em arquivo, mas não falha se não conseguir
            try:
                if not os.path.exists(DATA_DIR):
                    os.makedirs(DATA_DIR)
                self.current_odds.to_csv(ODDS_FILE, index=False)
            except Exception as e:
                logger.warning(f"Não foi possível salvar arquivo: {e}")
            
            logger.info(f"Coletou odds de {len(odds_data)} jogos")
            return self.current_odds
            
        except Exception as e:
            logger.error(f"Erro ao coletar odds: {e}")
            return pd.DataFrame()
    
    def _generate_sample_data(self):
        """Gera dados de exemplo mais realistas para teste"""
        games = [
            {"home": "Lakers", "away": "Warriors", "league": "NBA"},
            {"home": "Celtics", "away": "Nets", "league": "NBA"},
            {"home": "Bucks", "away": "Heat", "league": "NBA"},
            {"home": "Nuggets", "away": "Suns", "league": "NBA"}
        ]
        
        bookmakers = ["bet365", "Betano", "Sportingbet"]
        
        data = []
        timestamp = datetime.now()
        
        for game in games:
            # Gera odds base para o jogo
            base_home_odd = np.random.uniform(1.5, 3.0)
            base_away_odd = np.random.uniform(1.5, 3.0)
            
            for bookmaker in bookmakers:
                # Adiciona pequena variação para cada bookmaker
                home_variation = np.random.uniform(-0.1, 0.1)
                away_variation = np.random.uniform(-0.1, 0.1)
                
                data.append({
                    'Match': f"{game['home']} vs {game['away']}",
                    'League': game['league'],
                    'Home_Team': game['home'],
                    'Away_Team': game['away'],
                    'Bookmaker': bookmaker,
                    'Home_Odds': round(base_home_odd + home_variation, 2),
                    'Away_Odds': round(base_away_odd + away_variation, 2),
                    'Timestamp': timestamp
                })
        
        return data
    
    def get_current_odds(self):
        """Retorna as odds mais recentes da memória"""
        if self.current_odds.empty:
            # Se não tiver dados em memória, tenta coletar
            self.collect_odds()
        return self.current_odds

    def get_game_data(self, game_id):
        """Retorna dados do jogo"""
        odds_data = self.get_current_odds()
        if not odds_data.empty:
            game = odds_data[odds_data['Match'].str.contains(game_id, case=False)].iloc[0]
            return {
                'id': game_id,
                'home_team': game['Home_Team'],
                'away_team': game['Away_Team'],
                'odds': {
                    'home': float(game['Home_Odds']),
                    'away': float(game['Away_Odds'])
                },
                'last_update': self.last_update.strftime('%H:%M:%S') if self.last_update else None
            }
        return None

    def get_live_games(self):
        """Retorna lista de jogos ativos"""
        odds_data = self.get_current_odds()
        if not odds_data.empty:
            games = odds_data.drop_duplicates('Match')[['Match', 'League', 'Home_Team', 'Away_Team']]
            return games.to_dict('records')
        return []

if __name__ == "__main__":
    collector = OddsCollector()
    collector.start_collection()