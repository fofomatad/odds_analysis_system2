import pandas as pd
import time
from datetime import datetime
import os
from config import OPPORTUNITIES_FILE, ALERT_THRESHOLDS, DATA_DIR
import logging
import numpy as np
import requests
import threading
from queue import Queue

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self):
        self.high_ev_threshold = 5.0  # Alerta para EV% acima de 5%
        self.last_check = None
        self.notified_opportunities = set()
        self.alert_queue = Queue()
        self.is_running = False
        self.alert_thread = None
        self.last_alerts = {}  # Evita alertas duplicados
        self.alert_cooldown = 300  # 5 minutos entre alertas similares
        
    def start(self):
        """Inicia o sistema de alertas em uma thread separada"""
        if not self.is_running:
            self.is_running = True
            self.alert_thread = threading.Thread(target=self._alert_loop)
            self.alert_thread.daemon = True
            self.alert_thread.start()
            logger.info("Sistema de alertas iniciado")
    
    def stop(self):
        """Para o sistema de alertas"""
        self.is_running = False
        if self.alert_thread:
            self.alert_thread.join()
            logger.info("Sistema de alertas parado")
    
    def _alert_loop(self):
        """Loop principal de processamento de alertas"""
        while self.is_running:
            try:
                if not self.alert_queue.empty():
                    alert = self.alert_queue.get()
                    self._process_alert(alert)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Erro no loop de alertas: {e}")
                time.sleep(5)
    
    def _process_alert(self, alert):
        """Processa e envia um alerta"""
        try:
            alert_key = f"{alert['type']}_{alert['message']}"
            current_time = datetime.now()
            
            # Verifica se já enviou alerta similar recentemente
            if alert_key in self.last_alerts:
                time_diff = (current_time - self.last_alerts[alert_key]).total_seconds()
                if time_diff < self.alert_cooldown:
                    return
            
            # Envia alerta
            self._send_alert(alert)
            self.last_alerts[alert_key] = current_time
            
        except Exception as e:
            logger.error(f"Erro ao processar alerta: {e}")
    
    def _send_alert(self, alert):
        """Envia alerta (implementar conforme necessário)"""
        logger.info(f"ALERTA: {alert['type']} - {alert['message']}")
        print(f"\n{'='*50}")
        print(f"ALERTA: {alert['type']}")
        print(f"Mensagem: {alert['message']}")
        print(f"Timestamp: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*50}\n")
    
    def check_odds_movement(self, current_odds, previous_odds):
        """Verifica movimentações significativas nas odds"""
        try:
            for match in current_odds['Match'].unique():
                curr_match = current_odds[current_odds['Match'] == match]
                prev_match = previous_odds[previous_odds['Match'] == match] if not previous_odds.empty else pd.DataFrame()
                
                if prev_match.empty:
                    continue
                
                # Analisa variação percentual
                for side in ['Home', 'Away']:
                    curr_odds = curr_match[f'{side}_Odds'].mean()
                    prev_odds = prev_match[f'{side}_Odds'].mean()
                    
                    variation = ((curr_odds - prev_odds) / prev_odds) * 100
                    
                    if abs(variation) >= ALERT_THRESHOLDS['odds_movement']:
                        self.alert_queue.put({
                            'type': 'Movimento de Odds',
                            'match': match,
                            'message': f"Variação de {variation:.1f}% nas odds {side}"
                        })
                        
        except Exception as e:
            logger.error(f"Erro ao verificar movimentos de odds: {e}")
