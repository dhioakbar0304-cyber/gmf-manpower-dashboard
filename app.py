import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import ssl

# Bypass SSL Verification for macOS environments
ssl._create_default_https_context = ssl._create_unverified_context

# 1. CORE PAGE CONFIGURATION
st.set_page_config(
    page_title="GMF AeroAsia - Manpower Allocation Dashboard",
    page_icon="https://www.garuda-indonesia.com/favicon.ico", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔑 INITIALIZE SESSION STATE FOR AUTHENTICATION
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# 🎯 SECURE USER DATABASE
USER_DATABASE = {
    "dhioakbar0304": {"password": "gmfsecure01", "role": "PPC Planning & Control"},
    "supervisor_gmf": {"password": "gmfsecure02", "role": "Maintenance Supervisor"}
}

# 🎨 PREMIUM CSS: INTER UI TYPOGRAPHY & APPLE SPRING ANIMATION ARCHITECTURE
st.markdown("""
    <style>
        /* Import Apple-preferred web typography (Inter) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }

        /* GLOBAL CANVAS BACKGROUND */
        .stApp {
            background-image: linear-gradient(rgba(244, 246, 249, 0.94), rgba(244, 246, 249, 0.94)), 
                              url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* 🍏 PREMIUM INSPIRED LEFT SIDEBAR */
        section[data-testid="stSidebar"] {
            background-color: #0B132B !important; 
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        div[data-testid="stSidebarUserContent"] p,
        div[data-testid="stSidebarUserContent"] span,
        div[data-testid="stSidebarUserContent"] h3,
        div[data-testid="stSidebarUserContent"] label {
            font-family: 'Inter', sans-serif !important;
            color: #E2E8F0 !important;
            font-weight: 500;
        }
        
        div[data-testid="stSidebarUserContent"] code {
            background-color: rgba(56, 189, 248, 0.1) !important;
            color: #38BDF8 !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            padding: 4px 8px !important;
            border-radius: 6px;
        }
        
        /* BUTTON ACTIONS */
        div.stButton > button {
            background-color: #1E3A8A !important;
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif !important;
            border-radius: 10px !important;
            border: 1px solid #3B82F6 !important;
            font-weight: 600 !important;
            padding: 12px !important;
            letter-spacing: 0.3px;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        div.stButton > button:hover {
            background-color: #172554 !important;
            transform: translateY(-1px);
            box-shadow: 0px 4px 12px rgba(59, 130, 246, 0.3);
        }
        
        .sheets-btn {
            display: block;
            text-align: center;
            background-color: #16A34A !important;
            color: #FFFFFF !important;
            padding: 12px;
            font-family: 'Inter', sans-serif !important;
            border-radius: 10px;
            font-weight: 600;
            font-size: 13px;
            text-decoration: none;
            margin-top: 10px;
            margin-bottom: 20px;
            border: 1px solid #22C55E;
            transition: all 0.2s ease;
        }
        .sheets-btn:hover {
            background-color: #15803D !important;
            color: #FFFFFF !important;
            text-decoration: none;
            box-shadow: 0px 4px 12px rgba(22, 163, 74, 0.3);
        }
        
        /* HEAD BANNER */
        .gmf-banner {
            background: linear-gradient(135deg, #0B132B 0%, #1C2541 100%);
            padding: 40px 20px;
            border-radius: 16px;
            color: #FFFFFF !important;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px rgba(11, 19, 43, 0.15);
        }
        
        .gmf-banner h1 {
            color: #FFFFFF !important;
            font-size: 38px !important;
            font-weight: 800 !important;
            letter-spacing: 1px;
            margin: 0 !important;
        }
        
        .gmf-banner p {
            color: #38BDF8 !important;
            font-size: 12px !important;
            font-weight: 700;
            letter-spacing: 4px;
            margin-top: 12px !important;
            text-transform: uppercase;
        }

        div[data-testid="stTextInput"] input {
            font-family: 'Inter', sans-serif !important;
            border-radius: 10px !important;
            border: 1px solid #CBD5E1 !important;
            padding: 12px !important;
            font-size: 15px !important;
            background-color: #FFFFFF !important;
        }

        /* KPI CARDS */
        .kpi-card {
            background-color: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.7);
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
            border-top: 4px solid #1E3A8A;
        }
        
        .kpi-title {
            color: #64748B;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        
        .kpi-number {
            font-size: 32px;
            font-weight: 800;
            color: #0F172A;
            margin: 0;
        }

        .section-header {
            font-size: 16px;
            font-weight: 700;
            color: #0F172A;
            margin-top: 32px;
            margin-bottom: 16px;
            border-left: 4px solid #1E3A8A;
            padding-left: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .floating-panel {
            background-color: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.7);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
            margin-bottom: 24px;
        }

        /* =====================================================================
           🍏 NATIVE APPLE POPOVER TRANSITION ARCHITECTURE
           ===================================================================== */
        
        /* Popover Trigger Buttons */
        div[data-testid="stPopover"] > button {
            background-color: rgba(255, 255, 255, 0.8) !important;
            backdrop-filter: blur(12px) !important;
            color: #0F172A !important;
            border: 1px solid rgba(15, 23, 42, 0.12) !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            padding: 12px 20px !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        div[data-testid="stPopover"] > button:hover {
            background-color: #FFFFFF !important;
            border-color: #1E3A8A !important;
        }

        /* Apple Spring Popover Frame Container */
        div[data-testid="stPopoverBody"] {
            background-color: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(30px) !important;
            border-radius: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08) !important;
            padding: 20px !important;
            
            /* Native Apple Spring Animation Matrix */
            animation: appleSpringOpen 0.45s cubic-bezier(0.25, 1.1, 0.4, 1) forwards !important;
            transform-origin: top center !important;
        }

        @keyframes appleSpringOpen {
            0% {
                opacity: 0;
                transform: scale(0.93) translateY(-6px);
            }
            100% {
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# 🔑 GATEWAY CONTROLLER (ENGLISH)
# =====================================================================
if not st.session_state.logged_in:
    col_space_l, col_login_core, col_space_r = st.columns([1, 1.1, 1])
    
    with col_login_core:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; margin-bottom: 25px;">
                <h2 style="color: #0F172A; font-weight: 800; letter-spacing: 0.5px; font-size: 24px; margin:0;">
                    TACTICAL COMMAND PORTAL
                </h2>
                <p style="color: #1E3A8A; font-weight: 700; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; margin-top:6px;">
                    GMF AeroAsia - Outstation Division
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            try:
                st.image("gmf aeroasia logo new blue.png", use_container_width=True)
                st.markdown("<br>", unsafe_allow_html=True)
            except:
                pass

            input_user = st.text_input("Username", placeholder="Enter your personnel ID...", key="login_user")
            input_pass = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
            
            st.markdown("<br>", unsafe_allow_html=True)
            btn_login = st.button("AUTHENTICATE SYSTEM 🔓", use_container_width=True)
            
            if btn_login:
                username_clean = input_user.strip()
                if username_clean in USER_DATABASE and USER_DATABASE[username_clean]["password"] == input_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = username_clean
                    st.session_state.role = USER_DATABASE[username_clean]["role"]
                    st.rerun()
                else:
                    st.error("🚨 Invalid username or password configuration.")
                
    st.stop()


# =====================================================================
# 💻 SYSTEM ENTERPRISE CORE
# =====================================================================

COORDINATE_REGISTRY = {
    "CGK": [-6.1256, 106.6559], "KNO": [3.6422, 98.8853],
    "DPS": [-8.7481, 115.1674], "SUB": [-7.3798, 112.7873],
    "UPG": [-5.0616, 119.5523], "DJJ": [-2.5783, 140.5167],
    "BTH": [1.1211, 104.1182], "BPN": [-1.2683, 116.8944]
}

LINK_EDIT_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/edit"
LINK_EXPORT_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/export?format=csv&gid=827445294"

def load_live_google_sheets():
    try:
        return pd.read_csv(LINK_EXPORT_GOOGLE_SHEETS)
    except Exception as e:
        return pd.DataFrame([{"ID": 551001, "Nama": "Ahmad", "Kualifikasi": "B737 Expert", "Lokasi": "DPS", "Status": "Active", "PPC Pengirim": "Backup Layer"}])

df_raw = load_live_google_sheets()

# SIDEBAR FRAMEWORK
st.sidebar.markdown("<br>", unsafe_allow_html=True)
try:
    st.sidebar.image("gmf aeroasia logo new blue.png", use_container_width=True)
except:
    pass

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 ENGINE CONTROL")
st.sidebar.markdown(f'<a href="{LINK_EDIT_GOOGLE_SHEETS}" target="_blank" class="sheets-btn">🟢 EDIT LIVE MASTER SHEET</a>', unsafe_allow_html=True)

if st.sidebar.button("🔄 RE-SYNC DATASETS", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 SYSTEM USER METRICS")
st.sidebar.markdown(f"""
<div style="line-height: 2.2; font-size: 13px;">
    <p style="margin: 0; color: #94A3B8;">Operator Station:</p>
    <p style="margin: 0 0 12px 0; color: #38BDF8; font-weight: 700; font-size:14px;">{st.session_state.username}</p>
    <p style="margin: 0; color: #94A3B8;">Privilege Matrix:</p>
    <p style="margin: 0; color: #38BDF8; font-weight: 700; font-size:14px;">{st.session_state.role}</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
if st.sidebar.button("🔴 TERMINATE SESSION", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# COMMAND CENTER BANNER
st.markdown('<div class="gmf-banner"><h1>GMF AEROASIA</h1><p>Tactical Outstation Manpower Command Center</p></div>', unsafe_allow_html=True)

# INTELLIGENT SEARCH
st.markdown("<div class='section-header'>🔎 Tactical Resource Search Engine</div>", unsafe_allow_html=True)
search_query = st.text_input("Query filter directory by Name, Qualification, or Station Hub:", "")

if search_query:
    df_filtered = df_raw[
        df_raw['Nama'].str.contains(search_query, case=False, na=False) |
        df_raw['Kualifikasi'].str.contains(search_query, case=False, na=False) |
        df_raw['Lokasi'].str.contains(search_query, case=False, na=False)
    ]
else:
    df_filtered = df_raw

# EXECUTIVE TELEMETRY METRICS
total_px = len(df_filtered)
active_px = len(df_filtered[df_filtered['Status'].str.strip() == 'Active'])
standby_px = len(df_filtered[df_filtered['Status'].str.strip() == 'Standby'])
cgk_px = len(df_filtered[df_filtered['Lokasi'].str.strip() == 'CGK'])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">📁 Fleet Capacity</div><div class="kpi-number">{total_px} Px</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card" style="border-top-color: #16A34A;"><div class="kpi-title" style="color:#16A34A;">🟢 Active Deployment</div><div class="kpi-number">{active_px} Px</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card" style="border-top-color: #D97706;"><div class="kpi-title" style="color:#D97706;">🟡 Standby Status</div><div class="kpi-number">{standby_px} Px</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-card" style="border-top-color: #2563EB;"><div class="kpi-title" style="color:#2563EB;">🔵 Hub CGK Force</div><div class="kpi-number">{cgk_px} Px</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# MONITORING MATRIX SPLIT
col_left, col_right = st.columns([4, 3])

with col_left:
    st.markdown("<div class='section-header'>🗺️ Live Tactical Spatial Distribution</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    
    # Initialize Core Map Canvas
    m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles="OpenStreetMap")
    
    # RENDER SPATIAL MARKERS AND DETAILED DATA POPUPS
    for station, coords in COORDINATE_REGISTRY.items():
        sub_df = df_filtered[df_filtered['Lokasi'].str.strip() == station]
        if not sub_df.empty:
            station_total = len(sub_df)
            marker_color = "red" if station == "CGK" else ("green" if any(sub_df['Status'].str.strip() == 'Active') else "orange")
            
            # Formulating pristine responsive data tables inside map nodes
            popup_html = f"""
            <div style='font-family: "Inter", sans-serif; color: #0F172A; min-width:250px;'>
                <h4 style='margin:0 0 4px 0; color:#1E3A8A; font-weight:700;'>Station Hub: {station}</h4>
                <p style='margin:0 0 10px 0; font-size:12px; color:#64748B;'>Active Registry: <b>{station_total} Crew</b></p>
                <table style='width:100%; font-size:11px; border-collapse: collapse;'>
                    <tr style='background-color:#F1F5F9; text-align:left; border-bottom: 2px solid #E2E8F0;'>
                        <th style='padding:6px 4px; font-weight:600;'>Name</th>
                        <th style='padding:6px 4px; font-weight:600;'>Qualification</th>
                    </tr>
            """
            for _, row in sub_df.iterrows():
                popup_html += f"""
                <tr>
                    <td style='padding:6px 4px; border-bottom:1px solid #E2E8F0; font-weight:500;'>{row['Nama']}</td>
                    <td style='padding:6px 4px; border-bottom:1px solid #E2E8F0; color:#475569;'>{row['Kualifikasi']}</td>
                </tr>
                """
            popup_html += "</table></div>"
            
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"Hub {station}: {station_total} Px Available",
                icon=folium.Icon(color=marker_color, icon="info-sign")
            ).add_to(m)
            
    st_folium(m, width="100%", height=520)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div class='section-header'>📋 Personnel Directory Ledger</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='section-header'>📊 Advanced Manpower Analytics</div>", unsafe_allow_html=True)
    
    pop_col1, pop_col2 = st.columns(2)
    
    with pop_col1:
        # Popover 1: Micro UI Container Engine
        with st.popover("⚙️ View Deployment Telemetry", use_container_width=True):
            st.markdown("<h4 style='color:#0F172A; font-size:14px; font-weight:700; margin:0 0 4px 0;'>📊 Duty Distribution Status</h4>", unsafe_allow_html=True)
            st.caption("Active operational breakdown of real-time statuses.")
            if not df_filtered.empty:
                st.bar_chart(df_filtered['Status'].value_counts(), color="#16A34A", height=200)
                
    with pop_col2:
        # Popover 2: Micro UI Container Engine
        with st.popover("✈️ Inspect Type Ratings", use_container_width=True):
            st.markdown("<h4 style='color:#0F172A; font-size:14px; font-weight:700; margin:0 0 4px 0;'>🚀 Fleet Skillset Capability</h4>", unsafe_allow_html=True)
            st.caption("Top 5 certified active competencies monitored.")
            if not df_filtered.empty:
                st.bar_chart(df_filtered['Kualifikasi'].value_counts().head(5), color="#D97706", height=200)
                
    st.markdown("<div class='section-header'>📈 Station Concentration Metrics</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    if not df_filtered.empty:
        st.bar_chart(df_filtered['Lokasi'].value_counts(), color="#1E3A8A", height=280)
    st.markdown('</div>', unsafe_allow_html=True)
