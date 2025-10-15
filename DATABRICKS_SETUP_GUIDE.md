# 🚀 Databricks Setup Guide

## 📋 **Quick Start Checklist**

- [ ] Create Databricks Community Edition account
- [ ] Get workspace URL
- [ ] Create personal access token
- [ ] Create SQL Warehouse
- [ ] Test connection
- [ ] Set up environment variables

## 🆓 **Step 1: Create Databricks Community Edition Account**

### **Sign Up Process:**
1. **Go to:** https://community.cloud.databricks.com/
2. **Click:** "Get Started for Free"
3. **Sign up with:**
   - Your email address
   - Create a strong password
   - Accept terms and conditions
4. **Verify your email** (check your inbox)
5. **Complete registration** (may take 1-2 minutes)

### **What You Get:**
- ✅ **Free compute hours** (limited per month)
- ✅ **Free storage** (limited)
- ✅ **SQL Warehouses** for BI tools
- ✅ **Notebooks** for data processing
- ✅ **Workflows** for automation
- ✅ **Delta Lake** for data storage

## 🔗 **Step 2: Get Your Workspace URL**

### **Finding Your Workspace URL:**
1. **After logging in**, look at your browser's address bar
2. **Your URL will look like:**
   ```
   https://adb-1234567890123456.7.azuredatabricks.net/
   ```
3. **Copy this URL** (without the trailing slash)
4. **This is your `DATABRICKS_WORKSPACE_URL`**

### **Example:**
```
DATABRICKS_WORKSPACE_URL=https://adb-1234567890123456.7.azuredatabricks.net
```

## 🔑 **Step 3: Create Personal Access Token**

### **Token Creation Process:**
1. **In your Databricks workspace:**
   - Click on your **username** (top right corner)
   - Select **"User Settings"** from the dropdown

2. **Navigate to Access Tokens:**
   - Click on **"Access Tokens"** tab
   - Click **"Generate New Token"**

3. **Configure your token:**
   - **Name:** `Retail Intelligence Project`
   - **Expiration:** `90 days` (recommended for free tier)
   - **Click:** `Generate`

4. **⚠️ CRITICAL:** 
   - **COPY THE TOKEN IMMEDIATELY**
   - **You won't see it again!**
   - **This is your `DATABRICKS_TOKEN`**

### **Token Format:**
```
DATABRICKS_TOKEN=dapi1234567890abcdef1234567890abcdef12345678
```

## 🏗️ **Step 4: Create SQL Warehouse (for BI Tools)**

### **SQL Warehouse Setup:**
1. **In your workspace:**
   - Click **"SQL Warehouses"** in the left sidebar
   - Click **"Create SQL Warehouse"**

2. **Configure the warehouse:**
   - **Name:** `retail-intelligence-warehouse`
   - **Size:** `2X-Small` (free tier)
   - **Auto Stop:** `10 minutes` (saves credits)
   - **Click:** `Create`

3. **Get connection details:**
   - Click on your newly created warehouse
   - Go to **"Connection Details"** tab
   - **Note these values:**
     - **Server hostname:** `your-workspace.cloud.databricks.com`
     - **HTTP path:** `/sql/1.0/warehouses/your-warehouse-id`
     - **Port:** `443`

### **Connection Details for BI Tools:**
```
Server: your-workspace.cloud.databricks.com
Port: 443
HTTP Path: /sql/1.0/warehouses/your-warehouse-id
Username: token
Password: your-personal-access-token
```

## 🧪 **Step 5: Test Your Connection**

### **Quick Test:**
1. **Go to "Data"** in the left sidebar
2. **Click "Create Table"** > **"Upload File"**
3. **Upload a small CSV file** (like your retail data)
4. **Create a simple query:**
   ```sql
   SELECT * FROM your_table_name LIMIT 10
   ```
5. **Verify the query runs successfully**

### **Test with Python (Optional):**
```python
from databricks import sql
import os

# Test connection
with sql.connect(
    server_hostname=os.getenv('DATABRICKS_WORKSPACE_URL'),
    http_path=os.getenv('DATABRICKS_HTTP_PATH'),
    access_token=os.getenv('DATABRICKS_TOKEN')
) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"Connection successful: {result}")
```

## ⚙️ **Step 6: Set Up Environment Variables**

### **Create .env file:**
```bash
# Copy the checklist
cp ENVIRONMENT_VARIABLES_CHECKLIST.txt .env

# Edit with your values
nano .env
```

### **Fill in your values:**
```env
# Databricks Configuration
DATABRICKS_WORKSPACE_URL=https://adb-1234567890123456.7.azuredatabricks.net
DATABRICKS_TOKEN=dapi1234567890abcdef1234567890abcdef12345678

# SQL Warehouse (for BI tools)
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
```

## 🔧 **Step 7: Import Your Project Files**

### **Upload Project to Databricks:**
1. **Go to "Workspace"** in the left sidebar
2. **Create a folder:** `retail-intelligence-platform`
3. **Upload your notebooks:**
   - `databricks/notebooks/01_data_ingestion.py`
   - `databricks/notebooks/02_data_cleaning.py`
   - `databricks/notebooks/03_delta_lake_setup.py`
   - `databricks/notebooks/04_mongodb_integration.py`
   - `databricks/notebooks/06_dbt_transformations.py`

### **Set up Workflows:**
1. **Go to "Workflows"** in the left sidebar
2. **Click "Create Workflow"**
3. **Import the workflow JSON:**
   - `databricks/workflows/retail_etl_workflow.json`
   - `databricks/workflows/ml_training_workflow.json`

## 🚨 **Important Notes & Limitations**

### **Free Tier Limitations:**
- **Compute hours:** Limited per month
- **Storage:** Limited (but usually sufficient for projects)
- **SQL Warehouse:** Auto-stops after inactivity
- **Concurrent users:** Limited

### **Best Practices:**
- **Auto-stop warehouses** after 10 minutes of inactivity
- **Use smaller cluster sizes** (2X-Small)
- **Monitor your usage** in the workspace
- **Set calendar reminders** for token expiration

### **Security:**
- **Never share your access token**
- **Don't commit tokens to git**
- **Use environment variables**
- **Rotate tokens regularly**

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **"Invalid token" error:**
   - Check if token is expired
   - Verify token was copied correctly
   - Regenerate token if needed

2. **"Connection timeout" error:**
   - Check if SQL Warehouse is running
   - Start the warehouse if it's stopped
   - Verify network connectivity

3. **"Permission denied" error:**
   - Check if you have access to the workspace
   - Verify your account is active
   - Contact support if needed

4. **"Workspace not found" error:**
   - Verify the workspace URL is correct
   - Check if you're using the right region
   - Ensure you're logged into the correct account

### **Getting Help:**
- **Databricks Documentation:** https://docs.databricks.com/
- **Community Forum:** https://community.databricks.com/
- **Support:** Available for paid accounts

## 🎯 **Next Steps**

1. **✅ Complete Databricks setup**
2. **📊 Set up MongoDB Atlas** (see MongoDB setup guide)
3. **🔗 Connect BI tools** (Tableau/Power BI)
4. **📈 Create your first dashboard**
5. **🚀 Deploy your project**

## 📚 **Additional Resources**

- [Databricks Community Edition](https://community.cloud.databricks.com/)
- [Databricks SQL Documentation](https://docs.databricks.com/sql/)
- [Personal Access Tokens](https://docs.databricks.com/dev-tools/auth/pat.html)
- [SQL Warehouses](https://docs.databricks.com/sql/admin/sql-endpoints.html)
- [Delta Lake Documentation](https://docs.delta.io/)

