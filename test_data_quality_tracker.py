"""Test Step 3: Data Quality Tracking System"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from src.processing.data_quality_tracker import (
    DataQualityTracker,
    DataQuality,
    get_global_tracker,
    register_series_quality,
    get_data_quality_status
)


class TestDataQualityTracker:
    """Test DataQualityTracker class"""
    
    def test_register_series_all_actual(self):
        """Test registering a series with all actual data"""
        tracker = DataQualityTracker()
        
        dates = pd.date_range('2025-01-01', '2025-03-01', freq='MS')
        data = pd.Series([100, 105, 110], index=dates)
        
        tracker.register_series('TEST_SERIES', data)
        
        # All should be marked as actual
        for date in dates:
            assert tracker.get_quality_status('TEST_SERIES', date) == DataQuality.ACTUAL
    
    def test_register_series_with_interpolation(self):
        """Test registering a series with interpolated data"""
        tracker = DataQualityTracker()
        
        dates = pd.date_range('2025-09-01', '2025-11-01', freq='MS')
        data = pd.Series([4.4, 4.5, 4.6], index=dates)
        
        metadata = {
            'estimated_dates': [pd.Timestamp('2025-10-01')],
            'estimation_method': 'linear',
            'interpolated_count': 1
        }
        
        tracker.register_series('UNRATE', data, metadata)
        
        # Check quality status
        assert tracker.get_quality_status('UNRATE', '2025-09-01') == DataQuality.ACTUAL
        assert tracker.get_quality_status('UNRATE', '2025-10-01') == DataQuality.INTERPOLATED
        assert tracker.get_quality_status('UNRATE', '2025-11-01') == DataQuality.ACTUAL
    
    def test_get_quality_flags(self):
        """Test getting quality flags for multiple dates"""
        tracker = DataQualityTracker()
        
        dates = pd.date_range('2025-09-01', '2025-11-01', freq='MS')
        data = pd.Series([4.4, 4.5, 4.6], index=dates)
        
        metadata = {
            'estimated_dates': [pd.Timestamp('2025-10-01')],
            'estimation_method': 'linear'
        }
        
        tracker.register_series('UNRATE', data, metadata)
        
        flags = tracker.get_quality_flags('UNRATE', dates)
        
        assert flags.loc['2025-09-01'] == 'actual'
        assert flags.loc['2025-10-01'] == 'interpolated'
        assert flags.loc['2025-11-01'] == 'actual'
    
    def test_get_estimated_dates(self):
        """Test getting list of estimated dates"""
        tracker = DataQualityTracker()
        
        dates = pd.date_range('2025-08-01', '2025-12-01', freq='MS')
        data = pd.Series([100, 101, 102, 103, 104], index=dates)
        
        metadata = {
            'estimated_dates': [pd.Timestamp('2025-10-01'), pd.Timestamp('2025-11-01')]
        }
        
        tracker.register_series('TEST', data, metadata)
        
        estimated = tracker.get_estimated_dates('TEST')
        
        assert len(estimated) == 2
        assert pd.Timestamp('2025-10-01') in estimated
        assert pd.Timestamp('2025-11-01') in estimated
    
    def test_october_2025_affected(self):
        """Test checking if series is affected by October 2025 shutdown"""
        tracker = DataQualityTracker()
        
        assert tracker.is_october_2025_affected('UNRATE') == True
        assert tracker.is_october_2025_affected('PCE') == True
        assert tracker.is_october_2025_affected('SAHM_Rule') == True
        assert tracker.is_october_2025_affected('RANDOM_SERIES') == False
    
    def test_get_interpolation_metadata(self):
        """Test retrieving interpolation metadata"""
        tracker = DataQualityTracker()
        
        dates = pd.date_range('2025-09-01', '2025-11-01', freq='MS')
        data = pd.Series([4.4, 4.5, 4.6], index=dates)
        
        metadata = {
            'estimated_dates': [pd.Timestamp('2025-10-01')],
            'estimation_method': 'linear',
            'interpolated_count': 1,
            'shutdown_affected': True
        }
        
        tracker.register_series('UNRATE', data, metadata)
        
        retrieved = tracker.get_interpolation_metadata('UNRATE')
        
        assert retrieved['estimation_method'] == 'linear'
        assert retrieved['interpolated_count'] == 1
        assert retrieved['shutdown_affected'] == True
    
    def test_get_summary(self):
        """Test getting summary of all series"""
        tracker = DataQualityTracker()
        
        # Register multiple series
        dates = pd.date_range('2025-09-01', '2025-11-01', freq='MS')
        
        # Series 1: One interpolated point
        data1 = pd.Series([4.4, 4.5, 4.6], index=dates)
        metadata1 = {'estimated_dates': [pd.Timestamp('2025-10-01')]}
        tracker.register_series('UNRATE', data1, metadata1)
        
        # Series 2: All actual
        data2 = pd.Series([100, 105, 110], index=dates)
        tracker.register_series('OTHER', data2)
        
        summary = tracker.get_summary()
        
        assert len(summary) == 2
        assert summary[summary['series_id'] == 'UNRATE']['interpolated_points'].values[0] == 1
        assert summary[summary['series_id'] == 'OTHER']['interpolated_points'].values[0] == 0
    
    def test_split_series_by_quality(self):
        """Test splitting series into actual and interpolated portions"""
        tracker = DataQualityTracker()
        
        dates = pd.date_range('2025-09-01', '2025-11-01', freq='MS')
        data = pd.Series([4.4, 4.5, 4.6], index=dates)
        
        metadata = {
            'estimated_dates': [pd.Timestamp('2025-10-01')]
        }
        
        tracker.register_series('UNRATE', data, metadata)
        
        actual, interpolated = tracker.split_series_by_quality('UNRATE', data)
        
        # Actual should have Sept and Nov, Oct should be NaN
        assert actual.loc['2025-09-01'] == 4.4
        assert pd.isna(actual.loc['2025-10-01'])
        assert actual.loc['2025-11-01'] == 4.6
        
        # Interpolated should only have Oct
        assert pd.isna(interpolated.loc['2025-09-01'])
        assert interpolated.loc['2025-10-01'] == 4.5
        assert pd.isna(interpolated.loc['2025-11-01'])
    
    def test_get_october_2025_status(self):
        """Test getting comprehensive October 2025 status"""
        tracker = DataQualityTracker()
        
        dates = pd.date_range('2025-09-01', '2025-11-01', freq='MS')
        data = pd.Series([4.4, 4.5, 4.6], index=dates)
        
        metadata = {
            'estimated_dates': [pd.Timestamp('2025-10-01')],
            'estimation_method': 'linear'
        }
        
        tracker.register_series('UNRATE', data, metadata)
        
        oct_status = tracker.get_october_2025_status()
        
        assert 'UNRATE' in oct_status
        assert oct_status['UNRATE']['has_oct_data'] == True
        assert oct_status['UNRATE']['interpolated_count'] == 1
        assert oct_status['UNRATE']['estimation_method'] == 'linear'
        assert oct_status['UNRATE']['shutdown_affected'] == True


class TestGlobalTracker:
    """Test global tracker functions"""
    
    def test_register_and_retrieve_global(self):
        """Test registering and retrieving from global tracker"""
        dates = pd.date_range('2025-09-01', '2025-11-01', freq='MS')
        data = pd.Series([100, 101, 102], index=dates)
        
        metadata = {
            'estimated_dates': [pd.Timestamp('2025-10-01')]
        }
        
        register_series_quality('GLOBAL_TEST', data, metadata)
        
        # Should be able to retrieve
        status = get_data_quality_status('GLOBAL_TEST', '2025-10-01')
        assert status == 'interpolated'
        
        status_actual = get_data_quality_status('GLOBAL_TEST', '2025-09-01')
        assert status_actual == 'actual'


class TestIntegrationWithInterpolation:
    """Test integration with actual interpolation module"""
    
    def test_workflow_with_interpolation(self):
        """Test complete workflow: interpolate → register → check quality"""
        from src.processing.data_interpolation import interpolate_october_2025
        
        # Create data with October NaN
        dates = pd.date_range('2025-09-01', '2025-11-01', freq='MS')
        data = pd.Series([4.4, np.nan, 4.6], index=dates)
        
        # Interpolate
        interpolated, metadata = interpolate_october_2025(data)
        
        # Register with tracker
        tracker = DataQualityTracker()
        tracker.register_series('UNRATE', interpolated, metadata)
        
        # Check quality
        assert tracker.get_quality_status('UNRATE', '2025-10-01') == DataQuality.INTERPOLATED
        
        # Verify metadata
        retrieved_meta = tracker.get_interpolation_metadata('UNRATE')
        assert 'estimated_dates' in retrieved_meta
        assert len(retrieved_meta['estimated_dates']) == 1


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
    
    # Also run a quick demo
    print("\n" + "="*60)
    print("Step 3 Demo: Data Quality Tracking")
    print("="*60)
    
    tracker = DataQualityTracker()
    
    # Simulate UNRATE with October interpolated
    dates = pd.date_range('2025-09-01', '2025-11-01', freq='MS')
    unrate_data = pd.Series([4.4, 4.5, 4.6], index=dates)
    unrate_metadata = {
        'estimated_dates': [pd.Timestamp('2025-10-01')],
        'estimation_method': 'linear',
        'interpolated_count': 1
    }
    
    tracker.register_series('UNRATE', unrate_data, unrate_metadata)
    
    # Display results
    print("\nUNRATE Data Quality:")
    for date in dates:
        quality = tracker.get_quality_status('UNRATE', date)
        value = unrate_data.loc[date]
        print(f"  {date.strftime('%Y-%m-%d')}: {value:.1f} ({quality.value})")
    
    print("\nOctober 2025 Status:")
    oct_status = tracker.get_october_2025_status()
    for series, status in oct_status.items():
        print(f"  {series}:")
        print(f"    Interpolated: {status['interpolated_count']} points")
        print(f"    Method: {status['estimation_method']}")
    
    print("\nSummary:")
    print(tracker.get_summary().to_string(index=False))
    print("="*60)
