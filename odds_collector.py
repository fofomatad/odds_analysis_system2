import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import logging

class OddsCollector:
    def __init__(self, update_interval=15):
        self.update_interval = update_interval
        self.current_odds = pd.DataFrame()
        self.last_update = None
        self.running = False
        self.thread = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._collection_loop)
            self.thread.daemon = True
            self.thread.start()
            self.logger.info("Iniciou coleta de odds NBA")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            self.logger.info("Parou coleta de odds")

    def _collection_loop(self):
        while self.running:
            try:
                self.collect_odds()
                time.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"Erro na coleta: {str(e)}")
                time.sleep(5)

    def valor_esperado(self, prob_acerto, odds):
        """Calcula o valor esperado (EV) da aposta"""
        ganho = (odds - 1)  # Ganho líquido se acertar
        perda = -1  # Perda se errar
        prob_erro = 1 - prob_acerto
        return (prob_acerto * ganho) + (prob_erro * perda)

    def criterio_kelly(self, prob_acerto, odds):
        """Calcula a fração ideal de banca usando critério de Kelly"""
        q = 1 - prob_acerto
        b = odds - 1
        f = (b * prob_acerto - q) / b
        return max(0, min(0.05, round(f, 3)))  # Limitado a 5% da banca

    def _generate_nba_games(self):
        """Gera dados de exemplo para jogos da NBA"""
        games = [
            {
                'home': 'Lakers',
                'away': 'Warriors',
                'start_time': datetime.now() + timedelta(minutes=30),
                'home_form': '7-3',
                'away_form': '6-4',
                'market_movement': 'Subindo',
                'key_players': 'LeBron (P), Curry (P)',
            },
            {
                'home': 'Celtics',
                'away': 'Bucks',
                'start_time': datetime.now() + timedelta(minutes=15),
                'home_form': '8-2',
                'away_form': '7-3',
                'market_movement': 'Estável',
                'key_players': 'Tatum (P), Giannis (P)',
            },
            {
                'home': 'Nets',
                'away': 'Heat',
                'start_time': datetime.now() + timedelta(minutes=5),
                'home_form': '5-5',
                'away_form': '6-4',
                'market_movement': 'Descendo',
                'key_players': 'Durant (D), Butler (P)',
            }
        ]
        
        data = []
        for game in games:
            # Probabilidades baseadas em forma e fatores
            home_strength = int(game['home_form'].split('-')[0])
            away_strength = int(game['away_form'].split('-')[0])
            
            # Cálculo de probabilidade base
            total_strength = home_strength + away_strength
            base_prob = home_strength / total_strength
            
            # Ajuste por fatores de mercado
            market_adj = {
                'Subindo': 0.05,
                'Estável': 0,
                'Descendo': -0.05
            }.get(game['market_movement'], 0)
            
            # Probabilidade ajustada
            prob_acerto = min(0.95, max(0.05, base_prob + market_adj))
            
            # Odds e valor esperado
            odds = round(1 / prob_acerto, 2)
            ev = self.valor_esperado(prob_acerto, odds)
            
            # Confiança baseada em múltiplos fatores
            confidence = self._calculate_confidence(
                market_movement=game['market_movement'],
                time_to_start=(game['start_time'] - datetime.now()).total_seconds() / 60,
                form=game['home_form']
            )
            
            # Kelly stake
            kelly = self.criterio_kelly(prob_acerto, odds)
            
            data.append({
                'game': f"{game['home']} vs {game['away']}",
                'start_time': game['start_time'],
                'time_to_start': f"{(game['start_time'] - datetime.now()).total_seconds() / 60:.0f} min",
                'odds': odds,
                'prob_acerto': f"{prob_acerto*100:.1f}%",
                'home_form': game['home_form'],
                'away_form': game['away_form'],
                'key_players': game['key_players'],
                'confidence': round(confidence, 1),
                'value_bet': round(ev * 100, 1),
                'market_movement': game['market_movement'],
                'kelly_stake': f"{kelly*100:.1f}%",
                'bet_timing': self._get_bet_timing(game['start_time']),
                'recommendation': self._get_recommendation(ev, confidence, kelly)
            })
        
        return data

    def _calculate_confidence(self, market_movement, time_to_start, form):
        """Calcula confiança baseada na estratégia Holzhauer para NBA"""
        base_confidence = 70
        
        # Ajuste por movimento de mercado
        movement_adj = {
            'Subindo': 5,
            'Estável': 0,
            'Descendo': -5
        }.get(market_movement, 0)
        
        # Ajuste por timing
        time_adj = min(10, max(-10, (30 - time_to_start) / 3))
        
        # Ajuste por forma recente
        wins = int(form.split('-')[0])
        form_adj = (wins - 5) * 2  # 5 vitórias é neutro
        
        return min(95, max(60, base_confidence + movement_adj + time_adj + form_adj))

    def _get_bet_timing(self, start_time):
        """Timing Holzhauer para apostas NBA"""
        minutes_to_start = (start_time - datetime.now()).total_seconds() / 60
        
        if minutes_to_start <= 5:
            return "🔥 APOSTAR AGORA!"
        elif minutes_to_start <= 15:
            return "👀 Monitorar Lineup"
        else:
            return "⏳ Aguardar Informações"

    def _get_recommendation(self, ev, confidence, kelly):
        """Recomendação de aposta estilo Holzhauer"""
        if ev <= 0 or confidence < 75 or kelly <= 0:
            return "❌ Passar"
        elif ev >= 0.1 and confidence >= 85 and kelly >= 0.03:
            return "💰 Value Bet Forte"
        else:
            return "⚠️ Value Bet Moderado"

    def collect_odds(self):
        try:
            odds_data = self._generate_nba_games()
            self.current_odds = pd.DataFrame(odds_data)
            self.last_update = datetime.now()
            self.logger.info(f"Coletou odds para {len(odds_data)} jogos NBA")
        except Exception as e:
            self.logger.error(f"Erro ao coletar odds: {str(e)}")

    def get_live_games(self):
        if self.current_odds.empty:
            return []
        return self.current_odds.to_dict('records')

    def get_opportunities(self, confidence_threshold=75, value_threshold=3):
        if self.current_odds.empty:
            return []
        
        opportunities = self.current_odds[
            (self.current_odds['confidence'] >= confidence_threshold) &
            (self.current_odds['value_bet'] >= value_threshold) &
            (self.current_odds['bet_timing'] == "🔥 APOSTAR AGORA!")
        ]
        
        return opportunities.to_dict('records')
