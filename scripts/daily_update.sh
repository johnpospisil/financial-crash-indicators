#!/bin/bash
#
# Daily data update script for Recession Dashboard
# Schedule this with cron for automated daily updates
#
# Example cron entry (runs at 6 AM daily):
# 0 6 * * * /path/to/financial_crash_indicators/scripts/daily_update.sh
#

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment if it exists
if [ -d "$HOME/tf/bin/activate" ]; then
    source "$HOME/tf/bin/activate"
fi

# Change to project directory
cd "$PROJECT_ROOT"

# Run update script with notification
echo "Starting recession dashboard data update at $(date)"
python scripts/update_data.py --notify --verbose

# Check exit code
if [ $? -eq 0 ]; then
    echo "Data update completed successfully at $(date)"
    exit 0
else
    echo "Data update failed at $(date)"
    exit 1
fi
