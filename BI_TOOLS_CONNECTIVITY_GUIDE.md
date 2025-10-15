# 📊 BI Tools Connectivity Guide

## ✅ **Yes, both Tableau and Power BI can connect to Databricks SQL!**

### **Free Versions Support:**
- ✅ **Tableau Public Desktop** (Free) - Can connect with some limitations
- ✅ **Power BI Desktop** (Free) - Full connectivity with minor limitations
- ✅ **Paid versions** - Full enterprise features and capabilities

### **Tableau Connection to Databricks SQL**

#### **Free Version (Tableau Public Desktop):**
- ✅ **Can connect** to Databricks SQL Warehouse
- ✅ **Native connector** available
- ⚠️ **Data must be published as extracts** (not live connections)
- ⚠️ **10GB data limit** for published workbooks
- ⚠️ **Public visibility** - data will be visible to everyone
- ⚠️ **No automatic refresh** of published workbooks

#### **Paid Version (Tableau Desktop/Server):**
1. **Direct Connection** (Recommended)
   - Use Databricks SQL Warehouse as data source
   - Native connector available in Tableau Desktop/Server
   - Supports real-time queries and live connections

2. **JDBC Connection**
   - Use Databricks JDBC driver
   - Works with Tableau Desktop and Server
   - Good for custom configurations

#### **Setup Steps:**
1. **In Databricks:**
   - Create SQL Warehouse in Databricks workspace
   - Note the connection details (server hostname, port, HTTP path)
   - Get personal access token

2. **In Tableau:**
   - Connect to "Databricks" data source
   - Enter server hostname: `your-workspace.cloud.databricks.com`
   - Enter HTTP path: `/sql/1.0/warehouses/your-warehouse-id`
   - Enter personal access token
   - Select database and schema

#### **Connection String Format:**
```
Server: your-workspace.cloud.databricks.com
Port: 443
HTTP Path: /sql/1.0/warehouses/your-warehouse-id
Username: token
Password: your-personal-access-token
```

### **Power BI Connection to Databricks SQL**

#### **Free Version (Power BI Desktop):**
- ✅ **Full connectivity** to Databricks SQL Warehouse
- ✅ **Native "Databricks" connector** available
- ✅ **Both DirectQuery and Import modes** supported
- ✅ **All visualization features** available
- ✅ **Publishing to Power BI Service** (free tier)
- ⚠️ **1GB dataset limit** for Power BI Service (free tier)
- ⚠️ **Limited refresh frequency** (daily max for free tier)
- ⚠️ **Basic sharing** - limited collaboration features

#### **Paid Version (Power BI Pro/Premium):**
1. **Direct Connection** (Recommended)
   - Use "Databricks" connector in Power BI Desktop
   - Native integration with Databricks SQL
   - Supports DirectQuery and Import modes

2. **Spark Connector**
   - Use "Spark" connector for advanced scenarios
   - Good for custom Spark configurations

#### **Setup Steps:**
1. **In Databricks:**
   - Create SQL Warehouse
   - Note connection details
   - Get personal access token

2. **In Power BI:**
   - Get Data → More → Databricks
   - Enter server URL: `https://your-workspace.cloud.databricks.com`
   - Enter HTTP path: `/sql/1.0/warehouses/your-warehouse-id`
   - Enter personal access token
   - Select data source (DirectQuery or Import)

#### **Connection String Format:**
```
Server: https://your-workspace.cloud.databricks.com
HTTP Path: /sql/1.0/warehouses/your-warehouse-id
Username: token
Password: your-personal-access-token
```

## 🚀 **Benefits of Databricks SQL for BI Tools**

### **Performance:**
- **Photon Engine** - High-performance query engine
- **Automatic Optimization** - Query optimization and caching
- **Concurrent Queries** - Multiple users can query simultaneously
- **Scalable Compute** - Auto-scaling based on demand

### **Features:**
- **Real-time Data** - Live connections to Delta Lake
- **ACID Transactions** - Data consistency and reliability
- **Time Travel** - Query historical data versions
- **Schema Evolution** - Handle changing data structures

### **Security:**
- **Row-level Security** - Fine-grained access control
- **Column-level Security** - Hide sensitive data
- **Audit Logging** - Track all data access
- **Encryption** - Data encrypted in transit and at rest

## 📋 **Setup Checklist for BI Tools**

### **Prerequisites:**
- [ ] Databricks workspace with SQL Warehouse
- [ ] Personal access token
- [ ] Delta Lake tables with data
- [ ] Proper permissions and access

### **Tableau Public Desktop (Free) Setup:**
- [ ] Download and install Tableau Public Desktop
- [ ] Configure connection with Databricks credentials
- [ ] Test connection and create first dashboard
- [ ] Publish as extract (not live connection)
- [ ] Note: Data will be publicly visible

### **Tableau Desktop/Server (Paid) Setup:**
- [ ] Install Tableau Desktop/Server
- [ ] Download Databricks connector (if needed)
- [ ] Configure connection with credentials
- [ ] Test connection and create first dashboard

### **Power BI Desktop (Free) Setup:**
- [ ] Download and install Power BI Desktop
- [ ] Configure Databricks connection
- [ ] Test connection and create first report
- [ ] Publish to Power BI Service (free tier)
- [ ] Note: 1GB dataset limit for free tier

### **Power BI Pro/Premium (Paid) Setup:**
- [ ] Install Power BI Desktop
- [ ] Configure Databricks connection
- [ ] Test connection and create first report
- [ ] Publish to Power BI Service
- [ ] Set up automatic refresh schedules

## 🔧 **Connection Troubleshooting**

### **Common Issues:**

1. **Authentication Errors**
   - Verify personal access token is valid
   - Check token permissions and expiration
   - Ensure correct username format (use "token")

2. **Connection Timeouts**
   - Check network connectivity
   - Verify SQL Warehouse is running
   - Increase timeout settings in BI tool

3. **Query Performance Issues**
   - Use appropriate SQL Warehouse size
   - Optimize Delta Lake tables with Z-ordering
   - Consider using materialized views

4. **Data Access Issues**
   - Check user permissions in Databricks
   - Verify table/schema access rights
   - Ensure proper data sharing settings

### **Best Practices:**

1. **Use SQL Warehouses**
   - Create dedicated warehouses for BI tools
   - Size appropriately for expected workload
   - Enable auto-stop to save costs

2. **Optimize Queries**
   - Use appropriate filters and aggregations
   - Leverage Delta Lake optimizations
   - Consider materialized views for complex queries

3. **Security**
   - Use service principals for production
   - Implement row-level security
   - Regular access reviews and audits

## 📊 **Sample Dashboard Queries**

### **For Tableau Public Desktop (Static Extract):**
```sql
-- Sales Performance Summary (Static Data)
SELECT 
    DATE(order_date) as date,
    SUM(total_amount) as daily_sales,
    COUNT(DISTINCT sale_id) as daily_orders,
    AVG(total_amount) as avg_order_value
FROM gold_sales_fact
WHERE order_date >= '2024-01-01'
GROUP BY DATE(order_date)
ORDER BY date DESC
```

### **For Power BI Desktop (Dynamic/Real-time):**
```sql
-- Real-time Sales Dashboard
SELECT 
    DATE(order_date) as date,
    SUM(total_amount) as daily_sales,
    COUNT(DISTINCT sale_id) as daily_orders,
    AVG(total_amount) as avg_order_value
FROM gold_sales_fact
WHERE order_date >= CURRENT_DATE() - INTERVAL 30 DAYS
GROUP BY DATE(order_date)
ORDER BY date DESC
```

### **Product Performance Dashboard:**
```sql
SELECT 
    p.product_name,
    p.category,
    p.brand,
    SUM(s.total_amount) as total_sales,
    SUM(s.quantity) as total_quantity,
    COUNT(DISTINCT s.reseller_id) as unique_customers
FROM gold_sales_fact s
JOIN gold_product_dim p ON s.product_id = p.product_id
WHERE s.order_date >= CURRENT_DATE() - INTERVAL 90 DAYS
GROUP BY p.product_id, p.product_name, p.category, p.brand
ORDER BY total_sales DESC
```

### **Regional Performance Dashboard:**
```sql
SELECT 
    r.region_name,
    r.country,
    r.region_group,
    SUM(s.total_amount) as total_sales,
    COUNT(DISTINCT s.reseller_id) as unique_customers,
    COUNT(DISTINCT s.salesperson_id) as active_salespeople
FROM gold_sales_fact s
JOIN gold_region_dim r ON s.region_id = r.region_id
WHERE s.order_date >= CURRENT_DATE() - INTERVAL 30 DAYS
GROUP BY r.region_id, r.region_name, r.country, r.region_group
ORDER BY total_sales DESC
```

## 🎯 **Next Steps**

### **For Free Versions:**
1. **Set up Databricks SQL Warehouse**
2. **Download Tableau Public Desktop and Power BI Desktop**
3. **Create sample dashboards in both tools**
4. **Test connectivity and performance**
5. **Publish dashboards (Tableau Public extracts, Power BI Service)**
6. **Showcase different capabilities for your portfolio**

### **For Paid Versions:**
1. **Set up Databricks SQL Warehouse**
2. **Create sample dashboards in Tableau/Power BI**
3. **Test connectivity and performance**
4. **Implement security best practices**
5. **Create production-ready dashboards**
6. **Set up automatic refresh schedules**

## 💡 **Recommendations for Your Project**

### **Portfolio/Resume Strategy:**
- **Use Tableau Public Desktop** for static, impressive dashboards
- **Use Power BI Desktop** for more dynamic dashboards
- **Create dashboards in both tools** to showcase versatility
- **Use Tableau Public for portfolio** (public visibility)
- **Use Power BI for more dynamic use cases** (better refresh options)

### **Best Approach:**
1. **Create dashboards in both tools**
2. **Showcase different capabilities**
3. **Use Tableau Public for portfolio**
4. **Use Power BI for more dynamic use cases**

## 📚 **Additional Resources**

- [Databricks SQL Documentation](https://docs.databricks.com/sql/)
- [Tableau Databricks Connector](https://help.tableau.com/current/pro/desktop/en-us/databricks_overview.htm)
- [Power BI Databricks Connector](https://docs.microsoft.com/en-us/power-bi/connect-data/desktop-databricks-sql-warehouse)
- [Delta Lake Documentation](https://docs.delta.io/)
