"""
Enhanced Data Cache Manager
Manages caching of FRED data with intelligent refresh based on data frequency
"""
import os
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

class DataCacheManager:
    """
    Enhanced cache manager with frequency-aware caching
    """
    
    # Cache durations based on data frequency (in hours)
    CACHE_DURATIONS = {
        'daily': 24,        # 1 day
        'weekly': 168,      # 7 days
        'monthly': 720,     # 30 days
        'quarterly': 2160,  # 90 days
        'annual': 8760,     # 365 days
        'unknown': 24       # Default to 1 day
    }
    
    # FRED series frequency mapping
    SERIES_FREQUENCIES = {
        # Daily series
        'DGS10': 'daily',
        'DGS2': 'daily',
        'DGS3MO': 'daily',
        'BAMLH0A0HYM2': 'daily',
        'BAMLC0A4CBBB': 'daily',
        'DBAA': 'daily',
        'DAAA': 'daily',
        
        # Weekly series
        'ICSA': 'weekly',
        
        # Monthly series
        'UNRATE': 'monthly',
        'SAHMREALTIME': 'monthly',
        'UMCSENT': 'monthly',
        'CSCICP03USM665S': 'monthly',
        'PCE': 'monthly',
        'RSXFS': 'monthly',
        'HOUST': 'monthly',
        'PERMIT': 'monthly',
        'HSN1F': 'monthly',
        'EXHOSLUSM495S': 'monthly',
        'MSPUS': 'monthly',
        'USSLIND': 'monthly',
        'USALOLITONOSTSAM': 'monthly',
        'MANEMP': 'monthly',
        'NEWORDER': 'monthly',
        'MANEMP': 'monthly',
        'INDPRO': 'monthly',
        
        # Quarterly series
        'GDPC1': 'quarterly',
        'A939RX0Q048SBEA': 'quarterly',
        'DGDSRG3Q086SBEA': 'quarterly',
    }
    
    def __init__(self, cache_dir):
        """
        Initialize cache manager
        
        Parameters:
        -----------
        cache_dir : str or Path
            Directory for cache storage
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir = self.cache_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
    
    def _get_data_path(self, series_id):
        """Get cache file path for series data"""
        return self.cache_dir / f"{series_id}.pkl"
    
    def _get_metadata_path(self, series_id):
        """Get cache file path for series metadata"""
        return self.metadata_dir / f"{series_id}.json"
    
    def _get_frequency(self, series_id):
        """Determine the frequency of a series"""
        return self.SERIES_FREQUENCIES.get(series_id, 'unknown')
    
    def _get_cache_duration(self, series_id):
        """Get cache duration in hours for a series"""
        frequency = self._get_frequency(series_id)
        return self.CACHE_DURATIONS[frequency]
    
    def save(self, series_id, data, custom_metadata=None):
        """
        Save data to cache with metadata
        
        Parameters:
        -----------
        series_id : str
            Series identifier
        data : pd.Series or pd.DataFrame
            Data to cache
        custom_metadata : dict, optional
            Additional metadata to store
        """
        # Save data
        data_path = self._get_data_path(series_id)
        with open(data_path, 'wb') as f:
            pickle.dump(data, f)
        
        # Save metadata
        metadata = {
            'series_id': series_id,
            'cached_at': datetime.now().isoformat(),
            'frequency': self._get_frequency(series_id),
            'cache_duration_hours': self._get_cache_duration(series_id),
            'data_points': len(data),
            'start_date': str(data.index.min()) if len(data) > 0 else None,
            'end_date': str(data.index.max()) if len(data) > 0 else None,
            'data_type': type(data).__name__
        }
        
        if custom_metadata:
            metadata.update(custom_metadata)
        
        metadata_path = self._get_metadata_path(series_id)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load(self, series_id):
        """
        Load data from cache
        
        Parameters:
        -----------
        series_id : str
            Series identifier
            
        Returns:
        --------
        pd.Series or pd.DataFrame or None
            Cached data, or None if not found
        """
        data_path = self._get_data_path(series_id)
        if not data_path.exists():
            return None
        
        with open(data_path, 'rb') as f:
            return pickle.load(f)
    
    def get_metadata(self, series_id):
        """
        Get metadata for cached series
        
        Parameters:
        -----------
        series_id : str
            Series identifier
            
        Returns:
        --------
        dict or None
            Metadata dictionary, or None if not found
        """
        metadata_path = self._get_metadata_path(series_id)
        if not metadata_path.exists():
            return None
        
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def is_valid(self, series_id, custom_duration_hours=None):
        """
        Check if cached data is still valid
        
        Parameters:
        -----------
        series_id : str
            Series identifier
        custom_duration_hours : int, optional
            Override cache duration in hours
            
        Returns:
        --------
        bool
            True if cache is valid, False otherwise
        """
        metadata = self.get_metadata(series_id)
        if metadata is None:
            return False
        
        cached_at = datetime.fromisoformat(metadata['cached_at'])
        duration_hours = custom_duration_hours or metadata['cache_duration_hours']
        cache_expires = cached_at + timedelta(hours=duration_hours)
        
        return datetime.now() < cache_expires
    
    def get_age(self, series_id):
        """
        Get the age of cached data
        
        Parameters:
        -----------
        series_id : str
            Series identifier
            
        Returns:
        --------
        timedelta or None
            Age of cache, or None if not found
        """
        metadata = self.get_metadata(series_id)
        if metadata is None:
            return None
        
        cached_at = datetime.fromisoformat(metadata['cached_at'])
        return datetime.now() - cached_at
    
    def list_cached_series(self):
        """
        List all cached series with metadata
        
        Returns:
        --------
        list of dict
            List of metadata dictionaries for all cached series
        """
        cached = []
        for metadata_file in self.metadata_dir.glob("*.json"):
            series_id = metadata_file.stem
            metadata = self.get_metadata(series_id)
            if metadata:
                metadata['is_valid'] = self.is_valid(series_id)
                metadata['age_hours'] = self.get_age(series_id).total_seconds() / 3600
                cached.append(metadata)
        
        return sorted(cached, key=lambda x: x['cached_at'], reverse=True)
    
    def clear(self, series_id):
        """
        Clear cache for a specific series
        
        Parameters:
        -----------
        series_id : str
            Series identifier
        """
        data_path = self._get_data_path(series_id)
        metadata_path = self._get_metadata_path(series_id)
        
        if data_path.exists():
            data_path.unlink()
        if metadata_path.exists():
            metadata_path.unlink()
    
    def clear_all(self):
        """Clear all cached data"""
        for data_file in self.cache_dir.glob("*.pkl"):
            data_file.unlink()
        for metadata_file in self.metadata_dir.glob("*.json"):
            metadata_file.unlink()
    
    def clear_expired(self):
        """
        Clear only expired cache entries
        
        Returns:
        --------
        list of str
            List of cleared series IDs
        """
        cleared = []
        for metadata_file in self.metadata_dir.glob("*.json"):
            series_id = metadata_file.stem
            if not self.is_valid(series_id):
                self.clear(series_id)
                cleared.append(series_id)
        
        return cleared
    
    def clear_by_age(self, max_age_days):
        """
        Clear cache entries older than specified days
        
        Parameters:
        -----------
        max_age_days : int
            Maximum age in days
            
        Returns:
        --------
        list of str
            List of cleared series IDs
        """
        cleared = []
        max_age = timedelta(days=max_age_days)
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            series_id = metadata_file.stem
            age = self.get_age(series_id)
            if age and age > max_age:
                self.clear(series_id)
                cleared.append(series_id)
        
        return cleared
    
    def get_cache_stats(self):
        """
        Get cache statistics
        
        Returns:
        --------
        dict
            Cache statistics
        """
        cached = self.list_cached_series()
        
        if not cached:
            return {
                'total_series': 0,
                'valid_series': 0,
                'expired_series': 0,
                'total_size_mb': 0,
                'by_frequency': {},
                'oldest_cache': None,
                'newest_cache': None
            }
        
        # Calculate total cache size
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.pkl"))
        total_size += sum(f.stat().st_size for f in self.metadata_dir.glob("*.json"))
        
        # Count by frequency
        freq_counts = {}
        for item in cached:
            freq = item['frequency']
            freq_counts[freq] = freq_counts.get(freq, 0) + 1
        
        return {
            'total_series': len(cached),
            'valid_series': sum(1 for item in cached if item['is_valid']),
            'expired_series': sum(1 for item in cached if not item['is_valid']),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_frequency': freq_counts,
            'oldest_cache': min(cached, key=lambda x: x['cached_at'])['cached_at'] if cached else None,
            'newest_cache': max(cached, key=lambda x: x['cached_at'])['cached_at'] if cached else None
        }
    
    def print_cache_info(self):
        """Print formatted cache information"""
        stats = self.get_cache_stats()
        
        print("="*60)
        print("CACHE STATISTICS")
        print("="*60)
        print(f"Total cached series: {stats['total_series']}")
        print(f"Valid caches: {stats['valid_series']}")
        print(f"Expired caches: {stats['expired_series']}")
        print(f"Total cache size: {stats['total_size_mb']} MB")
        
        if stats['by_frequency']:
            print("\nBy frequency:")
            for freq, count in sorted(stats['by_frequency'].items()):
                duration = self.CACHE_DURATIONS[freq]
                print(f"  {freq}: {count} series (refresh every {duration}h)")
        
        if stats['oldest_cache']:
            print(f"\nOldest cache: {stats['oldest_cache']}")
            print(f"Newest cache: {stats['newest_cache']}")
        
        # List expired series if any
        cached = self.list_cached_series()
        expired = [item for item in cached if not item['is_valid']]
        
        if expired:
            print(f"\n⚠️  {len(expired)} expired series need refresh:")
            for item in expired[:10]:  # Show first 10
                age_hours = int(item['age_hours'])
                print(f"  - {item['series_id']} (age: {age_hours}h, frequency: {item['frequency']})")
            if len(expired) > 10:
                print(f"  ... and {len(expired) - 10} more")


if __name__ == "__main__":
    # Test the cache manager
    from pathlib import Path
    
    # Use project cache directory
    project_root = Path(__file__).parent.parent.parent
    cache_dir = project_root / "data" / "cache"
    
    cache = DataCacheManager(cache_dir)
    
    print("Testing Data Cache Manager...")
    print()
    
    # Print current cache info
    cache.print_cache_info()
    
    print("\n" + "="*60)
    print("CACHED SERIES DETAILS")
    print("="*60)
    
    cached_series = cache.list_cached_series()
    if cached_series:
        for item in cached_series[:15]:  # Show first 15
            status = "✓ Valid" if item['is_valid'] else "✗ Expired"
            age_hours = int(item['age_hours'])
            print(f"\n{item['series_id']} ({status})")
            print(f"  Frequency: {item['frequency']} (refresh every {item['cache_duration_hours']}h)")
            print(f"  Age: {age_hours}h")
            print(f"  Data range: {item['start_date']} to {item['end_date']}")
            print(f"  Data points: {item['data_points']}")
        
        if len(cached_series) > 15:
            print(f"\n... and {len(cached_series) - 15} more series")
    else:
        print("No cached data found. Run data fetcher first.")
