import streamlit as st
import requests

# Sayfa Yapılandırması
st.set_page_config(page_title="AI İddaa Analiz", page_icon="⚽", layout="wide")

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
        {"id": 2673, "name": "Bayern München"}, {"id": 2671, "name": "Bayer Leverkusen"},
        {"id": 2677, "name": "Borussia Dortmund"}
    ],
    "Şampiyonlar Ligi": [
        {"id": 2673, "name": "Real Madrid"}, {"id": 2675, "name": "Man City"},
        {"id": 2671, "name": "Inter"}, {"id": 2674, "name": "PSG"}
    ],
    "Avrupa Ligi": [
        {"id": 2818, "name": "Fenerbahçe"}, {"id": 2819, "name": "Beşiktaş"},
        {"id": 42, "name": "Arsenal"}
    ]
}

# Sidebar / Yan Menü
st.sidebar.title("⚽ Analiz Paneli")
st.sidebar.info("Lütfen analiz etmek istediğiniz ligi ve takımı seçin.")

# Arayüz Seçimleri
league_name = st.selectbox("Bir Lig Seçin", list(SUPPORTED_LEAGUES.keys()))
teams = SUPPORTED_LEAGUES[league_name]
team_names = [t["name"] for t in teams]
selected_team_name = st.selectbox("Bir Takım Seçin", team_names)

# Seçilen takımın ID'sini al
team_id = next(t["id"] for t in teams if t["name"] == selected_team_name)

if st.button("📊 Analizi Başlat"):
    with st.spinner(f'{selected_team_name} verileri analiz ediliyor...'):
        # SofaScore API URL (Örnek)
        api_url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/10"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ {selected_team_name} için son 10 maç verisi çekildi!")
                
                # ÖRNEK ANALİZ ÇIKTISI
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Seçilen Takım ID", team_id)
                with col2:
                    st.metric("Veri Durumu", "Aktif")
                
                st.divider()
                st.subheader("Ham Veri Çıktısı (Önizleme)")
                st.json(data) # Burası gerçek analiz formüllerinle değiştirilecek
                
            elif response.status_code == 403:
                st.error("🚫 API Erişimi Reddedildi. (User-Agent veya API Key hatası)")
            elif response.status_code == 429:
                st.error("⏳ Çok fazla istek gönderildi. API kotası dolmuş olabilir.")
            else:
                st.error(f"❌ Veri çekilemedi. Hata Kodu: {response.status_code}")
                
        except Exception as e:
            st.error(f"⚠️ Bağlantı Hatası: {str(e)}")

# Alt Bilgi
st.markdown("---")
st.caption("AI İddaa Analiz Sistemi - 2026")
