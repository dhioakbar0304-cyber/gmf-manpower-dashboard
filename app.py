import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import ssl

# Bypass verifikasi SSL Certificate pada macOS
ssl._create_default_https_context = ssl._create_unverified_context

# 1. KONFIGURASI HALAMAN UTAMA (Aviation & Corporate Standard)
st.set_page_config(
    page_title="GMF AeroAsia - Manpower Allocation Dashboard",
    page_icon="https://www.garuda-indonesia.com/favicon.ico", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔑 INITIALIZE SESSION STATE UNTUK LOGIN
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# 🎯 DATABASE USER
USER_DATABASE = {
    "dhioakbar0304": {"password": "gmfsecure01", "role": "PPC Planning & Control"},
    "supervisor_gmf": {"password": "gmfsecure02", "role": "Maintenance Supervisor"}
}

# 🎨 CSS KUSTOM: RESOLUSI FIX POSISI POPOVER & INTEGRITAS STRAAMUT ANIMATION
st.markdown("""
    <style>
        /* Import Font Montserrat */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif !important;
        }

        /* BACKGROUND UTAMA */
        .stApp {
            background-image: linear-gradient(rgba(240, 244, 248, 0.93), rgba(240, 244, 248, 0.93)), 
                              url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* SIDEBAR DECORATION */
        section[data-testid="stSidebar"] {
            background-color: #041226 !important; 
            border-right: 2px solid #005C97;
        }
        
        div[data-testid="stSidebarUserContent"] p,
        div[data-testid="stSidebarUserContent"] span,
        div[data-testid="stSidebarUserContent"] h3,
        div[data-testid="stSidebarUserContent"] label {
            font-family: 'Montserrat', sans-serif !important;
            color: #FFFFFF !important;
            font-weight: 500;
        }
        
        div[data-testid="stSidebarUserContent"] code {
            background-color: transparent !important;
            color: #38BDF8 !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            padding: 0px !important;
        }
        
        div.stButton > button {
            background-color: #005C97 !important;
            color: #FFFFFF !important;
            font-family: 'Montserrat', sans-serif !important;
            border-radius: 8px !important;
            border: 1px solid #00C9FF !important;
            font-weight: 700 !important;
            padding: 10px !important;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            background-color: #003F6B !important;
            box-shadow: 0px 4px 15px rgba(0, 201, 255, 0.4);
        }
        
        .sheets-btn {
            display: block;
            text-align: center;
            background-color: #107C41 !important;
            color: #FFFFFF !important;
            padding: 12px;
            font-family: 'Montserrat', sans-serif !important;
            border-radius: 8px;
            font-weight: 700;
            font-size: 13px;
            text-decoration: none;
            margin-top: 10px;
            margin-bottom: 20px;
            border: 1px solid #10B981;
            transition: all 0.3s ease;
            box-shadow: 0px 4px 10px rgba(16, 124, 65, 0.2);
        }
        .sheets-btn:hover {
            background-color: #0A5C30 !important;
            color: #FFFFFF !important;
            text-decoration: none;
        }
        
        .gmf-banner {
            background: linear-gradient(135deg, #041226 0%, #002D54 100%);
            padding: 35px 20px;
            border-radius: 14px;
            color: #FFFFFF !important;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 5px solid #00C9FF;
            box-shadow: 0 10px 30px rgba(3, 18, 38, 0.25);
        }
        
        .gmf-banner h1 {
            color: #FFFFFF !important;
            font-size: 42px !important;
            font-weight: 900 !important;
            letter-spacing: 2px;
            margin: 0 !important;
        }
        
        .gmf-banner p {
            color: #00C9FF !important;
            font-size: 13px !important;
            font-weight: 700;
            letter-spacing: 5px;
            margin-top: 10px !important;
            text-transform: uppercase;
        }

        div[data-testid="stTextInput"] input {
            font-family: 'Montserrat', sans-serif !important;
            border-radius: 8px !important;
            border: 2px solid #041226 !important;
            padding: 12px !important;
            font-size: 15px !important;
            color: #041226 !important;
            background-color: rgba(255, 255, 255, 0.95) !important;
            font-weight: 600 !important;
        }

        .kpi-card {
            background-color: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 24px 0 rgba(3, 18, 38, 0.05);
            border-top: 5px solid #005C97;
            transition: transform 0.2s;
        }
        
        .kpi-title {
            color: #556980;
            font-size: 11px;
            font-weight: 800;
            margin-bottom: 6px;
            letter-spacing: 1.2px;
            text-transform: uppercase;
        }
        
        .kpi-number {
            font-size: 34px;
            font-weight: 900;
            color: #041226;
            margin: 0;
        }

        .section-header {
            font-size: 18px;
            font-weight: 800;
            color: #041226;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 5px solid #005C97;
            padding-left: 12px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        
        .floating-panel {
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.6);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 24px 0 rgba(3, 18, 38, 0.05);
            margin-bottom: 20px;
        }

        /* =====================================================================
           🍏 PERBAIKAN TOTAL: TOMBOL POPOVER & EFEK TRANSISI APPLE SPRING
           ===================================================================== */
        
        /* Tombol Pemicu Popover */
        div[data-testid="stPopover"] > button {
            background-color: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(8px) !important;
            color: #041226 !important;
            border: 1px solid rgba(0, 92, 151, 0.3) !important;
            font-weight: 700 !important;
            border-radius: 12px !important;
            padding: 12px 20px !important;
            transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }
        
        div[data-testid="stPopover"] > button:hover {
            background-color: #FFFFFF !important;
            border-color: #005C97 !important;
            transform: scale(1.02);
        }

        /* 🚨 FIX UTAMA: Mencegah Popover loncat ke kiri atas dengan tetap menjaga anchor relatif stPopover */
        div[data-testid="stPopoverBody"] {
            background-color: rgba(255, 255, 255, 0.94) !important;
            backdrop-filter: blur(25px) !important;
            border-radius: 18px !important;
            border: 1px solid rgba(255, 255, 255, 0.6) !important;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12) !important;
            padding: 20px !important;
            
            /* Animasi iOS Spring Terlokalisasi */
            animation: appleSpringScale 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.15) forwards !important;
            transform-origin: top center !important;
        }

        /* Keyframe Khusus Animasi Pegas tanpa mengubah posisi koordinat absolut (Khas iOS) */
        @keyframes appleSpringScale {
            0% {
                opacity: 0;
                transform: scale(0.9) translateY(-4px);
            }
            100% {
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# 🔑 LOGIN PAGE CONTROLLER
# =====================================================================
if not st.session_state.logged_in:
    col_space_l, col_login_core, col_space_r = st.columns([1, 1.2, 1])
    
    with col_login_core:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #041226; font-weight: 900; letter-spacing: 1px; font-size: 26px; margin:0;">
                    TACTICAL COMMAND PORTAL
                </h2>
                <p style="color: #005C97; font-weight: bold; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; margin-top:5px;">
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

def load_live_google_sheets():
    try:
        return pd.read_csv(LINK_EXPORT_GOOGLE_SHEETS)
    except Exception as e:
        return pd.DataFrame([{"ID": 551001, "Nama": "Ahmad", "Kualifikasi": "B737 Engine Expert", "Lokasi": "DPS", "Status": "Active", "PPC Pengirim": "Offline Backup"}])

df_mentah = load_live_google_sheets()

# 2. PANEL SIDEBAR KIRI
st.sidebar.markdown("<br>", unsafe_allow_html=True)
try:
    st.sidebar.image("gmf aeroasia logo new blue.png", use_container_width=True)
except:
    pass

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 INPUT & UPDATE DATA")
st.sidebar.markdown(f'<a href="{LINK_EDIT_GOOGLE_SHEETS}" target="_blank" class="sheets-btn">🟢 EDIT LIVE EXCEL SHEET</a>', unsafe_allow_html=True)

st.sidebar.markdown("### 🎛️ CONTROL PANEL")
if st.sidebar.button("🔄 RE-SYNC LIVE DATA", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 MONITOR PROFILE")
st.sidebar.markdown(f"""
<div style="line-height: 2.0; font-size: 13px;">
    <p style="margin: 0;">👤 <b>User Authorized:</b><br><span style="color: #00C9FF !important; font-weight: bold; font-size:14px;">{st.session_state.username}</span></p><br>
    <p style="margin: 0;">💼 <b>Role Account:</b><br><span style="color: #00C9FF !important; font-weight: bold; font-size:14px;">{st.session_state.role}</span></p>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🔴 SECURE LOGOUT", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# BANNER HEAD
st.markdown('<div class="gmf-banner"><h1>GMF AEROASIA</h1><p>Tactical Outstation Manpower Command Center</p></div>', unsafe_allow_html=True)

# SEARCH ENGINE
st.markdown("<div class='section-header'>🔎 Tactical Resource Search Engine</div>", unsafe_allow_html=True)
search_query = st.text_input("Ketik di bawah ini untuk mencari personel atau kualifikasi:", "")

if search_query:
    df_pekerja = df_mentah[
        df_mentah['Nama'].str.contains(search_query, case=False, na=False) |
        df_mentah['Kualifikasi'].str.contains(search_query, case=False, na=False) |
        df_mentah['Lokasi'].str.contains(search_query, case=False, na=False)
    ]
else:
    df_pekerja = df_mentah

# KPI CARDS
total_personel = len(df_pekerja)
personel_aktif = len(df_pekerja[df_pekerja['Status'].str.strip() == 'Active'])
personel_standby = len(df_pekerja[df_pekerja['Status'].str.strip() == 'Standby'])
jumlah_di_cgk = len(df_pekerja[df_pekerja['Lokasi'].str.strip() == 'CGK'])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">📁 Total Fleet Manpower</div><div class="kpi-number">{total_personel} Px</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card" style="border-top-color: #10B981;"><div class="kpi-title" style="color:#10B981;">🟢 Active On Duty</div><div class="kpi-number">{personel_aktif} Px</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card" style="border-top-color: #F59E0B;"><div class="kpi-title" style="color:#F59E0B;">🟡 Standby Alert</div><div class="kpi-number">{personel_standby} Px</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-card" style="border-top-color: #3B82F6;"><div class="kpi-title" style="color:#3B82F6;">🔵 CGK Ready Resource</div><div class="kpi-number">{jumlah_di_cgk} Px</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. LAYOUT UTAMA MALAM
col_left, col_right = st.columns([4, 3])

with col_left:
    st.markdown("<div class='section-header'>🗺️ Live Tactical Spatial Distribution</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    
    # Inisialisasi Peta Utama
    m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles="OpenStreetMap")
    
    # 🚨 PENGEMBALIAN FITUR MARKER PER MANPOWER SECARA UTUH
    for lok, koordinat in DOKUMEN_KOORDINAT.items():
        sub_df = df_pekerja[df_pekerja['Lokasi'].str.strip() == lok]
        if not sub_df.empty:
            total_di_lokasi = len(sub_df)
            warna_pin = "red" if lok == "CGK" else ("green" if any(sub_df['Status'].str.strip() == 'Active') else "orange")
            
            # Membuat struktur balon tabel informasi per personel yang bertugas di bandara tersebut
            popup_html = f"""
            <div style='font-family: "Montserrat", sans-serif; color: #1e293b; min-width:240px;'>
                <h4 style='margin:0 0 5px 0; color:#1e3a8a; font-weight:800;'>Station Hub: {lok}</h4>
                <p style='margin:0 0 8px 0; font-size:12px;'>Total Resource: <b>{total_di_lokasi} Personel</b></p>
                <table style='width:100%; font-size:11px; border-collapse: collapse;'>
                    <tr style='background-color:#f1f5f9; text-align:left;'>
                        <th style='padding:4px; font-weight:700;'>Nama</th>
                        <th style='padding:4px; font-weight:700;'>Kualifikasi</th>
                    </tr>
            """
            for _, row in sub_df.iterrows():
                popup_html += f"""
                <tr>
                    <td style='padding:4px; border-bottom:1px solid #e2e8f0;'>{row['Nama']}</td>
                    <td style='padding:4px; border-bottom:1px solid #e2e8f0;'>{row['Kualifikasi']}</td>
                </tr>
                """
            popup_html += "</table></div>"
            
            folium.Marker(
                location=koordinat,
                popup=folium.Popup(popup_html, max_width=380),
                tooltip=f"Hub {lok}: {total_di_lokasi} Personnel",
                icon=folium.Icon(color=warna_pin, icon="info-sign")
            ).add_to(m)
            
    st_folium(m, width="100%", height=520)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div class='section-header'>📋 Personnel Directory Ledger</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    st.dataframe(df_pekerja, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='section-header'>📊 Advanced Manpower Analytics</div>", unsafe_allow_html=True)
    
    pop_col1, pop_col2 = st.columns(2)
    
    with pop_col1:
        # 🍏 Popover 1: Duduk Presisi dengan Efek Spring Pegas iOS Kustom
        with st.popover("⚙️ Open Status Telemetry Map", use_container_width=True):
            st.markdown("<h4 style='color:#041226; font-size:14px; font-weight:800; margin:0;'>📊 Duty Distribution Status</h4>", unsafe_allow_html=True)
            st.write("Analitik pembagian waktu siaga personil stasiun luar.")
            if not df_pekerja.empty:
                st.bar_chart(df_pekerja['Status'].value_counts(), color="#107C41", height=200)
                
    with pop_col2:
        # 🍏 Popover 2: Duduk Presisi dengan Efek Spring Pegas iOS Kustom
        with st.popover("✈️ Inspect Fleet Capabilities", use_container_width=True):
            st.markdown("<h4 style='color:#041226; font-size:14px; font-weight:800; margin:0;'>🚀 Fleet Skillset Capability</h4>", unsafe_allow_html=True)
            st.write("Kuantitas keahlian tipe pesawat yang bersertifikasi.")
            if not df_pekerja.empty:
                st.bar_chart(df_pekerja['Kualifikasi'].value_counts().head(5), color="#F59E0B", height=200)
                
    st.markdown("<div class='section-header'>📈 Hub Resource Strength Breakdown</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    if not df_pekerja.empty:
        st.bar_chart(df_pekerja['Lokasi'].value_counts(), color="#005C97", height=280)
    st.markdown('</div>', unsafe_allow_html=True)
