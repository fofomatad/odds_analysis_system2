import pandas as pd
import numpy as np
from datetime import datetime
import threading
import time
import logging

class OddsCollector:
    def __init__(self, update_interval=30):
        self.update_interval = update_interval
        self.current_odds = pd.DataFrame()
        self.last_update = None
        self.running = False
        self.thread = None
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Inicia a coleta de odds em uma thread separada"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._collection_loop)
            self.thread.daemon = True
            self.thread.start()
            self.logger.info("Iniciou coleta de odds")

    def stop(self):
        """Para a coleta de odds"""
        self.running = False
        if self.thread:
            self.thread.join()
            self.logger.info("Parou coleta de odds")

    def _collection_loop(self):
        """Loop principal de coleta"""
        while self.running:
            try:
                self.collect_odds()
                time.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"Erro na coleta: {str(e)}")
                time.sleep(5)  # Espera um pouco antes de tentar novamente

    def _generate_sample_data(self):
        """Gera dados de exemplo para demonstração"""
        games = [
            "Time A vs Time B",
            "Time C vs Time D",
            "Time E vs Time F"
        ]
        
        data = []
        for game in games:
            home_odds = np.random.uniform(1.5, 3.0)
            draw_odds = np.random.uniform(2.5, 4.0)
            away_odds = np.random.uniform(1.5, 3.0)
            
            data.append({
                'game': game,
                'home_odds': round(home_odds, 2),
                'draw_odds': round(draw_odds, 2),
                'away_odds': round(away_odds, 2),
                'timestamp': datetime.now(),
                'confidence': round(np.random.uniform(60, 90), 2),
                'value_bet': round(np.random.uniform(0, 10), 2)
            })
        
        return data

    def collect_odds(self):
        """Coleta as odds e atualiza o estado interno"""
        try:
            odds_data = self._generate_sample_data()
            self.current_odds = pd.DataFrame(odds_data)
            self.last_update = datetime.now()
            self.logger.info(f"Coletou odds para {len(odds_data)} jogos")
        except Exception as e:
            self.logger.error(f"Erro ao coletar odds: {str(e)}")

    def get_live_games(self):
        """Retorna os jogos ativos com suas odds"""
        if self.current_odds.empty:
            return []
        
        return self.current_odds.to_dict('records')

    def get_opportunities(self, confidence_threshold=75, value_threshold=5):
        """Retorna oportunidades de apostas baseadas nos critérios"""
        if self.current_odds.empty:
            return []
        
        opportunities = self.current_odds[
            (self.current_odds['confidence'] >= confidence_threshold) &
            (self.current_odds['value_bet'] >= value_threshold)
        ]
        
        return opportunities.to_dict('records')
