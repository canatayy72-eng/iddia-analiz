import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pro-Bet AI Analyzer", layout="wide")

# --- FONKSİYONLAR ---
def poisson_hesapla(ev_xg, dep_xg):
    # 0'dan 5 gole kadar olasılık matrisi
    ev_probs = poisson.pmf(range(6), ev_xg)
    dep_probs = poisson.pmf(range(6), dep_xg)
    return np.outer(ev_probs, dep_probs)

def form_puani_ver(son_bes_mac):
    # Örn: ["G", "B", "M", "G", "G"] -> Galibiyet 3, Beraberlik 1, Mağlubiyet 0
    puan = sum([3 if m=="G" else 1 if m=="B" else 0 for m in son_bes_mac])
    # Form katsayısı: 0.9 ile 1.1 arasında bir çarpan üretir
    return 0.9 + (puan / 15) * 0.2

# --- VERİTABANI (HAFIZA) SİMÜLASYONU ---
if 'hafiza' not in st.session_state:
    st.session_state.hafiza = []

# --- ARAYÜZ ---
st.title("🧠 AI Bahis Analiz & Hafıza Merkezi")

with st.sidebar:
    st.header("⚙️ Ayarlar")
    lig_sec = st.selectbox("Lig Seçin", ["Trendyol Süper Lig", "Premier Lig", "La Liga"])
    strateji = st.slider("Risk İştahı (xG Çarpanı)", 0.5, 1.5, 1.0)

# Ana Ekran - Maç Seçimi
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🏟️ Günün Kritik Maçları")
    # Bu veriler normalde API'den gelecek, şimdilik simüle ediyoruz
    mac_verisi = {
        "Fenerbahçe - Pendikspor": {"ev_xg": 2.4, "dep_xg": 0.8, "ev_form": ["G", "G", "B", "G", "M"]},
        "Liverpool - Man City": {"ev_xg": 1.9, "dep_xg": 1.8, "ev_form": ["G", "G", "G", "B", "G"]}
    }
    
    secilen_mac = st.selectbox("Maç Seçin", list(mac_verisi.keys()))
    m_detay = mac_verisi[secilen_mac]
    
    # Form ve Sakatlık Etkisini Uygula
    f_katsayi = form_puani_ver(m_detay["ev_form"])
    final_ev_xg = m_detay["ev_xg"] * f_katsayi * strateji
    
    # Analiz Sonuçları
    matris = poisson_hesapla(final_ev_xg, m_detay["dep_xg"])
    
    st.write(f"### 📊 {secilen_mac} Analizi")
    c1, c2, c3 = st.columns(3)
    c1.metric("Ev Sahibi Gücü", round(final_ev_xg, 2))
    c2.metric("Deplasman Gücü", round(m_detay["dep_xg"], 2))
    
    # Alt/Üst Olasılığı
    ust_25 = (1 - (matris[0,0] + matris[0,1] + matris[0,2] + matris[1,0] + matris[1,1] + matris[2,0])) * 100
    c3.metric("2.5 Üst İhtimali", f"%{round(ust_25, 1)}")

    if st.button("📌 Bu Maçı Hafızaya Ekle"):
        st.session_state.hafiza.append({
            "mac": secilen_mac,
            "tahmin": "2.5 Üst" if ust_25 > 55 else "Alt / Taraf",
            "oran": round(ust_25, 1)
        })
        st.toast("Hafızaya kaydedildi!", icon="🧠")

with col2:
    st.subheader("🧠 Kayıtlı Hafıza")
    if st.session_state.hafiza:
        for item in st.session_state.hafiza:
            st.warning(f"**{item['mac']}**\n\nBeklenti: {item['tahmin']} (%{item['oran']})")
    else:
        st.write("Henüz bir maç kaydetmedin.")

# Isı Haritası (Görsel Analiz)
st.write("### 🌡️ Skor Olasılık Isı Haritası")
df_map = pd.DataFrame(matris[:4, :4]) # İlk 4 gol olasılığı
st.table(df_map.style.background_gradient(cmap='Greens'))