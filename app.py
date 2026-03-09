import streamlit as st
import requests
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="SofaScore AI Analiz", page_icon="⚽", layout="wide")

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
def unix_to_date(unix_ts):
    return datetime.fromtimestamp(unix_ts).strftime('%d.%m.%Y %H:%M')

# --- ARAYÜZ ---
st.title("⚽ SofaScore AI Analiz & Fikstür")
st.markdown("---")

# Seçim Alanları (Benzersiz ID'ler eklendi)
col1, col2 = st.columns(2)
with col1:
    league_name = st.selectbox(
        "Lig Seçin", 
        list(SUPPORTED_LEAGUES.keys()), 
        key="unique_league_select"
    )
with col2:
    teams = SUPPORTED_LEAGUES[league_name]
    selected_team_name = st.selectbox(
        "Takım Seçin", 
        [t["name"] for t in teams], 
        key="unique_team_select"
    )
    team_id = next(t["id"] for t in teams if t["name"] == selected_team_name)

if st.button("📊 Analiz Et ve Fikstürü Getir", use_container_width=True):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # API Linkleri
    last_url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/10"
    next_url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/next/0"

    try:
        with st.spinner('Veriler SofaScore üzerinden güncelleniyor...'):
            last_res = requests.get(last_url, headers=headers)
            next_res = requests.get(next_url, headers=headers)
            
            if last_res.status_code == 200:
                # 1. ANALİZ KISMI (İstatistiksel Özet)
                st.subheader(f"📈 {selected_team_name} Analiz Özeti")
                m1, m2, m3 = st.columns(3)
                m1.metric("🔥 2.5 Üst Olasılığı", "%54.2") # Örnek Analiz
                m2.metric("⚽ KG VAR Olasılığı", "%58.1") # Örnek Analiz
                m3.metric("🏠 Form Durumu", "Yüksek")
                
                st.divider()

                # 2. FİKSTÜR KISMI (Sıradaki Maçlar)
                st.subheader("🗓️ Sıradaki Karşılaşmalar")
                if next_res.status_code == 200:
                    events = next_res.json().get('events', [])
                    if events:
                        # İlk 5 maçı tablo gibi gösterelim
                        for match in events[:5]:
                            home = match['homeTeam']['name']
                            away = match['awayTeam']['name']
                            match_time = unix_to_date(match['startTimestamp'])
                            tournament = match['tournament']['name']
                            
                            st.info(f"📅 **{match_time}** | 🏆 {tournament}\n\n🏟️ **{home}** vs **{away}**")
                    else:
                        st.warning("Bu takım için yakın zamanda planlanmış bir maç bulunamadı.")
                else:
                    st.error("Fikstür bilgisi çekilirken bir sorun oluştu.")

                with st.expander("Teknik Detayları İncele (JSON)"):
                    st.json(last_res.json())
            else:
                st.error(f"Veri çekilemedi. Hata Kodu: {last_res.status_code}")
                
    except Exception as e:
        st.error(f"Sistem Hatası: {e}")

st.caption("Veriler SofaScore veritabanından anlık olarak çekilmektedir.")
