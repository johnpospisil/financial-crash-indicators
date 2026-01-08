# Recession Dashboard - Deployment Guide

This guide covers deploying the Recession Dashboard to various platforms.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Heroku Deployment](#heroku-deployment)
4. [Render Deployment](#render-deployment)
5. [VPS Deployment (Ubuntu/Debian)](#vps-deployment)
6. [Environment Variables](#environment-variables)
7. [SSL Certificates](#ssl-certificates)
8. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Required

- FRED API Key (get from https://fred.stlouisfed.org/docs/api/api_key.html)
- Python 3.12+
- Git

### Optional (for email notifications)

- SMTP server credentials (Gmail, Outlook, SendGrid, etc.)

---

## Docker Deployment

### Local Development with Docker

1. **Build the image:**

   ```bash
   docker build -t recession-dashboard .
   ```

2. **Run with docker-compose:**

   ```bash
   # Create .env file first
   cp .env.example .env
   # Edit .env with your FRED_API_KEY

   # Start all services
   docker-compose up -d
   ```

3. **Access the dashboard:**

   - Dashboard: http://localhost:8050
   - Nginx (if enabled): http://localhost

4. **View logs:**

   ```bash
   docker-compose logs -f dashboard
   ```

5. **Stop services:**
   ```bash
   docker-compose down
   ```

### Production Docker Deployment

1. **Build for production:**

   ```bash
   docker build -t recession-dashboard:latest .
   ```

2. **Run with environment variables:**

   ```bash
   docker run -d \
     --name recession-dashboard \
     -p 8050:8050 \
     -e FRED_API_KEY=your_key_here \
     -v $(pwd)/data/cache:/app/data/cache \
     -v $(pwd)/logs:/app/logs \
     --restart unless-stopped \
     recession-dashboard:latest
   ```

3. **With docker-compose (recommended):**
   - Edit `docker-compose.yml` environment variables
   - Enable nginx service for SSL/reverse proxy
   - Enable data-updater for automated updates
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

---

## Heroku Deployment

### Setup

1. **Install Heroku CLI:**

   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku

   # Other platforms: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku:**

   ```bash
   heroku login
   ```

3. **Create Heroku app:**

   ```bash
   heroku create your-dashboard-name
   ```

4. **Set environment variables:**

   ```bash
   heroku config:set FRED_API_KEY=your_key_here

   # Optional: email notifications
   heroku config:set SMTP_SERVER=smtp.gmail.com
   heroku config:set SMTP_PORT=587
   heroku config:set SMTP_USERNAME=your_email@gmail.com
   heroku config:set SMTP_PASSWORD=your_app_password
   heroku config:set NOTIFICATION_EMAIL=recipient@example.com
   ```

5. **Deploy:**

   ```bash
   git push heroku main
   ```

6. **Open the app:**
   ```bash
   heroku open
   ```

### Monitoring

```bash
# View logs
heroku logs --tail

# Check dyno status
heroku ps

# Restart app
heroku restart
```

### Scheduled Data Updates (Heroku Scheduler)

1. **Install scheduler add-on:**

   ```bash
   heroku addons:create scheduler:standard
   ```

2. **Open scheduler dashboard:**

   ```bash
   heroku addons:open scheduler
   ```

3. **Add job:**
   - Frequency: Daily (or as preferred)
   - Command: `python scripts/update_data.py --notify`

---

## Render Deployment

### Automatic Deployment

1. **Push code to GitHub:**

   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Connect to Render:**

   - Go to https://render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml` and configure automatically

3. **Set environment variables:**

   - In Render dashboard, go to your service
   - Navigate to "Environment" tab
   - Add: `FRED_API_KEY` (required)
   - Add: `SMTP_*` variables (optional)

4. **Deploy:**
   - Render auto-deploys on git push to main branch
   - Manual deploy: Click "Manual Deploy" in dashboard

### Manual Deployment

1. **Create Web Service:**

   - Go to Render dashboard
   - Click "New +" → "Web Service"
   - Connect repository
   - Settings:
     - **Name:** recession-dashboard
     - **Environment:** Python 3
     - **Build Command:** `pip install -r web_app/requirements.txt`
     - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 4 web_app.app:server`

2. **Set environment variables** (same as above)

3. **Deploy**

---

## VPS Deployment

Deploy to any VPS (DigitalOcean, Linode, AWS EC2, etc.) running Ubuntu/Debian.

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.12 python3.12-venv python3-pip nginx certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash dashboarduser
sudo usermod -aG www-data dashboarduser
```

### 2. Install Application

```bash
# Clone repository
sudo mkdir -p /opt/recession-dashboard
sudo chown dashboarduser:www-data /opt/recession-dashboard
sudo -u dashboarduser git clone https://github.com/yourusername/recession-dashboard.git /opt/recession-dashboard

# Setup Python environment
cd /opt/recession-dashboard
sudo -u dashboarduser python3.12 -m venv venv
sudo -u dashboarduser venv/bin/pip install -r web_app/requirements.txt
```

### 3. Configure Environment

```bash
# Create .env file
sudo -u dashboarduser nano /opt/recession-dashboard/.env
```

Add:

```
FRED_API_KEY=your_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=recipient@example.com
```

### 4. Setup Systemd Service

```bash
# Copy service file
sudo cp deployment/systemd_service.conf /etc/systemd/system/recession-dashboard.service

# Edit service file
sudo nano /etc/systemd/system/recession-dashboard.service
# Update FRED_API_KEY and paths if needed

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable recession-dashboard
sudo systemctl start recession-dashboard

# Check status
sudo systemctl status recession-dashboard
```

### 5. Configure Nginx

```bash
# Copy nginx configuration
sudo cp deployment/nginx.conf /etc/nginx/sites-available/recession-dashboard

# Edit configuration
sudo nano /etc/nginx/sites-available/recession-dashboard
# Update server_name with your domain

# Enable site
sudo ln -s /etc/nginx/sites-available/recession-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Setup SSL with Let's Encrypt

```bash
# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test renewal
sudo certbot renew --dry-run
```

### 7. Setup Automated Data Updates

```bash
# Copy cron script
sudo cp scripts/daily_update.sh /opt/recession-dashboard/
sudo chmod +x /opt/recession-dashboard/daily_update.sh

# Add to cron
sudo -u dashboarduser crontab -e
```

Add:

```
# Update data daily at 6 AM
0 6 * * * /opt/recession-dashboard/daily_update.sh
```

### 8. Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

---

## Environment Variables

### Required

| Variable       | Description       | Example     |
| -------------- | ----------------- | ----------- |
| `FRED_API_KEY` | Your FRED API key | `abc123...` |

### Optional (Email Notifications)

| Variable             | Description                 | Example              |
| -------------------- | --------------------------- | -------------------- |
| `SMTP_SERVER`        | SMTP server address         | `smtp.gmail.com`     |
| `SMTP_PORT`          | SMTP port                   | `587`                |
| `SMTP_USERNAME`      | Email username              | `you@gmail.com`      |
| `SMTP_PASSWORD`      | Email password/app password | `your_password`      |
| `NOTIFICATION_EMAIL` | Recipient email             | `alerts@example.com` |

### Platform-Specific

| Variable         | Description            | Used By        |
| ---------------- | ---------------------- | -------------- |
| `PORT`           | Server port (auto-set) | Heroku, Render |
| `PYTHON_VERSION` | Python version         | Render         |
| `DEBUG`          | Enable debug mode      | Development    |

---

## SSL Certificates

### Let's Encrypt (Free, Recommended)

**For VPS:**

```bash
sudo certbot --nginx -d your-domain.com
```

**For Docker:**
Use a reverse proxy like Traefik or nginx-proxy-companion that handles Let's Encrypt automatically.

### Manual SSL

If you have existing certificates:

1. **Copy certificates:**

   ```bash
   sudo cp fullchain.pem /etc/ssl/certs/
   sudo cp privkey.pem /etc/ssl/private/
   ```

2. **Update nginx.conf:**
   ```nginx
   ssl_certificate /etc/ssl/certs/fullchain.pem;
   ssl_certificate_key /etc/ssl/private/privkey.pem;
   ```

---

## Monitoring & Maintenance

### Health Checks

**Dashboard Health:**

```bash
curl http://localhost:8050/
```

**Gunicorn Status:**

```bash
# VPS
sudo systemctl status recession-dashboard

# Docker
docker-compose ps
```

### Logs

**VPS:**

```bash
# Application logs
sudo journalctl -u recession-dashboard -f

# Nginx logs
sudo tail -f /var/log/nginx/dashboard_access.log
sudo tail -f /var/log/nginx/dashboard_error.log

# Data update logs
tail -f /opt/recession-dashboard/logs/data_update_*.log
```

**Docker:**

```bash
docker-compose logs -f dashboard
docker-compose logs -f nginx
docker-compose logs -f data-updater
```

**Heroku:**

```bash
heroku logs --tail
```

**Render:**

- View logs in Render dashboard

### Updating the Application

**VPS:**

```bash
cd /opt/recession-dashboard
sudo -u dashboarduser git pull
sudo -u dashboarduser venv/bin/pip install -r web_app/requirements.txt
sudo systemctl restart recession-dashboard
```

**Docker:**

```bash
docker-compose down
git pull
docker-compose build
docker-compose up -d
```

**Heroku/Render:**

```bash
git push origin main
# Auto-deploys on push
```

### Backup

**Important directories to backup:**

- `data/cache/` - Cached FRED data
- `logs/` - Application and update logs
- `.env` - Environment variables (secure storage)

**Backup script example:**

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup_$DATE.tar.gz data/cache/ logs/ .env
```

### Performance Tuning

**Gunicorn workers:**

```bash
# Formula: (2 × CPU cores) + 1
# Adjust in docker-compose.yml, Procfile, or gunicorn_config.py
```

**Nginx caching:**

- Already configured in `deployment/nginx.conf`
- Static assets cached for 30 days

**Database (if using):**

- Not currently used
- Could add PostgreSQL for persistent storage

---

## Troubleshooting

### Dashboard won't start

1. **Check logs:**

   ```bash
   # VPS
   sudo journalctl -u recession-dashboard -n 50

   # Docker
   docker-compose logs dashboard
   ```

2. **Verify FRED API key:**

   ```bash
   curl "https://api.stlouisfed.org/fred/series?series_id=GDP&api_key=YOUR_KEY&file_type=json"
   ```

3. **Test locally:**
   ```bash
   source venv/bin/activate
   python web_app/app.py
   ```

### Nginx errors

```bash
# Check configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### SSL certificate issues

```bash
# Renew certificates
sudo certbot renew

# Check expiration
sudo certbot certificates
```

### Out of memory

1. **Reduce Gunicorn workers:**

   - Edit `docker-compose.yml` or `gunicorn_config.py`
   - Change from 4 workers to 2

2. **Upgrade server:**
   - Minimum: 512MB RAM
   - Recommended: 1GB+ RAM

---

## Support

For issues or questions:

- Check logs first (see Monitoring section)
- Review FRED API status: https://fred.stlouisfed.org/
- Consult platform documentation:
  - Docker: https://docs.docker.com/
  - Heroku: https://devcenter.heroku.com/
  - Render: https://render.com/docs/
  - Nginx: https://nginx.org/en/docs/
