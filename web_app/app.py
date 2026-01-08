"""
Recession Dashboard Web Application
Multi-page Dash application for monitoring recession indicators
"""

import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# Initialize the Dash app with Bootstrap theme
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Recession Risk Dashboard"
)

# Server for deployment
server = app.server

# Navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Overview", href="/")),
        dbc.NavItem(dbc.NavLink("Core Indicators", href="/core-indicators")),
        dbc.NavItem(dbc.NavLink("Secondary Indicators", href="/secondary-indicators")),
        dbc.NavItem(dbc.NavLink("Historical Analysis", href="/historical-analysis")),
        dbc.NavItem(
            dbc.NavLink(
                [html.I(className="fas fa-sync-alt me-2"), "Refresh Data"],
                href="#",
                id="refresh-button",
                className="text-success"
            )
        ),
    ],
    brand="📊 Recession Risk Dashboard",
    brand_href="/",
    color="dark",
    dark=True,
    className="mb-4",
    fluid=True,
)

# Footer
footer = dbc.Container(
    dbc.Row(
        dbc.Col(
            html.Footer(
                [
                    html.Hr(),
                    html.P(
                        [
                            "Data Source: Federal Reserve Economic Data (FRED) | ",
                            "Recession Dates: NBER Official Periods | ",
                            f"Dashboard Version: 1.0"
                        ],
                        className="text-center text-muted small"
                    ),
                ],
                className="mt-5"
            ),
            width=12
        )
    ),
    fluid=True
)

# App layout with navigation and page content
app.layout = dbc.Container(
    [
        dcc.Location(id='url', refresh=False),
        navbar,
        dcc.Store(id='data-store'),  # Store for sharing data across pages
        dcc.Store(id='analysis-store'),  # Store for analysis results
        dcc.Interval(
            id='interval-component',
            interval=60*60*1000,  # Update every hour (in milliseconds)
            n_intervals=0,
            disabled=False
        ),
        dash.page_container,
        footer
    ],
    fluid=True,
    className="dbc"
)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
