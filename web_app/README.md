# Recession Risk Dashboard - Web Application

A multi-page Dash web application for monitoring recession risk indicators in real-time.

## Features

- **Overview Page**: Composite recession risk score with interactive gauge and detailed indicator breakdown
- **Core Indicators**: Treasury yields, labor market, and credit spreads with NBER recession overlays
- **Secondary Indicators**: GDP, consumer sentiment, LEI, PMI, and housing market indicators
- **Historical Analysis**: Trend analysis and comparison to pre-recession historical averages
- **Responsive Design**: Bootstrap-based layout that works on desktop and mobile
- **Auto-refresh**: Data automatically refreshes based on indicator update frequency

## Installation

1. **Install dependencies:**

   ```bash
   cd web_app
   pip install -r requirements.txt
   ```

2. **Set up FRED API key:**

   Make sure you have your FRED API key configured in the parent directory's `.env` file:

   ```
   FRED_API_KEY=your_api_key_here
   ```

## Running the Application

### Development Mode

```bash
cd web_app
python app.py
```

The dashboard will be available at `http://localhost:8050`

### Production Mode

Using Gunicorn (recommended for deployment):

```bash
cd web_app
gunicorn app:server --bind 0.0.0.0:8050 --workers 4
```

## Project Structure

```
web_app/
├── app.py                          # Main application file
├── requirements.txt                # Python dependencies
├── components/
│   ├── __init__.py
│   └── data_loader.py             # Shared data loading utilities
└── pages/
    ├── __init__.py
    ├── home.py                    # Overview page
    ├── core_indicators.py         # Core indicators page
    ├── secondary_indicators.py    # Secondary indicators page
    └── historical_analysis.py     # Historical analysis page
```

## Navigation

- **Overview**: Main dashboard with composite risk score and indicator breakdown
- **Core Indicators**: Detailed charts for yield curve, unemployment, and credit spreads
- **Secondary Indicators**: Additional economic indicators (GDP, consumer, LEI, PMI, housing)
- **Historical Analysis**: Trend analysis and pre-recession comparisons

## Data Sources

- **Federal Reserve Economic Data (FRED)**: All economic indicators
- **NBER**: Official recession period dates

## Technical Details

- **Framework**: Dash (Plotly)
- **Styling**: Bootstrap 5
- **Charting**: Plotly
- **Data Processing**: pandas, numpy
- **Statistical Analysis**: scipy

## Auto-Refresh Behavior

Data is cached based on indicator update frequency:

- Daily indicators (yields): 24 hours
- Weekly indicators (jobless claims): 7 days
- Monthly indicators (unemployment, PMI): 30 days
- Quarterly indicators (GDP): 90 days

The dashboard checks for new data on page load and automatically refreshes hourly.

## Customization

### Changing the Port

Edit `app.py` and modify the port in the last line:

```python
app.run_server(debug=True, host='0.0.0.0', port=YOUR_PORT)
```

### Adjusting Auto-Refresh Interval

Edit `app.py` and modify the `interval` property in the `dcc.Interval` component:

```python
dcc.Interval(
    id='interval-component',
    interval=YOUR_INTERVAL_IN_MILLISECONDS,
    ...
)
```

## Deployment

For deployment to cloud platforms (Heroku, Render, etc.), use the included `gunicorn` configuration.

Example Procfile for Heroku:

```
web: gunicorn app:server --bind 0.0.0.0:$PORT
```

## Troubleshooting

**Problem**: Import errors when running the app

**Solution**: Make sure you're running from the `web_app` directory and that the parent `src` directory is accessible.

**Problem**: Data not loading

**Solution**: Verify your FRED API key is set correctly and you have internet connectivity.

**Problem**: Slow initial load

**Solution**: First load fetches all data from FRED. Subsequent loads use cached data and are much faster.

## Version

Dashboard Version: 1.0

## License

Part of the Financial Crash Indicators project.
