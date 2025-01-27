from flask import Flask, render_template, jsonify
from datetime import datetime
import os
from odds_collector import OddsCollector

app = Flask(__name__)

# Configurações ajustadas para a estratégia Holzhauer
app.config.update(
    PORT=int(os.environ.get('PORT', 10000)),
    HOST=os.environ.get('HOST', '0.0.0.0'),
    ENVIRONMENT=os.environ.get('ENVIRONMENT', 'production'),
    UPDATE_INTERVAL=int(os.environ.get('UPDATE_INTERVAL', 15)),  # Mais rápido
    CONFIDENCE_THRESHOLD=float(os.environ.get('CONFIDENCE_THRESHOLD', 80)),  # Mais rigoroso
    VALUE_THRESHOLD=float(os.environ.get('VALUE_THRESHOLD', 3))  # Mais sensível
)

# Inicializa o coletor de odds
odds_collector = OddsCollector(update_interval=app.config['UPDATE_INTERVAL'])
odds_collector.start()

@app.route('/')
def index():
    """Página principal com análise Holzhauer"""
    games = odds_collector.get_live_games()
    opportunities = odds_collector.get_opportunities(
        confidence_threshold=app.config['CONFIDENCE_THRESHOLD'],
        value_threshold=app.config['VALUE_THRESHOLD']
    )
    return render_template('index.html', games=games, opportunities=opportunities)

# ... (manter as outras rotas existentes)
