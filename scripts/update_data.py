#!/usr/bin/env python3
"""
Automated data update script for Recession Dashboard
Fetches latest economic data from FRED and updates cache

Usage:
    python scripts/update_data.py [--force] [--notify] [--verbose]
    
Options:
    --force     Force refresh all data regardless of cache age
    --notify    Send email notification on completion/errors
    --verbose   Enable detailed logging output
"""

import sys
import os
from pathlib import Path
import argparse
import logging
from datetime import datetime
import json
import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from data_collection.fred_data_fetcher import FREDDataFetcher
from processing.recession_analyzer import RecessionIndicatorAnalyzer
from processing.recession_markers import RecessionMarkers

# Setup logging
LOG_DIR = project_root / 'logs'
LOG_DIR.mkdir(exist_ok=True)

def setup_logging(verbose=False):
    """Configure logging with file and console handlers"""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_file = LOG_DIR / f"data_update_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler (detailed)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler (less detailed)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger, log_file

def send_notification(subject, body, is_error=False):
    """Send email notification (configure SMTP settings)"""
    # Load email configuration from environment or config file
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    sender_email = os.environ.get('SENDER_EMAIL', '')
    sender_password = os.environ.get('SENDER_PASSWORD', '')
    recipient_email = os.environ.get('RECIPIENT_EMAIL', '')
    
    if not all([sender_email, sender_password, recipient_email]):
        logging.warning("Email configuration incomplete. Skipping notification.")
        logging.info("Set SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL environment variables.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"{'❌ ERROR' if is_error else '✅'} {subject}"
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        logging.info(f"Notification sent to {recipient_email}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send notification: {str(e)}")
        return False

def get_data_freshness(fetcher):
    """Check how fresh the cached data is"""
    cache_info = {}
    
    # Check each category
    categories = {
        'treasury_yields': ['DGS10', 'DGS2', 'DGS3MO'],
        'labor_market': ['UNRATE', 'SAHMREALTIME'],
        'credit_spreads': ['BAMLH0A0HYM2', 'DBAA'],
        'gdp': ['GDPC1'],
        'consumer': ['UMCSENT']
    }
    
    for category, series_ids in categories.items():
        for series_id in series_ids:
            cache_file = fetcher.cache.cache_dir / f"{series_id}.pkl"
            if cache_file.exists():
                age_hours = (datetime.now().timestamp() - cache_file.stat().st_mtime) / 3600
                cache_info[series_id] = {
                    'age_hours': age_hours,
                    'age_days': age_hours / 24,
                    'file': str(cache_file)
                }
    
    return cache_info

def update_data(force_refresh=False):
    """Main data update function"""
    logger = logging.getLogger()
    
    results = {
        'start_time': datetime.now(),
        'success': False,
        'indicators_fetched': 0,
        'indicators_failed': 0,
        'cache_cleared': force_refresh,
        'errors': [],
        'warnings': []
    }
    
    try:
        logger.info("="*70)
        logger.info("RECESSION DASHBOARD DATA UPDATE")
        logger.info("="*70)
        logger.info(f"Start time: {results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Force refresh: {force_refresh}")
        
        # Initialize components
        logger.info("\nInitializing data fetcher...")
        fetcher = FREDDataFetcher()
        markers = RecessionMarkers()
        analyzer = RecessionIndicatorAnalyzer()
        
        # Check current cache status
        if not force_refresh:
            logger.info("\nChecking cache freshness...")
            cache_info = get_data_freshness(fetcher)
            
            if cache_info:
                oldest = max(cache_info.items(), key=lambda x: x[1]['age_hours'])
                newest = min(cache_info.items(), key=lambda x: x[1]['age_hours'])
                logger.info(f"Oldest cached data: {oldest[0]} ({oldest[1]['age_days']:.1f} days old)")
                logger.info(f"Newest cached data: {newest[0]} ({newest[1]['age_hours']:.1f} hours old)")
            else:
                logger.info("No cached data found")
        
        # Clear cache if forced
        if force_refresh:
            logger.info("\nClearing all cached data...")
            fetcher.clear_cache()
            logger.info("Cache cleared successfully")
        
        # Fetch data
        logger.info("\nFetching all economic indicators...")
        logger.info("-" * 70)
        
        data = fetcher.fetch_all_indicators(start_date='2000-01-01')
        
        # Count successful fetches
        for category, df in data.items():
            if df is not None and not df.empty:
                results['indicators_fetched'] += len(df.columns)
                logger.info(f"✓ {category}: {len(df.columns)} indicators, "
                          f"{len(df)} data points, "
                          f"latest: {df.index.max().strftime('%Y-%m-%d')}")
            else:
                results['indicators_failed'] += 1
                results['errors'].append(f"No data for category: {category}")
                logger.warning(f"✗ {category}: No data available")
        
        # Run analysis
        logger.info("\nRunning recession analysis...")
        analysis = analyzer.analyze_all_indicators(data)
        
        composite = analysis['composite']
        logger.info(f"Composite Risk Score: {composite['composite_score']:.1f}/100")
        logger.info(f"Risk Level: {composite['risk_level']}")
        
        # Log top contributors
        logger.info("\nTop 3 Risk Contributors:")
        top_contributors = sorted(
            composite['breakdown'].items(),
            key=lambda x: x[1]['contribution'],
            reverse=True
        )[:3]
        
        for i, (indicator, details) in enumerate(top_contributors, 1):
            logger.info(f"{i}. {details['description']}: "
                       f"{details['contribution']:.1f} points "
                       f"({details['signal']})")
        
        # Save update summary
        summary_file = LOG_DIR / 'last_update_summary.json'
        summary = {
            'timestamp': results['start_time'].isoformat(),
            'risk_score': composite['composite_score'],
            'risk_level': composite['risk_level'],
            'indicators_fetched': results['indicators_fetched'],
            'indicators_failed': results['indicators_failed'],
            'latest_data_date': max(df.index.max() for df in data.values() if not df.empty).isoformat(),
            'top_risks': [
                {
                    'indicator': details['description'],
                    'contribution': details['contribution'],
                    'signal': details['signal']
                }
                for _, details in top_contributors
            ]
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"\nUpdate summary saved to: {summary_file}")
        
        results['success'] = True
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        logger.info("="*70)
        logger.info(f"DATA UPDATE COMPLETED SUCCESSFULLY")
        logger.info(f"Duration: {results['duration']:.1f} seconds")
        logger.info(f"Indicators fetched: {results['indicators_fetched']}")
        logger.info(f"Indicators failed: {results['indicators_failed']}")
        logger.info("="*70)
        
        return results
        
    except Exception as e:
        results['success'] = False
        results['end_time'] = datetime.now()
        results['errors'].append(str(e))
        
        logger.error("="*70)
        logger.error("DATA UPDATE FAILED")
        logger.error(f"Error: {str(e)}")
        logger.error("Traceback:")
        logger.error(traceback.format_exc())
        logger.error("="*70)
        
        return results

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Update recession dashboard data from FRED API'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh all data regardless of cache age'
    )
    parser.add_argument(
        '--notify',
        action='store_true',
        help='Send email notification on completion/errors'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable detailed logging output'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger, log_file = setup_logging(args.verbose)
    
    # Run update
    results = update_data(force_refresh=args.force)
    
    # Send notification if requested
    if args.notify:
        if results['success']:
            subject = f"Recession Dashboard Update - Success"
            body = f"""
Recession Dashboard Data Update Summary
========================================

Status: SUCCESS ✅
Duration: {results['duration']:.1f} seconds
Timestamp: {results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}

Indicators Updated: {results['indicators_fetched']}
Indicators Failed: {results['indicators_failed']}

Log file: {log_file}

This is an automated notification from the Recession Dashboard.
            """
            send_notification(subject, body.strip(), is_error=False)
        else:
            subject = f"Recession Dashboard Update - FAILED"
            body = f"""
Recession Dashboard Data Update FAILED
=======================================

Status: FAILED ❌
Timestamp: {results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}

Errors:
{chr(10).join(f'  - {e}' for e in results['errors'])}

Indicators Fetched: {results['indicators_fetched']}
Indicators Failed: {results['indicators_failed']}

Log file: {log_file}

Please check the logs and investigate the issue.
            """
            send_notification(subject, body.strip(), is_error=True)
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)

if __name__ == '__main__':
    main()
