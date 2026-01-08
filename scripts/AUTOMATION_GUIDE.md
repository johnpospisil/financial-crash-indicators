# Data Update Automation Guide

## Overview

The Recession Dashboard includes a comprehensive data automation system that fetches the latest economic indicators from FRED, updates the cache, runs analysis, and sends notifications on completion or errors.

## Components

### 1. Update Script (`scripts/update_data.py`)

Main automation script with full logging and error handling.

**Features:**

- Fetches all 41+ economic indicators from FRED API
- Checks cache freshness before updating
- Runs recession risk analysis
- Generates detailed logs
- Sends email notifications
- Creates JSON summaries for monitoring

**Usage:**

```bash
# Basic update (respects cache)
python scripts/update_data.py

# Force refresh all data
python scripts/update_data.py --force

# Enable email notifications
python scripts/update_data.py --notify

# Verbose logging
python scripts/update_data.py --verbose

# Combined
python scripts/update_data.py --force --notify --verbose
```

### 2. Daily Update Script (`scripts/daily_update.sh`)

Bash wrapper for cron scheduling.

**Features:**

- Activates virtual environment
- Changes to project directory
- Runs update with notifications
- Logs execution status

**Usage:**

```bash
# Make executable
chmod +x scripts/daily_update.sh

# Run manually
./scripts/daily_update.sh

# Schedule with cron (see below)
```

## Scheduling Options

### Option 1: Cron (macOS/Linux)

**Setup:**

```bash
# Edit crontab
crontab -e

# Add one of these schedules:

# Daily at 6 AM
0 6 * * * cd /Users/johnpospisil/Documents/GitHub/projects/financial_crash_indicators && source ~/tf/bin/activate && python scripts/update_data.py --notify >> logs/cron.log 2>&1

# Weekdays at 9 AM
0 9 * * 1-5 cd /Users/johnpospisil/Documents/GitHub/projects/financial_crash_indicators && source ~/tf/bin/activate && python scripts/update_data.py --notify >> logs/cron.log 2>&1

# Multiple times daily (6 AM, 12 PM, 6 PM)
0 6,12,18 * * * cd /Users/johnpospisil/Documents/GitHub/projects/financial_crash_indicators && source ~/tf/bin/activate && python scripts/update_data.py >> logs/cron.log 2>&1
```

**View cron jobs:**

```bash
crontab -l
```

**Remove cron jobs:**

```bash
crontab -r
```

**Check cron logs (macOS):**

```bash
log show --predicate 'process == "cron"' --last 1h
```

### Option 2: Systemd Timer (Linux)

See `scripts/systemd_timer_config.txt` for detailed configuration.

**Quick setup:**

```bash
# Create service file
sudo nano /etc/systemd/system/recession-dashboard-update.service

# Create timer file
sudo nano /etc/systemd/system/recession-dashboard-update.timer

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable recession-dashboard-update.timer
sudo systemctl start recession-dashboard-update.timer

# Check status
systemctl status recession-dashboard-update.timer
```

### Option 3: Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Recession Dashboard Update"
4. Trigger: Daily at 6:00 AM
5. Action: Start a program
   - Program: `C:\path\to\python.exe`
   - Arguments: `scripts\update_data.py --notify`
   - Start in: `C:\path\to\financial_crash_indicators`

## Email Notifications

### Setup

1. **Get App Password (Gmail):**

   - Go to Google Account → Security → 2-Step Verification
   - Click "App passwords"
   - Generate password for "Mail"

2. **Set Environment Variables:**

   ```bash
   export SMTP_SERVER="smtp.gmail.com"
   export SMTP_PORT="587"
   export SENDER_EMAIL="your.email@gmail.com"
   export SENDER_PASSWORD="your-app-password"
   export RECIPIENT_EMAIL="recipient@email.com"
   ```

3. **Permanent Configuration:**

   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   echo 'export SMTP_SERVER="smtp.gmail.com"' >> ~/.bashrc
   echo 'export SMTP_PORT="587"' >> ~/.bashrc
   echo 'export SENDER_EMAIL="your.email@gmail.com"' >> ~/.bashrc
   echo 'export SENDER_PASSWORD="your-app-password"' >> ~/.bashrc
   echo 'export RECIPIENT_EMAIL="recipient@email.com"' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Test:**
   ```bash
   python scripts/update_data.py --notify --verbose
   ```

### Notification Contents

**Success Email:**

- ✅ Success indicator
- Duration of update
- Number of indicators updated
- Number of failures (if any)
- Link to log file

**Error Email:**

- ❌ Error indicator
- Error messages
- Stack trace (in logs)
- Troubleshooting guidance

## Logging

### Log Files

All logs are stored in the `logs/` directory:

```
logs/
├── data_update_20260108.log    # Daily log with timestamp
├── cron.log                     # Cron execution log
├── systemd.log                  # Systemd service log
└── last_update_summary.json    # Latest update summary
```

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: Confirmation of successful operations
- **WARNING**: Unexpected but handled situations
- **ERROR**: Serious problems preventing operation

### View Logs

```bash
# Latest update log
tail -f logs/data_update_$(date +%Y%m%d).log

# All logs from today
cat logs/data_update_$(date +%Y%m%d).log

# Cron log
tail -f logs/cron.log

# Last update summary
cat logs/last_update_summary.json | python -m json.tool
```

## Recommended Schedules

### Daily Updates

Best for active monitoring during volatile periods:

```bash
0 6 * * * python scripts/update_data.py --notify
```

### Weekday Updates

For normal monitoring (skip weekends):

```bash
0 9 * * 1-5 python scripts/update_data.py --notify
```

### Multiple Daily Updates

For real-time monitoring:

```bash
0 6,12,18 * * * python scripts/update_data.py
```

### Weekly Updates

For casual monitoring:

```bash
0 6 * * 1 python scripts/update_data.py --force --notify
```

## Economic Data Release Schedule

Align updates with key data releases:

- **Employment Report**: First Friday of month, 8:30 AM ET
- **GDP**: End of quarter (Jan 30, Apr 30, Jul 30, Oct 30), 8:30 AM ET
- **Consumer Sentiment**: Mid-month, 10:00 AM ET
- **PMI**: First business day of month, 10:00 AM ET
- **Treasury Yields**: Daily, continuous during market hours

**Recommended**: Run updates daily at 6 AM (after most daily updates) and force refresh on major release days.

## Monitoring & Maintenance

### Check Last Update

```bash
# View summary
cat logs/last_update_summary.json

# Parse with Python
python -c "import json; print(json.load(open('logs/last_update_summary.json'))['risk_score'])"
```

### Clear Old Logs

```bash
# Delete logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete
```

### Clear Old Cache

```bash
# Delete cache files older than 90 days
find data/cache/ -name "*.pkl" -mtime +90 -delete
```

### Manual Update

```bash
# Force fresh data
python scripts/update_data.py --force --notify --verbose
```

## Troubleshooting

### Script Won't Run

**Check permissions:**

```bash
chmod +x scripts/update_data.py
chmod +x scripts/daily_update.sh
```

**Check Python path:**

```bash
which python
python --version
```

**Activate virtual environment:**

```bash
source ~/tf/bin/activate
```

### Cron Not Working

**Check cron is running:**

```bash
# macOS
sudo launchctl list | grep cron

# Linux
sudo systemctl status cron
```

**Check cron logs:**

```bash
# macOS
log show --predicate 'process == "cron"' --last 1h

# Linux
grep CRON /var/log/syslog
```

**Test command manually:**

```bash
cd /path/to/financial_crash_indicators
source ~/tf/bin/activate
python scripts/update_data.py --verbose
```

### Email Not Sending

**Verify environment variables:**

```bash
echo $SENDER_EMAIL
echo $SMTP_SERVER
```

**Check SMTP settings:**

- Gmail: smtp.gmail.com:587
- Outlook: smtp-mail.outlook.com:587
- Yahoo: smtp.mail.yahoo.com:587

**Test SMTP connection:**

```bash
telnet smtp.gmail.com 587
```

**Check app password:**

- Use App Password, not regular account password
- Generate new password if needed
- Verify 2FA is enabled

### API Rate Limits

FRED API has rate limits:

- 120 requests per minute
- Script waits 0.1s between requests
- Full update takes ~30-60 seconds

**If hitting limits:**

```bash
# Increase delay in fred_data_fetcher.py
time.sleep(0.2)  # Slower but safer
```

### Data Not Updating

**Check cache age:**

```bash
python -c "
from src.data_collection.fred_data_fetcher import FREDDataFetcher
fetcher = FREDDataFetcher()
fetcher.print_cache_info()
"
```

**Force refresh:**

```bash
python scripts/update_data.py --force
```

**Clear cache manually:**

```bash
rm -rf data/cache/*
```

## Best Practices

1. **Test First**: Run manually before scheduling
2. **Monitor Logs**: Check logs regularly for errors
3. **Email Alerts**: Enable notifications for daily updates
4. **Backup Data**: Save summaries periodically
5. **Update Schedule**: Align with economic calendar
6. **Resource Usage**: Avoid too frequent updates (API limits)
7. **Security**: Use App Passwords, never commit credentials

## Advanced Configuration

### Custom Email Template

Edit the email body in `scripts/update_data.py`:

```python
body = f"""
Custom notification template here
Risk Score: {results['risk_score']}
"""
```

### Conditional Notifications

Only notify on high risk:

```python
if composite['composite_score'] > 75:
    send_notification(...)
```

### Slack Integration

Replace email with Slack webhook:

```python
import requests
webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
requests.post(webhook_url, json={"text": message})
```

## Support

For issues:

1. Check logs in `logs/` directory
2. Review troubleshooting section
3. Test manually with `--verbose` flag
4. Check FRED API status
5. Verify network connectivity

---

**Version**: 1.0  
**Last Updated**: January 8, 2026  
**Dashboard**: Recession Risk Monitoring System
