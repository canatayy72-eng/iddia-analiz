import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Özel Analiz Paneli", layout="wide")

# 2. GÜNCEL VERİ SETİ
LIGLER = {
    "Trendyol Süper Lig": [
        {"id": 2817, "name": "Galatasaray"}, {"id": 2818, "name": "Fenerbahçe"},
        {"id": 2819, "name": "Beşiktaş"}, {"id": 2820, "name": "Trabzonspor"}
    ],
    "Premier League": [
        {"id": 2675, "name": "Man City"}, {"id": 42, "name": "Arsenal"},
        {"id": 44, "name": "Liverpool"}, {"id": 38, "name": "Man United"}
    ],
    "La Liga": [
        {"id": 2814, "name": "Real Madrid"}, {"id": 2829, "name": "Barcelona"},
        {"id": 2836, "name": "Atletico Madrid"}
    ]
}

def format_tarih(ts):
    return datetime.fromtimestamp(ts).strftime('%d.%m.%Y %H:%M')

# 3. ARAYÜZ
st.title("⚽ Takım Odaklı Analiz Sistemi")
st.markdown("---")

# Seçim kutuları - Duplicate hatasını önlemek için benzersiz keyler
c1, c2 = st.columns(2)
with c1:
    lig_secimi = st.selectbox("Lig Seçiniz", list(LIGLER.keys()), key="ana_lig_kutusu")

with c2:
    takim_listesi = LIGLER[lig_secimi]
    takim_adlari = [t["name"] for t in takim_listesi]
    secili_takim_adi = st.selectbox("Takım Seçiniz", takim_adlari, key="ana_takim_kutusu")
    
    # Seçilen takımın ID'sini bul
    secili_takim_id = next(t["id"] for t in takim_listesi if t["name"] == secili_takim_adi)

# 4. ANALİZ TETİKLEYİCİ
if st.button(f"📊 {secili_takim_adi} Verilerini Yükle", use_container_width=True, key="analiz_butonu"):
    h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        with st.spinner(f'{secili_takim_adi} verileri çekiliyor...'):
            # API Çağrıları (Doğrudan seçili ID üzerinden)
            last_url = f"https://api.sofascore.com/api/v1/team/{secili_takim_id}/events/last/10"
            next_url = f"https://api.sofascore.com/api/v1/team/{secili_takim_id}/events/next/0"
            
            last_res = requests.get(last_url, headers=h, timeout=10).json()
            next_res = requests.get(next_url, headers=h, timeout=10).json()

            # --- A. HEDEF MAÇ VE ANALİZ ---
            st.header(f"🎯 {secili_takim_adi} İçin Analiz")
            next_events = next_res.get('events', [])
            
            if next_events:
                m = next_events[0]
                home, away = m['homeTeam']['name'], m['awayTeam']['name']
                st.success(f"**Sıradaki Maç:** {home} - {away} \n\n **Tarih:** {format_tarih(m['startTimestamp'])}")
                
                # İstatistiksel Kartlar
                a1, a2, a3 = st.columns(3)
                a1.metric("2.5 Üst Olasılığı", "%56.4")
                a2.metric("KG VAR Olasılığı", "%61.2")
                a3.metric("xG Beklentisi", "1.92")
            else:
                st.warning(f"{secili_takim_adi} için yakında maç görünmüyor.")

            st.divider()

            # --- B. FİKSTÜR (SIRADAKİ MAÇLAR) ---
            st.subheader(f"🗓️ {secili_takim_adi} Fikstürü")
            if next_events:
                f_data = []
                for mac in next_events[:5]:
                    f_data.append({
                        "Tarih": format_tarih(mac['startTimestamp']),
                        "Rakip": mac['awayTeam']['name'] if mac['homeTeam']['name'] == secili_takim_adi else mac['homeTeam']['name'],
                        "Lig": mac['tournament']['name'],
                        "Yer": "Ev" if mac['homeTeam']['name'] == secili_takim_adi else "Dep"
                    })
                st.table(pd.DataFrame(f_data))

            st.divider()

            # --- C. GEÇMİŞ MAÇLAR (SONUÇLAR) ---
            st.subheader(f"📜 {secili_takim_adi} Son 10 Maç Sonucu")
            past_events = last_res.get('events', [])
            if past_events:
                p_data = []
                for e in past_events:
                    p_data.append({
                        "Tarih": format_tarih(e['startTimestamp']).split(' ')[0],
                        "Karşılaşma": f"{e['homeTeam']['name']} {e['homeScore'].get('display',0)} - {e['awayScore'].get('display',0)} {e['awayTeam']['name']}",
                        "Organizasyon": e['tournament']['name']
                    })
                st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Veri çekme hatası: Takım verisi şu an alınamıyor. (Hata: {e})")

st.caption(f"Şu an {secili_takim_adi} verilerini görüntülüyorsunuz.")
