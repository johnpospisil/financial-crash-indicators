# Interactive Features Guide

## Overview

The Recession Risk Dashboard now includes comprehensive interactive controls that allow you to customize visualizations, filter data, and export results for further analysis.

## New Features

### 1. Date Range Selector

**Location:** Core Indicators page

**Options:**

- 1 Year
- 3 Years
- 5 Years
- 10 Years
- All Data (default)

**Description:** Filter all charts on the page to show only data within the selected time period. This helps focus on recent trends or compare longer-term historical patterns.

### 2. Recession Shading Toggle

**Location:** Core Indicators page

**Description:** Turn on/off the red shaded regions that indicate NBER official recession periods. Useful for decluttering charts or focusing solely on indicator values without historical context.

**Default:** ON

### 3. Indicator Selection Checkboxes

#### Treasury Yields

**Location:** Core Indicators page

**Options:**

- 10-Year Treasury
- 2-Year Treasury
- 3-Month Treasury

**Description:** Show/hide specific yield curves to focus on particular maturities. The 10Y-2Y spread chart is always displayed.

**Default:** All selected

#### Credit Spreads

**Location:** Core Indicators page

**Options:**

- HY Spread (High Yield)
- BAA Spread
- BBB Spread

**Description:** Select which credit spread series to display. Useful for comparing specific credit quality levels or reducing chart complexity.

**Default:** All selected

### 4. Manual Data Refresh

**Location:** Overview (Home) page

**Button:** 🔄 Refresh Data (top-right corner)

**Description:** Force an immediate refresh of all economic data from FRED API, bypassing the cache. The timestamp updates to show when data was last refreshed.

**Use Cases:**

- Check for newly released economic data
- Ensure you have the absolute latest values
- Reset after API/data issues

**Note:** Cached data automatically refreshes based on indicator frequency (daily/weekly/monthly/quarterly)

### 5. CSV Data Export

#### Overview Page

**Buttons:**

- **Export Full Analysis**: Complete recession analysis with all indicators, scores, weights, and contributions
- **Export Breakdown**: Simplified indicator breakdown table

**File Format:** CSV with timestamp in filename  
**Example:** `recession_analysis_20260108_143052.csv`

#### Core Indicators Page

**Buttons:**

- **Export Treasury Data**: All treasury yield series and spreads
- **Export Labor Data**: Unemployment rate and Sahm Rule indicator
- **Export Credit Data**: All credit spread series

**File Format:** CSV with time series data

**Use Cases:**

- Import into Excel/Google Sheets for custom analysis
- Create custom visualizations
- Archive historical snapshots
- Share data with colleagues

## How to Use

### Filtering by Date Range

1. Navigate to the Core Indicators page
2. Select desired time range from the "Date Range" dropdown
3. All charts update automatically
4. Export buttons will export filtered data

### Customizing Charts

1. Use checkboxes to select which indicators to display
2. Toggle recession shading on/off as needed
3. Charts update in real-time as you make selections
4. All selections are independent for maximum flexibility

### Exporting Data

1. Click any export button
2. Browser will automatically download the CSV file
3. Open in your preferred spreadsheet application
4. Data includes all visible time periods and selected indicators

### Refreshing Data

1. Click the "Refresh Data" button on the Overview page
2. Wait for confirmation message
3. Navigate between pages to see updated values
4. Charts and risk scores reflect the latest data

## Technical Details

### Interactive Components

- **Dash Callbacks**: Real-time chart updates without page reload
- **Client-Side Storage**: Selections persist during session
- **Lazy Loading**: Data only refreshed when needed

### Export Formats

All exported CSV files include:

- Headers describing each column
- Date/timestamp information
- Properly formatted numeric values
- UTF-8 encoding for universal compatibility

### Performance

- Indicator filtering: Instant
- Date range changes: < 1 second
- Data refresh: 5-30 seconds (depending on FRED API response)
- CSV export: Instant

## Tips

1. **Compare Time Periods**: Use date range selector to zoom into specific periods (e.g., 2008 financial crisis, COVID-19 recession)

2. **Reduce Clutter**: Uncheck indicators you're not interested in to create cleaner, more focused charts

3. **Historical Analysis**: Turn off recession shading when analyzing pre-recession trends to avoid confirmation bias

4. **Regular Exports**: Export data weekly/monthly to track how risk scores evolve over time

5. **Refresh Timing**: Use manual refresh on economic data release days:
   - Treasury yields: Daily
   - Unemployment: First Friday of each month
   - GDP: End of each quarter

## Future Enhancements (Planned)

- Date range custom picker (select start/end dates)
- Save/load favorite indicator combinations
- Export to Excel with formatted sheets
- Comparison mode (overlay multiple time periods)
- Annotation tools for marking significant events

## Troubleshooting

**Charts not updating?**

- Check that at least one indicator is selected
- Try refreshing the page
- Clear browser cache if issues persist

**Export not working?**

- Check browser's download settings
- Ensure pop-ups/downloads are allowed
- Try a different browser

**Slow refresh?**

- Normal during high API load
- Some indicators update less frequently
- Check your internet connection

## Support

For issues or feature requests, please refer to the main README.md or contact the development team.

---

**Version**: 1.1  
**Last Updated**: January 8, 2026  
**Dashboard**: Recession Risk Monitoring System
