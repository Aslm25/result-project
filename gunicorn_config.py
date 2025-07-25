# Gunicorn configuration for handling large Excel files
bind = "0.0.0.0:5000"
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5 minutes timeout for large file processing
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
reload = True