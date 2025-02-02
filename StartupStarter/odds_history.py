import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from config import DATA_DIR
import json
import logging

logger = logging.getLogger(__name__)

class OddsHistory:
    def __init__(self):
        self.history_file = os.path.join(DATA_DIR, 'odds_history.csv')
        self.max_history_days = 7  # Mantém histórico dos últimos 7 dias
        self._initialize_history()

    def _initialize_history(self):
        """Inicializa ou carrega o arquivo de histórico"""
        try:
            if not os.path.exists(self.history_file):
                self._create_empty_history()
            else:
                self._clean_old_records()
        except Exception as e:
            logger.error(f"Erro ao inicializar histórico: {e}")
            self._create_empty_history()

    def _create_empty_history(self):
        """Cria um arquivo de histórico vazio"""
        df = pd.DataFrame(columns=[
            'timestamp', 'match', 'side', 'odds', 'bookmaker'
        ])
        df.to_csv(self.history_file, index=False)

    def _clean_old_records(self):
        """Remove registros mais antigos que max_history_days"""
        try:
            df = pd.read_csv(self.history_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            cutoff_date = datetime.now() - timedelta(days=self.max_history_days)
            df = df[df['timestamp'] > cutoff_date]
            df.to_csv(self.history_file, index=False)
        except Exception as e:
            logger.error(f"Erro ao limpar registros antigos: {e}")

    def add_odds(self, match, side, odds, bookmaker):
        """Adiciona novo registro de odds ao histórico"""
        try:
            new_record = pd.DataFrame([{
                'timestamp': datetime.now(),
                'match': match,
                'side': side,
                'odds': odds,
                'bookmaker': bookmaker
            }])
            
            df = pd.read_csv(self.history_file)
            df = pd.concat([df, new_record], ignore_index=True)
            df.to_csv(self.history_file, index=False)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar odds: {e}")
            return False

    def get_odds_history(self, hours=24):
        """Retorna histórico de odds com filtros opcionais"""
        try:
            df = pd.read_csv(self.history_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filtrar por período
            cutoff_time = datetime.now() - timedelta(hours=hours)
            df = df[df['timestamp'] > cutoff_time]
            
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {e}")
            return []

    def get_trend_analysis(self):
        """Analisa tendências nas odds"""
        try:
            if not os.path.exists(self.history_file):
                return {}
                
            history_df = pd.read_csv(self.history_file)
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            
            trends = {
                'increasing': [],  # Odds aumentando
                'decreasing': [],  # Odds diminuindo
                'volatile': []     # Odds instáveis
            }
            
            for match in history_df['match'].unique():
                match_data = history_df[history_df['match'] == match].copy()
                if len(match_data) < 3:  # Precisa de pelo menos 3 pontos
                    continue
                    
                for side in ['Home', 'Away']:
                    odds_col = f'{side}_Odds'
                    odds_series = match_data[odds_col]
                    
                    # Calcula volatilidade
                    volatility = odds_series.std() / odds_series.mean()
                    
                    # Determina tendência
                    slope = np.polyfit(range(len(odds_series)), odds_series, 1)[0]
                    
                    trend_info = {
                        'Match': match,
                        'Side': side,
                        'Current_Odds': odds_series.iloc[-1],
                        'Volatility': volatility
                    }
                    
                    if volatility > 0.1:  # Alta volatilidade
                        trends['volatile'].append(trend_info)
                    elif slope > 0.01:    # Tendência de alta
                        trends['increasing'].append(trend_info)
                    elif slope < -0.01:   # Tendência de baixa
                        trends['decreasing'].append(trend_info)
            
            return trends
            
        except Exception as e:
            logger.error(f"Erro ao analisar tendências: {e}")
            return {}
