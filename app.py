import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import ssl
import logging
from typing import Dict, List, Tuple

# ==============================================================================
# SYSTEM CONFIGURATION & LOGGING
# ==============================================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Bypass SSL Verification for specific network environments (macOS/Corporate Proxy)
ssl._create_default_https_context = ssl._create_unverified_context

# Constants
SHEET_EXPORT_URL = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/export?format=csv&gid=827445294"
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/edit"

STATION_COORDINATES: Dict[str, Tuple[float, float]] = {
    "CGK": (-6.1256, 106.6559), "KNO": (3.6422, 98.8853),
    "DPS": (-8.7481, 115.1674), "SUB": (-7.3798, 112.7873),
    "UPG": (-5.0616, 119.5523), "DJJ": (-2.5783, 140.5167),
    "BTH": (1.1211, 104.1182), "BPN": (-1.2683, 116.8944)
}

# ==============================================================================
# DATA MANAGEMENT LAYER (CACHED)
# ==============================================================================
@st.cache_data(ttl=300, show_spinner=False)  # Cache data for 5 minutes
def fetch_manpower_data() -> pd.DataFrame:
    """Fetches and caches live manpower data from Google Sheets."""
    try:
        df = pd.read_csv(SHEET_EXPORT_URL)
        logger.info(f"Successfully loaded {len(df)} records from database.")
        return df
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        st.toast("⚠️ Operating on local fallback data due to network error.", icon="📡")
        # Enterprise Fallback Data
        return pd.DataFrame([
            {"ID": 551001, "Nama": "System Admin", "Kualifikasi": "A330/B777 Expert", "Lokasi": "CGK", "Status": "Active"}
        ])

# ==============================================================================
# UI INJECTION (ENTERPRISE CSS)
# ==============================================================================
def inject_enterprise_css() -> None:
    """Injects refined, professional-grade CSS typography and structural styling."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
            
            /* Global Typography */
            html, body, [class*="css"], .stMarkdown, .stText {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
            }
            
            /* Deep Corporate Background */
            .stApp {
                background-color: #0B1120 !important;
                background-image: radial-gradient(circle at 50% 0%, #1E293B 0%, #0B1120 70%);
                color: #F8FAFC !important;
            }

            /* Professional Sidebar Refinement */
            section[data-testid="stSidebar"] {
                background-color: #0F172A !important;
                border-right: 1px solid #1E293B !important;
            }
            
            /* Enhanced Sidebar Text */
            div[data-testid="stSidebarUserContent"] p, div[data-testid="stSidebarUserContent"] h3 {
                color: #CBD5E1 !important;
                font-weight: 500;
            }
            
            /* Action Buttons (Standardized) */
            div.stButton > button {
                background-color: #2563EB !important;
                color: #FFFFFF !important;
                border: 1px solid #3B82F6 !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
                padding: 0.5rem 1rem !important;
                transition: all 0.2s ease-in-out;
            }
            div.stButton > button:hover {
                background-color: #1D4ED8 !important;
                border-color: #60A5FA !important;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
            }

            /* External Link Button */
            .action-link-btn {
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: #059669;
                color: white !important;
                padding: 0.6rem 1rem;
                border-radius: 6px;
                font-weight: 600;
                font-size: 0.875rem;
                text-decoration: none;
                transition: 0.2s ease;
                border: 1px solid #10B981;
                margin-bottom: 1rem;
            }
            .action-link-btn:hover {
                background-color: #047857;
                box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2);
            }

            /* Executive Banner */
            .exec-banner {
                background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
                border: 1px solid #334155;
                padding: 2rem;
                border-radius: 12px;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            }
            .exec-banner h1 {
                color: #F8FAFC !important;
                font-size: 2.2rem !important;
                font-weight: 800 !important;
                margin: 0;
            }
            .exec-banner p {
                color: #38BDF8 !important;
                font-size: 0.85rem !important;
                font-weight: 700;
                letter-spacing: 0.2em;
                margin-top: 0.5rem !important;
                text-transform: uppercase;
            }

            /* High-End KPI Cards */
            .metric-card {
                background-color: #1E293B;
                border: 1px solid #334155;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .metric-title {
                color: #94A3B8;
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.5rem;
            }
            .metric-value {
                font-size: 2rem;
                font-weight: 800;
                color: #F8FAFC;
                line-height: 1;
            }

            /* Structural Sections */
            .panel-container {
                background-color: #0F172A;
                border: 1px solid #1E293B;
                border-radius: 10px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            }
            .section-header {
                font-size: 1.1rem;
                font-weight: 700;
                color: #E2E8F0;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            /* Override Streamlit Inputs for Dark Theme */
            div[data-testid="stTextInput"] input {
                background-color: #1E293B !important;
                color: #F8FAFC !important;
                border: 1px solid #334155 !important;
                border-radius: 6px !important;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: #38BDF8 !important;
                box-shadow: 0 0 0 1px #38BDF8 !important;
            }
            
            /* Clean Popover Buttons */
            div[data-testid="stPopover"] > button {
                background-color: #1E293B !important;
                border: 1px solid #334155 !important;
                color: #E2E8F0 !important;
            }
            div[data-testid="stPopoverBody"] {
                background-color: #0F172A !important;
                border: 1px solid #334155 !important;
                border-radius: 12px !important;
            }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# AUTHENTICATION MODULE
# ==============================================================================
def render_authentication_gateway() -> None:
    """Renders the secure login interface."""
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="color: #F8FAFC; font-weight: 800; font-size: 1.8rem; margin:0;">SYSTEM GATEWAY</h2>
                <p style="color: #38BDF8; font-weight: 600; font-size: 0.75rem; letter-spacing: 0.2em; margin-top:0.2rem;">GMF TACTICAL COMMAND</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            username = st.text_input("Operator ID", key="auth_user")
            password = st.text_input("Access Credential", type="password", key="auth_pass")
            
            if st.button("INITIALIZE SESSION", use_container_width=True):
                # In production, use hashed passwords or SSO. Mocking logic here.
                if username == "admin" and password == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.username = username.upper()
                    st.session_state.role = "Command Level Administrator"
                    st.rerun()
                else:
                    st.error("Authentication Failed: Invalid credentials.")
    st.stop()

# ==============================================================================
# DASHBOARD RENDERING LOGIC
# ==============================================================================
def render_sidebar() -> None:
    """Renders the side navigation and control panel."""
    with st.sidebar:
        st.markdown("<h3 style='color:#F8FAFC; margin-bottom: 1.5rem;'>⚙️ Control Center</h3>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <a href="{SHEET_EDIT_URL}" target="_blank" class="action-link-btn">
                <span>📝 Edit Master Database</span>
            </a>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Force Data Sync", use_container_width=True):
            fetch_manpower_data.clear()
            st.toast("Cache cleared. Database synced.", icon="✅")
            st.rerun()
            
        st.divider()
        
        st.markdown("<div class='metric-title'>Current Session</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#38BDF8; font-weight:700; margin-bottom:1rem;'>👤 {st.session_state.username}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#94A3B8; font-size:0.85rem; margin-bottom:2rem;'>🛡️ {st.session_state.role}</div>", unsafe_allow_html=True)
        
        if st.button("Log Out Session", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()

def render_spatial_map(df: pd.DataFrame) -> None:
    """Generates the Folium interactive map with embedded analytical tooltips."""
    m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles="CartoDB dark_matter")
    
    for station, coords in STATION_COORDINATES.items():
        station_data = df[df['Lokasi'].str.strip() == station]
        if not station_data.empty:
            total_px = len(station_data)
            status_list = station_data['Status'].str.strip().tolist()
            
            # Logic for Node Colors
            if station == "CGK":
                node_color = "#3B82F6"  # Blue for HQ
            elif "Active" in status_list:
                node_color = "#10B981"  # Green for Active deployment
            else:
                node_color = "#F59E0B"  # Amber for Standby

            # HTML Table strictly formatted for Folium Tooltips
            html_table = f"""
            <div style="font-family:'Plus Jakarta Sans',sans-serif; min-width:260px;">
                <div style="background:#0F172A; color:#F8FAFC; padding:8px 12px; border-radius:6px 6px 0 0; border-bottom:2px solid {node_color};">
                    <strong style="font-size:14px;">HUB {station}</strong><br>
                    <span style="font-size:11px; color:#94A3B8;">Deployed Personnel: {total_px} Px</span>
                </div>
                <table style="width:100%; font-size:11px; background:#1E293B; color:#E2E8F0; border-collapse:collapse;">
            """
            for _, row in station_data.iterrows():
                html_table += f"""
                <tr style="border-bottom:1px solid #334155;">
                    <td style="padding:6px 8px;">{row['Nama']}</td>
                    <td style="padding:6px 8px; color:#94A3B8;">{row['Kualifikasi']}</td>
                </tr>
                """
            html_table += "</table></div>"

            folium.CircleMarker(
                location=coords,
                radius=8,
                color=node_color,
                fill=True,
                fill_color=node_color,
                fill_opacity=0.8,
                tooltip=folium.Tooltip(html_table),
            ).add_to(m)
            
    st_folium(m, width="100%", height=450, returned_objects=[])

# ==============================================================================
# MAIN APPLICATION CONTROLLER
# ==============================================================================
def main():
    st.set_page_config(
        page_title="GMF AeroAsia | Enterprise Command",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    inject_enterprise_css()
    
    # Init Session State
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        
    if not st.session_state.logged_in:
        render_authentication_gateway()
        
    # --- AUTHENTICATED ENVIRONMENT ---
    render_sidebar()
    
    # Header
    st.markdown("""
        <div class="exec-banner">
            <h1>OUTSTATION COMMAND CENTER</h1>
            <p>Tactical Resource Allocation & Telemetry</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Data Layer
    df_raw = fetch_manpower_data()
    
    # Filtering Engine
    search_query = st.text_input("🔍 Global Search (Filter by Name, Qualification, or Station)", placeholder="Enter keyword...")
    if search_query:
        df_display = df_raw[
            df_raw.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        ]
    else:
        df_display = df_raw

    # Telemetry KPIs
    total_px = len(df_display)
    active_px = len(df_display[df_display['Status'].str.strip() == 'Active'])
    standby_px = len(df_display[df_display['Status'].str.strip() == 'Standby'])
    hq_px = len(df_display[df_display['Lokasi'].str.strip() == 'CGK'])

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f"<div class='metric-card' style='border-top: 3px solid #64748B;'><div class='metric-title'>Total Capacity</div><div class='metric-value'>{total_px}</div></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='metric-card' style='border-top: 3px solid #10B981;'><div class='metric-title'>Active Duty</div><div class='metric-value'>{active_px}</div></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='metric-card' style='border-top: 3px solid #F59E0B;'><div class='metric-title'>Standby Alert</div><div class='metric-value'>{standby_px}</div></div>", unsafe_allow_html=True)
    with col4: st.markdown(f"<div class='metric-card' style='border-top: 3px solid #3B82F6;'><div class='metric-title'>HQ (CGK) Reserves</div><div class='metric-value'>{hq_px}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Core Dashboard Layout
    main_col, side_col = st.columns([7, 3])
    
    with main_col:
        st.markdown("<div class='section-header'>📍 Tactical Geospatial Overview</div>", unsafe_allow_html=True)
        st.markdown("<div class='panel-container'>", unsafe_allow_html=True)
        render_spatial_map(df_display)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>📋 Personnel Roster Ledger</div>", unsafe_allow_html=True)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    with side_col:
        st.markdown("<div class='section-header'>📊 Force Analytics</div>", unsafe_allow_html=True)
        st.markdown("<div class='panel-container'>", unsafe_allow_html=True)
        
        with st.popover("📈 View Status Distribution", use_container_width=True):
            st.caption("Real-time operational status ratios.")
            if not df_display.empty:
                st.bar_chart(df_display['Status'].value_counts(), color="#10B981")
                
        with st.popover("⚙️ View Competency Matrix", use_container_width=True):
            st.caption("Top 5 certified qualifications in the field.")
            if not df_display.empty:
                st.bar_chart(df_display['Kualifikasi'].value_counts().head(5), color="#F59E0B")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>🏢 Hub Concentration</div>", unsafe_allow_html=True)
        st.markdown("<div class='panel-container'>", unsafe_allow_html=True)
        if not df_display.empty:
            st.bar_chart(df_display['Lokasi'].value_counts(), color="#3B82F6", height=250)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
