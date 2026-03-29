import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Emissioni Pro - Full Suite", layout="wide")

# CSS Personalizzato
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-header { font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .stButton>button { width: 100%; height: 50px; font-weight: bold; border-radius: 10px; }
    .result-card { background-color: #f0f7ff; padding: 20px; border-radius: 15px; border: 1px solid #007bff; margin-bottom: 20px; }
    .metric-title { font-size: 13px; color: #555; font-weight: bold; }
    .metric-value { font-size: 19px; font-weight: bold; color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIONE SESSION STATE (MEMORIA APP) ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'dati_anagrafica' not in st.session_state: st.session_state.dati_anagrafica = {}
if 'risultati_fumi' not in st.session_state: st.session_state.risultati_fumi = {}
if 'lista_operatori' not in st.session_state: st.session_state.lista_operatori = ["Tecnico 1", "Tecnico 2"]

def nav(page_name):
    st.session_state.page = page_name

# --- NAVBAR LATERALE ---
with st.sidebar:
    st.title("🚀 Navigation")
    if st.button("🏠 Home"): nav('home')
    if st.button("🗂️ Dati Generali"): nav('dati')
    if st.button("📏 Dinamica Fumi"): nav('fumi')
    if st.button("💉 Campionamento"): nav('camp')
    if st.button("🧪 Laboratorio"): nav('lab')
    if st.button("📄 Report Finale"): nav('report')

# --- 0. HOME PAGE ---
if st.session_state.page == 'home':
    st.markdown("<p class='main-header'>🏭 Sistema Gestione Emissioni v2.5</p>", unsafe_allow_html=True)
    st.write("Benvenuto nel software gestionale per il campionamento isocinetico.")
    col1, col2 = st.columns(2)
    with col1:
        st.info("Inizia configurando i **Dati Generali** della ditta.")
        if st.button("Vai a Dati Generali"): nav('dati')
    with col2:
        st.success("Esegui i calcoli preliminari nella sezione **Dinamica**.")
        if st.button("Vai a Dinamica Fumi"): nav('fumi')

# --- 1. DATI GENERALI ---
elif st.session_state.page == 'dati':
    st.header("🗂️ Dati Generali e Anagrafica")
    with st.form("form_dati"):
        c1, c2 = st.columns(2)
        with c1:
            ditta = st.text_input("Ditta Cliente", value=st.session_state.dati_anagrafica.get('ditta', ''))
            impianto = st.text_input("Impianto / Camino", value=st.session_state.dati_anagrafica.get('impianto', ''))
        with c2:
            data_test = st.date_input("Data Campionamento")
            operatori = st.multiselect("Team Tecnico", options=st.session_state.lista_operatori, default=st.session_state.lista_operatori[:1])
        
        if st.form_submit_button("💾 Salva Anagrafica"):
            st.session_state.dati_anagrafica = {'ditta': ditta, 'impianto': impianto, 'data': data_test, 'operatori': operatori}
            st.success("Dati salvati!")

# --- 2. DINAMICA FUMI (VERSIONE CORRETTA) ---
elif st.session_state.page == 'fumi':
    st.header("📏 Dinamica dei Fumi (Misure Preliminari)")
    c_in, c_tab = st.columns([1, 2.2])

    with c_in:
        d_camino = st.number_input("Diametro Camino (m)", value=1.4, format="%.3f")
        t_fumi = st.number_input("Temperatura Fumi (°C)", value=259.0)
        k_pit = st.number_input("Costante Pitot (K)", value=0.69)
        p_atm = st.number_input("Pressione Atm (hPa)", value=1013.25)
        p_stat = st.number_input("Pressione Statica (Pa)", value=-10.0)
        st.write("---")
        o2_mis = st.number_input("O2 misurato (%)", value=14.71)
        co2_mis = st.number_input("CO2 misurata (%)", value=5.95)
        h_in = st.number_input("Umidità (%)", value=4.68)
        o2_rif = st.number_input("O2 Riferimento (%)", value=8.0)

    with c_tab:
        unita = st.radio("Unità ΔP:", ["mmH2O", "Pa"], horizontal=True)
        df_dp = pd.DataFrame({"Punto": ["P1","P2","P3","P4"], "ΔP": [26.6, 26.6, 26.6, 26.6]})
        edit_df = st.data_editor(df_dp, hide_index=True, use_container_width=True)
        
        # Calcoli
        vals = edit_df["ΔP"].tolist()
        dp_pa = (sum(vals)/len(vals)) * 9.80665 if unita == "mmH2O" else (sum(vals)/len(vals))
        p_ass = p_atm + (p_stat/100)
        
        # Chimica e Densità
        ms = (co2_mis * 44.01 + o2_mis * 31.999 + (100-o2_mis-co2_mis)*28.013)/100
        mu = ms * (1 - h_in/100) + 18.015 * (h_in/100)
        rho = (p_ass * 100 * mu) / (8314.47 * (t_fumi + 273.15))
        v = np.sqrt((2 * dp_pa * k_pit) / rho)
        
        # Portate
        area = (np.pi * d_camino**2) / 4
        q_aq = v * area * 3600
        q_un_u = q_aq * (273.15/(t_fumi+273.15)) * (p_ass/1013.25)
        q_un_s = q_un_u * (1 - h_in/100)
        # Portata Riferita (Formula Corretta: divide per il salto di O2)
        q_rif = q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif))

        # Box Risultati
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        res1, res2, res3 = st.columns(3)
        res1.markdown(f"<p class='metric-title'>Densità Reale</p><p class='metric-value'>{rho:.4f} kg/m³</p>", unsafe_allow_html=True)
        res1.markdown(f"<p class='metric-title'>Portata Tal Quale</p><p class='metric-value'>{q_aq:.0f} Am³/h</p>", unsafe_allow_html=True)
        res2.markdown(f"<p class='metric-title'>Velocità Media</p><p class='metric-value'>{v:.2f} m/s</p>", unsafe_allow_html=True)
        res2.markdown(f"<p class='metric-title'>Portata N. Umida</p><p class='metric-value'>{q_un_u:.0f} Nm³/h</p>", unsafe_allow_html=True)
        res3.markdown(f"<p class='metric-title'>Portata N. Secca</p><p class='metric-value'>{q_un_s:.0f} Nm³/h</p>", unsafe_allow_html=True)
        res3.markdown(f"<p class='metric-title' style='color:#28a745'>PORTATA RIFERITA</p><p class='metric-value' style='color:#28a745'>{q_rif:.0f} Nm³/h</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("🎯 Calcolo Isocinetismo")
        u_col1, u_col2 = st.columns(2)
        d_ug = u_col1.number_input("Ugello (mm)", value=5.0)
        t_c = u_col1.number_input("T. Contatore (°C)", value=20.0)
        q_p = (v * (np.pi * (d_ug/2000)**2) * 60000) * ((t_c+273.15)/(t_fumi+273.15)) * (p_ass/1013.25)
        u_col2.metric("FLUSSO POMPA TARGET", f"{q_p:.2f} l/min")
        
        if st.button("💾 Salva Dati Dinamica"):
            st.session_state.risultati_fumi = {'v': v, 'q_rif': q_rif, 'rho': rho, 'q_un_s': q_un_s}
            st.success("Calcoli salvati!")

# --- 3. CAMPIONAMENTO ---
elif st.session_state.page == 'camp':
    st.header("💉 Gestione Campionamenti")
    st.write("In questa sezione potrai gestire i singoli prelievi.")
    tab1, tab2 = st.tabs(["Campionamento 1", "Campionamento 2"])
    with tab1:
        st.selectbox("Sostanza", ["Polveri", "Metalli", "HCl", "HF", "TOC"])
        st.number_input("Volume Aspirato (litri)", value=0.0)
        st.number_input("Tempo Totale (min)", value=30)
        st.button("Salva Prova 1")

# --- 4. LABORATORIO ---
elif st.session_state.page == 'lab':
    st.header("🧪 Dati di Laboratorio")
    st.write("Inserimento concentrazioni analitiche.")
    with st.expander("Metalli (Esempio)", expanded=True):
        st.number_input("Massa rilevata (mg)", value=0.0, step=0.01)
        st.number_input("Volume Soluzione (ml)", value=100)

# --- 5. REPORT FINALE ---
elif st.session_state.page == 'report':
    st.header("📄 Report di Sintesi")
    if not st.session_state.risultati_fumi:
        st.warning("Esegui prima i calcoli nella sezione Dinamica.")
    else:
        st.subheader("Riepilogo Parametri Camino")
        rep_data = {
            "Parametro": ["Ditta", "Camino", "Velocità Media", "Densità Reale", "Portata Secca Norm.", "Portata Riferita"],
            "Valore": [
                st.session_state.dati_anagrafica.get('ditta', '-'),
                st.session_state.dati_anagrafica.get('impianto', '-'),
                f"{st.session_state.risultati_fumi['v']:.2f} m/s",
                f"{st.session_state.risultati_fumi['rho']:.4f} kg/m³",
                f"{st.session_state.risultati_fumi['q_un_s']:.0f} Nm³/h",
                f"{st.session_state.risultati_fumi['q_rif']:.0f} Nm³/h"
            ]
        }
        st.table(pd.DataFrame(rep_data))
        st.button("📥 Esporta in PDF (Simulato)")
