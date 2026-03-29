import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Emissioni Pro - Dashboard v2.1", layout="wide")

# CSS per Interfaccia
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-header { font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .stButton>button { width: 100%; height: 60px; font-weight: bold; border-radius: 10px; }
    .result-card { background-color: #f0f7ff; padding: 20px; border-radius: 15px; border: 1px solid #007bff; margin-top: 20px; }
    .metric-title { font-size: 14px; color: #555; margin-bottom: 2px; }
    .metric-value { font-size: 22px; font-weight: bold; color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = 'fumi'

if st.session_state.page == 'fumi':
    st.header("📏 Dinamica dei Fumi e Isocinetismo")

    col_in, col_tab = st.columns([1, 2.2])

    with col_in:
        st.subheader("Parametri Fisici")
        # Campi senza limiti min/max per permettere cancellazione e inserimento libero
        d_camino = st.number_input("Diametro Camino (m)", value=1.4, format="%.3f")
        t_fumi = st.number_input("Temperatura Fumi (°C)", value=259.0, format="%.1f")
        k_pit = st.number_input("Costante K Pitot (Tipo S)", value=0.69, format="%.2f")
        
        st.write("---")
        st.subheader("Pressioni")
        # Pressione Atmosferica e Statica completamente libere (senza min_value)
        p_atm = st.number_input("Pressione Atmosferica (hPa)", value=1013.25, format="%.2f")
        p_stat = st.number_input("Pressione Statica (Pa)", value=-10.0, format="%.2f", help="Puoi inserire valori positivi o negativi")
        
        # Calcolo Pressione Assoluta
        p_ass_hpa = p_atm + (p_stat / 100)
        st.metric("Pressione Assoluta (hPa)", f"{p_ass_hpa:.2f}")

        st.write("---")
        st.subheader("Chimica Fumi")
        o2_mis = st.number_input("O2 misurato (%)", value=14.71, format="%.2f")
        co2_mis = st.number_input("CO2 misurata (%)", value=5.95, format="%.2f")
        h_in = st.number_input("Umidità (%)", value=4.68, format="%.2f")
        o2_rif = st.number_input("O2 di Riferimento (%)", value=8.0, format="%.1f")

        unita_dp = st.radio("Unità Delta P in tabella:", ["mmH2O", "Pascal (Pa)"], horizontal=True)

    with col_tab:
        st.subheader("Tabella ΔP")
        punti_pos = [round(d_camino*p, 3) for p in [0.067, 0.25, 0.75, 0.933]]
        df_init = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(len(punti_pos))],
            "Posizione (m)": punti_pos,
            "Asse 1": [26.60]*len(punti_pos),
            "Asse 2": [None]*len(punti_pos)
        })
        
        edit_df = st.data_editor(df_init, use_container_width=True, hide_index=True)

        # --- MOTORE DI CALCOLO ---
        vals = edit_df["Asse 1"].dropna().tolist() + edit_df["Asse 2"].dropna().tolist()
        
        if vals:
            dp_med = sum(vals) / len(vals)
            dp_pa = dp_med * 9.80665 if unita_dp == "mmH2O" else dp_med
            
            # 1. Massa Molare (M)
            n_mis = 100 - o2_mis - co2_mis
            ms = (co2_mis * 44.01 + o2_mis * 31.999 + n_mis * 28.013) / 100
            mu = ms * (1 - h_in/100) + 18.015 * (h_in/100)
            
            # 2. Densità Reale (rho)
            rho_eff = (p_ass_hpa * 100 * mu) / (8314.47 * (t_fumi + 273.15))

            # 3. Velocità (v)
            v_media = np.sqrt((2 * dp_pa * k_pit) / rho_eff)
            
            # 4. Portate
            area_camino = (np.pi * d_camino**2) / 4
            q_aq = v_media * area_camino * 3600
            
            # Portata Normale Umida (0°C, 1013.25 hPa)
            q_un_umida = q_aq * (273.15 / (t_fumi + 273.15)) * (p_ass_hpa / 1013.25)
            
            # Portata Normale Secca
            q_un_secca = q_un_umida * (1 - h_in/100)
            
            # 5. Portata Riferita (Corretta)
            # Rapporto O2: (20.9 - Rif) / (20.9 - Mis)
            f_o2 = (20.9 - o2_rif) / (20.9 - o2_mis)
            q_rif = q_un_secca * f_o2

            # --- UGELLO ---
            st.markdown("---")
            st.subheader("🎯 Scelta Ugello")
            u1, u2 = st.columns(2)
            with u1:
                d_ugello = st.number_input("Diametro Ugello (mm)", value=5.0, format="%.1f")
                t_cont = st.number_input("T. al Contatore (°C)", value=20.0, format="%.1f")
            with u2:
                area_ugello_m2 = np.pi * ((d_ugello / 1000) / 2)**2
                q_cam_lmin = v_media * area_ugello_m2 * 60 * 1000
                q_pump = q_cam_lmin * ((t_cont + 273.15) / (t_fumi + 273.15)) * (p_ass_hpa / 1013.25)
                st.metric("FLUSSO POMPA (l/min)", f"{q_pump:.2f}")

            # RISULTATI FINALI
            st.markdown(f"""
            <div class='result-card'>
                <div style='display: flex; justify-content: space-between; text-align: center;'>
                    <div><p class='metric-title'>Densità Reale</p><p class='metric-value'>{rho_eff:.4f} kg/m³</p></div>
                    <div><p class='metric-title'>Velocità Media</p><p class='metric-value'>{v_media:.2f} m/s</p></div>
                    <div><p class='metric-title'>Portata N. Secca</p><p class='metric-value'>{q_un_secca:.0f} Nm³/h</p></div>
                    <div><p class='metric-title' style='color:#28a745'>PORTATA RIFERITA</p><p class='metric-value' style='color:#28a745'>{q_rif:.0f} Nm³/h</p></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("⬅️ Home"): st.session_state.page = 'home'
