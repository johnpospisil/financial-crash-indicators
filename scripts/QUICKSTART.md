# Quick Start: Data Automation

## 5-Minute Setup

### 1. Test the Script

```bash
cd /Users/johnpospisil/Documents/GitHub/projects/financial_crash_indicators
source ~/tf/bin/activate
python scripts/update_data.py --verbose
```

Expected output: "DATA UPDATE COMPLETED SUCCESSFULLY"

### 2. Setup Email Notifications (Optional)

```bash
# Add to ~/.bashrc or ~/.zshrc
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your.email@gmail.com"
export SENDER_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@email.com"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

Test:

```bash
python scripts/update_data.py --notify --verbose
```

### 3. Schedule Daily Updates

**Option A: Cron (Recommended for Mac)**

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 6 AM):
0 6 * * * cd /Users/johnpospisil/Documents/GitHub/projects/financial_crash_indicators && source ~/tf/bin/activate && python scripts/update_data.py --notify >> logs/cron.log 2>&1

# Save and exit (ESC :wq in vim)
```

Verify:

```bash
crontab -l
```

**Option B: Manual Scheduling**

Create a reminder to run:

```bash
./scripts/daily_update.sh
```

## Verify It's Working

### Check Logs

```bash
# View today's update log
cat logs/data_update_$(date +%Y%m%d).log

# View last update summary
cat logs/last_update_summary.json | python -m json.tool
```

### Check Cron

```bash
# List scheduled jobs
crontab -l

# View cron execution log
tail -f logs/cron.log
```

## Common Commands

```bash
# Force refresh all data
python scripts/update_data.py --force --notify

# Quick update (respects cache)
python scripts/update_data.py

# View logs
tail -f logs/data_update_$(date +%Y%m%d).log

# Check last update
cat logs/last_update_summary.json
```

## Troubleshooting

**Script fails?**

```bash
# Check Python environment
which python
python --version

# Activate virtual environment
source ~/tf/bin/activate
```

**Cron not running?**

```bash
# Check cron logs (macOS)
log show --predicate 'process == "cron"' --last 1h

# Test command manually first
cd /Users/johnpospisil/Documents/GitHub/projects/financial_crash_indicators
source ~/tf/bin/activate
python scripts/update_data.py --verbose
```

**Email not sending?**

- Verify environment variables are set: `echo $SENDER_EMAIL`
- Use App Password from Gmail (not your regular password)
- Enable 2-factor authentication first

## What Happens During Update

1. ✅ Checks cache freshness
2. 📥 Fetches 41+ economic indicators from FRED
3. 📊 Runs recession risk analysis
4. 📝 Generates detailed logs
5. 📧 Sends email notification (if --notify)
6. 💾 Saves JSON summary

## Next Steps

See full documentation:

- `scripts/AUTOMATION_GUIDE.md` - Complete automation guide
- `scripts/cron_examples.txt` - More cron examples
- `scripts/email_config.txt` - Email setup details

---

**Setup Time**: < 5 minutes  
**Daily Runtime**: ~30-60 seconds  
**Recommended Schedule**: Daily at 6 AM
