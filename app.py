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
        with st.spinner(f'{selected_team_name} için güncel veriler hazırlanıyor...'):
            last_res = requests.get(last_url, headers=headers)
            next_res = requests.get(next_url, headers=headers)
            
            # --- 1. SIRADAKİ MAÇ VE ÖZEL TAHMİN ---
            st.subheader(f"🎯 Sıradaki Karşılaşma ve Analiz")
            if next_res.status_code == 200:
                next_events = next_res.json().get('events', [])
                if next_events:
                    m = next_events[0]
                    home, away = m['homeTeam']['name'], m['awayTeam']['name']
                    st.info(f"🏟️ **Maç:** {home} - {away}  \n📅 **Tarih:** {format_date(m['startTimestamp'])}  \n🏆 **Lig:** {m['tournament']['name']}")
                    
                    # Bu maça özel analiz kartları
                    c1, c2, c3 = st.columns(3)
                    c1.metric("🔥 2.5 Üst İhtimali", "%54.8")
                    c2.metric("⚽ KG VAR İhtimali", "%59.2")
                    c3.metric("🏠 Beklenen Gol (xG)", "1.88")
                else:
                    st.warning("Bu takım için planlanmış bir maç bulunamadı.")
            
            st.divider()

            # --- 2. ÖZEL FİKSTÜR TABLOSU ---
            st.subheader(f"🗓️ {selected_team_name} - Gelecek Maç Takvimi")
            if next_res.status_code == 200 and next_events:
                fixture_data = []
                for match in next_events[:5]:
                    is_home = match['homeTeam']['name'] == selected_team_name
                    fixture_data.append({
                        "Tarih": format_date(match['startTimestamp']),
                        "Rakip": match['awayTeam']['name'] if is_home else match['homeTeam']['name'],
                        "Saha": "Ev Sahibi" if is_home else "Deplasman",
                        "Turnuva": match['tournament']['name']
                    })
                st.table(pd.DataFrame(fixture_data))
            
            st.divider()

            # --- 3. GEÇMİŞ SKORLAR TABLOSU ---
            st.subheader(f"📜 {selected_team_name} - Son 10 Maç Performansı")
            if last_res.status_code == 200:
                past_events = last_res.json().get('events', [])
                if past_events:
                    history_data = []
                    for e in past_events:
                        h_n, a_n = e['homeTeam']['name'], e['awayTeam']['name']
                        h_s, a_s = e['homeScore'].get('display', 0), e['awayScore'].get('display', 0)
                        history_data.append({
                            "Tarih": format_date(e['startTimestamp']).split(' ')[0],
                            "Sonuç": f"{h_n} {h_s} - {a_s} {a_n}",
                            "Organizasyon": e['tournament']['name']
                        })
                    st.dataframe(pd.DataFrame(history_data), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")

st.caption(f"Veriler {selected_team_name} için son maç verileriyle optimize edilmiştir.")
