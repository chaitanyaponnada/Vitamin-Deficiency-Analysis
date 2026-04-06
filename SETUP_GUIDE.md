# 📚 Vitamin Deficiency AI - Complete Setup & Configuration Guide

**Status:** ✅ Production-Ready  
**Last Updated:** April 2026

---

## 📋 Table of Contents

1. [Quick Start (5 minutes)](#quick-start-5-minutes)
2. [Local Development Setup](#local-development-setup)
3. [Firebase Configuration](#firebase-configuration)
4. [Environment Variables](#environment-variables)
5. [Testing & Verification](#testing--verification)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start (5 minutes)

### Option A: Demo Mode (No Firebase Required)

Perfect for testing without backend setup:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run streamlit_app.py

# 3. Try demo account:
#    Email: test@example.com
#    Password: Demo1234
#    Username: testuser
```

**Features:**
- ✅ Full UI access
- ✅ Image analysis works
- ✅ All 8 models available
- ❌ History lost on app restart (session-only)
- ❌ No persistent user accounts

---

### Option B: Full Setup with Firebase (Recommended for Production)

```bash
# 1. Follow "Firebase Configuration" section below

# 2. Set environment variables in .env file

# 3. Run the app
streamlit run streamlit_app.py
```

**Features:**
- ✅ Persistent user accounts
- ✅ Prediction history in Firestore
- ✅ Multi-user support
- ✅ Production-ready

---

## Local Development Setup

### Prerequisites

```bash
# System requirements
- Python 3.11+
- pip (Python package manager)
- Git (for version control)
```

### Step 1: Clone Repository

```bash
git clone https://github.com/chaitanyaponnada/vitamin-deficiency-main.git
cd vitamin-deficiency-main
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- Streamlit (web framework)
- TensorFlow + Keras (ML)
- Firebase (authentication)
- NumPy, Pandas, Pillow (data processing)
- Plotly (visualizations)

### Step 4: Create .env File

```bash
# Copy template
cp .env.example .env

# Edit .env with your Firebase credentials
# (See "Firebase Configuration" section below)
```

---

## Firebase Configuration

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click **"Add Project"**
3. Enter project name (e.g., "Vitamin-Deficiency-AI")
4. Continue through wizard
5. Create project

### Step 2: Set Up Authentication

**In Firebase Console:**

1. Left sidebar → **Authentication**
2. Click **"Get Started"**
3. Select **"Email/Password"** provider
   - Toggle "Email/Password" **ON**
   - Keep "Email link" **OFF**
   - Click **"Save"**

4. (Optional) Enable **Google OAuth**:
   - Click **"Google"** in providers list
   - Toggle **ON**
   - Select support email
   - Click **"Save"**

### Step 3: Set Up Firestore Database

**In Firebase Console:**

1. Left sidebar → **Firestore Database**
2. Click **"Create Database"**
3. Select **"Start in Test Mode"** (for development)
4. Choose database location (closest to your region)
5. Click **"Create"**

**Create Collections:**

**Collection 1: `users`**
```json
{
  "user_id": "unique_user_id",
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "password_hash": "bcrypt_hash",
  "created_at": timestamp,
  "login_provider": "email",
  "health_score": 75
}
```

**Collection 2: `analysis_{user_id}`** (one collection per user)
```json
{
  "1710451500": {
    "timestamp": "2026-03-15T10:30:45Z",
    "top_prediction": "Vitamin D Deficiency",
    "confidence": 0.92,
    "all_predictions": {class: confidence, ...},
    "model_votes": {model: class, ...},
    "recommendations": "...",
    "analysis_time_ms": 245
  }
}
```

### Step 4: Get Your Credentials

1. Project Settings (gear icon, top-left)
2. Click **"Service Accounts"** tab
3. Click **"Generate New Private Key"** (downloads JSON)
4. Extract these values:

```json
{
  "apiKey": "AIze...",
  "authDomain": "project-id.firebaseapp.com",
  "projectId": "project-id",
  "storageBucket": "project-id.appspot.com",
  "messagingSenderId": "123456789",
  "appId": "1:123456789:web:abc123..."
}
```

### Step 5: Configure Firestore Security Rules

**Go to:** Firestore → Rules tab

**Paste this (Development):**
```firestore
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow users to create/update their own documents
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
    
    // Allow users to access their analysis history
    match /analysis_{userId}/{document=**} {
      allow read, write: if request.auth.uid == userId;
    }
  }
}
```

---

## Environment Variables

### Create `.env` File

Create file `c:\Users\chait\OneDrive\Desktop\CNS\vitamin-deficiency-main\.env`

**Paste this template:**
```bash
# ========== Firebase Configuration ==========
FIREBASE_API_KEY="YOUR_API_KEY"
FIREBASE_AUTH_DOMAIN="YOUR_PROJECT.firebaseapp.com"
FIREBASE_PROJECT_ID="YOUR_PROJECT_ID"
FIREBASE_STORAGE_BUCKET="YOUR_PROJECT.appspot.com"
FIREBASE_MESSAGING_SENDER_ID="123456789"
FIREBASE_APP_ID="1:123456789:web:abc..."

# ========== Model Loading Configuration ==========
# Set to 1 to skip heavy models (EfficientNet, InceptionResNetV2) on low-RAM systems
LIGHTWEIGHT_MODE=0

# Maximum model file size in MB (default: 40MB)
MAX_MODEL_FILE_MB=40

# ========== Deployment Configuration ==========
# Set automatically on cloud platforms (don't modify unless needed)
IS_STREAMLIT_CLOUD=False
IS_RENDER=False

# ========== Logging ==========
LOG_LEVEL=INFO
DEBUG_MODE=False
```

**Fill in concrete values:**
```bash
# Example:
FIREBASE_API_KEY="AIzaSyD1234567890abcdefghijklmnopqrst"
FIREBASE_AUTH_DOMAIN="vitamin-ai.firebaseapp.com"
FIREBASE_PROJECT_ID="vitamin-ai"
```

### Verify Environment Variables Load

Run Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('FIREBASE_API_KEY')
print(f"Loaded: {api_key}")  # Should print your key (truncated)
```

---

## Testing & Verification

### Test 1: Verify Installation

```bash
# Check Streamlit
streamlit --version
# Expected: Streamlit, version 1.28.0 or higher

# Check TensorFlow
python -c "import tensorflow; print(tensorflow.__version__)"
# Expected: 2.18.0 or higher

# Check Firebase
python -c "import firebase_admin; print('Firebase OK')"
# Expected: Firebase OK
```

### Test 2: Run Application

```bash
streamlit run streamlit_app.py
```

**Expected output:**
```
You can now view your Streamlit app in the browser.
Local URL: http://localhost:8501
```

**Open in browser:** Navigate to `http://localhost:8501`

### Test 3: Test Signup

1. Click **"Sign Up"**
2. Fill form:
   ```
   Full Name:       Test User
   Email:           test@example.com
   Username:        testuser123
   Password:        SecurePass123  (8+ chars, 1 uppercase, 1 digit)
   Confirm:         SecurePass123
   ```
3. Click **"Create Account"**
4. Should show success message

### Test 4: Test Login

1. Click **"Login"**
2. Enter credentials:
   ```
   Email/Username:  testuser123
   Password:        SecurePass123
   ```
3. Click **"Sign In"**
4. Should redirect to Dashboard

### Test 5: Test Image Analysis

1. Go to **Analysis Tab**
2. Upload test image (any JPG/PNG)
3. Click **"Run Analysis"**
4. Should see predictions in 5-10 seconds

### Test 6: Test History

1. Go to **History Tab**
2. Should see your analysis from Test 5
3. Click to expand details

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'firebase_admin'"

**Solution:**
```bash
pip install -r requirements.txt
# OR
pip install firebase-admin
```

### Issue: "Authentication required, but user is not authenticated"

**Solution:**
1. Make sure `.env` file exists and has Firebase credentials
2. Try demo mode: No `.env` file needed
3. Check `.env` syntax (no spaces around `=`)

### Issue: "Models failed to load"

**Solution:**
```bash
# Check if model files exist
ls model_saved_files/
# Should show: Cnn.h5, MobileNet.h5, ResNet.h5, VGG16.h5, ...

# Try lightweight mode
# In .env, set: LIGHTWEIGHT_MODE=1
```

### Issue: "app.py:XXX - Unable to connect to Firestore"

**Solution:**
1. Verify internet connection
2. Check Firebase project is active
3. Verify Firebase credentials in `.env`
4. Check Firestore database exists
5. Review security rules (should allow reads/writes)

### Issue: "Port 8501 is already in use"

**Solution:**
```bash
# Use different port
streamlit run streamlit_app.py --server.port 8502
```

### Issue: "Image upload not working"

**Solution:**
1. Check file format (JPG, PNG, BMP)
2. Check file size (< 5MB recommended)
3. Try another image

### Issue: Models loading very slowly

**Solution:**
1. Set `LIGHTWEIGHT_MODE=1` in `.env` (skips heavy models)
2. Or set `MAX_MODEL_FILE_MB=40` to load only small models
3. Or reduce number of models (edit `load_models_with_live_ui()` in streamlit_app.py)

---

## Next Steps

### For Development:
1. ✅ Setup complete
2. Run `streamlit run streamlit_app.py`
3. Start modifying code
4. Test changes locally

### For Deployment:
1. See **DEPLOYMENT_GUIDE.md** for cloud setup
2. Push to GitHub
3. Deploy to Render or Streamlit Cloud

### For Production:
1. Update Firestore security rules from Test Mode to Production
2. Enable monitoring in Firebase Console
3. Set up backups
4. Configure email notifications
5. Test load with multiple users

---

## Project Structure Quick Reference

```
vitamin-deficiency-main/
├── streamlit_app.py              ← Main application
├── auth_ui_modern.py             ← Login/signup UI
├── firebase_auth.py              ← Backend auth
├── cookie_manager.py             ← Persistent login
├── ui_components.py              ← Design system & CSS
│
├── model_saved_files/            ← Pre-trained models
│   ├── Cnn.h5
│   ├── Mobilenet.h5
│   ├── ResNet.h5
│   ├── VGG16.h5
│   ├── InceptionV3.h5
│   ├── Xception.h5
│   ├── InceptionResNetV2.h5
│   ├── EfficientNetV2L.h5
│   └── ensemble_metadata.json
│
├── models/                       ← Training notebooks
│   ├── cnn.ipynb
│   ├── Mobilenet.ipynb
│   ├── resnet.ipynb
│   ├── vgg16.ipynb
│   ├── InceptionV3.ipynb
│   ├── xception.ipynb
│   ├── InceptionResNetV2.ipynb
│   ├── EfficientNetV2L.ipynb
│   └── ensemble.ipynb
│
├── dataset/                      ← Training images
│   ├── train/                    (14 classes)
│   └── test/                     (14 classes)
│
├── .env                          ← Firebase credentials (NOT in git)
├── .env.example                  ← Template
├── requirements.txt              ← Python dependencies
├── runtime.txt                   ← Python version
│
└── Documentation/
    ├── README.md                 ← Project overview
    ├── SETUP_GUIDE.md           ← THIS FILE (setup & config)
    ├── DEPLOYMENT_GUIDE.md      ← Cloud deployment
    └── PROJECT_ANALYSIS_COMPLETE.md ← Full technical details
```

---

## Support

**Questions?** Check:
1. **README.md** - Project overview
2. **PROJECT_ANALYSIS_COMPLETE.md** - Technical details
3. **DEPLOYMENT_GUIDE.md** - Deployment help

**Still stuck?** 
- Review error messages carefully
- Check `.env` file is properly formatted
- Verify all Firebase services are enabled
- Test in Demo Mode first

---

**Happy analyzing! 🚀**

