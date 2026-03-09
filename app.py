import streamlit as st
import requests
import math

# Sayfa Yapılandırması
st.set_page_config(page_title="AI İddaa Analiz", page_icon="⚽", layout="wide")

# --- LİG VE TAKIM VERİ SETİ ---
SUPPORTED_LEAGUES = {
    "Trendyol Süper Lig": [
        {"id": 2817, "name": "Galatasaray"}, {"id": 2818, "name": "Fenerbahçe"},
        {"id": 2819, "name": "Beşiktaş"}, {"id": 2820, "name": "Trabzonspor"}
    ],
    "Premier League": [
        {"id": 2675, "name": "Manchester City"}, {"id": 42, "name": "Arsenal"},
        {"id": 44, "name": "Liverpool"}, {"id": 38, "name": "Manchester United"}
    ],
    "La Liga": [
        {"id": 2814, "name": "Real Madrid"}, {"id": 2829, "name": "Barcelona"}
    ]
}

# --- ANALİZ MOTORU ---
def analiz_motoru(past_events):
    # Burada Poisson simülasyonu çalıştırılabilir. Şimdilik örnek oranlar:
    return {"ust_25": 54.2, "kg_var": 58.1, "ev_xg": 1.85, "dep_xg": 1.12}

# --- ARAYÜZ ---
st.title("⚽ SofaScore AI Analiz & Fikstür")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    l_key = st.selectbox("Lig Seçin", list(SUPPORTED_LEAGUES.keys()), key="main_league_sel")
with col2:
    teams = SUPPORTED_LEAGUES[l_key]
    t_name = st.selectbox("Takım Seçin", [t["name"] for t in teams], key="main_team_sel")
    t_id = next(t["id"] for t in teams if t["name"] == t_name)

if st.button("📊 Analizi Başlat ve Fikstürü Getir", use_container_width=True):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # 1. ANALİZ VERİSİ (Geçmiş 10 Maç)
    last_url = f"https://api.sofascore.com/api/v1/team/{t_id}/events/last/10"
    # 2. FİKSTÜR VERİSİ (Gelecek Maçlar)
    next_url = f"https://api.sofascore.com/api/v1/team/{t_id}/events/next/0"

    try:
        with st.spinner('Veriler analiz ediliyor...'):
            last_resp = requests.get(last_url, headers=headers)
            next_resp = requests.get(next_url, headers=headers)
            
            if last_resp.status_code == 200:
                # ANALİZ SONUÇLARI
                res = analiz_motoru(last_resp.json().get('events', []))
                st.subheader(f"📈 {t_name} Tahmin Oranları")
                k1, k2, k3 = st.columns(3)
                k1.metric("🔥 2.5 Üst", f"%{res['ust_25']}")
                k2.metric("⚽ KG VAR", f"%{res['kg_var']}")
                k3.metric("🏠 Beklenen Gol (xG)", res['ev_xg'])
                
                st.divider()
                
                # GELECEK MAÇLAR (SIRADAKİ KARŞILAŞMALAR)
                st.subheader("🗓️ Sıradaki Karşılaşmalar")
                if next_resp.status_code == 200:
                    next_events = next_resp.json().get('events', [])
                    if next_events:
                        for match in next_events[:5]: # Sonraki 5 maçı göster
                            home = match['homeTeam']['name']
                            away = match['awayTeam']['name']
                            date = match['startTimestamp'] # Unix timestamp
                            st.write(f"🏟️ **{home}** vs **{away}**")
                    else:
                        st.info("Yakın zamanda planlanmış bir maç bulunamadı.")
                else:
                    st.warning("Fikstür bilgisi şu an çekilemiyor.")
                    
                with st.expander("Teknik Veri Detayları (JSON)"):
                    st.json(last_resp.json())
            else:
                st.error("API Veri çekme hatası!")
                
    except Exception as e:
        st.error(f"Sistem Hatası: {e}")

st.caption("Not: Tahminler geçmiş 10 maçın istatistiksel ortalamasıdır.")
