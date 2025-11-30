"""
Product Recommendation System
Uses collaborative filtering to recommend products to customers
"""
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent

def load_data():
    """Load sales and product data from CSV"""
    sales_path = project_root / "data" / "cleaned" / "Sales_cleaned.csv"
    products_path = project_root / "data" / "cleaned" / "Products_cleaned.csv"
    
    if not sales_path.exists():
        raise FileNotFoundError(f"Sales data not found at {sales_path}")
    if not products_path.exists():
        raise FileNotFoundError(f"Products data not found at {products_path}")
    
    sales_df = pd.read_csv(sales_path)
    products_df = pd.read_csv(products_path)
    
    return sales_df, products_df

def create_user_item_matrix(sales_df):
    """Create user-item interaction matrix"""
    # Find correct column names
    customer_col = 'customer_key' if 'customer_key' in sales_df.columns else 'customerkey'
    product_col = 'product_key' if 'product_key' in sales_df.columns else 'productkey'
    quantity_col = 'order_quantity' if 'order_quantity' in sales_df.columns else 'quantity'
    
    # Create interaction matrix (customers x products)
    # Use quantity as interaction strength
    user_item = sales_df.groupby([customer_col, product_col])[quantity_col].sum().reset_index()
    
    # Pivot to create matrix
    user_item_matrix = user_item.pivot_table(
        index=customer_col,
        columns=product_col,
        values=quantity_col,
        fill_value=0
    )
    
    return user_item_matrix

def recommend_products_collaborative(user_item_matrix, customer_id, products_df, n_recommendations=10):
    """Recommend products using collaborative filtering"""
    if customer_id not in user_item_matrix.index:
        # New customer - recommend popular products
        product_popularity = user_item_matrix.sum().sort_values(ascending=False)
        top_products = product_popularity.head(n_recommendations).index.tolist()
        
        recommendations = products_df[products_df['productkey'].isin(top_products)][
            ['productkey', 'product_name', 'category', 'subcategory', 'price']
        ].head(n_recommendations)
        
        return recommendations, "Popular Products (New Customer)"
    
    # Calculate similarity between customers
    customer_vector = user_item_matrix.loc[customer_id].values.reshape(1, -1)
    similarities = cosine_similarity(customer_vector, user_item_matrix)[0]
    
    # Get top similar customers
    similar_customers_idx = np.argsort(similarities)[::-1][1:11]  # Exclude self, get top 10
    similar_customers = user_item_matrix.index[similar_customers_idx]
    
    # Get products liked by similar customers
    similar_customers_purchases = user_item_matrix.loc[similar_customers].sum()
    
    # Remove products customer already bought
    customer_purchases = user_item_matrix.loc[customer_id]
    similar_customers_purchases = similar_customers_purchases[customer_purchases == 0]
    
    # Get top recommendations
    top_products = similar_customers_purchases.sort_values(ascending=False).head(n_recommendations).index.tolist()
    
    recommendations = products_df[products_df['productkey'].isin(top_products)][
        ['productkey', 'product_name', 'category', 'subcategory', 'price']
    ].head(n_recommendations)
    
    return recommendations, "Based on Similar Customers"

def recommend_products_content_based(sales_df, products_df, customer_id, n_recommendations=10):
    """Recommend products based on customer's purchase history (content-based)"""
    customer_col = 'customer_key' if 'customer_key' in sales_df.columns else 'customerkey'
    product_col = 'product_key' if 'product_key' in sales_df.columns else 'productkey'
    
    # Get customer's purchase history
    customer_purchases = sales_df[sales_df[customer_col] == customer_id][product_col].unique()
    
    if len(customer_purchases) == 0:
        # New customer - recommend popular products
        product_counts = sales_df[product_col].value_counts()
        top_products = product_counts.head(n_recommendations).index.tolist()
        
        recommendations = products_df[products_df['productkey'].isin(top_products)][
            ['productkey', 'product_name', 'category', 'subcategory', 'price']
        ].head(n_recommendations)
        
        return recommendations, "Popular Products (New Customer)"
    
    # Get categories/subcategories customer likes
    customer_products = products_df[products_df['productkey'].isin(customer_purchases)]
    liked_categories = customer_products['category'].value_counts().head(3).index.tolist()
    liked_subcategories = customer_products['subcategory'].value_counts().head(5).index.tolist()
    
    # Recommend products in same categories but not yet purchased
    recommendations = products_df[
        (products_df['category'].isin(liked_categories) | 
         products_df['subcategory'].isin(liked_subcategories)) &
        (~products_df['productkey'].isin(customer_purchases))
    ].head(n_recommendations)
    
    if len(recommendations) < n_recommendations:
        # Fill with popular products if needed
        product_counts = sales_df[product_col].value_counts()
        top_products = product_counts[~product_counts.index.isin(customer_purchases)].head(
            n_recommendations - len(recommendations)
        ).index.tolist()
        
        additional = products_df[products_df['productkey'].isin(top_products)][
            ['productkey', 'product_name', 'category', 'subcategory', 'price']
        ]
        recommendations = pd.concat([recommendations, additional]).head(n_recommendations)
    
    return recommendations[['productkey', 'product_name', 'category', 'subcategory', 'price']], "Based on Purchase History"

def main():
    """Main function to demonstrate recommendation system"""
    print("🎯 Product Recommendation System")
    print("=" * 70)
    
    # Load data
    print("\n1. Loading data from CSV...")
    sales_df, products_df = load_data()
    print(f"   ✅ Loaded {len(sales_df):,} sales records")
    print(f"   ✅ Loaded {len(products_df)} products")
    
    # Create user-item matrix
    print("\n2. Creating user-item interaction matrix...")
    user_item_matrix = create_user_item_matrix(sales_df)
    print(f"   ✅ Matrix created: {user_item_matrix.shape[0]} customers x {user_item_matrix.shape[1]} products")
    
    # Get a sample customer
    sample_customer = user_item_matrix.index[0]
    print(f"\n3. Generating recommendations for customer {sample_customer}...")
    
    # Collaborative filtering recommendations
    collab_recs, collab_method = recommend_products_collaborative(
        user_item_matrix, sample_customer, products_df, n_recommendations=5
    )
    print(f"\n   Collaborative Filtering ({collab_method}):")
    for idx, row in collab_recs.iterrows():
        print(f"   - {row['product_name']} ({row['category']}) - ${row['price']}")
    
    # Content-based recommendations
    content_recs, content_method = recommend_products_content_based(
        sales_df, products_df, sample_customer, n_recommendations=5
    )
    print(f"\n   Content-Based ({content_method}):")
    for idx, row in content_recs.iterrows():
        print(f"   - {row['product_name']} ({row['category']}) - ${row['price']}")
    
    return user_item_matrix, products_df

if __name__ == "__main__":
    main()

