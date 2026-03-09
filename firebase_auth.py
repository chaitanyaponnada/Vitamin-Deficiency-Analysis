"""
Firebase Authentication and Firestore integration for Vitamin Deficiency AI.
Handles user registration, login, profile management, and prediction history.
"""

import os
import re
import hashlib
from datetime import datetime
from typing import Dict, Optional, Tuple
import requests
import json

import streamlit as st


def get_firebase_config() -> Dict:
    """Load Firebase configuration from environment variables."""
    config = {
        'api_key': os.getenv('FIREBASE_API_KEY', st.secrets.get('FIREBASE_API_KEY', '')),
        'auth_domain': os.getenv('FIREBASE_AUTH_DOMAIN', st.secrets.get('FIREBASE_AUTH_DOMAIN', '')),
        'project_id': os.getenv('FIREBASE_PROJECT_ID', st.secrets.get('FIREBASE_PROJECT_ID', '')),
        'storage_bucket': os.getenv('FIREBASE_STORAGE_BUCKET', st.secrets.get('FIREBASE_STORAGE_BUCKET', '')),
        'messaging_sender_id': os.getenv('FIREBASE_MESSAGING_SENDER_ID', st.secrets.get('FIREBASE_MESSAGING_SENDER_ID', '')),
        'app_id': os.getenv('FIREBASE_APP_ID', st.secrets.get('FIREBASE_APP_ID', '')),
    }
    
    # For demo mode: allow app to work without Firebase if env vars not set
    demo_mode = not all([config['api_key'], config['project_id']])
    if demo_mode:
        st.warning("Firebase not configured. Running in demo mode with local authentication.")
    
    return config


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_password(password: str) -> Tuple[bool, str]:
    """Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one number
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    return True, "Password is valid."


def is_valid_username(username: str) -> Tuple[bool, str]:
    """Validate username format."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if len(username) > 20:
        return False, "Username must be at most 20 characters long."
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens."
    return True, "Username is valid."


# Demo database for when Firebase is not configured
_DEMO_USERS = {}
_DEMO_ANALYSIS_HISTORY = {}


def signup_user(email: str, password: str, full_name: str, username: str) -> Tuple[bool, str]:
    """Register a new user.
    
    Returns:
        (success, message)
    """
    config = get_firebase_config()
    
    # Validate inputs
    if not is_valid_email(email):
        return False, "Invalid email format."
    
    valid_pwd, pwd_msg = is_valid_password(password)
    if not valid_pwd:
        return False, pwd_msg
    
    valid_user, user_msg = is_valid_username(username)
    if not valid_user:
        return False, user_msg
    
    if len(full_name.strip()) < 2:
        return False, "Full name must be at least 2 characters."
    
    # Demo mode
    if not config['api_key']:
        if email in _DEMO_USERS:
            return False, "Email already registered."
        if any(u['username'] == username for u in _DEMO_USERS.values()):
            return False, "Username already taken."
        
        user_id = hashlib.md5(email.encode()).hexdigest()[:12]
        _DEMO_USERS[email] = {
            'user_id': user_id,
            'email': email,
            'full_name': full_name,
            'username': username,
            'password_hash': hashlib.sha256(password.encode()).hexdigest(),
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'login_provider': 'email'
        }
        return True, "Signup successful! Please log in."
    
    # Firebase mode
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={config['api_key']}"
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            return False, f"Signup failed: {error_msg}"
        
        user_id = data.get('localId', '')
        
        # Store additional user profile in Firestore
        firestore_success = create_user_profile(
            user_id=user_id,
            email=email,
            full_name=full_name,
            username=username,
            login_provider='email'
        )
        
        if not firestore_success:
            return False, "Profile creation failed."
        
        return True, "Signup successful! Please log in."
    
    except Exception as e:
        return False, f"Signup error: {str(e)}"


def login_user(email_or_username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """Authenticate user with email/username and password.
    
    Returns:
        (success, message, user_data)
    """
    config = get_firebase_config()
    
    # Demo mode
    if not config['api_key']:
        user_data = None
        # Try email
        if email_or_username in _DEMO_USERS:
            user_data = _DEMO_USERS[email_or_username]
        # Try username
        else:
            for user in _DEMO_USERS.values():
                if user['username'] == email_or_username:
                    user_data = user
                    break
        
        if not user_data:
            return False, "User not found.", None
        
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        if user_data['password_hash'] != pwd_hash:
            return False, "Incorrect password.", None
        
        user_data['last_login'] = datetime.now().isoformat()
        return True, "Login successful.", {
            'user_id': user_data['user_id'],
            'email': user_data['email'],
            'username': user_data['username'],
            'full_name': user_data['full_name'],
            'login_provider': 'email',
            'photo_url': user_data.get('photo_url', ''),
        }
    
    # Firebase mode
    try:
        # Try as email first
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={config['api_key']}"
        payload = {
            'email': email_or_username,
            'password': password,
            'returnSecureToken': True
        }
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            return False, "Invalid email/password.", None
        
        user_id = data.get('localId', '')
        email = data.get('email', email_or_username)
        
        # Fetch user profile from Firestore
        user_profile = get_user_profile(user_id)
        if not user_profile:
            return False, "Profile not found.", None
        
        return True, "Login successful.", {
            'user_id': user_id,
            'email': email,
            'username': user_profile.get('username', ''),
            'full_name': user_profile.get('full_name', ''),
            'login_provider': 'email',
            'photo_url': user_profile.get('photo_url', ''),
        }
    
    except Exception as e:
        return False, f"Login error: {str(e)}", None


def login_with_google(id_token: str) -> Tuple[bool, str, Optional[Dict]]:
    """Authenticate user with Google ID token.
    
    Args:
        id_token: Google ID token from OAuth flow
        
    Returns:
        (success, message, user_data)
    """
    config = get_firebase_config()
    
    # Demo mode - simulate Google login
    if not config['api_key']:
        st.warning("Google Sign-In not available in demo mode. Please configure Firebase.")
        return False, "Google Sign-In requires Firebase configuration.", None
    
    try:
        # Verify ID token with Firebase
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={config['api_key']}"
        request_uri = f"https://{config['auth_domain']}" if config.get('auth_domain') else "http://localhost"
        payload = {
            'postBody': f'id_token={id_token}&providerId=google.com',
            'requestUri': request_uri,
            'returnIdpCredential': True,
            'returnSecureToken': True
        }
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            error_msg = data.get('error', {}).get('message', 'Google Sign-In failed')
            return False, error_msg, None
        
        user_id = data.get('localId', '')
        email = data.get('email', '')
        display_name = data.get('displayName', email.split('@')[0])
        photo_url = data.get('photoUrl', '')
        
        # Check if profile exists
        user_profile = get_user_profile(user_id)
        
        if not user_profile:
            # Create new profile for Google user
            username = email.split('@')[0].lower()
            # Ensure username is unique
            base_username = username
            counter = 1
            # In production, you'd check Firestore for uniqueness
            while False:  # Placeholder for uniqueness check
                username = f"{base_username}{counter}"
                counter += 1
            
            create_user_profile(
                user_id=user_id,
                email=email,
                full_name=display_name,
                username=username,
                login_provider='google',
                photo_url=photo_url,
            )
            
            user_profile = {
                'user_id': user_id,
                'email': email,
                'full_name': display_name,
                'username': username,
                'login_provider': 'google',
                'photo_url': photo_url,
            }
        
        return True, "Google Sign-In successful.", {
            'user_id': user_id,
            'email': email,
            'username': user_profile.get('username', email.split('@')[0]),
            'full_name': user_profile.get('full_name', display_name),
            'login_provider': 'google',
            'photo_url': user_profile.get('photo_url', photo_url),
        }
    
    except Exception as e:
        return False, f"Google Sign-In error: {str(e)}", None


def create_user_profile(user_id: str, email: str, full_name: str, username: str, login_provider: str = 'email', photo_url: str = '') -> bool:
    """Create user profile in Firestore."""
    config = get_firebase_config()
    
    # Demo mode
    if not config['project_id']:
        _DEMO_USERS[email] = _DEMO_USERS.get(email, {})
        _DEMO_USERS[email].update({
            'user_id': user_id,
            'email': email,
            'full_name': full_name,
            'username': username,
            'photo_url': photo_url,
            'created_at': datetime.now().isoformat(),
        })
        return True
    
    # Firebase mode
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{config['project_id']}/databases/(default)/documents/users/{user_id}"
        payload = {
            'fields': {
                'user_id': {'stringValue': user_id},
                'email': {'stringValue': email},
                'full_name': {'stringValue': full_name},
                'username': {'stringValue': username},
                'photo_url': {'stringValue': photo_url},
                'created_at': {'stringValue': datetime.now().isoformat()},
                'last_login': {'stringValue': datetime.now().isoformat()},
                'login_provider': {'stringValue': login_provider},
            }
        }
        response = requests.patch(url, json=payload, timeout=10)
        return response.status_code in [200, 201]
    except Exception:
        return False


def get_user_profile(user_id: str) -> Optional[Dict]:
    """Fetch user profile from Firestore."""
    config = get_firebase_config()
    
    # Demo mode
    if not config['project_id']:
        for user in _DEMO_USERS.values():
            if user.get('user_id') == user_id:
                return user
        return None
    
    # Firebase mode
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{config['project_id']}/databases/(default)/documents/users/{user_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        fields = data.get('fields', {})
        
        return {
            'user_id': fields.get('user_id', {}).get('stringValue', ''),
            'email': fields.get('email', {}).get('stringValue', ''),
            'full_name': fields.get('full_name', {}).get('stringValue', ''),
            'username': fields.get('username', {}).get('stringValue', ''),
            'photo_url': fields.get('photo_url', {}).get('stringValue', ''),
            'created_at': fields.get('created_at', {}).get('stringValue', ''),
            'last_login': fields.get('last_login', {}).get('stringValue', ''),
        }
    except Exception:
        return None


def store_analysis(user_id: str, image_name: str, predicted_condition: str, 
                  vitamin_deficiency: str, confidence_score: float) -> bool:
    """Store analysis result in Firestore."""
    config = get_firebase_config()
    
    analysis_id = hashlib.md5(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    
    # Demo mode
    if not config['project_id']:
        if user_id not in _DEMO_ANALYSIS_HISTORY:
            _DEMO_ANALYSIS_HISTORY[user_id] = []
        
        _DEMO_ANALYSIS_HISTORY[user_id].append({
            'analysis_id': analysis_id,
            'user_id': user_id,
            'image_name': image_name,
            'predicted_condition': predicted_condition,
            'vitamin_deficiency': vitamin_deficiency,
            'confidence_score': confidence_score,
            'timestamp': datetime.now().isoformat(),
        })
        return True
    
    # Firebase mode
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{config['project_id']}/databases/(default)/documents/analysis_history/{analysis_id}"
        payload = {
            'fields': {
                'analysis_id': {'stringValue': analysis_id},
                'user_id': {'stringValue': user_id},
                'image_name': {'stringValue': image_name},
                'predicted_condition': {'stringValue': predicted_condition},
                'vitamin_deficiency': {'stringValue': vitamin_deficiency},
                'confidence_score': {'doubleValue': confidence_score},
                'timestamp': {'stringValue': datetime.now().isoformat()},
            }
        }
        response = requests.patch(url, json=payload, timeout=10)
        return response.status_code in [200, 201]
    except Exception:
        return False


def get_analysis_history(user_id: str) -> list:
    """Fetch all analyses for a user from Firestore."""
    config = get_firebase_config()
    
    # Demo mode
    if not config['project_id']:
        return _DEMO_ANALYSIS_HISTORY.get(user_id, [])
    
    # Firebase mode
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{config['project_id']}/databases/(default)/documents/analysis_history"
        params = {
            'pageSize': 100,
        }
        # Note: Real implementation would need proper query filters
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        documents = data.get('documents', [])
        
        histories = []
        for doc in documents:
            fields = doc.get('fields', {})
            if fields.get('user_id', {}).get('stringValue') == user_id:
                histories.append({
                    'analysis_id': fields.get('analysis_id', {}).get('stringValue', ''),
                    'image_name': fields.get('image_name', {}).get('stringValue', ''),
                    'predicted_condition': fields.get('predicted_condition', {}).get('stringValue', ''),
                    'confidence_score': fields.get('confidence_score', {}).get('doubleValue', 0),
                    'timestamp': fields.get('timestamp', {}).get('stringValue', ''),
                })
        
        return sorted(histories, key=lambda x: x['timestamp'], reverse=True)
    except Exception:
        return []
