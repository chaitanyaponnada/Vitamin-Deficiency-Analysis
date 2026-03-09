# Firebase Authentication Setup Guide

## Overview

The Vitamin Deficiency AI application now includes a complete authentication and user management system powered by Firebase Authentication and Firestore. Users must create an account and log in to access the AI analysis features.

## Features

### Authentication
- **Email/Password Registration**: Users can sign up with email, password, and profile information
- **Email/Password Login**: Existing users can log in with their credentials
- **Google OAuth** (Coming Soon): One-click login with Google accounts
- **Session Management**: Secure session state management using Streamlit session state
- **Password Validation**: Enforced password requirements (8+ chars, 1 uppercase, 1 number)

### User Management
- **Profile Dashboard**: View profile information and account details
- **Profile Menu**: Top-right corner menu for quick access to profile, history, and logout
- **Account Creation Date**: Track when user account was created

### Prediction History
- **Automatic History Tracking**: Every analysis is automatically stored in Firestore
- **History Tab**: View all past analyses with predictions, confidence scores, and timestamps
- **Dashboard Statistics**: Quick stats on total analyses, last analysis date, and most detected conditions

### Security
- Passwords are hashed before storage
- Email uniqueness validation during registration
- Username uniqueness validation
- Input sanitization and validation
- Demo mode for development without Firebase

## Firebase Setup Instructions

### 1. Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Add Project" or select existing project
3. Enter project name (e.g., "Vitamin-Deficiency-AI")
4. Continue through setup wizard
5. Enable Google Analytics (optional)
6. Create project

### 2. Set Up Firebase Authentication

1. In Firebase Console, go to **Authentication** (left sidebar)
2. Click **Get Started**
3. Select **Email/Password**:
   - Enable "Email/Password" provider
   - Keep "Email link (passwordless sign-in)" disabled
   - Click "Save"

4. (Optional) Enable **Google** provider:
   - Click "Google" in providers list
   - Enable it
   - Select your support email
   - Save

### 3. Set Up Cloud Firestore

1. In Firebase Console, go to **Firestore Database**
2. Click **Create Database**
3. Select "Start in Test Mode" (for development)
4. Choose database location (recommend closest to users)
5. Click "Create"

6. Create Collections:

   **Collection 1: `users`**
   - Click "Start Collection"
   - Name: `users`
   - Document ID: Auto-ID
   - Add sample document with fields:
     ```
     user_id (string)
     email (string)
     full_name (string)
     username (string)
     created_at (timestamp)
     last_login (timestamp)
     login_provider (string)
     ```

   **Collection 2: `analysis_history`**
   - Click "Start Collection"
   - Name: `analysis_history`
   - Document ID: Auto-ID
   - Add sample document with fields:
     ```
     analysis_id (string)
     user_id (string)
     image_name (string)
     predicted_condition (string)
     vitamin_deficiency (string)
     confidence_score (number)
     timestamp (timestamp)
     ```

### 4. Get Firebase Credentials

1. In Firebase Console, click the **gear icon** (Settings) → **Project Settings**
2. Go to **Service Accounts** tab
3. Under "Firebase SDK snippet", select "Web"
4. Copy the configuration object (contains all needed credentials):
   ```javascript
   const firebaseConfig = {
     apiKey: "YOUR_API_KEY",
     authDomain: "YOUR_AUTH_DOMAIN",
     projectId: "YOUR_PROJECT_ID",
     storageBucket: "YOUR_STORAGE_BUCKET",
     messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
     appId: "YOUR_APP_ID"
   };
   ```

### 5. Configure Environment Variables

#### Option A: Using .env File (Local Development)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in Firebase credentials from step 4:
   ```
   FIREBASE_API_KEY=YOUR_API_KEY
   FIREBASE_AUTH_DOMAIN=YOUR_AUTH_DOMAIN
   FIREBASE_PROJECT_ID=YOUR_PROJECT_ID
   FIREBASE_STORAGE_BUCKET=YOUR_STORAGE_BUCKET
   FIREBASE_MESSAGING_SENDER_ID=YOUR_MESSAGING_SENDER_ID
   FIREBASE_APP_ID=YOUR_APP_ID
   ```

3. Install python-dotenv:
   ```bash
   pip install python-dotenv
   ```

4. Add to top of streamlit_app.py (after imports):
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

#### Option B: Using Streamlit Secrets (Recommended for Deployment)

1. Create `.streamlit/secrets.toml` file:
   ```toml
   FIREBASE_API_KEY = "YOUR_API_KEY"
   FIREBASE_AUTH_DOMAIN = "YOUR_AUTH_DOMAIN"
   FIREBASE_PROJECT_ID = "YOUR_PROJECT_ID"
   FIREBASE_STORAGE_BUCKET = "YOUR_STORAGE_BUCKET"
   FIREBASE_MESSAGING_SENDER_ID = "YOUR_MESSAGING_SENDER_ID"
   FIREBASE_APP_ID = "YOUR_APP_ID"
   ```

2. On Render/Streamlit Cloud, set environment variables in deployment settings

#### Option C: Using System Environment Variables

```bash
export FIREBASE_API_KEY="YOUR_API_KEY"
export FIREBASE_AUTH_DOMAIN="YOUR_AUTH_DOMAIN"
export FIREBASE_PROJECT_ID="YOUR_PROJECT_ID"
export FIREBASE_STORAGE_BUCKET="YOUR_STORAGE_BUCKET"
export FIREBASE_MESSAGING_SENDER_ID="YOUR_MESSAGING_SENDER_ID"
export FIREBASE_APP_ID="YOUR_APP_ID"
```

### 6. Configure Firestore Security Rules (Production)

In Firestore Console, go to **Rules** tab and set rules to prevent unauthorized access:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection - only allow reading own profile
    match /users/{userId} {
      allow read: if request.auth.uid == userId;
      allow create: if request.auth.uid != null;
      allow update: if request.auth.uid == userId;
    }
    
    // Analysis history - only allow reading own analyses
    match /analysis_history/{document=**} {
      allow read: if request.auth.uid == resource.data.user_id;
      allow create: if request.auth.uid == request.resource.data.user_id;
    }
  }
}
```

## How It Works

### Authentication Flow

1. **User Opens App**
   - `streamlit_app.py` calls `show_authentication_gateway()`
   - User sees login/signup menu

2. **Signup**
   - User fills signup form
   - `firebase_auth.py` validates inputs
   - User created in Firebase Authentication
   - User profile created in Firestore `users` collection

3. **Login**
   - User enters email/username and password
   - Firebase Authentication validates credentials
   - User profile loaded from Firestore
   - Session state set to authenticated

4. **Main App Access**
   - Dashboard displayed with statistics
   - User can analyze images
   - Each analysis automatically stored in Firestore

### Session State Variables

```python
st.session_state.is_authenticated  # Boolean: True if user logged in
st.session_state.user_data  # Dict with user_id, email, username, full_name
st.session_state.load_status  # Model loading status from startup
st.session_state.show_profile_menu  # Toggle profile dropdown menu
st.session_state.profile_page  # Current profile view (profile/history)
```

### Storage Structure

**Firestore Collections:**

```
users/
  {user_id}/
    - user_id: string
    - email: string
    - full_name: string
    - username: string
    - created_at: timestamp
    - last_login: timestamp
    - login_provider: string

analysis_history/
  {analysis_id}/
    - analysis_id: string
    - user_id: string
    - image_name: string
    - predicted_condition: string
    - vitamin_deficiency: string
    - confidence_score: number
    - timestamp: timestamp
```

## Demo Mode (Without Firebase)

The application works without Firebase configured! When Firebase credentials are missing:

- **Demo Mode Enabled**: Uses in-memory storage instead
- **Demo Users**: Pre-populated with demo credentials
- **No History Persistence**: Data lost when app restarts
- **Perfect for**: Testing UI, development, demos

Login with demo credentials (automatically created on first signup):
- Email: any email address
- Password: Any8Char1 (format: 8+ chars, 1 uppercase, 1 number)

## Testing the Authentication

### Local Testing

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure Firebase (if using) or use demo mode
# Set environment variables or create .streamlit/secrets.toml

# 3. Run Streamlit app
streamlit run streamlit_app.py

# 4. Try signup/login
# App will show authentication gateway first
```

### Deployment Testing

1. **Render** (Recommended):
   - Set Firebase environment variables in Render dashboard
   - Deploy normally - app will use Firebase automatically

2. **Streamlit Cloud**:
   - Create `App secrets` section
   - Add Firebase configuration
   - Deploy and test

## Troubleshooting

### Firebase Not Configured / Demo Mode Active

**Issue**: App shows "Running in demo mode with local authentication"

**Solution**: 
- Check that Firebase credentials are set in environment variables
- Ensure all 6 Firebase config variables are present
- Verify credentials are correct

### "User not found" Login Error

**Possible causes**:
- User hasn't signed up yet
- Wrong email or username
- Typo in credentials

**Solution**: Have user sign up first

### "Password does not match" Signup Error

**Requirements**:
- At least 8 characters
- At least one UPPERCASE letter
- At least one number (0-9)

**Example valid passwords**: `MyPass123`, `Secure#Pass1`

### History Not Showing

**Check**:
1. User is authenticated (check Dashboard loads)
2. Firebase is configured and Firestore is accessible
3. Analysis predictions have been made
4. Check Firestore console for `analysis_history` collection

### Profile Menu Not Appearing

**Solution**:
1. Clear browser cache
2. Restart Streamlit app (`Ctrl+C`, then `streamlit run streamlit_app.py`)
3. Refresh browser

## File Structure

```
vitamin-deficiency-main/
├── streamlit_app.py         # Main application (modified with auth)
├── firebase_auth.py         # Firebase authentication logic
├── auth_ui.py              # Authentication UI pages
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── secrets.toml       # Streamlit secrets (create for deployment)
└── .gitignore            # Should include .env and .streamlit/secrets.toml
```

## Next Steps

1. **Complete Firebase Setup**: Follow "Firebase Setup Instructions" above
2. **Test Locally**: Run app locally and test signup/login
3. **Deploy to Render**: Configure environment variables and deploy
4. **Test in Production**: Create test account on deployed app
5. **Customize**: Modify authentication pages to match brand guidelines

## Support

For issues with:
- **Firebase Setup**: See [Firebase Documentation](https://firebase.google.com/docs)
- **Streamlit**: See [Streamlit Documentation](https://docs.streamlit.io)
- **This App**: Check `streamlit_app.py` comments and error messages

## Security Best Practices

✅ **DO**:
- Store credentials in environment variables or Streamlit secrets
- Use HTTPS in production
- Enable Firestore security rules (see above)
- Hash passwords (done automatically by Firebase)
- Validate all user inputs

❌ **DON'T**:
- Commit Firebase credentials to GitHub
- Use the same password for multiple accounts
- Share API keys or credentials
- Store plain-text passwords
- Run app with overly permissive Firestore rules
