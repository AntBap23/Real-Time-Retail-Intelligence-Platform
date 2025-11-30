"""
Customer Churn Classification Model
Uses CSV data for training and prediction
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
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

def calculate_churn_features(sales_df, customers_df):
    """Calculate churn risk features"""
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
    
    # Estimate revenue
    customer_metrics['total_revenue'] = customer_metrics['total_quantity'] * 50  # Estimate
    customer_metrics['avg_order_value'] = customer_metrics['total_revenue'] / customer_metrics['order_count'].replace(0, 1)
    
    # Calculate days since last order (relative to dataset's last date, not today)
    last_date_in_data = pd.to_datetime(sales_df[date_col]).max()
    customer_metrics['days_since_last_order'] = (
        last_date_in_data - pd.to_datetime(customer_metrics['last_order_date'])
    ).dt.days
    
    customer_metrics['customer_lifetime_days'] = (
        pd.to_datetime(customer_metrics['last_order_date']) - 
        pd.to_datetime(customer_metrics['first_order_date'])
    ).dt.days
    
    # Define churn: customers with no order in last 60 days (relative to dataset end date)
    # This makes sense for historical data analysis
    customer_metrics['churned'] = (customer_metrics['days_since_last_order'] > 60).astype(int)
    
    # Merge with customer demographics
    # Handle column name variations
    customer_id_col = 'customerkey' if 'customerkey' in customers_df.columns else 'customer_key'
    churn_df = customer_metrics.merge(
        customers_df[[customer_id_col, 'annualincome', 'totalchildren', 'educationlevel', 'occupation', 'homeowner']],
        left_on='customer_key',
        right_on=customer_id_col,
        how='left'
    )
    
    # Clean annual income
    churn_df['annualincome'] = churn_df['annualincome'].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
    churn_df['annualincome'] = pd.to_numeric(churn_df['annualincome'], errors='coerce').fillna(0)
    
    # Encode categorical variables
    churn_df['homeowner_encoded'] = (churn_df['homeowner'] == 'Y').astype(int)
    
    return churn_df

def prepare_features(df):
    """Prepare features for churn prediction"""
    feature_cols = [
        'total_revenue',
        'avg_order_value',
        'order_count',
        'days_since_last_order',
        'customer_lifetime_days',
        'annualincome',
        'totalchildren',
        'homeowner_encoded'
    ]
    
    # Select and clean features
    X = df[feature_cols].fillna(0)
    y = df['churned']
    
    return X, y, feature_cols

def train_model(X, y):
    """Train churn classification model"""
    # Check if we have both classes
    unique_classes = y.unique()
    n_classes = len(unique_classes)
    
    if n_classes < 2:
        print(f"Warning: Only {n_classes} class(es) found. Using all data for training.")
        # If only one class, we can't do proper train/test split with stratification
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    else:
        # Try stratified split, fallback to regular if it fails
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        except ValueError:
            # If stratification fails, use regular split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Performance:")
    print(f"  Accuracy: {accuracy:.4f}")
    
    # Only print classification report if we have both classes in test set
    test_unique = np.unique(y_test)
    pred_unique = np.unique(y_pred)
    test_classes = len(test_unique)
    pred_classes = len(pred_unique)
    
    # Check if we can generate classification report
    # Need BOTH 0 and 1 to be present in the actual test data
    has_zero = 0 in test_unique
    has_one = 1 in test_unique
    
    # Only generate report if test set actually contains both classes
    if has_zero and has_one and test_classes == 2:
        try:
            print(f"\nClassification Report:")
            print(classification_report(
                y_test, y_pred, 
                labels=[0, 1],
                target_names=['Active', 'Churned'],
                zero_division=0
            ))
            print(f"\nConfusion Matrix:")
            print(confusion_matrix(y_test, y_pred, labels=[0, 1]))
        except Exception as e:
            print(f"\nNote: Could not generate classification report: {str(e)}")
            print(f"Test set has {test_classes} class(es): {test_unique}")
            print(f"Predictions have {pred_classes} class(es): {pred_unique}")
    else:
        # Skip classification report if only one class
        print(f"\nNote: Classification report skipped - only one class present in test set.")
        print(f"Test set classes: {test_classes} ({test_unique})")
        print(f"Predictions have {pred_classes} class(es): {pred_unique}")
        print(f"Has class 0: {has_zero}, Has class 1: {has_one}")
        print(f"Model accuracy: {accuracy:.4f}")
    
    return model

def main():
    """Main function to train and save model"""
    print("⚠️  Training Customer Churn Classification Model...")
    print("=" * 70)
    
    # Load data
    print("\n1. Loading data from CSV...")
    sales_df, customers_df = load_data()
    print(f"   ✅ Loaded {len(sales_df):,} sales records")
    print(f"   ✅ Loaded {len(customers_df):,} customer records")
    
    # Calculate features
    print("\n2. Calculating churn features...")
    churn_df = calculate_churn_features(sales_df, customers_df)
    print(f"   ✅ Created features for {len(churn_df)} customers")
    
    # Check churn distribution
    churn_rate = churn_df['churned'].mean()
    print(f"   📊 Churn rate: {churn_rate:.2%}")
    
    # Prepare features
    print("\n3. Preparing features for training...")
    X, y, feature_cols = prepare_features(churn_df)
    
    # Train model
    print("\n4. Training model...")
    model = train_model(X, y)
    
    # Save model
    model_path = project_root / "ml_models" / "churn_model.pkl"
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

