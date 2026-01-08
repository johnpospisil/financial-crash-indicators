# Procfile for Heroku deployment
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 web_app.app:server
