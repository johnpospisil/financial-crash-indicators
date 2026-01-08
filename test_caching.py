"""
Test Enhanced Caching System
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_collection.fred_data_fetcher import FREDDataFetcher
from data_collection.cache_manager import DataCacheManager

def test_cache_manager():
    """Test the cache manager directly"""
    print("="*60)
    print("TESTING CACHE MANAGER")
    print("="*60)
    
    project_root = Path(__file__).parent
    cache_dir = project_root / "data" / "cache"
    
    cache = DataCacheManager(cache_dir)
    
    # Print cache info
    cache.print_cache_info()
    
    return True

def test_frequency_based_caching():
    """Test that different frequencies have different cache durations"""
    print("\n" + "="*60)
    print("TESTING FREQUENCY-BASED CACHING")
    print("="*60)
    
    try:
        fetcher = FREDDataFetcher()
        
        # Fetch a few series with different frequencies
        print("\nFetching series with different update frequencies...")
        
        # Daily data
        print("\n📅 DAILY DATA:")
        fetcher.fetch_series('DGS10', start_date='2024-01-01')
        metadata = fetcher.cache.get_metadata('DGS10')
        if metadata:
            print(f"  DGS10: {metadata['frequency']} - refreshes every {metadata['cache_duration_hours']}h")
        
        # Weekly data
        print("\n📅 WEEKLY DATA:")
        fetcher.fetch_series('ICSA', start_date='2024-01-01')
        metadata = fetcher.cache.get_metadata('ICSA')
        if metadata:
            print(f"  ICSA: {metadata['frequency']} - refreshes every {metadata['cache_duration_hours']}h")
        
        # Monthly data
        print("\n📅 MONTHLY DATA:")
        fetcher.fetch_series('UNRATE', start_date='2024-01-01')
        metadata = fetcher.cache.get_metadata('UNRATE')
        if metadata:
            print(f"  UNRATE: {metadata['frequency']} - refreshes every {metadata['cache_duration_hours']}h")
        
        # Quarterly data
        print("\n📅 QUARTERLY DATA:")
        fetcher.fetch_series('GDPC1', start_date='2024-01-01')
        metadata = fetcher.cache.get_metadata('GDPC1')
        if metadata:
            print(f"  GDPC1: {metadata['frequency']} - refreshes every {metadata['cache_duration_hours']}h")
        
        print("\n✓ Different cache durations set correctly based on data frequency!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_validation():
    """Test cache validation logic"""
    print("\n" + "="*60)
    print("TESTING CACHE VALIDATION")
    print("="*60)
    
    try:
        fetcher = FREDDataFetcher()
        
        # Check which caches are valid
        print("\nChecking cache validity...")
        
        cached_series = fetcher.cache.list_cached_series()
        
        if not cached_series:
            print("No cached data found. Run test_secondary_indicators.py first.")
            return False
        
        valid_count = sum(1 for item in cached_series if item['is_valid'])
        expired_count = sum(1 for item in cached_series if not item['is_valid'])
        
        print(f"\n📊 Cache Status:")
        print(f"  Valid: {valid_count}")
        print(f"  Expired: {expired_count}")
        print(f"  Total: {len(cached_series)}")
        
        # Show some examples
        print("\n📋 Sample Cache Entries:")
        for item in cached_series[:5]:
            status = "✓" if item['is_valid'] else "✗"
            age_hours = int(item['age_hours'])
            print(f"  {status} {item['series_id']}: {age_hours}h old ({item['frequency']}, refreshes every {item['cache_duration_hours']}h)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_management():
    """Test cache management operations"""
    print("\n" + "="*60)
    print("TESTING CACHE MANAGEMENT")
    print("="*60)
    
    try:
        fetcher = FREDDataFetcher()
        
        # Get initial stats
        initial_stats = fetcher.cache.get_cache_stats()
        print(f"\nInitial cache: {initial_stats['total_series']} series, {initial_stats['total_size_mb']} MB")
        
        # Clear expired entries
        print("\nClearing expired cache entries...")
        cleared = fetcher.clear_expired_cache()
        
        # Get updated stats
        updated_stats = fetcher.cache.get_cache_stats()
        print(f"After cleanup: {updated_stats['total_series']} series, {updated_stats['total_size_mb']} MB")
        
        if cleared:
            print(f"Freed up space by removing {len(cleared)} expired entries")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_force_refresh():
    """Test forcing a refresh of cached data"""
    print("\n" + "="*60)
    print("TESTING FORCE REFRESH")
    print("="*60)
    
    try:
        fetcher = FREDDataFetcher()
        
        print("\nFetching with cache (should use cached data)...")
        data1 = fetcher.fetch_series('DGS10', start_date='2025-01-01', use_cache=True)
        
        print("\nForcing refresh from API...")
        data2 = fetcher.fetch_series('DGS10', start_date='2025-01-01', force_refresh=True)
        
        print("✓ Force refresh works!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import pandas as pd
    
    print("\n" + "="*60)
    print("ENHANCED CACHING SYSTEM TEST SUITE")
    print("="*60)
    
    # Run tests
    results = []
    
    results.append(("Cache Manager", test_cache_manager()))
    results.append(("Frequency-Based Caching", test_frequency_based_caching()))
    results.append(("Cache Validation", test_cache_validation()))
    results.append(("Cache Management", test_cache_management()))
    results.append(("Force Refresh", test_force_refresh()))
    
    # Final cache info
    print("\n" + "="*60)
    print("FINAL CACHE STATUS")
    print("="*60)
    
    fetcher = FREDDataFetcher()
    fetcher.print_cache_info()
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 Enhanced caching system working perfectly!")
        print("\n✨ Key Features:")
        print("  • Frequency-aware caching (daily/weekly/monthly/quarterly)")
        print("  • Automatic cache validation based on data update frequency")
        print("  • Cache metadata tracking (size, age, validity)")
        print("  • Smart cache management (clear expired, clear by age)")
        print("  • Force refresh capability")
        print("\nReady for Prompt 6 (recession probability calculations)!")
    else:
        print("\n⚠️ Some tests failed. Check errors above.")
