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
# 2. DINAMICA FUMI (LOGICA ISO 16911 - K-INTERNA -> RADICE -> K-ESTERNA)
# ==========================================
elif st.session_state.page == 'fumi':
    st.markdown("<h2 class='section-title'>📐 Dinamica dei Fumi (Mappatura ISO 16911)</h2>", unsafe_allow_html=True)
    d = st.session_state.dati_dinamica
    
    # Inizializzazione CO2 se assente nel dizionario
    if 'co2' not in d: d['co2'] = 0.0 

    c1, c2 = st.columns([1.2, 2], gap="large")
    
    with c1:
        st.markdown("<h4 style='color: #2c3e50; font-weight: 600; margin-bottom: 0;'>⚙️ Parametri di Condotto e Campionamento</h4>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        # --- SEZIONE 1: GEOMETRIA E STRUMENTO ---
        st.markdown("**1. Geometria e Strumentazione**")
        col_diam, col_k = st.columns(2)
        d_cam = col_diam.number_input("Diametro Camino (m)", value=d['d_cam'], format="%.3f")
        k_interna = col_k.number_input("K Pitot (Interna)", value=d['k_pit'], format="%.3f", help="Inserire la costante di targa. Il software ne calcolerà la radice quadrata per la formula UNI EN 16911.")
        
        # Logica Soglie ISO 16911 per configurazione punti
        if d_cam < 0.35: n_punti_fumi, coeffs = 1, [0.500]
        elif 0.35 <= d_cam < 1.10: n_punti_fumi, coeffs = 2, [0.146, 0.854]
        elif 1.10 <= d_cam < 1.60: n_punti_fumi, coeffs = 4, [0.067, 0.250, 0.750, 0.933]
        elif 1.60 <= d_cam < 2.25: n_punti_fumi, coeffs = 6, [0.044, 0.146, 0.296, 0.704, 0.854, 0.956]
        elif 2.25 <= d_cam < 2.50: n_punti_fumi, coeffs = 8, [0.032, 0.105, 0.194, 0.323, 0.677, 0.806, 0.895, 0.968]
        else: n_punti_fumi, coeffs = 10, [0.026, 0.082, 0.146, 0.226, 0.342, 0.658, 0.774, 0.854, 0.918, 0.974]
        
        st.caption(f"🔹 *Configurazione norma: {n_punti_fumi} punti per asse.*")

        # --- SEZIONE 2: TERMODINAMICA ---
        st.markdown("<br>**2. Termodinamica Fumi**", unsafe_allow_html=True)
        col_t, col_patm, col_pstat = st.columns(3)
        t_fumi = col_t.number_input("T. Fumi (°C)", value=d['t_fumi'])
        p_atm = col_patm.number_input("P. Atm (hPa)", value=d['p_atm'])
        p_stat_pa = col_pstat.number_input("P. Statica (Pa)", value=d['p_stat_pa'])
        
        p_ass_hpa = p_atm + (p_stat_pa / 100)
        
        # --- SEZIONE 3: COMPOSIZIONE GAS ---
        st.markdown("<br>**3. Composizione Gas**", unsafe_allow_html=True)
        c_h2o, c_o2, c_co2, c_o2r = st.columns(4)
        h_in = c_h2o.number_input("H₂O (%)", value=d['h_in'])
        o2_mis = c_o2.number_input("O₂ (%)", value=d['o2_mis'])
        co2_mis = c_co2.number_input("CO₂ (%)", value=d['co2'])
        o2_rif = c_o2r.number_input("O₂ Rif.(%)", value=d['o2_rif'])

    with c2:
        st.markdown("<h4 style='color: #2c3e50; font-weight: 600; margin-bottom: 0;'>📊 Mappatura Velocità (ΔP)</h4>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        unit_dp = st.radio("Unità di misura ΔP:", ["mmH2O", "Pa"], horizontal=True, label_visibility="collapsed")
        
        df_mappa = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(len(coeffs))],
            "Affondamento (cm)": [round(d_cam * c * 100, 1) for c in coeffs],
            f"ΔP Asse 1 ({unit_dp})": [0.0] * len(coeffs),
            f"ΔP Asse 2 ({unit_dp})": [0.0] * len(coeffs)
        })

        edit_mappa = st.data_editor(df_mappa, hide_index=True, use_container_width=True, key=f"map_v_final_{unit_dp}")
        
        # ==========================================
        # MOTORE DI CALCOLO UNI EN 16911-1
        # ==========================================
        
        # 1. Recupero dati e filtro zeri
        tutti_i_dp = pd.concat([edit_mappa.iloc[:,2], edit_mappa.iloc[:,3]]).tolist()
        lista_dp_validi = [v for v in tutti_i_dp if v > 0]
        
        # 2. Calcolo Densità Reale (rho_f)
        m_dry = (o2_mis/100 * 31.998) + (co2_mis/100 * 44.01) + ((100-o2_mis-co2_mis)/100 * 28.013)
        bws = h_in / 100
        m_wet = m_dry * (1 - bws) + (18.015 * bws)
        
        p_ass_pa = (p_atm * 100) + p_stat_pa 
        t_ass_k = t_fumi + 273.15
        rho_fumi = (p_ass_pa * m_wet) / (8314.472 * t_ass_k)
        
        # 3. TRASFORMAZIONE K (Radice Quadrata della K interna inserita)
        k_da_usare = np.sqrt(k_interna) if k_interna > 0 else 0
        
        velocita_punti = []
        for dp in lista_dp_validi:
            dp_pa_val = dp * 9.80665 if unit_dp == "mmH2O" else dp
            if rho_fumi > 0:
                v_punto = k_da_usare * np.sqrt((2 * dp_pa_val) / rho_fumi)
                velocita_punti.append(v_punto)
        
        v_fumi = np.mean(velocita_punti) if velocita_punti else 0.0

        # 4. Calcolo Portate Finali
        area = (np.pi * d_cam**2) / 4
        q_aq = v_fumi * area * 3600
        q_un_u = q_aq * (273.15 / t_ass_k) * (p_ass_hpa / 1013.25)
        q_un_s = q_un_u * (1 - bws)
        f_corr = (20.9 - o2_mis) / (20.9 - o2_rif) if o2_mis < 20.8 else 1.0
        q_rif = q_un_s * f_corr

        # ==========================================
        # DASHBOARD RISULTATI COMPLETA
        # ==========================================
        st.markdown(f"""
        <div class="result-card" style="margin-top: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <span class="label-custom">Velocità Media (UNI EN 16911)</span><br>
                    <span class="value-main">{v_fumi:.2f} m/s</span><br>
                    <small style="color: #6c757d;">Punti attivi: {len(lista_dp_validi)} | K applicato (radice): {k_da_usare:.4f}</small>
                </div>
                <div style="text-align: right;">
                    <span class="label-custom">Dati Termodinamici</span><br>
                    <span style="font-weight: 500;">P. Assoluta:</span> {p_ass_hpa:.2f} hPa<br>
                    <span style="font-weight: 500;">Densità (ρ):</span> {rho_fumi:.3f} kg/m³<br>
                    <span style="font-weight: 500;">Massa Mol.:</span> {m_wet:.2f} g/mol
                </div>
            </div>
            
            <div style="margin: 15px 0; border-top: 1px solid #e0e0e0;"></div>
            
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <span class="label-custom">Tal Quale (Am³/h)</span><br>
                    <span style="color: #2c3e50; font-size: 1.15rem; font-weight: 600;">{q_aq:.0f}</span><br><br>
                    <span class="label-custom">Normale Umida (Nm³/h)</span><br>
                    <span style="color: #2c3e50; font-size: 1.15rem; font-weight: 600;">{q_un_u:.0f}</span>
                </div>
                <div style="text-align: right;">
                    <span class="label-custom">Normale Secca (Nm³/h)</span><br>
                    <span style="color: #2c3e50; font-size: 1.15rem; font-weight: 600;">{q_un_s:.0f}</span><br><br>
                    <span class="label-custom" style="color: #27ae60;">Portata Rif. O₂ (Nm³/h)</span><br>
                    <span class="value-highlight">{q_rif:.0f}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💾 Salva Dati Dinamica", use_container_width=True):
            st.session_state.dati_dinamica.update({
                'v': v_fumi, 'q_aq': q_aq, 'q_un_u': q_un_u, 'q_un_s': q_un_s, 'q_rif': q_rif,
                'h_in': h_in, 't_fumi': t_fumi, 'p_ass': p_ass_hpa, 'o2_mis': o2_mis, 'co2': co2_mis,
                'd_cam': d_cam, 'k_pit': k_interna, 'n_punti': n_punti_fumi, 'rho': rho_fumi
            })
            st.success("✅ Dati dinamica e calcolo portate salvati con successo!")
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
