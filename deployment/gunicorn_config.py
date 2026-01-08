# Gunicorn configuration for production deployment
# Can be used with: gunicorn -c deployment/gunicorn_config.py web_app.app:server

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8050')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'  # Use 'gevent' or 'eventlet' for async if needed
worker_connections = 1000
threads = int(os.getenv('GUNICORN_THREADS', 2))
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50  # Add randomness to max_requests
timeout = 120  # Worker timeout in seconds
keepalive = 5  # Seconds to wait for requests on a Keep-Alive connection

# Process naming
proc_name = 'recession_dashboard'

# Logging
accesslog = '-'  # stdout
errorlog = '-'  # stderr
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
daemon = False  # Don't run in background (let systemd/docker handle it)
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Debugging
reload = os.getenv('DEBUG', 'False').lower() == 'true'
reload_extra_files = []

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Recession Dashboard")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading Recession Dashboard")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Recession Dashboard is ready. Workers: %s", workers)

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")

def worker_int(worker):
    """Called when a worker received INT or QUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker received SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")
