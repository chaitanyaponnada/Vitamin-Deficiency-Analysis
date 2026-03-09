"""
Modern UI Components for Production SaaS Application.
Minimal, clean, professional design with no emojis.
"""

import streamlit as st
from datetime import datetime


# ==================== STYLING ====================

def inject_global_styles():
    """Inject modern, minimal SaaS-style CSS."""
    st.markdown("""
        <style>
            /* Modern SaaS Reset */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            
            /* Hide Streamlit branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Main container */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 4rem;
                max-width: 1400px;
            }
            
            /* Modern Header */
            .app-header {
                position: sticky;
                top: 0;
                z-index: 999;
                background: rgba(255, 255, 255, 0.85);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(0, 0, 0, 0.06);
                padding: 1rem 2rem;
                margin: -2rem -2rem 2rem -2rem;
            }
            
            .app-header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .app-logo {
                font-size: 1.5rem;
                font-weight: 700;
                color: #0f172a;
                letter-spacing: -0.02em;
            }
            
            .app-logo-accent {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            /* Profile Avatar */
            .profile-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 0.9rem;
                cursor: pointer;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            
            .profile-avatar:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }
            
            /* Dropdown Menu */
            .dropdown-menu {
                position: absolute;
                right: 2rem;
                top: 4.5rem;
                min-width: 280px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
                border: 1px solid rgba(0, 0, 0, 0.06);
                padding: 0.5rem;
                animation: dropdown-appear 0.2s ease;
            }
            
            @keyframes dropdown-appear {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .dropdown-header {
                padding: 1rem;
                border-bottom: 1px solid rgba(0, 0, 0, 0.06);
            }
            
            .dropdown-user-name {
                font-weight: 600;
                color: #0f172a;
                font-size: 1.05rem;
                margin-bottom: 0.25rem;
            }
            
            .dropdown-user-email {
                color: #64748b;
                font-size: 0.85rem;
            }
            
            .dropdown-item {
                display: flex;
                align-items: center;
                padding: 0.75rem 1rem;
                color: #334155;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.15s ease;
                margin: 0.25rem 0;
            }
            
            .dropdown-item:hover {
                background: #f8fafc;
                color: #667eea;
            }
            
            .dropdown-item-icon {
                margin-right: 0.75rem;
                opacity: 0.7;
            }
            
            .dropdown-divider {
                height: 1px;
                background: rgba(0, 0, 0, 0.06);
                margin: 0.5rem 0;
            }
            
            /* Modern Tab Navigation */
            .stTabs {
                background: transparent;
            }
            
            .stTabs [data-baseweb="tab-list"] {
                gap: 0;
                background: rgba(0, 0, 0, 0.02);
                border-radius: 12px;
                padding: 0.25rem;
                justify-content: center;
                border: none;
            }
            
            .stTabs [data-baseweb="tab"] {
                background: transparent;
                border: none;
                color: #64748b;
                font-weight: 500;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                transition: all 0.2s ease;
            }
            
            .stTabs [data-baseweb="tab"]:hover {
                color: #334155;
                background: rgba(0, 0, 0, 0.04);
            }
            
            .stTabs [aria-selected="true"] {
                background: white !important;
                color: #667eea !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }
            
            /* Page Title */
            .page-title {
                font-size: 2.5rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 0.5rem;
                letter-spacing: -0.03em;
            }
            
            .page-subtitle {
                font-size: 1.1rem;
                color: #64748b;
                margin-bottom: 2rem;
                font-weight: 400;
            }
            
            /* Cards */
            .modern-card {
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
                border: 1px solid rgba(0, 0, 0, 0.06);
                transition: all 0.3s ease;
            }
            
            .modern-card:hover {
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
                transform: translateY(-2px);
            }
            
            .stat-card {
                text-align: center;
                background: white;
                padding: 2rem 1.5rem;
                border-radius: 16px;
                border: 1px solid rgba(0, 0, 0, 0.06);
                transition: all 0.3s ease;
            }
            
            .stat-card:hover {
                border-color: rgba(102, 126, 234, 0.3);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
            }
            
            .stat-value {
                font-size: 2.5rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 0.5rem;
                display: block;
            }
            
            .stat-label {
                font-size: 0.9rem;
                color: #64748b;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            /* Buttons */
            .stButton > button {
                border-radius: 10px;
                font-weight: 600;
                padding: 0.65rem 1.5rem;
                border: none;
                transition: all 0.2s ease;
            }
            
            .stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .stButton > button[kind="primary"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            
            .stButton > button[kind="secondary"] {
                background: white;
                color: #667eea;
                border: 1.5px solid #667eea;
            }
            
            .stButton > button[kind="secondary"]:hover {
                background: #f8fafc;
            }
            
            /* Loading Animation */
            .loading-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 4rem 2rem;
                text-align: center;
            }
            
            .loading-spinner {
                width: 60px;
                height: 60px;
                border: 4px solid rgba(102, 126, 234, 0.1);
                border-top-color: #667eea;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .loading-text {
                margin-top: 1.5rem;
                font-size: 1.1rem;
                color: #334155;
                font-weight: 500;
            }
            
            .loading-subtext {
                margin-top: 0.5rem;
                font-size: 0.9rem;
                color: #94a3b8;
            }
            
            /* Welcome Animation */
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .welcome-section {
                animation: fadeInUp 0.6s ease;
            }
            
            /* File Upload */
            .stFileUploader {
                border: 2px dashed rgba(102, 126, 234, 0.3);
                border-radius: 12px;
                padding: 2rem;
                background: rgba(102, 126, 234, 0.02);
                transition: all 0.3s ease;
            }
            
            .stFileUploader:hover {
                border-color: rgba(102, 126, 234, 0.5);
                background: rgba(102, 126, 234, 0.05);
            }
            
            /* Success/Error Messages */
            .stSuccess, .stError, .stWarning, .stInfo {
                border-radius: 12px;
                border: none;
                padding: 1rem 1.5rem;
            }
        </style>
    """, unsafe_allow_html=True)


# ==================== COMPONENTS ====================

def render_header(user_data=None):
    """Render modern application header with logo and profile."""
    st.markdown("""
        <div class="app-header">
            <div class="app-header-content">
                <div class="app-logo">
                    <span>Vitamin</span><span class="app-logo-accent">AI</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_profile_dropdown(user_data):
    """Render profile dropdown menu."""
    full_name = user_data.get('full_name', 'User')
    email = user_data.get('email', '')
    username = user_data.get('username', 'user')
    initial = full_name[0].upper() if full_name else 'U'
    
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col3:
        # Profile Avatar Button
        profile_clicked = st.button(
            initial,
            key="profile_button",
            help=f"@{username}",
            use_container_width=False
        )
        
        if profile_clicked:
            st.session_state.show_profile_menu = not st.session_state.get('show_profile_menu', False)
    
    # Dropdown Menu (rendered separately to avoid nesting issues)
    if st.session_state.get('show_profile_menu', False):
        dropdown_html = f"""
        <div class="dropdown-menu">
            <div class="dropdown-header">
                <div class="dropdown-user-name">{full_name}</div>
                <div class="dropdown-user-email">{email}</div>
            </div>
        </div>
        """
        st.markdown(dropdown_html, unsafe_allow_html=True)
        
        # Dropdown options
        col1, col2, col3 = st.columns([6, 1, 1])
        with col3:
            if st.button("Profile", key="goto_profile", use_container_width=True):
                st.session_state.show_profile_menu = False
                st.session_state.active_tab = "profile"
                st.rerun()
            
            if st.button("History", key="goto_history", use_container_width=True):
                st.session_state.show_profile_menu = False
                st.session_state.active_tab = "history"
                st.rerun()
            
            if st.button("Logout", key="do_logout", use_container_width=True):
                st.session_state.clear()
                st.rerun()


def render_loading_animation(message="Loading", submessage="Please wait..."):
    """Render modern loading animation."""
    st.markdown(f"""
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">{message}</div>
            <div class="loading-subtext">{submessage}</div>
        </div>
    """, unsafe_allow_html=True)


def render_page_header(title, subtitle=""):
    """Render page title and subtitle."""
    st.markdown(f'<h1 class="page-title">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="page-subtitle">{subtitle}</p>', unsafe_allow_html=True)


def render_stat_card(value, label):
    """Render a statistics card."""
    return f"""
    <div class="stat-card">
        <span class="stat-value">{value}</span>
        <span class="stat-label">{label}</span>
    </div>
    """


def get_current_date_display():
    """Get formatted current date and day."""
    now = datetime.now()
    return now.strftime("%B %d, %Y"), now.strftime("%A")
