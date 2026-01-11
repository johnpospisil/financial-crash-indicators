"""
Check if October 2025 CPI and Jobs Report data exists in FRED
Concerns: Government shutdown may have prevented data collection
"""

from src.data_collection.fred_data_fetcher import FREDDataFetcher
import pandas as pd

fetcher = FREDDataFetcher()

print('Checking October 2025 data availability...\n')
print('=' * 70)

# Check CPI data
print('\n1. CPI (Consumer Price Index - CPIAUCSL):')
print('-' * 70)
try:
    cpi = fetcher.fetch_series('CPIAUCSL', start_date='2025-08-01')
    print('   Last 5 data points:')
    for idx, val in cpi.tail().items():
        print(f'   {idx.strftime("%Y-%m-%d")}: {val:.2f}')
    
    oct_data = cpi[cpi.index >= '2025-10-01']
    if len(oct_data) > 0:
        print(f'\n   STATUS: October 2025 data EXISTS')
        print(f'   Date: {oct_data.index[0].strftime("%Y-%m-%d")}')
        print(f'   Value: {oct_data.iloc[0]:.2f}')
    else:
        print('\n   STATUS: October 2025 data MISSING')
        print('   This indicates a potential data gap!')
except Exception as e:
    print(f'   ERROR: {e}')

# Check Unemployment Rate
print('\n2. Unemployment Rate (UNRATE):')
print('-' * 70)
try:
    unrate = fetcher.fetch_series('UNRATE', start_date='2025-08-01')
    print('   Last 5 data points:')
    for idx, val in unrate.tail().items():
        print(f'   {idx.strftime("%Y-%m-%d")}: {val:.1f}%')
    
    oct_data = unrate[unrate.index >= '2025-10-01']
    if len(oct_data) > 0:
        print(f'\n   STATUS: October 2025 data EXISTS')
        print(f'   Date: {oct_data.index[0].strftime("%Y-%m-%d")}')
        print(f'   Value: {oct_data.iloc[0]:.1f}%')
    else:
        print('\n   STATUS: October 2025 data MISSING')
        print('   This indicates a potential data gap!')
except Exception as e:
    print(f'   ERROR: {e}')

# Check Nonfarm Payrolls
print('\n3. Nonfarm Payrolls (PAYEMS):')
print('-' * 70)
try:
    payems = fetcher.fetch_series('PAYEMS', start_date='2025-08-01')
    print('   Last 5 data points:')
    for idx, val in payems.tail().items():
        print(f'   {idx.strftime("%Y-%m-%d")}: {val:,.0f}K')
    
    oct_data = payems[payems.index >= '2025-10-01']
    if len(oct_data) > 0:
        print(f'\n   STATUS: October 2025 data EXISTS')
        print(f'   Date: {oct_data.index[0].strftime("%Y-%m-%d")}')
        print(f'   Value: {oct_data.iloc[0]:,.0f}K')
    else:
        print('\n   STATUS: October 2025 data MISSING')
        print('   This indicates a potential data gap!')
except Exception as e:
    print(f'   ERROR: {e}')

print('\n' + '=' * 70)
print('Analysis complete.')
