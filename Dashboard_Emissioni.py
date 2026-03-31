import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v3.8 - Ripristino Funzioni", layout="wide")

# --- INIZIALIZZAZIONE DATI ---
if 'suite' not in st.session_state: st.session_state.suite = 'home'
if 'page' not in st.session_state: st.session_state.page = 'home'

if 'dati_dinamica' not in st.session_state: 
    st.session_state.dati_dinamica = {
        'h_in': 4.68, 't_fumi': 259.0, 'p_atm': 1013.25, 'p_stat_pa': -10.0,
        'o2_mis': 14.71, 'o2_rif': 8.0, 'co2': 12.0, 'd_cam': 1.4, 'k_pit': 0.69,
        't_amb': 20.0, 'd_ugello_test': 6.0
    }

# --- CSS ESSENZIALE (BIANCO & NERO) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    
    .section-title { 
        font-size: 2rem; font-weight: 800; color: #000000; 
        border-left: 8px solid #2563eb; padding-left: 15px; margin-bottom: 20px; 
    }

    .res-box { 
        background-color: #F8F9FA; color: #000000;
        padding: 15px; border-radius: 10px; border: 1px solid #DEE2E6;
        text-align: center; margin-bottom: 10px;
    }
    
    .res-val { font-size: 1.8rem; font-weight: 900; color: #2563eb; margin: 0; }
    .res-lab { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #6C757D; }

    /* Input più visibili */
    .stNumberInput label { font-weight: 700 !important; color: #000000 !important; }
    input { font-weight: 800 !important; font-size: 1.1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGAZIONE ---
def navigate(suite, page='home'):
    st.session_state.suite = suite
    st.session_state.page = page

# Sidebar
with st.sidebar:
    st.title("Menu")
    if st.session_state.suite == 'emissioni':
        if st.button("📐 Dinamica Fumi", use_container_width=True): st.session_state.page = 'fumi'
        st.markdown("---")
        if st.button("🏠 Torna alla Home", use_container_width=True): navigate('home')
    else:
        st.info("Seleziona un modulo dalla Home.")

# ==========================================
# 1. HOME HUB
# ==========================================
if st.session_state.suite == 'home':
    st.markdown("<h1 class='section-title'>Hub Gestionale Emissioni</h1>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    with cols[0]:
        st.info("### 🌿 EMISSIONI\nCalcoli campo e isocinetismo.")
        if st.button("ENTRA IN EMISSIONI", use_container_width=True): navigate('emissioni', 'fumi'); st.rerun()
    with cols[1]:
        st.info("### 📜 CERTIFICATI\nGestione RdP e Archivio.")
        st.button("NON DISPONIBILE", disabled=True, use_container_width=True)
    with cols[2]:
        st.info("### 🔥 FORNI\nMonitoraggio combustione.")
        st.button("NON DISPONIBILE", disabled=True, use_container_width=True)

# ==========================================
# 2. MODULO EMISSIONI (CALCOLI COMPLETI)
# ==========================================
elif st.session_state.suite == 'emissioni' and st.session_state.page == 'fumi':
    st.markdown("<h1 class='section-title'>Dinamica Fumi & Portate</h1>", unsafe_allow_html=True)
    d = st.session_state.dati_dinamica
    
    c_left, c_mid, c_right = st.columns([1, 1.4, 1], gap="medium")
    
    with c_left:
        with st.container(border=True):
            st.markdown("**⚙️ PARAMETRI DI INPUT**")
            d_cam = st.number_input("Ø Camino (m)", value=d['d_cam'], format="%.3f")
            k_pit = st.number_input("K Pitot", value=d['k_pit'], format="%.3f")
            t_fumi = st.number_input("T. Fumi (°C)", value=d['t_fumi'])
            p_atm = st.number_input("P. Atm (hPa)", value=d['p_atm'])
            p_stat = st.number_input("P. Statica (Pa)", value=d['p_stat_pa'])
            h2o = st.number_input("H₂O (%)", value=d['h_in'])
            o2_mis = st.number_input("O₂ Misurata (%)", value=d['o2_mis'])
            co2_mis = st.number_input("CO₂ Misurata (%)", value=d['co2']) # RIPRISTINATA CO2
            o2_rif = st.number_input("O₂ Riferimento (%)", value=d['o2_rif'])

    with c_mid:
        st.markdown("**📊 MAPPATURA ΔP**")
        unit = st.radio("Unità:", ["mmH2O", "Pa"], horizontal=True)
        
        # Logica Punti / Affondamenti
        if d_cam < 0.35: coeffs = [0.500]
        elif d_cam < 1.10: coeffs = [0.146, 0.854]
        elif d_cam < 1.60: coeffs = [0.067, 0.250, 0.750, 0.933]
        else: coeffs = [0.044, 0.146, 0.296, 0.704, 0.854, 0.956]
        
        df_init = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(len(coeffs))],
            "Aff. (cm)": [round(d_cam * c * 100, 1) for c in coeffs],
            "Asse 1": [None]*len(coeffs), "Asse 2": [None]*len(coeffs)
        })
        edit_mappa = st.data_editor(df_init, hide_index=True, use_container_width=True)
        
        # --- CALCOLI (RIPRISTINO LOGICA COMPLETA) ---
        p_ass_pa = (p_atm * 100) + p_stat
        p_ass_hpa = p_ass_pa / 100
        dp_vals = pd.concat([pd.to_numeric(edit_mappa["Asse 1"]), pd.to_numeric(edit_mappa["Asse 2"])]).dropna()
        dp_list = [v for v in dp_vals if v > 0]
        
        # Massa molare fumi umidi (Usa CO2 misurata)
        n2_mis = 100 - o2_mis - co2_mis
        m_wet = ((o2_mis/100 * 31.998) + (co2_mis/100 * 44.01) + (n2_mis/100 * 28.013)) * (1 - h2o/100) + (18.015 * h2o/100)
        
        rho_fumi = (p_ass_pa * m_wet) / (8314.472 * (t_fumi + 273.15))
        v_fumi = np.mean([np.sqrt(k_pit) * np.sqrt((2 * v * (9.80665 if unit=="mmH2O" else 1.0)) / rho_fumi) for v in dp_list]) if dp_list and rho_fumi > 0 else 0.0

        q_aq = v_fumi * (np.pi * d_cam**2 / 4) * 3600
        q_un_u = q_aq * (273.15 / (t_fumi + 273.15)) * (p_ass_hpa / 1013.25)
        q_un_s = q_un_u * (1 - h2o/100)
        q_rif = q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif)) if o2_mis < 20.8 else q_un_s

        # Visualizzazione Risultati (RIPRISTINATA PORTATA UMIDA)
        r1, r2 = st.columns(2)
        with r1:
            st.markdown(f"<div class='res-box'><p class='res-lab'>Velocità</p><p class='res-val'>{v_fumi:.2f} m/s</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Umida</p><p class='res-val'>{q_un_u:.0f} Nm³/h(u)</p></div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Secca</p><p class='res-val'>{q_un_s:.0f} Nm³/h(s)</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Rif. O2</p><p class='res-val'>{q_rif:.0f} Nm³/h</p></div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("**🎯 TARGET ISOCINETICO**")
        with st.container(border=True):
            t_amb = st.number_input("T. Amb. (°C)", value=d['t_amb'])
            d_u = st.number_input("Ø Ugello (mm)", value=d['d_ugello_test'], step=0.5)
            if v_fumi > 0:
                q_p = (v_fumi * (np.pi * (d_u / 1000)**2 / 4) * 3600 * 1000 / 60) * (p_ass_hpa / p_atm) * ((t_amb + 273.15) / (t_fumi + 273.15))
                st.markdown(f"<div style='background:#f1f5f9; padding:20px; border-radius:12px; text-align:center; border:2px solid #2563eb;'>\
                    <p class='res-lab'>Flusso Pompa</p><p class='res-val' style='font-size:2.5rem;'>{q_p:.2f}</p><p style='font-weight:700;'>L/min</p></div>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("**Tabella Rapida Ugelli (L/min)**")
                st.table(pd.DataFrame([{"Ø": f"{u}mm", "L/min": round((v_fumi * (np.pi*(u/1000)**2/4)*3600*1000/60)*(p_ass_hpa/p_atm)*((t_amb+273.15)/(t_fumi+273.15)), 2)} for u in [5, 6, 7, 8, 10, 12]]))
