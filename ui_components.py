"""UI components and design system for a premium black aesthetic Streamlit app."""

from datetime import datetime

import streamlit as st


def inject_global_styles():
    """Inject app-wide black theme styles and stable layout rules."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

            :root {
                --bg: #0B0B0F;
                --surface: #121218;
                --card: #18181F;
                --text: #FFFFFF;
                --text-muted: #9CA3AF;
                --accent: #4F46E5;
                --border: #242430;
            }

            * {
                font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }

            #MainMenu, footer, header {
                visibility: hidden;
            }

            html, body, .stApp, [data-testid="stAppViewContainer"] {
                background: var(--bg) !important;
                color: var(--text) !important;
            }

            [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {
                background: transparent !important;
            }

            .main .block-container {
                max-width: 1200px !important;
                margin: 0 auto !important;
                padding: 24px !important;
            }

            .app-shell {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 16px 20px;
                margin-bottom: 18px;
            }

            .app-header {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 14px 16px;
                margin-bottom: 14px;
            }

            .app-logo {
                font-size: 2rem;
                font-weight: 700;
                color: var(--text);
                letter-spacing: -0.02em;
                line-height: 1;
            }

            .app-logo-accent {
                color: var(--accent);
            }

            .profile-avatar-btn button {
                width: 40px !important;
                min-width: 40px !important;
                height: 40px !important;
                border-radius: 999px !important;
                border: 1px solid var(--border) !important;
                background: var(--card) !important;
                color: var(--text) !important;
                padding: 0 !important;
                font-weight: 700 !important;
            }

            .profile-avatar-btn button:hover {
                border-color: var(--accent) !important;
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.18);
            }

            .profile-dropdown {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.4);
                margin-top: 8px;
            }

            .profile-name {
                font-size: 0.98rem;
                font-weight: 600;
                color: var(--text);
                margin-bottom: 2px;
            }

            .profile-email {
                font-size: 0.85rem;
                color: var(--text-muted);
                margin-bottom: 12px;
            }

            .profile-divider {
                border-top: 1px solid var(--border);
                margin: 10px 0 12px 0;
            }

            .nav-wrap {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 8px 12px;
                margin-bottom: 16px;
            }

            div[role="radiogroup"] {
                justify-content: center;
                gap: 8px;
                flex-wrap: wrap;
            }

            div[role="radiogroup"] > label {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 10px;
                color: var(--text-muted);
                padding: 8px 14px;
                transition: all 0.18s ease;
            }

            div[role="radiogroup"] > label:hover {
                color: var(--text);
                background: #161622;
                border-color: var(--border);
            }

            div[role="radiogroup"] > label:has(input:checked) {
                color: var(--text);
                border-color: var(--accent);
                box-shadow: inset 0 -2px 0 0 var(--accent);
                background: #161622;
            }

            .page-title {
                font-size: 2.2rem;
                font-weight: 700;
                margin-bottom: 4px;
                color: var(--text);
                letter-spacing: -0.02em;
            }

            .page-subtitle {
                font-size: 1rem;
                color: var(--text-muted);
                margin-bottom: 1.3rem;
            }

            .stat-card {
                text-align: center;
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 1.4rem 1rem;
                transition: border-color 0.2s ease, transform 0.2s ease;
                min-height: 150px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            .stat-card:hover {
                border-color: #2f2f3f;
                transform: translateY(-1px);
            }

            .stat-value {
                font-size: 2.4rem;
                font-weight: 700;
                color: var(--text);
                margin-bottom: 6px;
                word-break: break-word;
            }

            .stat-label {
                font-size: 0.86rem;
                color: var(--text-muted);
                font-weight: 600;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .loading-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 2.2rem;
                margin: 1rem 0;
            }

            .loading-spinner {
                width: 48px;
                height: 48px;
                border-radius: 999px;
                border: 3px solid #2b2b38;
                border-top-color: var(--accent);
                animation: ui-spin 1s linear infinite;
            }

            .loading-text {
                margin-top: 12px;
                color: var(--text);
                font-weight: 600;
            }

            .loading-subtext {
                color: var(--text-muted);
                font-size: 0.9rem;
                margin-top: 4px;
            }

            .center-loader-wrap {
                position: fixed;
                inset: 0;
                z-index: 9999;
                display: flex;
                justify-content: center;
                align-items: center;
                background: rgba(11, 11, 15, 0.72);
            }

            .center-loader-card {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 1.2rem 1.6rem;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45);
            }

            .center-loader {
                width: 34px;
                height: 34px;
                border-radius: 999px;
                border: 3px solid #2b2b38;
                border-top-color: var(--accent);
                animation: ui-spin 1s linear infinite;
                margin: 0 auto;
            }

            .center-loader-text {
                color: var(--text);
                margin-top: 10px;
                font-weight: 500;
            }

            .stButton > button,
            .stDownloadButton > button {
                border-radius: 10px !important;
                border: 1px solid var(--border) !important;
                background: var(--card) !important;
                color: var(--text) !important;
                font-weight: 600 !important;
            }

            .stButton > button[kind="primary"] {
                background: var(--accent) !important;
                border-color: var(--accent) !important;
                color: var(--text) !important;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover {
                border-color: #343449 !important;
            }

            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox [data-baseweb="select"] > div,
            .stFileUploader {
                background: var(--card) !important;
                color: var(--text) !important;
                border-color: var(--border) !important;
            }

            .stMarkdown, .stCaption, p, label {
                color: var(--text) !important;
            }

            .stMetric {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 10px;
            }

            div[data-testid="stExpander"] {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
            }

            @keyframes ui-spin {
                to {
                    transform: rotate(360deg);
                }
            }

            @media (max-width: 900px) {
                .main .block-container {
                    padding: 14px !important;
                }

                .app-logo {
                    font-size: 1.7rem;
                }

                .page-title {
                    font-size: 1.8rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(user_data=None):
    """Render structured header with left logo and top-right avatar button."""
    user_data = user_data or {}
    full_name = user_data.get("full_name", "User")
    initial = (full_name[0].upper() if full_name else "U")

    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    logo_col, avatar_col = st.columns([12, 1])
    with logo_col:
        st.markdown(
            '<div class="app-logo">Vitamin<span class="app-logo-accent">AI</span></div>',
            unsafe_allow_html=True,
        )
    with avatar_col:
        st.markdown('<div class="profile-avatar-btn">', unsafe_allow_html=True)
        if st.button(initial, key="profile_avatar_btn", help="Account"):
            st.session_state.show_profile_menu = not st.session_state.get("show_profile_menu", False)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_profile_dropdown(user_data):
    """Render profile dropdown card below the avatar in a stable right column."""
    if not st.session_state.get("show_profile_menu", False):
        return

    full_name = user_data.get("full_name", "User")
    email = user_data.get("email", "")

    left, right = st.columns([9, 3])
    with right:
        st.markdown(
            f"""
            <div class="profile-dropdown">
                <div class="profile-name">{full_name}</div>
                <div class="profile-email">{email}</div>
                <div class="profile-divider"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Profile", key="goto_profile", use_container_width=True):
            st.session_state.show_profile_menu = False
            st.session_state.active_tab = "profile"
            st.rerun()
        if st.button("History", key="goto_history", use_container_width=True):
            st.session_state.show_profile_menu = False
            st.session_state.active_nav = "History"
            st.rerun()
        if st.button("Logout", key="do_logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()


def render_loading_animation(message="Loading", submessage="Please wait..."):
    """Render centered loading card."""
    st.markdown(
        f"""
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">{message}</div>
            <div class="loading-subtext">{submessage}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title, subtitle=""):
    """Render consistent page heading."""
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_stat_card(value, label):
    """Render stat card HTML."""
    return (
        "<div class=\"stat-card\">"
        f"<span class=\"stat-value\">{value}</span>"
        f"<span class=\"stat-label\">{label}</span>"
        "</div>"
    )


def get_current_date_display():
    """Return formatted current date and weekday."""
    now = datetime.now()
    return now.strftime("%B %d, %Y"), now.strftime("%A")


def _show_modal_fallback(title, message, level="error"):
    """Fallback for Streamlit versions without st.dialog."""
    if level == "error":
        st.error(f"{title}: {message}")
    elif level == "warning":
        st.warning(f"{title}: {message}")
    else:
        st.info(f"{title}: {message}")


def show_modal(title, message, level="error", key_prefix="modal"):
    """Show centered dialog-based modal when supported."""
    if not hasattr(st, "dialog"):
        _show_modal_fallback(title, message, level=level)
        return

    @st.dialog(title)
    def _modal():
        st.markdown(
            f"""
            <div style="
                background:#18181F;
                border:1px solid #242430;
                border-radius:14px;
                padding:24px;
                box-shadow:0 20px 45px rgba(0,0,0,0.45);
                color:#FFFFFF;
            ">
                {message}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Close", key=f"{key_prefix}_close")

    _modal()


def show_error_modal(title, message, key_prefix="modal_err"):
    show_modal(title, message, level="error", key_prefix=key_prefix)


def show_info_modal(title, message, key_prefix="modal_info"):
    show_modal(title, message, level="info", key_prefix=key_prefix)
