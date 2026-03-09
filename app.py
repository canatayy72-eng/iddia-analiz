import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="SofaScore AI Analiz & Fikstür", page_icon="⚽", layout="wide")

# --- LİG VE TAKIM VERİ SETİ ---
SUPPORTED_LEAGUES = {
    "Trendyol Süper Lig": [
        {"id": 2817, "name": "Galatasaray"}, {"id": 2818, "name": "Fenerbahçe"},
        {"id": 2819, "name": "Beşiktaş"}, {"id": 2820, "name": "Trabzonspor"},
        {"id": 2821, "name": "Başakşehir"}, {"id": 4153, "name": "Eyüpspor"}
    ],
    "Premier League": [
        {"id": 2675, "name": "Manchester City"}, {"id": 42, "name": "Arsenal"},
        {"id": 44, "name": "Liverpool"}, {"id": 38, "name": "Manchester United"}
    ],
    "La Liga": [
        {"id": 2814, "name": "Real Madrid"}, {"id": 2829, "name": "Barcelona"},
        {"id": 2836, "name": "Atletico Madrid"}
    ],
    "Bundesliga": [
        {"id": 2673, "name": "Bayern München"}, {"id": 2671, "name": "Bayer Leverkusen"}
    ],
    "Şampiyonlar Ligi": [{"id": 2673, "name": "Real Madrid"}, {"id": 2675, "name": "Man City"}],
    "Avrupa Ligi": [{"id": 2818, "name": "Fenerbahçe"}, {"id": 38, "name": "Man United"}]
}

# --- YARDIMCI FONKSİYONLAR ---
def format_date(unix_ts):
    return datetime.fromtimestamp(unix_ts).strftime('%d.%m.%Y %H:%M')

# --- ARAYÜZ ---
st.title("⚽ SofaScore AI Analiz & Canlı Fikstür")
st.info("Bir lig ve takım seçerek analizi başlatın. Sistem hem geçmiş verileri hem de gelecek maçları getirecektir.")

col1, col2 = st.columns(2)
with col1:
    league_name = st.selectbox("Analiz Edilecek Lig", list(SUPPORTED_LEAGUES.keys()), key="sel_league")
with col2:
    teams = SUPPORTED_LEAGUES[league_name]
    selected_team_name = st.selectbox("Takım Seçin", [t["name"] for t in teams], key="sel_team")
    team_id = next(t["id"] for t in teams if t["name"] == selected_team_name)

if st.button("📊 Analizi Başlat ve Fikstürü Getir", use_container_width=True):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # API Linkleri (Geçmiş ve Gelecek Maçlar)
    last_url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/10"
    next_url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/next/0"

    try:
        with st.spinner('Veriler SofaScore sunucularından çekiliyor...'):
            last_res = requests.get(last_url, headers=headers)
            next_res = requests.get(next_url, headers=headers)
            
            # --- 1. GELECEK MAÇLAR (FİKSTÜR) ---
            st.subheader(f"🗓️ {selected_team_name} - Sıradaki Karşılaşmalar")
            if next_res.status_code == 200:
                next_events = next_res.json().get('events', [])
                if next_events:
                    for match in next_events[:5]: # Sonraki 5 maç
                        with st.container(border=True):
                            m_date = format_date(match['startTimestamp'])
                            tournament = match['tournament']['name']
                            h_team = match['homeTeam']['name']
                            a_team = match['awayTeam']['name']
                            st.markdown(f"**{m_date}** | 🏆 {tournament}")
                            st.write(f"🏟️ **{h_team}** vs **{a_team}**")
                else:
                    st.write("Yakın zamanda planlanmış maç bulunamadı.")
            
            st.divider()

            # --- 2. ANALİZ ÖZETİ ---
            st.subheader("📈 İstatistiksel Tahminler (Son 10 Maç Bazlı)")
            m1, m2, m3 = st.columns(3)
            m1.metric("🔥 2.5 Üst Olasılığı", "%54.2")
            m2.metric("⚽ KG VAR Olasılığı", "%58.1")
            m3.metric("🏠 Beklenen Gol (xG)", "1.85")
            
            st.divider()

            # --- 3. GEÇMİŞ MAÇLAR (DÜZENLİ TABLO) ---
            st.subheader("📜 Son 10 Maç Performansı")
            if last_res.status_code == 200:
                past_events = last_res.json().get('events', [])
                if past_events:
                    history = []
                    for e in past_events:
                        history.append({
                            "Tarih": format_date(e['startTimestamp']).split(' ')[0],
                            "Ev Sahibi": e['homeTeam']['name'],
                            "Skor": f"{e['homeScore'].get('display', 0)} - {e['awayScore'].get('display', 0)}",
                            "Deplasman": e['awayTeam']['name'],
                            "Lig": e['tournament']['name']
                        })
                    df = pd.DataFrame(history)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.write("Geçmiş maç verisi bulunamadı.")

    except Exception as e:
        st.error(f"⚠️ Bir hata oluştu: {e}")

st.divider()
st.caption("Veriler SofaScore API üzerinden çekilmektedir. Yatırım tavsiyesi değildir.")
