import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import ssl
from typing import Dict, Tuple

# Bypass SSL untuk environment tertentu
ssl._create_default_https_context = ssl._create_unverified_context

# ==============================================================================
# CONFIG & DATA LAYER
# ==============================================================================
SHEET_EXPORT_URL = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/export?format=csv&gid=827445294"
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1IPuSFsMxZCKQBcL7NBoE-JIsQkG7-DePII0I2b8x9Vk/edit"

STATION_COORDINATES: Dict[str, Tuple[float, float]] = {
    "CGK": (-6.1256, 106.6559), "KNO": (3.6422, 98.8853),
    "DPS": (-8.7481, 115.1674), "SUB": (-7.3798, 112.7873),
    "UPG": (-5.0616, 119.5523), "DJJ": (-2.5783, 140.5167),
    "BTH": (1.1211, 104.1182), "BPN": (-1.2683, 116.8944)
}

@st.cache_data(ttl=300, show_spinner=False)
def fetch_manpower_data() -> pd.DataFrame:
    try:
        return pd.read_csv(SHEET_EXPORT_URL)
    except:
        return pd.DataFrame([{"ID": 551001, "Nama": "System Admin", "Kualifikasi": "A330/B777 Expert", "Lokasi": "CGK", "Status": "Active"}])

# ==============================================================================
# UI INJECTION: PREMIUM DUAL-FONT & HARMONIC COLORS
# ==============================================================================
def inject_premium_ui():
    st.markdown("""
        <style>
            /* Mengimpor Poppins untuk Judul dan Inter untuk Teks Biasa */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600;700;800&display=swap');
            
            /* GLOBAL CANVAS - Soft Light Clean Theme */
            .stApp {
                background-color: #F4F7F9 !important;
                color: #1E293B !important;
                font-family: 'Inter', sans-serif !important;
            }

            /* =========================================
               SIDEBAR KIRI (Fokus Perbaikan Permintaan)
               ========================================= */
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0F2027 0%, #203A43 50%, #2C5364 100%) !important;
                border-right: none !important;
                box-shadow: 4px 0 15px rgba(0,0,0,0.05);
            }
            
            /* Merapikan Font di Sidebar Kiri agar elegan dan menyatu */
            div[data-testid="stSidebarUserContent"] p, 
            div[data-testid="stSidebarUserContent"] h3,
            div[data-testid="stSidebarUserContent"] label,
            div[data-testid="stSidebarUserContent"] span {
                font-family: 'Poppins', sans-serif !important;
                color: #FFFFFF !important;
                letter-spacing: 0.3px;
            }

            div[data-testid="stSidebarUserContent"] h3 {
                font-weight: 700 !important;
                font-size: 1.2rem !important;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                padding-bottom: 10px;
                margin-bottom: 15px;
            }

            /* =========================================
               KARTU METRIK & DASHBOARD (Warna Dinamis)
               ========================================= */
            .metric-card {
                background: #FFFFFF;
                border-radius: 16px;
                padding: 20px;
                box-shadow: 0 10px 20px rgba(15, 23, 42, 0.04);
                transition: transform 0.2s ease;
                border: 1px solid #E2E8F0;
                border-left: 5px solid; /* Aksen warna di kiri */
            }
            .metric-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
            }
            .metric-title {
                font-family: 'Poppins', sans-serif;
                color: #64748B;
                font-size: 0.85rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .metric-value {
                font-family: 'Poppins', sans-serif;
                font-size: 2.2rem;
                font-weight: 800;
                color: #0F172A;
                margin-top: 5px;
            }

            /* =========================================
               HEADER & CONTAINER UTAMA
               ========================================= */
            h1, h2, h3, .section-header {
                font-family: 'Poppins', sans-serif !important;
                color: #0F172A !important;
            }
            
            .section-header {
                font-size: 1.25rem;
                font-weight: 700;
                margin-top: 1rem;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .main-panel {
                background: #FFFFFF;
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 10px 20px rgba(15, 23, 42, 0.03);
                border: 1px solid #E2E8F0;
                margin-bottom: 1.5rem;
            }

            /* Tombol Aksi */
            div.stButton > button {
                font-family: 'Poppins', sans-serif !important;
                background-color: #2563EB !important;
                color: #FFFFFF !important;
                border-radius: 8px !important;
                border: none !important;
                font-weight: 600 !important;
                padding: 10px 20px !important;
                box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
            }
            div.stButton > button:hover {
                background-color: #1D4ED8 !important;
                box-shadow: 0 6px 15px rgba(37, 99, 235, 0.3);
            }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# MAIN DASHBOARD
# ==============================================================================
def main():
    st.set_page_config(page_title="GMF AeroAsia | Outstation Command", layout="wide", initial_sidebar_state="expanded")
    inject_premium_ui()
    
    # --- SIDEBAR (Kombinasi warna elegan) ---
    with st.sidebar:
        st.markdown("<h3>🚀 TACTICAL COMMAND</h3>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <a href="{SHEET_EDIT_URL}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #10B981; color: white; padding: 12px; border-radius: 8px; text-align: center; font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 14px; box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2); margin-bottom: 15px;">
                    📝 Edit Master Database
                </div>
            </a>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Sync Database", use_container_width=True):
            fetch_manpower_data.clear()
            st.rerun()
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div style='color: #94A3B8; font-family: Poppins; font-size: 12px; text-transform: uppercase;'>Current Operator</div>", unsafe_allow_html=True)
        st.markdown("<div style='color: #38BDF8; font-family: Poppins; font-size: 16px; font-weight: 700;'>ADMINISTRATOR</div>", unsafe_allow_html=True)

    # --- HEADER UTAMA ---
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 30px; border-radius: 20px; color: white; box-shadow: 0 10px 30px rgba(15,23,42,0.15); margin-bottom: 30px;'>
            <h1 style='color: white !important; margin: 0; font-size: 2.2rem;'>Outstation Manpower Command Center</h1>
            <p style='color: #94A3B8; font-family: Inter, sans-serif; margin: 5px 0 0 0; font-size: 1rem;'>Live Tactical Resource Allocation & Telemetry Dashboard</p>
        </div>
    """, unsafe_allow_html=True)

    df_raw = fetch_manpower_data()
    
    # --- PENCARIAN (SEARCH) ---
    search_query = st.text_input("🔍 Global Directory Search (Name, Hub, or Qualification)", placeholder="Enter keyword to filter records...")
    if search_query:
        df_display = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
    else:
        df_display = df_raw

    # --- KPI METRICS (Dengan warna harmonis yang berbeda tiap kartu) ---
    t_px = len(df_display)
    a_px = len(df_display[df_display['Status'].str.strip() == 'Active'])
    s_px = len(df_display[df_display['Status'].str.strip() == 'Standby'])
    hq_px = len(df_display[df_display['Lokasi'].str.strip() == 'CGK'])

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='metric-card' style='border-left-color: #64748B;'><div class='metric-title'>Total Capacity</div><div class='metric-value'>{t_px}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card' style='border-left-color: #10B981;'><div class='metric-title'>Active Duty</div><div class='metric-value'>{a_px}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card' style='border-left-color: #F59E0B;'><div class='metric-title'>Standby Alert</div><div class='metric-value'>{s_px}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card' style='border-left-color: #3B82F6;'><div class='metric-title'>CGK Hub Reserves</div><div class='metric-value'>{hq_px}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- MAIN LAYOUT (MAP & DATA) ---
    col_map, col_chart = st.columns([7, 3])
    
    with col_map:
        st.markdown("<div class='section-header'>🗺️ Tactical Spatial Deployment</div>", unsafe_allow_html=True)
        st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
        
        # Peta Terang/Bersih (CartoDB Positron) yang cocok dengan tema terang
        m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles="CartoDB positron")
        for station, coords in STATION_COORDINATES.items():
            station_data = df_display[df_display['Lokasi'].str.strip() == station]
            if not station_data.empty:
                total_px = len(station_data)
                color = "#3B82F6" if station == "CGK" else ("#10B981" if any(station_data['Status'].str.strip() == 'Active') else "#F59E0B")
                
                # Desain Popup/Tooltip yang rapi
                html = f"""
                <div style="font-family:'Inter',sans-serif; min-width:200px;">
                    <div style="background:#0F172A; color:white; padding:8px; border-radius:4px 4px 0 0;">
                        <b>HUB {station}</b> ({total_px} Pax)
                    </div>
                    <table style="width:100%; font-size:12px; background:white; color:#1E293B; border-collapse:collapse;">
                """
                for _, row in station_data.iterrows():
                    html += f"<tr><td style='padding:4px; border-bottom:1px solid #E2E8F0;'>{row['Nama']}</td><td style='padding:4px; border-bottom:1px solid #E2E8F0; color:#64748B;'>{row['Kualifikasi']}</td></tr>"
                html += "</table></div>"
                
                folium.CircleMarker(location=coords, radius=8, color=color, fill=True, fill_color=color, fill_opacity=0.9, tooltip=folium.Tooltip(html)).add_to(m)
        
        st_folium(m, width="100%", height=400, returned_objects=[])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header'>📋 Personnel Directory Ledger</div>", unsafe_allow_html=True)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    with col_chart:
        st.markdown("<div class='section-header'>📊 Analytics Analytics</div>", unsafe_allow_html=True)
        st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
        st.markdown("<span style='font-family: Poppins; font-weight: 600; color: #0F172A;'>Operational Status</span>", unsafe_allow_html=True)
        if not df_display.empty:
            st.bar_chart(df_display['Status'].value_counts(), color="#10B981", height=200)
        
        st.markdown("<span style='font-family: Poppins; font-weight: 600; color: #0F172A;'>Top Hub Distribution</span>", unsafe_allow_html=True)
        if not df_display.empty:
            st.bar_chart(df_display['Lokasi'].value_counts(), color="#3B82F6", height=250)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
