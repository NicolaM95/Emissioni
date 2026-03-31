import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CONFIGURAZIONE E PERSISTENZA ---
st.set_page_config(page_title="Emissioni Pro v3.8 - Full Suite", layout="wide")

if 'suite' not in st.session_state: st.session_state.suite = 'home'
if 'page' not in st.session_state: st.session_state.page = 'home'

# Inizializzazione Dati (Tutti i parametri storici preservati)
if 'dati_dinamica' not in st.session_state: 
    st.session_state.dati_dinamica = {
        'h_in': 4.68, 't_fumi': 259.0, 'p_atm': 1013.25, 'p_stat_pa': -10.0,
        'o2_mis': 14.71, 'o2_rif': 8.0, 'd_cam': 1.4, 'k_pit': 0.69,
        'v': 0.0, 'q_rif': 0.0, 'co2': 12.0, 't_amb': 20.0, 'd_ugello_test': 6.0
    }

# --- 2. PALETTE COLORI RICALIBRATA (10 TEMI) ---
temi = {
    "Neve": ["#FFFFFF", "#1E293B", "#F1F5F9", "#CBD5E1", "#2563EB"],
    "Notte": ["#0F172A", "#F8FAFC", "#1E293B", "#334155", "#38BDF8"],
    "Ardesia": ["#334155", "#F8FAFC", "#475569", "#64748B", "#0EA5E9"],
    "Foresta": ["#064E3B", "#ECFDF5", "#065F46", "#059669", "#10B981"],
    "Crema": ["#FDFCF0", "#451A03", "#FEFCE8", "#FEF08A", "#D97706"],
    "Oceano": ["#0C4A6E", "#F0F9FF", "#075985", "#0284C7", "#38BDF8"],
    "Grafite": ["#18181B", "#FAFAFA", "#27272A", "#3F3F46", "#A1A1AA"],
    "Ametista": ["#2E1065", "#FAF5FF", "#4C1D95", "#7C3AED", "#A855F7"],
    "Argilla": ["#451A03", "#FFF7ED", "#78350F", "#92400E", "#F59E0B"],
    "Cobalto": ["#1E3A8A", "#EFF6FF", "#1E40AF", "#3B82F6", "#60A5FA"]
}

if 'tema_attivo' not in st.session_state:
    st.session_state.tema_attivo = temi["Neve"]

t = st.session_state.tema_attivo

# --- 3. CSS ADATTIVO (OTTIMIZZATO TABLET) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {t[0]}; color: {t[1]}; transition: 0.3s; }}
    .section-title {{ 
        font-size: 2rem !important; font-weight: 800; color: {t[1]} !important; 
        border-left: 8px solid {t[4]}; padding-left: 15px; margin-bottom: 20px; 
    }}
    .res-box, .suite-card-inner {{ 
        background-color: {t[2]} !important; color: {t[1]} !important;
        padding: 18px; border-radius: 12px; border: 1px solid {t[3]} !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 10px;
    }}
    .res-val {{ font-size: 2rem !important; font-weight: 900 !important; color: {t[4]}; margin: 0; }}
    .res-lab {{ font-size: 0.8rem !important; font-weight: 700; text-transform: uppercase; opacity: 0.8; }}
    .stNumberInput input {{ font-size: 1.2rem !important; font-weight: 800 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGICA DI NAVIGAZIONE ---
def navigate(suite, page='home'):
    st.session_state.suite = suite
    st.session_state.page = page

# Sidebar Contestuale
with st.sidebar:
    st.markdown(f"<h3 style='color:{t[1]}'>SISTEMA GESTIONALE</h3>", unsafe_allow_html=True)
    if st.session_state.suite == 'emissioni':
        st.success("🌿 AREA EMISSIONI")
        if st.button("📐 Dinamica Fumi", use_container_width=True): st.session_state.page = 'fumi'
        if st.button("💉 Campionamenti", use_container_width=True): st.session_state.page = 'camp'
        st.markdown("---")
        if st.button("🏠 Torna alla Hub", use_container_width=True): navigate('home')
    else:
        st.info("Seleziona un modulo operativo dalla Hub.")

# --- 5. INTERFACCIA ---

# --- HOME HUB ---
if st.session_state.suite == 'home':
    st.markdown("<h1 class='section-title'>Hub Gestionale 360°</h1>", unsafe_allow_html=True)
    
    # Palette Swatches
    with st.container(border=True):
        st.markdown("**🎨 Personalizzazione Colori (Visibilità Tablet)**")
        p_cols = st.columns(10)
        for i, (nome, colori) in enumerate(temi.items()):
            if p_cols[i].button(nome[:2], help=nome, key=f"p_{i}", use_container_width=True):
                st.session_state.tema_attivo = colori
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Macro Blocchi
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(f"<div class='suite-card-inner' style='border-top: 6px solid #10B981;'><h2>🌿 EMISSIONI</h2><p>Calcoli campo e isocinetismo.</p></div>", unsafe_allow_html=True)
        if st.button("ACCEDI AL CAMPO", use_container_width=True): navigate('emissioni', 'fumi'); st.rerun()
    with b2:
        st.markdown(f"<div class='suite-card-inner' style='border-top: 6px solid #3B82F6;'><h2>📜 CERTIFICATI</h2><p>Archivio RdP e Scadenze.</p></div>", unsafe_allow_html=True)
        st.button("ACCEDI UFFICIO (N.D.)", disabled=True, use_container_width=True)
    with b3:
        st.markdown(f"<div class='suite-card-inner' style='border-top: 6px solid #F59E0B;'><h2>🔥 FORNI</h2><p>Monitoraggio parametri.</p></div>", unsafe_allow_html=True)
        st.button("ACCEDI FORNI (N.D.)", disabled=True, use_container_width=True)

# --- SUITE EMISSIONI ---
elif st.session_state.suite == 'emissioni' and st.session_state.page == 'fumi':
    st.markdown("<h1 class='section-title'>Dinamica Fumi & Portate</h1>", unsafe_allow_html=True)
    d = st.session_state.dati_dinamica
    
    c_left, c_mid, c_right = st.columns([1, 1.4, 1], gap="medium")
    
    with c_left:
        with st.container(border=True):
            st.markdown(f"<b style='color:{t[4]}'>⚙️ PARAMETRI FISICI</b>", unsafe_allow_html=True)
            d_cam = st.number_input("Ø Camino (m)", value=d['d_cam'], format="%.3f")
            k_pit = st.number_input("K Pitot", value=d['k_pit'], format="%.3f")
            t_fumi = st.number_input("T. Fumi (°C)", value=d['t_fumi'])
            p_atm = st.number_input("P. Atm (hPa)", value=d['p_atm'])
            p_stat = st.number_input("P. Statica (Pa)", value=d['p_stat_pa'])
            h2o = st.number_input("H₂O (%)", value=d['h_in'])
            o2_mis = st.number_input("O₂ (%)", value=d['o2_mis'])
            o2_rif = st.number_input("O₂ Rif (%)", value=d['o2_rif'])

    with c_mid:
        st.markdown(f"<b style='color:{t[4]}'>📊 MAPPATURA ΔP</b>", unsafe_allow_html=True)
        unit = st.radio("Unità:", ["mmH2O", "Pa"], horizontal=True, label_visibility="collapsed")
        
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
        
        # --- BLOCCO CALCOLI (INTEGRITÀ VERIFICATA) ---
        p_ass_pa = (p_atm * 100) + p_stat
        p_ass_hpa = p_ass_pa / 100
        dp_vals = pd.concat([pd.to_numeric(edit_mappa["Asse 1"]), pd.to_numeric(edit_mappa["Asse 2"])]).dropna()
        dp_list = [v for v in dp_vals if v > 0]
        
        # Massa molare fumi umidi
        m_wet = ((o2_mis/100 * 31.998) + (0.12 * 44.01) + ((100-o2_mis-12)/100 * 28.013)) * (1 - h2o/100) + (18.015 * h2o/100)
        rho_fumi = (p_ass_pa * m_wet) / (8314.472 * (t_fumi + 273.15))
        v_fumi = np.mean([np.sqrt(k_pit) * np.sqrt((2 * v * (9.80665 if unit=="mmH2O" else 1.0)) / rho_fumi) for v in dp_list]) if dp_list and rho_fumi > 0 else 0.0

        q_aq = v_fumi * (np.pi * d_cam**2 / 4) * 3600
        q_un_u = q_aq * (273.15 / (t_fumi + 273.15)) * (p_ass_hpa / 1013.25)
        q_un_s = q_un_u * (1 - h2o/100)
        q_rif = q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif)) if o2_mis < 20.8 else q_un_s

        # Risultati ad alta leggibilità
        r1, r2 = st.columns(2)
        with r1:
            st.markdown(f"<div class='res-box'><p class='res-lab'>Velocità</p><p class='res-val'>{v_fumi:.2f} <small style='font-size:1rem'>m/s</small></p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Umida</p><p class='res-val'>{q_un_u:.0f} <small style='font-size:1rem'>Nm³/h</small></p></div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='res-box'><p class='res-lab'>Portata Secca</p><p class='res-val'>{q_un_s:.0f} <small style='font-size:1rem'>Nm³/h</small></p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box'><p class='res-lab'>Riferita O2</p><p class='res-val'>{q_rif:.0f} <small style='font-size:1rem'>Nm³/h</small></p></div>", unsafe_allow_html=True)

    with c_right:
        st.markdown(f"<b style='color:{t[4]}'>🎯 PLANNING ISOCINETICO</b>", unsafe_allow_html=True)
        with st.container(border=True):
            t_amb = st.number_input("T. Amb. (°C)", value=d['t_amb'])
            d_u = st.number_input("Ø Ugello (mm)", value=d['d_ugello_test'], step=0.5)
            if v_fumi > 0:
                q_p = (v_fumi * (np.pi * (d_u / 1000)**2 / 4) * 3600 * 1000 / 60) * (p_ass_hpa / p_atm) * ((t_amb + 273.15) / (t_fumi + 273.15))
                st.markdown(f"""<div style='background:{t[1]}; color:{t[0]}; padding:20px; border-radius:12px; text-align:center;'>
                    <p class='res-lab' style='color:{t[0]}'>Target Pompa</p><p class='res-val' style='color:{t[0]}'>{q_p:.2f}</p><p style='font-weight:700; margin:0; color:{t[0]}'>L/min</p></div>""", unsafe_allow_html=True)
                st.table(pd.DataFrame([{"Ø": f"{u}mm", "L/min": round((v_fumi * (np.pi*(u/1000)**2/4)*3600*1000/60)*(p_ass_hpa/p_atm)*((t_amb+273.15)/(t_fumi+273.15)), 2)} for u in [5, 6, 7, 8, 10, 12]]))
