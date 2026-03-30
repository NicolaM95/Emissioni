# ==========================================
# 2. DINAMICA FUMI (VERSIONE AGGIORNATA 3.5+)
# ==========================================
elif st.session_state.page == 'fumi':
    st.header("📐 Dinamica dei Fumi (ISO 16911)")
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("Parametri di Input")
        d_cam = st.number_input("Diametro Camino (m)", value=1.4, format="%.3f")
        n_punti_fumi = st.number_input("Punti di misura Delta P", value=8)
        t_fumi = st.number_input("T. Fumi (°C)", value=259.0)
        k_pit = st.number_input("K Pitot", value=0.69)
        
        st.write("---")
        # Calcolo Pressione Assoluta
        p_atm = st.number_input("P. Atm (hPa)", value=1013.25)
        p_stat_pa = st.number_input("P. Statica (Pa)", value=-10.0)
        p_ass_hpa = p_atm + (p_stat_pa / 100) # Conversione Pa in hPa per somma
        st.metric("Pressione Assoluta", f"{p_ass_hpa:.2f} hPa")
        
        st.write("---")
        o2_mis = st.number_input("O2 misurata (%)", value=14.71, step=0.1)
        h_in = st.number_input("Umidità (%)", value=4.68)
        o2_rif = st.number_input("O2 riferimento (%)", value=8.0)

    with c2:
        st.subheader("Inserimento Mappatura ΔP")
        df_dp = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(int(n_punti_fumi))], 
            "ΔP (Pa)": [26.6]*int(n_punti_fumi)
        })
        edit_dp = st.data_editor(df_dp, hide_index=True, use_container_width=True)
        
        # --- MOTORE DI CALCOLO ---
        dp_med = edit_dp["ΔP (Pa)"].mean()
        
        # Calcolo Densità Reale (Metodo Scientifico)
        rho_std = 1.293 # Densità aria secca @ 0°C, 1013.25 hPa
        rho_fumi = rho_std * (p_ass_hpa / 1013.25) * (273.15 / (t_fumi + 273.15))
        
        # Velocità e Portate
        v_fumi = k_pit * np.sqrt((2 * dp_med) / rho_fumi) if rho_fumi > 0 else 0
        area = (np.pi * d_cam**2) / 4
        
        q_aq = v_fumi * area * 3600
        q_un_u = q_aq * (273.15/(t_fumi+273.15)) * (p_ass_hpa/1013.25)
        q_un_s = q_un_u * (1 - h_in/100)
        
        # --- LOGICA CORREZIONE O2 (Gestione Ossicombustione) ---
        if o2_mis >= 20.8:
            q_rif = q_un_s
            info_o2 = "⚠️ O2 >= 20.8%: Portata Riferita impostata uguale alla Secca (Aria ambiente/Ossicombustione)."
        else:
            f_corr = (20.9 - o2_mis) / (20.9 - o2_rif)
            q_rif = q_un_s * f_corr
            info_o2 = f"✅ Fattore Correzione O2 applicato: {f_corr:.3f}"

        # --- VISUALIZZAZIONE RISULTATI ---
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.write(f"*{info_o2}*")
        r1, r2 = st.columns(2)
        r1.markdown(f"""
            **Velocità:** {v_fumi:.2f} m/s<br>
            **Densità Fumi:** {rho_fumi:.3f} kg/m³<br>
            **Portata Tal Quale:** {q_aq:.0f} Am³/h
        """, unsafe_allow_html=True)
        
        r2.markdown(f"""
            **Portata N. Secca:** {q_un_s:.0f} Nm³/h<br>
            <span style='color:green; font-size:20px;'>
                <b>PORTATA RIFERITA: {q_rif:.0f} Nm³/h</b>
            </span>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("💾 Salva Dinamica"):
            st.session_state.dati_dinamica = {
                'v': v_fumi, 
                'q_rif': q_rif, 
                'p_ass': p_ass_hpa, 
                'h_in': h_in, 
                't_fumi': t_fumi, 
                'o2_mis': o2_mis
            }
            st.success("Dati dinamica archiviati con successo.")
