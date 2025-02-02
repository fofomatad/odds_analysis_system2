import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class HolzhauerNBAAnalyzer:
    def __init__(self) -> None:
        self.confidence_threshold: float = 0.8
        self.high_value_threshold: float = 5.0

    def analyze_quarter_patterns(self, game_data: pd.DataFrame, current_quarter: int = 1) -> Dict[str, Dict[str, Any]]:
        patterns = {f'q{quarter}': {'média': 0, 'tendência': 'estável'} for quarter in range(1, 5)}
        return patterns

    def identify_hot_streaks(self, player_data: pd.DataFrame) -> Dict[str, Any]:
        return {'current_streak': 0, 'max_streak': 0, 'is_hot': False}

    def find_prime_opportunities(self, player_stats: pd.DataFrame, current_game_stats: pd.DataFrame) -> List[Dict[str, Any]]:
        return []

    def generate_game_plan(self, player_stats: pd.DataFrame, opponent_stats: pd.DataFrame, game_situation: Dict[str, Any]) -> Dict[str, Any]:
        return {'momentum': {'overall_factor': 1.0}, 'high_value_targets': []}

    def adjust_confidence_by_momentum(self, base_confidence: float, momentum_factor: float) -> float:
        return min(base_confidence * momentum_factor, 1.0)

    def detect_momentum_shifts(self, player_stats: pd.DataFrame, game_situation: Dict[str, Any]) -> Dict[str, Any]:
        return {'has_shift': False, 'direction': 'neutral', 'intensity': 0}

    def analyze_matchup_history(self, player_stats: pd.DataFrame, opponent_stats: pd.DataFrame, current_matchup: Dict[str, Any]) -> Dict[str, Any]:
        return {'advantage': 'neutral', 'confidence': 0.5}

    def analyze_player_mood(self, player_name: str, game_date: datetime, recent_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {'mood_score': 0.5, 'confidence_impact': 0}

    def _analyze_trend(self, data_series: pd.Series) -> str:
        if len(data_series) < 2:
            return 'estável'
        trend = 'up' if data_series.iloc[-1] > data_series.iloc[0] else 'down'
        return trend


class HolzhauerStrategy:
    def __init__(self) -> None:
        self.model_file: str = os.path.join(os.getenv('DATA_DIR', '.'), 'holzhauer_model.joblib')
        self.scaler_file: str = os.path.join(os.getenv('DATA_DIR', '.'), 'holzhauer_scaler.joblib')
        self.min_confidence: float = 0.75
        self.model: RandomForestClassifier = self._load_model()
        self.scaler: StandardScaler = self._load_scaler()

        self.momentum_window: int = 10
        self.volatility_threshold: float = 0.1
        self.efficiency_threshold: float = 0.02
        self.value_threshold: float = 0.1

    def analyze_opportunity(self, match_data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        try:
            features = self._extract_features(match_data)
            if features is None:
                logger.warning("Features não extraídas.")
                return None

            features_scaled = self.scaler.transform([features])
            confidence = self.model.predict_proba(features_scaled)[0][1]

            return {
                'confidence': confidence,
                'recommended': confidence >= self.min_confidence,
                'momentum': self._analyze_momentum(match_data),
                'market_efficiency': self._analyze_market_efficiency(match_data),
                'value_opportunities': self._find_value_opportunities(match_data),
                'risk_assessment': self._assess_risk(match_data)
            }
        except Exception as e:
            logger.error(f"Erro ao analisar oportunidade: {e}")
            return None

    def _analyze_momentum(self, match_data: pd.DataFrame) -> Dict[str, Any]:
        odds_series = match_data['Home_Odds'].values
        if len(odds_series) < 2:
            return {'trend': 'neutral', 'strength': 0}

        momentum = (odds_series[-1] - odds_series[0]) / odds_series[0]
        trend = 'up' if momentum > 0 else 'down'
        return {'trend': trend, 'strength': abs(momentum)}

    def _analyze_market_efficiency(self, match_data: pd.DataFrame) -> Dict[str, Any]:
        spreads = match_data[['Home_Odds', 'Away_Odds']].agg(['max', 'min'])
        home_spread = spreads.loc['max', 'Home_Odds'] - spreads.loc['min', 'Home_Odds']
        away_spread = spreads.loc['max', 'Away_Odds'] - spreads.loc['min', 'Away_Odds']
        efficiency = 1 - (home_spread + away_spread) / 2
        return {'efficiency_score': efficiency, 'is_efficient': efficiency > self.efficiency_threshold}

    def _find_value_opportunities(self, match_data: pd.DataFrame) -> List[Dict[str, Any]]:
        opportunities = []
        for _, row in match_data.iterrows():
            for side in ['Home_Odds', 'Away_Odds']:
                ev = self._calculate_ev(row[side], side)
                if ev > self.value_threshold:
                    opportunities.append({'type': side, 'odds': row[side], 'ev': ev})
        return sorted(opportunities, key=lambda x: x['ev'], reverse=True)

    def _calculate_ev(self, odds: float, side: str) -> float:
        true_prob = 0.55 if side == 'Home_Odds' else 0.45
        return (true_prob * odds - 1) * 100

    def _assess_risk(self, match_data: pd.DataFrame) -> Dict[str, Any]:
        volatility = match_data['Home_Odds'].std()
        liquidity = len(match_data)
        risk_score = (volatility * 0.6) + ((1 / liquidity) * 0.4)
        return {'risk_score': risk_score, 'risk_level': 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.3 else 'low'}

    def _load_model(self) -> RandomForestClassifier:
        if os.path.exists(self.model_file):
            return joblib.load(self.model_file)
        return RandomForestClassifier(n_estimators=100, max_depth=10)

    def _load_scaler(self) -> StandardScaler:
        if os.path.exists(self.scaler_file):
            return joblib.load(self.scaler_file)
        return StandardScaler()

    def _extract_features(self, match_data: pd.DataFrame) -> Optional[List[float]]:
        try:
            odds_value = match_data['Home_Odds'].iloc[-1]
            efficiency = self._analyze_market_efficiency(match_data)['efficiency_score']
            volatility = match_data['Home_Odds'].std()
            momentum = self._analyze_momentum(match_data)['strength']
            value_ratio = (1 / odds_value) - 1
            return [odds_value, efficiency, volatility, momentum, value_ratio]
        except Exception as e:
            logger.error(f"Erro ao extrair features: {e}")
            return None
