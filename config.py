"""
Configuration settings for the Recession Indicators Dashboard
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"

# Create directories if they don't exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

# Data update settings
DATA_CACHE_DAYS = int(os.getenv("DATA_CACHE_DAYS", 1))
UPDATE_HOUR = int(os.getenv("UPDATE_HOUR", 6))

# Indicator configurations
FRED_SERIES = {
    # Treasury yields
    "DGS10": "10-Year Treasury Rate",
    "DGS2": "2-Year Treasury Rate",
    "DGS3MO": "3-Month Treasury Rate",
    
    # Labor market
    "UNRATE": "Unemployment Rate",
    "SAHMREALTIME": "Sahm Rule Recession Indicator",
    "ICSA": "Initial Jobless Claims",
    
    # Credit spreads
    "BAMLH0A0HYM2": "High Yield Corporate Bond Spread",
    "BAMLC0A4CBBB": "BBB Corporate Bond Spread",
    
    # Economic indices
    "UMCSENT": "University of Michigan Consumer Sentiment",
    "HOUST": "Housing Starts",
    "PERMIT": "Building Permits",
    
    # GDP
    "GDPC1": "Real GDP",
}

# Recession probability thresholds
THRESHOLDS = {
    "yield_curve_inversion": 0,  # Below 0 = inverted
    "sahm_rule": 0.5,  # >= 0.5 signals recession
    "credit_spread_warning": 4.0,  # Percentage points
    "unemployment_spike": 0.5,  # Percentage point increase
}

# Visualization settings
RECESSION_COLOR = "rgba(255, 0, 0, 0.2)"
WARNING_COLOR = "rgba(255, 165, 0, 0.3)"
SAFE_COLOR = "rgba(0, 255, 0, 0.2)"

# Historical recession dates (NBER)
RECESSIONS = [
    ("1980-01-01", "1980-07-01"),
    ("1981-07-01", "1982-11-01"),
    ("1990-07-01", "1991-03-01"),
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]
