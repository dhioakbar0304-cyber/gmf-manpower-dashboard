import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import ssl

# Bypass verifikasi SSL Certificate pada macOS
ssl._create_default_https_context = ssl._create_unverified_context

# 1. KONFIGURASI HALAMAN UTAMA
st.set_page_config(
    page_title="GMF AeroAsia - Manpower Allocation Dashboard",
    page_icon="https://www.garuda-indonesia.com/favicon.ico", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 CSS KUSTOM: AVIATION BACKDROP & GLASSMORPHISM DESIGN
st.markdown("""
    <style>
        /* Import Font Inter */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* BACKGROUND GAMBAR PENUH (TEMA AVIASI/HANGAR) */
        .stApp {
            background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), 
                              url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* Sidebar Gelap Premium dengan Teks Putih Kontras Tinggi */
        section[data-testid="stSidebar"] {
            background-color: #0B1329 !important; /* Biru Gelap Pekat */
            border-right: 2px solid #1E293B;
        }
        
        /* Memaksa semua elemen di sidebar terlihat putih terang */
        section[data-testid="stSidebar"] *, 
        section[data-testid="stSidebar"] span, 
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] h3 {
            color: #FFFFFF !important;
            font-weight: 500;
        }
        
        /* Membuang block abu-abu pada teks kode di sidebar */
        section[data-testid="stSidebar"] code {
            background-color: transparent !important;
            color: #38BDF8 !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            padding: 0px !important;
        }
        
        /* Tombol Sync Biru Terang di Sidebar */
        div.stButton > button {
            background-color: #0066CC !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid #38BDF8 !important;
            font-weight: 700 !important;
            padding: 10px !important;
        }
        div.stButton > button:hover {
            background-color: #0052A3 !important;
            box-shadow: 0px 4px 15px rgba(56, 189, 248, 0.4);
        }
        
        /* Banner GMF Premium Terang Kontras */
        .gmf-banner {
            background: linear-gradient(135deg, #0A2540 0%, #001020 100%);
            padding: 40px 20px;
            border-radius: 16px;
            color: #FFFFFF !important;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 5px solid #0066CC;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
        }
        
        .gmf-banner h1 {
            color: #FFFFFF !important;
            font-size: 46px !important;
            font-weight: 800 !important;
            letter-spacing: 1px;
            margin: 0 !important;
        }
        
        .gmf-banner p {
            color: #38BDF8 !important;
            font-size: 14px !important;
            font-weight: 700;
            letter-spacing: 3px;
            margin-top: 10px !important;
            margin-bottom: 0px !important;
            text-transform: uppercase;
        }

        /* Kolom Pencarian (Tebal & Glassmorphism) */
        div[data-testid="stTextInput"] input {
            border-radius: 8px !important;
            border: 2px solid #0A2540 !important;
            padding: 12px !important;
            font-size: 15px !important;
            color: #0F172A !important;
            background-color: rgba(255, 255, 255, 0.9) !important;
        }

        /* Kartu KPI dengan Efek Glassmorphism Modern */
        .kpi-card {
            background-color: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.4);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
            border-top: 5px solid #0066CC;
        }
        
        .kpi-title {
            color: #475569;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        
        .kpi-number {
            font-size: 34px;
            font-weight: 800;
            color: #0F172A;
            margin: 0;
        }

        /* Judul Section Sangat Jelas */
        .section-header {
            font-size: 20px;
            font-weight: 800;
            color: #0A2540;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 5px solid #0066CC;
            padding-left: 10px;
        }
        
        /* Container Float Glassmorphism untuk Peta & Tabel */
        .floating-panel {
            background-color: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.4);
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.06);
        }
    </style>
""", unsafe_allow_html=True)

# Master Koordinat Bandara Hub
DOKUMEN_KOORDINAT = {
    "CGK": [-6.1256, 106.6559], "KNO": [3.6422, 98.8853],
    "DPS": [-8.7481, 115.1674], "SUB": [-7.3798, 112.7873],
    "UPG": [-5.0616, 119.5523], "DJJ": [-2.5783, 140.5167],
    "BTH": [1.1211, 104.1182], "BPN": [-1.2683, 116.8944]
}

# Link Google Sheets live
LINK_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/export?format=csv&gid=827445294"

def load_live_google_sheets():
    try:
        return pd.read_csv(LINK_GOOGLE_SHEETS)
    except Exception as e:
        st.error(f"Gagal sinkronisasi ke Google Sheets: {e}")
        return pd.DataFrame([{"ID": 551001, "Nama": "Ahmad", "Kualifikasi": "B737 Expert", "Lokasi": "DPS", "Status": "Active", "PPC Pengirim": "Offline Backup"}])

df_mentah = load_live_google_sheets()

# 2. PANEL SIDEBAR KIRI
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# LOGO PT GMF AEROASIA (SVG CODE - DIJAMIN 100% MUNCUL)
gmf_logo_svg = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 120" width="100%">
  <!-- GMF Text -->
  <text x="10" y="70" font-family="'Inter', sans-serif" font-weight="900" font-size="70" fill="#FFFFFF">GMF</text>
  <!-- AeroAsia Text -->
  <text x="185" y="70" font-family="'Inter', sans-serif" font-weight="400" font-size="45" fill="#38BDF8">AeroAsia</text>
  <!-- Decorative underline -->
  <rect x="10" y="85" width="390" height="6" fill="#0066CC" rx="3"/>
</svg>
"""
st.sidebar.markdown(gmf_logo_svg, unsafe_allow_html=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("### 🎛️ CONTROL PANEL")
if st.sidebar.button("🔄 RE-SYNC LIVE DATA", use_container_width=True):
    st.cache_data.clear()
    st.toast("Menghubungkan ke server GMF Database...", icon="📡")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 MONITOR PROFILE")

st.sidebar.markdown("""
<div style="line-height: 1.8; font-size: 13px;">
    <p style="margin: 0;">👤 <b>User Authorized:</b><br><span style="color: #38BDF8 !important; font-weight: bold;">dhioakbar0304</span></p><br>
    <p style="margin: 0;">💼 <b>Role Account:</b><br><span style="color: #38BDF8 !important; font-weight: bold;">PPC Planning & Control</span></p><br>
    <p style="margin: 0;">🌐 <b>Environment:</b><br><span style="color: #38BDF8 !important; font-weight: bold;">Production Gateway</span></p><br>
    <p style="margin: 0;">📡 <b>Data Source:</b><br><span style="color: #10B981 !important; font-weight: bold;">Connected (Google Sheets Live)</span></p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# 3. HEADER BANNER MEWAH
st.markdown("""
    <div class="gmf-banner">
        <h1>GMF AEROASIA</h1>
        <p>Tactical Outstation Manpower Command Center</p>
    </div>
""", unsafe_allow_html=True)

# 🔍 4. SEARCH ENGINE MODERN
st.markdown("<div class='section-header'>🔎 Tactical Resource Search Engine</div>", unsafe_allow_html=True)
search_query = st.text_input("Ketik di bawah ini untuk mencari personel atau kualifikasi:", "", placeholder="Cari nama, keahlian khusus, atau lokasi stasiun (contoh: Ahmad, B737, Avionics, CGK)...")

# Filter data berdasarkan kueri pencarian
if search_query:
    df_pekerja = df_mentah[
        df_mentah['Nama'].str.contains(search_query, case=False, na=False) |
        df_pekerja['Kualifikasi'].str.contains(search_query, case=False, na=False) |
        df_pekerja['Lokasi'].str.contains(search_query, case=False, na=False)
    ]
else:
    df_pekerja = df_mentah

# 5. METRIK KARTU PREMIUM
jumlah_di_cgk = len(df_pekerja[df_pekerja['Lokasi'].str.strip() == 'CGK'])
total_personel = len(df_pekerja)
personel_aktif = len(df_pekerja[df_pekerja['Status'].str.strip() == 'Active'])
personel_standby = len(df_pekerja[df_pekerja['Status'].str.strip() == 'Standby'])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
        <div class="kpi-card" style="border-top-color: #64748B;">
            <div class="kpi-title">📁 Total Fleet Manpower</div>
            <div class="kpi-number">{total_personel} <span style="font-size:16px; color:#64748B;">Px</span></div>
        </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
        <div class="kpi-card" style="border-top-color: #10B981;">
            <div class="kpi-title" style="color:#10B981;">🟢 Active On Duty</div>
            <div class="kpi-number">{personel_aktif} <span style="font-size:16px; color:#10B981;">Px</span></div>
        </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
        <div class="kpi-card" style="border-top-color: #F59E0B;">
            <div class="kpi-title" style="color:#F59E0B;">🟡 Standby Alert</div>
            <div class="kpi-number">{personel_standby} <span style="font-size:16px; color:#F59E0B;">Px</span></div>
        </div>
    """, unsafe_allow_html=True)
with c4:
    if jumlah_di_cgk == 0:
        st.markdown(f"""
            <div class="kpi-card" style="border-top-color: #EF4444; background-color: #FEF2F2;">
                <div class="kpi-title" style="color:#EF4444;">🚨 CGK Base Alert</div>
                <div class="kpi-number" style="color:#EF4444; font-size: 22px; padding-top:10px;">EMPTY RESOURCE</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="kpi-card" style="border-top-color: #3B82F6;">
                <div class="kpi-title" style="color:#3B82F6;">🔵 CGK Ready Resource</div>
                <div class="kpi-number">{jumlah_di_cgk} <span style="font-size:16px; color:#3B82F6;">Px</span></div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. LAYOUT UTAMA: FLOATING PANEL (PETA & TABEL)
col_left, col_right = st.columns([4, 3])

with col_left:
    st.markdown("<div class='section-header'>🗺️ Live Tactical Spatial Distribution</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    
    m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles="OpenStreetMap")
    
    for lok, koordinat in DOKUMEN_KOORDINAT.items():
        sub_df = df_pekerja[df_pekerja['Lokasi'].str.strip() == lok]
        if not sub_df.empty:
            total_di_lokasi = len(sub_df)
            warna_pin = "red" if lok == "CGK" else ("green" if any(sub_df['Status'].str.strip() == 'Active') else "orange")
            
            popup_html = f"""
            <div style='font-family: "Inter", sans-serif; color: #1e293b; min-width:240px;'>
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
            
    st_folium(m, width="100%", height=480)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='section-header'>📋 Personnel Directory Ledger</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div class='section-header' style='margin-top:20px;'>📊 Hub Strength Chart</div>", unsafe_allow_html=True)
    st.markdown('<div class="floating-panel">', unsafe_allow_html=True)
    if not df_pekerja.empty:
        distribusi_lokasi = df_pekerja['Lokasi'].value_counts()
        st.bar_chart(distribusi_lokasi, color="#1E3A8A")
    else:
        st.caption("Tidak ada data untuk dibuat grafik.")
    st.markdown('</div>', unsafe_allow_html=True)
