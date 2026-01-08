"""
Shared data loading utilities for the dashboard
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from data_collection.fred_data_fetcher import FREDDataFetcher
from processing.recession_analyzer import RecessionIndicatorAnalyzer
from processing.recession_markers import RecessionMarkers

# Global instances (cached)
_fetcher = None
_markers = None
_analyzer = None
_last_data = None
_last_analysis = None
_last_update = None

def get_fetcher():
    """Get or create FREDDataFetcher instance"""
    global _fetcher
    if _fetcher is None:
        _fetcher = FREDDataFetcher()
    return _fetcher

def get_markers():
    """Get or create RecessionMarkers instance"""
    global _markers
    if _markers is None:
        _markers = RecessionMarkers()
    return _markers

def get_analyzer():
    """Get or create RecessionIndicatorAnalyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = RecessionIndicatorAnalyzer()
    return _analyzer

def load_data(force_refresh=False):
    """
    Load all economic indicators data
    
    Args:
        force_refresh: If True, bypass cache and fetch fresh data
    
    Returns:
        dict: Dictionary of DataFrames with economic indicators
    """
    global _last_data, _last_update
    
    # Return cached data if available and not forcing refresh
    if not force_refresh and _last_data is not None:
        return _last_data
    
    fetcher = get_fetcher()
    
    if force_refresh:
        fetcher.clear_cache()
    
    data = fetcher.fetch_all_indicators(start_date='2000-01-01')
    _last_data = data
    _last_update = datetime.now()
    
    return data

def load_analysis(data=None, force_refresh=False):
    """
    Analyze recession indicators
    
    Args:
        data: Optional data dict. If None, will load data.
        force_refresh: If True, bypass cache
    
    Returns:
        dict: Analysis results with composite score and breakdown
    """
    global _last_analysis
    
    # Return cached analysis if available
    if not force_refresh and _last_analysis is not None:
        return _last_analysis
    
    if data is None:
        data = load_data(force_refresh)
    
    analyzer = get_analyzer()
    analysis = analyzer.analyze_all_indicators(data)
    _last_analysis = analysis
    
    return analysis

def get_last_update_time():
    """Get the timestamp of last data update"""
    return _last_update

def format_number(value, decimals=1, prefix='', suffix=''):
    """Format number with specified decimals and prefix/suffix"""
    if pd.isna(value):
        return 'N/A'
    return f"{prefix}{value:.{decimals}f}{suffix}"

def format_date(date):
    """Format date as YYYY-MM-DD"""
    if pd.isna(date):
        return 'N/A'
    if isinstance(date, str):
        return date
    return date.strftime('%Y-%m-%d')

def get_risk_color(score):
    """Get color based on risk score"""
    if score < 25:
        return 'success'  # Green
    elif score < 50:
        return 'warning'  # Yellow
    elif score < 75:
        return 'orange'  # Orange
    else:
        return 'danger'  # Red

def get_risk_badge_color(score):
    """Get Bootstrap badge color based on risk score"""
    if score < 25:
        return 'success'
    elif score < 50:
        return 'warning'
    elif score < 75:
        return 'warning'
    else:
        return 'danger'
