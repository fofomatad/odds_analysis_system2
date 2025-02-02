import os
from pathlib import Path
import logging

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Files
ODDS_FILE = os.path.join(DATA_DIR, 'odds.csv')
OPPORTUNITIES_FILE = os.path.join(DATA_DIR, 'opportunities.csv')

# Server settings
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Collection settings
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 30))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5))

# Alert thresholds
ALERT_THRESHOLDS = {
    'odds_movement': float(os.getenv('ODDS_MOVEMENT_THRESHOLD', 5.0)),
    'volatility': float(os.getenv('VOLATILITY_THRESHOLD', 0.1)),
    'min_ev': float(os.getenv('MIN_EV_THRESHOLD', 5.0))
}

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = os.path.join(LOGS_DIR, 'app.log')

# Alert check interval
ALERT_CHECK_INTERVAL = int(os.getenv('ALERT_CHECK_INTERVAL', 60))
