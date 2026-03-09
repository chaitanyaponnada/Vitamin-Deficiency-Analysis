"""Modern authentication UI and Firebase Google sign-in integration."""

import json
import uuid

import streamlit as st
import streamlit.components.v1 as components

from firebase_auth import (
    get_firebase_config,
    is_valid_email,
    is_valid_password,
    is_valid_username,
    login_user,
    login_with_google,
    signup_user,
)
from ui_components import show_error_modal, show_info_modal


def inject_auth_styles():
    """Inject black-theme auth styles."""
    st.markdown(
        """
        <style>
            .auth-wrap {
                max-width: 520px;
                margin: 30px auto;
                padding: 22px;
                background: #121218;
                border: 1px solid #242430;
                border-radius: 18px;
            }

            .auth-logo {
                text-align: center;
                color: #ffffff;
                font-size: 3rem;
                font-weight: 700;
                letter-spacing: -0.02em;
                margin-bottom: 10px;
            }

            .auth-logo-accent {
                color: #4F46E5;
            }

            .auth-title {
                text-align: center;
                color: #ffffff;
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 6px;
            }

            .auth-subtitle {
                text-align: center;
                color: #9CA3AF;
                margin-bottom: 18px;
            }

            .auth-divider {
                text-align: center;
                color: #9CA3AF;
                margin: 12px 0;
            }

            .auth-footer-note {
                text-align: center;
                color: #9CA3AF;
                font-size: 0.88rem;
                margin-top: 14px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _consume_google_token_if_present():
    """Consume Google token from query params and finalize login."""
    token = st.query_params.get("google_id_token")
    if not token:
        return

    success, message, user_data = login_with_google(token)

    # Always clear params after consuming token to avoid repeat login attempts.
    st.query_params.clear()

    if success:
        st.session_state.is_authenticated = True
        st.session_state.user_data = user_data
        st.session_state.auth_page = None
        st.rerun()
    else:
        show_error_modal("Google Sign-In Failed", message, key_prefix="google_fail")


def _render_google_signin_button(component_key: str):
    """Render Firebase popup Google sign-in button and pass ID token to query params."""
    config = get_firebase_config()
    required = [
        config.get("api_key", ""),
        config.get("auth_domain", ""),
        config.get("project_id", ""),
        config.get("app_id", ""),
    ]
    if not all(required):
        show_info_modal(
            "Google Sign-In Setup",
            "Firebase Google provider is not fully configured. Add API key, auth domain, project ID, and app ID.",
            key_prefix="google_setup",
        )
        return

    firebase_cfg = {
        "apiKey": config.get("api_key", ""),
        "authDomain": config.get("auth_domain", ""),
        "projectId": config.get("project_id", ""),
        "storageBucket": config.get("storage_bucket", ""),
        "messagingSenderId": config.get("messaging_sender_id", ""),
        "appId": config.get("app_id", ""),
    }
    dom_id = f"google_btn_{component_key}_{uuid.uuid4().hex[:8]}"
    cfg_json = json.dumps(firebase_cfg)

    components.html(
        f"""
        <div style="display:flex;justify-content:center;">
            <button id="{dom_id}" style="
                width:100%;
                border-radius:10px;
                border:1px solid #242430;
                background:#18181F;
                color:#FFFFFF;
                font-weight:600;
                padding:10px 14px;
                cursor:pointer;
            ">Continue with Google</button>
        </div>
        <script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js"></script>
        <script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-auth-compat.js"></script>
        <script>
            const cfg = {cfg_json};
            const btn = document.getElementById("{dom_id}");
            if (!window.__vitaminFirebaseApp) {{
                window.__vitaminFirebaseApp = firebase.initializeApp(cfg, "vitaminAuthApp");
            }}
            const auth = firebase.auth(window.__vitaminFirebaseApp);

            btn.addEventListener('click', async () => {{
                try {{
                    const provider = new firebase.auth.GoogleAuthProvider();
                    provider.setCustomParameters({{prompt: 'select_account'}});
                    const result = await auth.signInWithPopup(provider);
                    const idToken = await result.user.getIdToken();
                    const target = new URL(window.parent.location.href);
                    target.searchParams.set('google_id_token', idToken);
                    target.searchParams.set('google_nonce', String(Date.now()));
                    window.parent.location.href = target.toString();
                }} catch (e) {{
                    const target = new URL(window.parent.location.href);
                    target.searchParams.set('google_error', encodeURIComponent((e && e.message) ? e.message : 'OAuth popup failed'));
                    target.searchParams.set('google_nonce', String(Date.now()));
                    window.parent.location.href = target.toString();
                }}
            }});
        </script>
        """,
        height=56,
    )


def _consume_google_error_if_present():
    error = st.query_params.get("google_error")
    if error:
        st.query_params.clear()
        show_error_modal("Google Sign-In Failed", error, key_prefix="google_popup_err")


def show_auth_menu():
    """Display authentication entry page."""
    inject_auth_styles()
    _consume_google_error_if_present()
    _consume_google_token_if_present()

    st.markdown(
        """
        <div class="auth-wrap">
            <div class="auth-logo">Vitamin<span class="auth-logo-accent">AI</span></div>
            <div class="auth-title">Welcome</div>
            <div class="auth-subtitle">Sign in to continue to your dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        if st.button("Sign In", key="auth_signin", use_container_width=True, type="primary"):
            st.session_state.auth_page = "login"
            st.rerun()
        if st.button("Create Account", key="auth_signup", use_container_width=True):
            st.session_state.auth_page = "signup"
            st.rerun()
        st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
        _render_google_signin_button("menu")


def show_login_page():
    """Display login form."""
    inject_auth_styles()
    _consume_google_error_if_present()
    _consume_google_token_if_present()

    st.markdown(
        """
        <div class="auth-wrap">
            <div class="auth-logo">Vitamin<span class="auth-logo-accent">AI</span></div>
            <div class="auth-title">Sign In</div>
            <div class="auth-subtitle">Use email/username and password</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        email_or_username = st.text_input("Email or Username", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Sign In", key="do_login", use_container_width=True, type="primary"):
            if not email_or_username or not password:
                show_error_modal("Authentication Error", "Please fill in all fields.", key_prefix="login_missing")
            else:
                success, message, user_data = login_user(email_or_username, password)
                if success:
                    st.session_state.is_authenticated = True
                    st.session_state.user_data = user_data
                    st.session_state.auth_page = None
                    st.rerun()
                else:
                    show_error_modal("Authentication Error", message, key_prefix="login_fail")

        st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
        _render_google_signin_button("login")

        a, b = st.columns(2)
        with a:
            if st.button("Back", key="login_back", use_container_width=True):
                st.session_state.auth_page = "menu"
                st.rerun()
        with b:
            if st.button("Create Account", key="to_signup", use_container_width=True):
                st.session_state.auth_page = "signup"
                st.rerun()


def show_signup_page():
    """Display sign-up form."""
    inject_auth_styles()
    _consume_google_error_if_present()
    _consume_google_token_if_present()

    st.markdown(
        """
        <div class="auth-wrap">
            <div class="auth-logo">Vitamin<span class="auth-logo-accent">AI</span></div>
            <div class="auth-title">Create Account</div>
            <div class="auth-subtitle">Set up your AI health workspace</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        full_name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Create Account", key="do_signup", use_container_width=True, type="primary"):
            if not all([full_name, email, username, password, confirm_password]):
                show_error_modal("Sign Up Error", "Please fill in all fields.", key_prefix="signup_missing")
            elif password != confirm_password:
                show_error_modal("Sign Up Error", "Passwords do not match.", key_prefix="signup_pwd_mismatch")
            elif not is_valid_email(email):
                show_error_modal("Sign Up Error", "Invalid email format.", key_prefix="signup_bad_email")
            else:
                valid_pwd, pwd_msg = is_valid_password(password)
                valid_user, user_msg = is_valid_username(username)
                if not valid_pwd:
                    show_error_modal("Sign Up Error", pwd_msg, key_prefix="signup_bad_pwd")
                elif not valid_user:
                    show_error_modal("Sign Up Error", user_msg, key_prefix="signup_bad_user")
                else:
                    success, message = signup_user(email, password, full_name, username)
                    if success:
                        show_info_modal("Account Created", "Your account is ready. Please sign in.", key_prefix="signup_ok")
                        st.session_state.auth_page = "login"
                        st.rerun()
                    else:
                        show_error_modal("Sign Up Error", message, key_prefix="signup_fail")

        st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
        _render_google_signin_button("signup")

        a, b = st.columns(2)
        with a:
            if st.button("Back", key="signup_back", use_container_width=True):
                st.session_state.auth_page = "menu"
                st.rerun()
        with b:
            if st.button("Sign In", key="to_login", use_container_width=True):
                st.session_state.auth_page = "login"
                st.rerun()


def show_authentication_gateway():
    """Main authentication router."""
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "menu"

    page = st.session_state.auth_page
    if page == "login":
        show_login_page()
    elif page == "signup":
        show_signup_page()
    else:
        show_auth_menu()
