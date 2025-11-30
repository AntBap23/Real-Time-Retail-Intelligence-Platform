import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL connection configuration
@st.cache_resource
def get_postgres_connection():
    """Get cached PostgreSQL connection"""
    try:
        # Build connection string (handle empty password)
        postgres_user = os.getenv('POSTGRES_USER')
        postgres_password = os.getenv('POSTGRES_PASSWORD', '')
        postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
        postgres_port = os.getenv('POSTGRES_PORT', '5432')
        postgres_db = os.getenv('POSTGRES_DB', 'bapbap23')
        
        if postgres_password:
            conn_string = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        else:
            conn_string = f"postgresql://{postgres_user}@{postgres_host}:{postgres_port}/{postgres_db}"
        
        engine = create_engine(conn_string)
        return engine
    except Exception as e:
        st.error(f"Failed to connect to PostgreSQL: {str(e)}")
        return None

def execute_query(query):
    """Execute SQL query and return DataFrame"""
    engine = get_postgres_connection()
    if engine:
        try:
            return pd.read_sql_query(query, engine)
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            return pd.DataFrame()
    return pd.DataFrame()

# ─────────────── Sidebar Navigation ─────────────── #
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "📌 Project Overview",
    "💰 Customer Lifetime Value",
    "⚠️ Churn Prediction",
    "🎯 Product Recommendations",
    "📊 Tableau Dashboards",
    "🔍 Findings & Insights"
])

st.title("📊 AdventureWorks Retail Analytics Platform")

# ─────────────── Pages ─────────────── #

if page == "📌 Project Overview":
    st.subheader("Project Scope")
    
    # Display architecture image if it exists
    architecture_path = "images/architecture.png"
    if os.path.exists(architecture_path):
        st.image(architecture_path, caption="End-to-End Architecture", use_container_width=True)
    else:
        st.info("📐 Architecture diagram will be displayed here when available.")
    
    st.markdown("""
    This project demonstrates a comprehensive retail analytics platform built with AdventureWorks data.

    ### 🏗️ Architecture Components:
    
    - **Data Processing**: Python scripts clean and transform AdventureWorks CSV files
    - **Data Warehouse**: PostgreSQL with star schema (dimensions + facts)
    - **Machine Learning Models**: 
      - Customer Lifetime Value (CLV) prediction
      - Customer churn classification
      - Product recommendation system
    - **Business Intelligence**: Interactive Tableau dashboards
    - **Interactive Dashboard**: Streamlit app for real-time analytics
    
    ### 📊 Available Features:
    
    - ✅ **Customer Analytics**: CLV analysis and predictions
    - ✅ **Churn Analysis**: Identify at-risk customers
    - ✅ **Product Recommendations**: ML-powered product suggestions
    - ✅ **Tableau Visualizations**: Interactive dashboards for sales insights
    
    ### 🎯 Use Cases:
    
    - Customer segmentation and lifetime value analysis
    - Churn prevention and customer retention
    - Personalized product recommendations
    - Sales performance tracking and insights
    """)

elif page == "💰 Customer Lifetime Value":
    st.subheader("💰 Customer Lifetime Value Analysis")
    
    # Load data from CSV
    sales_path = "data/cleaned/Sales_cleaned.csv"
    customers_path = "data/cleaned/Customers_cleaned.csv"
    
    if os.path.exists(sales_path) and os.path.exists(customers_path):
        sales_df = pd.read_csv(sales_path)
        customers_df = pd.read_csv(customers_path)
        
        # Calculate customer metrics
        customer_metrics = sales_df.groupby('customer_key').agg({
            'order_quantity': 'sum',
            'order_number': 'nunique',
            'order_date': ['min', 'max']
        }).reset_index()
        
        customer_metrics.columns = [
            'customer_key', 'total_quantity', 'order_count',
            'first_order_date', 'last_order_date'
        ]
        
        # Estimate revenue
        customer_metrics['total_spent'] = customer_metrics['total_quantity'] * 50
        customer_metrics['avg_order_value'] = customer_metrics['total_spent'] / customer_metrics['order_count']
        
        # Merge with customer names
        customer_metrics = customer_metrics.merge(
            customers_df[['customerkey', 'firstname', 'lastname']],
            left_on='customer_key',
            right_on='customerkey',
            how='left'
        )
        customer_metrics['customer_name'] = (
            customer_metrics['firstname'] + ' ' + customer_metrics['lastname']
        ).fillna('Unknown')
        
        # Calculate days since last order
        customer_metrics['last_order_date'] = pd.to_datetime(customer_metrics['last_order_date'])
        customer_metrics['days_since_last_order'] = (
            pd.Timestamp.now() - customer_metrics['last_order_date']
        ).dt.days
        
        # Display top customers
        top_customers = customer_metrics.nlargest(20, 'total_spent')[
            ['customer_name', 'order_count', 'total_spent', 'avg_order_value', 'days_since_last_order']
        ]
        top_customers.columns = ['Customer Name', 'Total Orders', 'Total Spent', 'Avg Order Value', 'Days Since Last Order']
        
        st.dataframe(top_customers, use_container_width=True)
        
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Top Customer", top_customers.iloc[0]['Customer Name'])
            st.metric("Total Spent", f"${top_customers.iloc[0]['Total Spent']:,.2f}")
        with col2:
            st.metric("Total Customers Analyzed", len(customer_metrics))
            st.metric("Average CLV", f"${customer_metrics['total_spent'].mean():,.2f}")
        
        # ML Model Prediction Section
        st.markdown("---")
        st.markdown("### 🤖 ML Model CLV Prediction")
        
        if st.button("Predict CLV"):
            try:
                import sys
                sys.path.append('ml_models')
                from predict_clv import load_data, calculate_clv_features, prepare_features, train_model
                
                with st.spinner("Training model and predicting CLV..."):
                    # Load and prepare data
                    sales_df, customers_df = load_data()
                    clv_df = calculate_clv_features(sales_df, customers_df)
                    X, y, feature_cols = prepare_features(clv_df)
                    
                    # Train model
                    model = train_model(X, y)
                    
                    # Predict CLV for all customers
                    predictions = model.predict(X)
                    clv_df['predicted_clv'] = predictions
                    
                    st.success("✅ CLV predictions generated!")
                    
                    # Show top predicted CLV customers
                    top_predicted = clv_df.nlargest(20, 'predicted_clv')[
                        ['customer_key', 'predicted_clv', 'clv']
                    ]
                    top_predicted.columns = ['Customer Key', 'Predicted CLV', 'Actual CLV']
                    st.dataframe(top_predicted, use_container_width=True)
                    
                    st.metric("Average Predicted CLV", f"${predictions.mean():,.2f}")
            except Exception as e:
                st.error(f"Error predicting CLV: {str(e)}")
    else:
        st.warning("Customer data files not found. Please ensure CSV files are available.")

elif page == "⚠️ Churn Prediction":
    st.subheader("⚠️ Customer Churn Classification")
    st.markdown("""
    Predict which customers are at risk of churning based on their purchase behavior and demographics.
    """)
    
    # Load data from CSV
    sales_path = "data/cleaned/Sales_cleaned.csv"
    customers_path = "data/cleaned/Customers_cleaned.csv"
    
    if os.path.exists(sales_path) and os.path.exists(customers_path):
        sales_df = pd.read_csv(sales_path)
        customers_df = pd.read_csv(customers_path)
        
        # Calculate churn features
        st.markdown("### Customer Churn Analysis")
        
        # Aggregate sales by customer
        customer_col = 'customer_key' if 'customer_key' in sales_df.columns else 'customerkey'
        date_col = 'order_date' if 'order_date' in sales_df.columns else 'orderdate'
        
        customer_metrics = sales_df.groupby(customer_col).agg({
            date_col: ['min', 'max', 'count']
        }).reset_index()
        
        customer_metrics.columns = ['customer_key', 'first_order_date', 'last_order_date', 'order_count']
        
        # Calculate days since last order (relative to dataset's last date, not today)
        sales_df[date_col] = pd.to_datetime(sales_df[date_col], errors='coerce')
        last_date_in_data = sales_df[date_col].max()
        customer_metrics['last_order_date'] = pd.to_datetime(customer_metrics['last_order_date'])
        customer_metrics['days_since_last_order'] = (
            last_date_in_data - customer_metrics['last_order_date']
        ).dt.days
        
        # Define churn: customers with no order in last 60 days (relative to dataset end)
        customer_metrics['churned'] = (customer_metrics['days_since_last_order'] > 60).astype(int)
        
        # Merge with customer names
        customer_id_col = 'customerkey' if 'customerkey' in customers_df.columns else 'customer_key'
        customer_metrics = customer_metrics.merge(
            customers_df[[customer_id_col, 'firstname', 'lastname']],
            left_on='customer_key',
            right_on=customer_id_col,
            how='left'
        )
        customer_metrics['customer_name'] = (
            customer_metrics['firstname'].fillna('') + ' ' + customer_metrics['lastname'].fillna('')
        ).str.strip()
        
        # Display churn statistics
        churn_rate = customer_metrics['churned'].mean()
        total_customers = len(customer_metrics)
        churned_customers = customer_metrics['churned'].sum()
        active_customers = total_customers - churned_customers
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Customers", f"{total_customers:,}")
        with col2:
            st.metric("Active Customers", f"{active_customers:,}")
        with col3:
            st.metric("Churned Customers", f"{churned_customers:,}")
        with col4:
            st.metric("Churn Rate", f"{churn_rate:.2%}")
        
        # Show at-risk customers (30-60 days since last order, relative to dataset)
        st.markdown("### At-Risk Customers (No order in 30-60 days)")
        at_risk = customer_metrics[
            (customer_metrics['days_since_last_order'] > 30) & 
            (customer_metrics['days_since_last_order'] <= 60)
        ].nlargest(20, 'days_since_last_order')[
            ['customer_name', 'order_count', 'days_since_last_order', 'last_order_date']
        ]
        if not at_risk.empty:
            at_risk.columns = ['Customer Name', 'Total Orders', 'Days Since Last Order', 'Last Order Date']
            st.dataframe(at_risk, use_container_width=True)
        else:
            st.info("No customers currently in the at-risk window (30-60 days since last order).")
        
        # ML Model Section
        st.markdown("---")
        st.markdown("### 🤖 ML Churn Prediction Model")
        
        if st.button("Train & Predict Churn"):
            try:
                import sys
                sys.path.append('ml_models')
                from classify_churn import load_data, calculate_churn_features, prepare_features, train_model
                
                with st.spinner("Training churn classification model..."):
                    # Load and prepare data
                    sales_df, customers_df = load_data()
                    churn_df = calculate_churn_features(sales_df, customers_df)
                    X, y, feature_cols = prepare_features(churn_df)
                    
                    # Train model
                    model = train_model(X, y)
                    
                    # Predict churn for all customers
                    predictions = model.predict(X)
                    probabilities = model.predict_proba(X)[:, 1]  # Probability of churning
                    
                    churn_df['predicted_churn'] = predictions
                    churn_df['churn_probability'] = probabilities
                    
                    st.success("✅ Churn predictions generated!")
                    
                    # Show high-risk customers
                    st.markdown("### High-Risk Customers (Predicted to Churn)")
                    high_risk = churn_df[churn_df['predicted_churn'] == 1].nlargest(20, 'churn_probability')[
                        ['customer_key', 'churn_probability', 'days_since_last_order', 'order_count']
                    ]
                    high_risk.columns = ['Customer Key', 'Churn Probability', 'Days Since Last Order', 'Order Count']
                    st.dataframe(high_risk, use_container_width=True)
                    
                    # Model metrics
                    st.markdown("### Model Performance")
                    accuracy = (predictions == y).mean()
                    st.metric("Model Accuracy", f"{accuracy:.2%}")
                    
                    # Feature importance
                    st.markdown("### Top Churn Risk Factors")
                    feature_importance = pd.DataFrame({
                        'feature': feature_cols,
                        'importance': model.feature_importances_
                    }).sort_values('importance', ascending=False)
                    
                    st.bar_chart(feature_importance.set_index('feature')['importance'])
                    
            except Exception as e:
                st.error(f"Error predicting churn: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    else:
        st.warning("Customer data files not found. Please ensure CSV files are available.")

elif page == "🎯 Product Recommendations":
    st.subheader("🎯 Product Recommendation System")
    st.markdown("""
    Get personalized product recommendations using machine learning.
    Recommendations are based on collaborative filtering (similar customers) and content-based filtering (purchase history).
    """)
    
    # Load data
    sales_path = "data/cleaned/Sales_cleaned.csv"
    products_path = "data/cleaned/Products_cleaned.csv"
    
    if os.path.exists(sales_path) and os.path.exists(products_path):
        sales_df = pd.read_csv(sales_path)
        products_df = pd.read_csv(products_path)
        
        # Get customer list
        customer_col = 'customer_key' if 'customer_key' in sales_df.columns else 'customerkey'
        customers = sales_df[customer_col].unique()
        
        st.markdown("### Select Customer")
        selected_customer = st.selectbox(
            "Choose a customer to get recommendations:",
            options=customers[:100],  # Limit to first 100 for performance
            format_func=lambda x: f"Customer {x}"
        )
        
        if st.button("Get Recommendations"):
            try:
                import sys
                sys.path.append('ml_models')
                from recommendation_system import (
                    create_user_item_matrix, 
                    recommend_products_collaborative,
                    recommend_products_content_based
                )
                
                with st.spinner("Generating recommendations..."):
                    # Create user-item matrix
                    user_item_matrix = create_user_item_matrix(sales_df)
                    
                    # Get collaborative filtering recommendations
                    collab_recs, collab_method = recommend_products_collaborative(
                        user_item_matrix, selected_customer, products_df, n_recommendations=10
                    )
                    
                    # Get content-based recommendations
                    content_recs, content_method = recommend_products_content_based(
                        sales_df, products_df, selected_customer, n_recommendations=10
                    )
                    
                    st.success("✅ Recommendations generated!")
                    
                    # Display recommendations
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"### Collaborative Filtering ({collab_method})")
                        collab_recs.columns = ['Product Key', 'Product Name', 'Category', 'Subcategory', 'Price']
                        st.dataframe(collab_recs, use_container_width=True)
                    
                    with col2:
                        st.markdown(f"### Content-Based ({content_method})")
                        content_recs.columns = ['Product Key', 'Product Name', 'Category', 'Subcategory', 'Price']
                        st.dataframe(content_recs, use_container_width=True)
                    
                    # Summary
                    st.markdown("---")
                    st.markdown("### Recommendation Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Collaborative Recommendations", len(collab_recs))
                    with col2:
                        st.metric("Content-Based Recommendations", len(content_recs))
                    with col3:
                        avg_price = (collab_recs['Price'].mean() + content_recs['Price'].mean()) / 2
                        st.metric("Average Recommended Price", f"${avg_price:.2f}")
                    
            except Exception as e:
                st.error(f"Error generating recommendations: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    else:
        st.warning("Data files not found. Please ensure CSV files are available.")

elif page == "📊 Tableau Dashboards":
    st.subheader("📊 Tableau Dashboard Visualizations")
    st.markdown("""
    Interactive dashboards created in Tableau for comprehensive retail analytics.
    These visualizations provide insights into sales performance, customer behavior, 
    and product trends.
    """)
    
    # Tableau Public Embed
    st.markdown("### Interactive Dashboard (Tableau Public)")
    st.markdown("""
    <div class='tableauPlaceholder' id='viz1764513783311' style='position: relative'>
    <noscript><a href='#'><img alt='Dashboard 1 ' src='https://public.tableau.com/static/images/Ad/AdventureWorksDashboard_17645136302510/Dashboard1/1_rss.png' style='border: none' /></a></noscript>
    <object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> 
    <param name='embed_code_version' value='3' /> 
    <param name='site_root' value='' />
    <param name='name' value='AdventureWorksDashboard_17645136302510&#47;Dashboard1' />
    <param name='tabs' value='no' />
    <param name='toolbar' value='yes' />
    <param name='static_image' value='https://public.tableau.com/static/images/Ad/AdventureWorksDashboard_17645136302510/Dashboard1/1.png' /> 
    <param name='animate_transition' value='yes' />
    <param name='display_static_image' value='yes' />
    <param name='display_spinner' value='yes' />
    <param name='display_overlay' value='yes' />
    <param name='display_count' value='yes' />
    <param name='language' value='en-US' /></object></div>
    <script type='text/javascript'>
        var divElement = document.getElementById('viz1764513783311');
        var vizElement = divElement.getElementsByTagName('object')[0];
        if ( divElement.offsetWidth > 800 ) { 
            vizElement.style.minWidth='420px';
            vizElement.style.maxWidth='650px';
            vizElement.style.width='100%';
            vizElement.style.minHeight='587px';
            vizElement.style.maxHeight='887px';
            vizElement.style.height=(divElement.offsetWidth*0.75)+'px';
        } else if ( divElement.offsetWidth > 500 ) { 
            vizElement.style.minWidth='420px';
            vizElement.style.maxWidth='650px';
            vizElement.style.width='100%';
            vizElement.style.minHeight='587px';
            vizElement.style.maxHeight='887px';
            vizElement.style.height=(divElement.offsetWidth*0.75)+'px';
        } else { 
            vizElement.style.width='100%';
            vizElement.style.height='1477px';
        }
        var scriptElement = document.createElement('script');
        scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
        vizElement.parentNode.insertBefore(scriptElement, vizElement);
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display Dashboard 1 (Static Screenshot)
    st.markdown("### Dashboard 1 - Static Screenshot")
    dashboard1_path = "dashboards/tableau/dashboard1.png"
    if os.path.exists(dashboard1_path):
        st.image(dashboard1_path, caption="Tableau Dashboard 1 - Sales & Performance Analytics", use_container_width=True)
    else:
        st.warning(f"Dashboard image not found at: {dashboard1_path}")
    
    st.markdown("---")
    
    # Display Dashboard 2 (Static Screenshot)
    st.markdown("### Dashboard 2 - Static Screenshot")
    dashboard2_path = "dashboards/tableau/dashboard2.png"
    if os.path.exists(dashboard2_path):
        st.image(dashboard2_path, caption="Tableau Dashboard 2 - Customer & Product Insights", use_container_width=True)
    else:
        st.warning(f"Dashboard image not found at: {dashboard2_path}")
    
    st.markdown("---")
    
    # Additional information with link
    st.markdown("""
    **For interaction find this visual on Tableau Public using this link:**
    
    https://public.tableau.com/views/AdventureWorksDashboard_17645136302510/Dashboard1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link
    """)

elif page == "🔍 Findings & Insights":
    st.subheader("Key Findings & Insights")
    st.markdown("""
    This page documents important learnings, challenges, and insights discovered during 
    model development and dashboard creation.
    """)
    
    st.markdown("---")
    
    # Model Development Insights
    st.markdown("### Machine Learning Model Insights")
    
    st.markdown("""
    #### Why 100% Accuracy Doesn't Mean a Good Model
    
    **Critical Learning:** A model achieving 100% accuracy is often a red flag, not a success indicator.
    
    **Why this happens:**
    - **Overfitting**: The model memorizes training data patterns instead of learning generalizable rules
    - **Data Leakage**: The model is using information that wouldn't be available in real-world scenarios
    - **Class Imbalance**: When one class dominates (e.g., 99% of customers are "active"), predicting the majority class gives high accuracy but poor insights
    - **Insufficient Data**: With very small datasets, the model can memorize all examples
    
    **What to look for instead:**
    - **Generalization**: How well does the model perform on unseen data?
    - **Precision & Recall**: Are we correctly identifying both positive and negative cases?
    - **Cross-validation**: Does the model perform consistently across different data splits?
    - **Business Value**: Does the model provide actionable insights?
    
    **In our churn model:**
    - We encountered scenarios where all customers appeared in one class (100% churn or 0% churn)
    - This would give "perfect" accuracy but provides no predictive value
    - We adjusted thresholds and used relative dates to create more realistic class distributions
    """)
    
    st.markdown("---")
    
    st.markdown("""
    #### Data Quality Challenges
    
    **Historical Data Limitations:**
    - AdventureWorks data spans 2015-2017, making "days since last order" calculations relative to dataset end date
    - All customers appear "churned" when calculated from today's date
    - Solution: Use dataset's last date as reference point for realistic analysis
    
    **Missing Features:**
    - Source data lacks many fields (address, phone, coordinates, etc.)
    - Removed unused columns from database schema to keep it clean and accurate
    - Models work with available features, making reasonable estimates where needed
    
    **Data Volume:**
    - Reduced CSV files by 50-75% to improve processing speed
    - Still maintains representative sample for analysis
    - Models train quickly on reduced dataset
    """)
    
    st.markdown("---")
    
    st.markdown("""
    #### Model Selection & Performance
    
    **Random Forest Choice:**
    - Selected for its ability to handle mixed data types
    - Provides feature importance for interpretability
    - Robust to outliers and missing values
    - Good baseline for classification and regression tasks
    
    **Recommendation System:**
    - Implemented both collaborative and content-based filtering
    - Collaborative: Finds similar customers and recommends their purchases
    - Content-based: Uses customer's purchase history to suggest similar products
    - Hybrid approach provides diverse recommendations
    
    **CLV Model:**
    - Uses customer purchase patterns and demographics
    - Estimates revenue where exact prices aren't available
    - Provides actionable customer segmentation
    """)
    
    st.markdown("---")
    
    # Dashboard Building Insights
    st.markdown("### Dashboard & Visualization Insights")
    
    st.markdown("""
    #### Tableau Dashboard Development
    
    **Design Principles:**
    - Created interactive dashboards for comprehensive sales analysis
    - Used star schema joins for efficient querying
    - Implemented time-based hierarchies for trend analysis
    - Focused on actionable KPIs and metrics
    
    **Data Connection Architecture:**
    - Connected directly to PostgreSQL database using custom SQL queries
    - Leveraged star schema design for optimized join performance
    - Implemented parameterized queries for dynamic filtering
    - Used calculated fields and table calculations for complex metrics
    - Ensured efficient data extraction and refresh strategies
    
    **Visualization Best Practices:**
    - Used appropriate chart types for different metrics
    - Implemented filters and parameters for interactivity
    - Created calculated fields for derived metrics
    - Ensured mobile responsiveness
    - Optimized dashboard performance with data source filters
    """)
    
    st.markdown("---")
    
    st.markdown("""
    #### Streamlit App Architecture
    
    **Design Decisions:**
    - Modular page structure for easy navigation
    - CSV-based data loading for ML model portability
    - On-demand model training to avoid pre-computation delays
    - Embedded Tableau dashboards for interactive visualizations
    
    **Performance Optimizations:**
    - Used `@st.cache_resource` for database connections
    - Lazy loading of ML models (train when needed)
    - Efficient data aggregation for visualizations
    - Responsive UI with proper error handling
    """)
    
    st.markdown("---")
    
    # Technical Challenges
    st.markdown("### Technical Challenges & Solutions")
    
    st.markdown("""
    #### Challenges Encountered
    
    1. **Single-Class Classification Error**
       - Problem: All customers in one class caused sklearn errors
       - Solution: Added robust checks and conditional reporting
       - Learning: Always validate class distribution before model evaluation
    
    2. **Date Calculations with Historical Data**
       - Problem: Using today's date made all customers appear churned
       - Solution: Use dataset's maximum date as reference point
       - Learning: Context matters - adjust metrics for historical analysis
    
    3. **Database Connection Reliability**
       - Problem: Database connections can fail in demo environments
       - Solution: Implemented CSV-based fallback for ML models while maintaining database connections for dashboards
       - Learning: Portability and reliability often trump real-time connections for model training
    
    4. **Schema Mismatch**
       - Problem: Database schema had columns not in source data
       - Solution: Removed unused columns, kept only what exists in data
       - Learning: Schema should match actual data, not theoretical requirements
    """)
    
    st.markdown("---")
    
    # Best Practices
    st.markdown("### Best Practices Applied")
    
    st.markdown("""
    #### Data Engineering Pipeline
    
    **Data Ingestion:**
    - Developed automated ingestion scripts to process multiple CSV sources
    - Implemented robust error handling for file reading and encoding issues
    - Created data validation checks during ingestion process
    - Built reusable functions for consistent data loading across sources
    
    **Data Transformation:**
    - Standardized column naming conventions across all datasets
    - Implemented data type validation and conversion pipelines
    - Created data quality checks (null handling, duplicate detection)
    - Built transformation scripts for combining related datasets
    
    **Data Warehouse Design:**
    - Implemented dimensional modeling with star schema architecture
    - Created proper fact and dimension tables with appropriate relationships
    - Designed staging layer for raw data before transformation
    - Built mart tables for pre-aggregated analytics
    
    **Data Quality:**
    - Handled multiple encoding formats (UTF-8, Latin-1, CP1252)
    - Removed unused columns to maintain schema accuracy
    - Implemented data normalization for product categories and subcategories
    - Created data lineage tracking for auditability
    """)
    
    st.markdown("---")
    
    st.markdown("""
    #### Machine Learning Best Practices
    - Used appropriate train/test splits with stratification where possible
    - Handled class imbalance scenarios with proper validation
    - Provided feature importance for model interpretability
    - Implemented comprehensive error handling for edge cases
    - Validated model assumptions before evaluation
    - Created reusable model training functions for consistency
    """)
    
    st.markdown("---")
    
    st.markdown("""
    #### Visualization Best Practices
    - Created interactive dashboards in Tableau with database connections
    - Embedded public dashboards for accessibility
    - Provided static screenshots as fallback
    - Used appropriate visualizations for each metric type
    - Ensured mobile-friendly designs
    - Optimized query performance for large datasets
    """)
    
    st.markdown("---")
    
    # Future Improvements
    st.markdown("### Future Improvements & Recommendations")
    
    st.markdown("""
    #### Model Enhancements
    - Implement time-series cross-validation for better evaluation
    - Add ensemble methods to improve prediction accuracy
    - Create A/B testing framework for model comparison
    - Implement model versioning and tracking
    
    #### Data Enhancements
    - Add real-time data streaming capabilities
    - Implement data quality monitoring
    - Create automated data validation pipelines
    - Add more external data sources (weather, economic indicators)
    
    #### Dashboard Enhancements
    - Add real-time updates for live dashboards
    - Implement user authentication and role-based access
    - Create custom alerting and notification system
    - Add export capabilities for reports
    """)
    
    st.markdown("---")
    
    # Key Takeaways
    st.markdown("### Key Takeaways")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Model Development:**
        - Always validate assumptions about your data
        - High accuracy doesn't guarantee a good model
        - Context matters (historical vs. real-time analysis)
        - Error handling is crucial for production systems
        """)
    
    with col2:
        st.markdown("""
        **Dashboard Building:**
        - Direct database connections enable real-time insights
        - Star schema design optimizes query performance
        - Interactive visualizations enhance user engagement
        - Always provide fallback options for reliability
        """)
    
    st.markdown("---")
    
    st.info("""
    **Remember**: The goal isn't perfect accuracy—it's creating models and dashboards 
    that provide actionable insights and business value. A 70% accurate model that 
    identifies high-value customers is more useful than a 100% accurate model that 
    just predicts the majority class.
    """)
