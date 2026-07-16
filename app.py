import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import ssl
import time
from datetime import datetime

# Bypass verifikasi SSL Certificate pada macOS
ssl._create_default_https_context = ssl._create_unverified_context

# 1. KONFIGURASI HALAMAN UTAMA
st.set_page_config(
    page_title="GMF AeroAsia - Manpower Allocation",
    page_icon="✈️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔑 INITIALIZE SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
# 🧠 MEMORY UNTUK TRACKING LIVE DATA
if "last_df" not in st.session_state:
    st.session_state.last_df = None
if "activity_logs" not in st.session_state:
    st.session_state.activity_logs = [
        {"time": datetime.now().strftime("%H:%M:%S"), "msg": "Sistem diinisialisasi. Memantau data live..."}
    ]

# 🎯 DATABASE USER
USER_DATABASE = {
    "dhioakbar0304": {"password": "gmfsecure01", "role": "PPC Planning & Control"},
    "supervisor_gmf": {"password": "gmfsecure02", "role": "Maintenance Supervisor"}
}

# 🎨 CSS KUSTOM: TERMASUK ANIMASI BLINKING & STYLING CUSTOM TABLE
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif !important;
        }

        .stApp {
            background-image: linear-gradient(rgba(240, 244, 248, 0.93), rgba(240, 244, 248, 0.93)), 
                              url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* SIDEBAR & BANNERS (Disembunyikan panjangnya agar hemat baris, sama persis seperti sebelumnya) */
        section[data-testid="stSidebar"] { background-color: #041226 !important; border-right: 2px solid #005C97; }
        div[data-testid="stSidebarUserContent"] p, div[data-testid="stSidebarUserContent"] span, 
        div[data-testid="stSidebarUserContent"] h3, div[data-testid="stSidebarUserContent"] label {
            color: #FFFFFF !important; font-family: 'Montserrat', sans-serif !important; font-weight: 500;
        }
        div.stButton > button { background-color: #005C97 !important; color: #FFFFFF !important; border-radius: 8px !important; border: 1px solid #00C9FF !important; font-weight: 700 !important; padding: 10px !important; }
        div.stButton > button:hover { background-color: #003F6B !important; box-shadow: 0px 4px 15px rgba(0, 201, 255, 0.4); }
        .sheets-btn { display: block; text-align: center; background-color: #107C41 !important; color: #FFFFFF !important; padding: 12px; border-radius: 8px; font-weight: 700; font-size: 13px; text-decoration: none; margin-top: 10px; margin-bottom: 20px; border: 1px solid #10B981; }
        .gmf-banner { background: linear-gradient(135deg, #041226 0%, #002D54 100%); padding: 35px 20px; border-radius: 14px; color: #FFFFFF !important; text-align: center; margin-bottom: 30px; border-bottom: 5px solid #00C9FF; box-shadow: 0 10px 30px rgba(3, 18, 38, 0.25); }
        .gmf-banner h1 { font-size: 42px !important; font-weight: 900 !important; letter-spacing: 2px; margin: 0 !important; }
        .gmf-banner p { color: #00C9FF !important; font-size: 13px !important; font-weight: 700; letter-spacing: 5px; margin-top: 10px !important; text-transform: uppercase; }
        
        .login-card { background-color: rgba(255, 255, 255, 0.85); backdrop-filter: blur(15px); padding: 40px; border-radius: 16px; box-shadow: 0 15px 35px rgba(4, 18, 38, 0.15); border: 1px solid rgba(255, 255, 255, 0.6); border-top: 5px solid #005C97; }
        .kpi-card { background-color: rgba(255, 255, 255, 0.92); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.5); padding: 20px; border-radius: 12px; box-shadow: 0 8px 24px 0 rgba(3, 18, 38, 0.05); border-top: 5px solid #005C97; }
        .kpi-title { color: #556980; font-size: 11px; font-weight: 800; margin-bottom: 6px; letter-spacing: 1.2px; text-transform: uppercase; }
        .kpi-number { font-size: 34px; font-weight: 900; color: #041226; margin: 0; }
        .section-header { font-size: 18px; font-weight: 800; color: #041226; margin-top: 30px; margin-bottom: 15px; border-left: 5px solid #005C97; padding-left: 12px; text-transform: uppercase; }
        .floating-panel { background-color: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.6); border-radius: 12px; padding: 20px; box-shadow: 0 8px 24px 0 rgba(3, 18, 38, 0.05); margin-bottom: 20px; }

        /* 🔥 CSS UNTUK STATUS WARNA & KEDAP-KEDIP */
        @keyframes blinker {
            50% { opacity: 0; }
        }
        .status-active { color: #10B981; font-weight: 800; }
        .status-standby { color: #F59E0B; font-weight: 800; }
        .status-offline { color: #EF4444; font-weight: 900; animation: blinker 1s linear infinite; }
        
        /* CSS UNTUK CUSTOM HTML TABLE (Pengganti st.dataframe) */
        .styled-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; background-color: transparent; }
        .styled-table thead tr { background-color: #041226; color: #ffffff; }
        .styled-table th, .styled-table td { padding: 12px 15px; border-bottom: 1px solid #E2E8F0; }
        .styled-table tbody tr:nth-of-type(even) { background-color: #F8FAFC; }

        /* Activity Feed Item */
        .activity-item { padding: 10px 0; border-bottom: 1px solid #E2E8F0; font-size: 12px; color: #334155; }
        .activity-time { font-weight: 800; color: #005C97; margin-right: 10px; }
        
        /* Animasi Popover iOS */
        div[data-testid="stPopoverBody"] { animation: appleSpringScale 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.15) forwards !important; }
        @keyframes appleSpringScale { 0% { opacity: 0; transform: scale(0.9) translateY(-4px); } 100% { opacity: 1; transform: scale(1) translateY(0); } }
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# 🔑 LOGIN PAGE CONTROLLER
# =====================================================================
if not st.session_state.logged_in:
    col_space_l, col_login_core, col_space_r = st.columns([1, 1.2, 1])
    with col_login_core:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<div class="login-card"><div style="text-align: center; margin-bottom: 25px;"><h2 style="color: #041226; font-weight: 900; letter-spacing: 1px; font-size: 26px; margin:0;">TACTICAL COMMAND</h2><p style="color: #005C97; font-weight: bold; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; margin-top:5px;">GMF AeroAsia - Outstation Division</p></div>', unsafe_allow_html=True)
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


# =====================================================================
# 💻 MAIN DASHBOARD APP
# =====================================================================

DOKUMEN_KOORDINAT = {
    "CGK": [-6.1256, 106.6559], "KNO": [3.6422, 98.8853],
    "DPS": [-8.7481, 115.1674], "SUB": [-7.3798, 112.7873],
    "UPG": [-5.0616, 119.5523], "DJJ": [-2.5783, 140.5167],
    "BTH": [1.1211, 104.1182], "BPN": [-1.2683, 116.8944]
}

LINK_EDIT_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/edit"
LINK_EXPORT_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/export?format=csv&gid=827445294"

@st.cache_data(ttl=60)
def load_live_google_sheets():
    try:
        df = pd.read_csv(LINK_EXPORT_GOOGLE_SHEETS)
        return df
    except Exception as e:
        # Fallback dummy jika link gagal
        return pd.DataFrame([
            {"ID": 551001, "Nama": "Ahmad", "Kualifikasi": "B737 Engine Expert", "Lokasi": "DPS", "Status": "Active", "PPC Pengirim": "Offline Backup"},
            {"ID": 551002, "Nama": "Budi", "Kualifikasi": "A320 Avionic", "Lokasi": "CGK", "Status": "Offline", "PPC Pengirim": "Offline Backup"}
        ])

df_mentah = load_live_google_sheets()

# -------------------------------------------------------------
# 🤖 LOGIC TRACKING DATA AKTUAL UNTUK ACTIVITY FEED
# -------------------------------------------------------------
if st.session_state.last_df is not None:
    try:
        # Bandingkan data lama vs data baru menggunakan kolom 'ID' (asumsi kolom ID unik)
        merged = st.session_state.last_df.merge(df_mentah, on="ID", suffixes=('_old', '_new'))
        for _, row in merged.iterrows():
            stat_old = str(row.get('Status_old', '')).strip().lower()
            stat_new = str(row.get('Status_new', '')).strip().lower()
            
            if stat_old != stat_new:
                st.session_state.activity_logs.insert(0, {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "msg": f"🔄 Status <b>{row.get('Nama_new', 'Personel')}</b> berubah: {stat_old.title()} ➡️ {stat_new.title()}"
                })
        
        # Cek orang baru (ID ada di df baru tapi gak ada di df lama)
        new_ids = set(df_mentah["ID"]) - set(st.session_state.last_df["ID"])
        for nid in new_ids:
            nama_baru = df_mentah[df_mentah["ID"] == nid]["Nama"].iloc[0]
            st.session_state.activity_logs.insert(0, {
                "time": datetime.now().strftime("%H:%M:%S"),
                "msg": f"➕ Personel baru masuk radar: <b>{nama_baru}</b>"
            })
            
    except Exception as e:
        pass # Lewati jika skema kolom berubah/ID tidak ada

# Simpan state dataframe terbaru untuk di-compare di refresh berikutnya
st.session_state.last_df = df_mentah.copy()
# Batasi log maksimal 6 item agar tidak kepanjangan
st.session_state.activity_logs = st.session_state.activity_logs[:6]

# -------------------------------------------------------------

# 2. PANEL SIDEBAR KIRI
st.sidebar.markdown("### 📊 INPUT & UPDATE DATA")
st.sidebar.markdown(f'<a href="{LINK_EDIT_GOOGLE_SHEETS}" target="_blank" class="sheets-btn">🟢 EDIT LIVE EXCEL SHEET</a>', unsafe_allow_html=True)

st.sidebar.markdown("### 🎛️ CONTROL PANEL")
if st.sidebar.button("🔄 RE-SYNC LIVE DATA", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(f"""<div style="line-height: 2.0; font-size: 13px; margin-bottom: 20px;"><p style="margin: 0;">👤 <b>User Authorized:</b><br><span style="color: #00C9FF !important; font-weight: bold; font-size:14px;">{st.session_state.username}</span></p></div>""", unsafe_allow_html=True)
if st.sidebar.button("🔴 SECURE LOGOUT", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# BANNER HEAD
st.markdown('<div class="gmf-banner"><h1>GMF AEROASIA</h1><p>Tactical Outstation Manpower Command Center</p></div>', unsafe_allow_html=True)

# SEARCH ENGINE
search_query = st.text_input("🔎 Pencarian Personel/Kualifikasi:", "")
if search_query:
    df_pekerja = df_mentah[
        df_mentah['Nama'].astype(str).str.contains(search_query, case=False, na=False) |
        df_mentah['Kualifikasi'].astype(str).str.contains(search_query, case=False, na=False) |
        df_mentah['Lokasi'].astype(str).str.contains(search_query, case=False, na=False)
    ]
else:
    df_pekerja = df_mentah

# KPI CARDS
total_personel = len(df_pekerja)
personel_aktif = len(df_pekerja[df_pekerja['Status'].astype(str).str.strip().str.lower() == 'active'])
personel_standby = len(df_pekerja[df_pekerja['Status'].astype(str).str.strip().str.lower() == 'standby'])
jumlah_di_cgk = len(df_pekerja[df_pekerja['Lokasi'].astype(str).str.strip() == 'CGK'])

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="kpi-card"><div class="kpi-title">📁 Total Fleet Manpower</div><div class="kpi-number">{total_personel} Px</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card" style="border-top-color: #10B981;"><div class="kpi-title" style="color:#10B981;">🟢 Active On Duty</div><div class="kpi-number">{personel_aktif} Px</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card" style="border-top-color: #F59E0B;"><div class="kpi-title" style="color:#F59E0B;">🟡 Standby Alert</div><div class="kpi-number">{personel_standby} Px</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card" style="border-top-color: #3B82F6;"><div class="kpi-title" style="color:#3B82F6;">🔵 CGK Ready Resource</div><div class="kpi-number">{jumlah_di_cgk} Px</div></div>', unsafe_allow_html=True)

# 6. LAYOUT UTAMA (Menyeimbangkan ruang kosong Kiri vs Kanan)
col_left, col_right = st.columns([5, 4])

with col_left:
    st.markdown("<div class='section-header'>🗺️ Live Tactical Spatial Distribution</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    
    m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles="OpenStreetMap")
    
    for lok, koordinat in DOKUMEN_KOORDINAT.items():
        sub_df = df_pekerja[df_pekerja['Lokasi'].astype(str).str.strip() == lok]
        if not sub_df.empty:
            total_di_lokasi = len(sub_df)
            # Menentukan warna pin (Hijau jika ada yg active, Kuning jika standby, Red jika full offline)
            statuses = [str(x).lower().strip() for x in sub_df['Status'].tolist()]
            if 'active' in statuses:
                warna_pin = "green"
            elif 'standby' in statuses:
                warna_pin = "orange" # folium tidak punya warna "yellow" murni untuk icon default
            else:
                warna_pin = "red"
            
            popup_html = f"""
            <div style='font-family: "Montserrat", sans-serif; color: #1e293b; min-width:260px;'>
                <h4 style='margin:0 0 5px 0; color:#1e3a8a; font-weight:800;'>Station Hub: {lok}</h4>
                <table style='width:100%; font-size:11px; border-collapse: collapse;'>
                    <tr style='background-color:#f1f5f9; text-align:left;'>
                        <th style='padding:4px; font-weight:700;'>Nama</th>
                        <th style='padding:4px; font-weight:700;'>Status</th>
                    </tr>
            """
            for _, row in sub_df.iterrows():
                # Format warna status di dalam Map Popup
                stat_val = str(row['Status']).strip()
                if stat_val.lower() == 'active':
                    stat_html = f"<span style='color: #10B981; font-weight: bold;'>🟢 Active</span>"
                elif stat_val.lower() == 'standby':
                    stat_html = f"<span style='color: #F59E0B; font-weight: bold;'>🟡 Standby</span>"
                else:
                    # Injeksi animasi blink langsung di tag style inline (jaga-jaga kelas css di isolasi Folium)
                    stat_html = f"<span style='color: #EF4444; font-weight: 800; animation: blinker 1s linear infinite;'>🔴 {stat_val}</span>"
                
                popup_html += f"<tr><td style='padding:4px; border-bottom:1px solid #e2e8f0;'>{row['Nama']}</td><td style='padding:4px; border-bottom:1px solid #e2e8f0;'>{stat_html}</td></tr>"
            popup_html += "</table></div>"
            
            folium.Marker(
                location=koordinat,
                popup=folium.Popup(popup_html, max_width=400),
                tooltip=f"Hub {lok}: {total_di_lokasi} Personnel",
                icon=folium.Icon(color=warna_pin, icon="info-sign")
            ).add_to(m)
            
    st_folium(m, width="100%", height=450)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div class='section-header'>📋 Personnel Directory Ledger</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel" style="overflow-x: auto;">', unsafe_allow_html=True)
    
    # 🌟 RENDER TABEL HTML CUSTOM UNTUK MENDUKUNG ANIMASI BLINKING RED! 🌟
    def style_status_html(status):
        val = str(status).strip()
        val_low = val.lower()
        if val_low == 'active':
            return '<span class="status-active">🟢 Active</span>'
        elif val_low == 'standby':
            return '<span class="status-standby">🟡 Standby</span>'
        else:
            return f'<span class="status-offline">🔴 {val}</span>'

    df_html_tampil = df_pekerja.copy()
    df_html_tampil['Status'] = df_html_tampil['Status'].apply(style_status_html)
    
    # Konversi DataFrame ke String HTML (Escape=False agar tag <span> terbaca sbg HTML, bukan teks biasa)
    html_table = df_html_tampil.to_html(escape=False, index=False, classes="styled-table")
    st.markdown(html_table, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='section-header'>📊 Advanced Analytics & Operations</div>", unsafe_allow_html=True)
    
    pop_col1, pop_col2 = st.columns(2)
    with pop_col1:
        with st.popover("⚙️ Status Telemetry Map", use_container_width=True):
            st.markdown("<h4 style='color:#041226; font-size:14px; font-weight:800; margin:0;'>📊 Duty Distribution</h4>", unsafe_allow_html=True)
            if not df_pekerja.empty:
                st.bar_chart(df_pekerja['Status'].value_counts(), color="#107C41", height=200)
                
    with pop_col2:
        with st.popover("✈️ Inspect Capabilities", use_container_width=True):
            st.markdown("<h4 style='color:#041226; font-size:14px; font-weight:800; margin:0;'>🚀 Fleet Skillset</h4>", unsafe_allow_html=True)
            if not df_pekerja.empty:
                st.bar_chart(df_pekerja['Kualifikasi'].value_counts().head(5), color="#F59E0B", height=200)

    st.markdown('<div class="floating-panel" style="margin-top: 15px;">', unsafe_allow_html=True)
    st.markdown("<h4 style='color:#041226; font-size:14px; font-weight:800; margin:0 0 15px 0;'>📈 Hub Resource Strength Breakdown</h4>", unsafe_allow_html=True)
    if not df_pekerja.empty:
        st.bar_chart(df_pekerja['Lokasi'].value_counts(), color="#005C97", height=250)
    st.markdown('</div>', unsafe_allow_html=True)

    # ACTUAL LIVE ACTIVITY TRACKING!
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    st.markdown("<h4 style='color:#041226; font-size:14px; font-weight:800; margin:0 0 15px 0;'>⚡ Network Resource Utilization</h4>", unsafe_allow_html=True)
    
    utilization_rate = int((personel_aktif / total_personel) * 100) if total_personel > 0 else 0
    st.markdown(f"""
        <div style="margin-bottom: 5px; font-size: 13px; font-weight: 600; color: #334155;">Active Deployment Load ({utilization_rate}%)</div>
        <div style="width: 100%; background-color: #E2E8F0; border-radius: 8px; height: 12px; margin-bottom: 20px;">
            <div style="width: {utilization_rate}%; background-color: #10B981; border-radius: 8px; height: 12px;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h4 style='color:#041226; font-size:14px; font-weight:800; margin:20px 0 10px 0;'>📡 Live Activity Feed (Real-Time Diff)</h4>", unsafe_allow_html=True)
    
    # Looping list log aktual dari state
    logs_html = ""
    for log in st.session_state.activity_logs:
        logs_html += f'<div class="activity-item"><span class="activity-time">{log["time"]}</span> {log["msg"]}</div>'
        
    st.markdown(logs_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
