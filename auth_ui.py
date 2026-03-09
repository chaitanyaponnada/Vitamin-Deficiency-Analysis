"""
Authentication UI pages for Vitamin Deficiency AI.
Handles login, signup, and Google authentication screens.
"""

import streamlit as st
from firebase_auth import (
    signup_user, login_user, is_valid_email, 
    is_valid_password, is_valid_username
)


def show_login_page():
    """Display the login page."""
    st.markdown("""
        <style>
            .auth-container {
                max-width: 450px;
                margin: 60px auto;
                padding: 40px;
                border-radius: 14px;
                background: rgba(255, 255, 255, 0.95);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
            }
            .auth-title {
                text-align: center;
                font-size: 2.2rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 8px;
            }
            .auth-subtitle {
                text-align: center;
                font-size: 0.95rem;
                color: #64748b;
                margin-bottom: 32px;
            }
            .auth-input {
                width: 100%;
                padding: 10px 14px;
                border: 1.5px solid #e2e8f0;
                border-radius: 8px;
                font-size: 0.95rem;
                margin-bottom: 14px;
            }
            .auth-button {
                width: 100%;
                padding: 11px;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .auth-button-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin-bottom: 12px;
            }
            .auth-button-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            .auth-divider {
                text-align: center;
                margin: 24px 0;
                font-size: 0.85rem;
                color: #94a3b8;
            }
            .auth-link {
                text-align: center;
                margin-top: 20px;
                font-size: 0.9rem;
                color: #64748b;
            }
            .auth-link a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="auth-container">
            <div class="auth-title">Welcome Back</div>
            <div class="auth-subtitle">Sign in to your Vitamin Deficiency AI account</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Back to Menu", use_container_width=True):
            st.session_state.auth_page = "menu"
            st.rerun()
    
    with col2:
        if st.button("Sign Up →", use_container_width=True):
            st.session_state.auth_page = "signup"
            st.rerun()

    st.divider()

    email_or_username = st.text_input(
        "Email or Username",
        placeholder="Enter your email or username",
        key="login_email"
    )
    
    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password"
    )

    if st.button("Login", use_container_width=True, type="primary"):
        if not email_or_username.strip():
            st.error("Please enter your email or username.")
        elif not password.strip():
            st.error("Please enter your password.")
        else:
            success, message, user_data = login_user(email_or_username, password)
            
            if success:
                st.session_state.is_authenticated = True
                st.session_state.user_data = user_data
                st.session_state.auth_page = None
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    st.markdown("""
        <div class="auth-divider">Or continue with</div>
    """, unsafe_allow_html=True)

    if st.button("🔵 Continue with Google", use_container_width=True):
        st.info("Google login feature coming soon!")

    st.markdown("""
        </div>
    """, unsafe_allow_html=True)


def show_signup_page():
    """Display the signup page."""
    st.markdown("""
        <style>
            .auth-container {
                max-width: 450px;
                margin: 40px auto;
                padding: 40px;
                border-radius: 14px;
                background: rgba(255, 255, 255, 0.95);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
            }
            .auth-title {
                text-align: center;
                font-size: 2.2rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 8px;
            }
            .auth-subtitle {
                text-align: center;
                font-size: 0.95rem;
                color: #64748b;
                margin-bottom: 28px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="auth-container">
            <div class="auth-title">Create Account</div>
            <div class="auth-subtitle">Join Vitamin Deficiency AI today</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Back to Menu", use_container_width=True):
            st.session_state.auth_page = "menu"
            st.rerun()
    
    with col2:
        if st.button("Login →", use_container_width=True):
            st.session_state.auth_page = "login"
            st.rerun()

    st.divider()

    full_name = st.text_input(
        "Full Name",
        placeholder="Enter your full name",
        key="signup_name"
    )
    
    email = st.text_input(
        "Email Address",
        placeholder="Enter your email",
        key="signup_email"
    )
    
    username = st.text_input(
        "Username",
        placeholder="Choose a username (3-20 characters)",
        key="signup_username"
    )
    
    password = st.text_input(
        "Password",
        type="password",
        placeholder="At least 8 characters, 1 uppercase, 1 number",
        key="signup_password"
    )
    
    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Re-enter your password",
        key="signup_confirm"
    )

    if st.button("Create Account", use_container_width=True, type="primary"):
        errors = []
        
        if not full_name.strip():
            errors.append("Full name is required.")
        if not email.strip():
            errors.append("Email is required.")
        elif not is_valid_email(email):
            errors.append("Invalid email format.")
        if not username.strip():
            errors.append("Username is required.")
        else:
            valid, msg = is_valid_username(username)
            if not valid:
                errors.append(msg)
        if not password:
            errors.append("Password is required.")
        else:
            valid, msg = is_valid_password(password)
            if not valid:
                errors.append(msg)
        if password != confirm_password:
            errors.append("Passwords do not match.")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            success, message = signup_user(email, password, full_name, username)
            if success:
                st.success(message)
                st.info("Redirecting to login...")
                import time
                time.sleep(2)
                st.session_state.auth_page = "login"
                st.rerun()
            else:
                st.error(message)

    st.markdown("""
        </div>
    """, unsafe_allow_html=True)


def show_auth_menu():
    """Display the main authentication menu."""
    st.markdown("""
        <style>
            .auth-menu-container {
                max-width: 500px;
                margin: 100px auto;
                text-align: center;
            }
            .auth-logo {
                font-size: 3.5rem;
                margin-bottom: 24px;
            }
            .auth-title {
                font-size: 2.8rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 8px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .auth-subtitle {
                font-size: 1.1rem;
                color: #64748b;
                margin-bottom: 48px;
            }
            .auth-button-group {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="auth-menu-container">
            <div class="auth-logo">🩺</div>
            <div class="auth-title">Vitamin Deficiency AI</div>
            <div class="auth-subtitle">Detect nutrient deficiencies from images using AI</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.2, 2.6, 1.2])
    
    with col2:
        if st.button("👤 Login", use_container_width=True, key="btn_login"):
            st.session_state.auth_page = "login"
            st.rerun()
        
        if st.button("✍️ Sign Up", use_container_width=True, key="btn_signup"):
            st.session_state.auth_page = "signup"
            st.rerun()
        
        if st.button("🔵 Continue with Google", use_container_width=True, key="btn_google"):
            st.info("Google authentication coming soon!")


def show_authentication_gateway():
    """Main authentication gateway - shows login/signup/menu based on state."""
    
    # Initialize auth page state
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = "menu"
    
    st.set_page_config(
        page_title="Vitamin Deficiency AI - Login",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # Set theme background
    st.markdown("""
        <style>
            body, [data-testid="stAppViewContainer"] {
                background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            }
            [data-testid="stHeader"] {
                background: transparent;
            }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.auth_page == "login":
        show_login_page()
    elif st.session_state.auth_page == "signup":
        show_signup_page()
    else:
        show_auth_menu()
