"""
Data Quality Tracking Module
Tracks which data points are actual vs estimated/interpolated, particularly for October 2025 shutdown
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum


class DataQuality(Enum):
    """Data quality status enumeration"""
    ACTUAL = "actual"
    ESTIMATED = "estimated"
    INTERPOLATED = "interpolated"
    UNKNOWN = "unknown"


class DataQualityTracker:
    """
    Tracks data quality status for economic indicators.
    
    Maintains a registry of which data points are actual measurements vs
    estimated/interpolated values, particularly for the October 2025 
    government shutdown period.
    """
    
    # Series known to be affected by October 2025 shutdown
    OCTOBER_2025_AFFECTED_SERIES = {
        # Labor market indicators
        'UNRATE',
        'SAHMREALTIME',
        'SAHM_Rule',
        
        # Consumer indicators
        'PCE',
        'PCE_MoM',
        'PCE_YoY',
        'Consumer_Confidence',
        
        # Housing indicators
        'Housing_Starts',
        'Building_Permits',
        'New_Home_Sales',
        'Existing_Home_Sales',
        'Case_Shiller_Index',
        'ZHVI',
        'Mortgage_Rate',
    }
    
    def __init__(self):
        """Initialize the data quality tracker"""
        self._quality_registry: Dict[str, Dict[pd.Timestamp, DataQuality]] = {}
        self._interpolation_metadata: Dict[str, Dict] = {}
        
    def register_series(self, series_id: str, data: pd.Series, metadata: Optional[Dict] = None):
        """
        Register a data series and its quality status.
        
        Parameters:
        -----------
        series_id : str
            Identifier for the data series (e.g., 'UNRATE', 'PCE')
        data : pd.Series
            The data series with DatetimeIndex
        metadata : dict, optional
            Metadata from interpolation, containing 'estimated_dates', 'estimation_method', etc.
        """
        if series_id not in self._quality_registry:
            self._quality_registry[series_id] = {}
        
        # Mark all dates as actual by default
        for date in data.index:
            if pd.notna(data.loc[date]):
                self._quality_registry[series_id][pd.Timestamp(date)] = DataQuality.ACTUAL
        
        # Update with interpolated dates if metadata provided
        if metadata and 'estimated_dates' in metadata:
            for date in metadata['estimated_dates']:
                self._quality_registry[series_id][pd.Timestamp(date)] = DataQuality.INTERPOLATED
            
            # Store full metadata
            self._interpolation_metadata[series_id] = metadata
    
    def get_quality_status(self, series_id: str, date: pd.Timestamp) -> DataQuality:
        """
        Get the data quality status for a specific series and date.
        
        Parameters:
        -----------
        series_id : str
            Identifier for the data series
        date : pd.Timestamp or str
            Date to check (will be converted to Timestamp)
            
        Returns:
        --------
        DataQuality
            Quality status: ACTUAL, INTERPOLATED, or UNKNOWN
        """
        date = pd.Timestamp(date)
        
        if series_id in self._quality_registry:
            return self._quality_registry[series_id].get(date, DataQuality.UNKNOWN)
        
        return DataQuality.UNKNOWN
    
    def get_quality_flags(self, series_id: str, dates: pd.DatetimeIndex) -> pd.Series:
        """
        Get quality flags for a series across multiple dates.
        
        Parameters:
        -----------
        series_id : str
            Identifier for the data series
        dates : pd.DatetimeIndex
            Dates to check
            
        Returns:
        --------
        pd.Series
            Series with same index as dates, values are 'actual' or 'interpolated'
        """
        flags = []
        for date in dates:
            quality = self.get_quality_status(series_id, date)
            flags.append(quality.value)
        
        return pd.Series(flags, index=dates, name=f'{series_id}_quality')
    
    def get_estimated_dates(self, series_id: str) -> List[pd.Timestamp]:
        """
        Get all estimated/interpolated dates for a series.
        
        Parameters:
        -----------
        series_id : str
            Identifier for the data series
            
        Returns:
        --------
        list of pd.Timestamp
            All dates marked as estimated/interpolated
        """
        if series_id not in self._quality_registry:
            return []
        
        return [
            date for date, quality in self._quality_registry[series_id].items()
            if quality == DataQuality.INTERPOLATED
        ]
    
    def is_october_2025_affected(self, series_id: str) -> bool:
        """
        Check if a series was affected by October 2025 shutdown.
        
        Parameters:
        -----------
        series_id : str
            Identifier for the data series
            
        Returns:
        --------
        bool
            True if series is known to be affected by October 2025 shutdown
        """
        return series_id in self.OCTOBER_2025_AFFECTED_SERIES
    
    def get_interpolation_metadata(self, series_id: str) -> Dict:
        """
        Get full interpolation metadata for a series.
        
        Parameters:
        -----------
        series_id : str
            Identifier for the data series
            
        Returns:
        --------
        dict
            Metadata dictionary with keys like 'estimated_dates', 'estimation_method',
            'interpolated_count', etc. Returns empty dict if no metadata available.
        """
        return self._interpolation_metadata.get(series_id, {})
    
    def get_summary(self) -> pd.DataFrame:
        """
        Get a summary of data quality across all registered series.
        
        Returns:
        --------
        pd.DataFrame
            Summary with columns: series_id, total_points, actual_points, 
            interpolated_points, interpolation_rate
        """
        summary_data = []
        
        for series_id, quality_map in self._quality_registry.items():
            total = len(quality_map)
            actual = sum(1 for q in quality_map.values() if q == DataQuality.ACTUAL)
            interpolated = sum(1 for q in quality_map.values() if q == DataQuality.INTERPOLATED)
            
            summary_data.append({
                'series_id': series_id,
                'total_points': total,
                'actual_points': actual,
                'interpolated_points': interpolated,
                'interpolation_rate': f"{(interpolated/total*100):.2f}%" if total > 0 else "0%",
                'oct_2025_affected': self.is_october_2025_affected(series_id)
            })
        
        return pd.DataFrame(summary_data)
    
    def split_series_by_quality(self, series_id: str, data: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """
        Split a data series into actual and interpolated portions.
        
        Useful for visualization where you want to display actual data differently
        from interpolated data.
        
        Parameters:
        -----------
        series_id : str
            Identifier for the data series
        data : pd.Series
            The full data series
            
        Returns:
        --------
        actual_data : pd.Series
            Series containing only actual data points (interpolated points set to NaN)
        interpolated_data : pd.Series
            Series containing only interpolated data points (actual points set to NaN)
        """
        actual_data = data.copy()
        interpolated_data = pd.Series(index=data.index, dtype=float)
        
        for date in data.index:
            quality = self.get_quality_status(series_id, date)
            
            if quality == DataQuality.INTERPOLATED:
                interpolated_data.loc[date] = data.loc[date]
                actual_data.loc[date] = None
        
        return actual_data, interpolated_data
    
    def get_october_2025_status(self) -> Dict[str, Dict]:
        """
        Get comprehensive status of October 2025 data quality across all series.
        
        Returns:
        --------
        dict
            Dictionary mapping series_id to status info including whether interpolated,
            estimation method, and dates affected
        """
        oct_2025_status = {}
        
        for series_id in self._quality_registry.keys():
            # Check if any October 2025 dates are interpolated
            oct_dates = [
                date for date in self._quality_registry[series_id].keys()
                if date.year == 2025 and date.month == 10
            ]
            
            interpolated_oct = [
                date for date in oct_dates
                if self.get_quality_status(series_id, date) == DataQuality.INTERPOLATED
            ]
            
            if oct_dates or self.is_october_2025_affected(series_id):
                metadata = self.get_interpolation_metadata(series_id)
                oct_2025_status[series_id] = {
                    'has_oct_data': len(oct_dates) > 0,
                    'interpolated_oct_dates': interpolated_oct,
                    'interpolated_count': len(interpolated_oct),
                    'estimation_method': metadata.get('estimation_method', 'N/A'),
                    'shutdown_affected': self.is_october_2025_affected(series_id)
                }
        
        return oct_2025_status


# Global tracker instance
_global_tracker = DataQualityTracker()


def get_global_tracker() -> DataQualityTracker:
    """Get the global data quality tracker instance"""
    return _global_tracker


def register_series_quality(series_id: str, data: pd.Series, metadata: Optional[Dict] = None):
    """
    Convenience function to register series quality with global tracker.
    
    Parameters:
    -----------
    series_id : str
        Identifier for the data series
    data : pd.Series
        The data series
    metadata : dict, optional
        Interpolation metadata
    """
    _global_tracker.register_series(series_id, data, metadata)


def get_data_quality_status(series_id: str, date) -> str:
    """
    Convenience function to get quality status from global tracker.
    
    Parameters:
    -----------
    series_id : str
        Identifier for the data series
    date : pd.Timestamp or str
        Date to check
        
    Returns:
    --------
    str
        Quality status: 'actual', 'interpolated', or 'unknown'
    """
    return _global_tracker.get_quality_status(series_id, date).value
