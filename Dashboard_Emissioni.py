import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v3.8 - FULL", layout="wide")

# --- INIZIALIZZAZIONE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'bg_color' not in st.session_state: st.session_state.bg_color = '#F8F9FA'
if 'text_color' not in st.session_state: st.session_state.text_color = '#1E293B'
if 'dati_dinamica' not in st.session_state: 
    st.session_state.dati_dinamica = {
        'h_in': 4.68, 't_fumi': 259.0, 'p_atm': 1013.25, 'p_stat_pa': -10.0,
        'o2_mis': 14.71, 'o2_rif': 8.0, 'd_cam': 1.4, 'k_pit': 0.69,
        'v': 0.0, 'q_rif': 0.0, 'co2': 0.0, 't_amb': 20.0, 'd_ugello_test': 6.0
    }

# --- CSS DINAMICO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.bg_color}; color: {st.session_state.text_color}; }}
    
    /* Card con trasparenza adattiva */
    .res-box {{ 
        background: rgba(255, 255, 255, 0.88); 
        padding: 15px; border-radius: 12px; text-align: center; 
        border: 1px solid rgba(0,0,0,0.1); margin-top: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    
    .section-title {{ 
        font-size: 2.5rem !important; font-weight: 950; 
        color: {st.session_state.text_color} !important; 
        border-left: 10px solid #2563eb; padding-left: 15px; margin-bottom: 25px; 
    }}

    /* Input Style richiesto */
    .stNumberInput input {{ font-size: 1.5rem !important; font-weight: 900 !important; color: #2563eb !important; }}
    .stNumberInput label {{ font-size: 1.1rem !important; font-weight: 800 !important; color: {st.session_state.text_color} !important; }}
    
    .res-val-big {{ font-size: 2.8rem !important; font-weight: 950 !important; line-height: 1; margin: 5px 0; }}
    .res-label-small {{ font-size: 0.9rem; font-weight: 800; color: #475569; text-transform: uppercase; }}

    /* Palette Color Picker */
    .color-swatch {{
        display: inline-block; width: 40px; height: 40px; border-radius: 50%;
        margin: 5px; border: 3px solid white; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    </style>
    """, unsafe_allow_html=True)

def nav(p): st.session_state.page = p

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🛰️ NAVIGATION")
    st.button("🏠 Home", on_click=lambda: nav('home'), use_container_width=True)
    st.button("📐 Dinamica Fumi", on_click=lambda: nav('fumi'), use_container_width=True)

# ==========================================
# 1. HOME CON BLOCCHI E PALETTE
# ==========================================
if st.session_state.page == 'home':
    st.markdown("<h1 class='section-title'>🏠 Dashboard Principale</h1>", unsafe_allow_html=True)
    
    # --- PALETTE COLORI (Migliorata per iPad) ---
    with st.container(border=True):
        st.markdown("**🎨 Seleziona Colore di Sfondo**")
        temi = {
            "⚪": ["#FFFFFF", "#1E293B"], "🌑": ["#1E293B", "#F8FAFC"], 
            "🔵": ["#0F172A", "#F1F5F9"], "🌲": ["#064E3B", "#F0FDF4"],
            "🔘": ["#475569", "#FFFFFF"], "⬛": ["#000000", "#FFFFFF"], 
            "🏜️": ["#F5F5DC", "#1E293B"], "🧊": ["#334155", "#E2E8F0"],
            "📓": ["#27272A", "#F4F4F5"], "🔮": ["#2D1B4E", "#F5F3FF"]
        }
        cols_p = st.columns(len(temi))
        for i, (icon, colors) in enumerate(temi.items()):
            if cols_p[i].button(icon, key=f"t_{i}"):
                st.session_state.bg_color = colors[0]
                st.session_state.text_color = colors[1]
                st.rerun()

    # --- BLOCCHI RICHIESTI ---
    st.markdown("---")
    b1, b2, b3 = st.columns(3)
    
    with b1:
        st.markdown(f"""<div style='background:#10b981; padding:30px; border-radius:20px; color:white; min-height:200px;'>
            <h3>🌿 Emissioni</h3><p>Gestione parametri camino e mappature isocinetiche.</p></div>""", unsafe_allow_html=True)
        if st.button("Vai a Emissioni", use_container_width=True): nav('fumi'); st.rerun()
    
    with b2:
        st.markdown(f"""<div style='background:#3b82f6; padding:30px; border-radius:20px; color:white; min-height:200px;'>
            <h3>📜 Certificati</h3><p>Archivio RdP e certificazioni strumentazione.</p></div>""", unsafe_allow_html=True)
        st.button("Apri Certificati", disabled=True, use_container_width=True)
        
    with b3:
        st.markdown(f"""<div style='background:#f59e0b; padding:30px; border-radius:20px; color:white; min-height:200px;'>
            <h3>🔥 Forni</h3><p>Monitoraggio temperature e combustione processi.</p></div>""", unsafe_allow_html=True)
        st.button("Monitora Forni", disabled=True, use_container_width=True)

# ==========================================
# 2. DINAMICA FUMI (CON PORTATA UMIDA)
# ==========================================
elif st.session_state.page == 'fumi':
    st.markdown("<h1 class='section-title'>📐 DINAMICA FUMI & PLANNING</h1>", unsafe_allow_html=True)
    d = st.session_state.dati_dinamica
    
    c_left, c_mid, c_right = st.columns([1, 1.4, 1], gap="medium")
    
    with c_left:
        with st.container(border=True):
            st.markdown("<p style='font-size:1.2rem; font-weight:900; color:#2563eb;'>⚙️ INPUT TECNICI</p>", unsafe_allow_html=True)
            d_cam = st.number_input("Diametro Camino (m)", value=d['d_cam'], format="%.3f")
            k_pit = st.number_input("K Pitot (Targa)", value=d['k_pit'], format="%.3f")
            t_fumi = st.number_input("T. Fumi (°C)", value=d['t_fumi'])
            p_atm = st.number_input("P. Atm (hPa)", value=d['p_atm'])
            p_stat = st.number_input("P. Statica (Pa)", value=d['p_stat_pa'])
            h2o = st.number_input("H₂O (%)", value=d['h_in'])
            o2_mis = st.number_input("O₂ (%)", value=d['o2_mis'])
            co2_mis = st.number_input("CO₂ (%)", value=d['co2'])
            o2_rif = st.number_input("O₂ Rif (%)", value=d['o2_rif'])

    with c_mid:
        st.markdown("<p style='font-size:1.2rem; font-weight:900; color:#166534;'>📊 MAPPATURA ΔP</p>", unsafe_allow_html=True)
        unit = st.radio("Unità:", ["mmH2O", "Pa"], horizontal=True, label_visibility="collapsed")
        
        # Logica punti camino
        n_punti, coeffs = (2, [0.146, 0.854]) if d_cam < 1.1 else (4, [0.067, 0.250, 0.750, 0.933])
        df_init = pd.DataFrame({"Punto": [f"P{i+1}" for i in range(len(coeffs))], "Asse 1": [None]*len(coeffs), "Asse 2": [None]*len(coeffs)})
        edit_mappa = st.data_editor(df_init, hide_index=True, use_container_width=True)
        
        # Calcoli
        p_ass_pa = (p_atm * 100) + p_stat
        p_ass_hpa = p_ass_pa / 100
        s1 = pd.to_numeric(edit_mappa["Asse 1"].astype(str).str.replace(',', '.'), errors='coerce')
        s2 = pd.to_numeric(edit_mappa["Asse 2"].astype(str).str.replace(',', '.'), errors='coerce')
        dp_list = [v for v in pd.concat([s1, s2]).dropna() if v > 0]
        
        m_wet = ((o2_mis/100 * 31.998) + (co2_mis/100 * 44.01) + ((100-o2_mis-co2_mis)/100 * 28.013)) * (1 - h2o/100) + (18.015 * h2o/100)
        rho_fumi = (p_ass_pa * m_wet) / (8314.472 * (t_fumi + 273.15))
        v_fumi = np.mean([np.sqrt(k_pit) * np.sqrt((2 * v * (9.80665 if unit=="mmH2O" else 1.0)) / rho_fumi) for v in dp_list]) if dp_list and rho_fumi > 0 else 0.0

        q_aq = v_fumi * (np.pi * d_cam**2 / 4) * 3600
        q_un_u = q_aq * (273.15 / (t_fumi + 273.15)) * (p_ass_hpa / 1013.25)
        q_un_s = q_un_u * (1 - h2o/100)
        q_rif = q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif)) if o2_mis < 20.8 else q_un_s

        # --- RISULTATI (INCLUSA PORTATA UMIDA) ---
        r1, r2 = st.columns(2)
        with r1:
            st.markdown(f"<div class='res-box' style='border-top:5px solid #1e40af'><p class='res-label-small'>VELOCITÀ</p><p class='res-val-big' style='color:#1e40af'>{v_fumi:.2f}</p><p class='res-label-small'>m/s</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box' style='border-top:5px solid #6b21a8'><p class='res-label-small'>PORTATA T.Q.</p><p class='res-val-big' style='color:#6b21a8; font-size:2.2rem !important'>{q_aq:.0f}</p><p class='res-label-small'>Am³/h</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box' style='border-top:5px solid #0ea5e9'><p class='res-label-small'>PORTATA UMIDA</p><p class='res-val-big' style='color:#0ea5e9; font-size:2.2rem !important'>{q_un_u:.0f}</p><p class='res-label-small'>Nm³/h (u)</p></div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='res-box' style='border-top:5px solid #16a34a'><p class='res-label-small'>PORTATA RIF O2</p><p class='res-val-big' style='color:#16a34a'>{q_rif:.0f}</p><p class='res-label-small'>Nm³/h</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box' style='border-top:5px solid #0891b2'><p class='res-label-small'>PORTATA SECCA</p><p class='res-val-big' style='color:#0891b2; font-size:2.2rem !important'>{q_un_s:.0f}</p><p class='res-label-small'>Nm³/h (s)</p></div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("<p style='font-size:1.2rem; font-weight:900; color:#92400e;'>🎯 PLANNING</p>", unsafe_allow_html=True)
        with st.container(border=True):
            t_amb = st.number_input("T. Ambiente (°C)", value=d['t_amb'])
            d_u = st.number_input("Ø Ugello (mm)", value=d['d_ugello_test'], step=0.5)
            if v_fumi > 0:
                q_p = (v_fumi * (np.pi * (d_u / 1000)**2 / 4) * 3600 * 1000 / 60) * (p_ass_hpa / p_atm) * ((t_amb + 273.15) / (t_fumi + 273.15))
                st.markdown(f"<div style='background:#000; padding:15px; border-radius:15px; color:#fbbf24; text-align:center;'><p style='margin:0; font-weight:800;'>TARGET POMPA</p><p style='font-size:3.2rem; font-weight:950; margin:0;'>{q_p:.2f}</p><p style='margin:0; font-weight:700;'>L/min (@{t_amb}°C)</p></div>", unsafe_allow_html=True)
                st.table(pd.DataFrame([{"Ø": f"{u}mm", "L/min": round((v_fumi * (np.pi*(u/1000)**2/4)*3600*1000/60)*(p_ass_hpa/p_atm)*((t_amb+273.15)/(t_fumi+273.15)), 2)} for u in [5, 6, 7, 8, 10, 12]]))
