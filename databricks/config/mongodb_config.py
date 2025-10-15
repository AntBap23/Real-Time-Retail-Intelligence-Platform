"""
MongoDB Atlas Configuration
Configuration settings for MongoDB Atlas integration
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class MongoDBConfig:
    """MongoDB Atlas configuration settings"""
    
    # Connection settings
    connection_string: str = "mongodb+srv://username:password@cluster.mongodb.net/"
    database_name: str = "retail_intelligence"
    
    # Collection settings
    collections: Dict[str, str] = None
    
    # Performance settings
    max_pool_size: int = 100
    min_pool_size: int = 10
    max_idle_time_ms: int = 30000
    server_selection_timeout_ms: int = 5000
    
    def __post_init__(self):
        """Set default values from environment variables"""
        self.connection_string = os.getenv('MONGODB_URI', self.connection_string)
        self.database_name = os.getenv('MONGODB_DB', self.database_name)
        
        if self.collections is None:
            self.collections = {
                "events_clickstream": "events_clickstream",
                "product_reviews": "product_reviews",
                "product_catalog": "product_catalog",
                "user_profiles": "user_profiles",
                "session_analytics": "session_analytics"
            }
    
    @property
    def client_options(self) -> Dict[str, Any]:
        """MongoDB client options"""
        return {
            "maxPoolSize": self.max_pool_size,
            "minPoolSize": self.min_pool_size,
            "maxIdleTimeMS": self.max_idle_time_ms,
            "serverSelectionTimeoutMS": self.server_selection_timeout_ms,
            "retryWrites": True,
            "retryReads": True
        }

# Global configuration instance
config = MongoDBConfig()

# Collection schemas for MongoDB
COLLECTION_SCHEMAS = {
    "events_clickstream": {
        "visitorid": "INTEGER",
        "event": "STRING",  # view, addtocart, transaction
        "itemid": "INTEGER",
        "timestamp": "TIMESTAMP",
        "transactionid": "STRING",
        "session_id": "STRING",
        "user_agent": "STRING",
        "ip_address": "STRING"
    },
    "product_reviews": {
        "review_id": "STRING",
        "product_id": "INTEGER",
        "user_id": "STRING",
        "rating": "INTEGER",
        "review_text": "STRING",
        "review_date": "TIMESTAMP",
        "helpful_votes": "INTEGER",
        "verified_purchase": "BOOLEAN",
        "sentiment_score": "DECIMAL(3,2)"
    },
    "product_catalog": {
        "product_id": "INTEGER",
        "product_name": "STRING",
        "category": "STRING",
        "subcategory": "STRING",
        "brand": "STRING",
        "price": "DECIMAL(10,2)",
        "description": "STRING",
        "features": "ARRAY<STRING>",
        "images": "ARRAY<STRING>",
        "tags": "ARRAY<STRING>",
        "availability": "STRING",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP"
    },
    "user_profiles": {
        "user_id": "STRING",
        "email": "STRING",
        "first_name": "STRING",
        "last_name": "STRING",
        "age": "INTEGER",
        "gender": "STRING",
        "location": {
            "country": "STRING",
            "state": "STRING",
            "city": "STRING",
            "postal_code": "STRING"
        },
        "preferences": {
            "categories": "ARRAY<STRING>",
            "brands": "ARRAY<STRING>",
            "price_range": {
                "min": "DECIMAL(10,2)",
                "max": "DECIMAL(10,2)"
            }
        },
        "behavior": {
            "total_orders": "INTEGER",
            "total_spent": "DECIMAL(15,2)",
            "avg_order_value": "DECIMAL(10,2)",
            "last_activity": "TIMESTAMP",
            "loyalty_tier": "STRING"
        },
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP"
    },
    "session_analytics": {
        "session_id": "STRING",
        "user_id": "STRING",
        "start_time": "TIMESTAMP",
        "end_time": "TIMESTAMP",
        "duration_seconds": "INTEGER",
        "page_views": "INTEGER",
        "products_viewed": "ARRAY<INTEGER>",
        "cart_additions": "ARRAY<INTEGER>",
        "purchases": "ARRAY<INTEGER>",
        "device_type": "STRING",
        "browser": "STRING",
        "traffic_source": "STRING",
        "conversion_value": "DECIMAL(10,2)",
        "conversion_goal": "STRING"
    }
}

# MongoDB indexes for performance
INDEXES = {
    "events_clickstream": [
        {"visitorid": 1, "timestamp": -1},
        {"itemid": 1, "timestamp": -1},
        {"event": 1, "timestamp": -1},
        {"session_id": 1}
    ],
    "product_reviews": [
        {"product_id": 1, "rating": -1},
        {"user_id": 1, "review_date": -1},
        {"review_text": "text"},
        {"sentiment_score": -1}
    ],
    "product_catalog": [
        {"product_id": 1},
        {"category": 1, "subcategory": 1},
        {"brand": 1},
        {"price": 1},
        {"product_name": "text", "description": "text"}
    ],
    "user_profiles": [
        {"user_id": 1},
        {"email": 1},
        {"location.country": 1, "location.state": 1},
        {"behavior.loyalty_tier": 1},
        {"behavior.total_spent": -1}
    ],
    "session_analytics": [
        {"session_id": 1},
        {"user_id": 1, "start_time": -1},
        {"conversion_goal": 1},
        {"traffic_source": 1, "start_time": -1}
    ]
}

# Aggregation pipelines for common analytics
AGGREGATION_PIPELINES = {
    "top_products_by_views": [
        {"$match": {"event": "view"}},
        {"$group": {
            "_id": "$itemid",
            "view_count": {"$sum": 1},
            "unique_visitors": {"$addToSet": "$visitorid"}
        }},
        {"$addFields": {"unique_visitor_count": {"$size": "$unique_visitors"}}},
        {"$sort": {"view_count": -1}},
        {"$limit": 100}
    ],
    "conversion_funnel": [
        {"$group": {
            "_id": "$visitorid",
            "events": {"$push": "$event"},
            "products": {"$addToSet": "$itemid"}
        }},
        {"$addFields": {
            "has_viewed": {"$in": ["view", "$events"]},
            "has_added_to_cart": {"$in": ["addtocart", "$events"]},
            "has_purchased": {"$in": ["transaction", "$events"]}
        }},
        {"$group": {
            "_id": None,
            "total_visitors": {"$sum": 1},
            "viewers": {"$sum": {"$cond": ["$has_viewed", 1, 0]}},
            "cart_adders": {"$sum": {"$cond": ["$has_added_to_cart", 1, 0]}},
            "purchasers": {"$sum": {"$cond": ["$has_purchased", 1, 0]}}
        }}
    ],
    "sentiment_analysis": [
        {"$match": {"review_text": {"$exists": True, "$ne": ""}}},
        {"$group": {
            "_id": "$product_id",
            "avg_rating": {"$avg": "$rating"},
            "avg_sentiment": {"$avg": "$sentiment_score"},
            "review_count": {"$sum": 1},
            "positive_reviews": {"$sum": {"$cond": [{"$gte": ["$sentiment_score", 0.1]}, 1, 0]}},
            "negative_reviews": {"$sum": {"$cond": [{"$lte": ["$sentiment_score", -0.1]}, 1, 0]}}
        }},
        {"$addFields": {
            "sentiment_ratio": {"$divide": ["$positive_reviews", "$review_count"]}
        }},
        {"$sort": {"avg_sentiment": -1}}
    ]
}
