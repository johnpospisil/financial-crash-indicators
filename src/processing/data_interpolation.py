"""
Data Interpolation Module
Handles interpolation of missing data points, particularly for October 2025 government shutdown
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, Dict, List


def interpolate_october_2025(series: pd.Series, method='linear') -> Tuple[pd.Series, Dict]:
    """
    Interpolate missing October 2025 data points using linear interpolation.
    
    This function specifically handles data gaps from the October 2025 government shutdown
    that prevented collection of key economic indicators. It handles both:
    - Existing NaN values in October 2025
    - Completely missing October 2025 dates (for monthly series)
    
    Parameters:
    -----------
    series : pd.Series
        Time series data with DatetimeIndex, potentially containing NaN values in Oct 2025
        or missing October 2025 entirely
    method : str, default 'linear'
        Interpolation method. Currently only 'linear' is supported.
        
    Returns:
    --------
    interpolated_series : pd.Series
        Series with October 2025 values interpolated (either filled NaN or added missing dates)
    metadata : dict
        Dictionary containing:
        - 'estimated_dates': List of dates that were interpolated
        - 'estimation_method': Method used for interpolation
        - 'original_nan_count': Number of NaN values before interpolation
        - 'interpolated_count': Number of values that were interpolated
        - 'shutdown_affected': True if October 2025 data was affected
        
    Examples:
    ---------
    >>> import pandas as pd
    >>> dates = pd.date_range('2025-09-01', '2025-11-01', freq='MS')
    >>> data = pd.Series([4.4, np.nan, 4.6], index=dates)
    >>> interpolated, metadata = interpolate_october_2025(data)
    >>> print(interpolated.loc['2025-10-01'])
    4.5
    >>> print(metadata['estimated_dates'])
    [Timestamp('2025-10-01 00:00:00')]
    """
    
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Series must have a DatetimeIndex")
    
    # Create a copy to avoid modifying original
    interpolated_series = series.copy()
    
    # Track original NaN count
    original_nan_count = series.isna().sum()
    
    # Check if October 2025 is completely missing (for monthly series)
    has_sept_2025 = any((interpolated_series.index.year == 2025) & (interpolated_series.index.month == 9))
    has_nov_2025 = any((interpolated_series.index.year == 2025) & (interpolated_series.index.month == 11))
    has_oct_2025 = any((interpolated_series.index.year == 2025) & (interpolated_series.index.month == 10))
    
    # If we have Sept and Nov but missing Oct, add Oct date for monthly series
    if has_sept_2025 and has_nov_2025 and not has_oct_2025:
        # This is likely monthly data - add October 2025-10-01
        oct_date = pd.Timestamp('2025-10-01')
        interpolated_series.loc[oct_date] = np.nan
        interpolated_series = interpolated_series.sort_index()
    
    # Identify October 2025 dates with NaN values
    oct_2025_mask = (
        (interpolated_series.index.year == 2025) & 
        (interpolated_series.index.month == 10) &
        (interpolated_series.isna())
    )
    
    estimated_dates = interpolated_series.index[oct_2025_mask].tolist()
    
    # Perform linear interpolation for October 2025 gaps
    if len(estimated_dates) > 0:
        if method == 'linear':
            # Linear interpolation only for October 2025 gaps
            interpolated_series = interpolated_series.interpolate(
                method='linear',
                limit_area='inside'  # Only interpolate between valid values
            )
        else:
            raise ValueError(f"Unsupported interpolation method: {method}")
    
    # Count how many were actually interpolated
    interpolated_count = len(estimated_dates)
    
    # Build metadata
    metadata = {
        'estimated_dates': estimated_dates,
        'estimation_method': method,
        'original_nan_count': int(original_nan_count),
        'interpolated_count': interpolated_count,
        'shutdown_affected': True if interpolated_count > 0 else False
    }
    
    return interpolated_series, metadata


def interpolate_missing_data(series: pd.Series, 
                             date_range: Tuple[str, str] = None,
                             method: str = 'linear') -> Tuple[pd.Series, Dict]:
    """
    General-purpose interpolation for missing data in any date range.
    
    Parameters:
    -----------
    series : pd.Series
        Time series data with DatetimeIndex
    date_range : tuple of str, optional
        (start_date, end_date) to limit interpolation to specific period
        Format: 'YYYY-MM-DD'
    method : str, default 'linear'
        Interpolation method ('linear', 'time', 'polynomial', etc.)
        
    Returns:
    --------
    interpolated_series : pd.Series
        Series with interpolated values
    metadata : dict
        Information about the interpolation performed
    """
    
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Series must have a DatetimeIndex")
    
    interpolated_series = series.copy()
    original_nan_count = series.isna().sum()
    
    # If date range specified, only interpolate within that range
    if date_range:
        start_date, end_date = date_range
        
        # Get NaN dates within the specified range
        mask = (
            (interpolated_series.index >= start_date) & 
            (interpolated_series.index <= end_date) &
            (interpolated_series.isna())
        )
        estimated_dates = interpolated_series.index[mask].tolist()
        
        # To interpolate within range, we need values before and after
        # Expand the slice slightly to include boundary values if they exist
        try:
            # Find index positions
            start_idx = interpolated_series.index.get_loc(start_date)
            end_idx = interpolated_series.index.get_loc(end_date)
            
            # Expand to include one value before and after if available
            expanded_start = max(0, start_idx - 1)
            expanded_end = min(len(interpolated_series) - 1, end_idx + 1)
            
            # Get expanded slice
            range_series = interpolated_series.iloc[expanded_start:expanded_end + 1].copy()
            range_series = range_series.interpolate(method=method, limit_area='inside')
            
            # Update only the original date range values (not the expanded boundaries)
            for date in estimated_dates:
                if date in range_series.index:
                    interpolated_series.loc[date] = range_series.loc[date]
        except KeyError:
            # If exact dates not in index, use nearest
            range_series = interpolated_series.loc[start_date:end_date].copy()
            range_series = range_series.interpolate(method=method, limit_area='inside')
            interpolated_series.update(range_series)
    else:
        # Get all NaN dates before interpolation
        estimated_dates = interpolated_series.index[interpolated_series.isna()].tolist()
        
        # Interpolate all gaps
        interpolated_series = interpolated_series.interpolate(
            method=method,
            limit_area='inside'
        )
    
    final_nan_count = interpolated_series.isna().sum()
    interpolated_count = original_nan_count - final_nan_count
    
    metadata = {
        'estimated_dates': estimated_dates,
        'estimation_method': method,
        'original_nan_count': int(original_nan_count),
        'interpolated_count': int(interpolated_count),
        'date_range': date_range
    }
    
    return interpolated_series, metadata


def get_data_quality_flags(series: pd.Series, metadata: Dict) -> pd.Series:
    """
    Create a parallel series with data quality flags.
    
    Parameters:
    -----------
    series : pd.Series
        Original or interpolated time series
    metadata : dict
        Metadata from interpolation function containing 'estimated_dates'
        
    Returns:
    --------
    quality_flags : pd.Series
        Series with same index as input, values are 'actual' or 'estimated'
    """
    
    quality_flags = pd.Series('actual', index=series.index)
    
    estimated_dates = metadata.get('estimated_dates', [])
    for date in estimated_dates:
        if date in quality_flags.index:
            quality_flags.loc[date] = 'estimated'
    
    return quality_flags


def apply_confidence_interval(series: pd.Series, 
                              metadata: Dict,
                              margin: float = 0.2) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate confidence intervals around estimated data points.
    
    Parameters:
    -----------
    series : pd.Series
        Interpolated time series
    metadata : dict
        Metadata from interpolation containing 'estimated_dates'
    margin : float
        Confidence margin (±) to apply to estimated values
        
    Returns:
    --------
    upper_bound : pd.Series
        Upper confidence bound (NaN for actual data, value+margin for estimated)
    lower_bound : pd.Series
        Lower confidence bound (NaN for actual data, value-margin for estimated)
    """
    
    upper_bound = pd.Series(np.nan, index=series.index)
    lower_bound = pd.Series(np.nan, index=series.index)
    
    estimated_dates = metadata.get('estimated_dates', [])
    
    for date in estimated_dates:
        if date in series.index and not pd.isna(series.loc[date]):
            value = series.loc[date]
            upper_bound.loc[date] = value + margin
            lower_bound.loc[date] = value - margin
    
    return upper_bound, lower_bound
