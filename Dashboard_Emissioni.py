import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v4.1", layout="wide")

# --- PERSISTENZA DATI ---
if 'suite' not in st.session_state: st.session_state.suite = 'home'
if 'page' not in st.session_state: st.session_state.page = 'home'

if 'dati_dinamica' not in st.session_state: 
    st.session_state.dati_dinamica = {
        'h_in': 4.68, 't_fumi': 259.0, 'p_atm': 1013.25, 'p_stat_pa': -10.0,
        'o2_mis': 14.71, 'o2_rif': 8.0, 'co2': 12.0, 'd_cam': 1.4, 'k_pit': 0.69,
        't_amb': 20.0, 'd_ugello_test': 6.0
    }

# --- CSS HIGH-CONTRAST RICALIBRATO ---
st.markdown("""
    <style>
    /* Sfondo Generale Bianco */
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    
    /* Titoli */
    .section-title { 
        font-size: 2.2rem !important; font-weight: 900 !important; color: #000000 !important; 
        border-left: 10px solid #000000; padding-left: 15px; margin-bottom: 25px; 
    }

    /* BOX INPUT (Sfondo Nero, Testo Bianco come richiesto) */
    .input-dark-box {
        background-color: #000000 !important;
        padding: 20px;
        border-radius: 10px;
        color: #FFFFFF !important;
        margin-bottom: 20px;
    }
    .input-dark-box b, .input-dark-box p { color: #FFFFFF !important; }
    
    /* Forzatura colore numeri negli input */
    div[data-baseweb="input"] input {
        color: #000000 !important; /* Testo inserito nero su fondo bianco dell'input */
        font-weight: 800 !important;
    }
    
    /* Label degli input nella sezione scura */
    .stNumberInput label { color: #000000 !important; font-weight: 800 !important; }

    /* Bottoni Home e Sidebar (Bordo Nero, Testo Nero) */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        font-weight: 800 !important;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }

    /* Box Risultati */
    .res-box { 
        background-color: #F1F3F5 !important; 
        color: #000000 !important;
        padding: 15px; border-radius: 10px; border: 2px solid #000000 !important;
        text-align: center; margin-bottom: 10px;
    }
    .res-val { font-size: 1.8rem !important; font-weight: 900 !important; color: #000000 !important; }
    .res-lab { font-size: 0.8rem !important; font-weight: 700; color: #495057 !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 2px solid #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

def switch_suite(suite_name, page_name='home'):
    st.session_state.suite = suite_name
    st.session_state.page = page_name

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:black'>NAVIGAZIONE</h2>", unsafe_allow_html=True)
    if st.session_state.suite != 'home':
        if st.button("🏠 TORNA ALLA HOME", use_container_width=True): switch_suite('home')
        st.write("---")
        if st.button("📐 DINAMICA FUMI", use_container_width=True): st.session_state.page = 'fumi'

# ==========================================
# 1. HOME PAGE
# ==========================================
if st.session_state.suite == 'home':
    st.markdown("<h1 class='section-title'>HUB EMISSIONI PRO</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div style='border:2px solid black; padding:20px; border-radius:10px; height:200px; background:#F8F9FA;'>"
                    "<h2 style='color:black'>🌿 EMISSIONI</h2><p style='color:black'>Calcoli isocinetici e dinamica fumi in campo.</p></div>", unsafe_allow_html=True)
        if st.button("VAI A EMISSIONI", key="btn_em", use_container_width=True): switch_suite('emissioni', 'fumi'); st.rerun()
    with c2:
        st.markdown("<div style='border:2px solid black; padding:20px; border-radius:10px; height:200px; background:#F8F9FA;'>"
                    "<h2 style='color:black'>📜 CERTIFICATI</h2><p style='color:black'>Archivio rapporti e scadenziario.</p></div>", unsafe_allow_html=True)
        st.button("NON ATTIVO", disabled=True, use_container_width=True)
    with c3:
        st.markdown("<div style='border:2px solid black; padding:20px; border-radius:10px; height:200px; background:#F8F9FA;'>"
                    "<h2 style='color:black'>🔥 FORNI</h2><p style='color:black'>Monitoraggio combustione impianti.</p></div>", unsafe_allow_html=True)
        st.button("NON ATTIVO", disabled=True, use_container_width=True)

# ==========================================
# 2. SEZIONE FUMI (CALCOLI & INPUT)
# ==========================================
elif st.session_state.suite == 'emissioni' and st.session_state.page == 'fumi':
    st.markdown("<h1 class='section-title'>Dinamica Fumi & Portate</h1>", unsafe_allow_html=True)
    d = st.session_state.dati_dinamica
    
    col_in, col_map, col_out = st.columns([1, 1.2, 1], gap="small")
    
    with col_in:
        # CONTENITORE INPUT NERO CON TESTO BIANCO
        st.markdown('<div class="input-dark-box"><b>⚙️ PARAMETRI TECNICI</b>', unsafe_allow_html=True)
        d_cam = st.number_input("Diametro Camino (m)", value=d['d_cam'], format="%.3f")
        k_pit = st.number_input("Costante Pitot (K)", value=d['k_pit'], format="%.3f")
        t_fumi = st.number_input("Temperatura Fumi (°C)", value=d['t_fumi'])
        p_atm = st.number_input("Pressione Atm. (hPa)", value=d['p_atm'])
        p_stat = st.number_input("Pressione Statica (Pa)", value=d['p_stat_pa'])
        h2o = st.number_input("Umidità H2O (%)", value=d['h_in'])
        o2_mis = st.number_input("O2 Misurato (%)", value=d['o2_mis'])
        co2_mis = st.number_input("CO2 Misurata (%)", value=d['co2'])
        o2_rif = st.number_input("O2 Riferimento (%)", value=d['o2_rif'])
        st.markdown('</div>', unsafe_allow_html=True)

    with col_map:
        st.markdown("<b>📊 MAPPATURA ΔP</b>", unsafe_allow_html=True)
        unit = st.radio("Unità:", ["mmH2O", "Pa"], horizontal=True)
        
        # Logica Norma Punti
        if d_cam < 0.35: coeffs = [0.500]
        elif d_cam < 1.10: coeffs = [0.146, 0.854]
        elif d_cam < 1.60: coeffs = [0.067, 0.250, 0.750, 0.933]
        else: coeffs = [0.044, 0.146, 0.296, 0.704, 0.854, 0.956]
        
        df = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(len(coeffs))],
            "Aff. (cm)": [round(d_cam * c * 100, 1) for c in coeffs],
            "Asse 1": [None]*len(coeffs), "Asse 2": [None]*len(coeffs)
        })
        edit_df = st.data_editor(df, hide_index=True, use_container_width=True)
        
        # --- CALCOLI (RIPRISTINATI) ---
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

        # Griglia 4 Portate
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='res-box'><p class='res-lab'>Velocità</p><p class='res-val'>{v_fumi:.2f} m/s</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Camino (1)</p><p class='res-val'>{q_aq:.0f} Am³/h</p></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Umida (2)</p><p class='res-val'>{q_un_u:.0f} Nm³/h u</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Secca (3)</p><p class='res-val'>{q_un_s:.0f} Nm³/h s</p></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Riferita O2 (4)</p><p class='res-val'>{q_rif:.0f} Nm³/h</p></div>", unsafe_allow_html=True)

    with col_out:
        st.markdown("<b>🎯 PLANNING</b>", unsafe_allow_html=True)
        with st.container(border=True):
            t_amb = st.number_input("T. Amb. (°C)", value=d['t_amb'])
            d_u = st.number_input("Ø Ugello (mm)", value=d['d_ugello_test'], step=0.5)
            if v_fumi > 0:
                q_p = (v_fumi * (np.pi * (d_u / 1000)**2 / 4) * 3600 * 1000 / 60) * (p_ass_hpa / p_atm) * ((t_amb + 273.15) / (t_fumi + 273.15))
                st.markdown(f"<div style='background:black; color:white; padding:20px; border-radius:10px; text-align:center;'>"
                            f"<p style='margin:0;'>TARGET POMPA</p><p style='font-size:2.5rem; font-weight:900;'>{q_p:.2f}</p><p style='margin:0;'>L/min</p></div>", unsafe_allow_html=True)
                st.table(pd.DataFrame([{"Ø": f"{u}mm", "L/min": round((v_fumi * (np.pi*(u/1000)**2/4)*3600*1000/60)*(p_ass_hpa/p_atm)*((t_amb+273.15)/(t_fumi+273.15)), 2)} for u in [5, 6, 7, 8, 10, 12]]))
