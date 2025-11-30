#!/usr/bin/env python3
"""
Clean AdventureWorks CSV files and save to data/cleaned/
"""
import os
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def clean_csv_file(input_path, output_path, encoding='utf-8'):
    """Clean a CSV file and save to output path"""
    try:
        # Try different encodings if utf-8 fails
        encodings = [encoding, 'latin-1', 'cp1252', 'iso-8859-1']
        df = None
        
        for enc in encodings:
            try:
                df = pd.read_csv(input_path, encoding=enc, low_memory=False)
                print(f"  ✓ Read with {enc} encoding")
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        
        if df is None:
            print(f"  ✗ Failed to read {input_path}")
            return False
        
        # Clean column names (lowercase, replace spaces with underscores)
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.strip()
        
        # Remove leading/trailing whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            # Replace empty strings with None
            df[col] = df[col].replace(['', 'nan', 'None', 'null'], None)
        
        # Save cleaned file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"  ✓ Saved {len(df)} rows to {output_path}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error cleaning {input_path}: {str(e)}")
        return False

def combine_products_data():
    """Combine Products with Categories and Subcategories"""
    print("\n📦 Combining Products data...")
    
    try:
        # Read base files
        products = pd.read_csv('data/raw/AdventureWorks_Products.csv', encoding='utf-8', low_memory=False)
        categories = pd.read_csv('data/raw/AdventureWorks_Product_Categories.csv', encoding='utf-8')
        subcategories = pd.read_csv('data/raw/AdventureWorks_Product_Subcategories.csv', encoding='utf-8')
        
        # Clean column names
        products.columns = products.columns.str.lower().str.replace(' ', '_').str.strip()
        categories.columns = categories.columns.str.lower().str.replace(' ', '_').str.strip()
        subcategories.columns = subcategories.columns.str.lower().str.replace(' ', '_').str.strip()
        
        # Merge subcategories with categories
        subcat_with_cat = subcategories.merge(
            categories,
            on='productcategorykey',
            how='left',
            suffixes=('', '_cat')
        )
        
        # Merge products with subcategories
        products_combined = products.merge(
            subcat_with_cat,
            on='productsubcategorykey',
            how='left',
            suffixes=('', '_subcat')
        )
        
        # Clean string columns
        for col in products_combined.select_dtypes(include=['object']).columns:
            products_combined[col] = products_combined[col].astype(str).str.strip()
            products_combined[col] = products_combined[col].replace(['nan', 'None', 'null', ''], None)
        
        # Rename columns for clarity
        products_combined = products_combined.rename(columns={
            'categoryname': 'category',
            'subcategoryname': 'subcategory',
            'productname': 'product_name',
            'productsku': 'product_sku',
            'modelname': 'model_name',
            'productdescription': 'product_description',
            'productcolor': 'color',
            'productsize': 'size',
            'productstyle': 'style',
            'productcost': 'cost',
            'productprice': 'price'
        })
        
        # Save cleaned products
        os.makedirs('data/cleaned', exist_ok=True)
        products_combined.to_csv('data/cleaned/Products_cleaned.csv', index=False, encoding='utf-8')
        print(f"  ✓ Combined and saved {len(products_combined)} products")
        return True
        
    except Exception as e:
        print(f"  ✗ Error combining products: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def combine_sales_data():
    """Combine all sales years into one file"""
    print("\n📊 Combining Sales data...")
    
    try:
        sales_files = [
            'data/raw/AdventureWorks_Sales_2015.csv',
            'data/raw/AdventureWorks_Sales_2016.csv',
            'data/raw/AdventureWorks_Sales_2017.csv'
        ]
        
        sales_dfs = []
        for file in sales_files:
            if os.path.exists(file):
                try:
                    df = pd.read_csv(file, encoding='utf-8', low_memory=False)
                    df.columns = df.columns.str.lower().str.replace(' ', '_').str.strip()
                    sales_dfs.append(df)
                    print(f"  ✓ Loaded {len(df)} rows from {os.path.basename(file)}")
                except Exception as e:
                    print(f"  ⚠ Skipped {file}: {str(e)}")
        
        if not sales_dfs:
            print("  ✗ No sales files found")
            return False
        
        # Combine all sales
        sales_combined = pd.concat(sales_dfs, ignore_index=True)
        
        # Clean date columns
        date_cols = ['orderdate', 'stockdate']
        for col in date_cols:
            if col in sales_combined.columns:
                sales_combined[col] = pd.to_datetime(sales_combined[col], errors='coerce', format='%m/%d/%Y')
        
        # Clean string columns
        for col in sales_combined.select_dtypes(include=['object']).columns:
            sales_combined[col] = sales_combined[col].astype(str).str.strip()
            sales_combined[col] = sales_combined[col].replace(['nan', 'None', 'null', ''], None)
        
        # Rename columns
        sales_combined = sales_combined.rename(columns={
            'orderdate': 'order_date',
            'stockdate': 'stock_date',
            'ordernumber': 'order_number',
            'productkey': 'product_key',
            'customerkey': 'customer_key',
            'territorykey': 'territory_key',
            'orderlineitem': 'order_line_item',
            'orderquantity': 'order_quantity'
        })
        
        # Save cleaned sales
        os.makedirs('data/cleaned', exist_ok=True)
        sales_combined.to_csv('data/cleaned/Sales_cleaned.csv', index=False, encoding='utf-8')
        print(f"  ✓ Combined and saved {len(sales_combined)} sales records")
        return True
        
    except Exception as e:
        print(f"  ✗ Error combining sales: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def clean_customers():
    """Clean customers data"""
    print("\n👥 Cleaning Customers data...")
    return clean_csv_file(
        'data/raw/AdventureWorks_Customers.csv',
        'data/cleaned/Customers_cleaned.csv',
        encoding='latin-1'
    )

def clean_territories():
    """Clean territories data (regions)"""
    print("\n🌍 Cleaning Territories/Regions data...")
    return clean_csv_file(
        'data/raw/AdventureWorks_Territories.csv',
        'data/cleaned/Regions_cleaned.csv'
    )

def clean_returns():
    """Clean returns data"""
    print("\n↩️  Cleaning Returns data...")
    return clean_csv_file(
        'data/raw/AdventureWorks_Returns.csv',
        'data/cleaned/Returns_cleaned.csv'
    )

def clean_calendar():
    """Clean calendar data"""
    print("\n📅 Cleaning Calendar data...")
    return clean_csv_file(
        'data/raw/AdventureWorks_Calendar.csv',
        'data/cleaned/Calendar_cleaned.csv'
    )

def main():
    """Main cleaning function"""
    print("🧹 ADVENTUREWORKS DATA CLEANING")
    print("=" * 70)
    
    # Change to project root
    os.chdir(project_root)
    
    results = []
    
    # Clean individual files
    results.append(("Products (combined)", combine_products_data()))
    results.append(("Sales (combined)", combine_sales_data()))
    results.append(("Customers", clean_customers()))
    results.append(("Regions/Territories", clean_territories()))
    results.append(("Returns", clean_returns()))
    results.append(("Calendar", clean_calendar()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 CLEANING SUMMARY")
    print("=" * 70)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\n✅ Successfully cleaned {success_count}/{total_count} datasets")
    print(f"📁 Cleaned files saved to: data/cleaned/")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



