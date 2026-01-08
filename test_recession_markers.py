"""
Test Historical Recession Markers and Visualization Overlays
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from processing.recession_markers import RecessionMarkers
from data_collection.fred_data_fetcher import FREDDataFetcher
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def test_recession_markers():
    """Test basic recession marker functionality"""
    print("="*70)
    print("TESTING RECESSION MARKERS")
    print("="*70)
    
    markers = RecessionMarkers()
    
    # Print summary
    markers.print_summary()
    
    return True

def test_date_checking():
    """Test recession date checking"""
    print("\n" + "="*70)
    print("TESTING DATE CHECKING")
    print("="*70)
    
    markers = RecessionMarkers()
    
    # Test known recession dates
    test_cases = [
        ('2008-10-01', True, 'Great Recession'),
        ('2020-03-15', True, 'COVID-19 Recession'),
        ('2019-01-01', False, None),
        ('1982-01-01', True, 'Reagan Recession'),
    ]
    
    passed = True
    for date, expected_recession, expected_name in test_cases:
        is_rec = markers.is_recession(date)
        rec_name = markers.get_recession_name(date)
        
        if is_rec == expected_recession:
            status = "✓"
        else:
            status = "✗"
            passed = False
        
        print(f"{status} {date}: Recession={is_rec}, Name={rec_name}")
    
    return passed

def test_time_analysis():
    """Test time in recession calculations"""
    print("\n" + "="*70)
    print("TESTING TIME IN RECESSION ANALYSIS")
    print("="*70)
    
    markers = RecessionMarkers()
    
    # Analyze the 2000s decade
    stats = markers.get_time_in_recession('2000-01-01', '2009-12-31')
    
    print(f"\n2000-2009 Decade Analysis:")
    print(f"  Total days: {stats['total_days']:,}")
    print(f"  Recession days: {stats['recession_days']:,}")
    print(f"  Time in recession: {stats['recession_percentage']:.1f}%")
    print(f"  Recessions: {stats['recessions_in_period']}")
    
    # Should have 2 recessions: Dot-com and Great Recession
    if stats['recessions_in_period'] == 2:
        print("  ✓ Correctly identified 2 recessions")
        return True
    else:
        print(f"  ✗ Expected 2 recessions, found {stats['recessions_in_period']}")
        return False

def test_plotly_visualization():
    """Test Plotly recession overlay"""
    print("\n" + "="*70)
    print("TESTING PLOTLY VISUALIZATION OVERLAY")
    print("="*70)
    
    try:
        # Fetch some data
        print("\nFetching unemployment data...")
        fetcher = FREDDataFetcher()
        data = fetcher.fetch_series('UNRATE', start_date='2000-01-01')
        
        # Create plot
        print("Creating plot with recession overlays...")
        markers = RecessionMarkers()
        
        fig = go.Figure()
        
        # Add data trace
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data.values,
            mode='lines',
            name='Unemployment Rate',
            line=dict(color='blue', width=2)
        ))
        
        # Add recession shading
        markers.add_plotly_recession_shapes(fig, date_range=(data.index.min(), data.index.max()))
        
        # Update layout
        fig.update_layout(
            title='Unemployment Rate with Recession Periods',
            xaxis_title='Date',
            yaxis_title='Unemployment Rate (%)',
            hovermode='x unified',
            height=500
        )
        
        # Save to HTML
        output_file = Path(__file__).parent / "test_recession_overlay.html"
        fig.write_html(str(output_file))
        print(f"✓ Visualization saved to {output_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multi_indicator_plot():
    """Test recession overlay on multiple indicators"""
    print("\n" + "="*70)
    print("TESTING MULTI-INDICATOR PLOT WITH RECESSIONS")
    print("="*70)
    
    try:
        print("\nFetching indicator data...")
        fetcher = FREDDataFetcher()
        
        # Fetch multiple indicators
        unrate = fetcher.fetch_series('UNRATE', start_date='2000-01-01')
        dgs10 = fetcher.fetch_series('DGS10', start_date='2000-01-01')
        dgs2 = fetcher.fetch_series('DGS2', start_date='2000-01-01')
        spread = dgs10 - dgs2
        
        print("Creating multi-panel visualization...")
        markers = RecessionMarkers()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Unemployment Rate', '10Y-2Y Treasury Spread'),
            vertical_spacing=0.12
        )
        
        # Add unemployment trace
        fig.add_trace(
            go.Scatter(x=unrate.index, y=unrate.values, 
                      mode='lines', name='Unemployment',
                      line=dict(color='blue')),
            row=1, col=1
        )
        
        # Add yield spread trace
        fig.add_trace(
            go.Scatter(x=spread.index, y=spread.values,
                      mode='lines', name='Yield Spread',
                      line=dict(color='green')),
            row=2, col=1
        )
        
        # Add recession shading to both subplots
        date_range = (unrate.index.min(), unrate.index.max())
        
        # For subplot 1
        recessions = markers.get_recession_periods(date_range[0], date_range[1])
        for _, recession in recessions.iterrows():
            # Top subplot
            fig.add_shape(
                type='rect',
                xref='x', yref='y',
                x0=recession['start'], x1=recession['end'],
                y0=0, y1=1,
                fillcolor='rgba(255, 0, 0, 0.15)',
                line=dict(width=0),
                layer='below',
                row=1, col=1
            )
            # Bottom subplot
            fig.add_shape(
                type='rect',
                xref='x2', yref='y2',
                x0=recession['start'], x1=recession['end'],
                y0=-10, y1=10,
                fillcolor='rgba(255, 0, 0, 0.15)',
                line=dict(width=0),
                layer='below',
                row=2, col=1
            )
        
        # Add horizontal line at 0 for yield spread
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
        
        # Update layout
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Unemployment Rate (%)", row=1, col=1)
        fig.update_yaxes(title_text="Spread (%)", row=2, col=1)
        
        fig.update_layout(
            title='Key Recession Indicators with Historical Recession Periods',
            showlegend=True,
            height=700,
            hovermode='x unified'
        )
        
        # Save
        output_file = Path(__file__).parent / "test_multi_indicator_recession.html"
        fig.write_html(str(output_file))
        print(f"✓ Multi-indicator visualization saved to {output_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recession_mask():
    """Test creating recession boolean mask"""
    print("\n" + "="*70)
    print("TESTING RECESSION MASK CREATION")
    print("="*70)
    
    try:
        markers = RecessionMarkers()
        
        # Create a date range
        dates = pd.date_range('2007-01-01', '2010-12-31', freq='M')
        
        # Create mask
        mask = markers.create_recession_mask(dates)
        
        print(f"\nDate range: {dates.min()} to {dates.max()}")
        print(f"Total months: {len(dates)}")
        print(f"Recession months: {mask.sum()}")
        print(f"Percentage in recession: {mask.sum() / len(dates) * 100:.1f}%")
        
        # Show some examples
        print("\nSample dates:")
        for i in [0, len(dates)//2, -1]:
            date = dates[i]
            in_rec = mask.iloc[i]
            status = "✓ Recession" if in_rec else "✗ Normal"
            print(f"  {date.strftime('%Y-%m')}: {status}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("HISTORICAL RECESSION MARKERS TEST SUITE")
    print("="*70)
    
    # Run tests
    results = []
    
    results.append(("Recession Markers", test_recession_markers()))
    results.append(("Date Checking", test_date_checking()))
    results.append(("Time Analysis", test_time_analysis()))
    results.append(("Recession Mask", test_recession_mask()))
    results.append(("Plotly Visualization", test_plotly_visualization()))
    results.append(("Multi-Indicator Plot", test_multi_indicator_plot()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        print("\n✨ Features:")
        print("  • NBER recession period database (1969-2020)")
        print("  • Recession date checking and lookup")
        print("  • Time-in-recession analysis")
        print("  • Plotly visualization overlays")
        print("  • Matplotlib visualization support")
        print("  • Boolean mask generation for filtering")
        print("\n📊 Generated Visualizations:")
        print("  • test_recession_overlay.html - Single indicator with recessions")
        print("  • test_multi_indicator_recession.html - Multiple indicators")
        print("\nReady for Prompt 8 (Jupyter notebook dashboard)!")
    else:
        print("\n⚠️ Some tests failed. Check errors above.")
