import os

# Configurações do Gunicorn para o Render
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 1  # Número reduzido de workers para o plano gratuito
worker_class = 'sync'
worker_connections = 50
timeout = 120
keepalive = 2

# Configurações de logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
