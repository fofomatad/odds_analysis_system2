import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
import time

class NBAOddsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.logger = logging.getLogger(__name__)

    def get_odds_from_oddsportal(self):
        """Coleta odds do OddsPortal (exemplo de implementação)"""
        try:
            url = 'https://www.oddsportal.com/basketball/usa/nba'
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Implementar parser específico para o site
                return self._parse_odds_portal(soup)
            else:
                self.logger.error(f"Erro ao acessar OddsPortal: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Erro no scraping: {str(e)}")
            return []

    def get_reddit_sentiment(self, team):
        """Coleta sentimento do Reddit r/nba"""
        try:
            url = f'https://www.reddit.com/r/nba/search.json?q={team}&restrict_sr=1&sort=new'
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                posts = response.json()['data']['children']
                sentiments = []
                for post in posts[:5]:  # Analisa os 5 posts mais recentes
                    text = post['data']['title'] + ' ' + post['data']['selftext']
                    sentiment = self.sentiment_analyzer.polarity_scores(text)['compound']
                    sentiments.append(sentiment)
                return sum(sentiments) / len(sentiments) if sentiments else 0
            return 0
        except Exception as e:
            self.logger.error(f"Erro ao coletar sentimento: {str(e)}")
            return 0

    def get_injury_news(self, team):
        """Coleta informações de lesões do RotoWire"""
        try:
            url = f'https://www.rotowire.com/basketball/team/injuries.php?team={team}'
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Implementar parser específico para o site
                return self._parse_injury_news(soup)
            return "Sem informações"
        except Exception as e:
            self.logger.error(f"Erro ao coletar lesões: {str(e)}")
            return "Erro ao coletar"

    def _parse_odds_portal(self, soup):
        """Parser específico para OddsPortal"""
        games = []
        try:
            # Implementar parser específico para o site
            # Este é um exemplo simplificado
            game_rows = soup.find_all('tr', {'class': 'deactivate'})
            for row in game_rows:
                teams = row.find('td', {'class': 'name'}).text.strip().split(' - ')
                if len(teams) == 2:
                    home_team, away_team = teams
                    odds = row.find_all('td', {'class': 'odds'})
                    if odds:
                        games.append({
                            'home_team': home_team,
                            'away_team': away_team,
                            'home_odds': float(odds[0].text),
                            'away_odds': float(odds[1].text),
                            'timestamp': datetime.now()
                        })
        except Exception as e:
            self.logger.error(f"Erro no parsing: {str(e)}")
        return games

    def _parse_injury_news(self, soup):
        """Parser específico para RotoWire"""
        try:
            injuries = soup.find_all('div', {'class': 'injury'})
            return [injury.text.strip() for injury in injuries]
        except Exception as e:
            self.logger.error(f"Erro no parsing de lesões: {str(e)}")
            return []

    def analyze_value_bet(self, implied_prob, true_prob, odds):
        """Análise de value bet usando a estratégia Holzhauer"""
        ev = (true_prob * odds) - 1
        kelly = self._calculate_kelly(true_prob, odds)
        confidence = self._calculate_confidence(implied_prob, true_prob)
        
        return {
            'ev': ev,
            'kelly': kelly,
            'confidence': confidence
        }

    def _calculate_kelly(self, prob, odds):
        """Implementação do Critério de Kelly"""
        q = 1 - prob
        b = odds - 1
        f = (b * prob - q) / b
        return max(0, min(0.05, f))  # Limita a 5% da banca

    def _calculate_confidence(self, implied_prob, true_prob):
        """Calcula confiança baseada na diferença entre probabilidades"""
        diff = abs(implied_prob - true_prob)
        base_confidence = 70
        
        if diff > 0.1:
            confidence_adj = 15
        elif diff > 0.05:
            confidence_adj = 10
        else:
            confidence_adj = 5
            
        return min(95, base_confidence + confidence_adj)

    def get_nba_games(self):
        """Coleta e analisa todos os dados para jogos da NBA"""
        games = self.get_odds_from_oddsportal()
        analyzed_games = []
        
        for game in games:
            home_sentiment = self.get_reddit_sentiment(game['home_team'])
            away_sentiment = self.get_reddit_sentiment(game['away_team'])
            
            home_injuries = self.get_injury_news(game['home_team'])
            away_injuries = self.get_injury_news(game['away_team'])
            
            # Calcula probabilidades ajustadas com base no sentimento
            implied_prob_home = 1 / game['home_odds']
            sentiment_adj = (home_sentiment - away_sentiment) * 0.05
            true_prob_home = min(0.95, max(0.05, implied_prob_home + sentiment_adj))
            
            # Análise de value bet
            value_analysis = self.analyze_value_bet(implied_prob_home, true_prob_home, game['home_odds'])
            
            analyzed_games.append({
                'game': f"{game['home_team']} vs {game['away_team']}",
                'start_time': game['timestamp'],
                'odds': game['home_odds'],
                'implied_prob': f"{implied_prob_home*100:.1f}%",
                'true_prob': f"{true_prob_home*100:.1f}%",
                'value_bet': round(value_analysis['ev'] * 100, 1),
                'kelly_stake': f"{value_analysis['kelly']*100:.1f}%",
                'confidence': value_analysis['confidence'],
                'home_sentiment': round(home_sentiment, 2),
                'away_sentiment': round(away_sentiment, 2),
                'injuries': f"Home: {home_injuries}, Away: {away_injuries}"
            })
            
            # Respeita rate limits
            time.sleep(1)
        
        return analyzed_games
