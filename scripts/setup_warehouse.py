#!/usr/bin/env python3
"""
Master script to set up the entire data warehouse
Runs all steps in the correct order:
1. Create schema
2. Load data
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from create_warehouse_schema import create_warehouse_schema
from load_warehouse_data import main as load_data

def main():
    """Run complete warehouse setup"""
    print("🚀 COMPLETE DATA WAREHOUSE SETUP\n")
    print("=" * 70)
    
    try:
        # Step 1: Create schema
        print("\n📋 Step 1: Creating warehouse schema...")
        create_warehouse_schema()
        
        # Step 2: Load data
        print("\n📦 Step 2: Loading data into warehouse...")
        load_data()
        
        print("\n" + "=" * 70)
        print("\n🎉 DATA WAREHOUSE SETUP COMPLETE!")
        print("\n✅ Your warehouse is ready for analysis!")
        print("   - Dimensions loaded")
        print("   - Facts loaded with proper foreign keys")
        print("\n📊 Next steps:")
        print("   - Connect Tableau to PostgreSQL using tableau_sales_query.sql")
        print("   - Run: streamlit run app/app.py")
        print("   - Query data using SQL")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

