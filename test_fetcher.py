"""
Test script for FRED Data Fetcher
Run this to verify your API key and data fetching functionality
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_collection.fred_data_fetcher import FREDDataFetcher

def test_api_connection():
    """Test basic API connection"""
    print("="*60)
    print("TESTING FRED API CONNECTION")
    print("="*60)
    
    try:
        fetcher = FREDDataFetcher()
        print("✓ API key loaded successfully")
        
        # Test with a simple series
        print("\nTesting with unemployment rate (UNRATE)...")
        data = fetcher.fetch_series('UNRATE', start_date='2020-01-01')
        print(f"✓ Successfully fetched {len(data)} data points")
        print(f"  Latest value: {data.iloc[-1]:.1f}% (as of {data.index[-1].strftime('%Y-%m-%d')})")
        
        return True
        
    except ValueError as e:
        print(f"✗ Configuration Error: {e}")
        print("\nPlease ensure:")
        print("  1. You have copied .env.example to .env")
        print("  2. You have added your FRED API key to .env")
        print("  3. See docs/API_SETUP_GUIDE.md for instructions")
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_core_indicators():
    """Test fetching all core indicators"""
    print("\n" + "="*60)
    print("TESTING CORE INDICATORS FETCH")
    print("="*60)
    
    try:
        fetcher = FREDDataFetcher(cache_days=1)
        
        # Fetch recent data only for faster testing
        print("\nFetching data from 2020 onwards (testing mode)...")
        data = fetcher.fetch_all_core_indicators(start_date='2020-01-01')
        
        print("\n✓ All core indicators fetched successfully!")
        
        # Show summary
        print("\n" + "-"*60)
        print("DATA SUMMARY")
        print("-"*60)
        
        for category, df in data.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Data points: {len(df)}")
            print(f"  Date range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error fetching core indicators: {e}")
        return False

def test_latest_values():
    """Test getting latest values"""
    print("\n" + "="*60)
    print("TESTING LATEST VALUES RETRIEVAL")
    print("="*60)
    
    try:
        fetcher = FREDDataFetcher()
        latest = fetcher.get_latest_values()
        
        print("\n✓ Latest values retrieved successfully!")
        print("\n" + "-"*60)
        print("CURRENT RECESSION INDICATORS")
        print("-"*60)
        
        # Treasury yields
        if 'treasury_yields' in latest:
            print("\nYield Curve:")
            ty = latest['treasury_yields']
            if 'Spread_10Y2Y' in ty:
                spread = ty['Spread_10Y2Y']['value']
                date = ty['Spread_10Y2Y']['date']
                status = "⚠️ INVERTED" if spread < 0 else "✓ Normal"
                print(f"  10Y-2Y Spread: {spread:+.2f}% ({status}) - {date}")
            
            if 'Spread_10Y3M' in ty:
                spread = ty['Spread_10Y3M']['value']
                date = ty['Spread_10Y3M']['date']
                status = "⚠️ INVERTED" if spread < 0 else "✓ Normal"
                print(f"  10Y-3M Spread: {spread:+.2f}% ({status}) - {date}")
        
        # Labor market
        if 'labor_market' in latest:
            print("\nLabor Market:")
            lm = latest['labor_market']
            if 'UNRATE' in lm:
                rate = lm['UNRATE']['value']
                date = lm['UNRATE']['date']
                print(f"  Unemployment Rate: {rate:.1f}% - {date}")
            
            if 'SAHM_Rule' in lm:
                sahm = lm['SAHM_Rule']['value']
                date = lm['SAHM_Rule']['date']
                status = "⚠️ RECESSION SIGNAL" if sahm >= 0.5 else "✓ Normal"
                print(f"  Sahm Rule: {sahm:.2f} ({status}) - {date}")
        
        # Credit spreads
        if 'credit_spreads' in latest:
            print("\nCredit Spreads:")
            cs = latest['credit_spreads']
            for key in ['HY_Spread', 'BBB_Spread', 'BAA_Spread']:
                if key in cs:
                    value = cs[key]['value']
                    date = cs[key]['date']
                    if not pd.isna(value):
                        print(f"  {key}: {value:.2f}% - {date}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error getting latest values: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import pandas as pd
    
    print("\n" + "="*60)
    print("FRED DATA FETCHER TEST SUITE")
    print("="*60)
    
    # Run tests
    results = []
    
    results.append(("API Connection", test_api_connection()))
    
    if results[0][1]:  # Only continue if API connection works
        results.append(("Core Indicators", test_core_indicators()))
        results.append(("Latest Values", test_latest_values()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Your FRED data fetcher is working correctly.")
        print("\nNext steps:")
        print("  1. Run: python src/data_collection/fred_data_fetcher.py")
        print("  2. Ready for Prompt 4 (secondary indicators)")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        print("See docs/API_SETUP_GUIDE.md for troubleshooting help.")
