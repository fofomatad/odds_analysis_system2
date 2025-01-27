import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import logging

class OddsCollector:
    def __init__(self, update_interval=15):  # Reduzido para 15 segundos
        self.update_interval = update_interval
        self.current_odds = pd.DataFrame()
        self.last_update = None
        self.running = False
        self.thread = None
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _generate_sample_data(self):
        """Gera dados de exemplo usando a estratégia Holzhauer"""
        games = [
            {
                'home': 'Liverpool',
                'away': 'Manchester City',
                'start_time': datetime.now() + timedelta(minutes=30),
                'league': 'Premier League',
                'historical_h2h': '2W-1D-1L',
                'market_movement': 'Subindo',
            },
            {
                'home': 'Barcelona',
                'away': 'Real Madrid',
                'start_time': datetime.now() + timedelta(minutes=15),
                'league': 'La Liga',
                'historical_h2h': '3W-0D-2L',
                'market_movement': 'Estável',
            },
            {
                'home': 'Bayern',
                'away': 'Dortmund',
                'start_time': datetime.now() + timedelta(minutes=5),
                'league': 'Bundesliga',
                'historical_h2h': '4W-1D-0L',
                'market_movement': 'Descendo',
            }
        ]
        
        data = []
        for game in games:
            # Cálculo de odds usando a estratégia Holzhauer
            base_prob = np.random.uniform(0.4, 0.6)
            market_inefficiency = np.random.uniform(-0.1, 0.1)
            
            # Odds ajustadas com base na ineficiência do mercado
            home_odds = round(1 / (base_prob + market_inefficiency), 2)
            draw_odds = round(1 / (0.25 + market_inefficiency), 2)
            away_odds = round(1 / (1 - base_prob + market_inefficiency), 2)
            
            # Cálculo de valor esperado (EV)
            true_prob = base_prob + (market_inefficiency * 0.5)
            ev = (true_prob * home_odds) - 1
            
            # Cálculo de confiança baseado em múltiplos fatores
            confidence = self._calculate_confidence(
                market_movement=game['market_movement'],
                time_to_start=(game['start_time'] - datetime.now()).total_seconds() / 60,
                h2h=game['historical_h2h']
            )
            
            data.append({
                'game': f"{game['home']} vs {game['away']}",
                'league': game['league'],
                'start_time': game['start_time'],
                'time_to_start': f"{(game['start_time'] - datetime.now()).total_seconds() / 60:.0f} min",
                'home_odds': home_odds,
                'draw_odds': draw_odds,
                'away_odds': away_odds,
                'home_team': game['home'],
                'away_team': game['away'],
                'confidence': round(confidence, 1),
                'value_bet': round(ev * 100, 1),
                'market_movement': game['market_movement'],
                'h2h': game['historical_h2h'],
                'recommended_stake': self._calculate_stake(ev, confidence),
                'bet_timing': self._get_bet_timing(game['start_time']),
                'kelly_criterion': self._calculate_kelly(true_prob, home_odds)
            })
        
        return data

    def _calculate_confidence(self, market_movement, time_to_start, h2h):
        """Calcula a confiança baseada na estratégia Holzhauer"""
        base_confidence = 70
        
        # Ajuste baseado no movimento do mercado
        movement_adj = {
            'Subindo': 5,
            'Estável': 0,
            'Descendo': -5
        }.get(market_movement, 0)
        
        # Ajuste baseado no tempo até o início
        time_adj = min(10, max(-10, (30 - time_to_start) / 3))
        
        # Ajuste baseado no histórico H2H
        wins = int(h2h[0])
        h2h_adj = wins * 2
        
        return min(95, max(60, base_confidence + movement_adj + time_adj + h2h_adj))

    def _calculate_stake(self, ev, confidence):
        """Calcula o stake recomendado (% do bankroll)"""
        if ev <= 0 or confidence < 70:
            return 0
        base_stake = ev * (confidence / 100)
        return min(5, max(1, round(base_stake * 100, 1)))

    def _get_bet_timing(self, start_time):
        """Determina o melhor momento para apostar"""
        minutes_to_start = (start_time - datetime.now()).total_seconds() / 60
        
        if minutes_to_start <= 5:
            return "APOSTAR AGORA! 🔥"
        elif minutes_to_start <= 15:
            return "Monitorar de perto 👀"
        else:
            return "Aguardar ⏳"

    def _calculate_kelly(self, prob, odds):
        """Calcula o critério de Kelly para gestão de banca"""
        q = 1 - prob
        b = odds - 1
        f = (b * prob - q) / b
        return max(0, round(f * 100, 1))

    def get_opportunities(self, confidence_threshold=75, value_threshold=3):
        """Retorna oportunidades de apostas baseadas nos critérios Holzhauer"""
        if self.current_odds.empty:
            return []
        
        opportunities = self.current_odds[
            (self.current_odds['confidence'] >= confidence_threshold) &
            (self.current_odds['value_bet'] >= value_threshold) &
            (self.current_odds['bet_timing'] == "APOSTAR AGORA! 🔥")
        ]
        
        return opportunities.to_dict('records')

    # ... (manter os outros métodos existentes)
