import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import ssl

# Bypass verifikasi SSL Certificate pada macOS
ssl._create_default_https_context = ssl._create_unverified_context

# 1. KONFIGURASI HALAMAN UTAMA (ENTERPRISE STANDARD)
st.set_page_config(
    page_title="GMF AeroAsia - Manpower Allocation Dashboard",
    page_icon="https://www.garuda-indonesia.com/favicon.ico", # Icon Garuda Group
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 CSS KUSTOM: PUTIH BERSIH & BIRU NAVY (SANGAT MUDAH DIBACA)
st.markdown("""
    <style>
        /* Background utama putih bersih */
        .stApp {
            background-color: #FFFFFF;
            color: #1E293B;
        }
        
        /* Sidebar abu-abu terang dengan teks hitam pekat */
        section[data-testid="stSidebar"] {
            background-color: #F8FAFC !important;
            border-right: 1px solid #E2E8F0;
        }
        section[data-testid="stSidebar"] * {
            color: #0F172A !important;
        }
        
        /* Judul GMF Premium */
        .main-title {
            font-family: 'Inter', Arial, sans-serif;
            font-size: 36px;
            font-weight: 800;
            color: #1E3A8A; /* Biru Navy GMF */
            text-align: center;
            margin-top: -15px;
            margin-bottom: 0px;
        }
        
        .sub-title {
            color: #64748B;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 2px;
            text-align: center;
            margin-bottom: 25px;
        }

        /* Kartu KPI Kotak Minimalis Modern */
        .kpi-box {
            background-color: #F1F5F9;
            border: 1px solid #E2E8F0;
            padding: 15px;
            border-radius: 12px;
            border-left: 5px solid #1E3A8A;
        }
        
        .kpi-lbl {
            color: #475569;
            font-size: 11px;
            font-weight: 700;
            margin: 0 0 5px 0;
            text-transform: uppercase;
        }
        
        .kpi-val {
            font-size: 28px;
            font-weight: 700;
            color: #0F172A;
            margin: 0;
        }

        /* Judul Section */
        .section-header {
            font-size: 16px;
            font-weight: 700;
            color: #1E3A8A;
            margin-top: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #38BDF8;
            padding-left: 8px;
        }
        
        /* Hilangkan header standar streamlit */
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Master Koordinat Bandara Hub
DOKUMEN_KOORDINAT = {
    "CGK": [-6.1256, 106.6559], "KNO": [3.6422, 98.8853],
    "DPS": [-8.7481, 115.1674], "SUB": [-7.3798, 112.7873],
    "UPG": [-5.0616, 119.5523], "DJJ": [-2.5783, 140.5167],
    "BTH": [1.1211, 104.1182], "BPN": [-1.2683, 116.8944]
}

# 🔗 LINK GOOGLE SHEETS LIVE KAMU
LINK_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/export?format=csv&gid=827445294"

def load_live_google_sheets():
    try:
        return pd.read_csv(LINK_GOOGLE_SHEETS)
    except Exception as e:
        st.error(f"Gagal sinkronisasi ke Google Sheets: {e}")
        return pd.DataFrame([{"ID": 551001, "Nama": "Ahmad", "Kualifikasi": "B737 Expert", "Lokasi": "DPS", "Status": "Active", "PPC Pengirim": "Offline Backup"}])

# Data Awal dari Google Sheets
df_mentah = load_live_google_sheets()

# 2. PANEL SIDEBAR ABU-ABU TERANG (Teks Terbaca 100%)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/Garuda_Indonesia_Logo.svg", width=160)
st.sidebar.markdown("---")

st.sidebar.markdown("### 🎛️ DATA MANAGER")
if st.sidebar.button("🔄 RE-SYNC DATA CLOUD", use_container_width=True):
    st.cache_data.clear()
    st.toast("Sinkronisasi ulang Google Sheets...", icon="📥")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 SYSTEM PROFILE")
st.sidebar.markdown("**User:** Central Administrator\n\n**Role:** PPC Planning & Control\n\n**Server:** Google Sheets Live")
st.sidebar.markdown("---")

# 3. HEADER UTAMA
st.markdown("<h1 class='main-title'>GMF AEROASIA</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>REAL-TIME OUTSTATION MANPOWER MONITORING SYSTEM</p>", unsafe_allow_html=True)

# 🔍 4. SEARCH ENGINE (FITUR PENCARIAN BARU)
st.markdown("<div class='section-header'>🔎 Personnel Search Engine</div>", unsafe_allow_html=True)
search_query = st.text_input("Ketik Nama Teknisi atau Kualifikasi / Rating Pesawat untuk Menyaring Data:", "", placeholder="Contoh: Ahmad, B737, Avionics...")

# Proses Penyaringan Data Berdasarkan Search Engine
if search_query:
    df_pekerja = df_mentah[
        df_mentah['Nama'].str.contains(search_query, case=False, na=False) |
        df_mentah['Kualifikasi'].str.contains(search_query, case=False, na=False) |
        df_mentah['Lokasi'].str.contains(search_query, case=False, na=False)
    ]
else:
    df_pekerja = df_mentah

# 5. METRIK KOTAK ABU-ABU MINIMALIS
jumlah_di_cgk = len(df_pekerja[df_pekerja['Lokasi'].str.strip() == 'CGK'])
total_personel = len(df_pekerja)
personel_aktif = len(df_pekerja[df_pekerja['Status'].str.strip() == 'Active'])
personel_standby = len(df_pekerja[df_pekerja['Status'].str.strip() == 'Standby'])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='kpi-box'><p class='kpi-lbl'>📁 TOTAL TRACKED</p><p class='kpi-val'>{total_personel} Px</p></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='kpi-box' style='border-left-color:#10B981;'><p class='kpi-lbl' style='color:#10B981;'>🟢 ACTIVE DUTY</p><p class='kpi-val'>{personel_aktif} Px</p></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='kpi-box' style='border-left-color:#F59E0B;'><p class='kpi-lbl' style='color:#F59E0B;'>🟡 STANDBY READY</p><p class='kpi-val'>{personel_standby} Px</p></div>", unsafe_allow_html=True)
with c4:
    if jumlah_di_cgk == 0:
        st.markdown(f"<div class='kpi-box' style='border-left-color:#EF4444; background-color:#FEF2F2;'><p class='kpi-lbl' style='color:#EF4444;'>🚨 CGK BASE STATUS</p><p class='kpi-val' style='color:#EF4444; font-size:20px; padding-top:4px;'>CRITICAL ALERT</p></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='kpi-box' style='border-left-color:#3B82F6;'><p class='kpi-lbl' style='color:#3B82F6;'>🔵 CGK BASE SECURE</p><p class='kpi-val'>{jumlah_di_cgk} Px</p></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. LAYOUT VISUAL: PETA KEMBALI TERANG & DATAFRAME
col_left, col_right = st.columns([4, 3])

with col_left:
    st.markdown("<div class='section-header'>🗺️ Geographic Manpower Live Map</div>", unsafe_allow_html=True)
    
    # KEMBALI KE PETA TERANG (OpenStreetMap standar, bumi warna biru & hijau normal)
    m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles="OpenStreetMap")
    
    for lok, koordinat in DOKUMEN_KOORDINAT.items():
        sub_df = df_pekerja[df_pekerja['Lokasi'].str.strip() == lok]
        if not sub_df.empty:
            total_di_lokasi = len(sub_df)
            warna_pin = "red" if lok == "CGK" else ("green" if any(sub_df['Status'].str.strip() == 'Active') else "orange")
            
            popup_html = f"""
            <div style='font-family: Arial, sans-serif; color: #1e293b; min-width:240px;'>
                <h4 style='margin:0 0 5px 0; color:#1e3a8a;'>Station: {lok}</h4>
                <p style='margin:0 0 8px 0; font-size:12px;'>Total Resource: <b>{total_di_lokasi} Personel</b></p>
                <table style='width:100%; font-size:11px; border-collapse: collapse;'>
                    <tr style='background-color:#f1f5f9; text-align:left;'>
                        <th style='padding:4px;'>Nama</th><th style='padding:4px;'>Kualifikasi</th>
                    </tr>
            """
            for _, row in sub_df.iterrows():
                popup_html += f"<tr><td style='padding:4px; border-bottom:1px solid #e2e8f0;'>{row['Nama']}</td><td style='padding:4px; border-bottom:1px solid #e2e8f0;'>{row['Kualifikasi']}</td></tr>"
            popup_html += "</table></div>"
            
            folium.Marker(
                location=koordinat,
                popup=folium.Popup(popup_html, max_width=380),
                tooltip=f"Hub {lok}: {total_di_lokasi} Px",
                icon=folium.Icon(color=warna_pin, icon="info-sign")
            ).add_to(m)
            
    st_folium(m, width="100%", height=470)

with col_right:
    st.markdown("<div class='section-header'>📋 Personnel Directory Ledger</div>", unsafe_allow_html=True)
    
    st.dataframe(
        df_pekerja,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID Personnel", format="%d"),
            "Nama": "Operator Name",
            "Kualifikasi": "Aircraft Core Qualification",
            "Lokasi": "Station Hub",
            "Status": "Status Duty",
            "PPC Pengirim": "Telemetry Source"
        }
    )
    
    st.markdown("<div class='section-header' style='margin-top:20px;'>📊 Hub Strength Chart</div>", unsafe_allow_html=True)
    if not df_pekerja.empty:
        distribusi_lokasi = df_pekerja['Lokasi'].value_counts()
        st.bar_chart(distribusi_lokasi, color="#1E3A8A")
    else:
        st.caption("Tidak ada data untuk dibuat grafik.")
