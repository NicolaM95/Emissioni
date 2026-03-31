import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v3.8 - FULL", layout="wide")

# --- INIZIALIZZAZIONE SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'bg_color' not in st.session_state: st.session_state.bg_color = '#FFFFFF'
if 'text_color' not in st.session_state: st.session_state.text_color = '#1E293B'
if 'dati_anagrafica' not in st.session_state:
    st.session_state.dati_anagrafica = {'tecnici': [], 'ditta': '', 'camino': ''}
if 'dati_dinamica' not in st.session_state: 
    st.session_state.dati_dinamica = {
        'h_in': 4.68, 't_fumi': 259.0, 'p_atm': 1013.25, 'p_stat_pa': -10.0,
        'o2_mis': 14.71, 'o2_rif': 8.0, 'd_cam': 1.4, 'k_pit': 0.69, 'n_punti': 4,
        'v': 0.0, 'q_rif': 0.0, 'co2': 0.0, 't_amb': 20.0, 'd_ugello_test': 6.0
    }
if 'lista_c' not in st.session_state: st.session_state.lista_c = []
if 'camp_attivo' not in st.session_state: st.session_state.camp_attivo = None
if 'step_camp' not in st.session_state: st.session_state.step_camp = 'selezione'

# --- CSS DINAMICO (SFONDO + CARD TRASPARENTI) ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {st.session_state.bg_color};
        color: {st.session_state.text_color};
    }}
    
    /* Card con trasparenza per adattarsi allo sfondo scelto */
    .res-box {{ 
        background: rgba(255, 255, 255, 0.85); 
        padding: 15px; 
        border-radius: 12px; 
        text-align: center; 
        border: 2px solid rgba(0,0,0,0.1); 
        margin-top: 10px;
        backdrop-filter: blur(5px);
    }}
    
    .section-title {{ 
        font-size: 2.8rem !important; 
        font-weight: 950; 
        color: {st.session_state.text_color} !important; 
        border-bottom: 6px solid #2563eb; 
        margin-bottom: 20px; 
    }}

    /* STILE INPUT RICHIESTO: font-size:1.5rem; font-weight:900; color:#2563eb */
    .stNumberInput input {{ font-size: 1.5rem !important; font-weight: 900 !important; color: #2563eb !important; }}
    .stNumberInput label {{ font-size: 1.2rem !important; font-weight: 800 !important; color: {st.session_state.text_color} !important; }}
    
    .res-val-big {{ font-size: 3.2rem !important; font-weight: 950 !important; line-height: 1; margin: 5px 0; }}
    .res-label-small {{ font-size: 1rem; font-weight: 800; color: #475569; text-transform: uppercase; }}

    /* Tabella */
    [data-testid="stTable"] td {{ font-size: 1.3rem !important; font-weight: 700 !important; color: #000 !important; }}
    div[data-testid="stDataFrame"] {{ font-size: 1.3rem !important; }}
    </style>
    """, unsafe_allow_html=True)

PARAMETRI_BASE = ["Polveri Totali", "Acidi (SOx, HCl, HF)", "SOx", "HCl", "HF", "Metalli", "Mercurio (Hg)", "Ammoniaca (NH3)", "SOV (COV)", "Formaldeide"]

def nav(p): st.session_state.page = p

# --- SIDEBAR ---
with st.sidebar:
    st.title("📑 MENU")
    st.button("🏠 Home", on_click=lambda: nav('home'), use_container_width=True)
    st.button("🗂️ Anagrafica", on_click=lambda: nav('anagrafica'), use_container_width=True)
    st.button("📐 Dinamica Fumi", on_click=lambda: nav('fumi'), use_container_width=True)
    st.button("💉 Campionamenti", on_click=lambda: nav('camp'), use_container_width=True)

# ==========================================
# 1. HOME & THEME SELECTOR
# ==========================================
if st.session_state.page == 'home':
    st.markdown("<h1 class='section-title'>🏠 Dashboard Emissioni</h1>", unsafe_allow_html=True)
    
    temi = {
        "Industrial White": ["#FFFFFF", "#1E293B"],
        "Slate Dark": ["#1E293B", "#F8FAFC"],
        "Deep Ocean": ["#0F172A", "#F1F5F9"],
        "Green Energy": ["#064E3B", "#F0FDF4"],
        "Technical Grey": ["#475569", "#FFFFFF"],
        "Midnight": ["#000000", "#FFFFFF"],
        "Sand": ["#F5F5DC", "#1E293B"],
        "Nordic Blue": ["#334155", "#E2E8F0"],
        "Soft Graphite": ["#27272A", "#F4F4F5"],
        "Cyber Punk": ["#2D1B4E", "#F5F3FF"]
    }

    with st.container(border=True):
        st.subheader("🎨 Personalizzazione Sfondo (Ottimizzazione iPad/PC)")
        scelta = st.selectbox("Scegli un tema visivo:", list(temi.keys()))
        if st.button("Applica Tema"):
            st.session_state.bg_color = temi[scelta][0]
            st.session_state.text_color = temi[scelta][1]
            st.rerun()

    st.info("Configurazione completata. Seleziona una sezione dal menu laterale per iniziare.")

# ==========================================
# 2. ANAGRAFICA
# ==========================================
elif st.session_state.page == 'anagrafica':
    st.markdown("<h2 class='section-title'>🗂️ Dati Generali</h2>", unsafe_allow_html=True)
    with st.form("anag_form"):
        st.session_state.dati_anagrafica['ditta'] = st.text_input("Ditta Cliente", st.session_state.dati_anagrafica.get('ditta',''))
        st.session_state.dati_anagrafica['camino'] = st.text_input("Nome Camino", st.session_state.dati_anagrafica.get('camino',''))
        tecnici_str = st.text_area("Tecnici Operanti", value="\n".join(st.session_state.dati_anagrafica.get('tecnici', [])))
        if st.form_submit_button("💾 Salva"):
            st.session_state.dati_anagrafica['tecnici'] = tecnici_str.split("\n")
            st.success("Dati salvati!")

# ==========================================
# 3. DINAMICA FUMI (LAYOUT CENTRALE + PORTATA SECCA)
# ==========================================
elif st.session_state.page == 'fumi':
    st.markdown("<h1 class='section-title'>📐 DINAMICA FUMI & PLANNING</h1>", unsafe_allow_html=True)
    d = st.session_state.dati_dinamica
    
    col_left, col_mid, col_right = st.columns([1, 1.4, 1], gap="medium")
    
    with col_left:
        with st.container(border=True):
            st.markdown("<p style='font-size:1.3rem; font-weight:900; color:#2563eb;'>⚙️ PARAMETRI</p>", unsafe_allow_html=True)
            d_cam = st.number_input("Diametro Camino (m)", value=d['d_cam'], format="%.3f")
            k_pit = st.number_input("K Pitot (Targa)", value=d['k_pit'], format="%.3f")
            
            if d_cam < 0.35: n_punti, coeffs = 1, [0.500]
            elif d_cam < 1.10: n_punti, coeffs = 2, [0.146, 0.854]
            elif d_cam < 1.60: n_punti, coeffs = 4, [0.067, 0.250, 0.750, 0.933]
            else: n_punti, coeffs = 6, [0.044, 0.146, 0.296, 0.704, 0.854, 0.956]
            
            st.error(f"PUNTI: {n_punti} per asse")
            t_fumi = st.number_input("T. Fumi (°C)", value=d['t_fumi'])
            p_atm = st.number_input("P. Atm (hPa)", value=d['p_atm'])
            p_stat = st.number_input("P. Statica (Pa)", value=d['p_stat_pa'])
            h2o = st.number_input("H₂O (%)", value=d['h_in'])
            o2_mis = st.number_input("O₂ (%)", value=d['o2_mis'])
            co2_mis = st.number_input("CO₂ (%)", value=d['co2'])
            o2_rif = st.number_input("O₂ Rif (%)", value=d['o2_rif'])

    with col_mid:
        st.markdown("<p style='font-size:1.3rem; font-weight:900; color:#166534;'>📊 MAPPATURA ΔP</p>", unsafe_allow_html=True)
        unit = st.radio("Unità:", ["mmH2O", "Pa"], horizontal=True, label_visibility="collapsed")
        
        df_init = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(len(coeffs))],
            "Aff. (cm)": [round(d_cam * c * 100, 1) for c in coeffs],
            "Asse 1": [None] * len(coeffs), "Asse 2": [None] * len(coeffs)
        })
        
        edit_mappa = st.data_editor(df_init, hide_index=True, use_container_width=True, key=f"ed_v9_{unit}")
        
        # --- CALCOLI (CO2 E ANTI-ERRORE VIRGOLA) ---
        p_ass_pa = (p_atm * 100) + p_stat
        p_ass_hpa = p_ass_pa / 100
        s1 = pd.to_numeric(edit_mappa["Asse 1"].astype(str).str.replace(',', '.'), errors='coerce')
        s2 = pd.to_numeric(edit_mappa["Asse 2"].astype(str).str.replace(',', '.'), errors='coerce')
        dp_list = [v for v in pd.concat([s1, s2]).dropna() if v > 0]
        
        m_wet = ((o2_mis/100 * 31.998) + (co2_mis/100 * 44.01) + ((100-o2_mis-co2_mis)/100 * 28.013)) * (1 - h2o/100) + (18.015 * h2o/100)
        rho_fumi = (p_ass_pa * m_wet) / (8314.472 * (t_fumi + 273.15))
        v_fumi = np.mean([np.sqrt(k_pit) * np.sqrt((2 * v * (9.80665 if unit=="mmH2O" else 1.0)) / rho_fumi) for v in dp_list]) if dp_list and rho_fumi > 0 else 0.0

        area_cam = (np.pi * d_cam**2) / 4
        q_aq = v_fumi * area_cam * 3600
        q_un_u = q_aq * (273.15 / (t_fumi + 273.15)) * (p_ass_hpa / 1013.25)
        q_un_s = q_un_u * (1 - h2o/100)
        q_rif = q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif)) if o2_mis < 20.8 else q_un_s

        # --- RISULTATI SOTTO TABELLA ---
        r_c1, r_c2 = st.columns(2)
        with r_c1:
            st.markdown(f"<div class='res-box' style='border-top:5px solid #1e40af'><p class='res-label-small'>VELOCITÀ</p><p class='res-val-big' style='color:#1e40af'>{v_fumi:.2f}</p><p class='res-label-small'>m/s</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box' style='border-top:5px solid #6b21a8'><p class='res-label-small'>PORTATA T.Q.</p><p class='res-val-big' style='color:#6b21a8; font-size:2.4rem !important'>{q_aq:.0f}</p><p class='res-label-small'>Am³/h</p></div>", unsafe_allow_html=True)
        with r_c2:
            st.markdown(f"<div class='res-box' style='border-top:5px solid #16a34a'><p class='res-label-small'>PORTATA RIF O2</p><p class='res-val-big' style='color:#16a34a'>{q_rif:.0f}</p><p class='res-label-small'>Nm³/h</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='res-box' style='border-top:5px solid #0891b2'><p class='res-label-small'>PORTATA SECCA</p><p class='res-val-big' style='color:#0891b2; font-size:2.4rem !important'>{q_un_s:.0f}</p><p class='res-label-small'>Nm³/h (s)</p></div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<p style='font-size:1.3rem; font-weight:900; color:#92400e;'>🎯 PLANNING</p>", unsafe_allow_html=True)
        with st.container(border=True):
            t_amb = st.number_input("T. Ambiente (°C)", value=d['t_amb'])
            d_u = st.number_input("Ø Ugello (mm)", value=d['d_ugello_test'], step=0.5)
            if v_fumi > 0:
                q_p = (v_fumi * (np.pi * (d_u / 1000)**2 / 4) * 3600 * 1000 / 60) * (p_ass_hpa / p_atm) * ((t_amb + 273.15) / (t_fumi + 273.15))
                st.markdown(f"<div style='background:#000; padding:15px; border-radius:15px; color:#fbbf24; text-align:center;'><p style='margin:0; font-weight:800;'>TARGET POMPA</p><p style='font-size:3.2rem; font-weight:950; margin:0;'>{q_p:.2f}</p><p style='margin:0; font-weight:700;'>L/min (@{t_amb}°C)</p></div>", unsafe_allow_html=True)
                u_list = [5, 6, 7, 8, 10, 12]
                st.table(pd.DataFrame([{"Ø": f"{u}mm", "L/min": round((v_fumi * (np.pi*(u/1000)**2/4)*3600*1000/60)*(p_ass_hpa/p_atm)*((t_amb+273.15)/(t_fumi+273.15)), 2)} for u in u_list]))

    if st.button("💾 SALVA DEFINITIVAMENTE", use_container_width=True, type="primary"):
        st.session_state.dati_dinamica.update({'v': v_fumi, 'q_aq': q_aq, 'q_rif': q_rif, 'q_un_s': q_un_s, 'p_ass': p_ass_hpa, 'co2': co2_mis, 't_amb': t_amb})
        st.success("Dati salvati!")

# ==========================================
# 4. CAMPIONAMENTI
# ==========================================
elif st.session_state.page == 'camp':
    if st.session_state.camp_attivo is None:
        st.markdown("<h2 class='section-title'>💉 Campionamenti</h2>", unsafe_allow_html=True)
        if st.button("➕ AGGIUNGI", use_container_width=True):
            st.session_state.lista_c.append({'id': len(st.session_state.lista_c)+1, 'main': [], 'punti': 4, 'dati': None})
            st.rerun()
        
        for i, c in enumerate(st.session_state.lista_c):
            with st.container(border=True):
                st.write(f"### 📦 Campionamento n° {c['id']} - ({', '.join(c['main'])})")
                c1, c2 = st.columns(2)
                if c1.button("📊 APRI", key=f"op_{i}", use_container_width=True):
                    st.session_state.camp_attivo = i; st.session_state.step_camp = 'selezione'; st.rerun()
                if c2.button("🗑️ ELIMINA", key=f"dl_{i}", use_container_width=True):
                    st.session_state.lista_c.pop(i); st.rerun()
    
    else:
        idx = st.session_state.camp_attivo
        curr = st.session_state.lista_c[idx]
        if st.session_state.step_camp == 'selezione':
            st.subheader(f"⚙️ Parametri - Campionamento {curr['id']}")
            m_cols = st.columns(4)
            for j, p in enumerate(PARAMETRI_BASE):
                if m_cols[j % 4].checkbox(p, key=f"m_{idx}_{p}", value=(p in curr['main'])):
                    if p not in curr['main']: curr['main'].append(p)
                else:
                    if p in curr['main']: curr['main'].remove(p)
            if st.button("✅ PROCEDI"): st.session_state.step_camp = 'tabella'; st.rerun()
 
        elif st.session_state.step_camp == 'tabella':
            st.subheader(f"📊 Dati Campo - Camp. {curr['id']}")
            if st.button("⬅️ INDIETRO"): st.session_state.step_camp = 'selezione'; st.rerun()
            if curr.get('dati') is None:
                curr['dati'] = pd.DataFrame(0.0, index=range(curr['punti']), columns=["Punto", "ΔP (Pa)", "T Fumi (°C)", "Vol (L)", "Isocinetismo %"])
                curr['dati']["Punto"] = [f"P{k+1}" for k in range(curr['punti'])]
            st.data_editor(curr['dati'], use_container_width=True, hide_index=True)
            if st.button("💾 SALVA"): st.session_state.camp_attivo = None; st.balloons(); st.rerun()
