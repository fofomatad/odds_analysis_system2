import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from holzhauer_strategy import HolzhauerStrategy

logger = logging.getLogger(__name__)

class NBAAnalyzer:
    """
    NBA-specific implementation of Holzhauer's strategy
    Focuses on player props and game situations
    """
    
    def __init__(self):
        self.strategy = HolzhauerStrategy()
        self.position_factors = {
            'PG': {'assists': 1.1, 'points': 1.0},
            'SG': {'points': 1.1, 'rebounds': 0.9},
            'SF': {'points': 1.05, 'rebounds': 1.05},
            'PF': {'rebounds': 1.1, 'points': 1.0},
            'C': {'rebounds': 1.15, 'points': 0.95}
        }
        
    def analyze_game(self, game_data, player_stats, team_stats):
        """Analyze an NBA game using Holzhauer's principles"""
        try:
            analysis = {
                'game_id': game_data['id'],
                'timestamp': datetime.now(),
                'predictions': [],
                'value_bets': []
            }
            
            # Analyze each player
            for player in game_data.get('players', []):
                player_analysis = self._analyze_player(
                    player,
                    player_stats.get(player['id'], {}),
                    game_data
                )
                
                if player_analysis:
                    analysis['predictions'].extend(player_analysis)
                    
            # Find value bets
            for pred in analysis['predictions']:
                if pred.get('confidence', 0) >= self.strategy.confidence_threshold:
                    value = self.strategy.calculate_bet_value(
                        pred['true_probability'],
                        pred['current_odds']
                    )
                    
                    if value and value['is_value_bet']:
                        analysis['value_bets'].append({
                            **pred,
                            'value_ratio': value['value_ratio'],
                            'expected_value': value['expected_value']
                        })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing NBA game: {e}")
            return None
            
    def _analyze_player(self, player, stats, game_data):
        """Analyze individual player performance"""
        try:
            predictions = []
            
            if not stats:
                return predictions
                
            # Get position-specific factors
            position = player.get('position', 'SF')
            factors = self.position_factors.get(position, {})
            
            # Analyze each statistical category
            categories = ['points', 'rebounds', 'assists', 'threes']
            for category in categories:
                baseline = self._get_baseline(stats, category)
                if not baseline:
                    continue
                    
                # Apply Holzhauer's adjustments
                adjusted = baseline * factors.get(category, 1.0)
                
                # Account for game context
                context = self._get_game_context(game_data, player)
                final_prediction = adjusted * context.get('multiplier', 1.0)
                
                predictions.append({
                    'player_id': player['id'],
                    'player_name': player['name'],
                    'category': category,
                    'prediction': final_prediction,
                    'confidence': context['confidence'],
                    'factors': context['factors']
                })
                
            return predictions
            
        except Exception as e:
            logger.error(f"Error analyzing player: {e}")
            return []
            
    def _get_baseline(self, stats, category):
        """Calculate baseline performance for a category"""
        try:
            recent_games = stats.get('recent_games', [])
            if len(recent_games) < 5:
                return None
                
            values = [game[category] for game in recent_games 
                     if category in game]
            
            if not values:
                return None
                
            return np.mean(values)
            
        except Exception as e:
            logger.error(f"Error getting baseline: {e}")
            return None
            
    def _get_game_context(self, game_data, player):
        """Analyze game context for a player"""
        context = {
            'multiplier': 1.0,
            'confidence': 0.7,  # Base confidence
            'factors': []
        }
        
        # Rest factor
        days_rest = game_data.get('days_rest', {}).get(player['id'], 1)
        if days_rest == 0:
            context['multiplier'] *= 0.95
            context['confidence'] *= 0.9
            context['factors'].append('back_to_back')
        elif days_rest >= 3:
            context['multiplier'] *= 1.05
            context['confidence'] *= 1.1
            context['factors'].append('well_rested')
            
        # Home/Away
        if game_data.get('is_home_team', False):
            context['multiplier'] *= 1.03
            context['confidence'] *= 1.05
            context['factors'].append('home_game')
            
        return context
