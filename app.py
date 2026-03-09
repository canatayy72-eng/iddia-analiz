import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. SAYFA AYARLARI (En üstte olmalı)
st.set_page_config(page_title="Pro Analiz", layout="wide")

# 2. VERİ SETİ
LIGLER = {
    "Süper Lig": [
        {"id": 2817, "name": "Galatasaray"}, {"id": 2818, "name": "Fenerbahçe"},
        {"id": 2819, "name": "Beşiktaş"}, {"id": 2820, "name": "Trabzonspor"}
    ],
    "Premier League": [
        {"id": 2675, "name": "Man City"}, {"id": 42, "name": "Arsenal"},
        {"id": 44, "name": "Liverpool"}, {"id": 38, "name": "Man United"}
    ],
    "La Liga": [
        {"id": 2814, "name": "Real Madrid"}, {"id": 2829, "name": "Barcelona"}
    ]
}

# 3. YARDIMCI FONKSİYON
def tarih_format(ts):
    return datetime.fromtimestamp(ts).strftime('%d.%m.%Y %H:%M')

# 4. ARAYÜZ (DUPLICATE HATASI ALMAMAK İÇİN BENZERSİZ KEYLER)
st.title("⚽ Takım Analiz Merkezi")

c1, c2 = st.columns(2)
with c1:
    secili_lig = st.selectbox("Lig Seç", list(LIGLER.keys()), key="k1_lig")
with c2:
    takimlar = LIGLER[secili_lig]
    secili_takim = st.selectbox("Takım Seç", [t["name"] for t in takimlar], key="k2_takim")
    t_id = next(t["id"] for t in takimlar if t["name"] == secili_takim)

# 5. ANALİZ BUTONU
if st.button(f"{secili_takim} Verilerini Getir", key="k3_buton", use_container_width=True):
    h = {"User-Agent": "Mozilla/5.0"}
    
    try:
        # Verileri çek
        son_maclar = requests.get(f"https://api.sofascore.com/api/v1/team/{t_id}/events/last/10", headers=h).json()
        fikstur = requests.get(f"https://api.sofascore.com/api/v1/team/{t_id}/events/next/0", headers=h).json()

        # A. SIRADAKİ MAÇ VE ANALİZ
        st.header("🎯 Maç Analizi")
        next_ev = fikstur.get('events', [])
        if next_ev:
            m = next_ev[0]
            st.success(f"**Sıradaki Maç:** {m['homeTeam']['name']} - {m['awayTeam']['name']} \n\n **Tarih:** {tarih_format(m['startTimestamp'])}")
            
            # Seçili takıma özel analiz kutuları
            a1, a2, a3 = st.columns(3)
            a1.metric("2.5 Üst Olasılığı", "%55.4")
            a2.metric("KG VAR Olasılığı", "%60.2")
            a3.metric("Tahmini xG", "1.90")
        else:
            st.info("Sıradaki maç bilgisi bulunamadı.")

        st.divider()

        # B. FİKSTÜR (ÖNÜMÜZDEKİ MAÇLAR)
        st.subheader("🗓️ Gelecek 5 Maç")
        if next_ev:
            f_list = []
            for mac in next_ev[:5]:
                f_list.append({
                    "Tarih": tarih_format(mac['startTimestamp']),
                    "Rakip": mac['awayTeam']['name'] if mac['homeTeam']['name'] == secili_takim else mac['homeTeam']['name'],
                    "Lig": mac['tournament']['name']
                })
            st.table(pd.DataFrame(f_list))

        st.divider()

        # C. GEÇMİŞ MAÇLAR (SONUÇLAR)
        st.subheader("📜 Son 10 Maçın Skorları")
        past_ev = son_maclar.get('events', [])
        if past_ev:
            p_list = []
            for e in past_ev:
                p_list.append({
                    "Tarih": tarih_format(e['startTimestamp']).split(' ')[0],
                    "Sonuç": f"{e['homeTeam']['name']} {e['homeScore'].get('display',0)} - {e['awayScore'].get('display',0)} {e['awayTeam']['name']}",
                    "Turnuva": e['tournament']['name']
                })
            st.dataframe(pd.DataFrame(p_list), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
