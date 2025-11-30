# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites

1. **GitHub Account** - You need a GitHub account
2. **Streamlit Cloud Account** - Sign up at [streamlit.io/cloud](https://streamlit.io/cloud) (free)
3. **Repository on GitHub** - Your code should be pushed to GitHub

---

## Step 1: Prepare Your Repository

### 1.1 Ensure All Files Are Committed

```bash
# Check git status
git status

# Add all files (if not already added)
git add .

# Commit changes
git commit -m "Prepare for Streamlit Cloud deployment"

# Push to GitHub
git push origin main
```

### 1.2 Verify Required Files Are Present

Make sure these files exist in your repository:
- ✅ `app/app.py` - Main Streamlit app
- ✅ `requirements.txt` - Python dependencies
- ✅ `data/cleaned/*.csv` - Data files (or ensure they're generated)
- ✅ `ml_models/*.py` - ML model files
- ✅ `.gitignore` - Excludes venv and cache files

---

## Step 2: Create Streamlit Cloud Account

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign up"** or **"Sign in"**
3. Sign in with your GitHub account
4. Authorize Streamlit Cloud to access your GitHub repositories

---

## Step 3: Deploy Your App

### 3.1 New App

1. Click **"New app"** button
2. Fill in the deployment form:

   **Repository:**
   - Select your repository: `Real-Time-Retail-Intelligence-Platform`
   
   **Branch:**
   - Select branch: `main` (or `master`)
   
   **Main file path:**
   - Enter: `app/app.py`
   
   **App URL (optional):**
   - Leave default or customize: `your-app-name`

### 3.2 Advanced Settings (if needed)

Click **"Advanced settings"** if you need to:

- **Python version:** Default (3.11) is fine
- **Secrets:** Add environment variables if needed (e.g., database credentials)
  - Format: `KEY=value` (one per line)

### 3.3 Deploy

1. Click **"Deploy!"**
2. Wait for deployment (usually 1-2 minutes)
3. Your app will be live at: `https://your-app-name.streamlit.app`

---

## Step 4: Verify Deployment

After deployment, check:

1. ✅ App loads without errors
2. ✅ All pages are accessible
3. ✅ ML models can be trained (click buttons)
4. ✅ Data loads correctly
5. ✅ Tableau dashboard embeds properly

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError"

**Solution:** Ensure all dependencies are in `requirements.txt`

```bash
# Generate requirements.txt from your venv
pip freeze > requirements.txt

# Or manually add missing packages
```

### Issue: "FileNotFoundError: data/cleaned/..."

**Solution:** Ensure CSV files are committed to GitHub

```bash
# Check if files are tracked
git ls-files data/cleaned/

# If not, add them
git add data/cleaned/*.csv
git commit -m "Add cleaned data files"
git push
```

### Issue: App is slow to load

**Solution:** 
- CSV files might be large - consider reducing size
- Use `@st.cache_data` for data loading (already implemented)

### Issue: Database connection errors

**Solution:** 
- Your app uses CSV files, so database isn't needed
- If you add database features later, use Streamlit Secrets for credentials

---

## Updating Your App

### Automatic Updates

Streamlit Cloud automatically redeploys when you push to your main branch.

### Manual Redeploy

1. Go to your app dashboard on Streamlit Cloud
2. Click **"⋮"** (three dots) menu
3. Select **"Redeploy"**

---

## Environment Variables (Secrets)

If you need to add secrets (e.g., API keys, database passwords):

1. Go to your app dashboard
2. Click **"⋮"** menu → **"Settings"**
3. Go to **"Secrets"** tab
4. Add your secrets in TOML format:

```toml
[secrets]
POSTGRES_USER = "your_username"
POSTGRES_PASSWORD = "your_password"
POSTGRES_HOST = "your_host"
POSTGRES_DB = "bapbap23"
```

Access in your app:
```python
import streamlit as st
import os

# Access secrets
postgres_user = st.secrets.get("POSTGRES_USER", os.getenv("POSTGRES_USER"))
```

---

## Best Practices

1. **Keep requirements.txt updated** - Add all dependencies
2. **Test locally first** - Always test before pushing
3. **Use .gitignore** - Don't commit venv, cache, or secrets
4. **Monitor app usage** - Check Streamlit Cloud dashboard for errors
5. **Version control** - Use meaningful commit messages

---

## File Size Limits

- **Free tier:** 1GB total repository size
- **Individual files:** 200MB max
- **Recommendation:** Keep CSV files under 50MB each

If your data files are too large:
- Reduce CSV file sizes (you already did this)
- Use data compression
- Load data from external sources (S3, etc.)

---

## Quick Checklist Before Deployment

- [ ] All code is committed and pushed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] `app/app.py` is the main file
- [ ] Data files (`data/cleaned/*.csv`) are in repository
- [ ] `.gitignore` excludes venv and cache
- [ ] Tested app locally - works without errors
- [ ] No hardcoded secrets or credentials
- [ ] Repository is public (or you have Streamlit Cloud Pro)

---

## Support

- **Streamlit Docs:** [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Community:** [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues:** Report bugs in your repository

---

## Your Deployment Details

**Main file:** `app/app.py`  
**Requirements:** `requirements.txt`  
**Data location:** `data/cleaned/`  
**ML models:** `ml_models/`

Good luck with your deployment! 🎉

