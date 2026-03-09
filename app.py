import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Analiz Pro", layout="centered")

# --- ANALİZ MOTORU ---
def poisson_hesapla(ev_xg, dep_xg):
    # 0-5 gol arası olasılıkları hesaplar
    ev_probs = poisson.pmf(range(6), ev_xg)
    dep_probs = poisson.pmf(range(6), dep_xg)
    return np.outer(ev_probs, dep_probs)

# --- HAFIZA SİSTEMİ ---
if 'hafiza' not in st.session_state:
    st.session_state.hafiza = []

# --- ARAYÜZ ---
st.title("⚽ Pro Analiz & Hafıza")
st.markdown("Veriler **Poisson Dağılımı** ile hesaplanmaktadır.")

# Örnek Maç Verileri
mac_verisi = {
    "Fenerbahçe - Galatasaray": {"ev_xg": 1.8, "dep_xg": 1.4},
    "Real Madrid - Barcelona": {"ev_xg": 2.1, "dep_xg": 1.9},
    "Liverpool - Man City": {"ev_xg": 1.7, "dep_xg": 1.7},
    "Bayern Münih - Dortmund": {"ev_xg": 2.4, "dep_xg": 1.1}
}

secilen_mac = st.selectbox("Analiz edilecek maçı seçin:", list(mac_verisi.keys()))

if secilen_mac:
    m_detay = mac_verisi[secilen_mac]
    ev_xg, dep_xg = m_detay["ev_xg"], m_detay["dep_xg"]
    
    matris = poisson_hesapla(ev_xg, dep_xg)
    
    # 1. Özet Bilgiler
    st.info(f"**Maç:** {secilen_mac} | **xG Beklentisi:** {ev_xg} - {dep_xg}")
    
    c1, c2 = st.columns(2)
    # 2.5 Üst Olasılığı (0, 1 ve 2 gollü tüm skorları çıkarıyoruz)
    alt_skorlar = (matris[0,0] + matris[0,1] + matris[0,2] + 
                   matris[1,0] + matris[1,1] + matris[2,0])
    ust_25 = (1 - alt_skorlar) * 100
    
    # KG VAR Olasılığı
    kg_yok = matris[0,:].sum() + matris[:,0].sum() - matris[0,0]
    kg_var = (1 - kg_yok) * 100
    
    c1.metric("2.5 Üst Olasılığı", f"%{round(ust_25, 1)}")
    c2.metric("KG VAR Olasılığı", f"%{round(kg_var, 1)}")

    # 2. Skor Tablosu
    st.write("### 📊 Skor Olasılık Tablosu (%)")
    df_map = pd.DataFrame(matris[:4, :4]) 
    df_map.columns = [f"D {i}" for i in range(4)]
    df_map.index = [f"E {i}" for i in range(4)]
    
    # Tabloyu yüzde olarak ve temiz bir görünümle göster
    st.dataframe(df_map.style.format("{:.1%}"), use_container_width=True)

    # 3. Hafıza Bölümü
    st.divider()
    st.subheader("🧠 Kişisel Hafıza")
    not_al = st.text_area("Bu maç için notun:", placeholder="Önemli istatistikleri buraya yaz...")
    
    if st.button("📌 Notu Hafızaya Kaydet"):
        if not_al:
            st.session_state.hafiza.append({"mac": secilen_mac, "not": not_al})
            st.toast("Kaydedildi!", icon="✅")
        else:
            st.warning("Lütfen bir not yazın.")

    if st.session_state.hafiza:
        st.write("---")
        for h in reversed(st.session_state.hafiza):
            with st.expander(f"📌 {h['mac']}"):
                st.write(h['not'])
