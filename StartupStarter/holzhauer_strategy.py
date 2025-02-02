import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class HolzhauerStrategy:
    """
    Implements James Holzhauer's aggressive, data-driven betting strategy.
    Key principles:
    1. High-confidence bets with maximum value
    2. Statistical analysis of historical performance
    3. Multi-source data integration
    4. Risk-adjusted decision making
    """
    
    def __init__(self):
        self.confidence_threshold = 0.75  # Only bet on 75%+ confidence
        self.value_threshold = 1.15  # Minimum value ratio for bets
        self.min_data_points = 10  # Minimum historical data points needed
        
    def calculate_bet_value(self, true_probability, offered_odds):
        """Calculate the expected value of a bet using Holzhauer's method"""
        try:
            decimal_odds = self._convert_to_decimal(offered_odds)
            implied_probability = 1 / decimal_odds
            value_ratio = true_probability / implied_probability
            
            return {
                'value_ratio': value_ratio,
                'expected_value': (true_probability * decimal_odds) - 1,
                'is_value_bet': value_ratio > self.value_threshold
            }
        except Exception as e:
            logger.error(f"Error calculating bet value: {e}")
            return None
            
    def analyze_player_props(self, player_stats, current_odds, game_context):
        """Analyze player proposition bets using Holzhauer's methods"""
        try:
            analysis = []
            
            # Calculate baseline performance
            baseline = self._calculate_baseline(player_stats)
            
            # Adjust for recent form
            form_factor = self._analyze_recent_form(player_stats)
            
            # Adjust for game context
            context_multiplier = self._analyze_game_context(game_context)
            
            # Calculate true probability
            adjusted_probability = baseline * form_factor * context_multiplier
            
            for prop in current_odds:
                value = self.calculate_bet_value(
                    adjusted_probability,
                    prop['odds']
                )
                
                if value and value['is_value_bet']:
                    analysis.append({
                        'prop_type': prop['type'],
                        'confidence': min(adjusted_probability, 0.95),
                        'value_ratio': value['value_ratio'],
                        'recommendation': 'BET' if value['value_ratio'] > 1.2 else 'MONITOR'
                    })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing player props: {e}")
            return []
            
    def _calculate_baseline(self, stats):
        """Calculate baseline performance probability"""
        try:
            if len(stats) < self.min_data_points:
                return 0.5
                
            return np.mean(stats['success_rate'])
        except Exception as e:
            logger.error(f"Error calculating baseline: {e}")
            return 0.5
            
    def _analyze_recent_form(self, stats):
        """Analyze recent performance trends"""
        try:
            recent_games = stats.sort_values('date').tail(5)
            trend = np.polyfit(range(len(recent_games)), 
                             recent_games['performance'], 
                             deg=1)[0]
            
            # Convert trend to multiplier
            return 1 + (trend * 0.1)  # 10% adjustment per trend unit
        except Exception as e:
            logger.error(f"Error analyzing recent form: {e}")
            return 1.0
            
    def _analyze_game_context(self, context):
        """Analyze game context factors"""
        factors = {
            'back_to_back': 0.9,
            'rest_advantage': 1.1,
            'home_game': 1.05,
            'rivalry_game': 1.02
        }
        
        multiplier = 1.0
        for factor, impact in factors.items():
            if context.get(factor, False):
                multiplier *= impact
                
        return multiplier
        
    def _convert_to_decimal(self, odds):
        """Convert various odds formats to decimal"""
        if isinstance(odds, (int, float)):
            return float(odds)
        
        # American odds conversion
        if isinstance(odds, str):
            if odds.startswith('+'):
                return 1 + (float(odds[1:]) / 100)
            elif odds.startswith('-'):
                return 1 + (100 / float(odds[1:]))
                
        return float(odds)
        
    def is_healthy(self):
        """Health check for monitoring"""
        return True
