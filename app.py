import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
from streamlit_folium import st_folium
import ssl
import os
import time
from datetime import datetime

# Bypass verifikasi SSL Certificate
ssl._create_default_https_context = ssl._create_unverified_context

# 1. KONFIGURASI HALAMAN UTAMA
st.set_page_config(
    page_title="GMF AeroAsia | Manpower Allocation",
    page_icon="pngegg.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🏢 CONFIG LOGO UTAMA GMF AEROASIA
LOGO_SOURCE = "gmf aeroasia logo new blue.png"

# INITIALIZE SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "last_df" not in st.session_state:
    st.session_state.last_df = None
if "activity_logs" not in st.session_state:
    st.session_state.activity_logs = [
        {"time": datetime.now().strftime("%H:%M:%S"), "msg": "Sistem diinisialisasi. Memantau data live..."}
    ]

# DATABASE USER
USER_DATABASE = {
    "dhioakbar0304": {"password": "gmfsecure01", "role": "PPC Planning & Control"},
    "supervisor_gmf": {"password": "gmfsecure02", "role": "Maintenance Supervisor"}
}

# ============================================================================
# 🖋️  ICON SYSTEM — small monoline SVGs (stroke-based, no emoji) for a
#     cleaner enterprise look. Each returns an inline <svg> string.
# ============================================================================
def icon(name, size=18, color="currentColor", stroke=1.8):
    paths = {
        "users": '<path d="M17 21v-1.5a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4V21"/><circle cx="9.5" cy="7.5" r="3.5"/><path d="M22 21v-1.5a4 4 0 0 0-3-3.87"/><path d="M15 3.6a3.5 3.5 0 0 1 0 6.8"/>',
        "check": '<circle cx="12" cy="12" r="9"/><path d="M7.5 12.5l3 3 6-6.5"/>',
        "alert": '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.2"/><circle cx="12" cy="16.3" r="0.4" fill="currentColor" stroke="none"/>',
        "pin": '<path d="M19.5 10c0 6-7.5 11.5-7.5 11.5S4.5 16 4.5 10a7.5 7.5 0 1 1 15 0z"/><circle cx="12" cy="10" r="2.7"/>',
        "pulse": '<path d="M22 12.5h-4.2l-2.6 7-5.4-15-2.6 8H2"/>',
        "refresh": '<path d="M20.5 12a8.5 8.5 0 1 1-2.8-6.3"/><path d="M20.5 4v5h-5"/>',
        "logout": '<path d="M9.5 20.5H6a2 2 0 0 1-2-2v-13a2 2 0 0 1 2-2h3.5"/><path d="M15.5 16.5l4.5-4.5-4.5-4.5"/><path d="M20 12H9.5"/>',
        "sheet": '<rect x="3.5" y="3.5" width="17" height="17" rx="2.5"/><path d="M3.5 9.5h17"/><path d="M9 20.5V9.5"/>',
        "layers": '<path d="M12 2.5 2.5 7.5 12 12.5l9.5-5-9.5-5z"/><path d="M2.5 16.5 12 21.5l9.5-5"/><path d="M2.5 12 12 17l9.5-5"/>',
        "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
        "shield": '<path d="M12 21.5S4.5 17.8 4.5 11V5.3L12 2.5l7.5 2.8V11c0 6.8-7.5 10.5-7.5 10.5z"/>',
        "id": '<rect x="2.5" y="5.5" width="19" height="13" rx="2.2"/><circle cx="8" cy="12" r="2.1"/><path d="M5.5 16c.6-1.4 1.6-2.1 2.5-2.1s1.9.7 2.5 2.1"/><path d="M14 9.5h4"/><path d="M14 13h4"/>',
        "lock": '<rect x="5" y="10.5" width="14" height="9.5" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
        "plane": '<path d="M2.5 16l19-6.5-2-2-7 2-6-4.5-2 .7 3.8 5.5-4.3 1.5z"/><path d="M8 18.5l2-.6.7 2-3.2 1z"/>',
    }
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;">{paths.get(name, "")}</svg>'

# ============================================================================
# 🎨 DESIGN SYSTEM — "Flight Ops Console" v2 (softer, corporate-grade)
# ============================================================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800;900&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        :root {
            --navy-950: #070F1A;
            --navy-900: #0D1B2A;
            --navy-800: #14283C;
            --steel-700: #0B4870;
            --steel-600: #0E5C8C;
            --steel-400: #3E93BE;
            --cyan-400: #22C3E6;
            --slate-50: #F7F9FC;
            --slate-100: #EEF2F7;
            --slate-200: #E4E9F0;
            --slate-400: #8D9BAF;
            --slate-500: #5B6B80;
            --ink-900: #0B1220;
            --success: #148F5E;
            --success-bg: #E7F6EF;
            --warning: #B8730F;
            --warning-bg: #FBF0DD;
            --danger: #C5303A;
            --danger-bg: #FBE7E8;
            --radius-lg: 16px;
            --radius-md: 12px;
            --shadow-sm: 0 1px 2px rgba(11, 18, 32, 0.05);
            --shadow-md: 0 4px 16px rgba(11, 18, 32, 0.06);
            --shadow-lg: 0 12px 32px rgba(11, 18, 32, 0.10);
        }

        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; color: var(--ink-900); }
        h1, h2, h3, .display-font { font-family: 'Montserrat', sans-serif !important; }
        .mono { font-family: 'JetBrains Mono', monospace !important; }

        .stApp {
            background-color: var(--slate-50);
            background-image:
                radial-gradient(circle at 100% 0%, rgba(34, 195, 230, 0.05), transparent 45%),
                linear-gradient(rgba(11, 72, 112, 0.045) 1px, transparent 1px),
                linear-gradient(90deg, rgba(11, 72, 112, 0.045) 1px, transparent 1px);
            background-size: auto, 44px 44px, 44px 44px;
            background-attachment: fixed;
        }

        #MainMenu, footer { visibility: hidden; }
        .block-container { padding-top: 1.6rem !important; }

        /* ---- Search field ---- */
        div[data-testid="stTextInput"] label {
            color: var(--slate-500) !important; font-weight: 600 !important; font-size: 11.5px !important;
            letter-spacing: 0.6px; text-transform: uppercase;
        }
        div[data-testid="stTextInput"] input {
            font-family: 'Inter', sans-serif !important;
            border: 1.5px solid var(--slate-200) !important;
            background-color: #FFFFFF !important;
            color: var(--ink-900) !important;
            border-radius: 11px !important;
            padding: 12px 16px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            box-shadow: var(--shadow-sm) !important;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: var(--steel-400) !important;
            box-shadow: 0 0 0 4px rgba(14, 92, 140, 0.10) !important;
        }

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] { background-color: var(--navy-950) !important; border-right: 1px solid rgba(255,255,255,0.06); }
        div[data-testid="stSidebarUserContent"] p, div[data-testid="stSidebarUserContent"] span,
        div[data-testid="stSidebarUserContent"] h3, div[data-testid="stSidebarUserContent"] label {
            color: #C9D6E3 !important; font-family: 'Inter', sans-serif !important; font-weight: 500;
        }
        .sidebar-eyebrow {
            color: var(--slate-400) !important; font-family: 'Inter', sans-serif !important; font-size: 10.5px !important;
            letter-spacing: 1.4px; text-transform: uppercase; font-weight: 700 !important; margin: 22px 0 10px 2px;
            display: flex; align-items: center; gap: 7px;
        }
        .sidebar-user-card {
            background: linear-gradient(155deg, var(--navy-900), var(--navy-950));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: var(--radius-md);
            padding: 16px 18px;
            margin-bottom: 6px;
            display: flex; align-items: center; gap: 12px;
        }
        .sidebar-avatar {
            width: 38px; height: 38px; border-radius: 10px; flex-shrink: 0;
            background: linear-gradient(155deg, var(--steel-600), var(--cyan-400));
            display: flex; align-items: center; justify-content: center;
            color: #fff; font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 14px;
        }
        .sidebar-user-name { color: #FFFFFF !important; font-weight: 700 !important; font-size: 13.5px; margin: 0; line-height: 1.3; }
        .sidebar-user-role { color: var(--slate-400) !important; font-size: 11px; margin: 1px 0 0 0; }

        div.stButton > button {
            background-color: rgba(255,255,255,0.04) !important;
            color: #DCE6F0 !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            font-weight: 600 !important;
            font-size: 12.5px !important;
            padding: 10px 14px !important;
            letter-spacing: 0.2px;
            text-align: left !important;
            transition: all 0.15s ease;
        }
        div.stButton > button:hover {
            background-color: rgba(34, 195, 230, 0.10) !important;
            border-color: var(--cyan-400) !important;
            color: #FFFFFF !important;
        }
        .sheets-btn {
            display: flex; align-items: center; gap: 9px; justify-content: center;
            background: linear-gradient(135deg, #0F7A47, #12925A) !important;
            color: #FFFFFF !important; padding: 11px; border-radius: 10px; font-weight: 600; font-size: 12.5px;
            text-decoration: none; margin-top: 8px; margin-bottom: 4px; letter-spacing: 0.2px;
            box-shadow: 0 4px 14px rgba(15, 122, 71, 0.25);
            transition: all 0.15s ease;
        }
        .sheets-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(15, 122, 71, 0.35); }

        /* ---- Login split panel ---- */
        .login-brand-panel {
            background: linear-gradient(160deg, var(--navy-950) 0%, var(--navy-900) 55%, var(--steel-700) 130%);
            border-radius: var(--radius-lg);
            padding: 46px 40px;
            height: 100%;
            min-height: 460px;
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
        }
        .login-brand-panel::before {
            content: "";
            position: absolute; inset: 0;
            background-image: linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px),
                               linear-gradient(90deg, rgba(255,255,255,0.045) 1px, transparent 1px);
            background-size: 34px 34px;
            pointer-events: none;
        }
        .login-brand-eyebrow {
            color: var(--cyan-400); font-family: 'JetBrains Mono', monospace; font-size: 11px;
            letter-spacing: 2.2px; text-transform: uppercase; font-weight: 600; margin: 0 0 14px 0; position: relative;
        }
        .login-brand-title {
            color: #FFFFFF; font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 26px;
            line-height: 1.35; margin: 0 0 18px 0; position: relative; max-width: 320px;
        }
        .login-brand-sub {
            color: #A9BCCF; font-size: 13.5px; line-height: 1.6; margin: 0 0 32px 0; position: relative; max-width: 300px;
        }
        .login-brand-feature {
            display: flex; align-items: center; gap: 12px; color: #DCE6F0; font-size: 12.5px;
            font-weight: 500; margin-bottom: 14px; position: relative;
        }
        .login-brand-feature .feat-icon {
            width: 30px; height: 30px; border-radius: 8px; background: rgba(34, 195, 230, 0.14);
            display: flex; align-items: center; justify-content: center; color: var(--cyan-400); flex-shrink: 0;
        }
        .login-card {
            background-color: #FFFFFF;
            padding: 44px 40px;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--slate-200);
            height: 100%;
        }
        .login-eyebrow {
            color: var(--steel-600); font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: 10.5px;
            letter-spacing: 2.2px; text-transform: uppercase; margin: 0 0 8px 0;
        }
        .login-title { color: var(--ink-900); font-weight: 800; font-size: 22px; letter-spacing: 0.2px; margin: 0 0 8px 0; }
        .login-hint { color: var(--slate-500); font-size: 12.5px; margin: 0 0 28px 0; }
        .login-footnote {
            display: flex; align-items: center; gap: 7px; color: var(--slate-400); font-size: 11.5px;
            margin-top: 22px; justify-content: center;
        }

        /* ---- KPI blocks ---- */
        .kpi-card {
            background-color: #FFFFFF; border: 1px solid var(--slate-200);
            padding: 20px 22px; border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md); margin-bottom: 22px;
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }
        .kpi-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
        .kpi-icon {
            width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
            margin-bottom: 14px;
        }
        .kpi-title { color: var(--slate-500); font-size: 10.5px; font-weight: 700; margin-bottom: 6px; letter-spacing: 1.2px; text-transform: uppercase; }
        .kpi-number { font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 700; color: var(--ink-900); margin: 0; letter-spacing: -0.6px; }
        .kpi-unit { font-family: 'Inter', sans-serif; font-size: 12.5px; font-weight: 500; color: var(--slate-400); margin-left: 5px; }

        .section-header {
            font-family: 'Montserrat', sans-serif; font-size: 13px; font-weight: 700; color: var(--ink-900);
            margin-top: 4px; margin-bottom: 16px; letter-spacing: 0.6px; text-transform: uppercase;
            display: flex; align-items: center; gap: 10px;
        }
        .section-header .sh-icon {
            width: 26px; height: 26px; border-radius: 8px; background: var(--slate-100); color: var(--steel-600);
            display: flex; align-items: center; justify-content: center;
        }

        .floating-panel {
            background-color: #FFFFFF; border: 1px solid var(--slate-200); border-radius: var(--radius-lg);
            padding: 20px; box-shadow: var(--shadow-md); margin-bottom: 20px;
        }

        @keyframes blinker { 50% { opacity: 0.3; } }
        .status-pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 11px; border-radius: 20px; font-size: 11.5px; font-weight: 700; letter-spacing: 0.2px; }
        .status-active { color: var(--success); background: var(--success-bg); }
        .status-standby { color: var(--warning); background: var(--warning-bg); }
        .status-offline { color: var(--danger); background: var(--danger-bg); animation: blinker 1.3s ease-in-out infinite; }

        .table-wrapper { width: 100% !important; overflow: hidden !important; border-radius: var(--radius-md); border: 1px solid var(--slate-200); }
        .styled-table { width: 100%; border-collapse: collapse; font-size: 12.5px; text-align: left; background-color: transparent; }
        .styled-table thead tr { background: linear-gradient(135deg, var(--navy-950), var(--navy-900)); color: #E7EEF5; }
        .styled-table th { padding: 13px 18px; font-weight: 600; font-size: 10.5px; letter-spacing: 0.8px; text-transform: uppercase; }
        .styled-table td { padding: 12px 18px; border-bottom: 1px solid var(--slate-100); white-space: nowrap; color: var(--ink-900); }
        .styled-table tbody tr:last-child td { border-bottom: none; }
        .styled-table tbody tr:nth-of-type(even) { background-color: var(--slate-50); }
        .styled-table tbody tr:hover { background-color: #EAF3F9; }

        .activity-item { padding: 11px 0; border-bottom: 1px solid var(--slate-100); font-size: 12.5px; color: #334155; display: flex; gap: 10px; }
        .activity-item:last-child { border-bottom: none; }
        .activity-time { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--steel-600); font-size: 11px; flex-shrink: 0; padding-top: 1px; }
    </style>
""", unsafe_allow_html=True)

# LOGIN CONTROLLER
if not st.session_state.logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    col_space_l, col_login_core, col_space_r = st.columns([0.6, 2.2, 0.6])
    with col_login_core:
        col_brand, col_form = st.columns([1, 1], gap="medium")

        with col_brand:
            st.markdown(f"""
                <div class="login-brand-panel">
                    <p class="login-brand-eyebrow">GMF AeroAsia · Digital Operations</p>
                    <h2 class="login-brand-title">Satu dasbor untuk seluruh personel outstation Anda.</h2>
                    <p class="login-brand-sub">Pantau distribusi tenaga kerja, kualifikasi, dan status kesiapan di seluruh stasiun secara real-time.</p>
                    <div class="login-brand-feature"><span class="feat-icon">{icon('pin', 15)}</span> 8 stasiun hub terhubung live</div>
                    <div class="login-brand-feature"><span class="feat-icon">{icon('pulse', 15)}</span> Sinkronisasi data setiap 5 detik</div>
                    <div class="login-brand-feature"><span class="feat-icon">{icon('shield', 15)}</span> Akses berbasis peran &amp; personel</div>
                </div>
            """, unsafe_allow_html=True)

        with col_form:
            if os.path.exists(LOGO_SOURCE):
                st.image(LOGO_SOURCE, width=150)
            st.markdown(
                '<div class="login-card">'
                '<p class="login-eyebrow">Tactical Outstation Command</p>'
                '<h3 class="login-title">Masuk ke Sistem</h3>'
                '<p class="login-hint">Gunakan kredensial resmi perusahaan untuk melanjutkan.</p>',
                unsafe_allow_html=True
            )
            input_user = st.text_input("Username", placeholder="Masukkan ID personel Anda...", key="login_user")
            input_pass = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            btn_login = st.button("Masuk ke Dashboard →", use_container_width=True)

            if btn_login:
                username_clean = input_user.strip()
                if username_clean in USER_DATABASE and USER_DATABASE[username_clean]["password"] == input_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = username_clean
                    st.session_state.role = USER_DATABASE[username_clean]["role"]
                    st.rerun()
                else:
                    st.error("🚨 Username atau password salah.")
            st.markdown(
                f'<div class="login-footnote">{icon("lock", 13)} Akses termonitor &amp; dilindungi kebijakan IT Security GMF</div>'
                '</div>',
                unsafe_allow_html=True
            )
    st.stop()

# DATA SOURCE CONFIG
DOKUMEN_KOORDINAT = {
    "CGK": [-6.1256, 106.6559], "KNO": [3.6422, 98.8853],
    "DPS": [-8.7481, 115.1674], "SUB": [-7.3798, 112.7873],
    "UPG": [-5.0616, 119.5523], "DJJ": [-2.5783, 140.5167],
    "BTH": [1.1211, 104.1182], "BPN": [-1.2683, 116.8944]
}

LINK_EDIT_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/edit"
LINK_EXPORT_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/export?format=csv&gid=827445294"

@st.cache_data(ttl=5)
def load_live_google_sheets():
    try:
        return pd.read_csv(LINK_EXPORT_GOOGLE_SHEETS)
    except Exception as e:
        return pd.DataFrame([{"ID": 551001, "Nama": "Ahmad", "Kualifikasi": "B737 Engine Expert", "Lokasi": "DPS", "Status": "Active", "PPC Pengirim": "Backup"}])

df_mentah = load_live_google_sheets()

# REAL LIVE DIFF LOGIC TRACKING
if st.session_state.last_df is not None:
    try:
        merged = st.session_state.last_df.merge(df_mentah, on="ID", suffixes=('_old', '_new'))
        for _, row in merged.iterrows():
            stat_old = str(row.get('Status_old', '')).strip()
            stat_new = str(row.get('Status_new', '')).strip()

            if stat_old.lower() != stat_new.lower():
                st.session_state.activity_logs.insert(0, {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "msg": f"Status <b>{row.get('Nama_new', 'Personel')}</b> berubah: <span style='color:#B8730F;'>{stat_old}</span> → <span style='color:#148F5E;'>{stat_new}</span>"
                })

        new_ids = set(df_mentah["ID"]) - set(st.session_state.last_df["ID"])
        for nid in new_ids:
            nama_baru = df_mentah[df_mentah["ID"] == nid]["Nama"].iloc[0]
            st.session_state.activity_logs.insert(0, {
                "time": datetime.now().strftime("%H:%M:%S"),
                "msg": f"Personel baru terdeteksi: <b>{nama_baru}</b>"
            })
    except Exception as e:
        pass

st.session_state.last_df = df_mentah.copy()
st.session_state.activity_logs = st.session_state.activity_logs[:5]

# SIDEBAR CONTROL & LOGO
if os.path.exists(LOGO_SOURCE):
    st.sidebar.image(LOGO_SOURCE, use_container_width=True)

user_initial = st.session_state.username[:2].upper() if st.session_state.username else "??"
st.sidebar.markdown(
    f'<div class="sidebar-user-card">'
    f'<div class="sidebar-avatar">{user_initial}</div>'
    f'<div><p class="sidebar-user-name">{st.session_state.username}</p>'
    f'<p class="sidebar-user-role">{st.session_state.role}</p></div>'
    f'</div>',
    unsafe_allow_html=True
)

st.sidebar.markdown(f'<p class="sidebar-eyebrow">{icon("sheet", 13)} Input &amp; Update Data</p>', unsafe_allow_html=True)
st.sidebar.markdown(f'<a href="{LINK_EDIT_GOOGLE_SHEETS}" target="_blank" class="sheets-btn">{icon("sheet", 15, "#FFFFFF")} Edit Live Excel Sheet</a>', unsafe_allow_html=True)
st.sidebar.markdown(f'<p class="sidebar-eyebrow">{icon("refresh", 13)} Control Panel</p>', unsafe_allow_html=True)
if st.sidebar.button(f"⟳   Re-sync Live Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
if st.sidebar.button(f"⏻   Secure Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# ---- LIVE HEADER STRIP (real-time WIB clock, self-contained JS component) ----
components.html(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600&family=JetBrains+Mono:wght@500;600&display=swap');
        html, body {{ margin:0; padding:0; background:transparent; }}
        .strip {{
            display:flex; align-items:center; justify-content:space-between;
            background: linear-gradient(90deg, #070F1A 0%, #0D1B2A 100%);
            border: 1px solid #0B4870; border-radius: 14px; padding: 12px 22px;
            font-family:'Inter', sans-serif; box-shadow: 0 6px 20px rgba(7,15,26,0.18);
        }}
        .strip-left {{ display:flex; align-items:center; gap:10px; }}
        .dot {{ width:8px; height:8px; border-radius:50%; background:#22C3E6; box-shadow:0 0 0 4px rgba(34,195,230,0.16); animation: pulse 2s ease-in-out infinite; }}
        @keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}
        .label {{ color:#DCEAF3; font-size:12px; font-weight:600; letter-spacing:0.4px; }}
        .clock {{ color:#8FB4CE; font-family:'JetBrains Mono', monospace; font-size:12.5px; font-weight:500; letter-spacing:0.3px; }}
    </style>
    <div class="strip">
        <div class="strip-left"><div class="dot"></div><span class="label">GMF AeroAsia — Live Feed Connected</span></div>
        <div class="clock" id="liveClock">—</div>
    </div>
    <script>
        function tick() {{
            const now = new Date();
            const fmt = new Intl.DateTimeFormat('id-ID', {{
                timeZone: 'Asia/Jakarta', weekday: 'long', day: '2-digit', month: 'long', year: 'numeric',
                hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
            }});
            document.getElementById('liveClock').textContent = fmt.format(now) + ' WIB';
        }}
        tick();
        setInterval(tick, 1000);
    </script>
""", height=58)

st.markdown("<br>", unsafe_allow_html=True)

# 🏢 MAIN BANNER
st.markdown("""
    <div style="padding-top: 2px;">
        <h2 style="color: #0B1220; font-weight: 900; margin: 0; letter-spacing: 0.3px;">Manpower Allocation Dashboard</h2>
        <p style="color: #0E5C8C; font-size: 12.5px; font-weight: 600; letter-spacing: 2.2px; margin-top: 6px; text-transform: uppercase; font-family: 'JetBrains Mono', monospace;">Outstation Personnel Monitoring System</p>
    </div>
""", unsafe_allow_html=True)
st.markdown('<hr style="border: none; border-top: 1.5px solid #E4E9F0; margin-top: 16px; margin-bottom: 26px;">', unsafe_allow_html=True)

# SEARCH CONTAINER
search_query = st.text_input("Pencarian berdasarkan nama / kualifikasi / stasiun hub", placeholder="Ketik nama personel atau kode stasiun di sini...")

if search_query:
    df_pekerja = df_mentah[
        df_mentah['Nama'].astype(str).str.contains(search_query, case=False, na=False) |
        df_mentah['Kualifikasi'].astype(str).str.contains(search_query, case=False, na=False) |
        df_mentah['Lokasi'].astype(str).str.contains(search_query, case=False, na=False)
    ]
else:
    df_pekerja = df_mentah

# KPI BLOCKS
total_personel = len(df_pekerja)
personel_aktif = len(df_pekerja[df_pekerja['Status'].astype(str).str.strip().str.lower() == 'active'])
personel_standby = len(df_pekerja[df_pekerja['Status'].astype(str).str.strip().str.lower() == 'standby'])
jumlah_di_cgk = len(df_pekerja[df_pekerja['Lokasi'].astype(str).str.strip() == 'CGK'])

st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'''<div class="kpi-card">
    <div class="kpi-icon" style="background:#EAF3F9; color:#0E5C8C;">{icon("users", 19)}</div>
    <div class="kpi-title">Total Fleet Manpower</div>
    <div class="kpi-number">{total_personel}<span class="kpi-unit">personel</span></div>
</div>''', unsafe_allow_html=True)
c2.markdown(f'''<div class="kpi-card">
    <div class="kpi-icon" style="background:#E7F6EF; color:#148F5E;">{icon("check", 19)}</div>
    <div class="kpi-title" style="color:#148F5E;">Active On Duty</div>
    <div class="kpi-number">{personel_aktif}<span class="kpi-unit">personel</span></div>
</div>''', unsafe_allow_html=True)
c3.markdown(f'''<div class="kpi-card">
    <div class="kpi-icon" style="background:#FBF0DD; color:#B8730F;">{icon("alert", 19)}</div>
    <div class="kpi-title" style="color:#B8730F;">Standby Alert</div>
    <div class="kpi-number">{personel_standby}<span class="kpi-unit">personel</span></div>
</div>''', unsafe_allow_html=True)
c4.markdown(f'''<div class="kpi-card">
    <div class="kpi-icon" style="background:#E9F8FC; color:#0E5C8C;">{icon("pin", 19)}</div>
    <div class="kpi-title">CGK Ready Resource</div>
    <div class="kpi-number">{jumlah_di_cgk}<span class="kpi-unit">personel</span></div>
</div>''', unsafe_allow_html=True)

# ROW ATAS: MAP DISTRIBUSI VS LIVE TELEMETRY LOGS
col_left, col_right = st.columns([55, 45])

with col_left:
    st.markdown(f"<div class='section-header'><span class='sh-icon'>{icon('pin', 14)}</span>Live Tactical Spatial Distribution</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)

    m = folium.Map(location=[-0.7893, 113.9213], zoom_start=5, tiles="CartoDB positron")

    for lok, koordinat in DOKUMEN_KOORDINAT.items():
        sub_df = df_pekerja[df_pekerja['Lokasi'].astype(str).str.strip() == lok]
        if not sub_df.empty:
            statuses = [str(x).lower().strip() for x in sub_df['Status'].tolist()]
            warna_pin = "green" if 'active' in statuses else ("orange" if 'standby' in statuses else "red")

            popup_html = f"""
            <div style='font-family: "Inter", sans-serif; color: #0B1220; min-width:240px;'>
                <h4 style='margin:0 0 5px 0; color:#0E5C8C; font-weight:800; font-family:"Montserrat",sans-serif;'>Station Hub: {lok}</h4>
                <table style='width:100%; font-size:11px; border-collapse: collapse;'>
                    <tr style='background-color:#F7F9FC; text-align:left;'>
                        <th style='padding:4px;'>Nama</th>
                        <th style='padding:4px;'>Status</th>
                    </tr>
            """
            for _, row in sub_df.iterrows():
                sv = str(row['Status']).strip()
                s_html = f"<span style='color:#148F5E;font-weight:700;'>● Active</span>" if sv.lower() == 'active' else (f"<span style='color:#B8730F;font-weight:700;'>● Standby</span>" if sv.lower() == 'standby' else f"<span style='color:#C5303A;font-weight:800;'>● {sv}</span>")
                popup_html += f"<tr><td style='padding:4px; border-bottom:1px solid #E4E9F0;'>{row['Nama']}</td><td style='padding:4px; border-bottom:1px solid #E4E9F0;'>{s_html}</td></tr>"
            popup_html += "</table></div>"

            folium.Marker(location=koordinat, popup=folium.Popup(popup_html, max_width=350), icon=folium.Icon(color=warna_pin)).add_to(m)

    st_folium(m, width="100%", height=380)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown(f"<div class='section-header'><span class='sh-icon'>{icon('pulse', 14)}</span>Operational Telemetry &amp; Logs</div>", unsafe_allow_html=True)

    pop_col1, pop_col2 = st.columns(2)
    with pop_col1:
        with st.popover("Status Telemetry Chart", use_container_width=True):
            if not df_pekerja.empty: st.bar_chart(df_pekerja['Status'].value_counts(), color="#0E5C8C", height=150)
    with pop_col2:
        with st.popover("Core Fleet Capabilities", use_container_width=True):
            if not df_pekerja.empty: st.bar_chart(df_pekerja['Kualifikasi'].value_counts().head(5), color="#22C3E6", height=150)

    st.markdown('<div class="floating-panel" style="margin-top: 10px;">', unsafe_allow_html=True)
    utilization_rate = int((personel_aktif / total_personel) * 100) if total_personel > 0 else 0
    st.markdown(f"""
        <div style="margin-bottom: 7px; font-size: 12.5px; font-weight: 600; color: #334155;">Active Deployment Load <span class="mono" style="color:#0E5C8C;">({utilization_rate}%)</span></div>
        <div style="width: 100%; background-color: #E4E9F0; border-radius: 10px; height: 8px; margin-bottom: 20px; overflow:hidden;">
            <div style="width: {utilization_rate}%; background: linear-gradient(90deg, #0E5C8C, #22C3E6); border-radius: 10px; height: 8px;"></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<h4 style='color:#0B1220; font-size:12px; font-weight:700; margin:8px 0 10px 0; text-transform:uppercase; letter-spacing:0.6px; font-family:\"Montserrat\",sans-serif; display:flex; align-items:center; gap:8px;'>{icon('pulse', 13, '#5B6B80')} Live Activity Feed</h4>", unsafe_allow_html=True)
    logs_html = ""
    for log in st.session_state.activity_logs:
        logs_html += f'<div class="activity-item"><span class="activity-time">{log["time"]}</span><span>{log["msg"]}</span></div>'
    st.markdown(logs_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 🚨 ROW BAWAH (ISOLASI PARALEL): FULL-WIDTH ANTI TABRAKAN
st.markdown(f"<div class='section-header'><span class='sh-icon'>{icon('layers', 14)}</span>Personnel Directory Master Ledger</div>", unsafe_allow_html=True)
st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)

def render_status(status):
    v = str(status).strip()
    if v.lower() == 'active': return '<span class="status-pill status-active">● Active</span>'
    elif v.lower() == 'standby': return '<span class="status-pill status-standby">● Standby</span>'
    else: return f'<span class="status-pill status-offline">● {v}</span>'

df_html = df_pekerja.copy()
df_html['Status'] = df_html['Status'].apply(render_status)
st.markdown(df_html.to_html(escape=False, index=False, classes="styled-table"), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
