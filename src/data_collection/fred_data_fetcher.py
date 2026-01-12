"""
FRED Data Fetcher Module
Fetches economic indicators from the Federal Reserve Economic Data (FRED) API
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from fredapi import Fred
from dotenv import load_dotenv
import pickle

from .cache_manager import DataCacheManager
try:
    from ..processing.data_interpolation import interpolate_october_2025, get_data_quality_flags
    from ..processing.data_quality_tracker import get_global_tracker
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from processing.data_interpolation import interpolate_october_2025, get_data_quality_flags
    from processing.data_quality_tracker import get_global_tracker

# Load environment variables
load_dotenv()

class FREDDataFetcher:
    """
    Fetches and caches economic data from FRED API with intelligent caching
    """
    
    def __init__(self, api_key=None, cache_dir=None, cache_days=None):
        """
        Initialize FRED data fetcher
        
        Parameters:
        -----------
        api_key : str, optional
            FRED API key. If None, reads from environment variable
        cache_dir : str or Path, optional
            Directory for caching data. Defaults to project data/cache directory
        cache_days : int, optional
            DEPRECATED - Cache duration is now automatic based on data frequency
        """
        self.api_key = api_key or os.getenv('FRED_API_KEY')
        if not self.api_key:
            raise ValueError("FRED API key not found. Set FRED_API_KEY in .env file")
        
        self.fred = Fred(api_key=self.api_key)
        
        # Set up cache directory
        if cache_dir is None:
            project_root = Path(__file__).parent.parent.parent
            cache_dir = project_root / "data" / "cache"
        else:
            cache_dir = Path(cache_dir)
        
        # Initialize cache manager
        self.cache = DataCacheManager(cache_dir)
        
        # Legacy support
        if cache_days is not None:
            print(f"Note: cache_days parameter is deprecated. Cache duration is now automatic based on data frequency.")
    
    def fetch_series(self, series_id, start_date='1980-01-01', use_cache=True, force_refresh=False):
        """
        Fetch a single FRED series with intelligent caching
        
        Parameters:
        -----------
        series_id : str
            FRED series identifier (e.g., 'UNRATE')
        start_date : str, optional
            Start date in 'YYYY-MM-DD' format (default: '1980-01-01')
        use_cache : bool, optional
            Whether to use cached data if available (default: True)
        force_refresh : bool, optional
            Force refresh from API even if cache is valid (default: False)
            
        Returns:
        --------
        pd.Series
            Time series data with date index
        """
        # Check cache first
        if use_cache and not force_refresh and self.cache.is_valid(series_id):
            print(f"Loading {series_id} from cache...")
            return self.cache.load(series_id)
        
        # Fetch from API
        print(f"Fetching {series_id} from FRED API...")
        try:
            data = self.fred.get_series(series_id, observation_start=start_date)
            data.name = series_id
            
            # Save to cache
            if use_cache:
                self.cache.save(series_id, data)
            
            return data
        except Exception as e:
            print(f"Error fetching {series_id}: {e}")
            # Try to return cached data even if expired
            cached_data = self.cache.load(series_id)
            if cached_data is not None:
                print(f"Returning expired cache for {series_id}")
                return cached_data
            raise
    
    def fetch_treasury_yields(self, start_date='1980-01-01'):
        """
        Fetch Treasury yield data and calculate spreads
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with columns: DGS10, DGS2, DGS3MO, Spread_10Y2Y, Spread_10Y3M
        """
        print("\n=== Fetching Treasury Yields ===")
        
        dgs10 = self.fetch_series('DGS10', start_date)
        dgs2 = self.fetch_series('DGS2', start_date)
        dgs3mo = self.fetch_series('DGS3MO', start_date)
        
        # Combine into DataFrame
        df = pd.DataFrame({
            'DGS10': dgs10,
            'DGS2': dgs2,
            'DGS3MO': dgs3mo
        })
        
        # Calculate spreads (yield curve)
        df['Spread_10Y2Y'] = df['DGS10'] - df['DGS2']
        df['Spread_10Y3M'] = df['DGS10'] - df['DGS3MO']
        
        return df
    
    def fetch_labor_market_data(self, start_date='1980-01-01', apply_interpolation=True):
        """
        Fetch labor market indicators
        
        Parameters:
        -----------
        start_date : str, default '1980-01-01'
            Start date for data fetch
        apply_interpolation : bool, default True
            Whether to interpolate missing October 2025 data
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with unemployment rate, Sahm Rule, and jobless claims
        """
        print("\n=== Fetching Labor Market Data ===")
        
        unrate = self.fetch_series('UNRATE', start_date)
        
        # Try to fetch Sahm Rule (may not be available for all dates)
        try:
            sahm = self.fetch_series('SAHMREALTIME', start_date)
        except:
            print("SAHMREALTIME not available, calculating manually...")
            sahm = self._calculate_sahm_rule(unrate)
        
        # Initial jobless claims (weekly data)
        icsa = self.fetch_series('ICSA', start_date)
        
        # Calculate 4-week moving average of jobless claims
        icsa_4wk = icsa.rolling(window=4).mean()
        
        # Apply October 2025 interpolation if requested
        if apply_interpolation:
            unrate, unrate_meta = interpolate_october_2025(unrate)
            sahm, sahm_meta = interpolate_october_2025(sahm)
            icsa, icsa_meta = interpolate_october_2025(icsa)
            icsa_4wk, icsa_4wk_meta = interpolate_october_2025(icsa_4wk)
            
            # Register quality tracking
            tracker = get_global_tracker()
            tracker.register_series('UNRATE', unrate, unrate_meta)
            tracker.register_series('SAHM_Rule', sahm, sahm_meta)
            tracker.register_series('Jobless_Claims', icsa, icsa_meta)
            tracker.register_series('Jobless_Claims_4WK', icsa_4wk, icsa_4wk_meta)
        
        df = pd.DataFrame({
            'UNRATE': unrate,
            'SAHM_Rule': sahm,
            'Jobless_Claims': icsa,
            'Jobless_Claims_4WK': icsa_4wk
        })
        
        return df
    
    def _calculate_sahm_rule(self, unemployment_rate):
        """
        Calculate Sahm Rule Recession Indicator
        
        Sahm Rule: 3-month average unemployment rate - minimum unemployment rate 
        over previous 12 months. Signal when >= 0.5 percentage points
        
        Parameters:
        -----------
        unemployment_rate : pd.Series
            Monthly unemployment rate
            
        Returns:
        --------
        pd.Series
            Sahm Rule indicator
        """
        # 3-month moving average
        ma3 = unemployment_rate.rolling(window=3).mean()
        
        # Minimum over previous 12 months
        min12 = unemployment_rate.rolling(window=12).min()
        
        # Sahm Rule indicator
        sahm = ma3 - min12
        sahm.name = 'SAHM_Rule'
        
        return sahm
    
    def fetch_credit_spreads(self, start_date='1980-01-01'):
        """
        Fetch corporate credit spread data
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with credit spread indicators
        """
        print("\n=== Fetching Credit Spreads ===")
        
        # High Yield spread
        try:
            hy_spread = self.fetch_series('BAMLH0A0HYM2', start_date)
        except:
            print("High yield spread (BAMLH0A0HYM2) not available")
            hy_spread = pd.Series(dtype=float)
        
        # BBB Corporate Bond spread
        try:
            bbb_spread = self.fetch_series('BAMLC0A4CBBB', start_date)
        except:
            print("BBB spread (BAMLC0A4CBBB) not available")
            bbb_spread = pd.Series(dtype=float)
        
        # Alternative: Calculate spread from yields if direct spread not available
        try:
            baa = self.fetch_series('DBAA', start_date)  # BAA Corporate Bond Yield
            aaa = self.fetch_series('DAAA', start_date)  # AAA Corporate Bond Yield
            dgs10 = self.fetch_series('DGS10', start_date)  # 10-Year Treasury
            
            baa_spread = baa - dgs10
            aaa_spread = aaa - dgs10
        except:
            print("Alternative corporate yields not available")
            baa_spread = pd.Series(dtype=float)
            aaa_spread = pd.Series(dtype=float)
        
        df = pd.DataFrame({
            'HY_Spread': hy_spread,
            'BBB_Spread': bbb_spread,
            'BAA_Spread': baa_spread,
            'AAA_Spread': aaa_spread
        })
        
        return df
    
    def fetch_leading_economic_index(self, start_date='1980-01-01'):
        """
        Fetch Leading Economic Index (LEI) data
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with LEI and its components
        """
        print("\n=== Fetching Leading Economic Index ===")
        
        # OECD Leading Economic Index for United States
        try:
            lei = self.fetch_series('USALOLITONOSTSAM', start_date)  # OECD Composite LEI
        except:
            print("USALOLITONOSTSAM not available, trying Conference Board...")
            try:
                lei = self.fetch_series('USSLIND', start_date)  # Conference Board LEI (discontinued)
            except:
                print("LEI not available")
                lei = pd.Series(dtype=float)
        
        # Calculate month-over-month change
        if len(lei) > 0:
            lei_mom = lei.pct_change(1) * 100  # Percentage change
            lei_6m = lei.pct_change(6) * 100
        else:
            lei_mom = pd.Series(dtype=float)
            lei_6m = pd.Series(dtype=float)
        
        df = pd.DataFrame({
            'LEI': lei,
            'LEI_MoM': lei_mom,
            'LEI_6M_Change': lei_6m
        })
        
        return df
    
    def fetch_manufacturing_pmi(self, start_date='1980-01-01'):
        """
        Fetch ISM Manufacturing PMI data
        
        Note: Actual ISM PMI is proprietary and not available via FRED.
        Using Industrial Production as a proxy for manufacturing activity.
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with manufacturing indicators
        """
        print("\n=== Fetching Manufacturing PMI ===")
        
        # Use Industrial Production: Manufacturing (IPMAN) as PMI proxy
        # This is on a ~100 index scale, similar to PMI
        try:
            pmi_proxy = self.fetch_series('IPMAN', start_date)  # Manufacturing Industrial Production
        except:
            print("IPMAN not available, using INDPRO...")
            try:
                pmi_proxy = self.fetch_series('INDPRO', start_date)
            except:
                print("Manufacturing proxy not available")
                pmi_proxy = pd.Series(dtype=float)
        
        # Manufacturing Employment (in thousands)
        try:
            employment = self.fetch_series('MANEMP', start_date)
        except:
            print("MANEMP not available")
            employment = pd.Series(dtype=float)
        
        # ISM Manufacturing: New Orders
        try:
            new_orders = self.fetch_series('NEWORDER', start_date)
        except:
            print("NEWORDER not available")
            new_orders = pd.Series(dtype=float)
        
        # Industrial Production Index (better proxy for manufacturing activity)
        try:
            industrial_prod = self.fetch_series('INDPRO', start_date)
            ip_mom = industrial_prod.pct_change(1) * 100
        except:
            print("INDPRO not available")
            industrial_prod = pd.Series(dtype=float)
            ip_mom = pd.Series(dtype=float)
        
        df = pd.DataFrame({
            'ISM_PMI': pmi_proxy,  # Using IPMAN/INDPRO as proxy (index ~100 scale)
            'ISM_Employment': employment,
            'ISM_New_Orders': new_orders,
            'Industrial_Production': industrial_prod,
            'IP_MoM': ip_mom
        })
        
        return df
        
        return df
    
    def fetch_gdp_data(self, start_date='1980-01-01'):
        """
        Fetch GDP and related economic growth data
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with GDP and growth indicators
        """
        print("\n=== Fetching GDP Data ===")
        
        # Real GDP (quarterly)
        gdp = self.fetch_series('GDPC1', start_date)
        
        # Calculate quarter-over-quarter annualized growth rate
        gdp_qoq = gdp.pct_change(1) * 100
        
        # Calculate year-over-year growth
        gdp_yoy = gdp.pct_change(4) * 100
        
        # Real Gross Domestic Product per Capita
        try:
            gdp_per_capita = self.fetch_series('A939RX0Q048SBEA', start_date)
        except:
            print("GDP per capita not available")
            gdp_per_capita = pd.Series(dtype=float)
        
        # Real GDP: Goods
        try:
            gdp_goods = self.fetch_series('DGDSRG3Q086SBEA', start_date)
        except:
            print("GDP Goods component not available")
            gdp_goods = pd.Series(dtype=float)
        
        df = pd.DataFrame({
            'Real_GDP': gdp,
            'GDP_QoQ_Growth': gdp_qoq,
            'GDP_YoY_Growth': gdp_yoy,
            'GDP_Per_Capita': gdp_per_capita,
            'GDP_Goods': gdp_goods
        })
        
        return df
    
    def fetch_consumer_confidence(self, start_date='1980-01-01', apply_interpolation=True):
        """
        Fetch consumer confidence and sentiment data
        
        Parameters:
        -----------
        start_date : str, default '1980-01-01'
            Start date for data fetch
        apply_interpolation : bool, default True
            Whether to interpolate missing October 2025 data
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with consumer confidence indicators
        """
        print("\n=== Fetching Consumer Confidence ===")
        
        # University of Michigan Consumer Sentiment
        umich = self.fetch_series('UMCSENT', start_date)
        
        # Consumer Confidence Index (Conference Board)
        try:
            cci = self.fetch_series('CSCICP03USM665S', start_date)
        except:
            print("Conference Board CCI not available")
            cci = pd.Series(dtype=float)
        
        # Personal Consumption Expenditures
        try:
            pce = self.fetch_series('PCE', start_date)
        except:
            print("PCE not available")
            pce = pd.Series(dtype=float)
        
        # Retail Sales
        try:
            retail = self.fetch_series('RSXFS', start_date)
        except:
            print("Retail sales not available")
            retail = pd.Series(dtype=float)
        
        # Apply October 2025 interpolation if requested
        if apply_interpolation:
            umich, umich_meta = interpolate_october_2025(umich)
            cci, cci_meta = interpolate_october_2025(cci)
            pce, pce_meta = interpolate_october_2025(pce)
            retail, retail_meta = interpolate_october_2025(retail)
            
            # Register quality tracking
            tracker = get_global_tracker()
            tracker.register_series('UMich_Sentiment', umich, umich_meta)
            tracker.register_series('Consumer_Confidence', cci, cci_meta)
            tracker.register_series('PCE', pce, pce_meta)
            tracker.register_series('Retail_Sales', retail, retail_meta)
        
        # Calculate percentage changes after interpolation
        pce_mom = pce.pct_change(1) * 100
        pce_yoy = pce.pct_change(12) * 100
        retail_mom = retail.pct_change(1) * 100
        
        df = pd.DataFrame({
            'UMich_Sentiment': umich,
            'Consumer_Confidence': cci,
            'PCE': pce,
            'PCE_MoM': pce_mom,
            'PCE_YoY': pce_yoy,
            'Retail_Sales': retail,
            'Retail_Sales_MoM': retail_mom
        })
        
        return df
    
    def fetch_housing_data(self, start_date='1980-01-01'):
        """
        Fetch housing market indicators
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with housing starts and building permits
        """
        print("\n=== Fetching Housing Data ===")
        
        # Housing Starts
        housing_starts = self.fetch_series('HOUST', start_date)
        
        # Building Permits
        building_permits = self.fetch_series('PERMIT', start_date)
        
        # New Home Sales
        try:
            new_home_sales = self.fetch_series('HSN1F', start_date)
        except:
            print("New home sales not available")
            new_home_sales = pd.Series(dtype=float)
        
        # Existing Home Sales
        try:
            existing_home_sales = self.fetch_series('EXHOSLUSM495S', start_date)
        except:
            print("Existing home sales not available")
            existing_home_sales = pd.Series(dtype=float)
        
        # Median Home Price
        try:
            median_price = self.fetch_series('MSPUS', start_date)
            price_yoy = median_price.pct_change(4) * 100  # Quarterly data
        except:
            print("Median home price not available")
            median_price = pd.Series(dtype=float)
            price_yoy = pd.Series(dtype=float)
        
        # Calculate month-over-month changes
        starts_mom = housing_starts.pct_change(1) * 100
        permits_mom = building_permits.pct_change(1) * 100
        
        df = pd.DataFrame({
            'Housing_Starts': housing_starts,
            'Building_Permits': building_permits,
            'Starts_MoM': starts_mom,
            'Permits_MoM': permits_mom,
            'New_Home_Sales': new_home_sales,
            'Existing_Home_Sales': existing_home_sales,
            'Median_Home_Price': median_price,
            'Price_YoY': price_yoy
        })
        
        return df
    
    def fetch_all_core_indicators(self, start_date='1980-01-01'):
        """
        Fetch all core recession indicators
        
        Returns:
        --------
        dict
            Dictionary with DataFrames for each indicator category
        """
        print("\n" + "="*60)
        print("FETCHING ALL CORE RECESSION INDICATORS")
        print("="*60)
        
        data = {
            'treasury_yields': self.fetch_treasury_yields(start_date),
            'labor_market': self.fetch_labor_market_data(start_date),
            'credit_spreads': self.fetch_credit_spreads(start_date)
        }
        
        print("\n" + "="*60)
        print("DATA FETCH COMPLETE")
        print("="*60)
        
        return data
    
    def fetch_all_secondary_indicators(self, start_date='1980-01-01'):
        """
        Fetch all secondary recession indicators
        
        Returns:
        --------
        dict
            Dictionary with DataFrames for each indicator category
        """
        print("\n" + "="*60)
        print("FETCHING ALL SECONDARY RECESSION INDICATORS")
        print("="*60)
        
        data = {
            'lei': self.fetch_leading_economic_index(start_date),
            'manufacturing': self.fetch_manufacturing_pmi(start_date),
            'gdp': self.fetch_gdp_data(start_date),
            'consumer': self.fetch_consumer_confidence(start_date),
            'housing': self.fetch_housing_data(start_date)
        }
        
        print("\n" + "="*60)
        print("SECONDARY INDICATORS FETCH COMPLETE")
        print("="*60)
        
        return data
    
    def fetch_all_indicators(self, start_date='1980-01-01'):
        """
        Fetch ALL recession indicators (core + secondary)
        
        Returns:
        --------
        dict
            Dictionary with DataFrames for all indicator categories
        """
        print("\n" + "="*60)
        print("FETCHING ALL RECESSION INDICATORS (CORE + SECONDARY)")
        print("="*60)
        
        core = self.fetch_all_core_indicators(start_date)
        secondary = self.fetch_all_secondary_indicators(start_date)
        
        # Combine both dictionaries
        data = {**core, **secondary}
        
        print("\n" + "="*60)
        print("ALL INDICATORS FETCH COMPLETE")
        print("="*60)
        
        return data
    
    def get_latest_values(self, include_secondary=True):
        """
        Get the most recent values for all indicators
        
        Parameters:
        -----------
        include_secondary : bool, optional
            Whether to include secondary indicators (default: True)
        
        Returns:
        --------
        dict
            Dictionary with latest values and their dates
        """
        if include_secondary:
            data = self.fetch_all_indicators()
        else:
            data = self.fetch_all_core_indicators()
        
        latest = {}
        
        for category, df in data.items():
            latest[category] = {}
            for col in df.columns:
                valid_data = df[col].dropna()
                if len(valid_data) > 0:
                    latest[category][col] = {
                        'value': valid_data.iloc[-1],
                        'date': valid_data.index[-1].strftime('%Y-%m-%d')
                    }
        
        return latest
    
    def clear_cache(self, series_id=None):
        """
        Clear cached data
        
        Parameters:
        -----------
        series_id : str, optional
            Specific series to clear. If None, clears all cache
        """
        if series_id:
            self.cache.clear(series_id)
            print(f"Cleared cache for {series_id}")
        else:
            self.cache.clear_all()
            print("Cleared all cache")
    
    def clear_expired_cache(self):
        """
        Clear only expired cache entries
        
        Returns:
        --------
        list of str
            List of cleared series IDs
        """
        cleared = self.cache.clear_expired()
        if cleared:
            print(f"Cleared {len(cleared)} expired cache entries")
        else:
            print("No expired cache entries found")
        return cleared
    
    def print_cache_info(self):
        """Print cache statistics and information"""
        self.cache.print_cache_info()


if __name__ == "__main__":
    # Test the fetcher with all indicators
    print("Testing FRED Data Fetcher (All Indicators)...")
    
    fetcher = FREDDataFetcher()
    
    # Fetch all indicators (core + secondary)
    print("\n" + "="*60)
    print("Testing: Fetching ALL indicators from 2015 onwards...")
    print("="*60)
    data = fetcher.fetch_all_indicators(start_date='2015-01-01')
    
    # Display summary
    print("\n" + "="*60)
    print("DATA SUMMARY - ALL INDICATORS")
    print("="*60)
    
    for category, df in data.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        print(f"  Date range: {df.index.min()} to {df.index.max()}")
        print(f"  Columns ({len(df.columns)}): {', '.join(df.columns)}")
        print(f"  Latest values:")
        for col in df.columns:
            latest = df[col].dropna().iloc[-1] if len(df[col].dropna()) > 0 else None
            if latest is not None:
                date = df[col].dropna().index[-1]
                print(f"    {col}: {latest:.2f} (as of {date.strftime('%Y-%m-%d')})")
    
    # Get latest values with secondary indicators
    print("\n" + "="*60)
    print("LATEST VALUES WITH DATES (ALL INDICATORS)")
    print("="*60)
    latest = fetcher.get_latest_values(include_secondary=True)
    
    # Display in organized format
    print("\n📊 CORE INDICATORS:")
    print("-" * 60)
    
    for category in ['treasury_yields', 'labor_market', 'credit_spreads']:
        if category in latest:
            print(f"\n{category.upper().replace('_', ' ')}:")
            for indicator, info in latest[category].items():
                if not pd.isna(info['value']):
                    print(f"  {indicator}: {info['value']:.2f} ({info['date']})")
    
    print("\n\n📈 SECONDARY INDICATORS:")
    print("-" * 60)
    
    for category in ['lei', 'manufacturing', 'gdp', 'consumer', 'housing']:
        if category in latest:
            print(f"\n{category.upper()}:")
            for indicator, info in latest[category].items():
                if not pd.isna(info['value']):
                    # Format based on indicator type
                    if 'MoM' in indicator or 'YoY' in indicator or 'Growth' in indicator:
                        print(f"  {indicator}: {info['value']:+.2f}% ({info['date']})")
                    else:
                        print(f"  {indicator}: {info['value']:.2f} ({info['date']})")
