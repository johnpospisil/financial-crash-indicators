import sys
sys.path.insert(0, '/Users/johnpospisil/Documents/GitHub/projects/financial_crash_indicators')

from web_app.components.data_loader import load_data, get_markers
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import timedelta

def filter_by_date_range(df, date_range):
    if date_range is None or date_range == 'all':
        return df
    end_date = df.index.max()
    if date_range == '1y':
        start_date = end_date - timedelta(days=365)
    elif date_range == '3y':
        start_date = end_date - timedelta(days=3*365)
    elif date_range == '5y':
        start_date = end_date - timedelta(days=5*365)
    elif date_range == '10y':
        start_date = end_date - timedelta(days=10*365)
    else:
        return df
    return df[df.index >= start_date]

def create_labor_market_chart(data, markers, date_range='all', show_recessions=True):
    lm = data['labor_market']
    lm_filtered = filter_by_date_range(lm, date_range)
    
    print(f"Filtered data shape: {lm_filtered.shape}")
    print(f"Filtered data columns: {list(lm_filtered.columns)}")
    print(f"UNRATE in columns: {'UNRATE' in lm_filtered.columns}")
    print(f"SAHM_Rule in columns: {'SAHM_Rule' in lm_filtered.columns}")
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Unemployment Rate', 'Sahm Rule Recession Indicator'),
        vertical_spacing=0.12
    )
    
    if 'UNRATE' in lm_filtered.columns:
        unrate_data = lm_filtered['UNRATE'].dropna()
        print(f"\nUNRATE data points: {len(unrate_data)}")
        print(f"UNRATE index type: {type(unrate_data.index)}")
        print(f"UNRATE first value: {unrate_data.iloc[0] if len(unrate_data) > 0 else 'None'}")
        print(f"UNRATE last value: {unrate_data.iloc[-1] if len(unrate_data) > 0 else 'None'}")
        
        fig.add_trace(
            go.Scatter(x=lm_filtered.index, y=lm_filtered['UNRATE'], mode='lines', name='Unemployment Rate',
                       line=dict(color='blue', width=2)),
            row=1, col=1
        )
    
    if 'SAHM_Rule' in lm_filtered.columns:
        sahm_data = lm_filtered['SAHM_Rule'].dropna()
        print(f"\nSAHM_Rule data points: {len(sahm_data)}")
        
        fig.add_trace(
            go.Scatter(x=lm_filtered.index, y=lm_filtered['SAHM_Rule'], mode='lines', name='Sahm Rule',
                       line=dict(color='red', width=3)),
            row=2, col=1
        )
    
    print(f"\nTotal traces in figure: {len(fig.data)}")
    return fig

data = load_data()
markers = get_markers()
fig = create_labor_market_chart(data, markers, 'all', True)
print("\nChart created successfully!")
