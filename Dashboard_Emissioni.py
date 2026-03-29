import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v3.5 - FULL", layout="wide")

# CSS per Interfaccia
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E3A8A; }
    .result-card { background-color: #f0f7ff; padding: 20px; border-radius: 15px; border: 1px solid #007bff; margin-bottom: 20px; }
    .metric-value { font-size: 20px; font-weight: bold; color: #1E3A8A; }
    .camp-container { border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; background-color: white; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'dati_anagrafica' not in st.session_state: st.session_state.dati_anagrafica = {'tecnici': []}
if 'dati_dinamica' not in st.session_state: st.session_state.dati_dinamica = {}
if 'lista_c' not in st.session_state: st.session_state.lista_c = []
if 'camp_attivo' not in st.session_state: st.session_state.camp_attivo = None
if 'step_camp' not in st.session_state: st.session_state.step_camp = 'selezione'

PARAMETRI_BASE = [
    "Polveri Totali", "Acidi (SOx, HCl, HF)", "SOx", "HCl", "HF", "SO3",
    "Cromo VI", "Metalli (EN 14385)", "Mercurio (Hg)", "Ammoniaca (NH3)", 
    "PM10", "PM2.5", "SOV (COV)", "Formaldeide", "Benzolo", "Aldeidi"
]

def nav(p): st.session_state.page = p

# --- SIDEBAR ---
with st.sidebar:
    st.title("📑 MENU PRINCIPALE")
    if st.button("🏠 Home"): nav('home')
    if st.button("🗂️ Dati Generali & Tecnici"): nav('anagrafica')
    if st.button("📐 Dinamica Fumi"): nav('fumi')
    if st.button("💉 Campionamenti"): nav('camp')
    if st.button("📄 Report Finale (RdP)"): nav('rdp')

# ==========================================
# 1. DATI GENERALI & TECNICI
# ==========================================
if st.session_state.page == 'anagrafica':
    st.header("🗂️ Dati Generali e Team Tecnico")
    with st.form("anag_form"):
        st.session_state.dati_anagrafica['ditta'] = st.text_input("Ditta Cliente", st.session_state.dati_anagrafica.get('ditta',''))
        st.session_state.dati_anagrafica['camino'] = st.text_input("Nome Camino", st.session_state.dati_anagrafica.get('camino',''))
        
        st.write("---")
        tecnici_str = st.text_area("Tecnici Operanti (uno per riga)", value="\n".join(st.session_state.dati_anagrafica.get('tecnici', [])))
        
        if st.form_submit_button("💾 Salva Dati"):
            st.session_state.dati_anagrafica['tecnici'] = tecnici_str.split("\n")
            st.success("Dati Generali e Team salvati!")

# ==========================================
# 2. DINAMICA FUMI
# ==========================================
elif st.session_state.page == 'fumi':
    st.header("📐 Dinamica dei Fumi (Calcoli ISO 16911)")
    c1, c2 = st.columns([1, 2])
    
    with c1:
        d_cam = st.number_input("Diametro Camino (m)", value=1.4, format="%.3f")
        # Logica Punti Automatica
        if d_cam <= 0.35: n_default = 1
        elif d_cam <= 1.1: n_default = 4
        elif d_cam <= 1.5: n_default = 8
        else: n_default = 12
        
        n_punti_fumi = st.number_input("Punti di misura Delta P", value=n_default)
        t_fumi = st.number_input("T. Fumi (°C)", value=259.0)
        k_pit = st.number_input("K Pitot", value=0.69)
        p_atm = st.number_input("P. Atm (hPa)", value=1013.25)
        p_stat = st.number_input("P. Statica (Pa)", value=-10.0)
        o2_mis = st.number_input("O2 misurata (%)", value=14.71)
        h_in = st.number_input("Umidità (%)", value=4.68)
        o2_rif = st.number_input("O2 riferimento (%)", value=8.0)

    with c2:
        st.subheader("Inserimento Mappatura ΔP")
        df_dp = pd.DataFrame({"Punto": [f"P{i+1}" for i in range(n_punti_fumi)], "ΔP (Pa)": [26.6]*n_punti_fumi})
        edit_dp = st.data_editor(df_dp, hide_index=True, use_container_width=True)
        
        dp_med = edit_dp["ΔP (Pa)"].mean()
        p_ass = p_atm + (p_stat/100)
        
        # Motore di Calcolo Fisico
        rho_fumi = 0.621 # kg/m3 (Dato utente fisso per coerenza con calcoli precedenti)
        v_fumi = np.sqrt((2 * dp_med * k_pit) / rho_fumi)
        area = (np.pi * d_cam**2) / 4
        
        q_aq = v_fumi * area * 3600
        q_un_u = q_aq * (273.15/(t_fumi+273.15)) * (p_ass/1013.25)
        q_un_s = q_un_u * (1 - h_in/100)
        q_rif = q_un_s * ((20.9 - o2_mis)/(20.9 - o2_rif))

        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        r1.markdown(f"**Velocità:** {v_fumi:.2f} m/s<br>**Portata Tal Quale:** {q_aq:.0f} Am³/h<br>**Portata N. Umida:** {q_un_u:.0f} Nm³/h", unsafe_allow_html=True)
        r2.markdown(f"**Portata N. Secca:** {q_un_s:.0f} Nm³/h<br><span style='color:green; font-size:20px;'><b>PORTATA RIFERITA: {q_rif:.0f} Nm³/h</b></span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("💾 Salva Dinamica"):
            st.session_state.dati_dinamica = {'v': v_fumi, 'q_rif': q_rif, 'p_ass': p_ass, 'h_in': h_in, 't_fumi': t_fumi}
            st.success("Dati dinamica archiviati correttamente.")

# ==========================================
# 3. CAMPIONAMENTI
# ==========================================
elif st.session_state.page == 'camp':
    if st.session_state.camp_attivo is None:
        st.header("💉 Gestione Campionamenti")
        if st.button("➕ AGGIUNGI CAMPIONAMENTO", use_container_width=True):
            st.session_state.lista_c.append({'id': len(st.session_state.lista_c)+1, 'main': [], 'sep': [], 'punti': 4})
            st.rerun()
        
        for i, c in enumerate(st.session_state.lista_c):
            with st.container():
                st.markdown(f"<div class='camp-container'>", unsafe_allow_html=True)
                ca1, ca2, ca3 = st.columns([4, 1, 1])
                ca1.write(f"### 📦 Campionamento n° {c['id']}")
                if ca2.button("📊 APRI", key=f"open_{i}"):
                    st.session_state.camp_attivo = i
                    st.session_state.step_camp = 'selezione'; st.rerun()
                if ca3.button("🗑️ ELIMINA", key=f"del_{i}"):
                    st.session_state.lista_c.pop(i); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        idx = st.session_state.camp_attivo
        curr = st.session_state.lista_c[idx]

        if st.session_state.step_camp == 'selezione':
            st.subheader(f"⚙️ Selezione Parametri - Campionamento {curr['id']}")
            
            st.write("#### 🟦 LINEA ISOCINETICA (Unica)")
            m_cols = st.columns(4)
            for j, p in enumerate(PARAMETRI_BASE):
                with m_cols[j % 4]:
                    if st.checkbox(p, key=f"m_{idx}_{p}", value=(p in curr['main'])):
                        if p not in curr['main']: curr['main'].append(p)
                    else:
                        if p in curr['main']: curr['main'].remove(p)
            
            st.write("#### 🟧 LINEE SEPARATE / DERIVATE")
            s_cols = st.columns(4)
            for j, p in enumerate(PARAMETRI_BASE):
                with s_cols[j % 4]:
                    if st.checkbox(p, key=f"s_{idx}_{p}", value=(p in curr['sep'])):
                        if p not in curr['sep']: curr['sep'].append(p)
                    else:
                        if p in curr['sep']: curr['sep'].remove(p)

            curr['punti'] = st.number_input("Punti Campionamento", min_value=1, value=curr['punti'])
            if st.button("✅ CONFERMA E VAI ALLA TABELLA"): st.session_state.step_camp = 'tabella'; st.rerun()

        elif st.session_state.step_camp == 'tabella':
            st.subheader(f"📊 Dati Campo - Camp. {curr['id']}")
            if st.button("⬅️ MODIFICA SELEZIONE"): st.session_state.step_camp = 'selezione'; st.rerun()

            # Umidità
            st.write("### 💧 Umidità specifica")
            u_sel = st.selectbox("Parametro per Umidità:", ["Dinamica"] + curr['main'] + curr['sep'])
            if u_sel != "Dinamica":
                if "Polveri" in u_sel:
                    u1, u2 = st.columns(2)
                    m1_i = u1.number_input("Serp. Iniziale (g)", 0.0); m1_f = u1.number_input("Serp. Finale (g)", 0.0)
                    m2_i = u2.number_input("Gel Iniziale (g)", 0.0); m2_f = u2.number_input("Gel Finale (g)", 0.0)
                else:
                    u1, u2 = st.columns(2)
                    mi = u1.number_input("Gorg. Iniziali (g)", 0.0); mf = u2.number_input("Gorg. Finali (g)", 0.0)

            # Tabella
            st.write("### 📝 Tabella di Marcia")
            cols = ["Punto", "ΔP (Pa)", "T Fumi (°C)"]
            if curr['main']: cols += ["Vol. Main (L)", "T. Main (°C)"]
            for s in curr['sep']: cols += [f"Vol. {s} (L)", f"T. {s} (°C)"]
            cols += ["Isocinetismo %"]
            
            df_c = pd.DataFrame([{c: 0.0 for c in cols} for _ in range(curr['punti'])])
            df_c["Punto"] = [f"P{k+1}" for k in range(curr['punti'])]
            st.data_editor(df_c, use_container_width=True, hide_index=True)

# ==========================================
# 4. HOME & RDP
# ==========================================
elif st.session_state.page == 'home':
    st.markdown("<p class='main-header'>🏭 Emissioni Pro v3.5</p>", unsafe_allow_html=True)
    st.write("Benvenuto nel sistema completo.")
elif st.session_state.page == 'rdp':
    st.header("📄 Rapporto di Prova")
    st.write(f"Ditta: {st.session_state.dati_anagrafica.get('ditta')}")
    st.write(f"Tecnici: {', '.join(st.session_state.dati_anagrafica.get('tecnici', []))}")
