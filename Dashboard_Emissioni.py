import streamlit as st
import pandas as pd
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="Gestione Emissioni", layout="wide")

# ==========================================
# CSS CUSTOM - DESIGN MODERNO (SFONDO BIANCO)
# ==========================================
st.markdown("""
    <style>
    /* Sfondo principale chiaro */
    .main {
        background-color: #f8f9fa;
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

    /* Titoli e Label */
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
    </style>
    """, unsafe_allow_html=True)

# Inizializzazione Session State (Logica Originale)
if 'page' not in st.session_state:
    st.session_state.page = 'fumi'
if 'dati_dinamica' not in st.session_state:
    st.session_state.dati_dinamica = {
        'd_cam': 1.6, 'k_pit': 0.84, 't_fumi': 120.0, 'p_atm': 1013.0, 'p_stat_pa': 0.0,
        'h_in': 5.0, 'o2_mis': 10.0, 'o2_rif': 11.0, 'v': 0.0, 'q_rif': 0.0, 'n_punti': 6
    }

# Navigazione (Le tue sezioni originali)
st.sidebar.title("🛠️ Menu")
if st.sidebar.button("📐 Dinamica Fumi"):
    st.session_state.page = 'fumi'
if st.sidebar.button("🧪 Campionamento"):
    st.session_state.page = 'campionamento'
if st.sidebar.button("📄 Report Finale"):
    st.session_state.page = 'report'

# ==========================================
# 2. DINAMICA FUMI (LOGICA ORIGINALE + DESIGN)
# ==========================================
if st.session_state.page == 'fumi':
    st.markdown("<h2 class='section-title'>📐 Dinamica dei Fumi (Mappatura ISO 16911)</h2>", unsafe_allow_html=True)
    
    d = st.session_state.dati_dinamica
    c1, c2 = st.columns([1, 2], gap="large")
    
    with c1:
        st.subheader("Parametri Condotto")
        d_cam = st.number_input("Diametro Camino (m)", value=d['d_cam'], format="%.3f")
        
        # --- LOGICA SOGLIE RICHIESTE (Invariata) ---
        if d_cam < 0.35:
            n_punti_fumi, coeffs = 1, [0.500]
        elif 0.35 <= d_cam < 1.10:
            n_punti_fumi, coeffs = 2, [0.146, 0.854]
        elif 1.10 <= d_cam < 1.60:
            n_punti_fumi, coeffs = 4, [0.067, 0.250, 0.750, 0.933]
        elif 1.60 <= d_cam < 2.25:
            n_punti_fumi, coeffs = 6, [0.044, 0.146, 0.296, 0.704, 0.854, 0.956]
        elif 2.25 <= d_cam < 2.50:
            n_punti_fumi, coeffs = 8, [0.032, 0.105, 0.194, 0.323, 0.677, 0.806, 0.895, 0.968]
        else:
            n_punti_fumi, coeffs = 10, [0.026, 0.082, 0.146, 0.226, 0.342, 0.658, 0.774, 0.854, 0.918, 0.974]
            
        st.info(f"Configurazione: {n_punti_fumi} punti per asse")
        k_pit = st.number_input("K Pitot", value=d['k_pit'])
        
        st.markdown("---")
        st.subheader("Condizioni Gas")
        t_fumi = st.number_input("T. Fumi (°C)", value=d['t_fumi'])
        p_atm = st.number_input("P. Atmosferica (hPa)", value=d['p_atm'])
        p_stat_pa = st.number_input("P. Statica (Pa)", value=d['p_stat_pa'])
        h_in = st.number_input("Umidità (%)", value=d['h_in'])
        o2_mis = st.number_input("O2 misurata (%)", value=d['o2_mis'])
        o2_rif = st.number_input("O2 riferimento (%)", value=d['o2_rif'])

    with c2:
        st.subheader("Mappatura ΔP")
        unit_dp = st.radio("Unità ΔP:", ["mmH2O", "Pa"], horizontal=True)
        
        affondamenti_cm = [round(d_cam * c * 100, 1) for c in coeffs]
        df_mappa = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(len(affondamenti_cm))],
            "Affondamento (cm)": affondamenti_cm,
            f"ΔP Asse 1 ({unit_dp})": [0.0] * len(affondamenti_cm),
            f"ΔP Asse 2 ({unit_dp})": [0.0] * len(affondamenti_cm)
        })

        edit_mappa = st.data_editor(
            df_mappa, hide_index=True, use_container_width=True, 
            key=f"map_dyn_{d_cam}_{unit_dp}_{n_punti_fumi}"
        )
        
        # --- CALCOLI (Logica Originale) ---
        col_1, col_2 = f"ΔP Asse 1 ({unit_dp})", f"ΔP Asse 2 ({unit_dp})"
        dp_medio_raw = pd.concat([edit_mappa[col_1], edit_mappa[col_2]]).mean()
        dp_pa = dp_medio_raw * 9.80665 if unit_dp == "mmH2O" else dp_medio_raw
        
        p_ass_hpa = p_atm + (p_stat_pa / 100)
        rho_fumi = 1.293 * (p_ass_hpa / 1013.25) * (273.15 / (t_fumi + 273.15))
        v_fumi = k_pit * np.sqrt((2 * dp_pa) / rho_fumi) if rho_fumi > 0 else 0
        area = (np.pi * d_cam**2) / 4
        
        q_aq = v_fumi * area * 3600
        q_un_u = q_aq * (273.15 / (t_fumi + 273.15)) * (p_ass_hpa / 1013.25)
        q_un_s = q_un_u * (1 - h_in/100)
        f_corr = (20.9 - o2_mis) / (20.9 - o2_rif) if o2_mis < 20.8 else 1.0
        q_rif = q_un_s * f_corr

        # --- DESIGN RISULTATI (Card Moderna su sfondo bianco) ---
        st.markdown(f"""
        <div class="result-card">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <span class="label-custom">Velocità Media</span><br>
                    <span class="value-main">{v_fumi:.2f} m/s</span>
                </div>
                <div style="text-align: right;">
                    <span class="label-custom">Pressione Assoluta</span><br>
                    <span style="font-size: 1.2rem; font-weight: 600;">{p_ass_hpa:.2f} hPa</span>
                </div>
            </div>
            <div style="margin: 20px 0; border-top: 1px solid #eee;"></div>
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <span class="label-custom">Tal Quale</span><br>
                    <span style="font-size: 1.3rem; font-weight: 600;">{q_aq:.0f} Am³/h</span><br><br>
                    <span class="label-custom">Normale Umida</span><br>
                    <span style="font-size: 1.3rem; font-weight: 600;">{q_un_u:.0f} Nm³/h</span>
                </div>
                <div style="text-align: right;">
                    <span class="label-custom">Normale Secca</span><br>
                    <span style="font-size: 1.3rem; font-weight: 600;">{q_un_s:.0f} Nm³/h</span><br><br>
                    <span class="label-custom" style="color: #27ae60;">Portata Riferita (O2)</span><br>
                    <span class="value-highlight">{q_rif:.0f} Nm³/h</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💾 SALVA DATI DINAMICA"):
            st.session_state.dati_dinamica.update({
                'v': v_fumi, 'q_rif': q_rif, 'd_cam': d_cam, 't_fumi': t_fumi, 'p_ass': p_ass_hpa
            })
            st.success("Dati salvati!")

elif st.session_state.page == 'campionamento':
    st.markdown("<h2 class='section-title'>🧪 Sezione Campionamento</h2>", unsafe_allow_html=True)
    st.info("Qui puoi inserire la logica per il campionamento isocinetico.")

elif st.session_state.page == 'report':
    st.markdown("<h2 class='section-title'>📄 Report Finale</h2>", unsafe_allow_html=True)
    st.write("Dati attuali in memoria:", st.session_state.dati_dinamica)
