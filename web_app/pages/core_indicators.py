"""
Core Indicators page - Treasury yields, labor market, credit spreads with interactive controls
"""

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import io
import base64

from web_app.components.data_loader import load_data, get_markers, format_date

dash.register_page(__name__, path='/core-indicators', title='Core Indicators - Recession Dashboard')

def filter_by_date_range(df, date_range):
    """Filter dataframe by date range"""
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

def create_treasury_yields_chart(data, markers, date_range='all', show_recessions=True, selected_indicators=None):
    """Create treasury yields and spread chart"""
    ty = data['treasury_yields']
    ty_filtered = filter_by_date_range(ty, date_range)
    
    if selected_indicators is None:
        selected_indicators = ['DGS10', 'DGS2', 'DGS3MO']
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Treasury Yields', '10Y-2Y Spread (Yield Curve)'),
        vertical_spacing=0.12,
        row_heights=[0.5, 0.5]
    )
    
    # Plot yields
    if 'DGS10' in selected_indicators and 'DGS10' in ty_filtered.columns:
        fig.add_trace(
            go.Scatter(x=ty_filtered.index, y=ty_filtered['DGS10'], mode='lines', name='10-Year',
                       line=dict(color='blue', width=2)),
            row=1, col=1
        )
    if 'DGS2' in selected_indicators and 'DGS2' in ty_filtered.columns:
        fig.add_trace(
            go.Scatter(x=ty_filtered.index, y=ty_filtered['DGS2'], mode='lines', name='2-Year',
                       line=dict(color='green', width=2)),
            row=1, col=1
        )
    if 'DGS3MO' in selected_indicators and 'DGS3MO' in ty_filtered.columns:
        fig.add_trace(
            go.Scatter(x=ty_filtered.index, y=ty_filtered['DGS3MO'], mode='lines', name='3-Month',
                       line=dict(color='orange', width=2)),
            row=1, col=1
        )
    
    # Plot spread
    if 'Spread_10Y2Y' in ty_filtered.columns:
        fig.add_trace(
            go.Scatter(x=ty_filtered.index, y=ty_filtered['Spread_10Y2Y'], mode='lines', name='10Y-2Y Spread',
                       line=dict(color='purple', width=3)),
            row=2, col=1
        )
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=2, col=1,
                  annotation_text="Inversion Threshold", annotation_position="right")
    
    # Add recession shading
    if show_recessions:
        recessions = markers.get_recession_periods(ty_filtered.index.min(), ty_filtered.index.max())
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

def create_labor_market_chart(data, markers, date_range='all', show_recessions=True):
    """Create labor market indicators chart"""
    lm = data['labor_market']
    lm_filtered = filter_by_date_range(lm, date_range)
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Unemployment Rate', 'Sahm Rule Recession Indicator'),
        vertical_spacing=0.12
    )
    
    # Unemployment rate
    if 'UNRATE' in lm_filtered.columns:
        fig.add_trace(
            go.Scatter(x=lm_filtered.index, y=lm_filtered['UNRATE'], mode='lines', name='Unemployment Rate',
                       line=dict(color='blue', width=2)),
            row=1, col=1
        )
    
    # Sahm Rule
    if 'SAHM_Rule' in lm_filtered.columns:
        fig.add_trace(
            go.Scatter(x=lm_filtered.index, y=lm_filtered['SAHM_Rule'], mode='lines', name='Sahm Rule',
                       line=dict(color='red', width=3)),
            row=2, col=1
        )
    
    # Add recession threshold
    fig.add_hline(y=0.5, line_dash="dash", line_color="red", row=2, col=1,
                  annotation_text="Recession Threshold (0.5)", annotation_position="right")
    
    # Add recession shading
    if show_recessions:
        recessions = markers.get_recession_periods(lm_filtered.index.min(), lm_filtered.index.max())
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

def create_credit_spreads_chart(data, markers, date_range='all', show_recessions=True, selected_spreads=None):
    """Create credit spreads chart"""
    cs = data['credit_spreads']
    cs_filtered = filter_by_date_range(cs, date_range)
    
    if selected_spreads is None:
        selected_spreads = ['HY_Spread', 'BAA_Spread', 'BBB_Spread']
    
    fig = go.Figure()
    
    # Plot available spreads
    if 'HY_Spread' in selected_spreads and 'HY_Spread' in cs_filtered.columns:
        fig.add_trace(go.Scatter(x=cs_filtered.index, y=cs_filtered['HY_Spread'], mode='lines',
                                 name='High Yield Spread', line=dict(width=2)))
    
    if 'BAA_Spread' in selected_spreads and 'BAA_Spread' in cs_filtered.columns:
        fig.add_trace(go.Scatter(x=cs_filtered.index, y=cs_filtered['BAA_Spread'], mode='lines',
                                 name='BAA Spread', line=dict(width=2)))
    
    if 'BBB_Spread' in selected_spreads and 'BBB_Spread' in cs_filtered.columns:
        fig.add_trace(go.Scatter(x=cs_filtered.index, y=cs_filtered['BBB_Spread'], mode='lines',
                                 name='BBB Spread', line=dict(width=2)))
    
    # Add stress thresholds
    fig.add_hline(y=4.0, line_dash="dash", line_color="orange",
                  annotation_text="Elevated Stress (4%)", annotation_position="right")
    fig.add_hline(y=6.0, line_dash="dash", line_color="red",
                  annotation_text="Severe Stress (6%)", annotation_position="right")
    
    # Add recession shading
    if show_recessions:
        recessions = markers.get_recession_periods(cs_filtered.index.min(), cs_filtered.index.max())
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
    """Page layout with interactive controls"""
    try:
        data = load_data()
        markers = get_markers()
        
        # Get latest values
        ty = data['treasury_yields']
        lm = data['labor_market']
        cs = data['credit_spreads']
        
        current_spread = ty['Spread_10Y2Y'].dropna().iloc[-1]
        spread_date = ty['Spread_10Y2Y'].dropna().index[-1]
        
        current_unrate = lm['UNRATE'].dropna().iloc[-1]
        current_sahm = lm['SAHM_Rule'].dropna().iloc[-1]
        sahm_date = lm['SAHM_Rule'].dropna().index[-1]
        
        return dbc.Container([
            html.H1("Core Recession Indicators", className="mt-4 mb-4"),
            
            # Control Panel
            dbc.Card([
                dbc.CardBody([
                    html.H5("Interactive Controls", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Date Range:", className="fw-bold"),
                            dcc.Dropdown(
                                id='core-date-range',
                                options=[
                                    {'label': '1 Year', 'value': '1y'},
                                    {'label': '3 Years', 'value': '3y'},
                                    {'label': '5 Years', 'value': '5y'},
                                    {'label': '10 Years', 'value': '10y'},
                                    {'label': 'All Data', 'value': 'all'}
                                ],
                                value='all',
                                clearable=False
                            )
                        ], md=3),
                        dbc.Col([
                            html.Label("Show Recessions:", className="fw-bold"),
                            dbc.Switch(
                                id='core-show-recessions',
                                value=True,
                                className="mt-2"
                            )
                        ], md=2),
                        dbc.Col([
                            html.Label("Treasury Yields:", className="fw-bold"),
                            dcc.Checklist(
                                id='core-treasury-indicators',
                                options=[
                                    {'label': ' 10-Year', 'value': 'DGS10'},
                                    {'label': ' 2-Year', 'value': 'DGS2'},
                                    {'label': ' 3-Month', 'value': 'DGS3MO'}
                                ],
                                value=['DGS10', 'DGS2', 'DGS3MO'],
                                inline=True
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Credit Spreads:", className="fw-bold"),
                            dcc.Checklist(
                                id='core-credit-spreads',
                                options=[
                                    {'label': ' HY', 'value': 'HY_Spread'},
                                    {'label': ' BAA', 'value': 'BAA_Spread'},
                                    {'label': ' BBB', 'value': 'BBB_Spread'}
                                ],
                                value=['HY_Spread', 'BAA_Spread', 'BBB_Spread'],
                                inline=True
                            )
                        ], md=3)
                    ])
                ])
            ], className="mb-4"),
            
            # Treasury Yields Section
            dbc.Card([
                dbc.CardBody([
                    html.H3("📈 Treasury Yields & Yield Curve"),
                    html.P([
                        "The yield curve (10Y-2Y spread) is one of the most reliable recession predictors. ",
                        "An inverted curve (negative spread) has preceded every recession since 1970."
                    ], className="text-muted"),
                    dbc.Alert([
                        html.Strong(f"Current 10Y-2Y Spread: {current_spread:+.2f}%"),
                        f" (as of {format_date(spread_date)})",
                        html.Br(),
                        html.Span("⚠️ INVERTED - Historical recession signal!" if current_spread < 0 else "✅ Normal curve",
                                 className="text-danger" if current_spread < 0 else "text-success")
                    ], color="warning" if current_spread < 0 else "success"),
                    dcc.Graph(id='core-treasury-chart'),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("📥 Export Treasury Data", id="export-treasury-btn", color="primary", size="sm")
                        ], width="auto"),
                        dcc.Download(id="download-treasury-data")
                    ], className="mt-2")
                ])
            ], className="mb-4"),
            
            # Labor Market Section
            dbc.Card([
                dbc.CardBody([
                    html.H3("👥 Labor Market Indicators"),
                    html.P([
                        "The Sahm Rule triggers when the 3-month average unemployment rate rises 0.5 percentage points ",
                        "above its low during the previous 12 months."
                    ], className="text-muted"),
                    dbc.Alert([
                        html.Strong(f"Current Unemployment: {current_unrate:.1f}%"),
                        html.Br(),
                        html.Strong(f"Sahm Rule: {current_sahm:.2f}"),
                        f" (as of {format_date(sahm_date)})",
                        html.Br(),
                        html.Span("🚨 RECESSION SIGNAL TRIGGERED!" if current_sahm >= 0.5 
                                 else "⚠️ Approaching recession threshold" if current_sahm >= 0.3
                                 else "✅ Below recession threshold",
                                 className="text-danger" if current_sahm >= 0.5
                                 else "text-warning" if current_sahm >= 0.3
                                 else "text-success")
                    ], color="danger" if current_sahm >= 0.5 else "warning" if current_sahm >= 0.3 else "success"),
                    dcc.Graph(id='core-labor-chart'),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("📥 Export Labor Data", id="export-labor-btn", color="primary", size="sm")
                        ], width="auto"),
                        dcc.Download(id="download-labor-data")
                    ], className="mt-2")
                ])
            ], className="mb-4"),
            
            # Credit Spreads Section
            dbc.Card([
                dbc.CardBody([
                    html.H3("💰 Corporate Credit Spreads"),
                    html.P([
                        "Credit spreads widen during times of financial stress. ",
                        "Spreads above 4% indicate elevated stress, while spreads above 6% suggest severe stress."
                    ], className="text-muted"),
                    dcc.Graph(id='core-credit-chart'),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("📥 Export Credit Data", id="export-credit-btn", color="primary", size="sm")
                        ], width="auto"),
                        dcc.Download(id="download-credit-data")
                    ], className="mt-2")
                ])
            ], className="mb-4"),
            
            # Hidden div to store data
            dcc.Store(id='core-data-store', data={
                'treasury': ty.to_json(date_format='iso'),
                'labor': lm.to_json(date_format='iso'),
                'credit': cs.to_json(date_format='iso')
            })
            
        ], fluid=True, className="px-4")
        
    except Exception as e:
        return dbc.Container([
            dbc.Alert([
                html.H4("Error Loading Data", className="alert-heading"),
                html.P(f"An error occurred while loading the core indicators: {str(e)}")
            ], color="danger", className="mt-4")
        ])

# Callbacks for interactivity
@callback(
    Output('core-treasury-chart', 'figure'),
    [Input('core-date-range', 'value'),
     Input('core-show-recessions', 'value'),
     Input('core-treasury-indicators', 'value')]
)
def update_treasury_chart(date_range, show_recessions, selected_indicators):
    """Update treasury chart based on controls"""
    try:
        data = load_data()
        markers = get_markers()
        return create_treasury_yields_chart(data, markers, date_range, show_recessions, selected_indicators)
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)

@callback(
    Output('core-labor-chart', 'figure'),
    [Input('core-date-range', 'value'),
     Input('core-show-recessions', 'value')]
)
def update_labor_chart(date_range, show_recessions):
    """Update labor chart based on controls"""
    try:
        data = load_data()
        markers = get_markers()
        return create_labor_market_chart(data, markers, date_range, show_recessions)
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)

@callback(
    Output('core-credit-chart', 'figure'),
    [Input('core-date-range', 'value'),
     Input('core-show-recessions', 'value'),
     Input('core-credit-spreads', 'value')]
)
def update_credit_chart(date_range, show_recessions, selected_spreads):
    """Update credit chart based on controls"""
    try:
        data = load_data()
        markers = get_markers()
        return create_credit_spreads_chart(data, markers, date_range, show_recessions, selected_spreads)
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)

@callback(
    Output("download-treasury-data", "data"),
    Input("export-treasury-btn", "n_clicks"),
    State('core-data-store', 'data'),
    prevent_initial_call=True
)
def export_treasury_data(n_clicks, data_json):
    """Export treasury data to CSV"""
    if n_clicks is None:
        return None
    
    df = pd.read_json(io.StringIO(data_json['treasury']))
    return dcc.send_data_frame(df.to_csv, "treasury_yields.csv")

@callback(
    Output("download-labor-data", "data"),
    Input("export-labor-btn", "n_clicks"),
    State('core-data-store', 'data'),
    prevent_initial_call=True
)
def export_labor_data(n_clicks, data_json):
    """Export labor data to CSV"""
    if n_clicks is None:
        return None
    
    df = pd.read_json(io.StringIO(data_json['labor']))
    return dcc.send_data_frame(df.to_csv, "labor_market.csv")

@callback(
    Output("download-credit-data", "data"),
    Input("export-credit-btn", "n_clicks"),
    State('core-data-store', 'data'),
    prevent_initial_call=True
)
def export_credit_data(n_clicks, data_json):
    """Export credit data to CSV"""
    if n_clicks is None:
        return None
    
    df = pd.read_json(io.StringIO(data_json['credit']))
    return dcc.send_data_frame(df.to_csv, "credit_spreads.csv")
