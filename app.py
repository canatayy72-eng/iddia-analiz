import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Pro Analiz", layout="centered")

# --- SENİN API BİLGİLERİN ---
API_KEY = "480fd0060cmsh368c3cb730d7b33p16a976jsn858f6f07fc47"
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "sofascore.p.rapidapi.com"
}

# --- ANALİZ MOTORU ---
def poisson_analiz(ev_xg, dep_xg):
    ev_probs = poisson.pmf(range(6), ev_xg)
    dep_probs = poisson.pmf(range(6), dep_xg)
    return np.outer(ev_probs, dep_probs)

# --- VERİ ÇEKME FONKSİYONU ---
def son_maclari_getir(team_id):
    url = "https://sofascore.p.rapidapi.com/teams/get-last-matches"
    params = {"teamId": str(team_id), "pageIndex": "0"}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        return response.json().get('events', [])
    except Exception as e:
        return []

# --- ARAYÜZ TASARIMI ---
st.title("⚽ SofaScore AI Analiz")
st.markdown("Takım ID girerek son maç verilerine dayalı **Poisson Analizi** yapın.")

# Takım ID Girişi (Örn: 38 Manchester City, 602 Fenerbahçe)
team_id = st.text_input("Analiz edilecek Takım ID:", "38")

if st.button("📊 Analizi Başlat"):
    with st.spinner('Veriler çekiliyor...'):
        maclar = son_maclari_getir(team_id)
    
    if maclar:
        # Son 5 maçın gollerinden xG tahmini üretme
        ev_skorlar = []
        dep_skorlar = []
        
        for m in maclar[:10]: # Son 10 maçı tara
            if 'homeScore' in m and 'awayScore' in m:
                ev_skorlar.append(m['homeScore'].get('current', 0))
                dep_skorlar.append(m['awayScore'].get('current', 0))
        
        # Ortalama gol beklentisi (xG) hesapla
        ev_xg = sum(ev_skorlar) / len(ev_skorlar) if ev_skorlar else 1.5
        dep_xg = sum(dep_skorlar) / len(dep_skorlar) if dep_skorlar else 1.2
        
        matris = poisson_analiz(ev_xg, dep_xg)
        
        # --- SONUÇ PANELİ ---
        st.success(f"Analiz Tamamlandı! (Son {len(ev_skorlar)} maç baz alındı)")
        
        col1, col2 = st.columns(2)
        
        # 2.5 Üst Hesaplama
        alt_olasilik = (matris[0,0] + matris[0,1] + matris[0,2] + 
                        matris[1,0] + matris[1,1] + matris[2,0])
        ust_25 = (1 - alt_olasilik) * 100
        
        # KG VAR Hesaplama
        kg_yok = matris[0,:].sum() + matris[:,0].sum() - matris[0,0]
        kg_var = (1 - kg_yok) * 100
        
        col1.metric("🔥 2.5 Üst İhtimali", f"%{round(ust_25, 1)}")
        col2.metric("⚽ KG VAR İhtimali", f"%{round(kg_var, 1)}")
        
        # Skor Tablosu
        st.write("### 📊 Olası Skor Dağılımı (%)")
        df_skor = pd.DataFrame(matris[:4
