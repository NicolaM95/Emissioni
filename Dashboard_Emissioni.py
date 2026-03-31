import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v4.2", layout="wide")

# --- 2. GESTIONE STATO (EVITA ERRORI) ---
if 'suite' not in st.session_state: st.session_state.suite = 'home'
if 'page' not in st.session_state: st.session_state.page = 'home'

# Dati tecnici (CO2 inclusa)
if 'dati_dinamica' not in st.session_state: 
    st.session_state.dati_dinamica = {
        'h_in': 4.68, 't_fumi': 259.0, 'p_atm': 1013.25, 'p_stat_pa': -10.0,
        'o2_mis': 14.71, 'o2_rif': 8.0, 'co2': 12.0, 'd_cam': 1.4, 'k_pit': 0.69,
        't_amb': 20.0, 'd_ugello_test': 6.0
    }

# --- 3. CSS RADICALE (BIANCO & NERO) ---
st.markdown("""
    <style>
    /* Forza sfondo bianco ovunque */
    .stApp, div[data-testid="stToolbar"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Titoli Neri */
    .section-title { 
        font-size: 2rem !important; font-weight: 900 !important; color: #000000 !important; 
        border-left: 10px solid #000000; padding-left: 15px; margin-bottom: 25px; 
    }

    /* Input Fields: Sfondo Bianco, Testo Nero */
    div[data-baseweb="input"], input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
    }
    label, p, span { color: #000000 !important; font-weight: 700 !important; }

    /* Risultati: Box identici e coerenti */
    .res-grid-box { 
        background-color: #FFFFFF !important; 
        color: #000000 !important;
        padding: 20px; 
        border-radius: 5px; 
        border: 2px solid #000000 !important;
        text-align: center; 
        height: 120px; /* Altezza fissa per coerenza visiva */
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
    }
    .res-val { font-size: 1.8rem !important; font-weight: 900 !important; margin: 0; }
    .res-lab { font-size: 0.8rem !important; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; }

    /* Bottoni */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        font-weight: 800 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
        border-right: 2px solid #000000 !important; 
    }
    
    /* Tabelle (Data Editor) */
    .stDataEditor { background-color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

def switch_suite(suite_name, page_name='home'):
    st.session_state.suite = suite_name
    st.session_state.page = page_name

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:black'>MENU</h2>", unsafe_allow_html=True)
    if st.session_state.suite != 'home':
        if st.button("🏠 HOME PRINCIPALE", use_container_width=True): switch_suite('home')
        st.write("---")
        if st.button("📐 DINAMICA FUMI", use_container_width=True): st.session_state.page = 'fumi'

# ==========================================
# 5. HOME PAGE
# ==========================================
if st.session_state.suite == 'home':
    st.markdown("<h1 class='section-title'>DASHBOARD EMISSIONI PRO</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div style='border:3px solid black; padding:20px; height:200px;'>"
                    "<h2>🌿 EMISSIONI</h2><p>Calcoli campo e isocinetismo fumi.</p></div>", unsafe_allow_html=True)
        if st.button("ACCEDI EMISSIONI", use_container_width=True): switch_suite('emissioni', 'fumi'); st.rerun()
    with c2:
        st.markdown("<div style='border:1px solid #ccc; padding:20px; height:200px; color:#aaa;'>"
                    "<h2>📜 CERTIFICATI</h2><p>Modulo non attivo.</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div style='border:1px solid #ccc; padding:20px; height:200px; color:#aaa;'>"
                    "<h2>🔥 FORNI</h2><p>Modulo non attivo.</p></div>", unsafe_allow_html=True)

# ==========================================
# 6. SEZIONE EMISSIONI (FUMI)
# ==========================================
elif st.session_state.suite == 'emissioni' and st.session_state.page == 'fumi':
    st.markdown("<h1 class='section-title'>Dinamica Fumi & Portate</h1>", unsafe_allow_html=True)
    d = st.session_state.dati_dinamica
    
    col_input, col_main = st.columns([1, 2.4], gap="large")
    
    with col_input:
        with st.container(border=True):
            st.markdown("### ⚙️ PARAMETRI")
            d_cam = st.number_input("Ø Camino (m)", value=d['d_cam'], format="%.3f")
            k_pit = st.number_input("Costante Pitot", value=d['k_pit'], format="%.3f")
            t_fumi = st.number_input("T. Fumi (°C)", value=d['t_fumi'])
            p_atm = st.number_input("P. Atm (hPa)", value=d['p_atm'])
            p_stat = st.number_input("P. Statica (Pa)", value=d['p_stat_pa'])
            h2o = st.number_input("Umidità (%)", value=d['h_in'])
            o2_mis = st.number_input("O2 Mis. (%)", value=d['o2_mis'])
            co2_mis = st.number_input("CO2 Mis. (%)", value=d['co2'])
            o2_rif = st.number_input("O2 Rif. (%)", value=d['o2_rif'])

    with col_main:
        # Riga Mappatura e Target
        c_map, c_target = st.columns([1.5, 1])
        
        with c_map:
            st.markdown("### 📊 MAPPATURA ΔP")
            unit = st.radio("Unità:", ["mmH2O", "Pa"], horizontal=True)
            
            # Calcolo Affondamenti Norma
            if d_cam < 0.35: coeffs = [0.500]
            elif d_cam < 1.10: coeffs = [0.146, 0.854]
            elif d_cam < 1.60: coeffs = [0.067, 0.250, 0.750, 0.933]
            else: coeffs = [0.044, 0.146, 0.296, 0.704, 0.854, 0.956]
            
            df = pd.DataFrame({
                "Punto": [f"P{i+1}" for i in range(len(coeffs))],
                "Affond. (cm)": [round(d_cam * c * 100, 1) for c in coeffs],
                "Asse 1": [None]*len(coeffs), "Asse 2": [None]*len(coeffs)
            })
            edit_df = st.data_editor(df, hide_index=True, use_container_width=True)

        with c_target:
            st.markdown("### 🎯 PLANNING")
            t_amb = st.number_input("T. Amb. (°C)", value=d['t_amb'])
            d_u = st.number_input("Ø Ugello (mm)", value=d['d_ugello_test'], step=0.5)

        # --- LOGICA CALCOLO (4 PORTATE + VELOCITÀ) ---
        p_ass_pa = (p_atm * 100) + p_stat
        p_ass_hpa = p_ass_pa / 100
        dp_vals = pd.concat([pd.to_numeric(edit_df["Asse 1"]), pd.to_numeric(edit_df["Asse 2"])]).dropna()
        dp_list = [v for v in dp_vals if v > 0]
        
        m_wet = ((o2_mis/100 * 31.998) + (co2_mis/100 * 44.01) + ((100-o2_mis-co2_mis)/100 * 28.013)) * (1 - h2o/100) + (18.015 * h2o/100)
        rho_fumi = (p_ass_pa * m_wet) / (8314.472 * (t_fumi + 273.15))
        v_fumi = np.mean([np.sqrt(k_pit) * np.sqrt((2 * v * (9.80665 if unit=="mmH2O" else 1.0)) / rho_fumi) for v in dp_list]) if dp_list and rho_fumi > 0 else 0.0

        q_aq = v_fumi * (np.pi * d_cam**2 / 4) * 3600
        q_un_u = q_aq * (273.15 / (t_fumi + 273.15)) * (p_ass_hpa / 1013.25)
        q_un_s = q_un_u * (1 - h2o/100)
        q_rif = q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif)) if o2_mis < 20.8 else q_un_s

        # --- RISULTATI COERENTI ---
        st.markdown("### 📈 RISULTATI TECNICI")
        r1, r2, r3, r4, r5 = st.columns(5)
        
        with r1: st.markdown(f"<div class='res-grid-box'><span class='res-lab'>Velocità</span><span class='res-val'>{v_fumi:.2f}</span><small>m/s</small></div>", unsafe_allow_html=True)
        with r2: st.markdown(f"<div class='res-grid-box'><span class='res-lab'>Camino</span><span class='res-val'>{q_aq:.0f}</span><small>Am³/h</small></div>", unsafe_allow_html=True)
        with r3: st.markdown(f"<div class='res-grid-box'><span class='res-lab'>Umida</span><span class='res-val'>{q_un_u:.0f}</span><small>Nm³/h u</small></div>", unsafe_allow_html=True)
        with r4: st.markdown(f"<div class='res-grid-box'><span class='res-lab'>Secca</span><span class='res-val'>{q_un_s:.0f}</span><small>Nm³/h s</small></div>", unsafe_allow_html=True)
        with r5: st.markdown(f"<div class='res-grid-box'><span class='res-lab'>Riferita</span><span class='res-val'>{q_rif:.0f}</span><small>Nm³/h</small></div>", unsafe_allow_html=True)

        if v_fumi > 0:
            q_p = (v_fumi * (np.pi * (d_u / 1000)**2 / 4) * 3600 * 1000 / 60) * (p_ass_hpa / p_atm) * ((t_amb + 273.15) / (t_fumi + 273.15))
            st.markdown(f"<div style='border:3px solid black; padding:15px; text-align:center; margin-top:10px;'>"
                        f"<b>FLUSSO TARGET POMPA PER Ø {d_u}mm: {q_p:.2f} L/min</b></div>", unsafe_allow_html=True)
