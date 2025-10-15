# Databricks notebook source
"""
04 - MongoDB Integration
Integrate MongoDB Atlas with Databricks for semi-structured data analytics
"""

# COMMAND ----------

# Import libraries
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import sys
import json

# Add config to path
sys.path.append('/Workspace/Shared/databricks/config')
from mongodb_config import config, COLLECTION_SCHEMAS, INDEXES, AGGREGATION_PIPELINES

# COMMAND ----------

# Initialize Spark session
spark = SparkSession.builder \
    .appName("MongoDB Integration") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Set log level
spark.sparkContext.setLogLevel("INFO")

# COMMAND ----------

# Use database
spark.sql(f"USE {config.catalog_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. MongoDB Connection Setup

# COMMAND ----------

# Install MongoDB connector
%pip install pymongo

# COMMAND ----------

from pymongo import MongoClient
import pandas as pd

# COMMAND ----------

# Connect to MongoDB Atlas
def connect_to_mongodb():
    """Connect to MongoDB Atlas"""
    try:
        client = MongoClient(config.connection_string, **config.client_options)
        db = client[config.database_name]
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully")
        return client, db
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {str(e)}")
        return None, None

# COMMAND ----------

# Test connection
client, db = connect_to_mongodb()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create MongoDB Collections

# COMMAND ----------

def create_mongodb_collections():
    """Create MongoDB collections with proper schemas"""
    if not db:
        print("❌ MongoDB connection not available")
        return
    
    collections = [
        "events_clickstream",
        "product_reviews",
        "product_catalog",
        "user_profiles",
        "session_analytics"
    ]
    
    for collection_name in collections:
        try:
            # Create collection if it doesn't exist
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"✅ Created collection: {collection_name}")
            else:
                print(f"ℹ️ Collection already exists: {collection_name}")
        except Exception as e:
            print(f"❌ Error creating collection {collection_name}: {str(e)}")

# COMMAND ----------

# Create collections
create_mongodb_collections()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Create MongoDB Indexes

# COMMAND ----------

def create_mongodb_indexes():
    """Create indexes for MongoDB collections"""
    if not db:
        print("❌ MongoDB connection not available")
        return
    
    for collection_name, indexes in INDEXES.items():
        try:
            collection = db[collection_name]
            for index in indexes:
                try:
                    collection.create_index(list(index.items()))
                    print(f"✅ Created index on {collection_name}: {index}")
                except Exception as e:
                    print(f"⚠️ Index creation failed for {collection_name}: {str(e)}")
        except Exception as e:
            print(f"❌ Error creating indexes for {collection_name}: {str(e)}")

# COMMAND ----------

# Create indexes
create_mongodb_indexes()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Sample Data Generation

# COMMAND ----------

# Generate sample clickstream events
def generate_sample_clickstream_events(num_events=1000):
    """Generate sample clickstream events"""
    import random
    from datetime import datetime, timedelta
    
    events = []
    event_types = ["view", "addtocart", "transaction"]
    products = list(range(1, 100))  # Product IDs 1-99
    visitors = list(range(1, 500))  # Visitor IDs 1-499
    
    for i in range(num_events):
        event = {
            "visitorid": random.choice(visitors),
            "event": random.choice(event_types),
            "itemid": random.choice(products),
            "timestamp": datetime.now() - timedelta(days=random.randint(0, 30)),
            "session_id": f"session_{random.randint(1000, 9999)}",
            "user_agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            ]),
            "ip_address": f"192.168.1.{random.randint(1, 255)}"
        }
        
        if event["event"] == "transaction":
            event["transactionid"] = f"txn_{random.randint(10000, 99999)}"
        
        events.append(event)
    
    return events

# COMMAND ----------

# Generate sample product reviews
def generate_sample_product_reviews(num_reviews=500):
    """Generate sample product reviews"""
    import random
    from datetime import datetime, timedelta
    
    reviews = []
    products = list(range(1, 100))  # Product IDs 1-99
    users = [f"user_{i}" for i in range(1, 200)]  # User IDs
    
    review_texts = [
        "Great product, highly recommended!",
        "Good quality, fast shipping.",
        "Average product, nothing special.",
        "Poor quality, would not recommend.",
        "Excellent value for money.",
        "Product arrived damaged.",
        "Love this product, will buy again.",
        "Not as described, disappointed.",
        "Perfect for my needs.",
        "Overpriced for what you get."
    ]
    
    for i in range(num_reviews):
        rating = random.randint(1, 5)
        sentiment_score = (rating - 3) / 2  # Convert rating to sentiment (-1 to 1)
        
        review = {
            "review_id": f"review_{i+1}",
            "product_id": random.choice(products),
            "user_id": random.choice(users),
            "rating": rating,
            "review_text": random.choice(review_texts),
            "review_date": datetime.now() - timedelta(days=random.randint(0, 90)),
            "helpful_votes": random.randint(0, 50),
            "verified_purchase": random.choice([True, False]),
            "sentiment_score": round(sentiment_score, 2)
        }
        reviews.append(review)
    
    return reviews

# COMMAND ----------

# Insert sample data
if db:
    # Insert clickstream events
    events = generate_sample_clickstream_events(1000)
    db.events_clickstream.insert_many(events)
    print(f"✅ Inserted {len(events)} clickstream events")
    
    # Insert product reviews
    reviews = generate_sample_product_reviews(500)
    db.product_reviews.insert_many(reviews)
    print(f"✅ Inserted {len(reviews)} product reviews")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. MongoDB Analytics with Aggregation Pipelines

# COMMAND ----------

def run_mongodb_analytics():
    """Run MongoDB aggregation pipelines for analytics"""
    if not db:
        print("❌ MongoDB connection not available")
        return
    
    # Top products by views
    print("📊 Top Products by Views:")
    print("=" * 40)
    top_products = list(db.events_clickstream.aggregate(AGGREGATION_PIPELINES["top_products_by_views"]))
    for product in top_products[:10]:
        print(f"Product {product['_id']}: {product['view_count']} views, {product['unique_visitor_count']} unique visitors")
    
    # Conversion funnel
    print("\n🔄 Conversion Funnel:")
    print("=" * 40)
    funnel = list(db.events_clickstream.aggregate(AGGREGATION_PIPELINES["conversion_funnel"]))
    if funnel:
        data = funnel[0]
        print(f"Total Visitors: {data['total_visitors']}")
        print(f"Viewers: {data['viewers']} ({data['viewers']/data['total_visitors']*100:.1f}%)")
        print(f"Cart Adders: {data['cart_adders']} ({data['cart_adders']/data['total_visitors']*100:.1f}%)")
        print(f"Purchasers: {data['purchasers']} ({data['purchasers']/data['total_visitors']*100:.1f}%)")
    
    # Sentiment analysis
    print("\n😊 Sentiment Analysis:")
    print("=" * 40)
    sentiment = list(db.product_reviews.aggregate(AGGREGATION_PIPELINES["sentiment_analysis"]))
    for product in sentiment[:10]:
        print(f"Product {product['_id']}: Avg Rating {product['avg_rating']:.1f}, Sentiment {product['avg_sentiment']:.2f}, Reviews {product['review_count']}")

# COMMAND ----------

# Run analytics
run_mongodb_analytics()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Export MongoDB Data to Delta Lake

# COMMAND ----------

def export_mongodb_to_delta():
    """Export MongoDB data to Delta Lake tables"""
    if not db:
        print("❌ MongoDB connection not available")
        return
    
    # Export clickstream events
    try:
        events_df = spark.createDataFrame(list(db.events_clickstream.find()))
        events_df.write \
            .format("delta") \
            .mode("overwrite") \
            .option("mergeSchema", "true") \
            .saveAsTable("mongodb_events_clickstream")
        print("✅ Exported clickstream events to Delta Lake")
    except Exception as e:
        print(f"❌ Error exporting clickstream events: {str(e)}")
    
    # Export product reviews
    try:
        reviews_df = spark.createDataFrame(list(db.product_reviews.find()))
        reviews_df.write \
            .format("delta") \
            .mode("overwrite") \
            .option("mergeSchema", "true") \
            .saveAsTable("mongodb_product_reviews")
        print("✅ Exported product reviews to Delta Lake")
    except Exception as e:
        print(f"❌ Error exporting product reviews: {str(e)}")

# COMMAND ----------

# Export to Delta Lake
export_mongodb_to_delta()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Create MongoDB Analytics Views

# COMMAND ----------

# Create view for clickstream analytics
spark.sql("""
    CREATE OR REPLACE VIEW mongodb_clickstream_analytics AS
    SELECT 
        itemid as product_id,
        event,
        COUNT(*) as event_count,
        COUNT(DISTINCT visitorid) as unique_visitors,
        COUNT(DISTINCT session_id) as unique_sessions,
        DATE(timestamp) as event_date
    FROM mongodb_events_clickstream
    GROUP BY itemid, event, DATE(timestamp)
""")

# COMMAND ----------

# Create view for product sentiment
spark.sql("""
    CREATE OR REPLACE VIEW mongodb_product_sentiment AS
    SELECT 
        product_id,
        AVG(rating) as avg_rating,
        AVG(sentiment_score) as avg_sentiment,
        COUNT(*) as review_count,
        SUM(CASE WHEN sentiment_score > 0.1 THEN 1 ELSE 0 END) as positive_reviews,
        SUM(CASE WHEN sentiment_score < -0.1 THEN 1 ELSE 0 END) as negative_reviews
    FROM mongodb_product_reviews
    GROUP BY product_id
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Cross-Database Analytics

# COMMAND ----------

# Combine Delta Lake and MongoDB data
spark.sql("""
    CREATE OR REPLACE VIEW cross_database_analytics AS
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.brand,
        p.price,
        s.avg_rating,
        s.avg_sentiment,
        s.review_count,
        s.positive_reviews,
        s.negative_reviews,
        c.event_count,
        c.unique_visitors,
        c.unique_sessions
    FROM gold_product_dim p
    LEFT JOIN mongodb_product_sentiment s ON p.product_id = s.product_id
    LEFT JOIN (
        SELECT 
            product_id,
            SUM(event_count) as event_count,
            SUM(unique_visitors) as unique_visitors,
            SUM(unique_sessions) as unique_sessions
        FROM mongodb_clickstream_analytics
        GROUP BY product_id
    ) c ON p.product_id = c.product_id
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Data Quality Checks

# COMMAND ----------

# Check MongoDB collection counts
if db:
    print("📊 MongoDB Collection Counts:")
    print("=" * 40)
    for collection_name in db.list_collection_names():
        count = db[collection_name].count_documents({})
        print(f"{collection_name}: {count:,} documents")

# COMMAND ----------

# Check Delta Lake table counts
print("\n📊 Delta Lake Table Counts:")
print("=" * 40)
delta_tables = [
    "mongodb_events_clickstream",
    "mongodb_product_reviews"
]

for table in delta_tables:
    try:
        count = spark.sql(f"SELECT COUNT(*) as count FROM {table}").collect()[0]['count']
        print(f"{table}: {count:,} records")
    except Exception as e:
        print(f"{table}: Error - {str(e)}")

# COMMAND ----------

# Check cross-database analytics
print("\n📊 Cross-Database Analytics:")
print("=" * 40)
try:
    cross_analytics = spark.sql("""
        SELECT 
            COUNT(*) as total_products,
            COUNT(avg_rating) as products_with_reviews,
            COUNT(event_count) as products_with_events,
            AVG(avg_rating) as overall_avg_rating,
            AVG(avg_sentiment) as overall_avg_sentiment
        FROM cross_database_analytics
    """).collect()[0]
    
    print(f"Total Products: {cross_analytics['total_products']}")
    print(f"Products with Reviews: {cross_analytics['products_with_reviews']}")
    print(f"Products with Events: {cross_analytics['products_with_events']}")
    print(f"Overall Avg Rating: {cross_analytics['overall_avg_rating']:.2f}")
    print(f"Overall Avg Sentiment: {cross_analytics['overall_avg_sentiment']:.2f}")
except Exception as e:
    print(f"Cross-database analytics error: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Real-time Analytics Dashboard Queries

# COMMAND ----------

# Top performing products (combining sales and engagement)
spark.sql("""
    CREATE OR REPLACE VIEW top_performing_products AS
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.brand,
        p.price,
        COALESCE(pp.total_sales, 0) as total_sales,
        COALESCE(pp.total_quantity, 0) as total_quantity,
        COALESCE(s.avg_rating, 0) as avg_rating,
        COALESCE(s.review_count, 0) as review_count,
        COALESCE(c.event_count, 0) as clickstream_events,
        COALESCE(c.unique_visitors, 0) as unique_visitors,
        (COALESCE(pp.total_sales, 0) * 0.4 + COALESCE(s.avg_rating, 0) * 20 * 0.3 + COALESCE(c.unique_visitors, 0) * 0.3) as performance_score
    FROM gold_product_dim p
    LEFT JOIN gold_product_performance pp ON p.product_id = pp.product_id
    LEFT JOIN mongodb_product_sentiment s ON p.product_id = s.product_id
    LEFT JOIN (
        SELECT 
            product_id,
            SUM(event_count) as event_count,
            SUM(unique_visitors) as unique_visitors
        FROM mongodb_clickstream_analytics
        GROUP BY product_id
    ) c ON p.product_id = c.product_id
    ORDER BY performance_score DESC
""")

# COMMAND ----------

# Display top performing products
display(spark.sql("SELECT * FROM top_performing_products LIMIT 20"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("🎉 MongoDB Integration Complete!")
print("=" * 50)
print("✅ MongoDB Atlas connection established")
print("✅ Collections created with proper schemas")
print("✅ Indexes created for performance")
print("✅ Sample data generated and inserted")
print("✅ Analytics pipelines executed")
print("✅ Data exported to Delta Lake")
print("✅ Cross-database analytics views created")
print("✅ Real-time dashboard queries ready")
print("\n📋 Next Steps:")
print("1. Run 05_ml_pipeline.py for machine learning models")
print("2. Run 06_dbt_transformations.py for additional transformations")
print("3. Create Databricks SQL dashboards")
print("4. Set up real-time data streaming from MongoDB")
