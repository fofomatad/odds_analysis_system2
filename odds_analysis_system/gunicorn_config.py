# Configuração básica para plano free
workers = 2
threads = 2
worker_class = 'sync'

# Timeouts
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Bind
bind = '0.0.0.0:10000'

# Limites para plano free
max_requests = 500
max_requests_jitter = 50