import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v3.8 - FULL", layout="wide")

# CSS per Interfaccia e Validazione
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E3A8A; }
    .result-card { background-color: #f0f7ff; padding: 20px; border-radius: 15px; border: 1px solid #007bff; margin-bottom: 20px; }
    .metric-value { font-size: 20px; font-weight: bold; color: #1E3A8A; }
    .camp-container { border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; background-color: white; margin-bottom: 15px; }
    .stDataFrame div[data-testid="stTable"] { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE ---
# Inizializziamo h_in e altri parametri per evitare NameError all'avvio
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'dati_anagrafica' not in st.session_state: st.session_state.dati_anagrafica = {'tecnici': [], 'ditta': '', 'camino': ''}
if 'dati_dinamica' not in st.session_state: 
    st.session_state.dati_dinamica = {
        'h_in': 4.68, 't_fumi': 259.0, 'p_atm': 1013.25, 'p_stat_pa': -10.0,
        'o2_mis': 14.71, 'o2_rif': 8.0, 'd_cam': 1.4, 'k_pit': 0.69, 'n_punti': 4
    }
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
    st.button("🏠 Home", on_click=lambda: nav('home'), use_container_width=True)
    st.button("🗂️ Dati Generali & Tecnici", on_click=lambda: nav('anagrafica'), use_container_width=True)
    st.button("📐 Dinamica Fumi", on_click=lambda: nav('fumi'), use_container_width=True)
    st.button("💉 Campionamenti", on_click=lambda: nav('camp'), use_container_width=True)
    st.button("📄 Report Finale (RdP)", on_click=lambda: nav('rdp'), use_container_width=True)

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
# 2. DINAMICA FUMI (VERSIONE AGGIORNATA)
# ==========================================
elif st.session_state.page == 'fumi':
    st.header("📐 Dinamica dei Fumi (Mappatura Excel ISO 16911)")
    d = st.session_state.dati_dinamica
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("Parametri Condotto")
        d_cam = st.number_input("Diametro Camino (m)", value=d['d_cam'], format="%.3f")
        n_punti_default = st.number_input("Punti per ogni Asse (X, Y)", value=d['n_punti'], min_value=1, max_value=10)
        
        # K Pitot posizionato sotto i punti come richiesto
        k_pit = st.number_input("K Pitot", value=d['k_pit'])
        
        st.write("---")
        unit_dp = st.radio("Unità di misura per ΔP in tabella:", ["mmH2O", "Pa"], horizontal=True)
        
        st.write("---")
        st.subheader("Pressioni e Temperature")
        t_fumi = st.number_input("T. Fumi (°C)", value=d['t_fumi'])
        p_atm = st.number_input("P. Atmosferica (hPa)", value=d['p_atm'])
        p_stat_pa = st.number_input("P. Statica nel camino (Pa)", value=d['p_stat_pa'])
        
        # Calcolo Pressione Assoluta (P.atm + P.stat/100)
        p_ass_hpa = p_atm + (p_stat_pa / 100)
        st.metric("Pressione Assoluta", f"{p_ass_hpa:.2f} hPa")

        st.write("---")
        h_in = st.number_input("Umidità (%)", value=d['h_in'])
        o2_mis = st.number_input("O2 misurata (%)", value=d['o2_mis'])
        o2_rif = st.number_input("O2 riferimento (%)", value=d['o2_rif'])

    with c2:
        st.subheader(f"Mappatura ΔP ({unit_dp})")
        
        # --- LOGICA AFFONDAMENTI DA EXCEL ---
        # Coefficienti estratti dal tuo file (A3-A12)
        coeff_excel = [0.032, 0.105, 0.194, 0.323, 0.500, 0.677, 0.806, 0.895, 0.968]
        # Calcoliamo gli affondamenti in base al diametro e al numero di righe richiesto
        affondamenti = [round(d_cam * coeff_excel[i], 3) for i in range(min(int(n_punti_default), len(coeff_excel)))]
        
        df_mappa = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(len(affondamenti))],
            "Affondamento (m)": affondamenti,
            f"ΔP Asse X ({unit_dp})": [26.6 if unit_dp=="Pa" else 2.7] * len(affondamenti),
            f"ΔP Asse Y ({unit_dp})": [26.6 if unit_dp=="Pa" else 2.7] * len(affondamenti)
        })

        # La key dinamica resetta la tabella se cambia diametro o numero punti
        edit_mappa = st.data_editor(
            df_mappa, 
            hide_index=True, 
            use_container_width=True, 
            key=f"map_{d_cam}_{n_punti_default}_{unit_dp}"
        )
        
        # --- MOTORE DI CALCOLO ---
        col_x = f"ΔP Asse X ({unit_dp})"
        col_y = f"ΔP Asse Y ({unit_dp})"
        dp_medio_input = pd.concat([edit_mappa[col_x], edit_mappa[col_y]]).mean()

        # Conversioni
        dp_pa = dp_medio_input * 9.80665 if unit_dp == "mmH2O" else dp_medio_input
        dp_visual_mmH2O = dp_medio_input if unit_dp == "mmH2O" else dp_medio_input / 9.80665

        rho_fumi = 1.293 * (p_ass_hpa / 1013.25) * (273.15 / (t_fumi + 273.15))
        v_fumi = k_pit * np.sqrt((2 * dp_pa) / rho_fumi) if rho_fumi > 0 else 0
        area = (np.pi * d_cam**2) / 4
        q_aq = v_fumi * area * 3600
        
        # Calcolo Portata Secca (Usa h_in definita sopra)
        q_un_u = q_aq * (273.15/(t_fumi+273.15)) * (p_ass_hpa/1013.25)
        q_un_s = q_un_u * (1 - h_in/100)
        
        f_corr = (20.9 - o2_mis) / (20.9 - o2_rif) if o2_mis < 20.8 else 1.0
        q_rif = q_un_s * f_corr

        st.markdown(f"""
            <div class="result-card">
                <b>Pressione Assoluta:</b> {p_ass_hpa:.2f} hPa | <b>ΔP Medio:</b> {dp_visual_mmH2O:.3f} mmH2O<br>
                <b>Velocità:</b> {v_fumi:.2f} m/s | <b>Portata A.Q.:</b> {q_aq:.0f} Am³/h<br>
                <span style="color:green; font-size:20px;"><b>PORTATA RIFERITA: {q_rif:.0f} Nm³/h</b></span>
            </div>
        """, unsafe_allow_html=True)

        if st.button("💾 Salva Dinamica"):
            st.session_state.dati_dinamica.update({
                'h_in': h_in, 't_fumi': t_fumi, 'p_atm': p_atm, 'p_stat_pa': p_stat_pa,
                'o2_mis': o2_mis, 'o2_rif': o2_rif, 'd_cam': d_cam, 'k_pit': k_pit,
                'q_rif': q_rif, 'v': v_fumi, 'n_punti': n_punti_default, 'p_ass': p_ass_hpa
            })
            st.success("Dati dinamica archiviati correttamente.")

# ==========================================
# 3. CAMPIONAMENTI
# ==========================================
elif st.session_state.page == 'camp':
    if st.session_state.camp_attivo is None:
        st.header("💉 Gestione Campionamenti")
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
            if st.button("✅ CONFERMA"): st.session_state.step_camp = 'tabella'; st.rerun()

        elif st.session_state.step_camp == 'tabella':
            st.subheader(f"📊 Dati Campo - Camp. {curr['id']}")
            if st.button("⬅️ INDIETRO"): st.session_state.step_camp = 'selezione'; st.rerun()
            
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
    st.header("📄 Riepilogo Rapporto di Prova")
    d_anag = st.session_state.dati_anagrafica
    d_fumi = st.session_state.dati_dinamica
    st.write(f"**Ditta:** {d_anag.get('ditta', 'N.D.')} | **Camino:** {d_anag.get('camino', 'N.D.')}")
    st.write(f"**Portata Riferita:** {d_fumi.get('q_rif', 0):.0f} Nm³/h")
    st.write(f"**Velocità Media:** {d_fumi.get('v', 0):.2f} m/s")
