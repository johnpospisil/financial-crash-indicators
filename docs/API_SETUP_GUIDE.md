# API Setup Guide

This guide will walk you through obtaining the necessary API keys for the Recession Indicators Dashboard.

## FRED API Key (Required)

The Federal Reserve Economic Data (FRED) API is the primary data source for economic indicators.

### Step-by-Step Instructions:

1. **Create a FRED Account**
   - Go to https://fred.stlouisfed.org/
   - Click "My Account" in the top right
   - Click "Register" and fill out the registration form
   - Verify your email address

2. **Request an API Key**
   - Log in to your FRED account
   - Go to https://fredaccount.stlouisfed.org/apikeys
   - Click "Request API Key"
   - Fill out the form:
     - **API Key Name**: Recession Dashboard (or any name you prefer)
     - **Description**: Personal recession indicator monitoring
     - **Website URL**: Can leave blank or add your GitHub repo
     - **Redirect URL**: Leave blank
   - Agree to the terms and click "Request API key"

3. **Copy Your API Key**
   - Your API key will be displayed immediately
   - **Important**: Copy this key - you'll need it for configuration
   - The key format looks like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

4. **Add to Configuration**
   - Copy `.env.example` to `.env` in your project root:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and replace `your_fred_api_key_here` with your actual API key:
     ```
     FRED_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
     ```

### API Limits:

- **Rate Limit**: 120 requests per minute
- **Daily Limit**: Unlimited (for non-commercial use)
- **Cost**: FREE for personal and educational use

### Testing Your API Key:

After configuration, test your API key with this Python snippet:

```python
from fredapi import Fred
import os
from dotenv import load_dotenv

load_dotenv()
fred = Fred(api_key=os.getenv('FRED_API_KEY'))

# Test by fetching unemployment rate
try:
    data = fred.get_series('UNRATE', limit=5)
    print("API key is working!")
    print(data)
except Exception as e:
    print(f"Error: {e}")
    print("Check your API key configuration")
```

## Optional: Yahoo Finance (Already Configured)

The `yfinance` library doesn't require an API key. It's already included in the project and works automatically.

## Optional: Email Notifications (Future Enhancement)

If you want to set up email alerts (Prompt 15), you'll need:

1. **Gmail App Password** (if using Gmail)
   - Go to https://myaccount.google.com/apppasswords
   - Generate an app-specific password
   - Add to `.env`:
     ```
     SMTP_SERVER=smtp.gmail.com
     SMTP_PORT=587
     EMAIL_ADDRESS=your_email@gmail.com
     EMAIL_PASSWORD=your_app_password
     ```

2. **Other SMTP Services**
   - Any SMTP service will work (SendGrid, Mailgun, etc.)
   - Update the `.env` file with your provider's settings

## Security Best Practices

- ✅ **Never commit** your `.env` file to version control
- ✅ The `.gitignore` file is already configured to exclude `.env`
- ✅ Share `.env.example` as a template (without real keys)
- ✅ Rotate your API keys periodically
- ✅ Use environment-specific `.env` files for production deployments

## Troubleshooting

### "No API key found" Error
- Verify `.env` file exists in project root
- Check that `FRED_API_KEY` is set (no spaces around `=`)
- Ensure you're running Python from the project root directory

### "Invalid API key" Error
- Copy the key again from FRED - ensure no extra spaces
- Check that the key is active in your FRED account
- Generate a new API key if needed

### Rate Limit Errors
- The dashboard caches data to minimize API calls
- Default cache is 1 day for most indicators
- Increase `DATA_CACHE_DAYS` in `.env` if needed

## Need Help?

- FRED API Documentation: https://fred.stlouisfed.org/docs/api/fred/
- FRED Support: https://fred.stlouisfed.org/contactus/
- Project Issues: [Create an issue on GitHub]
