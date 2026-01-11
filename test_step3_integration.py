"""Test Step 3 Integration: Verify quality tracking works with data fetcher"""

from src.data_collection.fred_data_fetcher import FREDDataFetcher
from src.processing.data_quality_tracker import get_global_tracker
import pandas as pd

print("=" * 70)
print("Step 3 Integration Test: Data Quality Tracking with FRED Data Fetcher")
print("=" * 70)

# Fetch data with interpolation
fetcher = FREDDataFetcher()
labor_data = fetcher.fetch_labor_market_data('2025-09-01', apply_interpolation=True)
consumer_data = fetcher.fetch_consumer_confidence('2025-09-01', apply_interpolation=True)

# Get the global tracker
tracker = get_global_tracker()

print("\n1. QUALITY STATUS CHECK (October 2025):")
print("-" * 70)

# Check labor market indicators
labor_series = ['UNRATE', 'SAHM_Rule']
for series_id in labor_series:
    status = tracker.get_quality_status(series_id, '2025-10-01')
    print(f"  {series_id:20s} Oct 2025: {status.value}")

# Check consumer indicators  
consumer_series = ['UMich_Sentiment', 'PCE']
for series_id in consumer_series:
    status = tracker.get_quality_status(series_id, '2025-10-01')
    print(f"  {series_id:20s} Oct 2025: {status.value}")

print("\n2. INTERPOLATION METADATA:")
print("-" * 70)

for series_id in ['UNRATE', 'SAHM_Rule']:
    metadata = tracker.get_interpolation_metadata(series_id)
    if metadata:
        print(f"  {series_id}:")
        print(f"    Method: {metadata.get('estimation_method', 'N/A')}")
        print(f"    Interpolated: {metadata.get('interpolated_count', 0)} points")
        estimated_dates = metadata.get('estimated_dates', [])
        if estimated_dates:
            print(f"    Dates: {[d.strftime('%Y-%m-%d') for d in estimated_dates]}")

print("\n3. OCTOBER 2025 COMPREHENSIVE STATUS:")
print("-" * 70)

oct_status = tracker.get_october_2025_status()
for series_id, status in oct_status.items():
    if status['interpolated_count'] > 0:
        print(f"  {series_id}:")
        print(f"    Has Oct data: {status['has_oct_data']}")
        print(f"    Interpolated: {status['interpolated_count']} points")
        print(f"    Method: {status['estimation_method']}")

print("\n4. DATA QUALITY SUMMARY:")
print("-" * 70)

summary = tracker.get_summary()
print(summary[['series_id', 'actual_points', 'interpolated_points', 'interpolation_rate', 'oct_2025_affected']].to_string(index=False))

print("\n5. SPLIT SERIES TEST (UNRATE):")
print("-" * 70)

# Get UNRATE from labor data
unrate_series = labor_data['UNRATE']['2025-09':'2025-11']
actual, interpolated = tracker.split_series_by_quality('UNRATE', unrate_series)

print("\n  Actual data (solid line):")
for date, val in actual.items():
    if pd.notna(val):
        print(f"    {date.strftime('%Y-%m-%d')}: {val:.2f}")

print("\n  Interpolated data (dashed line):")
for date, val in interpolated.items():
    if pd.notna(val):
        print(f"    {date.strftime('%Y-%m-%d')}: {val:.2f}")

print("\n" + "=" * 70)
print("Step 3 Complete: Quality tracking fully integrated!")
print("=" * 70)
