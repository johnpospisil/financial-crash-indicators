"""Test Step 2: Verify interpolation is applied to critical indicators"""

from src.data_collection.fred_data_fetcher import FREDDataFetcher
import pandas as pd

fetcher = FREDDataFetcher()

print("=" * 60)
print("Step 2 Verification: Interpolation Applied")
print("=" * 60)

# Test labor market
print("\n1. LABOR MARKET DATA:")
labor_with = fetcher.fetch_labor_market_data('2025-09-01', apply_interpolation=True)
labor_without = fetcher.fetch_labor_market_data('2025-09-01', apply_interpolation=False)

for col in ['UNRATE', 'SAHM_Rule']:
    raw = labor_without.loc['2025-10-01', col]
    interp = labor_with.loc['2025-10-01', col]
    status = "✓ FIXED" if (pd.isna(raw) and not pd.isna(interp)) else "- Has data"
    raw_str = f"{raw:.2f}" if not pd.isna(raw) else "NaN"
    interp_str = f"{interp:.2f}" if not pd.isna(interp) else "NaN"
    print(f"  {col}: {raw_str} → {interp_str} {status}")

# Test consumer confidence
print("\n2. CONSUMER CONFIDENCE DATA:")
consumer_with = fetcher.fetch_consumer_confidence('2025-09-01', apply_interpolation=True)
consumer_without = fetcher.fetch_consumer_confidence('2025-09-01', apply_interpolation=False)

for col in ['UMich_Sentiment', 'PCE']:
    raw = consumer_without.loc['2025-10-01', col]
    interp = consumer_with.loc['2025-10-01', col]
    status = "✓ FIXED" if (pd.isna(raw) and not pd.isna(interp)) else ("⏳ Need Nov data" if pd.isna(interp) else "- Has data")
    raw_str = f"{raw:.2f}" if not pd.isna(raw) else "NaN"
    interp_str = f"{interp:.2f}" if not pd.isna(interp) else "NaN"
    print(f"  {col}: {raw_str} → {interp_str} {status}")

print("\n" + "=" * 60)
print("Step 2 Complete!")
print("=" * 60)
