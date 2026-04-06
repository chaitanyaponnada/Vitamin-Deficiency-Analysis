"""UI components and design system -- glassmorphism dark theme over video background."""

from datetime import datetime

import streamlit as st


def inject_global_styles():
    """Inject video background, glass-morphism CSS, and Streamlit overrides."""
    st.markdown(
        """
        <video autoplay loop muted playsinline id="bg-video">
            <source src="https://res.cloudinary.com/doiceztkc/video/upload/v1769665529/2_hff2at.mp4" type="video/mp4">
        </video>

        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

            :root {
                --bg-dark: transparent;
                --surface: rgba(20,20,26,0.55);
                --card: rgba(24,24,32,0.65);
                --border: rgba(255,255,255,0.08);
                --text: #F9FAFB;
                --text-muted: #9CA3AF;
                --accent: #4F46E5;
                --accent-hover: #4338CA;
                --accent-soft: rgba(79,70,229,0.15);
                --success: #10B981;
                --warning: #F59E0B;
                --error: #EF4444;
            }

            * {
                font-family: 'Space Grotesk', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            }

            /* --- Video Background --- */
            #bg-video {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                z-index: -2;
            }

            /* --- Hide Streamlit Chrome --- */
            #MainMenu, footer, header {
                visibility: hidden;
                height: 0 !important;
                min-height: 0 !important;
                padding: 0 !important;
                margin: 0 !important;
            }

            /* --- Transparent Containers --- */
            html, body, .stApp, [data-testid="stAppViewContainer"] {
                background: transparent !important;
                color: var(--text) !important;
            }

            [data-testid="stHeader"],
            [data-testid="stToolbar"],
            [data-testid="stSidebar"] {
                background: transparent !important;
            }

            [data-testid="stHeader"] {
                height: 0 !important;
                min-height: 0 !important;
                max-height: 0 !important;
                padding: 0 !important;
                margin: 0 !important;
                overflow: hidden !important;
            }

            .main .block-container {
                max-width: 1200px !important;
                margin: 0 auto !important;
                padding: 0 24px 24px 24px !important;
            }

            /* --- Glass Card --- */
            .glass-card {
                backdrop-filter: blur(18px);
                -webkit-backdrop-filter: blur(18px);
                background: rgba(18,18,26,0.75);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 20px;
                box-shadow: 0 10px 35px rgba(0,0,0,0.45);
            }

            /* --- Header --- */
            .app-header {
                backdrop-filter: blur(18px);
                -webkit-backdrop-filter: blur(18px);
                background: rgba(18,18,26,0.75);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 18px;
                margin-bottom: 20px;
                box-shadow: 0 10px 35px rgba(0,0,0,0.45);
            }

            .app-logo {
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 0.5px;
                line-height: 1;
                background: linear-gradient(135deg, #6366F1, #8B5CF6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .app-logo-accent {
                background: linear-gradient(135deg, #6366F1, #8B5CF6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            /* --- Avatar Button --- */
            .profile-avatar-btn button {
                width: 40px !important;
                min-width: 40px !important;
                height: 40px !important;
                border-radius: 10px !important;
                border: 1px solid rgba(0,0,0,0.12) !important;
                background: rgba(55,65,81,0.25) !important;
                color: #374151 !important;
                padding: 0 !important;
                font-weight: 600 !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
                transition: all 0.2s ease !important;
            }

            .profile-avatar-btn button:hover {
                border-color: var(--accent) !important;
                background: rgba(99,102,241,0.15) !important;
                color: #4F46E5 !important;
                box-shadow: 0 0 0 3px rgba(79,70,229,0.12);
                transform: translateY(-1px);
            }

            /* --- Navigation Links --- */
            div[role="radiogroup"] {
                display: flex;
                justify-content: center;
                gap: 28px;
                flex-wrap: wrap;
                padding: 10px 0;
                background: transparent;
                border: none;
                border-radius: 0;
                border-bottom: 1px solid var(--border);
                margin-bottom: 16px;
            }

            div[role="radiogroup"] > label {
                background: transparent !important;
                border: none;
                border-radius: 0;
                color: #6B7280 !important;
                padding: 8px 4px;
                font-size: 15px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                border-bottom: 2px solid transparent;
            }

            div[role="radiogroup"] > label > div:first-child {
                display: none !important;
            }

            div[role="radiogroup"] > label:hover {
                color: #374151 !important;
                background: transparent !important;
                border-bottom-color: rgba(99,102,241,0.4);
            }

            div[role="radiogroup"] > label:has(input:checked) {
                color: #374151 !important;
                background: transparent !important;
                border-bottom: 2px solid #6366F1;
            }

            /* --- Page Headings --- */
            .page-title {
                font-size: 2.2rem;
                font-weight: 700;
                margin-bottom: 4px;
                color: #9CA3AF;
                letter-spacing: -0.02em;
            }

            .page-subtitle {
                font-size: 1rem;
                color: var(--text-muted);
                margin-bottom: 1.3rem;
            }

            /* --- Stat Cards --- */
            .stat-card {
                text-align: center;
                backdrop-filter: blur(18px);
                -webkit-backdrop-filter: blur(18px);
                background: rgba(18,18,26,0.75);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 1.4rem 1rem;
                transition: transform 0.2s ease, border-color 0.2s ease;
                min-height: 150px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                box-shadow: 0 10px 35px rgba(0,0,0,0.45);
            }

            .stat-card:hover {
                border-color: rgba(255,255,255,0.14);
                transform: translateY(-3px);
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

            /* --- Center Loader Overlay --- */
            .center-loader-wrap {
                position: fixed;
                inset: 0;
                z-index: 9999;
                display: flex;
                justify-content: center;
                align-items: center;
                background: rgba(0,0,0,0.72);
                backdrop-filter: blur(4px);
                -webkit-backdrop-filter: blur(4px);
            }

            .center-loader-card {
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 1.4rem 1.8rem;
                box-shadow: 0 20px 40px rgba(0,0,0,0.45);
                text-align: center;
            }

            .center-loader {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                border: 3px solid rgba(255,255,255,0.2);
                border-top: 3px solid var(--accent);
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }

            .center-loader-text {
                color: var(--text);
                margin-top: 10px;
                font-weight: 500;
            }

            /* --- Buttons --- */
            .stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #4F46E5, #6366F1) !important;
                border: none !important;
                border-radius: 10px !important;
                color: var(--text) !important;
                font-weight: 500 !important;
                padding: 10px 18px !important;
                transition: all 0.2s ease !important;
            }

            .stButton > button[kind="primary"]:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 18px rgba(79,70,229,0.35);
            }

            .stButton > button:not([kind="primary"]),
            .stDownloadButton > button {
                border-radius: 10px !important;
                border: 1px solid var(--border) !important;
                background: var(--card) !important;
                color: var(--text) !important;
                font-weight: 500 !important;
                padding: 10px 18px !important;
                transition: all 0.2s ease !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
            }

            .stButton > button:not([kind="primary"]):hover,
            .stDownloadButton > button:hover {
                border-color: rgba(255,255,255,0.14) !important;
                transform: translateY(-1px);
            }

            /* --- Form Inputs --- */
            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox [data-baseweb="select"] > div,
            .stFileUploader {
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
                background: var(--card) !important;
                color: var(--text) !important;
                border-color: var(--border) !important;
                border-radius: 10px !important;
            }

            /* --- Text --- */
            .stMarkdown, .stCaption {
                color: var(--text) !important;
            }

            p, label {
                color: var(--text-muted) !important;
            }

            div[role="radiogroup"] > label {
                color: #6B7280 !important;
            }

            div[role="radiogroup"] > label:hover {
                color: #374151 !important;
            }

            div[role="radiogroup"] > label:has(input:checked) {
                color: #374151 !important;
            }

            /* --- Metrics --- */
            .stMetric {
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 10px;
            }

            /* --- Expanders --- */
            div[data-testid="stExpander"] {
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
            }

            /* --- Modal --- */
            .modal-content {
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                background: rgba(20,20,26,0.85);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 24px;
                box-shadow: 0 20px 45px rgba(0,0,0,0.45);
                color: #FFFFFF;
            }

            /* --- Profile Dropdown --- */
            .profile-dropdown-card {
                position: relative;
                width: 220px;
                float: right;
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 8px 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.4);
                animation: dropdownFade 0.18s ease-out;
                margin-bottom: 8px;
            }

            .profile-dropdown-card .dropdown-item button {
                width: 100% !important;
                text-align: left !important;
                background: transparent !important;
                border: none !important;
                border-radius: 0 !important;
                color: var(--text-muted) !important;
                font-weight: 500 !important;
                padding: 10px 18px !important;
                transition: all 0.15s ease !important;
            }

            .profile-dropdown-card .dropdown-item button:hover {
                background: var(--accent-soft) !important;
                color: var(--text) !important;
            }

            @keyframes dropdownFade {
                from { opacity: 0; transform: translateY(-6px); }
                to   { opacity: 1; transform: translateY(0); }
            }

            /* --- Spinner Animation --- */
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            /* --- Section Card --- */
            .section-card {
                backdrop-filter: blur(18px);
                -webkit-backdrop-filter: blur(18px);
                background: rgba(18,18,26,0.75);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 24px;
                margin-top: 24px;
                box-shadow: 0 10px 35px rgba(0,0,0,0.45);
            }

            .section-card-title {
                font-size: 1.15rem;
                font-weight: 600;
                color: var(--text);
                margin-bottom: 12px;
            }

            /* --- Upload Dropzone --- */
            .upload-dropzone {
                backdrop-filter: blur(18px);
                -webkit-backdrop-filter: blur(18px);
                background: rgba(18,18,26,0.75);
                border: 2px dashed rgba(255,255,255,0.12);
                border-radius: 14px;
                padding: 48px 24px;
                text-align: center;
                transition: border-color 0.2s ease;
                margin: 16px 0;
                box-shadow: 0 10px 35px rgba(0,0,0,0.45);
            }

            .upload-dropzone:hover {
                border-color: var(--accent);
            }

            .upload-dropzone-title {
                font-size: 1.2rem;
                font-weight: 600;
                color: var(--text);
                margin-bottom: 4px;
            }

            .upload-dropzone-sub {
                font-size: 0.9rem;
                color: var(--text-muted);
            }

            /* --- Glass Divider --- */
            .glass-divider {
                border: none;
                border-top: 1px solid var(--border);
                margin: 20px 0;
            }

            /* --- Result Card --- */
            .result-card {
                backdrop-filter: blur(18px);
                -webkit-backdrop-filter: blur(18px);
                background: rgba(18,18,26,0.75);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 20px;
                box-shadow: 0 10px 35px rgba(0,0,0,0.45);
            }

            /* --- About Section --- */
            .about-section {
                backdrop-filter: blur(18px);
                -webkit-backdrop-filter: blur(18px);
                background: rgba(18,18,26,0.75);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 24px;
                margin-bottom: 20px;
                box-shadow: 0 10px 35px rgba(0,0,0,0.45);
            }

            .about-section-title {
                font-size: 1.15rem;
                font-weight: 600;
                color: var(--text);
                margin-bottom: 10px;
            }

            .about-section p, .about-section li {
                color: var(--text-muted) !important;
                line-height: 1.7;
            }

            /* --- Mobile Responsive --- */
            @media (max-width: 900px) {
                .main .block-container {
                    padding: 12px !important;
                }
                .app-header {
                    padding: 12px;
                    margin-bottom: 14px;
                }
                .app-logo {
                    font-size: 1.5rem;
                }
                .page-title {
                    font-size: 1.6rem;
                }
                .page-subtitle {
                    font-size: 0.88rem;
                }
                .stat-card {
                    min-height: 100px;
                    padding: 0.8rem 0.6rem;
                }
                .stat-value {
                    font-size: 1.8rem;
                }
                .stat-label {
                    font-size: 0.78rem;
                }
                .section-card {
                    padding: 14px;
                    margin-top: 14px;
                }
                .upload-dropzone {
                    padding: 28px 14px;
                }
                .result-card {
                    padding: 14px;
                }
                .about-section {
                    padding: 16px;
                    margin-bottom: 14px;
                }
                div[role="radiogroup"] {
                    gap: 16px;
                    padding: 8px 0;
                }
                div[role="radiogroup"] > label {
                    padding: 6px 2px;
                    font-size: 0.8rem;
                }
                .center-loader-card {
                    padding: 1rem 1.2rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(user_data=None):
    """Render glass header with logo and avatar button."""
    user_data = user_data or {}
    full_name = user_data.get("full_name", "User")
    initial = (full_name[0].upper() if full_name else "U")

    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    logo_col, avatar_col = st.columns([10, 1])
    with logo_col:
        st.markdown(
            '<div class="app-logo">Vitamin<span class="app-logo-accent">AI</span></div>',
            unsafe_allow_html=True,
        )
    with avatar_col:
        st.markdown('<div class="profile-avatar-btn">', unsafe_allow_html=True)
        if st.button(initial, key="profile_avatar_btn", help="Profile"):
            st.session_state.show_profile_menu = not st.session_state.get("show_profile_menu", False)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_profile_dropdown(user_data):
    """Render glass dropdown with Profile, History, and Logout."""
    if not st.session_state.get("show_profile_menu", False):
        return

    spacer, dropdown_col = st.columns([9, 3])
    with dropdown_col:
        st.markdown('<div class="profile-dropdown-card">', unsafe_allow_html=True)

        st.markdown('<div class="dropdown-item">', unsafe_allow_html=True)
        if st.button("Profile", key="dd_profile"):
            st.session_state.show_profile_menu = False
            st.session_state.switch_to_profile = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="dropdown-item">', unsafe_allow_html=True)
        if st.button("History", key="dd_history"):
            st.session_state.show_profile_menu = False
            st.session_state.switch_to_profile = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="dropdown-item">', unsafe_allow_html=True)
        if st.button("Logout", key="do_logout"):
            st.session_state.clear()
            st.session_state._needs_cookie_delete = True
            st.session_state._cookie_checked = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


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
            f'<div class="modal-content">{message}</div>',
            unsafe_allow_html=True,
        )
        st.button("Close", key=f"{key_prefix}_close")

    _modal()


def show_error_modal(title, message, key_prefix="modal_err"):
    show_modal(title, message, level="error", key_prefix=key_prefix)


def show_info_modal(title, message, key_prefix="modal_info"):
    show_modal(title, message, level="info", key_prefix=key_prefix)
