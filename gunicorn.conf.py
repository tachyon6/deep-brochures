# Gunicorn configuration file for production

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 1  # EC2 t3.micro에서는 1개 워커 권장
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "media_kit_api"

# Worker tmp directory
worker_tmp_dir = "/dev/shm"

# Preload app for memory efficiency
preload_app = True 