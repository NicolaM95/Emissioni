import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
 
# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v3.8 - FULL", layout="wide")
 
# ==========================================
# CSS CUSTOM - DESIGN MODERNO (SFONDO BIANCO)
# ==========================================
st.markdown("""
    <style>
    /* Sfondo principale chiaro */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Intestazioni principali */
    .main-header { 
        font-size: 26px;
        font-weight: bold; 
        color: #1a1c2e; 
    }
    
    /* Card dei risultati tipo dashboard professionale */
    .result-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* Titoli e Label interne */
    .section-title {
        color: #1a1c2e;
        font-weight: 700;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5px;
        margin-bottom: 15px;
    }
    
    .label-custom {
        color: #6c757d;
        font-size: 0.85rem;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Valori in risalto */
    .value-main {
        color: #2c3e50;
        font-size: 1.8rem;
        font-weight: 800;
    }

    .value-highlight {
        color: #27ae60;
        font-size: 2.2rem;
        font-weight: 800;
    }
    
    /* Sidebar restyling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }

    /* Contenitori Campionamento */
    .camp-container { 
        border: 1px solid #e0e0e0; 
        padding: 15px; 
        border-radius: 10px; 
        background-color: white;
        margin-bottom: 15px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .stDataFrame div[data-testid="stTable"] { width: 100%; }
    </style>
    """, unsafe_allow_html=True)
 
# --- INIZIALIZZAZIONE ---
if 'page' not in st.session_state: 
    st.session_state.page = 'home'
if 'dati_anagrafica' not in st.session_state:
    st.session_state.dati_anagrafica = {'tecnici': [], 'ditta': '', 'camino': ''}
if 'dati_dinamica' not in st.session_state: 
    st.session_state.dati_dinamica = {
        'h_in': 4.68, 't_fumi': 259.0, 'p_atm': 1013.25, 'p_stat_pa': -10.0,
        'o2_mis': 14.71, 'o2_rif': 8.0, 'd_cam': 1.4, 'k_pit': 0.69, 'n_punti': 4,
        'v': 0.0, 'q_rif': 0.0
    }
if 'lista_c' not in st.session_state:
    st.session_state.lista_c = []
if 'camp_attivo' not in st.session_state:
    st.session_state.camp_attivo = None
if 'step_camp' not in st.session_state: 
    st.session_state.step_camp = 'selezione'
 
PARAMETRI_BASE = [
    "Polveri Totali", "Acidi (SOx, HCl, HF)", "SOx", "HCl", "HF", "SO3",
    "Cromo VI", "Metalli (EN 14385)", "Mercurio (Hg)", "Ammoniaca (NH3)", 
    "PM10", "PM2.5", "SOV (COV)", "Formaldeide", "Benzolo", "Aldeidi"
]
 
def nav(p):
    st.session_state.page = p
 
# --- SIDEBAR ---
with st.sidebar:
    st.title("📑 MENU PRINCIPALE")
    st.button("🏠 Home", on_click=lambda: nav('home'), use_container_width=True)
    st.button("🗂️ Dati Generali & Tecnici", on_click=lambda: nav('anagrafica'), use_container_width=True)
    st.button("📐 Dinamica Fumi", on_click=lambda: nav('fumi'), use_container_width=True)
    st.button("💉 Campionamenti", on_click=lambda: nav('camp'), use_container_width=True)
    st.button("📄 Report Finale (RdP)", on_click=lambda: nav('rdp'), use_container_width=True)
 
# ==========================================
# 1. DATI GENERALI & TECNICI
# ==========================================
if st.session_state.page == 'anagrafica':
    st.markdown("<h2 class='section-title'>🗂️ Dati Generali e Team Tecnico</h2>", unsafe_allow_html=True)
    with st.form("anag_form"):
        st.session_state.dati_anagrafica['ditta'] = st.text_input("Ditta Cliente", st.session_state.dati_anagrafica.get('ditta',''))
        st.session_state.dati_anagrafica['camino'] = st.text_input("Nome Camino", st.session_state.dati_anagrafica.get('camino',''))
        st.write("---")
        tecnici_str = st.text_area("Tecnici Operanti (uno per riga)", value="\n".join(st.session_state.dati_anagrafica.get('tecnici', [])))
        if st.form_submit_button("💾 Salva Dati"):
            st.session_state.dati_anagrafica['tecnici'] = tecnici_str.split("\n")
            st.success("Dati Generali e Team salvati!")
 
# ==========================================
# 2. DINAMICA FUMI & PLANNING (LAYOUT OTTIMIZZATO V6.5)
# ==========================================
elif st.session_state.page == 'fumi':
    st.markdown("""
        <style>
        .section-title { font-size: 2.8rem !important; font-weight: 950; color: #1e293b; border-bottom: 6px solid #2563eb; margin-bottom: 20px; }
        .stNumberInput label, .stRadio label { font-size: 1.3rem !important; font-weight: 800 !important; }
        
        /* Card di Design */
        .color-card { padding: 20px; border-radius: 15px; margin-bottom: 15px; border: 2px solid rgba(0,0,0,0.05); }
        .card-header { font-size: 1.6rem !important; font-weight: 900 !important; margin-bottom: 10px; border-bottom: 2px solid rgba(0,0,0,0.1); }
        
        /* Dashboard Risultati (Spostata al centro) */
        .res-box { background: #ffffff; padding: 15px; border-radius: 12px; text-align: center; border: 2px solid #e2e8f0; margin-top: 10px; }
        .res-val-big { font-size: 3.5rem !important; font-weight: 950 !important; line-height: 1; margin: 5px 0; }
        .res-label-small { font-size: 1rem; font-weight: 800; color: #64748b; text-transform: uppercase; }
        
        /* Tabella Data Editor - Aumento leggibilità */
        [data-testid="stTable"] td, [data-testid="stDataFrame"] td { font-size: 1.5rem !important; font-weight: 700 !important; }
        div[data-testid="stDataFrame"] { font-size: 1.4rem !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='section-title'>📐 DINAMICA FUMI & PLANNING</h1>", unsafe_allow_html=True)
    d = st.session_state.dati_dinamica
    
    # Init parametri
    for k, v in {'t_amb': 20.0, 'd_ugello_test': 6.0, 'co2': 0.0}.items():
        if k not in d: d[k] = v

    col_left, col_mid, col_right = st.columns([1, 1.4, 1], gap="medium")
    
    # --- COLONNA SINISTRA: INPUT ---
    with col_left:
        with st.container(border=True):
            st.markdown("<p style='font-size:1.5rem; font-weight:900; color:#2563eb;'>⚙️ PARAMETRI</p>", unsafe_allow_html=True)
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

    # --- COLONNA CENTRALE: MAPPATURA + RISULTATI (SPOSTATI QUI) ---
    with col_mid:
        st.markdown("<p style='font-size:1.5rem; font-weight:900; color:#166534;'>📊 MAPPATURA ΔP</p>", unsafe_allow_html=True)
        unit = st.radio("Unità:", ["mmH2O", "Pa"], horizontal=True, label_visibility="collapsed")
        
        df_init = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(len(coeffs))],
            "Aff. (cm)": [round(d_cam * c * 100, 1) for c in coeffs],
            "Asse 1": [None] * len(coeffs),
            "Asse 2": [None] * len(coeffs)
        })
        
        edit_mappa = st.data_editor(df_init, hide_index=True, use_container_width=True, key=f"ed_v7_{unit}")
        
        # --- LOGICA DI CALCOLO CON FIX VIRGOLA ---
        p_ass_pa = (p_atm * 100) + p_stat
        p_ass_hpa = p_ass_pa / 100

        def clean_val(series):
            # Converte virgole in punti se l'utente inserisce stringhe, poi forza a numerico
            return pd.to_numeric(series.astype(str).str.replace(',', '.'), errors='coerce')

        dp_list = pd.concat([clean_val(edit_mappa["Asse 1"]), clean_val(edit_mappa["Asse 2"])]).dropna()
        dp_list = dp_list[dp_list > 0].tolist()
        
        m_wet = ((o2_mis/100 * 31.998) + (co2_mis/100 * 44.01) + ((100-o2_mis-co2_mis)/100 * 28.013)) * (1 - h2o/100) + (18.015 * h2o/100)
        rho_fumi = (p_ass_pa * m_wet) / (8314.472 * (t_fumi + 273.15)) if (t_fumi + 273.15) > 0 else 1.2
        v_fumi = np.mean([np.sqrt(k_pit) * np.sqrt((2 * v * (9.80665 if unit == "mmH2O" else 1.0)) / rho_fumi) for v in dp_list]) if dp_list and rho_fumi > 0 else 0.0

        # --- DASHBOARD RISULTATI (SOTTO LA TABELLA) ---
        area_cam = (np.pi * d_cam**2) / 4
        q_aq = v_fumi * area_cam * 3600
        q_un_u = q_aq * (273.15 / (t_fumi + 273.15)) * (p_ass_hpa / 1013.25)
        q_un_s = q_un_u * (1 - h2o/100)
        q_rif = q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif)) if o2_mis < 20.8 else q_un_s

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.markdown(f"""<div class='res-box' style='border-top:5px solid #1e40af'><p class='res-label-small'>VELOCITÀ</p><p class='res-val-big' style='color:#1e40af'>{v_fumi:.2f}</p><p class='res-label-small'>m/s</p></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class='res-box'><p class='res-label-small'>PORTATA T.Q.</p><p class='res-val-big' style='font-size:2.5rem !important'>{q_aq:.0f}</p><p class='res-label-small'>Am³/h</p></div>""", unsafe_allow_html=True)
        with res_col2:
            st.markdown(f"""<div class='res-box' style='border-top:5px solid #16a34a'><p class='res-label-small'>PORTATA RIF O2</p><p class='res-val-big' style='color:#16a34a'>{q_rif:.0f}</p><p class='res-label-small'>Nm³/h</p></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class='res-box'><p class='res-label-small'>PORTATA N. UMIDA</p><p class='res-val-big' style='font-size:2.5rem !important'>{q_un_u:.0f}</p><p class='res-label-small'>Nm³/h</p></div>""", unsafe_allow_html=True)

    # --- COLONNA DESTRA: PLANNING UGELLO ---
    with col_right:
        st.markdown("<p style='font-size:1.5rem; font-weight:900; color:#92400e;'>🎯 PLANNING</p>", unsafe_allow_html=True)
        with st.container(border=True):
            t_amb = st.number_input("T. Ambiente (°C)", value=d['t_amb'])
            d_u = st.number_input("Ø Ugello (mm)", value=d['d_ugello_test'], step=0.5)
            
            if v_fumi > 0:
                q_p = (v_fumi * (np.pi * (d_u / 1000)**2 / 4) * 3600 * 1000 / 60) * (p_ass_hpa / p_atm) * ((t_amb + 273.15) / (t_fumi + 273.15))
                st.markdown(f"""<div style='background:#000; padding:20px; border-radius:15px; color:#fbbf24; text-align:center;'>
                    <p style='margin:0; font-weight:800;'>TARGET ALLA POMPA</p>
                    <p style='font-size:3.5rem; font-weight:950; margin:0;'>{q_p:.2f}</p>
                    <p style='margin:0; font-weight:700;'>L/min (@{t_amb}°C)</p>
                </div>""", unsafe_allow_html=True)
                
                u_list = [5, 6, 7, 8, 10, 12]
                st.table(pd.DataFrame([{"Ø": f"{u}mm", "L/min": round((v_fumi * (np.pi*(u/1000)**2/4)*3600*1000/60)*(p_ass_hpa/p_atm)*((t_amb+273.15)/(t_fumi+273.15)), 2)} for u in u_list]))

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 SALVA DATI E PROCEDI", use_container_width=True, type="primary"):
        st.session_state.dati_dinamica.update({'v': v_fumi, 'q_aq': q_aq, 'q_rif': q_rif, 'p_ass': p_ass_hpa, 't_amb': t_amb, 'd_ugello_test': d_u})
        st.success("Dati salvati!")
# ==========================================
# 3. CAMPIONAMENTI
# ==========================================
elif st.session_state.page == 'camp':
    if st.session_state.camp_attivo is None:
        st.markdown("<h2 class='section-title'>💉 Gestione Campionamenti</h2>", unsafe_allow_html=True)
        if st.button("➕ AGGIUNGI CAMPIONAMENTO", use_container_width=True):
            st.session_state.lista_c.append({'id': len(st.session_state.lista_c)+1, 'main': [], 'sep': [], 'punti': 4, 'dati': None})
            st.rerun()
        
        for i, c in enumerate(st.session_state.lista_c):
            with st.container():
                st.markdown(f"<div class='camp-container'>", unsafe_allow_html=True)
                ca1, ca2, ca3 = st.columns([4, 1, 1])
                ca1.write(f"### 📦 Campionamento n° {c['id']} - ({', '.join(c['main'] + c['sep'])})")
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
            st.write("#### 🟦 LINEA ISOCINETICA")
            m_cols = st.columns(4)
            for j, p in enumerate(PARAMETRI_BASE):
                with m_cols[j % 4]:
                    if st.checkbox(p, key=f"m_{idx}_{p}", value=(p in curr['main'])):
                        if p not in curr['main']: curr['main'].append(p)
                    else:
                        if p in curr['main']: curr['main'].remove(p)
            
            curr['punti'] = st.number_input("Punti Campionamento", min_value=1, value=curr['punti'])
            if st.button("✅ CONFERMA"):
                st.session_state.step_camp = 'tabella'; st.rerun()
 
        elif st.session_state.step_camp == 'tabella':
            st.subheader(f"📊 Dati Campo - Camp. {curr['id']}")
            if st.button("⬅️ INDIETRO"):
                st.session_state.step_camp = 'selezione'; st.rerun()
            
            cols = ["Punto", "ΔP (Pa)", "T Fumi (°C)", "Vol (L)", "Isocinetismo %"]
            if curr.get('dati') is None or len(curr['dati']) != curr['punti']:
                df_init = pd.DataFrame(0.0, index=range(curr['punti']), columns=cols)
                df_init["Punto"] = [f"P{k+1}" for k in range(curr['punti'])]
                df_init["Isocinetismo %"] = 100.0
                curr['dati'] = df_init
 
            edited_df = st.data_editor(curr['dati'], use_container_width=True, hide_index=True, key=f"edit_camp_{idx}")
            
            if st.button("💾 SALVA DEFINITIVAMENTE"):
                st.session_state.lista_c[idx]['dati'] = edited_df
                st.session_state.camp_attivo = None
                st.balloons(); st.rerun()
 
# ==========================================
# 4. ALTRE PAGINE (HOME & RDP)
# ==========================================
elif st.session_state.page == 'home':
    st.markdown("<p class='main-header'>🏭 Emissioni Pro v3.8</p>", unsafe_allow_html=True)
    st.info("Benvenuto. Usa il menu laterale per navigare tra le sezioni del rapporto.")
 
elif st.session_state.page == 'rdp':
    st.markdown("<h2 class='section-title'>📄 Riepilogo Rapporto di Prova</h2>", unsafe_allow_html=True)
    d_anag = st.session_state.dati_anagrafica
    d_fumi = st.session_state.dati_dinamica
    st.write(f"**Ditta:** {d_anag.get('ditta', 'N.D.')} | **Camino:** {d_anag.get('camino', 'N.D.')}")
    st.write(f"**Portata Riferita:** {d_fumi.get('q_rif', 0):.0f} Nm³/h")
    st.write(f"**Velocità Media:** {d_fumi.get('v', 0):.2f} m/s")
