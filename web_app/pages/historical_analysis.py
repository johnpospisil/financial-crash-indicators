"""
Historical Analysis page - Trend analysis and pre-recession comparisons
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats

from components.data_loader import load_data, get_markers

dash.register_page(__name__, path='/historical-analysis', title='Historical Analysis - Recession Dashboard')

def create_historical_comparison_chart(data, markers):
    """Create chart comparing current values to pre-recession averages"""
    recession_periods = markers.get_recession_periods(pd.Timestamp('1960-01-01'), pd.Timestamp('2025-12-31'))
    
    comparison_indicators = [
        ('treasury_yields', 'Spread_10Y2Y', '10Y-2Y Spread'),
        ('labor_market', 'UNRATE', 'Unemployment Rate'),
        ('labor_market', 'SAHM_Rule', 'Sahm Rule'),
        ('credit_spreads', 'BAA_Spread', 'BAA Spread'),
        ('gdp', 'GDP_YoY_Growth', 'GDP Growth (YoY)'),
        ('consumer', 'UMich_Sentiment', 'Consumer Sentiment'),
    ]
    
    current_vals = []
    pre_rec_vals = []
    indicator_names = []
    
    for category, indicator, name in comparison_indicators:
        if category not in data or indicator not in data[category].columns:
            continue
        
        series = data[category][indicator].dropna()
        
        if len(series) == 0:
            continue
        
        # Current value
        current_value = series.iloc[-1]
        
        # Calculate pre-recession averages
        pre_recession_values = []
        
        for _, rec in recession_periods.iterrows():
            rec_start = pd.Timestamp(rec['start'])
            pre_start = rec_start - pd.DateOffset(months=6)
            pre_end = rec_start
            
            pre_rec_data = series[(series.index >= pre_start) & (series.index < pre_end)]
            if len(pre_rec_data) > 0:
                pre_recession_values.append(pre_rec_data.mean())
        
        if len(pre_recession_values) > 0:
            avg_pre_recession = np.mean(pre_recession_values)
            
            current_vals.append(current_value)
            pre_rec_vals.append(avg_pre_recession)
            indicator_names.append(name)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Current',
        x=indicator_names,
        y=current_vals,
        marker_color='blue'
    ))
    
    fig.add_trace(go.Bar(
        name='Pre-Recession Avg',
        x=indicator_names,
        y=pre_rec_vals,
        marker_color='red'
    ))
    
    fig.update_layout(
        title='Current Indicators vs Pre-Recession Historical Averages',
        xaxis_title='Indicator',
        yaxis_title='Value',
        barmode='group',
        height=500,
        xaxis_tickangle=-45,
        margin=dict(l=50, r=50, t=80, b=120)
    )
    
    return fig

def create_trend_analysis_table(data):
    """Create trend analysis table"""
    trend_indicators = [
        ('treasury_yields', 'Spread_10Y2Y', '10Y-2Y Spread'),
        ('labor_market', 'UNRATE', 'Unemployment Rate'),
        ('credit_spreads', 'BAA_Spread', 'BAA Credit Spread'),
        ('gdp', 'GDP_YoY_Growth', 'GDP Growth'),
        ('consumer', 'UMich_Sentiment', 'Consumer Sentiment'),
    ]
    
    trend_data = []
    
    for category, indicator, name in trend_indicators:
        if category not in data or indicator not in data[category].columns:
            continue
        
        series = data[category][indicator].dropna()
        
        if len(series) == 0:
            continue
        
        # Get last 12 months of data
        cutoff_date = series.index[-1] - pd.DateOffset(months=12)
        recent_data = series[series.index >= cutoff_date]
        
        if len(recent_data) < 2:
            continue
        
        # Calculate trend
        x = np.arange(len(recent_data))
        y = recent_data.values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Annualized trend
        periods_per_year = 12 if len(recent_data) > 20 else 4
        annualized_trend = slope * periods_per_year
        
        # Volatility
        volatility = recent_data.std()
        
        # Current value
        current = recent_data.iloc[-1]
        
        # 12-month change
        change_12m = current - recent_data.iloc[0]
        
        # Trend direction
        if abs(annualized_trend) < volatility * 0.1:
            direction = '➡️ Flat'
        elif annualized_trend > 0:
            direction = '📈 Rising'
        else:
            direction = '📉 Falling'
        
        trend_data.append({
            'Indicator': name,
            'Current': current,
            '12M Change': change_12m,
            'Trend': direction,
            'Annualized Trend': annualized_trend,
            'Volatility': volatility,
            'R²': r_value**2
        })
    
    return pd.DataFrame(trend_data)

def layout():
    """Create the historical analysis page layout"""
    
    try:
        data = load_data()
        markers = get_markers()
        
        # Create trend analysis table
        trend_df = create_trend_analysis_table(data)
        
    except Exception as e:
        return dbc.Container([
            dbc.Alert(f"Error loading data: {str(e)}", color="danger")
        ])
    
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("📈 Historical Analysis", className="mb-4"),
                html.P(
                    "Compare current indicator values to historical pre-recession averages and analyze recent trends.",
                    className="lead text-muted"
                ),
            ], width=12)
        ], className="mb-4"),
        
        # Historical Comparison Chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Current vs Pre-Recession Averages", className="mb-0")),
                    dbc.CardBody([
                        html.P(
                            "This chart compares current indicator values to their average values in the 6 months "
                            "before each NBER recession start date. This provides context for whether current conditions "
                            "are similar to past pre-recession periods.",
                            className="text-muted"
                        ),
                        dcc.Graph(
                            figure=create_historical_comparison_chart(data, markers),
                            config={'displayModeBar': True, 'displaylogo': False}
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Trend Analysis Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("12-Month Trend Analysis", className="mb-0")),
                    dbc.CardBody([
                        html.P(
                            "Statistical analysis of recent trends and volatility over the past 12 months.",
                            className="text-muted mb-3"
                        ),
                        dbc.Table.from_dataframe(
                            trend_df.round({
                                'Current': 2,
                                '12M Change': 2,
                                'Annualized Trend': 2,
                                'Volatility': 2,
                                'R²': 3
                            }),
                            striped=True,
                            bordered=True,
                            hover=True,
                            responsive=True
                        ),
                        html.Div([
                            html.H6("Interpretation Guide:", className="mt-4 mb-2"),
                            html.Ul([
                                html.Li([
                                    html.Strong("📈 Rising: "),
                                    "Indicator trending upward over the past 12 months"
                                ]),
                                html.Li([
                                    html.Strong("📉 Falling: "),
                                    "Indicator trending downward over the past 12 months"
                                ]),
                                html.Li([
                                    html.Strong("➡️ Flat: "),
                                    "No significant trend detected"
                                ]),
                                html.Li([
                                    html.Strong("R²: "),
                                    "Strength of linear trend (1.0 = perfect linear trend, 0.0 = no trend)"
                                ]),
                                html.Li([
                                    html.Strong("Volatility (σ): "),
                                    "Standard deviation - higher values indicate more variability in the indicator"
                                ]),
                            ], className="small")
                        ], className="bg-light p-3 rounded")
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Key Insights
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Key Historical Insights", className="mb-0")),
                    dbc.CardBody([
                        html.Ul([
                            html.Li(
                                "Pre-recession averages are calculated from 6 months before each of the 8 NBER recessions from 1969-2020."
                            ),
                            html.Li(
                                "Rising unemployment and falling GDP growth are typical pre-recession patterns."
                            ),
                            html.Li(
                                "Credit spreads typically widen (increase) in the months leading up to recessions as financial stress builds."
                            ),
                            html.Li(
                                "The yield curve (10Y-2Y spread) historically inverts 6-18 months before recessions begin."
                            ),
                            html.Li(
                                "High R² values (>0.7) in trend analysis indicate strong, persistent directional movement."
                            ),
                        ])
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ], fluid=True)
