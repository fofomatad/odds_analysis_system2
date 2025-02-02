from flask import Flask, render_template, jsonify, request, send_from_directory
import pandas as pd
from config import ODDS_FILE, OPPORTUNITIES_FILE
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
from odds_history import OddsHistory
from alerts import AlertSystem
from player_stats import PlayerStatsAnalyzer
from player_behavior_tracker import PlayerBehaviorTracker
import config
import logging
import os
from datetime import datetime
import threading
from odds_collector import OddsCollector
from monitoring import SystemMonitor
from holzhauer_strategy import HolzhauerStrategy
from nba_analyzer import NBAAnalyzer
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Configuração do Sentry para monitoramento de erros
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FlaskIntegration()],
    environment=os.getenv("ENVIRONMENT", "production"),
    traces_sample_rate=1.0
)

# Configuração de logging
logging.basicConfig(
    filename=os.path.join(config.LOGS_DIR, 'app.log'),
    level=logging.INFO,
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Inicializa o app Flask
app = Flask(__name__, static_folder='static')

# Configuração do CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuração do Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "30 per hour"]
)

# Configuração do Cache simples
cache_config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}
cache = Cache(app, config=cache_config)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///odds.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Inicialização dos sistemas
odds_collector = OddsCollector()
history_manager = OddsHistory()
alert_system = AlertSystem()
stats_analyzer = PlayerStatsAnalyzer()
behavior_tracker = PlayerBehaviorTracker()
system_monitor = SystemMonitor()
holzhauer = HolzhauerStrategy()
nba_analyzer = NBAAnalyzer()

# Inicia a coleta de odds
odds_collector.start_collection()

# Configuração para servir arquivos estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/')
@limiter.limit("60 per minute")
@cache.cached(timeout=30)
def index():
    try:
        games = [{'home': 'Lakers', 'away': 'Warriors'}, ...]  # Exemplo de estrutura de dados sem imagens
        logger.info(f"Games data: {games}")
        opportunities = holzhauer.get_opportunities()
        return render_template('index.html', 
                             games=games,
                             opportunities=opportunities,
                             last_update=odds_collector.last_update)
    except Exception as e:
        logger.error(f"Erro na página inicial: {e}")
        return render_template('index.html', 
                             games=[],
                             opportunities=[],
                             error="Erro ao carregar dados")

@app.route('/players')
def player_dashboard():
    """Dashboard de análise de jogadores"""
    return render_template('behavior_tracker.html')

@app.route('/register_observation', methods=['POST'])
def register_observation():
    """Registra uma nova observação de comportamento"""
    try:
        data = request.json
        observation = behavior_tracker.register_observation(
            player_name=data['player'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            observation_type=data['type'],
            details=data.get('details', '')
        )
        return jsonify({'success': True, 'observation': observation})
    except Exception as e:
        logger.error(f"Erro ao registrar observação: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/register_interaction', methods=['POST'])
def register_interaction():
    """Registra uma interação entre jogadores"""
    try:
        data = request.json
        interaction = behavior_tracker.register_interaction(
            player1=data['player1'],
            player2=data['player2'],
            interaction_type=data['type'],
            details=data.get('details', '')
        )
        return jsonify({'success': True, 'interaction': interaction})
    except Exception as e:
        logger.error(f"Erro ao registrar interação: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/get_emotional_states')
def get_emotional_states():
    """Retorna estados emocionais atuais dos jogadores"""
    try:
        states = {}
        for player in request.args.getlist('players[]'):
            states[player] = behavior_tracker.get_player_emotional_state(player)
        return jsonify(states)
    except Exception as e:
        logger.error(f"Erro ao obter estados emocionais: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/get_sequence_analysis')
def get_sequence_analysis():
    """Retorna análise de sequências para jogadores"""
    try:
        analysis = {}
        for player in request.args.getlist('players[]'):
            analysis[player] = behavior_tracker.analyze_sequence_patterns(player)
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Erro ao obter análise de sequências: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/get_correlation_analysis')
def get_correlation_analysis():
    """Retorna análise de correlações para jogadores"""
    try:
        analysis = {}
        for player in request.args.getlist('players[]'):
            analysis[player] = behavior_tracker.analyze_event_correlations(player)
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Erro ao obter análise de correlações: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/get_behavior_history')
def get_behavior_history():
    """Retorna histórico de observações"""
    try:
        player = request.args.get('player')
        time_window = int(request.args.get('time_window', 30))  # minutos
        observations = behavior_tracker._get_recent_observations(player, time_window)
        return jsonify(observations)
    except Exception as e:
        logger.error(f"Erro ao obter histórico de comportamento: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/get_opportunities')
@limiter.limit("60 per minute")
@cache.cached(timeout=30)
def get_opportunities():
    try:
        odds_data = odds_collector.get_current_odds()
        if not odds_data.empty:
            opportunities = holzhauer.analyze_opportunities(odds_data)
            return jsonify(opportunities)
        return jsonify([])
    except Exception as e:
        logger.error(f"Erro ao obter oportunidades: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_player_stats')
def get_player_stats():
    """Retorna estatísticas completas do jogador"""
    try:
        stats = {
            'total_bets': stats_analyzer.get_total_bets(),
            'win_rate': stats_analyzer.get_win_rate(),
            'current_streak': stats_analyzer.get_current_streak(),
            'emotional_state': behavior_tracker.get_current_emotional_state(),
            'behavior_history': behavior_tracker.get_recent_history()
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do jogador: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/get_live_games')
@limiter.limit("120 per minute")
@cache.cached(timeout=15)
def get_live_games():
    try:
        games = odds_collector.get_live_games()
        return jsonify({
            'games': games,
            'last_update': odds_collector.last_update.strftime('%H:%M:%S') if odds_collector.last_update else None
        })
    except Exception as e:
        logger.error(f"Erro ao obter jogos ao vivo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_upcoming_games')
def get_upcoming_games():
    """Retorna próximos jogos com previsões"""
    try:
        # Aqui você implementaria a conexão com uma API de calendário NBA
        # Por enquanto, retornando dados de exemplo
        games = [
            {
                'id': '2',
                'home_team': 'Celtics',
                'away_team': 'Nets',
                'date': '2024-01-24',
                'time': '19:30',
                'predictions': [
                    {
                        'player': 'Jayson Tatum',
                        'type': 'Pontos',
                        'prediction': 'Over 28.5',
                        'confidence': 85,
                        'confidence_class': 'confidence-high'
                    },
                    {
                        'player': 'Kevin Durant',
                        'type': 'Rebotes',
                        'prediction': 'Over 7.5',
                        'confidence': 75,
                        'confidence_class': 'confidence-medium'
                    }
                ]
            }
        ]
        return jsonify(games)
    except Exception as e:
        logger.error(f"Erro ao obter próximos jogos: {e}")
        return jsonify([])

@app.route('/analysis/<game_id>')
def game_analysis(game_id):
    """Página de análise detalhada do jogo ao vivo"""
    return render_template('game_analysis.html', game_id=game_id)

@app.route('/pregame/<game_id>')
def pregame_analysis(game_id):
    """Página de análise pré-jogo"""
    return render_template('pregame_analysis.html', game_id=game_id)

@app.route('/get_game_data/<game_id>')
def get_game_data(game_id):
    """Retorna dados atualizados do jogo"""
    try:
        # Aqui você implementaria a conexão com uma API de jogos ao vivo
        # Por enquanto, retornando dados de exemplo
        data = {
            'home_team': 'Lakers',
            'away_team': 'Warriors',
            'home_score': 89,
            'away_score': 85,
            'quarter': 3,
            'time': '4:35',
            'momentum': 65  # Porcentagem do momento do jogo (0-100)
        }
        return jsonify(data)
    except Exception as e:
        logger.error(f"Erro ao obter dados do jogo: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/get_player_analysis/<game_id>')
def get_player_analysis(game_id):
    """Retorna análise detalhada dos jogadores"""
    try:
        # Obter dados do jogo
        game_data = odds_collector.get_game_data(game_id)
        player_stats = {}  # Implementar coleta de estatísticas
        team_stats = {}    # Implementar coleta de estatísticas
        
        # Análise Holzhauer
        analysis = []
        for player in game_data.get('players', []):
            quarter_stats = {}
            for quarter in range(1, 5):
                stats = holzhauer.analyze_quarter_stats(
                    player_name=player['name'],
                    quarter=quarter,
                    game_situation=game_data
                )
                quarter_stats[quarter] = {
                    'average': stats['average'],
                    'confidence': stats['confidence'],
                    'trend': stats['trend']
                }
            
            analysis.append({
                'name': player['name'],
                'quarter_stats': quarter_stats
            })
            
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Erro ao obter análise dos jogadores: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_game_predictions/<game_id>')
def get_game_predictions(game_id):
    """Retorna previsões para o jogo atual"""
    try:
        # Aqui você implementaria as previsões reais usando a estratégia Holzhauer
        # Por enquanto, retornando dados de exemplo
        predictions = [
            {
                'player': 'LeBron James',
                'type': 'Pontos',
                'prediction': 'Over 32.5',
                'confidence': 85
            },
            {
                'player': 'Stephen Curry',
                'type': 'Assistências',
                'prediction': 'Over 8.5',
                'confidence': 75
            }
        ]
        return jsonify(predictions)
    except Exception as e:
        logger.error(f"Erro ao obter previsões: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/update_charts')
def update_charts():
    """Atualiza os gráficos do dashboard"""
    try:
        odds_data = odds_collector.get_current_odds()
        
        # Criar gráfico de comparação de odds
        odds_chart_data = {
            'data': [
                {
                    'x': odds_data['Bookmaker'].tolist(),
                    'y': odds_data['Home_Odds'].tolist(),
                    'type': 'bar',
                    'name': 'Odds Casa'
                },
                {
                    'x': odds_data['Bookmaker'].tolist(),
                    'y': odds_data['Away_Odds'].tolist(),
                    'type': 'bar',
                    'name': 'Odds Fora'
                }
            ],
            'layout': {
                'title': 'Comparação de Odds por Casa de Apostas',
                'xaxis': {'title': 'Casa de Apostas'},
                'yaxis': {'title': 'Odds'},
                'barmode': 'group'
            }
        }

        return jsonify({
            'odds_chart': odds_chart_data,
            'last_update': datetime.now().strftime('%H:%M:%S')
        })

    except Exception as e:
        logger.error(f"Erro ao atualizar gráficos: {str(e)}")
        return jsonify({
            'error': 'Erro ao atualizar gráficos',
            'details': str(e)
        }), 500

@app.route('/get_trends')
def get_trends():
    try:
        odds_df, _ = load_data()
        trends = {
            'increasing': [],
            'decreasing': [],
            'volatile': []
        }
        
        for match in odds_df['Match'].unique():
            analysis = history_manager.get_trend_analysis(match)
            if not analysis:
                continue
            
            trend_data = {
                'Match': analysis['match'],
                'Side': odds_df[odds_df['Match'] == match]['Side'].iloc[0],
                'Current_Odds': analysis['current_odds']
            }
            
            if analysis['is_volatile']:
                trends['volatile'].append(trend_data)
            elif analysis['variation_percent'] > 5:
                trends['increasing'].append(trend_data)
            elif analysis['variation_percent'] < -5:
                trends['decreasing'].append(trend_data)
        
        return jsonify(trends)
        
    except Exception as e:
        logger.error(f"Erro ao obter tendências: {str(e)}")
        return jsonify({
            'error': 'Erro ao obter tendências',
            'details': str(e)
        }), 500

@app.route('/system/health')
def system_health():
    """Retorna status do sistema"""
    try:
        health = system_monitor.get_system_health()
        return jsonify(health)
    except Exception as e:
        logger.error(f"Erro ao obter saúde do sistema: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/system/stats')
def system_stats():
    """Retorna estatísticas do sistema"""
    try:
        hours = request.args.get('hours', default=24, type=int)
        stats = system_monitor.get_historical_stats(hours)
        return jsonify(stats.to_dict('records'))
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_opportunity/<match_id>')
def analyze_opportunity(match_id):
    """Analisa oportunidade usando estratégia Holzhauer"""
    try:
        odds_data = odds_collector.get_current_odds()
        match_data = odds_data[odds_data['Match'] == match_id]
        
        if match_data.empty:
            return jsonify({'error': 'Partida não encontrada'}), 404
            
        analysis = holzhauer.analyze_opportunity(match_data)
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Erro ao analisar oportunidade: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/nba/analyze/<game_id>')
def analyze_nba_game(game_id):
    """Analisa jogo NBA usando estratégia Holzhauer"""
    try:
        # Obter dados do jogo
        game_data = odds_collector.get_game_data(game_id)
        player_stats = {}  # Implementar coleta de estatísticas
        team_stats = {}    # Implementar coleta de estatísticas
        
        # Análise Holzhauer
        analysis = nba_analyzer.analyze_game(game_data, player_stats, team_stats)
        
        if not analysis:
            return jsonify({'error': 'Não foi possível analisar o jogo'}), 400
            
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Erro ao analisar jogo NBA: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/nba/games')
def get_nba_games():
    """Retorna jogos NBA disponíveis"""
    try:
        games = [
            {
                'id': '1',
                'home_team': 'Lakers',
                'away_team': 'Warriors',
                'start_time': '19:30'
            },
            {
                'id': '2',
                'home_team': 'Celtics',
                'away_team': 'Nets',
                'start_time': '20:00'
            }
        ]
        logger.info(f"Jogos NBA coletados: {games}")
        return jsonify(games)
    except Exception as e:
        logger.error(f"Erro ao obter jogos NBA: {e}")
        return jsonify([])

@app.route('/nba/dashboard')
def nba_dashboard():
    """Renderiza dashboard NBA"""
    return render_template('nba_dashboard.html')

@app.route('/register_emotion', methods=['POST'])
def register_emotion():
    """Registra uma emoção do jogador"""
    try:
        data = request.json
        emotion = data.get('emotion')
        behavior_tracker.register_emotion(emotion)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erro ao registrar emoção: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/trigger_alert', methods=['POST'])
def trigger_alert():
    """Dispara um alerta de risco"""
    try:
        data = request.json
        alert_type = data.get('type')
        alert_system.trigger_alert(alert_type)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erro ao disparar alerta: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/add_note', methods=['POST'])
def add_note():
    """Adiciona uma nota de observação"""
    try:
        data = request.json
        note = data.get('note')
        behavior_tracker.add_note(note)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erro ao adicionar nota: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/holzhauer')
@limiter.limit("60 per minute")
def holzhauer_analysis():
    analysis = holzhauer.get_current_analysis()
    trends = behavior_tracker.get_trends()
    return render_template('holzhauer.html', 
                         analysis=analysis, 
                         trends=trends)

@app.route('/get_quarter_analysis/<game_id>')
def get_quarter_analysis(game_id):
    """Retorna análise por quarter dos jogadores"""
    try:
        # Obtém dados do jogo
        game_data = odds_collector.get_game_data(game_id)
        
        # Análise por quarter usando estratégia Holzhauer
        analysis = []
        for player in game_data.get('players', []):
            quarter_stats = {}
            for quarter in range(1, 5):
                stats = holzhauer.analyze_quarter_stats(
                    player_name=player['name'],
                    quarter=quarter,
                    game_situation=game_data
                )
                quarter_stats[quarter] = {
                    'average': stats['average'],
                    'confidence': stats['confidence'],
                    'trend': stats['trend']
                }
            
            analysis.append({
                'name': player['name'],
                'quarter_stats': quarter_stats
            })
            
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Erro ao obter análise por quarter: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_value_props/<game_id>')
def get_value_props(game_id):
    """Retorna props com valor usando estratégia Holzhauer"""
    try:
        # Obtém dados do jogo
        game_data = odds_collector.get_game_data(game_id)
        
        # Análise de props usando estratégia Holzhauer
        props = []
        for player in game_data.get('players', []):
            player_props = holzhauer.analyze_player_props(
                player_name=player['name'],
                game_situation=game_data
            )
            
            for prop in player_props:
                if prop['value_rating'] >= 5:  # Apenas props com valor significativo
                    props.append({
                        'player': player['name'],
                        'type': prop['type'],
                        'line': prop['line'],
                        'prediction': prop['prediction'],
                        'confidence': prop['confidence'],
                        'value_rating': prop['value_rating'],
                        'analysis': prop['analysis']
                    })
        
        # Ordena por value_rating
        props.sort(key=lambda x: x['value_rating'], reverse=True)
        return jsonify(props)
        
    except Exception as e:
        logger.error(f"Erro ao obter props com valor: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Recurso não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno do servidor: {error}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

def start_alert_system():
    """Inicia o sistema de alertas em uma thread separada"""
    alert_system.run()

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'odds_collector': odds_collector.is_healthy(),
            'holzhauer': holzhauer.is_healthy(),
            'player_tracker': behavior_tracker.is_healthy()
        }
    })

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    
    # Iniciar sistema de alertas em background
    alert_thread = threading.Thread(target=start_alert_system)
    alert_thread.daemon = True  # Thread será finalizada quando o programa principal terminar
    alert_thread.start()
    
    # Iniciar monitoramento do sistema
    system_monitor.start()
    
    # Iniciar servidor
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 
    from odds_collector import OddsCollector
from nba_analyzer import NBAAnalyzer
@app.route('/live_odds')
def live_odds():
    collector = OddsCollector()
    return collector.get_live_odds()

@app.route('/upcoming_games')
def upcoming_games():
    analyzer = NBAAnalyzer()
    return analyzer.get_upcoming_games()