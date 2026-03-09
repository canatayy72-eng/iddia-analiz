import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="Pro Analiz Sistemi", page_icon="⚽", layout="wide")

# --- GENİŞLETİLMİŞ LİG VE TAKIM VERİ SETİ ---
SUPPORTED_LEAGUES = {
    "Trendyol Süper Lig": [
        {"id": 2817, "name": "Galatasaray"}, {"id": 2818, "name": "Fenerbahçe"},
        {"id": 2819, "name": "Beşiktaş"}, {"id": 2820, "name": "Trabzonspor"},
        {"id": 2821, "name": "Başakşehir"}, {"id": 4153, "name": "Eyüpspor"}
    ],
    "Premier League": [
        {"id": 2675, "name": "Manchester City"}, {"id": 42, "name": "Arsenal"},
        {"id": 44, "name": "Liverpool"}, {"id": 38, "name": "Manchester United"},
        {"id": 40, "name": "Chelsea"}
    ],
    "La Liga": [
        {"id": 2814, "name": "Real Madrid"}, {"id": 2829, "name": "Barcelona"},
        {"id": 2836, "name": "Atletico Madrid"}
    ],
    "Bundesliga": [
        {"id": 2673, "name": "Bayern München"}, {"id": 2671, "name": "Bayer Leverkusen"},
        {"id": 2677, "name": "Borussia Dortmund"}
    ],
    "Şampiyonlar Ligi": [{"id": 2673, "name": "Real Madrid"}, {"id": 2675, "name": "Man City"}],
    "Avrupa Ligi": [{"id": 2818, "name": "Fenerbahçe"}, {"id": 2819, "name": "Beşiktaş"}]
}

# --- YARDIMCI FONKSİYONLAR ---
def format_date(unix_ts):
    return datetime.fromtimestamp(unix_ts).strftime('%d.%m.%Y %H:%M')

# --- ARAYÜZ ---
st.title("⚽ Profesyonel Takım Analiz Paneli")
st.markdown("---")

# Seçim Alanları
col_l, col_t = st.columns(2)
with col_l:
    league_name = st.selectbox("Lütfen Bir Lig Seçin", list(SUPPORTED_LEAGUES.keys()), key="l_select_pro")
with col_t:
    teams = SUPPORTED_LEAGUES[league_name]
    selected_team_name = st.selectbox("Analiz Edilecek Takımı Seçin", [t["name"] for t in teams], key="t_select_pro")
    team_id = next(t["id"] for t in teams if t["name"] == selected_team_name)

if st.button(f"📊 {selected_team_name} Verilerini Getir", use_container_width=True):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # API Endpointleri
    last_url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/10"
    next_url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/next/0"

    try:
        with st.spinner(f'{selected_team_name} için güncel veriler hazırlan
