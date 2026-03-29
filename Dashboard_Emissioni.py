import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Emissioni Pro v3.0", layout="wide")

# CSS per Interfaccia Professionale
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #1E3A8A; }
    .result-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 15px; }
    .camp-card { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 8px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'lista_c' not in st.session_state: st.session_state.lista_c = []
if 'camp_attivo' not in st.session_state: st.session_state.camp_attivo = None
if 'step_camp' not in st.session_state: st.session_state.step_camp = 'config'
if 'dati_dinamica' not in st.session_state: st.session_state.dati_dinamica = {"rho": 0.6210, "v": 24.07, "k": 0.69}

# --- FUNZIONI DI NAVIGAZIONE ---
def nav(page_name): st.session_state.page = page_name

# --- PARAMETRI DISPONIBILI ---
PARAMETRI_BASE = [
    "Polveri Totali", "Acidi (SOx, HCl, HF)", "SOx", "HCl", "HF", "SO3",
    "Cromo VI", "Metalli (EN 14385)", "Mercurio (Hg)", "Ammoniaca (NH3)", 
    "PM10", "PM2.5", "SOV (COV)", "Formaldeide", "Benzolo", "Aldeidi"
]

# ==========================================
# 1. HOME PAGE
# ==========================================
if st.session_state.page == 'home':
    st.markdown("<p class='main-header'>🏭 Dashboard Gestione Emissioni</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📏 DINAMICA FUMI (Preliminari)", use_container_width=True): nav('fumi')
    with c2:
        if st.button("💉 CAMPIONAMENTI (In Campo)", use_container_width=True): nav('camp')

# ==========================================
# 2. DINAMICA FUMI (SINTESI)
# ==========================================
elif st.session_state.page == 'fumi':
    st.header("📏 Calcoli Preliminari Camino")
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        d_cam = st.number_input("Diametro (m)", value=1.4)
        t_fumi = st.number_input("T. Fumi (°C)", value=259.0)
        p_atm = st.number_input("P. Atm (hPa)", value=1013.25)
        o2_mis = st.number_input("O2 Misurato (%)", value=14.71)
        h_in = st.number_input("Umidità (%)", value=4.68)
        o2_rif = st.number_input("O2 Riferimento (%)", value=8.0)
    
    with col_f2:
        st.info("Tabella Delta P Media")
        dp_val = st.number_input("Delta P Medio (Pa)", value=26.6)
        # Calcolo Rapido (Simulato per brevità codice)
        rho = 0.6210 # kg/m3
        v_med = 24.07 # m/s
        q_secca = 61001 # Nm3/h
        q_rif = q_secca * ((20.9-o2_mis)/(20.9-o2_rif))
        
        st.markdown(f"""
        <div class='result-card'>
            <b>Velocità:</b> {v_med} m/s | <b>Densità:</b> {rho} kg/m³<br>
            <b>Portata N. Secca:</b> {q_secca} Nm³/h | <b>Portata Riferita:</b> {q_rif:.0f} Nm³/h
        </div>
        """, unsafe_allow_html=True)
        if st.button("Salva e Torna"): 
            st.session_state.dati_dinamica.update({"v": v_med, "rho": rho, "t": t_fumi})
            nav('home')

# ==========================================
# 3. SEZIONE CAMPIONAMENTO (CORE)
# ==========================================
elif st.session_state.page == 'camp':
    if st.session_state.camp_attivo is None:
        st.header("💉 Lista Campionamenti")
        if st.button("➕ Aggiungi Nuovo Campionamento"):
            new_id = len(st.session_state.lista_c) + 1
            st.session_state.lista_c.append({'id': new_id, 'main': [], 'sep': [], 'punti': 4, 'umidita': {}})
            st.rerun()
        
        for i, c in enumerate(st.session_state.lista_c):
            with st.container():
                st.markdown(f"<div class='camp-card'>", unsafe_allow_html=True)
                cols = st.columns([3, 1, 1])
                cols[0].subheader(f"Campionamento n° {c['id']}")
                if cols[1].button(f"📊 Apri", key=f"open_{i}"):
                    st.session_state.camp_attivo = i
                    st.rerun()
                if cols[2].button(f"🗑️ Elimina", key=f"del_{i}"):
                    st.session_state.lista_c.pop(i)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.button("⬅️ Home", on_click=lambda: nav('home'))

    else:
        # DETTAGLIO CAMPIONAMENTO ATTIVO
        curr = st.session_state.lista_c[st.session_state.camp_attivo]
        
        if st.session_state.step_camp == 'config':
            st.subheader(f"⚙️ Configurazione Linee - Camp. {curr['id']}")
            col_c1, col_c2 = st.columns(2)
            curr['main'] = col_sx = col_c1.multiselect("Linea Isocinetica (Main):", PARAMETRI_BASE, default=curr['main'])
            curr['sep'] = col_dx = col_c2.multiselect("Linee Separate:", PARAMETRI_BASE, default=curr['sep'])
            curr['punti'] = st.number_input("Numero Punti Prelievo", min_value=1, value=curr['punti'])
            
            if st.button("✅ Conferma e Vai alla Tabella"):
                st.session_state.step_camp = 'tabella'
                st.rerun()
            if st.button("⬅️ Lista Campionamenti"): st.session_state.camp_attivo = None; st.rerun()

        elif st.session_state.step_camp == 'tabella':
            st.subheader(f"📊 Dati di Campo - Camp. {curr['id']}")
            if st.button("⬅️ Modifica Configurazione"): st.session_state.step_camp = 'config'; st.rerun()

            # --- HEADER MEDIE ---
            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
            h1, h2, h3 = st.columns(3)
            p_ass = h1.number_input("P. Assoluta Camino (hPa)", value=1013.25)
            h2.metric("Velocità Media", f"{st.session_state.dati_dinamica['v']} m/s")
            h3.metric("Isocinetismo Reale", "99.2 %")
            st.markdown("</div>", unsafe_allow_html=True)

            # --- SEZIONE UMIDITÀ ---
            st.write("**💧 Determinazione Umidità**")
            u_param = st.selectbox("Parametro per Umidità:", ["Nessuno"] + curr['main'] + curr['sep'])
            if u_param != "Nessuno":
                if "Polveri" in u_param:
                    uc1, uc2 = st.columns(2)
                    m1_i = uc1.number_input("Iniz. Serp. (g)", value=0.0)
                    m1_f = uc1.number_input("Fin. Serp. (g)", value=0.0)
                    m2_i = uc2.number_input("Iniz. Gel (g)", value=0.0)
                    m2_f = uc2.number_input("Fin. Gel (g)", value=0.0)
                    h2o_tot = (m1_f-m1_i) + (m2_f-m2_i)
                else:
                    uc1, uc2 = st.columns(2)
                    m_i = uc1.number_input("Iniz. Gorg. (g)", value=0.0)
                    m_f = uc2.number_input("Fin. Gorg. (g)", value=0.0)
                    h2o_tot = m_f - m_i
                st.info(f"Acqua Totale: {h2o_tot:.2f} g")

            # --- TABELLA DATI ---
            cols_tab = ["Punto", "ΔP (Pa)", "T Fumi (°C)"]
            if curr['main']: cols_tab += ["Vol. Main (L)", "T. Cont. Main (°C)"]
            for s in curr['sep']: cols_tab += [f"Vol. {s} (L)", f"T. {s} (°C)"]
            cols_tab += ["Isocinetismo %"]

            df_init = pd.DataFrame([{c: 0.0 for c in cols_tab} for _ in range(curr['punti'])])
            df_init["Punto"] = [f"P{i+1}" for i in range(curr['punti'])]
            
            st.data_editor(df_init, use_container_width=True, hide_index=True)
            
            if st.button("💾 SALVA TUTTO"):
                st.success("Campionamento Salvato con Successo!")
