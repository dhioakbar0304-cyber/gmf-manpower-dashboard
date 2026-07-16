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

# 🎨 CSS KUSTOM: EFEK APPLE PREMIUM TRANSLUCENT & SMOOTH ANIMATION
st.markdown("""
    <style>
        /* Import Font Montserrat */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif !important;
        }

        /* BACKGROUND UTAMA: Nuansa Biru/Abu Dingin Maskapai Modern */
        .stApp {
            background-image: linear-gradient(rgba(240, 244, 248, 0.93), rgba(240, 244, 248, 0.93)), 
                              url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* SIDEBAR: Biru Gelap Pekat */
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
            box-shadow: 0px 4px 15px rgba(16, 185, 129, 0.4);
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
            font-family: 'Montserrat', sans-serif !important;
            color: #FFFFFF !important;
            font-size: 42px !important;
            font-weight: 900 !important;
            letter-spacing: 2px;
            margin: 0 !important;
        }
        
        .gmf-banner p {
            font-family: 'Montserrat', sans-serif !important;
            color: #00C9FF !important;
            font-size: 13px !important;
            font-weight: 700;
            letter-spacing: 5px;
            margin-top: 10px !important;
            margin-bottom: 0px !important;
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
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 30px 0 rgba(3, 18, 38, 0.1);
        }
        
        .kpi-title {
            font-family: 'Montserrat', sans-serif !important;
            color: #556980;
            font-size: 11px;
            font-weight: 800;
            margin-bottom: 6px;
            letter-spacing: 1.2px;
            text-transform: uppercase;
        }
        
        .kpi-number {
            font-family: 'Montserrat', sans-serif !important;
            font-size: 34px;
            font-weight: 900;
            color: #041226;
            margin: 0;
        }

        .section-header {
            font-family: 'Montserrat', sans-serif !important;
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
           🍏 APPLE STYLE POPOVER DESIGN AND SPRING ANIMATION (IOS ANIMATION)
           ===================================================================== */
        
        /* Modifikasi Tombol Pemicu Popover */
        div[data-testid="stPopover"] > button {
            background-color: rgba(255, 255, 255, 0.8) !important;
            backdrop-filter: blur(10px) !important;
            color: #041226 !important;
            border: 1px solid rgba(0, 92, 151, 0.25) !important;
            font-weight: 700 !important;
            border-radius: 12px !important; /* Sudut membulat halus khas iOS */
            padding: 12px 20px !important;
            box-shadow: 0px 4px 12px rgba(3, 18, 38, 0.04) !important;
            transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }
        
        div[data-testid="stPopover"] > button:hover {
            background-color: #FFFFFF !important;
            border-color: #005C97 !important;
            transform: scale(1.02);
            box-shadow: 0px 8px 20px rgba(0, 92, 151, 0.12) !important;
        }

        /* Frame Kontainer Jendela Pop-up Popover */
        div[data-testid="stPopoverBody"] {
            background-color: rgba(255, 255, 255, 0.92) !important;
            backdrop-filter: blur(20px) !important; /* Efek Kaca Buram Apple (Translucent) */
            border-radius: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12), 0 1px 3px rgba(0, 0, 0, 0.05) !important;
            padding: 24px !important;
            
            /* Menjalankan Animasi Kustom iPhone Semasa Terbuka */
            animation: appleSpringOpen 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.175) forwards !important;
            transform-origin: top center;
        }

        /* 📉 KEYFRAMES KUSTOM: Efek Membal Pegas Premium (Apple Spring Transition) */
        @keyframes appleSpringOpen {
            0% {
                opacity: 0;
                transform: scale(0.86) translateY(-10px);
                filter: blur(4px);
            }
            70% {
                transform: scale(1.01) translateY(1px);
                filter: blur(0px);
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
            except Exception as e:
                st.markdown("<h3 style='color:#041226; font-weight:800; margin-top:0;'>🔒 Secure Gateway Login</h3>", unsafe_allow_html=True)

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
                    st.toast("Akses berhasil! Menyiapkan dashboard...", icon="✅")
                    st.rerun()
                else:
                    st.error("🚨 Username atau password salah. Pastikan kredensial Anda valid.")
                
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
        st.error(f"Gagal sinkronisasi ke Google Sheets: {e}")
        return pd.DataFrame([{"ID": 551001, "Nama": "Ahmad", "Kualifikasi": "B737 Expert", "Lokasi": "DPS", "Status": "Active", "PPC Pengirim": "Offline Backup"}])

df_mentah = load_live_google_sheets()

# SIDEBAR CONTROL
st.sidebar.markdown("<br>", unsafe_allow_html=True)
try:
    st.sidebar.image("gmf aeroasia logo new blue.png", use_container_width=True)
except Exception as e:
    pass

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 INPUT & UPDATE DATA")
st.sidebar.markdown(f'<a href="{LINK_EDIT_GOOGLE_SHEETS}" target="_blank" class="sheets-btn"> 🟢 EDIT LIVE EXCEL SHEET</a>', unsafe_allow_html=True)

st.sidebar.markdown("### 🎛️ CONTROL PANEL")
if st.sidebar.button("🔄 RE-SYNC LIVE DATA", use_container_width=True):
    st.cache_data.clear()
    st.toast("Menghubungkan ke server GMF Database...", icon="📡")
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

# BANNER
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

# KPI METRICS
jumlah_di_cgk = len(df_pekerja[df_pekerja['Lokasi'].str.strip() == 'CGK'])
total_personel = len(df_pekerja)
personel_aktif = len(df_pekerja[df_pekerja['Status'].str.strip() == 'Active'])
personel_standby = len(df_pekerja[df_pekerja['Status'].str.strip() == 'Standby'])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">📁 Total Fleet Manpower</div><div class="kpi-number">{total_personel}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card" style="border-top-color: #10B981;"><div class="kpi-title" style="color:#10B981;">🟢 Active On Duty</div><div class="kpi-number">{personel_aktif}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card" style="border-top-color: #F59E0B;"><div class="kpi-title" style="color:#F59E0B;">🟡 Standby Alert</div><div class="kpi-number">{personel_standby}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-card" style="border-top-color: #3B82F6;"><div class="kpi-title" style="color:#3B82F6;">🔵 CGK Ready Resource</div><div class="kpi-number">{jumlah_di_cgk}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# MAIN LAYOUT
col_left, col_right = st.columns([4, 3])

with col_left:
    st.markdown("<div class='section-header'>🗺️ Live Tactical Spatial Distribution</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    
    m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles="OpenStreetMap")
    for lok, koordinat in DOKUMEN_KOORDINAT.items():
        sub_df = df_pekerja[df_pekerja['Lokasi'].str.strip() == lok]
        if not sub_df.empty:
            total_di_lokasi = len(sub_df)
            folium.Marker(location=koordinat, tooltip=f"Hub {lok}: {total_di_lokasi} Px").add_to(m)
            
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
        # 🍏 Widget Popover 1 dengan Animasi iOS Kustom
        with st.popover("⚙️ Open Status Telemetry Map", use_container_width=True):
            st.markdown("<h4 style='color:#041226; font-size:15px; font-weight:800; margin-bottom:10px;'>📊 Duty Distribution</h4>", unsafe_allow_html=True)
            if not df_pekerja.empty:
                st.bar_chart(df_pekerja['Status'].value_counts(), color="#107C41", height=180)
                
    with pop_col2:
        # 🍏 Widget Popover 2 dengan Animasi iOS Kustom
        with st.popover("✈️ Inspect Fleet Capabilities", use_container_width=True):
            st.markdown("<h4 style='color:#041226; font-size:15px; font-weight:800; margin-bottom:10px;'>🚀 Skillset Capabilities</h4>", unsafe_allow_html=True)
            if not df_pekerja.empty:
                st.bar_chart(df_pekerja['Kualifikasi'].value_counts().head(5), color="#F59E0B", height=180)
                
    st.markdown("<div class='section-header'>📈 Hub Resource Strength Breakdown</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    if not df_pekerja.empty:
        st.bar_chart(df_pekerja['Lokasi'].value_counts(), color="#005C97", height=280)
    st.markdown('</div>', unsafe_allow_html=True)
