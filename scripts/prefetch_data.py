"""
Prefetch and cache data for Render deployment
This runs during the build process to ensure data is available when app starts
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def prefetch_data():
    """Fetch all data and cache it"""
    print("=" * 60)
    print("PREFETCHING DATA FOR RENDER DEPLOYMENT")
    print("=" * 60)
    
    try:
        from web_app.components.data_loader import load_data
        
        print("\nFetching all indicator data...")
        data = load_data()
        
        print("\nData fetched successfully!")
        print(f"Treasury yields: {data['treasury_yields'].shape}")
        print(f"Labor market: {data['labor_market'].shape}")
        print(f"Credit spreads: {data['credit_spreads'].shape}")
        
        print("\n" + "=" * 60)
        print("DATA PREFETCH COMPLETE - Ready for deployment")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n⚠️ ERROR during data prefetch: {str(e)}")
        print("App will attempt to fetch data on first request")
        return False

if __name__ == "__main__":
    success = prefetch_data()
    sys.exit(0 if success else 1)
