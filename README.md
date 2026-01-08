# Financial Recession Indicators Dashboard

A comprehensive dashboard for monitoring key economic indicators that signal potential recessions.

## Project Structure

```
financial_crash_indicators/
├── data/                      # Data storage and cache
├── src/                       # Source code
│   ├── data_collection/      # Data fetching modules
│   ├── processing/           # Data processing and calculations
│   └── visualization/        # Chart and plot generation
├── web_app/                  # Web-based dashboard
├── notebooks/                # Jupyter notebooks
└── requirements.txt          # Python dependencies
```

## Setup

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd financial_crash_indicators
   ```

2. **Activate the tf virtual environment**

   ```bash
   source tf/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**

   - Copy `.env.example` to `.env`: `cp .env.example .env`
   - Get a free FRED API key (see [API Setup Guide](docs/API_SETUP_GUIDE.md))
   - Edit `.env` and add your FRED API key

   For detailed setup instructions, see [docs/API_SETUP_GUIDE.md](docs/API_SETUP_GUIDE.md)

## Indicators Tracked

### Core Indicators

- **Yield Curve** (10Y-2Y, 10Y-3M Treasury spreads)
- **Sahm Rule** & Unemployment Rate
- **Initial Jobless Claims** (4-week average)
- **Corporate Credit Spreads**

### Secondary Indicators

- Leading Economic Index (LEI)
- ISM Manufacturing PMI
- GDP Growth (quarterly)
- Consumer Confidence Index
- Housing Starts & Building Permits

## Usage

### Jupyter Notebook Dashboard

```bash
jupyter notebook notebooks/
```

### Web Dashboard (coming soon)

```bash
python web_app/app.py
```

## Data Sources

- **FRED** (Federal Reserve Economic Data): Economic indicators
- **Yahoo Finance**: Market data
- **NBER**: Recession dates

## License

MIT
