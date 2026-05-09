# Configuración de Gunicorn para Producción

# Numero de worker processes
workers = 4

# Tipo de worker
worker_class = 'sync'

# Bind address
bind = '0.0.0.0:8000'

# Timeout
timeout = 30

# Access log
accesslog = '/var/log/gunicorn/access.log'

# Error log
errorlog = '/var/log/gunicorn/error.log'

# Log level
loglevel = 'info'

# Graceful timeout
graceful_timeout = 30

# Keep alive
keepalive = 2
