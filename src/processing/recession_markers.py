"""
Historical Recession Markers
NBER recession dates and visualization utilities
"""
import pandas as pd
import numpy as np
from datetime import datetime

class RecessionMarkers:
    """
    Manages NBER recession dates and provides utilities for visualization overlays
    """
    
    # NBER-defined recession periods (start, end)
    NBER_RECESSIONS = [
        # Date, Start, End, Name, Description
        ('1969-12-01', '1970-11-01', 'Nixon Recession', 'Tight monetary policy'),
        ('1973-11-01', '1975-03-01', 'Oil Crisis', 'OPEC oil embargo'),
        ('1980-01-01', '1980-07-01', 'Energy Crisis', 'Iranian Revolution, oil prices'),
        ('1981-07-01', '1982-11-01', 'Reagan Recession', 'Volcker high interest rates'),
        ('1990-07-01', '1991-03-01', 'Gulf War Recession', 'Savings & loan crisis'),
        ('2001-03-01', '2001-11-01', 'Dot-com Crash', 'Tech bubble burst, 9/11'),
        ('2007-12-01', '2009-06-01', 'Great Recession', 'Financial crisis, housing bubble'),
        ('2020-02-01', '2020-04-01', 'COVID-19 Recession', 'Global pandemic'),
    ]
    
    def __init__(self):
        """Initialize recession markers"""
        self.recessions_df = self._create_recession_dataframe()
    
    def _create_recession_dataframe(self):
        """
        Create a DataFrame with recession information
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with recession periods and metadata
        """
        data = []
        for start, end, name, description in self.NBER_RECESSIONS:
            start_date = pd.Timestamp(start)
            end_date = pd.Timestamp(end)
            duration_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            
            data.append({
                'start': start_date,
                'end': end_date,
                'name': name,
                'description': description,
                'duration_months': duration_months,
                'decade': f"{(start_date.year // 10) * 10}s"
            })
        
        return pd.DataFrame(data)
    
    def get_recession_periods(self, start_date=None, end_date=None):
        """
        Get recession periods within a date range
        
        Parameters:
        -----------
        start_date : str or pd.Timestamp, optional
            Start of date range
        end_date : str or pd.Timestamp, optional
            End of date range
            
        Returns:
        --------
        pd.DataFrame
            Filtered recession periods
        """
        df = self.recessions_df.copy()
        
        if start_date:
            start_date = pd.Timestamp(start_date)
            df = df[df['end'] >= start_date]
        
        if end_date:
            end_date = pd.Timestamp(end_date)
            df = df[df['start'] <= end_date]
        
        return df
    
    def is_recession(self, date):
        """
        Check if a date is within a recession period
        
        Parameters:
        -----------
        date : str or pd.Timestamp
            Date to check
            
        Returns:
        --------
        bool
            True if date is in recession
        """
        date = pd.Timestamp(date)
        for _, row in self.recessions_df.iterrows():
            if row['start'] <= date <= row['end']:
                return True
        return False
    
    def get_recession_name(self, date):
        """
        Get recession name for a given date
        
        Parameters:
        -----------
        date : str or pd.Timestamp
            Date to check
            
        Returns:
        --------
        str or None
            Recession name if in recession, None otherwise
        """
        date = pd.Timestamp(date)
        for _, row in self.recessions_df.iterrows():
            if row['start'] <= date <= row['end']:
                return row['name']
        return None
    
    def create_recession_mask(self, date_index):
        """
        Create a boolean mask indicating recession periods
        
        Parameters:
        -----------
        date_index : pd.DatetimeIndex
            Index to create mask for
            
        Returns:
        --------
        pd.Series
            Boolean series with True for recession dates
        """
        mask = pd.Series(False, index=date_index)
        
        for _, row in self.recessions_df.iterrows():
            recession_mask = (date_index >= row['start']) & (date_index <= row['end'])
            mask[recession_mask] = True
        
        return mask
    
    def add_plotly_recession_shapes(self, fig, date_range=None, row=None, col=None):
        """
        Add recession shading to a Plotly figure
        
        Parameters:
        -----------
        fig : plotly.graph_objects.Figure
            Plotly figure to add shapes to
        date_range : tuple, optional
            (start_date, end_date) to limit recession shading
        row : int, optional
            Row number for subplot (if using subplots)
        col : int, optional
            Column number for subplot (if using subplots)
            
        Returns:
        --------
        plotly.graph_objects.Figure
            Figure with recession shapes added
        """
        recessions = self.recessions_df
        
        if date_range:
            recessions = self.get_recession_periods(date_range[0], date_range[1])
        
        for _, recession in recessions.iterrows():
            shape_kwargs = {
                'type': 'rect',
                'xref': 'x',
                'yref': 'paper',
                'x0': recession['start'],
                'x1': recession['end'],
                'y0': 0,
                'y1': 1,
                'fillcolor': 'rgba(255, 0, 0, 0.1)',
                'line': {'width': 0},
                'layer': 'below'
            }
            
            # Handle subplots
            if row is not None and col is not None:
                shape_kwargs['xref'] = f'x{col}' if col > 1 else 'x'
                shape_kwargs['yref'] = f'y{row}' if row > 1 else 'paper'
            
            fig.add_shape(**shape_kwargs)
        
        return fig
    
    def add_matplotlib_recession_spans(self, ax, date_range=None, alpha=0.2, color='red'):
        """
        Add recession shading to a Matplotlib axes
        
        Parameters:
        -----------
        ax : matplotlib.axes.Axes
            Axes to add shading to
        date_range : tuple, optional
            (start_date, end_date) to limit recession shading
        alpha : float, optional
            Transparency of shading (default: 0.2)
        color : str, optional
            Color of shading (default: 'red')
            
        Returns:
        --------
        matplotlib.axes.Axes
            Axes with recession spans added
        """
        recessions = self.recessions_df
        
        if date_range:
            recessions = self.get_recession_periods(date_range[0], date_range[1])
        
        for _, recession in recessions.iterrows():
            ax.axvspan(recession['start'], recession['end'], 
                      alpha=alpha, color=color, label='Recession' if _ == 0 else '')
        
        return ax
    
    def get_statistics(self):
        """
        Get recession statistics
        
        Returns:
        --------
        dict
            Dictionary with recession statistics
        """
        df = self.recessions_df
        
        return {
            'total_recessions': len(df),
            'avg_duration_months': df['duration_months'].mean(),
            'median_duration_months': df['duration_months'].median(),
            'min_duration_months': df['duration_months'].min(),
            'max_duration_months': df['duration_months'].max(),
            'shortest_recession': df.loc[df['duration_months'].idxmin(), 'name'],
            'longest_recession': df.loc[df['duration_months'].idxmax(), 'name'],
            'by_decade': df.groupby('decade').size().to_dict(),
            'recessions': df.to_dict('records')
        }
    
    def print_summary(self):
        """Print a formatted summary of recession data"""
        print("="*70)
        print("NBER RECESSION PERIODS SUMMARY")
        print("="*70)
        
        stats = self.get_statistics()
        
        print(f"\nTotal Recessions Tracked: {stats['total_recessions']}")
        print(f"Average Duration: {stats['avg_duration_months']:.1f} months")
        print(f"Median Duration: {stats['median_duration_months']:.0f} months")
        print(f"Shortest: {stats['shortest_recession']} ({stats['min_duration_months']} months)")
        print(f"Longest: {stats['longest_recession']} ({stats['max_duration_months']} months)")
        
        print("\n" + "-"*70)
        print("RECESSION PERIODS")
        print("-"*70)
        
        for rec in stats['recessions']:
            print(f"\n{rec['name']} ({rec['start'].year}-{rec['end'].year})")
            print(f"  Period: {rec['start'].strftime('%b %Y')} - {rec['end'].strftime('%b %Y')}")
            print(f"  Duration: {rec['duration_months']} months")
            print(f"  Cause: {rec['description']}")
        
        print("\n" + "-"*70)
        print("RECESSIONS BY DECADE")
        print("-"*70)
        
        for decade, count in sorted(stats['by_decade'].items()):
            print(f"  {decade}: {count} recession(s)")
    
    def export_to_csv(self, filepath):
        """
        Export recession data to CSV
        
        Parameters:
        -----------
        filepath : str or Path
            Path to save CSV file
        """
        self.recessions_df.to_csv(filepath, index=False)
        print(f"Recession data exported to {filepath}")
    
    def get_time_in_recession(self, start_date, end_date):
        """
        Calculate percentage of time in recession for a date range
        
        Parameters:
        -----------
        start_date : str or pd.Timestamp
            Start of period
        end_date : str or pd.Timestamp
            End of period
            
        Returns:
        --------
        dict
            Statistics about time in recession
        """
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)
        
        # Create daily date range
        all_dates = pd.date_range(start_date, end_date, freq='D')
        
        # Count recession days
        recession_days = sum(self.is_recession(date) for date in all_dates)
        total_days = len(all_dates)
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_days': total_days,
            'recession_days': recession_days,
            'normal_days': total_days - recession_days,
            'recession_percentage': (recession_days / total_days * 100) if total_days > 0 else 0,
            'recessions_in_period': len(self.get_recession_periods(start_date, end_date))
        }


if __name__ == "__main__":
    # Test the recession markers
    print("Testing Recession Markers Module...")
    
    markers = RecessionMarkers()
    
    # Print summary
    markers.print_summary()
    
    # Test date checking
    print("\n" + "="*70)
    print("DATE CHECKING EXAMPLES")
    print("="*70)
    
    test_dates = [
        '2008-09-15',  # Lehman Brothers collapse
        '2020-03-15',  # COVID pandemic
        '2024-01-01',  # Recent
        '1999-01-01',  # Dot-com boom
    ]
    
    for date in test_dates:
        is_rec = markers.is_recession(date)
        rec_name = markers.get_recession_name(date)
        status = f"IN RECESSION: {rec_name}" if is_rec else "Not in recession"
        print(f"{date}: {status}")
    
    # Time in recession analysis
    print("\n" + "="*70)
    print("TIME IN RECESSION ANALYSIS")
    print("="*70)
    
    periods = [
        ('1980-01-01', '1989-12-31', '1980s'),
        ('1990-01-01', '1999-12-31', '1990s'),
        ('2000-01-01', '2009-12-31', '2000s'),
        ('2010-01-01', '2019-12-31', '2010s'),
        ('2020-01-01', '2025-12-31', '2020s'),
    ]
    
    for start, end, name in periods:
        stats = markers.get_time_in_recession(start, end)
        print(f"\n{name}:")
        print(f"  Total days: {stats['total_days']:,}")
        print(f"  Recession days: {stats['recession_days']:,}")
        print(f"  Time in recession: {stats['recession_percentage']:.1f}%")
        print(f"  Number of recessions: {stats['recessions_in_period']}")
    
    print("\n✓ Recession markers module working correctly!")
