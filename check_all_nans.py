"""
Comprehensive check for NaN (missing) values across all economic indicators
"""

from src.data_collection.fred_data_fetcher import FREDDataFetcher
import pandas as pd
from datetime import datetime

fetcher = FREDDataFetcher()

print('Checking ALL economic indicators for NaN values...')
print('=' * 80)
print('Focusing on recent data (2024-2026) where issues are most likely')
print('=' * 80)

start_date = '2024-01-01'

# Get all data
print('\nFetching all data...')
treasury_data = fetcher.fetch_treasury_yields(start_date)
labor_data = fetcher.fetch_labor_market_data(start_date)
credit_data = fetcher.fetch_credit_spreads(start_date)
gdp_data = fetcher.fetch_gdp_data(start_date)
consumer_data = fetcher.fetch_consumer_confidence(start_date)
lei_data = fetcher.fetch_leading_economic_index(start_date)
pmi_data = fetcher.fetch_manufacturing_pmi(start_date)
housing_data = fetcher.fetch_housing_data(start_date)

all_series = {}

# Collect all series
print('Organizing data series...\n')

# Treasury yields
for col in treasury_data.columns:
    all_series[f'Treasury: {col}'] = treasury_data[col]

# Labor market
for col in labor_data.columns:
    all_series[f'Labor: {col}'] = labor_data[col]

# Credit indicators
for col in credit_data.columns:
    all_series[f'Credit: {col}'] = credit_data[col]

# GDP data
for col in gdp_data.columns:
    all_series[f'GDP: {col}'] = gdp_data[col]

# Consumer confidence
for col in consumer_data.columns:
    all_series[f'Consumer: {col}'] = consumer_data[col]

# Leading Economic Index
for col in lei_data.columns:
    all_series[f'LEI: {col}'] = lei_data[col]

# Manufacturing PMI
for col in pmi_data.columns:
    all_series[f'PMI: {col}'] = pmi_data[col]

# Housing data
for col in housing_data.columns:
    all_series[f'Housing: {col}'] = housing_data[col]

# Check each series for NaN values
print('SCANNING FOR MISSING DATA (NaN values):')
print('=' * 80)

found_issues = False
total_series = len(all_series)
series_with_nans = 0

for series_name, series_data in all_series.items():
    nan_count = series_data.isna().sum()
    
    if nan_count > 0:
        series_with_nans += 1
        found_issues = True
        
        # Find the dates with NaN
        nan_dates = series_data[series_data.isna()].index
        
        print(f'\n⚠️  {series_name}')
        print(f'    Total NaN values: {nan_count}')
        print(f'    Missing dates:')
        
        # Show first 10 NaN dates
        for date in nan_dates[:10]:
            print(f'      - {date.strftime("%Y-%m-%d")}')
        
        if len(nan_dates) > 10:
            print(f'      ... and {len(nan_dates) - 10} more')
        
        # Check if recent data (last 3 months) has NaN
        recent_data = series_data[series_data.index >= '2025-10-01']
        recent_nans = recent_data.isna().sum()
        if recent_nans > 0:
            print(f'    ❌ CRITICAL: {recent_nans} missing values in recent data (Oct 2025+)')

print('\n' + '=' * 80)
print('SUMMARY:')
print('=' * 80)
print(f'Total series checked: {total_series}')
print(f'Series with NaN values: {series_with_nans}')
print(f'Clean series: {total_series - series_with_nans}')

if not found_issues:
    print('\n✅ All data is complete - no NaN values found!')
else:
    print(f'\n⚠️  Found missing data in {series_with_nans} series')
    print('This may impact recession analysis and visualizations.')

# Special check for October 2025 across all series
print('\n' + '=' * 80)
print('OCTOBER 2025 SPECIFIC CHECK:')
print('=' * 80)

oct_issues = []
for series_name, series_data in all_series.items():
    oct_data = series_data[(series_data.index >= '2025-10-01') & (series_data.index < '2025-11-01')]
    if len(oct_data) > 0 and oct_data.isna().all():
        oct_issues.append(series_name)

if oct_issues:
    print(f'\n❌ {len(oct_issues)} series completely missing October 2025 data:')
    for series in oct_issues:
        print(f'   - {series}')
else:
    print('\n✅ No series completely missing October 2025')

print('\n' + '=' * 80)
