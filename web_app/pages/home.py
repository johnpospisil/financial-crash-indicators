"""
Overview page - Main dashboard with risk gauge and summary
"""

import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import io

from web_app.components.data_loader import load_data, load_analysis, get_markers, format_date

dash.register_page(__name__, path='/', title='Overview - Recession Dashboard')

# Global flag to force refresh
_force_refresh = False

def create_risk_gauge(score, risk_level, risk_color):
    """Create the main risk gauge visualization"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Recession Risk Score", 'font': {'size': 24}},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': risk_color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': 'rgba(0, 255, 0, 0.2)'},
                {'range': [25, 50], 'color': 'rgba(255, 255, 0, 0.2)'},
                {'range': [50, 75], 'color': 'rgba(255, 165, 0, 0.2)'},
                {'range': [75, 100], 'color': 'rgba(255, 0, 0, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        font={'size': 16},
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def create_contributions_chart(breakdown):
    """Create bar chart of indicator contributions"""
    # Sort by contribution
    sorted_items = sorted(breakdown.items(), key=lambda x: x[1]['contribution'], reverse=True)
    
    indicators = [item[1]['description'] for item in sorted_items]
    contributions = [item[1]['contribution'] for item in sorted_items]
    scores = [item[1]['score'] for item in sorted_items]
    signals = [item[1]['signal'] for item in sorted_items]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=contributions,
        y=indicators,
        orientation='h',
        marker=dict(
            color=scores,
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="Score", x=1.15)
        ),
        text=signals,
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Contribution: %{x:.1f}<br>Signal: %{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Indicator Contributions to Composite Score',
        xaxis_title='Contribution to Total Risk',
        yaxis_title='',
        height=400,
        showlegend=False,
        margin=dict(l=20, r=150, t=50, b=50)
    )
    
    return fig

def layout():
    """Create the overview page layout"""
    
    # Load data and analysis
    try:
        global _force_refresh
        data = load_data(force_refresh=_force_refresh)
        analysis = load_analysis(data, force_refresh=_force_refresh)
        _force_refresh = False  # Reset flag
        
        composite = analysis['composite']
        
        score = composite['composite_score']
        risk_level = composite['risk_level']
        risk_color = composite['risk_color']
        breakdown = composite['breakdown']
        
        # Determine badge color
        if score < 25:
            badge_color = 'success'
        elif score < 50:
            badge_color = 'warning'
        elif score < 75:
            badge_color = 'warning'
        else:
            badge_color = 'danger'
        
        # Get latest data info
        latest_date = max(df.index.max() for df in data.values())
        
    except Exception as e:
        return dbc.Container([
            dbc.Alert(
                f"Error loading data: {str(e)}",
                color="danger"
            )
        ])
    
    return dbc.Container([
        # Header with Refresh Button
        dbc.Row([
            dbc.Col([
                html.H1("📊 Recession Risk Dashboard", className="text-center mb-3"),
                html.P(
                    f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"Latest Data: {format_date(latest_date)}",
                    className="text-center text-muted",
                    id='home-last-updated'
                ),
            ], md=10),
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-sync me-2"), "Refresh Data"],
                    id='home-refresh-button',
                    color="primary",
                    size="sm",
                    className="mt-3"
                )
            ], md=2, className="text-end")
        ], className="mb-4"),
        
        # Risk Score Card
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("Current Recession Risk", className="text-center"),
                        html.H1(
                            f"{score:.1f}/100",
                            className="text-center display-3 fw-bold"
                        ),
                        html.H4(
                            dbc.Badge(risk_level, color=badge_color, className="p-3"),
                            className="text-center mt-3"
                        ),
                    ])
                ], className="shadow-sm mb-4")
            ], lg=4, md=12),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_risk_gauge(score, risk_level, risk_color),
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], lg=8, md=12)
        ]),
        
        # Indicator Breakdown
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Indicator Breakdown", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_contributions_chart(breakdown),
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Detailed Breakdown Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Detailed Indicator Analysis", className="mb-0")),
                    dbc.CardBody([
                        dbc.Table(
                            [
                                html.Thead(
                                    html.Tr([
                                        html.Th("Indicator"),
                                        html.Th("Current Signal"),
                                        html.Th("Score"),
                                        html.Th("Weight"),
                                        html.Th("Contribution"),
                                        html.Th("Risk Level"),
                                    ])
                                ),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(details['description']),
                                        html.Td(details['signal']),
                                        html.Td(f"{details['score']:.1f}/100"),
                                        html.Td(f"{details['weight']}%"),
                                        html.Td(f"{details['contribution']:.1f}"),
                                        html.Td(
                                            dbc.Badge(
                                                '🟢 Normal' if details['score'] < 25 else
                                                '🟡 Caution' if details['score'] < 50 else
                                                '🟠 Warning' if details['score'] < 75 else
                                                '🔴 Critical',
                                                color=(
                                                    'success' if details['score'] < 25 else
                                                    'warning' if details['score'] < 50 else
                                                    'warning' if details['score'] < 75 else
                                                    'danger'
                                                )
                                            )
                                        ),
                                    ])
                                    for indicator, details in sorted(
                                        breakdown.items(),
                                        key=lambda x: x[1]['contribution'],
                                        reverse=True
                                    )
                                ])
                            ],
                            striped=True,
                            bordered=True,
                            hover=True,
                            responsive=True
                        )
                    ])
                ], className="shadow-sm mb-4")
            ], width=12)
        ]),
        
        # Key Insights
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Key Insights", className="mb-0")),
                    dbc.CardBody([
                        html.Ul([
                            html.Li(
                                f"Composite recession risk score is {score:.1f}/100, "
                                f"indicating {risk_level.lower()} conditions."
                            ),
                            html.Li(
                                f"Top risk contributor: {max(breakdown.items(), key=lambda x: x[1]['contribution'])[1]['description']} "
                                f"(contributing {max(breakdown.items(), key=lambda x: x[1]['contribution'])[1]['contribution']:.1f} points)"
                            ),
                            html.Li(
                                f"{sum(1 for d in breakdown.values() if d['score'] >= 75)} indicators in critical range (75-100), "
                                f"{sum(1 for d in breakdown.values() if 50 <= d['score'] < 75)} in warning range (50-75)"
                            ),
                            html.Li(
                                "Navigate to 'Core Indicators' and 'Secondary Indicators' pages for detailed charts and trends."
                            ),
                        ])
                    ])
                ], className="shadow-sm")
            ], width=12)
        ]),
        
        # Export Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("📥 Export Data", className="mb-3"),
                        dbc.ButtonGroup([
                            dbc.Button("Export Full Analysis", id="export-full-btn", color="primary", size="sm"),
                            dbc.Button("Export Breakdown", id="export-breakdown-btn", color="secondary", size="sm"),
                        ])
                    ])
                ], className="shadow-sm mt-4")
            ], width=12)
        ]),
        
        # Download components
        dcc.Download(id="download-full-data"),
        dcc.Download(id="download-breakdown-data"),
        
        # Store data for export
        dcc.Store(id='home-analysis-store', data={
            'score': score,
            'risk_level': risk_level,
            'breakdown': {k: v for k, v in breakdown.items()}
        })
    ], fluid=True)

# Callback for refresh button
@callback(
    Output('home-last-updated', 'children'),
    Input('home-refresh-button', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    """Force refresh all data"""
    global _force_refresh
    _force_refresh = True
    latest_date = max(df.index.max() for df in load_data(force_refresh=True).values())
    return f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Latest Data: {format_date(latest_date)} | ✅ Data refreshed!"

# Callback for export full analysis
@callback(
    Output("download-full-data", "data"),
    Input("export-full-btn", "n_clicks"),
    prevent_initial_call=True
)
def export_full_analysis(n_clicks):
    """Export full analysis to CSV"""
    if n_clicks is None:
        return None
    
    data = load_data()
    analysis = load_analysis(data)
    composite = analysis['composite']
    breakdown = composite['breakdown']
    
    # Create export dataframe
    export_data = []
    for indicator, details in breakdown.items():
        export_data.append({
            'Indicator': details['description'],
            'Signal': details['signal'],
            'Score': details['score'],
            'Weight': details['weight'],
            'Contribution': details['contribution'],
            'Category': indicator.split('_')[0]  # Extract category
        })
    
    df = pd.DataFrame(export_data)
    df = df.sort_values('Contribution', ascending=False)
    
    # Add summary row
    summary = pd.DataFrame([{
        'Indicator': 'COMPOSITE SCORE',
        'Signal': composite['risk_level'],
        'Score': composite['composite_score'],
        'Weight': 100,
        'Contribution': composite['composite_score'],
        'Category': 'Summary'
    }])
    
    df = pd.concat([summary, df], ignore_index=True)
    
    return dcc.send_data_frame(df.to_csv, f"recession_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)

# Callback for export breakdown
@callback(
    Output("download-breakdown-data", "data"),
    Input("export-breakdown-btn", "n_clicks"),
    prevent_initial_call=True
)
def export_breakdown(n_clicks):
    """Export breakdown table to CSV"""
    if n_clicks is None:
        return None
    
    data = load_data()
    analysis = load_analysis(data)
    composite = analysis['composite']
    breakdown = composite['breakdown']
    
    # Create simplified breakdown
    export_data = []
    for indicator, details in sorted(breakdown.items(), key=lambda x: x[1]['contribution'], reverse=True):
        export_data.append({
            'Indicator': details['description'],
            'Current Signal': details['signal'],
            'Risk Score': f"{details['score']:.1f}/100",
            'Weight %': details['weight'],
            'Weighted Contribution': f"{details['contribution']:.1f}"
        })
    
    df = pd.DataFrame(export_data)
    
    return dcc.send_data_frame(df.to_csv, f"indicator_breakdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)
