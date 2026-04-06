# 🚀 Deployment Guide - Production Deployment

**Status:** ✅ Production-Ready  
**Last Updated:** April 2026  
**Platforms:** Render, Streamlit Cloud, Docker

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [GitHub Release Setup (Models)](#github-release-setup-models)
3. [Render Deployment (Recommended)](#render-deployment-recommended)
4. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Environment Variables](#environment-variables-for-cloud)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Pre-Deployment Checklist

Before deploying, verify:

- [ ] All code committed to GitHub
- [ ] `.env` file created with Firebase credentials
- [ ] `.gitignore` includes `.env` and `.streamlit/secrets.toml`
- [ ] `requirements.txt` updated with all dependencies
- [ ] `runtime.txt` specifies Python 3.11
- [ ] All 8 models in `model_saved_files/` folder
- [ ] App tested locally with `streamlit run streamlit_app.py`
- [ ] Demo mode works (auth without Firebase)
- [ ] All tests pass (see SETUP_GUIDE.md)

---

## GitHub Release Setup (Models)

### Why GitHub Release?

Models are large (1.1 GB total). Storing in GitHub causes slowdowns. Use GitHub Releases instead:

- ✅ Auto-download on app startup
- ✅ Version control
- ✅ Reliable hosting
- ✅ No repo bloat

### Step 1: Create GitHub Release

1. Go to your GitHub repo: `https://github.com/YOUR_USERNAME/vitamin-deficiency-main`
2. Click **"Releases"** (right sidebar)
3. Click **"Create a new release"**
4. Fill in:
   ```
   Tag version:    v1.0-models
   Release title:  Model Files v1.0
   Description:    Pre-trained deep learning models for vitamin deficiency detection
   ```

### Step 2: Upload All Model Files

Drag and drop these files from `model_saved_files/`:

**Required files (9 total):**
```
1. Cnn.h5
2. Mobilenet.h5
3. ResNet.h5
4. VGG16.h5
5. InceptionV3.h5
6. Xception.h5
7. InceptionResNetV2.h5
8. EfficientNetV2L.h5
9. ensemble_metadata.json
```

**Steps:**
1. Click "Attach binaries by dropping them here or selecting them"
2. Select all 9 files from `model_saved_files/` folder
3. Wait for all uploads (may take 5-10 minutes, large files)
4. Verify all 9 files appear before publishing

### Step 3: Publish Release

1. Click **"Publish release"**
2. Verify all assets are listed (9 files)
3. Copy the release URL for later

### Step 4: Remove Model Files from Git

To prevent pushing large models:

```bash
# Add to .gitignore
echo "model_saved_files/*.h5" >> .gitignore
echo "model_saved_files/*/*.h5" >> .gitignore

# Remove from git (don't delete files)
git rm --cached model_saved_files/*.h5
git add .gitignore
git commit -m "Move models to GitHub Releases"
git push origin main
```

---

## Render Deployment (Recommended)

**Why Render?**
- ✅ Auto model downloads from GitHub Release
- ✅ Simple GitHub integration
- ✅ Affordable ($7/month paid tier for all 8 models)
- ✅ Free tier for lightweight mode (2-3 models)
- ✅ Auto SSL certificates

### Free Tier (512 MB RAM)
- Loads: MobileNet, CNN, VGG16 (3 models, ~110 MB)
- Available models: 3/8
- Accuracy: Good (ensemble still works)

### Recommended Tier: Pro ($7/month)
- Loads: All 8 models (1.1 GB total)
- Available models: 8/8
- Accuracy: Best

### Step 1: Prepare Repository

```bash
# Make sure .env is in .gitignore
grep "\.env" .gitignore

# Commit all code
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Connect to Render

1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Click **"New +"** → **"Web Service"**
4. Select your repository: `vitamin-deficiency-main`
5. Click **"Connect"**

### Step 3: Configure Web Service

Fill in these settings:

```
Name:              vitamin-deficiency-ai
Environment:       Python 3
Region:            Choose closest to users
Plan:              $7/month (Pro) for all models
                   OR Free for lightweight mode

Build Command:     pip install -r requirements.txt

Start Command:     streamlit run streamlit_app.py \
                   --server.port=$PORT \
                   --server.address=0.0.0.0
```

### Step 4: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

**Add these variables:**

```
LIGHTWEIGHT_MODE           = 0  (set to 1 for free tier)
MAX_MODEL_FILE_MB          = 40
GITHUB_REPO                = YOUR_USERNAME/vitamin-deficiency-main

FIREBASE_API_KEY           = (from .env)
FIREBASE_AUTH_DOMAIN       = (from .env)
FIREBASE_PROJECT_ID        = (from .env)
FIREBASE_STORAGE_BUCKET    = (from .env)
FIREBASE_MESSAGING_SENDER_ID = (from .env)
FIREBASE_APP_ID            = (from .env)

STREAMLIT_LOGGER_LEVEL     = error
STREAMLIT_CLIENT_LOGGER_LEVEL = off
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for build (2-5 minutes)
3. Render will auto-download models from GitHub Release
4. View live at: `https://vitamin-deficiency-ai.onrender.com`

**First deployment takes 5-10 minutes (models download)**  
**Subsequent deploys take 1-2 minutes**

### Health Check

Open service logs and look for:
```
[vitamin-app] Loading models...
[vitamin-app] Loaded: Cnn.h5 (38 MB)
[vitamin-app] Loaded: Mobilenet.h5 (13 MB)
...
```

---

## Streamlit Cloud Deployment

**Pros:** Free tier available  
**Cons:** Limited CPU/RAM

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Ready for Streamlit Cloud"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   ```
   Repository:    YOUR_USERNAME/vitamin-deficiency-main
   Branch:        main
   Main file:     streamlit_app.py
   Python version: 3.11
   ```

### Step 3: Add Environment Variables

Click **"Advanced Settings"** → **"Secrets"**

**Paste:**
```toml
[firebase]
api_key = "YOUR_API_KEY"
auth_domain = "YOUR_AUTH_DOMAIN"
project_id = "YOUR_PROJECT_ID"
storage_bucket = "YOUR_STORAGE_BUCKET"
messaging_sender_id = "YOUR_SENDER_ID"
app_id = "YOUR_APP_ID"

LIGHTWEIGHT_MODE = "1"
MAX_MODEL_FILE_MB = "40"
```

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for initial build
3. View live at: `https://vitamin-deficiency-ai.streamlit.app`

**Note:** Streamlit Cloud auto-enables lightweight mode due to limited RAM

---

## Docker Deployment

### Use Case
- Self-hosted servers
- Kubernetes/Docker Compose
- Private cloud platforms

### Step 1: Create Dockerfile

Already included in project: `Dockerfile`

**Review contents:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
```

### Step 2: Build Docker Image

```bash
# Build image
docker build -t vitamin-ai:latest .

# Tag for registry (optional)
docker tag vitamin-ai:latest YOUR_REGISTRY/vitamin-ai:latest
```

### Step 3: Run Container

```bash
# Local testing
docker run -p 8501:8501 \
  -e LIGHTWEIGHT_MODE=1 \
  -e FIREBASE_API_KEY="YOUR_KEY" \
  -e FIREBASE_PROJECT_ID="YOUR_ID" \
  vitamin-ai:latest

# Access at http://localhost:8501
```

### Step 4: Push to Registry (Optional)

```bash
# Push to Docker Hub
docker push YOUR_USERNAME/vitamin-ai:latest

# Or to private registry
docker push YOUR_REGISTRY/vitamin-ai:latest
```

### Step 5: Deploy on Server

```bash
# Pull and run on server
docker pull YOUR_REGISTRY/vitamin-ai:latest
docker run -d -p 8501:8501 \
  -e LIGHTWEIGHT_MODE=1 \
  -e FIREBASE_API_KEY="YOUR_KEY" \
  --name vitamin-ai \
  YOUR_REGISTRY/vitamin-ai:latest
```

---

## Environment Variables for Cloud

### Required Variables

```bash
# Firebase (required for persistent auth)
FIREBASE_API_KEY              - Your Firebase API key
FIREBASE_AUTH_DOMAIN          - Firebase auth domain
FIREBASE_PROJECT_ID           - Firebase project ID
FIREBASE_STORAGE_BUCKET       - Firebase storage bucket
FIREBASE_MESSAGING_SENDER_ID  - Firebase sender ID
FIREBASE_APP_ID               - Firebase app ID
```

### Optional Variables

```bash
# Model Loading (customize for your hardware)
LIGHTWEIGHT_MODE=1            - Skip heavy models (free tier)
                               Range: 0 (all models) | 1 (light models)

MAX_MODEL_FILE_MB=40          - Max file size to load in MB
                               Range: 10-500 (adjust based on RAM)

GITHUB_REPO=user/repo         - For model auto-download
                               Format: YOUR_USERNAME/REPO_NAME

# Logging
LOG_LEVEL=INFO                - Logging verbosity
DEBUG_MODE=False              - Debug mode toggle

# Platform Detection (auto-set, don't modify)
IS_STREAMLIT_CLOUD=False
IS_RENDER=False
```

### How to Set Variables

**On Render:**
1. Dashboard → Select Service
2. "Settings" → "Environment"
3. Add each variable

**On Streamlit Cloud:**
1. App Settings (gear icon top-right)
2. "Secrets"
3. Edit secrets.toml

**On Docker:**
```bash
docker run -e VARIABLE_NAME="value" ...
```

---

## Post-Deployment Verification

### Test 1: Check App Loads

Visit your deployed URL and verify:
- [ ] Auth gateway appears
- [ ] No error messages in browser console
- [ ] Streamlit sidebar visible

### Test 2: Test Demo Mode

1. Click "Sign Up"
2. Create account with any valid credentials
3. Should redirect to Dashboard
4. Upload test image
5. Should get predictions in 10-15 seconds

### Test 3: Check Logs

**On Render:**
1. Dashboard → Select Service
2. Click "Logs" tab
3. Look for startup messages:
   ```
   Loading models...
   Model Cnn.h5 loaded (38 MB)
   Model Mobilenet.h5 loaded (13 MB)
   ...
   ```

**On Streamlit Cloud:**
1. View deployment logs (gear icon)
2. Look for similar messages

### Test 4: Test with Real Firebase

If Firebase configured:
1. Create new account (provide real email)
2. Verify account created in Firestore (Firebase Console)
3. Log out and log back in
4. Verify session persists
5. Upload image
6. Check prediction stored in Firestore

### Test 5: Monitor Performance

**For first 10 minutes:**
- Check CPU usage (should be < 80%)
- Check memory usage (should be < 90%)
- Check response times (< 5 seconds typical)

**If slow:**
- Check logs for errors
- Reduce number of models (set LIGHTWEIGHT_MODE=1)
- Upgrade to better tier

---

## Monitoring & Troubleshooting

### Slow Predictions (> 10 seconds)

**Cause:** Too many models for available RAM

**Fix:**
```
1. Set LIGHTWEIGHT_MODE=1 in environment variables
2. Or reduce MAX_MODEL_FILE_MB to 30
3. Or upgrade to better hosting tier
```

### "Models failed to load" Error

**Cause:** GitHub Release download failed

**Fix:**
```
1. Check GitHub Release has all 9 files
2. Check GITHUB_REPO variable is correct (format: user/repo)
3. Verify model files < 500MB each
4. Check internet connection on server
5. Manual download: Change download_models.sh path
```

### "Authentication required" Error

**Cause:** Firebase credentials incorrect or missing

**Fix:**
```
1. Verify all 6 Firebase environment variables set
2. Double-check values don't have extra spaces
3. Check Firebase project is active
4. Try demo mode (remove Firebase credentials)
5. Check .env file locally first
```

### App Crashes on Startup

**Check logs for common errors:**

```
"ModuleNotFoundError":
  → Missing dependency in requirements.txt
  → Solution: pip install -r requirements.txt

"OutOfMemory":
  → Too many models for available RAM
  → Solution: Set LIGHTWEIGHT_MODE=1

"ConnectionError":
  → Can't reach Firebase/GitHub
  → Solution: Check internet, firewall, credentials

"Permission denied":
  → Firestore security rules too strict
  → Solution: Update security rules in Firebase Console
```

### High Memory Usage

**If memory usage > 80%:**

1. Set `LIGHTWEIGHT_MODE=1` (loads only small models)
2. Or set `MAX_MODEL_FILE_MB=30` (skip large models)
3. Or restart container/service
4. Or reduce number of concurrent users

### Connection Timeouts

**If predictions time out:**

1. Check model load succeeded in logs
2. Check image size (< 5MB)
3. Check TensorFlow version (should be 2.18.0)
4. Increase timeout in streamlit config

---

## Performance Stats

### Expected Performance by Platform

| Platform | Startup | 1st Prediction | 2nd+ Predictions | RAM Used |
|----------|---------|----------------|------------------|----------|
| Local (Dev) | 2s | 5s | 1s | 800MB |
| Render (Free, Lightweight) | 15s | 8s | 2s | 480MB |
| Render (Pro, All Models) | 20s | 8s | 2s | 1.2GB |
| Streamlit Cloud | 10s | 10s | 3s | 700MB |
| Docker (Local) | 5s | 6s | 1s | 900MB |

---

## Next Steps

1. **Deploy to Render** (recommended)
2. **Test thoroughly** with real users
3. **Monitor logs** for errors
4. **Collect user feedback**
5. **Update models** as data improves

---

**Need help?** Check logs and error messages - they usually tell you exactly what's wrong! 🔍

