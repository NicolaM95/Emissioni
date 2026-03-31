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
# 2. DINAMICA FUMI & PIANIFICAZIONE ISOCINETICA
# ==========================================
elif st.session_state.page == 'fumi':
    st.markdown("<h2 class='section-title'>📐 Dinamica dei Fumi & Planning Isocinetico</h2>", unsafe_allow_html=True)
    d = st.session_state.dati_dinamica
    
    # Inizializzazione parametri mancanti
    if 'co2' not in d: d['co2'] = 0.0
    if 'd_ugello_test' not in d: d['d_ugello_test'] = 6.0

    # Layout a tre colonne per una gestione più pulita
    col_input, col_mappa, col_planning = st.columns([1, 1.2, 1], gap="medium")
    
    with col_input:
        st.markdown("#### ⚙️ Input Tecnici")
        with st.expander("Geometria e Strumento", expanded=True):
            d_cam = st.number_input("Diametro Camino (m)", value=d['d_cam'], format="%.3f")
            k_interna = st.number_input("K Pitot (Targa)", value=d['k_pit'], format="%.3f")
            # Logica soglie ISO 16911
            if d_cam < 0.35: n_punti_fumi, coeffs = 1, [0.500]
            elif 0.35 <= d_cam < 1.10: n_punti_fumi, coeffs = 2, [0.146, 0.854]
            elif 1.10 <= d_cam < 1.60: n_punti_fumi, coeffs = 4, [0.067, 0.250, 0.750, 0.933]
            else: n_punti_fumi, coeffs = 6, [0.044, 0.146, 0.296, 0.704, 0.854, 0.956]
            st.caption(f"Configurazione: {n_punti_fumi} punti per asse.")

        with st.expander("Parametri Gas", expanded=True):
            t_fumi = st.number_input("T. Fumi (°C)", value=d['t_fumi'])
            p_atm = st.number_input("P. Atm (hPa)", value=d['p_atm'])
            p_stat_pa = st.number_input("P. Statica (Pa)", value=d['p_stat_pa'])
            h_in = st.number_input("H₂O (%)", value=d['h_in'])
            o2_mis = st.number_input("O₂ (%)", value=d['o2_mis'])
            co2_mis = st.number_input("CO₂ (%)", value=d['co2'])
            o2_rif = st.number_input("O₂ Rif.(%)", value=d['o2_rif'])

    with col_mappa:
        st.markdown("#### 📊 Mappatura ΔP")
        unit_dp = st.radio("Unità:", ["mmH2O", "Pa"], horizontal=True, label_visibility="collapsed")
        
        df_mappa = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(len(coeffs))],
            "Affond. (cm)": [round(d_cam * c * 100, 1) for c in coeffs],
            f"ΔP Asse 1": [0.0] * len(coeffs),
            f"ΔP Asse 2": [0.0] * len(coeffs)
        })
        edit_mappa = st.data_editor(df_mappa, hide_index=True, use_container_width=True, key=f"map_v_{unit_dp}")
        
        # --- CALCOLO MOTORE ---
        tutti_i_dp = pd.concat([edit_mappa.iloc[:,2], edit_mappa.iloc[:,3]]).tolist()
        lista_dp_validi = [v for v in tutti_i_dp if v > 0]
        
        # Densità e Massa Molecolare
        m_wet = ((o2_mis/100 * 31.998) + (co2_mis/100 * 44.01) + ((100-o2_mis-co2_mis)/100 * 28.013)) * (1 - h_in/100) + (18.015 * h_in/100)
        p_ass_pa = (p_atm * 100) + p_stat_pa
        rho_fumi = (p_ass_pa * m_wet) / (8314.472 * (t_fumi + 273.15))
        k_da_usare = np.sqrt(k_interna) if k_interna > 0 else 0
        
        velocita_punti = [k_da_usare * np.sqrt((2 * (dp * 9.80665 if unit_dp == "mmH2O" else dp)) / rho_fumi) for dp in lista_dp_validi if rho_fumi > 0]
        v_fumi = np.mean(velocita_punti) if velocita_punti else 0.0

    with col_planning:
        st.markdown("#### 🎯 Scelta Ugello")
        st.info("Calcolo del flusso di aspirazione per mantenere l'isocinetismo.")
        
        d_u = st.number_input("Ø Ugello selezionato (mm)", value=d['d_ugello_test'], step=1.0, format="%.1f")
        
        if v_fumi > 0:
            # Calcolo Area Ugello
            area_u = (np.pi * (d_u / 1000)**2) / 4
            # Flusso Isocinetico alle condizioni di camino (m3/h)
            q_iso_camino_m3h = v_fumi * area_u * 3600
            # Flusso Isocinetico in Litri al minuto (L/min) - Utile per settare la pompa
            q_iso_lmin = (q_iso_camino_m3h * 1000) / 60
            
            # Stima flusso al contatore (assumendo T_meter = 20°C e P_meter = P_atm)
            # Formula: Q_m = Q_f * (P_f / P_m) * (T_m / T_f)
            t_m_stima = 20.0
            q_meter_lmin = q_iso_lmin * (p_ass_pa / (p_atm * 100)) * ((t_m_stima + 273.15) / (t_fumi + 273.15))

            st.markdown(f"""
            <div style="background-color: #e8f4f8; padding: 15px; border-radius: 10px; border-left: 5px solid #3498db;">
                <span class="label-custom">Target Isocinetico (Camino)</span><br>
                <span style="font-size: 1.4rem; font-weight: bold; color: #2980b9;">{q_iso_lmin:.2f} L/min</span><br>
                <span class="label-custom">Flusso Stimato al Contatore (20°C)</span><br>
                <span style="font-size: 1.1rem; font-weight: 600; color: #16a085;">{q_meter_lmin:.2f} L/min</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Suggeritore rapido di ugelli
            st.write("---")
            st.caption("Tabella rapida (L/min teorici in camino):")
            ugelli_test = [4, 5, 6, 7, 8, 10, 12]
            quick_data = []
            for ut in ugelli_test:
                a_ut = (np.pi * (ut/1000)**2) / 4
                q_ut = (v_fumi * a_ut * 3600 * 1000) / 60
                quick_data.append({"Ø": f"{ut}mm", "L/min": round(q_ut, 2)})
            st.table(pd.DataFrame(quick_data))
        else:
            st.warning("Inserire i ΔP per calcolare il flusso.")

    # --- FOOTER RISULTATI FINALI ---
    area_cam = (np.pi * d_cam**2) / 4
    q_aq = v_fumi * area_cam * 3600
    q_un_s = q_aq * (273.15 / (t_fumi + 273.15)) * (p_ass_pa / 101325.0) * (1 - h_in/100)
    f_corr = (20.9 - o2_mis) / (20.9 - o2_rif) if o2_mis < 20.8 else 1.0
    q_rif = q_un_s * f_corr

    st.markdown(f"""
    <div class="result-card">
        <div style="display: flex; justify-content: space-between;">
            <div>
                <span class="label-custom">Velocità Media</span><br>
                <span class="value-main">{v_fumi:.2f} m/s</span>
            </div>
            <div style="text-align: center;">
                <span class="label-custom">Portata Normale Secca</span><br>
                <span class="value-main">{q_un_s:.0f} Nm³/h</span>
            </div>
            <div style="text-align: right;">
                <span class="label-custom">Portata di Riferimento (O₂)</span><br>
                <span class="value-highlight">{q_rif:.0f} Nm³/h</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("💾 Salva Dati e Configurazione Isocinetica", use_container_width=True):
        st.session_state.dati_dinamica.update({
            'v': v_fumi, 'q_rif': q_rif, 'rho': rho_fumi, 'd_cam': d_cam,
            'k_pit': k_interna, 't_fumi': t_fumi, 'h_in': h_in,
            'd_ugello_test': d_u, 'q_iso_target': q_iso_lmin
        })
        st.success("Dati salvati! Ora puoi procedere al campionamento.")
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
