"""
Secondary Indicators page - GDP, consumer, LEI, PMI, housing
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from components.data_loader import load_data, get_markers, format_date

dash.register_page(__name__, path='/secondary-indicators', title='Secondary Indicators - Recession Dashboard')

def create_gdp_chart(data, markers):
    """Create GDP growth chart"""
    gdp = data['gdp']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=gdp.index, y=gdp['GDP_YoY_Growth'], mode='lines',
                             name='GDP YoY Growth', line=dict(color='green', width=2)))
    
    fig.add_hline(y=0, line_dash="dash", line_color="red",
                  annotation_text="Zero Growth", annotation_position="right")
    
    # Add recession shading
    recessions = markers.get_recession_periods(gdp.index.min(), gdp.index.max())
    for _, rec in recessions.iterrows():
        fig.add_vrect(x0=rec['start'], x1=rec['end'], fillcolor="red", opacity=0.1,
                      layer="below", line_width=0)
    
    fig.update_layout(
        title='Real GDP Growth (Year-over-Year)',
        xaxis_title='Date',
        yaxis_title='Growth Rate (%)',
        height=400,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_consumer_sentiment_chart(data, markers):
    """Create consumer sentiment chart"""
    consumer = data['consumer']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=consumer.index, y=consumer['UMich_Sentiment'], mode='lines',
                             name='U. Michigan Sentiment', line=dict(color='blue', width=2)))
    
    # Add recession shading
    recessions = markers.get_recession_periods(consumer.index.min(), consumer.index.max())
    for _, rec in recessions.iterrows():
        fig.add_vrect(x0=rec['start'], x1=rec['end'], fillcolor="red", opacity=0.1,
                      layer="below", line_width=0)
    
    fig.update_layout(
        title='Consumer Sentiment Index',
        xaxis_title='Date',
        yaxis_title='Index Value',
        height=400,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_lei_chart(data, markers):
    """Create LEI chart"""
    if 'lei' not in data or len(data['lei']) == 0:
        return go.Figure().add_annotation(
            text="LEI data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
    
    lei = data['lei']
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Leading Economic Index', 'LEI 6-Month Change'),
        vertical_spacing=0.12
    )
    
    # LEI level
    if 'LEI' in lei.columns:
        fig.add_trace(
            go.Scatter(x=lei.index, y=lei['LEI'], mode='lines', name='LEI',
                       line=dict(color='purple', width=2)),
            row=1, col=1
        )
    
    # LEI 6-month change
    if 'LEI_6M_Change' in lei.columns:
        fig.add_trace(
            go.Scatter(x=lei.index, y=lei['LEI_6M_Change'], mode='lines', name='6M Change',
                       line=dict(color='red', width=2)),
            row=2, col=1
        )
        
        fig.add_hline(y=-2.0, line_dash="dash", line_color="red", row=2, col=1,
                      annotation_text="Recession Signal (-2%)", annotation_position="right")
    
    # Add recession shading
    recessions = markers.get_recession_periods(lei.index.min(), lei.index.max())
    for _, rec in recessions.iterrows():
        fig.add_vrect(x0=rec['start'], x1=rec['end'], fillcolor="red", opacity=0.1,
                      layer="below", line_width=0, row=1, col=1)
        fig.add_vrect(x0=rec['start'], x1=rec['end'], fillcolor="red", opacity=0.1,
                      layer="below", line_width=0, row=2, col=1)
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Index Value", row=1, col=1)
    fig.update_yaxes(title_text="6M % Change", row=2, col=1)
    
    fig.update_layout(
        height=700,
        showlegend=True,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_pmi_chart(data, markers):
    """Create PMI chart"""
    if 'pmi' not in data or len(data['pmi']) == 0:
        return go.Figure().add_annotation(
            text="PMI data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
    
    pmi = data['pmi']
    
    fig = go.Figure()
    
    if 'ISM_PMI' in pmi.columns:
        fig.add_trace(go.Scatter(x=pmi.index, y=pmi['ISM_PMI'], mode='lines',
                                 name='ISM Manufacturing PMI', line=dict(color='brown', width=2)))
        
        fig.add_hline(y=50, line_dash="dash", line_color="black",
                      annotation_text="Expansion/Contraction Threshold (50)", annotation_position="right")
    
    # Add recession shading
    recessions = markers.get_recession_periods(pmi.index.min(), pmi.index.max())
    for _, rec in recessions.iterrows():
        fig.add_vrect(x0=rec['start'], x1=rec['end'], fillcolor="red", opacity=0.1,
                      layer="below", line_width=0)
    
    fig.update_layout(
        title='ISM Manufacturing PMI',
        xaxis_title='Date',
        yaxis_title='PMI Value',
        height=400,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_housing_chart(data, markers):
    """Create housing indicators chart"""
    housing = data['housing']
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Housing Starts', 'Building Permits', 'New Home Sales', 'Existing Home Sales'),
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    # Housing starts
    fig.add_trace(
        go.Scatter(x=housing.index, y=housing['Housing_Starts'], mode='lines',
                   name='Starts', line=dict(color='blue', width=2)),
        row=1, col=1
    )
    
    # Building permits
    fig.add_trace(
        go.Scatter(x=housing.index, y=housing['Building_Permits'], mode='lines',
                   name='Permits', line=dict(color='green', width=2)),
        row=1, col=2
    )
    
    # New home sales
    if 'New_Home_Sales' in housing.columns:
        fig.add_trace(
            go.Scatter(x=housing.index, y=housing['New_Home_Sales'], mode='lines',
                       name='New Sales', line=dict(color='orange', width=2)),
            row=2, col=1
        )
    
    # Existing home sales
    if 'Existing_Home_Sales' in housing.columns:
        fig.add_trace(
            go.Scatter(x=housing.index, y=housing['Existing_Home_Sales'], mode='lines',
                       name='Existing Sales', line=dict(color='purple', width=2)),
            row=2, col=2
        )
    
    # Add recession shading to all subplots
    recessions = markers.get_recession_periods(housing.index.min(), housing.index.max())
    for _, rec in recessions.iterrows():
        for row in [1, 2]:
            for col in [1, 2]:
                fig.add_vrect(x0=rec['start'], x1=rec['end'], fillcolor="red", opacity=0.1,
                              layer="below", line_width=0, row=row, col=col)
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=2)
    fig.update_yaxes(title_text="Thousands", row=1, col=1)
    fig.update_yaxes(title_text="Thousands", row=1, col=2)
    fig.update_yaxes(title_text="Thousands", row=2, col=1)
    fig.update_yaxes(title_text="Thousands", row=2, col=2)
    
    fig.update_layout(
        height=700,
        showlegend=False,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def layout():
    """Create the secondary indicators page layout"""
    
    try:
        data = load_data()
        markers = get_markers()
        
        # Get current values
        gdp = data['gdp']
        consumer = data['consumer']
        housing = data['housing']
        
        current_gdp = gdp['GDP_YoY_Growth'].dropna().iloc[-1]
        gdp_date = gdp['GDP_YoY_Growth'].dropna().index[-1]
        
        current_sentiment = consumer['UMich_Sentiment'].dropna().iloc[-1]
        sentiment_date = consumer['UMich_Sentiment'].dropna().index[-1]
        
    except Exception as e:
        return dbc.Container([
            dbc.Alert(f"Error loading data: {str(e)}", color="danger")
        ])
    
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("📊 Secondary Economic Indicators", className="mb-4"),
                html.P(
                    "Additional indicators that provide context and confirmation for recession signals.",
                    className="lead text-muted"
                ),
            ], width=12)
        ], className="mb-4"),
        
        # GDP and Consumer Sentiment Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("GDP Growth", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_gdp_chart(data, markers),
                            config={'displayModeBar': True, 'displaylogo': False}
                        ),
                        dbc.Alert([
                            html.Strong("Current: "),
                            f"{current_gdp:+.2f}% YoY (as of {format_date(gdp_date)})"
                        ], color="info", className="mt-2")
                    ])
                ], className="shadow-sm mb-4")
            ], lg=6, md=12),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Consumer Sentiment", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_consumer_sentiment_chart(data, markers),
                            config={'displayModeBar': True, 'displaylogo': False}
                        ),
                        dbc.Alert([
                            html.Strong("Current: "),
                            f"{current_sentiment:.1f} (as of {format_date(sentiment_date)})"
                        ], color="info", className="mt-2")
                    ])
                ], className="shadow-sm mb-4")
            ], lg=6, md=12)
        ]),
        
        # LEI Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Leading Economic Index (LEI)", className="mb-0")),
                    dbc.CardBody([
                        html.P(
                            "The Conference Board's LEI is a composite indicator designed to predict economic turning points. "
                            "A 6-month decline of more than 2% is a strong recession signal.",
                            className="text-muted"
                        ),
                        dcc.Graph(
                            figure=create_lei_chart(data, markers),
                            config={'displayModeBar': True, 'displaylogo': False}
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # PMI Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Manufacturing PMI", className="mb-0")),
                    dbc.CardBody([
                        html.P(
                            "The ISM Manufacturing PMI is a key gauge of manufacturing sector health. "
                            "Values below 50 indicate contraction.",
                            className="text-muted"
                        ),
                        dcc.Graph(
                            figure=create_pmi_chart(data, markers),
                            config={'displayModeBar': True, 'displaylogo': False}
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Housing Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Housing Market Indicators", className="mb-0")),
                    dbc.CardBody([
                        html.P(
                            "Housing starts, permits, and sales are leading indicators of economic activity. "
                            "Declines often precede broader economic slowdowns.",
                            className="text-muted"
                        ),
                        dcc.Graph(
                            figure=create_housing_chart(data, markers),
                            config={'displayModeBar': True, 'displaylogo': False}
                        ),
                        dbc.Alert([
                            html.Strong("Current Housing Indicators:"),
                            html.Br(),
                            *[
                                html.Span([
                                    f"{col.replace('_', ' ')}: {housing[col].dropna().iloc[-1]:.0f}K ",
                                    f"(as of {format_date(housing[col].dropna().index[-1])})",
                                    html.Br()
                                ])
                                for col in ['Housing_Starts', 'Building_Permits', 'New_Home_Sales', 'Existing_Home_Sales']
                                if col in housing.columns and len(housing[col].dropna()) > 0
                            ]
                        ], color="info", className="mt-3")
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ], fluid=True)
