from flask import Flask, render_template, jsonify
from datetime import datetime
import os
from odds_collector import OddsCollector

app = Flask(__name__)

# Configurações
app.config.update(
    PORT=int(os.environ.get('PORT', 10000)),
    HOST=os.environ.get('HOST', '0.0.0.0'),
    ENVIRONMENT=os.environ.get('ENVIRONMENT', 'production'),
    UPDATE_INTERVAL=int(os.environ.get('UPDATE_INTERVAL', 30)),
    CONFIDENCE_THRESHOLD=float(os.environ.get('CONFIDENCE_THRESHOLD', 75)),
    VALUE_THRESHOLD=float(os.environ.get('VALUE_THRESHOLD', 5))
)

# Inicializa o coletor de odds
odds_collector = OddsCollector(update_interval=app.config['UPDATE_INTERVAL'])
odds_collector.start()

@app.route('/')
def index():
    """Página principal"""
    games = odds_collector.get_live_games()
    opportunities = odds_collector.get_opportunities(
        confidence_threshold=app.config['CONFIDENCE_THRESHOLD'],
        value_threshold=app.config['VALUE_THRESHOLD']
    )
    return render_template('index.html', games=games, opportunities=opportunities)

@app.route('/api/games')
def get_games():
    """API endpoint para jogos ao vivo"""
    games = odds_collector.get_live_games()
    return jsonify({
        'status': 'success',
        'games': games,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/opportunities')
def get_opportunities():
    """API endpoint para oportunidades de apostas"""
    opportunities = odds_collector.get_opportunities(
        confidence_threshold=app.config['CONFIDENCE_THRESHOLD'],
        value_threshold=app.config['VALUE_THRESHOLD']
    )
    return jsonify({
        'status': 'success',
        'opportunities': opportunities,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT']
    )
