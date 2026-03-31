import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v4.0", layout="wide")

# --- PERSISTENZA DATI ---
if 'suite' not in st.session_state: st.session_state.suite = 'home'
if 'page' not in st.session_state: st.session_state.page = 'home'

# Inizializzazione parametri (Coerenza 100% con versioni precedenti)
if 'dati_dinamica' not in st.session_state: 
    st.session_state.dati_dinamica = {
        'h_in': 4.68, 't_fumi': 259.0, 'p_atm': 1013.25, 'p_stat_pa': -10.0,
        'o2_mis': 14.71, 'o2_rif': 8.0, 'co2': 12.0, 'd_cam': 1.4, 'k_pit': 0.69,
        't_amb': 20.0, 'd_ugello_test': 6.0
    }

# --- STILE HIGH-CONTRAST (BIANCO E NERO) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* Titoli Neri e Grandi */
    .section-title { 
        font-size: 2.2rem !important; font-weight: 900 !important; color: #000000 !important; 
        border-left: 10px solid #000000; padding-left: 15px; margin-bottom: 25px; 
    }

    /* Box Risultati - Sfondo chiaro, testo nero */
    .res-box { 
        background-color: #F0F2F6 !important; 
        color: #000000 !important;
        padding: 20px; border-radius: 10px; border: 2px solid #000000 !important;
        text-align: center; margin-bottom: 15px;
    }
    
    .res-val { font-size: 2rem !important; font-weight: 900 !important; color: #000000 !important; margin: 0; }
    .res-lab { font-size: 0.9rem !important; font-weight: 800 !important; text-transform: uppercase; color: #000000 !important; }

    /* Input Fields */
    .stNumberInput label, .stRadio label { color: #000000 !important; font-weight: 800 !important; font-size: 1.1rem !important; }
    input { color: #000000 !important; font-weight: 900 !important; border: 2px solid #000000 !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 2px solid #000000 !important; }
    .stButton > button { border: 2px solid #000000 !important; color: #000000 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGAZIONE ---
def switch_suite(suite_name, page_name='home'):
    st.session_state.suite = suite_name
    st.session_state.page = page_name

# Sidebar Dinamica
with st.sidebar:
    st.markdown("<h2 style='color:black'>MENU</h2>", unsafe_allow_html=True)
    if st.session_state.suite == 'emissioni':
        st.write("---")
        if st.button("📐 DINAMICA FUMI", use_container_width=True): st.session_state.page = 'fumi'
        if st.button("💉 CAMPIONAMENTI", use_container_width=True): st.session_state.page = 'camp'
        st.write("---")
        if st.button("🏠 TORNA ALLA HOME", use_container_width=True): switch_suite('home')
    else:
        st.info("Seleziona una sezione nella Home per sbloccare le funzioni.")

# ==========================================
# 1. HOME PAGE (LE 3 SEZIONI)
# ==========================================
if st.session_state.suite == 'home':
    st.markdown("<h1 class='section-title'>DASHBOARD GESTIONALE 360°</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div style='border:3px solid black; padding:20px; border-radius:15px; background:#e2e8f0; height:220px;'>"
                    "<h2 style='color:black'>🌿 EMISSIONI</h2><p style='color:black; font-weight:600;'>Lavoro in campo: Calcoli isocinetismo, fumi e campionamenti.</p></div>", unsafe_allow_html=True)
        if st.button("ACCEDI EMISSIONI", use_container_width=True): switch_suite('emissioni', 'fumi'); st.rerun()
    with c2:
        st.markdown("<div style='border:3px solid black; padding:20px; border-radius:15px; background:#e2e8f0; height:220px;'>"
                    "<h2 style='color:black'>📜 CERTIFICATI</h2><p style='color:black; font-weight:600;'>Lavoro d'ufficio: Gestione RdP, scadenze e database clienti.</p></div>", unsafe_allow_html=True)
        st.button("MODULO UFFICIO (N.D.)", disabled=True, use_container_width=True)
    with c3:
        st.markdown("<div style='border:3px solid black; padding:20px; border-radius:15px; background:#e2e8f0; height:220px;'>"
                    "<h2 style='color:black'>🔥 FORNI</h2><p style='color:black; font-weight:600;'>Monitoraggio: Analisi combustione e parametri impianti.</p></div>", unsafe_allow_html=True)
        st.button("MODULO FORNI (N.D.)", disabled=True, use_container_width=True)

# ==========================================
# 2. MODULO EMISSIONI (CALCOLI COMPLETI)
# ==========================================
elif st.session_state.suite == 'emissioni' and st.session_state.page == 'fumi':
    st.markdown("<h1 class='section-title'>Dinamica Fumi & Portate</h1>", unsafe_allow_html=True)
    d = st.session_state.dati_dinamica
    
    col_input, col_map, col_res = st.columns([1, 1.4, 1], gap="medium")
    
    with col_input:
        with st.container(border=True):
            st.markdown("<b style='font-size:1.2rem'>⚙️ INPUT PARAMETRI</b>", unsafe_allow_html=True)
            d_cam = st.number_input("Ø Camino (m)", value=d['d_cam'], format="%.3f")
            k_pit = st.number_input("K Pitot", value=d['k_pit'], format="%.3f")
            t_fumi = st.number_input("T. Fumi (°C)", value=d['t_fumi'])
            p_atm = st.number_input("P. Atm (hPa)", value=d['p_atm'])
            p_stat = st.number_input("P. Statica (Pa)", value=d['p_stat_pa'])
            h2o = st.number_input("H₂O (%)", value=d['h_in'])
            o2_mis = st.number_input("O₂ Misurata (%)", value=d['o2_mis'])
            co2_mis = st.number_input("CO₂ Misurata (%)", value=d['co2']) # RIPRISTINATA CO2
            o2_rif = st.number_input("O₂ Riferimento (%)", value=d['o2_rif'])

    with col_map:
        st.markdown("<b style='font-size:1.2rem'>📊 MAPPATURA ΔP</b>", unsafe_allow_html=True)
        unit = st.radio("Scegli Unità:", ["mmH2O", "Pa"], horizontal=True)
        
        # Norma Affondamenti
        if d_cam < 0.35: coeffs = [0.500]
        elif d_cam < 1.10: coeffs = [0.146, 0.854]
        elif d_cam < 1.60: coeffs = [0.067, 0.250, 0.750, 0.933]
        else: coeffs = [0.044, 0.146, 0.296, 0.704, 0.854, 0.956]
        
        df_init = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(len(coeffs))],
            "Affond. (cm)": [round(d_cam * c * 100, 1) for c in coeffs],
            "Asse 1": [None]*len(coeffs), "Asse 2": [None]*len(coeffs)
        })
        edit_mappa = st.data_editor(df_init, hide_index=True, use_container_width=True)
        
        # --- CALCOLI FISICI ---
        p_ass_pa = (p_atm * 100) + p_stat
        p_ass_hpa = p_ass_pa / 100
        dp_vals = pd.concat([pd.to_numeric(edit_mappa["Asse 1"]), pd.to_numeric(edit_mappa["Asse 2"])]).dropna()
        dp_list = [v for v in dp_vals if v > 0]
        
        # Massa molare umida (usando CO2 e O2)
        n2_mis = 100 - o2_mis - co2_mis
        m_wet = ((o2_mis/100 * 31.998) + (co2_mis/100 * 44.01) + (n2_mis/100 * 28.013)) * (1 - h2o/100) + (18.015 * h2o/100)
        
        rho_fumi = (p_ass_pa * m_wet) / (8314.472 * (t_fumi + 273.15))
        v_fumi = np.mean([np.sqrt(k_pit) * np.sqrt((2 * v * (9.80665 if unit=="mmH2O" else 1.0)) / rho_fumi) for v in dp_list]) if dp_list and rho_fumi > 0 else 0.0

        # LE 4 PORTATE (VERIFICA COMPLETEZZA)
        q_aq = v_fumi * (np.pi * d_cam**2 / 4) * 3600 # 1. Portata al camino (Am3/h)
        q_un_u = q_aq * (273.15 / (t_fumi + 273.15)) * (p_ass_hpa / 1013.25) # 2. Portata Umida (Nm3/h u)
        q_un_s = q_un_u * (1 - h2o/100) # 3. Portata Secca (Nm3/h s)
        q_rif = q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif)) if o2_mis < 20.8 else q_un_s # 4. Portata Riferita

        # Visualizzazione Grid
        r1, r2 = st.columns(2)
        with r1:
            st.markdown(f"<div class='res-box'><p class='res-lab'>Velocità</p><p class='res-val'>{v_fumi:.2f} m/s</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Camino</p><p class='res-val'>{q_aq:.0f} Am³/h</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Umida</p><p class='res-val'>{q_un_u:.0f} Nm³/h u</p></div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Secca</p><p class='res-val'>{q_un_s:.0f} Nm³/h s</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box'><p class='res-lab'>Riferita O₂</p><p class='res-val'>{q_rif:.0f} Nm³/h</p></div>", unsafe_allow_html=True)

    with col_res:
        st.markdown("<b style='font-size:1.2rem'>🎯 TARGET ISOCINETICO</b>", unsafe_allow_html=True)
        with st.container(border=True):
            t_amb = st.number_input("T. Ambiente (°C)", value=d['t_amb'])
            d_u = st.number_input("Ø Ugello (mm)", value=d['d_ugello_test'], step=0.5)
            if v_fumi > 0:
                q_p = (v_fumi * (np.pi * (d_u / 1000)**2 / 4) * 3600 * 1000 / 60) * (p_ass_hpa / p_atm) * ((t_amb + 273.15) / (t_fumi + 273.15))
                st.markdown(f"<div style='background:black; color:white; padding:20px; border-radius:15px; text-align:center;'>"
                            f"<p style='margin:0; font-weight:700;'>L/min TARGET</p><p style='font-size:3rem; font-weight:900; margin:0;'>{q_p:.2f}</p></div>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("**Tabella rapida ugelli:**")
                st.table(pd.DataFrame([{"Ø": f"{u}mm", "L/min": round((v_fumi * (np.pi*(u/1000)**2/4)*3600*1000/60)*(p_ass_hpa/p_atm)*((t_amb+273.15)/(t_fumi+273.15)), 2)} for u in [5, 6, 7, 8, 10, 12]]))
