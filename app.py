import streamlit as st
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
# 🎨 DESIGN SYSTEM — "Flight Ops Console"
# Palette   : deep hangar-navy base, steel-blue structure, cyan telemetry accent
# Type      : Montserrat (display/eyebrows) + Inter (body/UI) + JetBrains Mono (data)
# Signature : slim FIDS-style status strip + blueprint grid backdrop
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
            --slate-50: #F5F8FB;
            --slate-100: #EDF1F6;
            --slate-200: #E1E8F0;
            --slate-400: #90A0B4;
            --slate-500: #5B6B80;
            --ink-900: #0B1220;
            --success: #148F5E;
            --success-bg: #E7F6EF;
            --warning: #B8730F;
            --warning-bg: #FBF0DD;
            --danger: #C5303A;
            --danger-bg: #FBE7E8;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            color: var(--ink-900);
        }

        h1, h2, h3, .display-font {
            font-family: 'Montserrat', sans-serif !important;
        }

        .mono {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Blueprint-grid backdrop — quiet engineering-drafting texture, no stock photography */
        .stApp {
            background-color: var(--slate-50);
            background-image:
                linear-gradient(rgba(245, 248, 251, 0.94), rgba(245, 248, 251, 0.97)),
                linear-gradient(rgba(11, 72, 112, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(11, 72, 112, 0.05) 1px, transparent 1px);
            background-size: auto, 42px 42px, 42px 42px;
            background-attachment: fixed;
        }

        /* Hide default Streamlit chrome for a cleaner console feel */
        #MainMenu, footer { visibility: hidden; }

        /* ---- FIDS-style status strip (signature element) ---- */
        .fids-strip {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(90deg, var(--navy-950) 0%, var(--navy-900) 100%);
            border: 1px solid var(--steel-700);
            border-radius: 10px;
            padding: 10px 20px;
            margin-bottom: 22px;
            box-shadow: 0 6px 18px rgba(7, 15, 26, 0.18);
        }
        .fids-left { display: flex; align-items: center; gap: 10px; }
        .fids-dot {
            width: 9px; height: 9px; border-radius: 50%;
            background: var(--cyan-400);
            box-shadow: 0 0 0 3px rgba(34, 195, 230, 0.18);
            animation: pulse-dot 2s ease-in-out infinite;
        }
        @keyframes pulse-dot { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
        .fids-text {
            color: #DCEAF3;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11.5px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-weight: 500;
        }
        .fids-right {
            color: var(--slate-400);
            font-family: 'JetBrains Mono', monospace;
            font-size: 11.5px;
            letter-spacing: 1px;
        }

        /* ---- Search field ---- */
        div[data-testid="stTextInput"] label {
            color: var(--ink-900) !important;
            font-weight: 600 !important;
            font-size: 12.5px !important;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }
        div[data-testid="stTextInput"] input {
            font-family: 'Inter', sans-serif !important;
            border: 1.5px solid var(--slate-200) !important;
            background-color: #FFFFFF !important;
            color: var(--ink-900) !important;
            border-radius: 9px !important;
            padding: 11px 15px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            box-shadow: 0 1px 2px rgba(11, 18, 32, 0.04) !important;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: var(--steel-600) !important;
            box-shadow: 0 0 0 3px rgba(14, 92, 140, 0.12) !important;
        }

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] {
            background-color: var(--navy-950) !important;
            border-right: 1px solid var(--steel-700);
        }
        div[data-testid="stSidebarUserContent"] p, div[data-testid="stSidebarUserContent"] span,
        div[data-testid="stSidebarUserContent"] h3, div[data-testid="stSidebarUserContent"] label {
            color: #C9D6E3 !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500;
        }
        .sidebar-eyebrow {
            color: var(--cyan-400) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 10.5px !important;
            letter-spacing: 1.6px;
            text-transform: uppercase;
            font-weight: 600 !important;
            margin: 4px 0 2px 0;
        }
        .sidebar-user-card {
            background: var(--navy-900);
            border: 1px solid var(--steel-700);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 18px;
        }
        .sidebar-user-name {
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 14px;
            margin: 0;
        }
        .sidebar-user-role {
            color: var(--slate-400) !important;
            font-size: 11.5px;
            margin: 2px 0 0 0;
        }

        div.stButton > button {
            background-color: var(--steel-600) !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid var(--steel-400) !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            padding: 10px !important;
            letter-spacing: 0.2px;
            transition: all 0.15s ease;
        }
        div.stButton > button:hover {
            background-color: var(--steel-700) !important;
            box-shadow: 0 4px 14px rgba(34, 195, 230, 0.22);
            border-color: var(--cyan-400) !important;
        }
        .sheets-btn {
            display: block;
            text-align: center;
            background-color: #0F7A47 !important;
            color: #FFFFFF !important;
            padding: 11px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 12.5px;
            text-decoration: none;
            margin-top: 8px;
            margin-bottom: 22px;
            border: 1px solid #1CA25E;
            letter-spacing: 0.2px;
            transition: all 0.15s ease;
        }
        .sheets-btn:hover { background-color: #0C6339 !important; }

        /* ---- Login card ---- */
        .login-card {
            background-color: #FFFFFF;
            padding: 42px 40px 36px 40px;
            border-radius: 14px;
            box-shadow: 0 20px 45px rgba(7, 15, 26, 0.10);
            border: 1px solid var(--slate-200);
            border-top: 3px solid var(--steel-600);
        }
        .login-eyebrow {
            color: var(--steel-600);
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            font-size: 10.5px;
            letter-spacing: 2.4px;
            text-transform: uppercase;
            margin: 0 0 6px 0;
        }
        .login-title {
            color: var(--ink-900);
            font-weight: 800;
            font-size: 21px;
            letter-spacing: 0.2px;
            margin: 0 0 26px 0;
        }

        /* ---- KPI blocks ---- */
        .kpi-card {
            background-color: #FFFFFF;
            border: 1px solid var(--slate-200);
            padding: 18px 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(7, 15, 26, 0.04);
            border-left: 3px solid var(--steel-600);
            margin-bottom: 22px;
            transition: box-shadow 0.15s ease;
        }
        .kpi-card:hover { box-shadow: 0 6px 18px rgba(7, 15, 26, 0.08); }
        .kpi-title {
            color: var(--slate-500);
            font-size: 10.5px;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: 1.3px;
            text-transform: uppercase;
        }
        .kpi-number {
            font-family: 'JetBrains Mono', monospace;
            font-size: 27px;
            font-weight: 700;
            color: var(--ink-900);
            margin: 0;
            letter-spacing: -0.5px;
        }
        .kpi-unit {
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 500;
            color: var(--slate-400);
            margin-left: 4px;
        }

        .section-header {
            font-family: 'Montserrat', sans-serif;
            font-size: 13.5px;
            font-weight: 700;
            color: var(--ink-900);
            margin-top: 6px;
            margin-bottom: 14px;
            letter-spacing: 1.1px;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 9px;
        }
        .section-header::before {
            content: "";
            display: inline-block;
            width: 4px;
            height: 16px;
            background: var(--steel-600);
            border-radius: 2px;
        }

        .floating-panel {
            background-color: #FFFFFF;
            border: 1px solid var(--slate-200);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(7, 15, 26, 0.04);
            margin-bottom: 20px;
        }

        /* ---- Status badges ---- */
        @keyframes blinker { 50% { opacity: 0.25; } }
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11.5px;
            font-weight: 700;
            letter-spacing: 0.2px;
        }
        .status-active { color: var(--success); background: var(--success-bg); }
        .status-standby { color: var(--warning); background: var(--warning-bg); }
        .status-offline { color: var(--danger); background: var(--danger-bg); animation: blinker 1.2s linear infinite; }

        /* ---- Table ledger ---- */
        .table-wrapper { width: 100% !important; overflow-x: auto !important; border-radius: 8px; }
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12.5px;
            text-align: left;
            background-color: transparent;
        }
        .styled-table thead tr {
            background-color: var(--navy-950);
            color: #E7EEF5;
        }
        .styled-table th {
            padding: 12px 16px;
            font-weight: 600;
            font-size: 10.5px;
            letter-spacing: 0.8px;
            text-transform: uppercase;
        }
        .styled-table td {
            padding: 11px 16px;
            border-bottom: 1px solid var(--slate-200);
            white-space: nowrap;
            color: var(--ink-900);
        }
        .styled-table tbody tr:nth-of-type(even) { background-color: var(--slate-50); }
        .styled-table tbody tr:hover { background-color: #EAF3F9; }

        /* ---- Live activity feed ---- */
        .activity-item {
            padding: 10px 0;
            border-bottom: 1px solid var(--slate-200);
            font-size: 12.5px;
            color: #334155;
        }
        .activity-item:last-child { border-bottom: none; }
        .activity-time {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            color: var(--steel-600);
            margin-right: 10px;
            font-size: 11px;
        }
    </style>
""", unsafe_allow_html=True)

# LOGIN CONTROLLER
if not st.session_state.logged_in:
    col_space_l, col_login_core, col_space_r = st.columns([1, 1.2, 1])
    with col_login_core:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # LOGO GMF DI HALAMAN LOGIN
        if os.path.exists(LOGO_SOURCE):
            st.image(LOGO_SOURCE, use_container_width=True)

        st.markdown(
            '<div class="login-card">'
            '<p class="login-eyebrow">Tactical Outstation Command</p>'
            '<h3 class="login-title">System Authentication</h3>',
            unsafe_allow_html=True
        )
        input_user = st.text_input("Username", placeholder="Masukkan ID personel Anda...", key="login_user")
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
                st.error("🚨 Username atau password salah.")
        st.markdown("</div>", unsafe_allow_html=True)
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
                    "msg": f"🔄 Status <b>{row.get('Nama_new', 'Personel')}</b> berubah: <span style='color:#B8730F;'>{stat_old}</span> ➡️ <span style='color:#148F5E;'>{stat_new}</span>"
                })

        new_ids = set(df_mentah["ID"]) - set(st.session_state.last_df["ID"])
        for nid in new_ids:
            nama_baru = df_mentah[df_mentah["ID"] == nid]["Nama"].iloc[0]
            st.session_state.activity_logs.insert(0, {
                "time": datetime.now().strftime("%H:%M:%S"),
                "msg": f"➕ Personel baru terdeteksi: <b>{nama_baru}</b>"
            })
    except Exception as e:
        pass

st.session_state.last_df = df_mentah.copy()
st.session_state.activity_logs = st.session_state.activity_logs[:5]

# SIDEBAR CONTROL & LOGO
if os.path.exists(LOGO_SOURCE):
    st.sidebar.image(LOGO_SOURCE, use_container_width=True)

st.sidebar.markdown(
    f'<div class="sidebar-user-card">'
    f'<p class="sidebar-user-name">{st.session_state.username}</p>'
    f'<p class="sidebar-user-role">{st.session_state.role}</p>'
    f'</div>',
    unsafe_allow_html=True
)

st.sidebar.markdown('<p class="sidebar-eyebrow">📊 Input &amp; Update Data</p>', unsafe_allow_html=True)
st.sidebar.markdown(f'<a href="{LINK_EDIT_GOOGLE_SHEETS}" target="_blank" class="sheets-btn">🟢 EDIT LIVE EXCEL SHEET</a>', unsafe_allow_html=True)
st.sidebar.markdown('<p class="sidebar-eyebrow">🎛️ Control Panel</p>', unsafe_allow_html=True)
if st.sidebar.button("🔄 RE-SYNC LIVE DATA", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🔴 SECURE LOGOUT", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# ---- FIDS-STYLE STATUS STRIP (signature element) ----
st.markdown(f"""
    <div class="fids-strip">
        <div class="fids-left">
            <div class="fids-dot"></div>
            <span class="fids-text">GMF Aeroasia · Live Feed Connected</span>
        </div>
        <div class="fids-right">{datetime.now().strftime("%A, %d %B %Y · %H:%M:%S")} WIB</div>
    </div>
""", unsafe_allow_html=True)

# 🏢 MAIN BANNER
st.markdown("""
    <div style="padding-top: 2px;">
        <h2 style="color: #0B1220; font-weight: 900; margin: 0; letter-spacing: 0.3px;">Manpower Allocation Dashboard</h2>
        <p style="color: #0E5C8C; font-size: 13px; font-weight: 600; letter-spacing: 2.5px; margin-top: 6px; text-transform: uppercase; font-family: 'JetBrains Mono', monospace;">Outstation Personnel Monitoring System</p>
    </div>
""", unsafe_allow_html=True)
st.markdown('<hr style="border: none; border-top: 2px solid #E1E8F0; margin-top: 16px; margin-bottom: 26px;">', unsafe_allow_html=True)

# SEARCH CONTAINER
search_query = st.text_input("🔎 Pencarian Berdasarkan Nama / Kualifikasi / Stasiun Hub:", placeholder="Ketik nama personel atau kode stasiun di sini...")

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

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="kpi-card" style="border-left-color:#0E5C8C;"><div class="kpi-title">📁 Total Fleet Manpower</div><div class="kpi-number">{total_personel}<span class="kpi-unit">personel</span></div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card" style="border-left-color:#148F5E;"><div class="kpi-title" style="color:#148F5E;">🟢 Active On Duty</div><div class="kpi-number">{personel_aktif}<span class="kpi-unit">personel</span></div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card" style="border-left-color:#B8730F;"><div class="kpi-title" style="color:#B8730F;">🟡 Standby Alert</div><div class="kpi-number">{personel_standby}<span class="kpi-unit">personel</span></div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card" style="border-left-color:#22C3E6;"><div class="kpi-title" style="color:#0E5C8C;">🔵 CGK Ready Resource</div><div class="kpi-number">{jumlah_di_cgk}<span class="kpi-unit">personel</span></div></div>', unsafe_allow_html=True)

# ROW ATAS: MAP DISTRIBUSI VS LIVE TELEMETRY LOGS
col_left, col_right = st.columns([55, 45])

with col_left:
    st.markdown("<div class='section-header'>Live Tactical Spatial Distribution</div>", unsafe_allow_html=True)
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
                    <tr style='background-color:#F5F8FB; text-align:left;'>
                        <th style='padding:4px;'>Nama</th>
                        <th style='padding:4px;'>Status</th>
                    </tr>
            """
            for _, row in sub_df.iterrows():
                sv = str(row['Status']).strip()
                s_html = f"<span style='color:#148F5E;font-weight:700;'>🟢 Active</span>" if sv.lower() == 'active' else (f"<span style='color:#B8730F;font-weight:700;'>🟡 Standby</span>" if sv.lower() == 'standby' else f"<span style='color:#C5303A;font-weight:800;animation:blinker 1s linear infinite;'>🔴 {sv}</span>")
                popup_html += f"<tr><td style='padding:4px; border-bottom:1px solid #E1E8F0;'>{row['Nama']}</td><td style='padding:4px; border-bottom:1px solid #E1E8F0;'>{s_html}</td></tr>"
            popup_html += "</table></div>"

            folium.Marker(location=koordinat, popup=folium.Popup(popup_html, max_width=350), icon=folium.Icon(color=warna_pin)).add_to(m)

    st_folium(m, width="100%", height=380)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='section-header'>Operational Telemetry &amp; Logs</div>", unsafe_allow_html=True)

    pop_col1, pop_col2 = st.columns(2)
    with pop_col1:
        with st.popover("⚙️ Status Telemetry Chart", use_container_width=True):
            if not df_pekerja.empty: st.bar_chart(df_pekerja['Status'].value_counts(), color="#0E5C8C", height=150)
    with pop_col2:
        with st.popover("✈️ Core Fleet Capabilities", use_container_width=True):
            if not df_pekerja.empty: st.bar_chart(df_pekerja['Kualifikasi'].value_counts().head(5), color="#22C3E6", height=150)

    st.markdown('<div class="floating-panel" style="margin-top: 10px;">', unsafe_allow_html=True)
    utilization_rate = int((personel_aktif / total_personel) * 100) if total_personel > 0 else 0
    st.markdown(f"""
        <div style="margin-bottom: 6px; font-size: 12.5px; font-weight: 600; color: #334155;">Active Deployment Load <span class="mono" style="color:#0E5C8C;">({utilization_rate}%)</span></div>
        <div style="width: 100%; background-color: #E1E8F0; border-radius: 8px; height: 8px; margin-bottom: 18px;">
            <div style="width: {utilization_rate}%; background: linear-gradient(90deg, #0E5C8C, #22C3E6); border-radius: 8px; height: 8px;"></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='color:#0B1220; font-size:12.5px; font-weight:700; margin:8px 0 8px 0; text-transform:uppercase; letter-spacing:0.6px; font-family:\"Montserrat\",sans-serif;'>📡 Live Activity Feed</h4>", unsafe_allow_html=True)
    logs_html = ""
    for log in st.session_state.activity_logs:
        logs_html += f'<div class="activity-item"><span class="activity-time">[{log["time"]}]</span> {log["msg"]}</div>'
    st.markdown(logs_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 🚨 ROW BAWAH (ISOLASI PARALEL): FULL-WIDTH ANTI TABRAKAN
st.markdown("<div class='section-header'>Personnel Directory Master Ledger</div>", unsafe_allow_html=True)
st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)

def render_status(status):
    v = str(status).strip()
    if v.lower() == 'active': return '<span class="status-pill status-active">🟢 Active</span>'
    elif v.lower() == 'standby': return '<span class="status-pill status-standby">🟡 Standby</span>'
    else: return f'<span class="status-pill status-offline">🔴 {v}</span>'

df_html = df_pekerja.copy()
df_html['Status'] = df_html['Status'].apply(render_status)
st.markdown(df_html.to_html(escape=False, index=False, classes="styled-table"), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
