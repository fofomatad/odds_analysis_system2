import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
import time
import json

class NBAOddsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.logger = logging.getLogger(__name__)

    def get_player_stats(self, player_name, team):
        """Coleta estatísticas do jogador das últimas 5 partidas"""
        try:
            url = f'https://www.basketball-reference.com/players/{player_name[0]}/{player_name}.html'
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return self._parse_player_stats(soup)
            return None
        except Exception as e:
            self.logger.error(f"Erro ao coletar stats do jogador: {str(e)}")
            return None

    def get_player_props(self, game_id):
        """Coleta props dos jogadores para um jogo específico"""
        try:
            # Exemplo de dados simulados - substitua por scraping real
            props = {
                'LeBron James': {
                    'points': {'line': 25.5, 'over_odds': 1.87, 'under_odds': 1.87, 
                             'last_5': [28, 32, 25, 27, 30], 'avg': 28.4,
                             'matchup_rating': 8.5},
                    'rebounds': {'line': 7.5, 'over_odds': 1.95, 'under_odds': 1.85,
                               'last_5': [8, 7, 9, 6, 8], 'avg': 7.6,
                               'matchup_rating': 7.8},
                    'assists': {'line': 6.5, 'over_odds': 1.90, 'under_odds': 1.90,
                              'last_5': [7, 8, 6, 7, 5], 'avg': 6.6,
                              'matchup_rating': 8.0}
                },
                'Stephen Curry': {
                    'points': {'line': 28.5, 'over_odds': 1.85, 'under_odds': 1.95,
                             'last_5': [32, 29, 35, 27, 31], 'avg': 30.8,
                             'matchup_rating': 9.0},
                    'rebounds': {'line': 5.5, 'over_odds': 1.87, 'under_odds': 1.87,
                               'last_5': [4, 6, 5, 7, 5], 'avg': 5.4,
                               'matchup_rating': 7.5},
                    'assists': {'line': 5.5, 'over_odds': 1.90, 'under_odds': 1.90,
                              'last_5': [6, 7, 4, 6, 5], 'avg': 5.6,
                              'matchup_rating': 8.2}
                }
            }
            return props
        except Exception as e:
            self.logger.error(f"Erro ao coletar props: {str(e)}")
            return {}

    def analyze_prop_bet(self, prop_data):
        """Analisa uma prop bet específica usando a estratégia Holzhauer"""
        try:
            line = prop_data['line']
            avg = prop_data['avg']
            last_5 = prop_data['last_5']
            matchup_rating = prop_data['matchup_rating']
            
            # Calcula tendência
            trend = sum(1 for x in last_5 if x > line) / 5
            
            # Calcula valor esperado
            ev = self._calculate_prop_ev(avg, line, prop_data['over_odds'])
            
            # Calcula confiança
            confidence = self._calculate_prop_confidence(trend, matchup_rating, avg, line)
            
            # Determina recomendação
            if ev > 0.1 and confidence > 80:
                recommendation = "💰 FORTE VALOR"
            elif ev > 0.05 and confidence > 70:
                recommendation = "✅ VALOR MODERADO"
            else:
                recommendation = "⚠️ PASSAR"
            
            return {
                'ev': round(ev * 100, 1),
                'confidence': round(confidence, 1),
                'trend': f"{trend*100:.0f}%",
                'recommendation': recommendation,
                'analysis': self._get_prop_analysis(avg, line, last_5, matchup_rating)
            }
        except Exception as e:
            self.logger.error(f"Erro na análise de prop: {str(e)}")
            return None

    def _calculate_prop_ev(self, avg, line, odds):
        """Calcula o valor esperado de uma prop"""
        prob_over = 0.5 + (avg - line) / (2 * line)  # Ajusta probabilidade com base na média
        return (prob_over * (odds - 1)) - (1 - prob_over)

    def _calculate_prop_confidence(self, trend, matchup_rating, avg, line):
        """Calcula a confiança em uma prop"""
        base_confidence = 70
        
        # Ajuste por tendência
        trend_adj = (trend - 0.5) * 20
        
        # Ajuste por matchup
        matchup_adj = (matchup_rating - 7) * 5
        
        # Ajuste por diferença da média
        avg_diff = abs(avg - line) / line
        avg_adj = avg_diff * 20
        
        return min(95, max(60, base_confidence + trend_adj + matchup_adj + avg_adj))

    def _get_prop_analysis(self, avg, line, last_5, matchup_rating):
        """Gera análise detalhada da prop"""
        analysis = []
        
        if avg > line:
            analysis.append(f"Média ({avg:.1f}) acima da linha ({line})")
        else:
            analysis.append(f"Média ({avg:.1f}) abaixo da linha ({line})")
            
        hits = sum(1 for x in last_5 if x > line)
        analysis.append(f"Bateu em {hits}/5 últimos jogos")
        
        if matchup_rating >= 8:
            analysis.append("Ótimo matchup para esta prop")
        elif matchup_rating >= 7:
            analysis.append("Matchup favorável")
        else:
            analysis.append("Matchup difícil")
            
        return " | ".join(analysis)

    def get_nba_games(self):
        """Coleta jogos e props da NBA"""
        games = []
        
        # Simulação de jogos - substitua por scraping real
        sample_games = [
            {
                'id': 'LAL-GSW-20250127',
                'home': 'Lakers',
                'away': 'Warriors',
                'time': datetime.now() + timedelta(hours=2),
                'status': 'Próximo'
            },
            {
                'id': 'BOS-MIL-20250127',
                'home': 'Celtics',
                'away': 'Bucks',
                'time': datetime.now() + timedelta(minutes=30),
                'status': 'Em breve'
            }
        ]
        
        for game in sample_games:
            props = self.get_player_props(game['id'])
            analyzed_props = {}
            
            for player, player_props in props.items():
                analyzed_props[player] = {}
                for prop_type, prop_data in player_props.items():
                    analysis = self.analyze_prop_bet(prop_data)
                    if analysis:
                        analyzed_props[player][prop_type] = {
                            **prop_data,
                            'analysis': analysis
                        }
            
            games.append({
                **game,
                'props': analyzed_props
            })
            
            time.sleep(1)  # Respeita rate limits
            
        return games
