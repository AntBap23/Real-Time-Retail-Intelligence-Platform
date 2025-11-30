"""
Customer Lifetime Value Prediction Model
Uses CSV data for training and prediction
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent

def load_data():
    """Load sales and customer data from CSV"""
    sales_path = project_root / "data" / "cleaned" / "Sales_cleaned.csv"
    customers_path = project_root / "data" / "cleaned" / "Customers_cleaned.csv"
    
    if not sales_path.exists():
        raise FileNotFoundError(f"Sales data not found at {sales_path}")
    if not customers_path.exists():
        raise FileNotFoundError(f"Customers data not found at {customers_path}")
    
    sales_df = pd.read_csv(sales_path)
    customers_df = pd.read_csv(customers_path)
    
    return sales_df, customers_df

def calculate_clv_features(sales_df, customers_df):
    """Calculate CLV features from sales and customer data"""
    # Find correct column names (handle case variations)
    customer_col = 'customer_key' if 'customer_key' in sales_df.columns else 'customerkey'
    quantity_col = 'order_quantity' if 'order_quantity' in sales_df.columns else 'quantity'
    date_col = 'order_date' if 'order_date' in sales_df.columns else 'orderdate'
    
    # Aggregate sales by customer
    customer_metrics = sales_df.groupby(customer_col).agg({
        quantity_col: ['sum', 'mean', 'count'],
        date_col: ['min', 'max']
    }).reset_index()
    
    customer_metrics.columns = [
        'customer_key', 'total_quantity', 'avg_quantity', 'order_count',
        'first_order_date', 'last_order_date'
    ]
    
    # Estimate revenue (using average price estimate)
    customer_metrics['total_revenue'] = customer_metrics['total_quantity'] * 50  # Estimate
    customer_metrics['avg_order_value'] = customer_metrics['total_revenue'] / customer_metrics['order_count'].replace(0, 1)
    
    # Calculate additional metrics
    customer_metrics['customer_lifetime_days'] = (
        pd.to_datetime(customer_metrics['last_order_date']) - 
        pd.to_datetime(customer_metrics['first_order_date'])
    ).dt.days
    
    customer_metrics['days_since_first_order'] = (
        pd.Timestamp.now() - pd.to_datetime(customer_metrics['first_order_date'])
    ).dt.days
    
    customer_metrics['days_since_last_order'] = (
        pd.Timestamp.now() - pd.to_datetime(customer_metrics['last_order_date'])
    ).dt.days
    
    customer_metrics['purchase_frequency'] = (
        customer_metrics['order_count'] / 
        customer_metrics['customer_lifetime_days'].replace(0, 1)
    ) * 30  # Purchases per month
    
    # Merge with customer demographics
    # Handle column name variations
    customer_id_col = 'customerkey' if 'customerkey' in customers_df.columns else 'customer_key'
    clv_df = customer_metrics.merge(
        customers_df[[customer_id_col, 'annualincome', 'totalchildren', 'educationlevel', 'occupation', 'homeowner']],
        left_on='customer_key',
        right_on=customer_id_col,
        how='left'
    )
    
    # Clean annual income (remove $ and commas)
    clv_df['annualincome'] = clv_df['annualincome'].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
    clv_df['annualincome'] = pd.to_numeric(clv_df['annualincome'], errors='coerce').fillna(0)
    
    # Encode categorical variables
    clv_df['homeowner_encoded'] = (clv_df['homeowner'] == 'Y').astype(int)
    
    # Calculate CLV (target variable) - using total revenue as proxy
    clv_df['clv'] = clv_df['total_revenue']
    
    return clv_df

def prepare_features(df):
    """Prepare features for CLV prediction"""
    feature_cols = [
        'avg_order_value',
        'order_count',
        'total_quantity',
        'customer_lifetime_days',
        'days_since_first_order',
        'days_since_last_order',
        'purchase_frequency',
        'annualincome',
        'totalchildren',
        'homeowner_encoded'
    ]
    
    # Select and clean features
    X = df[feature_cols].fillna(0)
    y = df['clv']
    
    return X, y, feature_cols

def train_model(X, y):
    """Train CLV prediction model"""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Performance:")
    print(f"  MAE: ${mae:,.2f}")
    print(f"  RMSE: ${rmse:,.2f}")
    print(f"  R² Score: {r2:.4f}")
    
    return model

def main():
    """Main function to train and save model"""
    print("💰 Training Customer Lifetime Value Model...")
    print("=" * 70)
    
    # Load data
    print("\n1. Loading data from CSV...")
    sales_df, customers_df = load_data()
    print(f"   ✅ Loaded {len(sales_df):,} sales records")
    print(f"   ✅ Loaded {len(customers_df):,} customer records")
    
    # Calculate features
    print("\n2. Calculating CLV features...")
    clv_df = calculate_clv_features(sales_df, customers_df)
    print(f"   ✅ Created features for {len(clv_df)} customers")
    
    # Prepare features
    print("\n3. Preparing features for training...")
    X, y, feature_cols = prepare_features(clv_df)
    
    # Train model
    print("\n4. Training model...")
    model = train_model(X, y)
    
    # Save model
    model_path = project_root / "ml_models" / "clv_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump({'model': model, 'feature_cols': feature_cols}, f)
    print(f"\n5. ✅ Model saved to {model_path}")
    
    # Show feature importance
    print("\n6. Feature Importance (Top 10):")
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"   {row['feature']}: {row['importance']:.4f}")
    
    return model

if __name__ == "__main__":
    main()

