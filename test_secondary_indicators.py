"""
Test script for Secondary Indicators
Run this to verify secondary indicator fetching
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_collection.fred_data_fetcher import FREDDataFetcher
import pandas as pd

def test_secondary_indicators():
    """Test fetching all secondary indicators"""
    print("="*60)
    print("TESTING SECONDARY INDICATORS FETCH")
    print("="*60)
    
    try:
        fetcher = FREDDataFetcher(cache_days=1)
        
        # Fetch recent data only for faster testing
        print("\nFetching data from 2020 onwards (testing mode)...")
        data = fetcher.fetch_all_secondary_indicators(start_date='2020-01-01')
        
        print("\n✓ All secondary indicators fetched successfully!")
        
        # Show summary
        print("\n" + "-"*60)
        print("SECONDARY INDICATORS SUMMARY")
        print("-"*60)
        
        categories = {
            'lei': 'Leading Economic Index',
            'manufacturing': 'Manufacturing & PMI',
            'gdp': 'GDP & Economic Growth',
            'consumer': 'Consumer Confidence & Spending',
            'housing': 'Housing Market'
        }
        
        for key, name in categories.items():
            if key in data:
                df = data[key]
                print(f"\n{name}:")
                print(f"  Indicators: {len(df.columns)}")
                print(f"  Data points: {len(df)}")
                print(f"  Date range: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
                
                # Show latest non-null values
                print(f"  Latest values:")
                for col in df.columns:
                    valid = df[col].dropna()
                    if len(valid) > 0:
                        latest_val = valid.iloc[-1]
                        latest_date = valid.index[-1].strftime('%Y-%m-%d')
                        
                        # Format based on type
                        if 'MoM' in col or 'YoY' in col or 'Growth' in col or 'Change' in col:
                            print(f"    {col}: {latest_val:+.2f}% ({latest_date})")
                        else:
                            print(f"    {col}: {latest_val:.2f} ({latest_date})")
        
        return True
        
    except Exception as e:
        print(f"✗ Error fetching secondary indicators: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_indicators():
    """Test fetching ALL indicators (core + secondary)"""
    print("\n" + "="*60)
    print("TESTING ALL INDICATORS FETCH (CORE + SECONDARY)")
    print("="*60)
    
    try:
        fetcher = FREDDataFetcher()
        
        # Fetch recent data
        print("\nFetching all data from 2020 onwards...")
        data = fetcher.fetch_all_indicators(start_date='2020-01-01')
        
        print("\n✓ All indicators fetched successfully!")
        
        # Count total indicators
        total_indicators = sum(len(df.columns) for df in data.values())
        print(f"\n📊 Total indicators tracked: {total_indicators}")
        print(f"📁 Total categories: {len(data)}")
        
        # Show category breakdown
        print("\n" + "-"*60)
        print("CATEGORY BREAKDOWN")
        print("-"*60)
        
        core_categories = ['treasury_yields', 'labor_market', 'credit_spreads']
        secondary_categories = ['lei', 'manufacturing', 'gdp', 'consumer', 'housing']
        
        print("\nCORE INDICATORS:")
        for cat in core_categories:
            if cat in data:
                print(f"  {cat.replace('_', ' ').title()}: {len(data[cat].columns)} indicators")
        
        print("\nSECONDARY INDICATORS:")
        for cat in secondary_categories:
            if cat in data:
                print(f"  {cat.replace('_', ' ').title()}: {len(data[cat].columns)} indicators")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_recession_signals():
    """Show current recession warning signals"""
    print("\n" + "="*60)
    print("CURRENT RECESSION SIGNALS")
    print("="*60)
    
    try:
        fetcher = FREDDataFetcher()
        latest = fetcher.get_latest_values(include_secondary=True)
        
        signals = []
        
        # Check yield curve
        if 'treasury_yields' in latest:
            ty = latest['treasury_yields']
            if 'Spread_10Y2Y' in ty:
                spread = ty['Spread_10Y2Y']['value']
                date = ty['Spread_10Y2Y']['date']
                if spread < 0:
                    signals.append(f"⚠️  Yield Curve INVERTED: {spread:+.2f}% ({date})")
                else:
                    print(f"✓ Yield Curve Normal: {spread:+.2f}% ({date})")
        
        # Check Sahm Rule
        if 'labor_market' in latest:
            lm = latest['labor_market']
            if 'SAHM_Rule' in lm:
                sahm = lm['SAHM_Rule']['value']
                date = lm['SAHM_Rule']['date']
                if sahm >= 0.5:
                    signals.append(f"🚨 Sahm Rule TRIGGERED: {sahm:.2f} ({date})")
                else:
                    print(f"✓ Sahm Rule Normal: {sahm:.2f} ({date})")
        
        # Check LEI
        if 'lei' in latest:
            lei_data = latest['lei']
            if 'LEI_6M_Change' in lei_data:
                lei_change = lei_data['LEI_6M_Change']['value']
                date = lei_data['LEI_6M_Change']['date']
                if lei_change < -2:
                    signals.append(f"⚠️  LEI Declining: {lei_change:+.2f}% over 6 months ({date})")
                else:
                    print(f"✓ LEI Trend: {lei_change:+.2f}% over 6 months ({date})")
        
        # Check GDP
        if 'gdp' in latest:
            gdp_data = latest['gdp']
            if 'GDP_QoQ_Growth' in gdp_data:
                gdp_growth = gdp_data['GDP_QoQ_Growth']['value']
                date = gdp_data['GDP_QoQ_Growth']['date']
                if gdp_growth < 0:
                    signals.append(f"⚠️  GDP Contracting: {gdp_growth:+.2f}% QoQ ({date})")
                else:
                    print(f"✓ GDP Growing: {gdp_growth:+.2f}% QoQ ({date})")
        
        # Check Manufacturing PMI
        if 'manufacturing' in latest:
            mfg = latest['manufacturing']
            if 'ISM_PMI' in mfg:
                pmi = mfg['ISM_PMI']['value']
                date = mfg['ISM_PMI']['date']
                if pmi < 50:
                    signals.append(f"⚠️  Manufacturing Contracting: PMI={pmi:.1f} ({date})")
                else:
                    print(f"✓ Manufacturing Expanding: PMI={pmi:.1f} ({date})")
        
        # Display warnings
        if signals:
            print("\n" + "!"*60)
            print("RECESSION WARNING SIGNALS DETECTED:")
            print("!"*60)
            for signal in signals:
                print(signal)
        else:
            print("\n✅ No major recession signals detected at this time.")
        
        return True
        
    except Exception as e:
        print(f"✗ Error analyzing signals: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SECONDARY INDICATORS TEST SUITE")
    print("="*60)
    
    # Run tests
    results = []
    
    results.append(("Secondary Indicators", test_secondary_indicators()))
    results.append(("All Indicators", test_all_indicators()))
    results.append(("Recession Signals", show_recession_signals()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All secondary indicators working! Ready for Prompt 5 (caching mechanism).")
    else:
        print("\n⚠️ Some tests failed. Check errors above.")
