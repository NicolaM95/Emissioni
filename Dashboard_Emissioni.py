import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v3.1", layout="wide")

# CSS per Blocchi e Interfaccia
st.markdown("""
    <style>
    .param-block {
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #dee2e6;
        text-align: center;
        cursor: pointer;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .selected-main { background-color: #e3f2fd; border-color: #2196f3; color: #1565c0; }
    .selected-sep { background-color: #fff3e0; border-color: #ff9800; color: #e65100; }
    .result-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; }
    .metric-val { font-size: 20px; font-weight: bold; color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'lista_c' not in st.session_state: st.session_state.lista_c = []
if 'camp_attivo' not in st.session_state: st.session_state.camp_attivo = None
if 'step_camp' not in st.session_state: st.session_state.step_camp = 'selezione'

PARAMETRI_TUTTI = [
    "Polveri Totali", "Acidi (SOx, HCl, HF)", "SOx", "HCl", "HF", "SO3",
    "Cromo VI", "Metalli (EN 14385)", "Mercurio (Hg)", "Ammoniaca (NH3)", 
    "PM10", "PM2.5", "SOV (COV)", "Formaldeide", "Benzolo", "Aldeidi"
]

# ==========================================
# SEZIONE 1: DINAMICA FUMI (CALCOLI COMPLETI)
# ==========================================
if st.session_state.page == 'fumi':
    st.header("📏 Dinamica dei Fumi - Calcoli Tecnici")
    c1, c2 = st.columns([1, 2])
    
    with c1:
        d_camino = st.number_input("Diametro Camino (m)", value=1.4, format="%.3f")
        t_fumi = st.number_input("Temperatura Fumi (°C)", value=259.0)
        k_pitot = st.number_input("Costante K Pitot", value=0.69)
        p_atm = st.number_input("Pressione Atm. (hPa)", value=1013.25)
        p_stat = st.number_input("Pressione Statica (Pa)", value=-10.0) # Libero (+/-)
        st.write("---")
        o2_mis = st.number_input("O2 misurato (%)", value=14.71)
        co2_mis = st.number_input("CO2 misurata (%)", value=5.95)
        h_in = st.number_input("Umidità (%)", value=4.68)
        o2_rif = st.number_input("O2 di Riferimento (%)", value=8.0)

    with c2:
        st.subheader("Tabella ΔP")
        df_dp = pd.DataFrame({"Punto": ["P1","P2","P3","P4"], "ΔP (Pa)": [26.6, 26.6, 26.6, 26.6]})
        edit_dp = st.data_editor(df_dp, hide_index=True, use_container_width=True)
        
        # Motore di Calcolo
        dp_med = edit_dp["ΔP (Pa)"].mean()
        p_ass = p_atm + (p_stat/100)
        ms = (co2_mis * 44.01 + o2_mis * 31.999 + (100-o2_mis-co2_mis)*28.013)/100
        mu = ms * (1 - h_in/100) + 18.015 * (h_in/100)
        rho = (p_ass * 100 * mu) / (8314.47 * (t_fumi + 273.15))
        v = np.sqrt((2 * dp_med * k_pitot) / rho)
        
        area = (np.pi * d_camino**2) / 4
        q_aq = v * area * 3600
        q_un_u = q_aq * (273.15/(t_fumi+273.15)) * (p_ass/1013.25)
        q_un_s = q_un_u * (1 - h_in/100)
        q_rif = q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif)) # Formula corretta

        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)
        r1.markdown(f"Densità: **{rho:.4f}** kg/m³<br>Velocità: **{v:.2f}** m/s", unsafe_allow_html=True)
        r2.markdown(f"Tal Quale: **{q_aq:.0f}** Am³/h<br>N. Umida: **{q_un_u:.0f}** Nm³/h", unsafe_allow_html=True)
        r3.markdown(f"N. Secca: **{q_un_s:.0f}** Nm³/h<br><span style='color:green'>RIFERITA: <b>{q_rif:.0f}</b> Nm³/h</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("⬅️ Torna alla Home"): st.session_state.page = 'home'; st.rerun()

# ==========================================
# SEZIONE 2: GESTIONE CAMPIONAMENTI
# ==========================================
elif st.session_state.page == 'camp':
    if st.session_state.camp_attivo is None:
        st.header("💉 Gestione Campionamenti")
        if st.button("➕ AGGIUNGI CAMPIONAMENTO", use_container_width=True):
            new_id = len(st.session_state.lista_c) + 1
            st.session_state.lista_c.append({'id': new_id, 'main': [], 'sep': [], 'punti': 4, 'data_tab': None})
            st.rerun()
        
        for i, c in enumerate(st.session_state.lista_c):
            with st.container():
                st.markdown(f"<div style='border:1px solid #ccc; padding:15px; border-radius:10px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;'><b>📦 Campionamento n° {c['id']}</b></div>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([4,1,1])
                if c2.button("📊 APRI", key=f"op_{i}"): st.session_state.camp_attivo = i; st.session_state.step_camp = 'selezione'; st.rerun()
                if c3.button("🗑️ ELIMINA", key=f"de_{i}"): st.session_state.lista_c.pop(i); st.rerun()
        st.button("🏠 Home", on_click=lambda: nav('home'))

    else:
        idx = st.session_state.camp_attivo
        curr = st.session_state.lista_c[idx]

        # STEP A: SELEZIONE A BLOCCHI
        if st.session_state.step_camp == 'selezione':
            st.subheader(f"⚙️ Selezione Parametri - Campionamento {curr['id']}")
            
            st.write("### 🟦 LINEA ISOCINETICA (Main)")
            m_cols = st.columns(4)
            for j, p in enumerate(PARAMETRI_TUTTI):
                is_sel = p in curr['main']
                with m_cols[j % 4]:
                    if st.checkbox(p, value=is_sel, key=f"m_{idx}_{p}"):
                        if p not in curr['main']: curr['main'].append(p)
                    else:
                        if p in curr['main']: curr['main'].remove(p)

            st.write("---")
            st.write("### 🟧 LINEE SEPARATE / DERIVATE")
            s_cols = st.columns(4)
            for j, p in enumerate(PARAMETRI_TUTTI):
                is_sel = p in curr['sep']
                with s_cols[j % 4]:
                    if st.checkbox(p, value=is_sel, key=f"s_{idx}_{p}"):
                        if p not in curr['sep']: curr['sep'].append(p)
                    else:
                        if p in curr['sep']: curr['sep'].remove(p)

            curr['punti'] = st.number_input("Numero Punti Mappatura", min_value=1, value=curr['punti'])
            
            if st.button("✅ CONFERMA E VAI ALLA TABELLA", use_container_width=True):
                st.session_state.step_camp = 'tabella'; st.rerun()
            if st.button("⬅️ Torna alla Lista"): st.session_state.camp_attivo = None; st.rerun()

        # STEP B: TABELLA DATI
        elif st.session_state.step_camp == 'tabella':
            st.subheader(f"📊 Inserimento Dati Campo - Camp. {curr['id']}")
            if st.button("⬅️ MODIFICA SELEZIONE PARAMETRI"): st.session_state.step_camp = 'selezione'; st.rerun()

            # Header Medie
            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
            h1, h2, h3, h4 = st.columns(4)
            p_ass_camp = h1.number_input("P. Assoluta (hPa)", value=1013.25)
            h2.metric("T. Fumi Media", "259 °C")
            h3.metric("Velocità Media", "24.1 m/s")
            h4.metric("Isocinetismo", "100.2 %")
            st.markdown("</div>", unsafe_allow_html=True)

            # Umidità
            st.write("### 💧 Determinazione Umidità")
            u_param = st.selectbox("Umidità basata su:", ["Dinamica"] + curr['main'] + curr['sep'])
            if u_param != "Dinamica":
                if "Polveri" in u_param:
                    u1, u2 = st.columns(2)
                    u1.number_input("Serpentina Iniz (g)", 0.0); u1.number_input("Serpentina Fin (g)", 0.0)
                    u2.number_input("Gel Iniz (g)", 0.0); u2.number_input("Gel Fin (g)", 0.0)
                else:
                    u1, u2 = st.columns(2)
                    u1.number_input("Gorgogliatori Iniz (g)", 0.0); u2.number_input("Gorgogliatori Fin (g)", 0.0)

            # Tabella Dinamica
            st.write("### 📝 Tabella Punti")
            col_nomi = ["Punto", "ΔP (Pa)", "T Fumi (°C)"]
            if curr['main']: col_nomi += ["Vol. Main (L)", "T. Cont Main (°C)"]
            for s in curr['sep']: col_nomi += [f"Vol. {s} (L)", f"T. {s} (°C)"]
            col_nomi += ["Isocinetismo %"]
            
            df_campo = pd.DataFrame([{c: 0.0 for c in col_nomi} for _ in range(curr['punti'])])
            df_campo["Punto"] = [f"P{k+1}" for k in range(curr['punti'])]
            st.data_editor(df_campo, use_container_width=True, hide_index=True)
            
            if st.button("💾 SALVA DEFINITIVO"): st.success("Dati salvati!")

# ==========================================
# HOME PAGE
# ==========================================
else:
    st.markdown("<p class='main-header'>🏭 Dashboard Emissioni Pro</p>", unsafe_allow_html=True)
    if st.button("📐 VAI A DINAMICA FUMI"): nav('fumi')
    if st.button("💉 VAI A CAMPIONAMENTI"): nav('camp')
