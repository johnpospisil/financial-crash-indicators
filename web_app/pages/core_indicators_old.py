"""
Core Indicators page - Treasury yields, labor market, credit spreads
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

from components.data_loader import load_data, get_markers, format_date

dash.register_page(__name__, path='/core-indicators', title='Core Indicators - Recession Dashboard')

def create_treasury_yields_chart(data, markers, date_range=None, show_recessions=True):
    """Create treasury yields and spread chart"""
    ty = data['treasury_yields']
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Treasury Yields', '10Y-2Y Spread (Yield Curve)'),
        vertical_spacing=0.12,
        row_heights=[0.5, 0.5]
    )
    
    # Plot yields
    fig.add_trace(
        go.Scatter(x=ty.index, y=ty['DGS10'], mode='lines', name='10-Year',
                   line=dict(color='blue', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=ty.index, y=ty['DGS2'], mode='lines', name='2-Year',
                   line=dict(color='green', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=ty.index, y=ty['DGS3MO'], mode='lines', name='3-Month',
                   line=dict(color='orange', width=2)),
        row=1, col=1
    )
    
    # Plot spread
    fig.add_trace(
        go.Scatter(x=ty.index, y=ty['Spread_10Y2Y'], mode='lines', name='10Y-2Y Spread',
                   line=dict(color='purple', width=3)),
        row=2, col=1
    )
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=2, col=1,
                  annotation_text="Inversion Threshold", annotation_position="right")
    
    # Add recession shading
    recessions = markers.get_recession_periods(ty.index.min(), ty.index.max())
    for _, rec in recessions.iterrows():
        fig.add_vrect(x0=rec['start'], x1=rec['end'], fillcolor="red", opacity=0.1,
                      layer="below", line_width=0, row=1, col=1)
        fig.add_vrect(x0=rec['start'], x1=rec['end'], fillcolor="red", opacity=0.1,
                      layer="below", line_width=0, row=2, col=1)
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Yield (%)", row=1, col=1)
    fig.update_yaxes(title_text="Spread (%)", row=2, col=1)
    
    fig.update_layout(
        height=700,
        showlegend=True,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_labor_market_chart(data, markers):
    """Create labor market indicators chart"""
    lm = data['labor_market']
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Unemployment Rate', 'Sahm Rule Recession Indicator'),
        vertical_spacing=0.12
    )
    
    # Unemployment rate
    fig.add_trace(
        go.Scatter(x=lm.index, y=lm['UNRATE'], mode='lines', name='Unemployment Rate',
                   line=dict(color='blue', width=2)),
        row=1, col=1
    )
    
    # Sahm Rule
    fig.add_trace(
        go.Scatter(x=lm.index, y=lm['SAHM_Rule'], mode='lines', name='Sahm Rule',
                   line=dict(color='red', width=3)),
        row=2, col=1
    )
    
    # Add recession threshold
    fig.add_hline(y=0.5, line_dash="dash", line_color="red", row=2, col=1,
                  annotation_text="Recession Threshold (0.5)", annotation_position="right")
    
    # Add recession shading
    recessions = markers.get_recession_periods(lm.index.min(), lm.index.max())
    for _, rec in recessions.iterrows():
        fig.add_vrect(x0=rec['start'], x1=rec['end'], fillcolor="red", opacity=0.1,
                      layer="below", line_width=0, row=1, col=1)
        fig.add_vrect(x0=rec['start'], x1=rec['end'], fillcolor="red", opacity=0.1,
                      layer="below", line_width=0, row=2, col=1)
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Unemployment Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Sahm Rule Value", row=2, col=1)
    
    fig.update_layout(
        height=700,
        showlegend=True,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_credit_spreads_chart(data, markers):
    """Create credit spreads chart"""
    cs = data['credit_spreads']
    
    fig = go.Figure()
    
    # Plot available spreads
    if 'HY_Spread' in cs.columns:
        fig.add_trace(go.Scatter(x=cs.index, y=cs['HY_Spread'], mode='lines',
                                 name='High Yield Spread', line=dict(width=2)))
    
    if 'BAA_Spread' in cs.columns:
        fig.add_trace(go.Scatter(x=cs.index, y=cs['BAA_Spread'], mode='lines',
                                 name='BAA Spread', line=dict(width=2)))
    
    if 'BBB_Spread' in cs.columns:
        fig.add_trace(go.Scatter(x=cs.index, y=cs['BBB_Spread'], mode='lines',
                                 name='BBB Spread', line=dict(width=2)))
    
    # Add stress thresholds
    fig.add_hline(y=4.0, line_dash="dash", line_color="orange",
                  annotation_text="Elevated Stress (4%)", annotation_position="right")
    fig.add_hline(y=6.0, line_dash="dash", line_color="red",
                  annotation_text="Severe Stress (6%)", annotation_position="right")
    
    # Add recession shading
    recessions = markers.get_recession_periods(cs.index.min(), cs.index.max())
    for _, rec in recessions.iterrows():
        fig.add_vrect(x0=rec['start'], x1=rec['end'], fillcolor="red", opacity=0.1,
                      layer="below", line_width=0)
    
    fig.update_layout(
        title='Corporate Credit Spreads',
        xaxis_title='Date',
        yaxis_title='Spread (%)',
        height=500,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def layout():
    """Create the core indicators page layout"""
    
    try:
        data = load_data()
        markers = get_markers()
        
        # Get current values
        ty = data['treasury_yields']
        lm = data['labor_market']
        cs = data['credit_spreads']
        
        current_spread = ty['Spread_10Y2Y'].dropna().iloc[-1]
        spread_date = ty['Spread_10Y2Y'].dropna().index[-1]
        
        current_unrate = lm['UNRATE'].dropna().iloc[-1]
        current_sahm = lm['SAHM_Rule'].dropna().iloc[-1]
        sahm_date = lm['SAHM_Rule'].dropna().index[-1]
        
    except Exception as e:
        return dbc.Container([
            dbc.Alert(f"Error loading data: {str(e)}", color="danger")
        ])
    
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("📈 Core Recession Indicators", className="mb-4"),
                html.P(
                    "Key economic indicators with the strongest predictive power for recessions.",
                    className="lead text-muted"
                ),
            ], width=12)
        ], className="mb-4"),
        
        # Treasury Yields Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Treasury Yields & Yield Curve", className="mb-0")),
                    dbc.CardBody([
                        html.P(
                            "The yield curve is one of the most reliable recession predictors. "
                            "An inverted curve (negative 10Y-2Y spread) has preceded every recession since 1970.",
                            className="text-muted"
                        ),
                        dcc.Graph(
                            figure=create_treasury_yields_chart(data, markers),
                            config={'displayModeBar': True, 'displaylogo': False}
                        ),
                        dbc.Alert([
                            html.Strong("Current Status: "),
                            f"10Y-2Y Spread: {current_spread:+.2f}% (as of {format_date(spread_date)})",
                            html.Br(),
                            "⚠️ INVERTED - Historical recession signal!" if current_spread < 0 else "✅ Normal curve"
                        ], color="warning" if current_spread < 0 else "success", className="mt-3")
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Labor Market Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Labor Market Indicators", className="mb-0")),
                    dbc.CardBody([
                        html.P(
                            "The Sahm Rule recession indicator identifies economic downturns in real-time. "
                            "It triggers when the 3-month average unemployment rate rises 0.5 percentage points above its low in the prior 12 months.",
                            className="text-muted"
                        ),
                        dcc.Graph(
                            figure=create_labor_market_chart(data, markers),
                            config={'displayModeBar': True, 'displaylogo': False}
                        ),
                        dbc.Alert([
                            html.Strong("Current Status: "),
                            f"Unemployment Rate: {current_unrate:.1f}% | ",
                            f"Sahm Rule: {current_sahm:.2f} (as of {format_date(sahm_date)})",
                            html.Br(),
                            (
                                "🚨 RECESSION SIGNAL TRIGGERED!" if current_sahm >= 0.5 else
                                "⚠️ Approaching recession threshold" if current_sahm >= 0.3 else
                                "✅ Below recession threshold"
                            )
                        ], color="danger" if current_sahm >= 0.5 else "warning" if current_sahm >= 0.3 else "success", className="mt-3")
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Credit Spreads Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Corporate Credit Spreads", className="mb-0")),
                    dbc.CardBody([
                        html.P(
                            "Credit spreads measure the extra yield investors demand for corporate bonds over Treasury bonds. "
                            "Widening spreads indicate increasing financial stress and recession risk.",
                            className="text-muted"
                        ),
                        dcc.Graph(
                            figure=create_credit_spreads_chart(data, markers),
                            config={'displayModeBar': True, 'displaylogo': False}
                        ),
                        dbc.Alert([
                            html.Strong("Current Spreads: "),
                            html.Br(),
                            *[
                                html.Span([
                                    f"{col.replace('_', ' ')}: {cs[col].dropna().iloc[-1]:.2f}% ",
                                    f"(as of {format_date(cs[col].dropna().index[-1])})",
                                    html.Br()
                                ])
                                for col in ['HY_Spread', 'BAA_Spread', 'BBB_Spread']
                                if col in cs.columns
                            ]
                        ], color="info", className="mt-3")
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ], fluid=True)
