"""
Modern Authentication UI for Production SaaS Application.
Clean, minimal, glassmorphism design with Google Sign-In.
"""

import streamlit as st
from firebase_auth import (
    signup_user, login_user, login_with_google,
    is_valid_email, is_valid_password, is_valid_username
)


def inject_auth_styles():
    """Inject modern authentication page styles."""
    st.markdown("""
        <style>
            /* Auth Page Container */
            .auth-page {
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
            }
            
            /* Auth Card */
            .auth-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-radius: 24px;
                padding: 3rem;
                max-width: 480px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            
            /* Logo */
            .auth-logo {
                text-align: center;
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                color: #0f172a;
                letter-spacing: -0.02em;
            }
            
            .auth-logo-accent {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            /* Title */
            .auth-title {
                text-align: center;
                font-size: 1.75rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 0.5rem;
                margin-top: 2rem;
            }
            
            .auth-subtitle {
                text-align: center;
                font-size: 1rem;
                color: #64748b;
                margin-bottom: 2rem;
            }
            
            /* Form Elements */
            .stTextInput > div > div > input {
                border-radius: 12px;
                border: 1.5px solid #e2e8f0;
                padding: 0.75rem 1rem;
                font-size: 1rem;
                transition: all 0.2s ease;
            }
            
            .stTextInput > div > div > input:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            /* Auth Buttons */
            .auth-button-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0.875rem 2rem;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
                margin-top: 1rem;
            }
            
            .auth-button-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
            }
            
            .auth-button-google {
                background: white;
                color: #334155;
                border: 1.5px solid #e2e8f0;
                border-radius: 12px;
                padding: 0.875rem 2rem;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                width: 100%;
                margin-top: 1rem;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.75rem;
            }
            
            .auth-button-google:hover {
                border-color: #667eea;
                background: #f8fafc;
            }
            
            .auth-button-secondary {
                background: transparent;
                color: #667eea;
                border: 1.5px solid #667eea;
                border-radius: 12px;
                padding: 0.75rem 1.5rem;
                font-size: 0.95rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                width: 100%;
                margin-top: 0.75rem;
            }
            
            .auth-button-secondary:hover {
                background: rgba(102, 126, 234, 0.05);
            }
            
            /* Divider */
            .auth-divider {
                display: flex;
                align-items: center;
                text-align: center;
                margin: 1.5rem 0;
                color: #94a3b8;
                font-size: 0.875rem;
            }
            
            .auth-divider::before,
            .auth-divider::after {
                content: '';
                flex: 1;
                border-bottom: 1px solid #e2e8f0;
            }
            
            .auth-divider:not(:empty)::before {
                margin-right: 1rem;
            }
            
            .auth-divider:not(:empty)::after {
                margin-left: 1rem;
            }
            
            /* Link */
            .auth-link {
                text-align: center;
                margin-top: 1.5rem;
                font-size: 0.95rem;
                color: #64748b;
            }
            
            .auth-link a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
            }
            
            .auth-link a:hover {
                text-decoration: underline;
            }
        </style>
    """, unsafe_allow_html=True)


def show_auth_menu():
    """Display main authentication menu."""
    inject_auth_styles()
    
    st.markdown("""
        <div class="auth-card">
            <div class="auth-logo">
                <span>Vitamin</span><span class="auth-logo-accent">AI</span>
            </div>
            <div class="auth-title">Welcome</div>
            <div class="auth-subtitle">AI-powered vitamin deficiency analysis</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign In", key="btn_signin", use_container_width=True, type="primary"):
            st.session_state.auth_page = "login"
            st.rerun()
        
        if st.button("Create Account", key="btn_signup", use_container_width=True):
            st.session_state.auth_page = "signup"
            st.rerun()
        
        st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
        
        # Google Sign-In Button (placeholder - requires OAuth flow)
        if st.button("🔐 Continue with Google", key="btn_google", use_container_width=True):
            st.info("Google Sign-In requires OAuth configuration. Coming soon...")
            # In production, this would trigger OAuth flow:
            # 1. Redirect to Google OAuth
            # 2. Get ID token
            # 3. Call login_with_google(id_token)


def show_login_page():
    """Display modern login page."""
    inject_auth_styles()
    
    st.markdown("""
        <div class="auth-card">
            <div class="auth-logo">
                <span>Vitamin</span><span class="auth-logo-accent">AI</span>
            </div>
            <div class="auth-title">Sign In</div>
            <div class="auth-subtitle">Welcome back! Please sign in to continue</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Login Form
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
        
        if st.button("Sign In", key="do_login", use_container_width=True, type="primary"):
            if not email_or_username or not password:
                st.error("Please fill in all fields.")
            else:
                with st.spinner("Signing in..."):
                    success, message, user_data = login_user(email_or_username, password)
                    
                    if success:
                        st.session_state.is_authenticated = True
                        st.session_state.user_data = user_data
                        st.session_state.auth_page = None
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(message)
        
        st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
        
        # Google Sign-In
        if st.button("🔐 Continue with Google", key="login_google", use_container_width=True):
            st.info("Google Sign-In requires OAuth configuration. Coming soon...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_back, col_signup = st.columns(2)
        
        with col_back:
            if st.button("← Back", key="login_back", use_container_width=True):
                st.session_state.auth_page = "menu"
                st.rerun()
        
        with col_signup:
            if st.button("Sign Up →", key="login_to_signup", use_container_width=True):
                st.session_state.auth_page = "signup"
                st.rerun()


def show_signup_page():
    """Display modern signup page."""
    inject_auth_styles()
    
    st.markdown("""
        <div class="auth-card">
            <div class="auth-logo">
                <span>Vitamin</span><span class="auth-logo-accent">AI</span>
            </div>
            <div class="auth-title">Create Account</div>
            <div class="auth-subtitle">Start your health journey today</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Signup Form
        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            key="signup_name"
        )
        
        email = st.text_input(
            "Email",
            placeholder="Enter your email",
            key="signup_email"
        )
        
        username = st.text_input(
            "Username",
            placeholder="Choose a username",
            key="signup_username",
            help="3-20 characters, letters, numbers, - or _"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password",
            key="signup_password",
            help="8+ characters, 1 uppercase, 1 number"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password",
            key="signup_confirm"
        )
        
        if st.button("Create Account", key="do_signup", use_container_width=True, type="primary"):
            if not all([full_name, email, username, password, confirm_password]):
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                # Validate inputs
                if not is_valid_email(email):
                    st.error("Invalid email format.")
                    st.stop()
                
                valid_pwd, pwd_msg = is_valid_password(password)
                if not valid_pwd:
                    st.error(pwd_msg)
                    st.stop()
                
                valid_user, user_msg = is_valid_username(username)
                if not valid_user:
                    st.error(user_msg)
                    st.stop()
                
                with st.spinner("Creating your account..."):
                    success, message = signup_user(email, password, full_name, username)
                    
                    if success:
                        st.success("Account created successfully! Please sign in.")
                        st.balloons()
                        # Redirect to login
                        st.session_state.auth_page = "login"
                        st.rerun()
                    else:
                        st.error(message)
        
        st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
        
        # Google Sign-In
        if st.button("🔐 Continue with Google", key="signup_google", use_container_width=True):
            st.info("Google Sign-In requires OAuth configuration. Coming soon...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_back, col_login = st.columns(2)
        
        with col_back:
            if st.button("← Back", key="signup_back", use_container_width=True):
                st.session_state.auth_page = "menu"
                st.rerun()
        
        with col_login:
            if st.button("Sign In →", key="signup_to_login", use_container_width=True):
                st.session_state.auth_page = "login"
                st.rerun()


def show_authentication_gateway():
    """Main authentication router."""
    # Initialize auth page state
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = "menu"
    
    # Route to appropriate page
    if st.session_state.auth_page == "login":
        show_login_page()
    elif st.session_state.auth_page == "signup":
        show_signup_page()
    else:
        show_auth_menu()
