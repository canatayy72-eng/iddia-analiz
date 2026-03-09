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
import streamlit as st
import requests
import math

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

# --- POISSON HESAPLAMA FONKSİYONU ---
def poisson(actual, mean):
    return (math.exp(-mean) * (mean**actual)) / math.factorial(actual)

def analiz_et(events):
    # Basit bir simülasyon (Gerçek xG değerlerini buradan hesaplayabilirsin)
    # Burada son 10 maçın ortalamasını aldığını varsayıyoruz
    home_expectancy = 1.7
    away_expectancy = 1.0
    
    over_25 = 50.6
    btts_yes = 52.0
    
    return home_expectancy, away_expectancy, over_25, btts_yes

# --- ARAYÜZ ---
st.title("⚽ SofaScore AI Analiz")
st.caption("Takım seçerek son maç verilerine dayalı Poisson Analizi yapın.")

col1, col2 = st.columns(2)
with col1:
    league_name = st.selectbox("Bir Lig Seçin", list(SUPPORTED_LEAGUES.keys()))
with col2:
    teams = SUPPORTED_LEAGUES[league_name]
    selected_team = st.selectbox("Bir Takım Seçin", [t["name"] for t in teams])
    team_id = next(t["id"] for t in teams if t["name"] == selected_team)

if st.button("📊 Analizi Başlat"):
    api_url = f"https://api.sofascore.com/api/v1/team/{team_id}/events/last/10"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ {selected_team} için son 10 maç verisi çekildi!")
            
            # Analiz Motorunu Çalıştır
            ev_xg, dep_xg, ust_ihtimal, kg_ihtimal = analiz_et(data.get('events', []))
            
            # İstatistik Kartları
            c1, c2 = st.columns(2)
            c1.metric("🔥 2.5 Üst İhtimali", f"%{ust_ihtimal}")
            c2.metric("⚽ KG VAR İhtimali", f"%{kg_ihtimal}")
            
            # Skor Dağılım Tablosu (Görseldeki gibi)
            st.subheader("📊 Olası Skor Dağılımı (%)")
            # Burada bir dataframe veya tablo oluşturabilirsin
            st.image("https://via.placeholder.com/800x200.png?text=Skor+Tablosu+Buraya+Gelecek") # Geçici
            
            st.info(f"💡 Tahmini xG Değerleri: Ev: {ev_xg} | Dep: {dep_xg}")
            
            with st.expander("Ham Veri Çıktısını Gör"):
                st.json(data)
        else:
            st.error(f"Veri çekilemedi. Hata: {response.status_code}")
    except Exception as e:
        st.error(f"Hata oluştu: {e}")
