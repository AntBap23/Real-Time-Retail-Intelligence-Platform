#!/usr/bin/env python3
"""
Load cleaned AdventureWorks data into PostgreSQL warehouse
Maps data to dimension and fact tables
"""
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create database connection"""
    postgres_user = os.getenv('POSTGRES_USER')
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    postgres_db = os.getenv('POSTGRES_DB', 'bapbap23')
    
    if not postgres_user:
        raise ValueError("Missing POSTGRES_USER environment variable")
    
    if postgres_password:
        conn_string = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    else:
        conn_string = f"postgresql://{postgres_user}@{postgres_host}:{postgres_port}/{postgres_db}"
    
    return create_engine(conn_string)

def load_dim_product(engine):
    """Load products into dim_product"""
    print("\n📦 Loading dim_product...")
    
    try:
        df = pd.read_csv('data/cleaned/Products_cleaned.csv', encoding='utf-8', low_memory=False)
        
        # Map columns to dim_product schema
        product_df = pd.DataFrame({
            'product_id': df['productkey'],
            'product_name': df.get('product_name', df.get('productname', '')),
            'category': df.get('category', ''),
            'subcategory': df.get('subcategory', ''),
            'brand': df.get('model_name', df.get('modelname', '')),  # Using model as brand
            'price': pd.to_numeric(df.get('price', df.get('productprice', 0)), errors='coerce'),
            'cost': pd.to_numeric(df.get('cost', df.get('productcost', 0)), errors='coerce'),
            'color': df.get('color', df.get('productcolor', '')),
            'size': df.get('size', df.get('productsize', '')),
            'is_active': True,
            'created_date': datetime.now().date(),
            'updated_date': datetime.now(),
            'scd_start_date': datetime.now().date(),
            'scd_end_date': None,
            'scd_current_flag': True
        })
        
        # Replace empty strings with None
        product_df = product_df.replace(['', 'nan', 'None'], None)
        
        # Load to database
        product_df.to_sql(
            'dim_product',
            engine,
            schema='dimensions',
            if_exists='append',
            index=False,
            method='multi'
        )
        
        print(f"  ✅ Loaded {len(product_df)} products")
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading products: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def load_dim_region(engine):
    """Load territories into dim_region"""
    print("\n🌍 Loading dim_region...")
    
    try:
        df = pd.read_csv('data/cleaned/Regions_cleaned.csv', encoding='utf-8', low_memory=False)
        
        # Map columns to dim_region schema
        region_df = pd.DataFrame({
            'region_id': df.get('salesterritorykey', df.get('territorykey', df.index + 1)),
            'region_name': df.get('region', ''),
            'country': df.get('country', ''),
            'region_group': df.get('continent', ''),
            'is_active': True,
            'created_date': datetime.now().date(),
            'updated_date': datetime.now()
        })
        
        # Replace empty strings with None
        region_df = region_df.replace(['', 'nan', 'None'], None)
        
        # Load to database
        region_df.to_sql(
            'dim_region',
            engine,
            schema='dimensions',
            if_exists='append',
            index=False,
            method='multi'
        )
        
        print(f"  ✅ Loaded {len(region_df)} regions")
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading regions: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def load_dim_reseller(engine):
    """Load customers into dim_reseller (treating customers as resellers)"""
    print("\n🏢 Loading dim_reseller (from customers)...")
    
    try:
        df = pd.read_csv('data/cleaned/Customers_cleaned.csv', encoding='utf-8', low_memory=False)
        
        # Map columns to dim_reseller schema
        reseller_df = pd.DataFrame({
            'reseller_id': df.get('customerkey', df.index + 1),
            'reseller_name': (df.get('firstname', '') + ' ' + df.get('lastname', '')).str.strip(),
            'business_type': df.get('occupation', ''),
            'contact_person': (df.get('firstname', '') + ' ' + df.get('lastname', '')).str.strip(),
            'email': df.get('emailaddress', ''),
            'customer_tier': df.get('educationlevel', ''),  # Using education as tier
            'is_active': True,
            'created_date': datetime.now().date(),
            'updated_date': datetime.now()
        })
        
        # Replace empty strings with None
        reseller_df = reseller_df.replace(['', 'nan', 'None'], None)
        
        # Load to database
        reseller_df.to_sql(
            'dim_reseller',
            engine,
            schema='dimensions',
            if_exists='append',
            index=False,
            method='multi'
        )
        
        print(f"  ✅ Loaded {len(reseller_df)} resellers")
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading resellers: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def load_dim_salesperson(engine):
    """Create placeholder salesperson data"""
    print("\n👤 Loading dim_salesperson (placeholder)...")
    
    try:
        # Create placeholder salesperson since we don't have salesperson data
        salesperson_df = pd.DataFrame({
            'salesperson_id': [1],
            'first_name': ['System'],
            'last_name': ['Generated'],
            'full_name': ['System Generated'],
            'email': ['system@adventureworks.com'],
            'hire_date': datetime.now().date(),
            'commission_rate': 0.10,
            'sales_quota': 100000.00,
            'manager_id': None,
            'department': 'Sales',
            'performance_tier': 'Standard',
            'is_active': True,
            'created_date': datetime.now().date(),
            'updated_date': datetime.now()
        })
        
        # Load to database
        salesperson_df.to_sql(
            'dim_salesperson',
            engine,
            schema='dimensions',
            if_exists='append',
            index=False,
            method='multi'
        )
        
        print(f"  ✅ Loaded {len(salesperson_df)} salesperson (placeholder)")
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading salesperson: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def load_fact_sales(engine):
    """Load sales into fact_sales"""
    print("\n💰 Loading fact_sales...")
    
    try:
        df = pd.read_csv('data/cleaned/Sales_cleaned.csv', encoding='utf-8', low_memory=False)
        
        # Get dimension keys from database
        with engine.connect() as conn:
            # Get product keys
            product_map = pd.read_sql(
                "SELECT product_key, product_id FROM dimensions.dim_product",
                conn
            )
            product_dict = dict(zip(product_map['product_id'], product_map['product_key']))
            
            # Get region keys
            region_map = pd.read_sql(
                "SELECT region_key, region_id FROM dimensions.dim_region",
                conn
            )
            region_dict = dict(zip(region_map['region_id'], region_map['region_key']))
            
            # Get reseller keys
            reseller_map = pd.read_sql(
                "SELECT reseller_key, reseller_id FROM dimensions.dim_reseller",
                conn
            )
            reseller_dict = dict(zip(reseller_map['reseller_id'], reseller_map['reseller_key']))
            
            # Get salesperson key (use first one, which is placeholder)
            salesperson_result = conn.execute(text("SELECT salesperson_key FROM dimensions.dim_salesperson LIMIT 1"))
            salesperson_key = salesperson_result.fetchone()[0] if salesperson_result else 1
        
        # Map product keys
        df['product_key'] = df.get('product_key', df.get('productkey', 0)).map(product_dict)
        
        # Map region keys
        df['region_key'] = df.get('territory_key', df.get('territorykey', 0)).map(region_dict)
        
        # Map reseller keys
        df['reseller_key'] = df.get('customer_key', df.get('customerkey', 0)).map(reseller_dict)
        
        # Parse order date
        order_date = pd.to_datetime(df.get('order_date', df.get('orderdate', '')), errors='coerce')
        
        # Create date_key (YYYYMMDD format)
        date_key = order_date.dt.strftime('%Y%m%d').astype(int)
        
        # Get product prices for calculations
        product_prices = pd.read_sql(
            "SELECT product_key, price FROM dimensions.dim_product",
            engine
        )
        price_dict = dict(zip(product_prices['product_key'], product_prices['price']))
        
        # Calculate amounts
        quantity = pd.to_numeric(df.get('order_quantity', df.get('orderquantity', 1)), errors='coerce').fillna(1)
        unit_price = df['product_key'].map(price_dict).fillna(0)
        total_amount = quantity * unit_price
        
        # Create fact_sales dataframe
        fact_df = pd.DataFrame({
            'sale_id': df.index + 1,
            'order_date': order_date,
            'product_key': df['product_key'],
            'region_key': df['region_key'],
            'reseller_key': df['reseller_key'],
            'salesperson_key': salesperson_key,  # Use placeholder
            'date_key': date_key,
            'quantity': quantity.astype(int),
            'unit_price': unit_price,
            'total_amount': total_amount,
            'discount_percent': 0.0,
            'discount_amount': 0.0,
            'tax_amount': total_amount * 0.08,  # Estimate 8% tax
            'shipping_cost': 10.0,  # Estimate shipping
            'order_status': 'Completed',
            'payment_method': 'Credit Card',
            'profit_amount': total_amount * 0.30,  # Estimate 30% profit margin
            'margin_percent': 30.0,
            'created_timestamp': datetime.now(),
            'updated_timestamp': datetime.now()
        })
        
        # Remove rows with missing foreign keys
        fact_df = fact_df.dropna(subset=['product_key', 'region_key', 'reseller_key'])
        
        # Replace NaN with None for database
        fact_df = fact_df.where(pd.notnull(fact_df), None)
        
        # Load to database in chunks to avoid memory issues
        chunk_size = 10000
        total_loaded = 0
        
        for i in range(0, len(fact_df), chunk_size):
            chunk = fact_df.iloc[i:i+chunk_size]
            chunk.to_sql(
                'fact_sales',
                engine,
                schema='facts',
                if_exists='append',
                index=False,
                method='multi'
            )
            total_loaded += len(chunk)
            print(f"  ⏳ Loaded {total_loaded}/{len(fact_df)} records...", end='\r')
        
        print(f"\n  ✅ Loaded {total_loaded} sales records")
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading sales: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def clear_existing_data(engine):
    """Clear existing data from tables"""
    print("\n🗑️  Clearing existing data...")
    
    try:
        with engine.connect() as conn:
            # Clear in reverse order (facts first, then dimensions)
            conn.execute(text("TRUNCATE TABLE facts.fact_sales CASCADE"))
            conn.execute(text("TRUNCATE TABLE facts.fact_targets CASCADE"))
            conn.execute(text("TRUNCATE TABLE dimensions.dim_product CASCADE"))
            conn.execute(text("TRUNCATE TABLE dimensions.dim_region CASCADE"))
            conn.execute(text("TRUNCATE TABLE dimensions.dim_reseller CASCADE"))
            conn.execute(text("TRUNCATE TABLE dimensions.dim_salesperson CASCADE"))
            conn.commit()
        print("  ✅ Cleared existing data")
        return True
    except Exception as e:
        print(f"  ⚠️  Warning clearing data: {str(e)}")
        return True  # Continue anyway

def main():
    """Main loading function"""
    print("📥 LOADING DATA INTO WAREHOUSE")
    print("=" * 70)
    
    # Change to project root
    os.chdir(project_root)
    
    # Check if cleaned files exist
    required_files = [
        'data/cleaned/Products_cleaned.csv',
        'data/cleaned/Sales_cleaned.csv',
        'data/cleaned/Customers_cleaned.csv',
        'data/cleaned/Regions_cleaned.csv'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("❌ Missing cleaned data files. Please run clean_adventureworks_data.py first.")
        print("Missing files:")
        for f in missing_files:
            print(f"  - {f}")
        return False
    
    try:
        engine = get_db_connection()
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ Failed to connect to database: {str(e)}")
        return False
    
    # Clear existing data
    clear_existing_data(engine)
    
    # Load dimensions first (required for fact tables)
    results = []
    results.append(("dim_product", load_dim_product(engine)))
    results.append(("dim_region", load_dim_region(engine)))
    results.append(("dim_reseller", load_dim_reseller(engine)))
    results.append(("dim_salesperson", load_dim_salesperson(engine)))
    
    # Load facts
    results.append(("fact_sales", load_fact_sales(engine)))
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 LOADING SUMMARY")
    print("=" * 70)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\n✅ Successfully loaded {success_count}/{total_count} tables")
    
    # Get record counts
    try:
        with engine.connect() as conn:
            print("\n📊 Record Counts:")
            tables = [
                ('dim_product', 'dimensions'),
                ('dim_region', 'dimensions'),
                ('dim_reseller', 'dimensions'),
                ('dim_salesperson', 'dimensions'),
                ('fact_sales', 'facts')
            ]
            for table, schema in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {schema}.{table}"))
                count = result.fetchone()[0]
                print(f"  {schema}.{table}: {count:,} records")
    except Exception as e:
        print(f"⚠️  Could not get record counts: {str(e)}")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

