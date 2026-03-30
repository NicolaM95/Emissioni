import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAZIONE DASHBOARD ---
st.set_page_config(page_title="Emissioni Pro v3.7 - FULL", layout="wide")

# CSS Personalizzato
st.markdown("""
    <style>
    .main-header { font-size: 28px; font-weight: bold; color: #1E3A8A; border-bottom: 2px solid #1E3A8A; margin-bottom: 20px; }
    .result-card { background-color: #f8fbff; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; margin: 10px 0; }
    .stNumberInput div div input { font-weight: bold; }
    .camp-box { border: 1px solid #d1d5db; padding: 15px; border-radius: 8px; background-color: #ffffff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE STATO ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'dati_anagrafica' not in st.session_state: st.session_state.dati_anagrafica = {'tecnici': [], 'ditta': '', 'camino': ''}
if 'dati_dinamica' not in st.session_state: st.session_state.dati_dinamica = {}
if 'lista_c' not in st.session_state: st.session_state.lista_c = []
if 'camp_attivo' not in st.session_state: st.session_state.camp_attivo = None
if 'step_camp' not in st.session_state: st.session_state.step_camp = 'selezione'

PARAMETRI_BASE = [
    "Polveri Totali", "Metalli (EN 14385)", "Acidi (SOx, HCl, HF)", "Mercurio (Hg)", 
    "Ammoniaca (NH3)", "PM10", "PM2.5", "SOV (COV)", "Formaldeide", "Benzolo", "IPA", "Diossine"
]

def nav(p): st.session_state.page = p

# --- SIDEBAR NAVIGAZIONE ---
with st.sidebar:
    st.title("🚀 Emissioni Pro v3.7")
    st.button("🏠 Dashboard Home", on_click=lambda: nav('home'), use_container_width=True)
    st.button("🗂️ Anagrafica & Tecnici", on_click=lambda: nav('anagrafica'), use_container_width=True)
    st.button("📐 Dinamica Fumi & Pressioni", on_click=lambda: nav('fumi'), use_container_width=True)
    st.button("💉 Gestione Campionamenti", on_click=lambda: nav('camp'), use_container_width=True)
    st.button("📄 Report Finale", on_click=lambda: nav('rdp'), use_container_width=True)

# ==========================================
# 1. ANAGRAFICA
# ==========================================
if st.session_state.page == 'anagrafica':
    st.markdown("<p class='main-header'>🗂️ Dati Generali del Sito</p>", unsafe_allow_html=True)
    with st.form("anag_form"):
        st.session_state.dati_anagrafica['ditta'] = st.text_input("Ragione Sociale Cliente", st.session_state.dati_anagrafica['ditta'])
        st.session_state.dati_anagrafica['camino'] = st.text_input("Identificativo Camino (E1, E2...)", st.session_state.dati_anagrafica['camino'])
        st.write("---")
        tecnici_raw = st.text_area("Tecnici al campionamento (uno per riga)", "\n".join(st.session_state.dati_anagrafica['tecnici']))
        if st.form_submit_button("Salva Anagrafica"):
            st.session_state.dati_anagrafica['tecnici'] = tecnici_raw.split("\n")
            st.success("Anagrafica aggiornata!")

# ==========================================
# 2. DINAMICA FUMI (CALCOLO PRESSIONI)
# ==========================================
elif st.session_state.page == 'fumi':
    st.markdown("<p class='main-header'>📐 Dinamica Fumi & Pressione Assoluta</p>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("Dati Pressione")
        p_atm = st.number_input("P. Atmosferica (hPa)", value=1013.25, step=0.1)
        p_stat_mmca = st.number_input("P. Statica (mmH2O / mmca)", value=-2.0, step=0.5)
        
        # Conversione mmca -> hPa (1 mmca = 0.09806 hPa)
        p_stat_hpa = p_stat_mmca * 0.09806
        p_ass = p_atm + p_stat_hpa
        
        st.metric("Pressione Assoluta (Pass)", f"{p_ass:.2f} hPa")
        
        st.write("---")
        d_cam = st.number_input("Diametro Camino (m)", value=1.2, format="%.3f")
        t_fumi = st.number_input("Temperatura Fumi (°C)", value=180.0)
        h_fumi = st.number_input("Umidità Stimata (%)", value=8.0)
        o2_mis = st.number_input("O2 Misurato (%)", value=13.5, step=0.1)
        o2_rif = st.number_input("O2 Riferimento (%)", value=11.0)

    with c2:
        st.subheader("Profilo di Velocità (ΔP)")
        n_punti = st.slider("Numero Punti di Misura", 1, 24, 8)
        df_dp = pd.DataFrame({"Punto": [f"P{i+1}" for i in range(n_punti)], "ΔP (Pa)": [35.0]*n_punti})
        edit_dp = st.data_editor(df_dp, use_container_width=True, hide_index=True)
        
        dp_med = edit_dp["ΔP (Pa)"].mean()
        # Densità Fumi Reale
        rho_fumi = 1.293 * (p_ass / 1013.25) * (273.15 / (t_fumi + 273.15))
        v_fumi = 0.69 * np.sqrt((2 * dp_med) / rho_fumi) if rho_fumi > 0 else 0
        
        area = (np.pi * d_cam**2) / 4
        q_aq = v_fumi * area * 3600
        q_un_s = q_aq * (273.15/(t_fumi+273.15)) * (p_ass/1013.25) * (1 - h_fumi/100)
        
        # Correzione O2
        if o2_mis >= 20.8:
            q_rif = q_un_s
            info_o2 = "O2 Ambientale: Portata Riferita = Portata Secca"
        else:
            f_o2 = (20.9 - o2_mis) / (20.9 - o2_rif)
            q_rif = q_un_s * f_o2
            info_o2 = f"Fattore O2: {f_o2:.3f}"

        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.info(info_o2)
        r1, r2 = st.columns(2)
        r1.write(f"**Velocità:** {v_fumi:.2f} m/s")
        r1.write(f"**Portata A.Q.:** {q_aq:.0f} Am³/h")
        r2.write(f"**Portata N. Secca:** {q_un_s:.0f} Nm³/h")
        r2.markdown(f"<span style='color:green; font-size:18px;'><b>PORTATA RIFERITA: {q_rif:.0f} Nm³/h</b></span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("💾 Archivia Dinamica"):
            st.session_state.dati_dinamica = {'p_ass': p_ass, 'v': v_fumi, 'q_rif': q_rif, 'area': area}
            st.success("Dati salvati nello stato sessione.")

# ==========================================
# 3. CAMPIONAMENTI (CALCOLO UMIDITÀ)
# ==========================================
elif st.session_state.page == 'camp':
    if st.session_state.camp_attivo is None:
        st.markdown("<p class='main-header'>💉 Gestione Campionamenti</p>", unsafe_allow_html=True)
        if st.button("➕ Crea Nuovo Campionamento"):
            st.session_state.lista_c.append({
                'id': len(st.session_state.lista_c)+1, 'main': [], 'sep': [], 'punti': 4,
                'umidita': {'pi': 0.0, 'pf': 0.0, 'param': 'Nessuno'}, 'dati': None
            })
            st.rerun()

        for i, camp in enumerate(st.session_state.lista_c):
            with st.container():
                st.markdown(f"<div class='camp-box'>", unsafe_allow_html=True)
                ca1, ca2, ca3 = st.columns([4, 1, 1])
                ca1.write(f"**Campionamento #{camp['id']}** - {', '.join(camp['main'])}")
                if ca2.button("Apri 📊", key=f"btn_o_{i}"):
                    st.session_state.camp_attivo = i; st.session_state.step_camp = 'selezione'; st.rerun()
                if ca3.button("Elimina 🗑️", key=f"btn_d_{i}"):
                    st.session_state.lista_c.pop(i); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    else:
        idx = st.session_state.camp_attivo
        curr = st.session_state.lista_c[idx]

        if st.session_state.step_camp == 'selezione':
            st.subheader(f"Configurazione Campionamento #{curr['id']}")
            curr['main'] = st.multiselect("Parametri Linea Isocinetica", PARAMETRI_BASE, default=curr['main'])
            curr['sep'] = st.multiselect("Parametri Linee Separate (Derivate)", PARAMETRI_BASE, default=curr['sep'])
            curr['punti'] = st.number_input("Numero Punti Tabella", 1, 20, curr['punti'])
            if st.button("Conferma e Vai alla Tabella"): st.session_state.step_camp = 'tabella'; st.rerun()

        elif st.session_state.step_camp == 'tabella':
            st.subheader(f"Tabella di Marcia Isocinetica - Camp. #{curr['id']}")
            
            # --- BLOCCO UMIDITÀ ---
            with st.expander("💧 CALCOLO UMIDITÀ GRAVIMETRICO", expanded=True):
                u1, u2, u3 = st.columns(3)
                param_u = u1.selectbox("Umidità basata su:", ["Nessuno"] + curr['main'], index=0)
                p_i = u2.number_input("Peso Gorg. Iniziale (g)", value=curr['umidita']['pi'])
                p_f = u3.number_input("Peso Gorg. Finale (g)", value=curr['umidita']['pf'])
                
                v_h2o_nl = (p_f - p_i) * 1.244 # Litri normali vapore
                curr['umidita'] = {'pi': p_i, 'pf': p_f, 'param': param_u}
                st.info(f"Vapore Acqueo Generato: {v_h2o_nl:.3f} Nl")

            # --- TABELLA DATI ---
            st.write("### Inserimento Dati Campo")
            nomi_col = ["Punto", "ΔP (Pa)", "T Fumi (°C)"]
            if curr['main']:
                label = "+".join(curr['main'])
                nomi_col += [f"Vol {label} (L)", f"T {label} (°C)", f"P {label} (mmHg)"]
            nomi_col.append("Isocinetismo %")

            if curr['dati'] is None or len(curr['dati']) != curr['punti']:
                curr['dati'] = pd.DataFrame(0.0, index=range(curr['punti']), columns=nomi_col)
                curr['dati']["Punto"] = [f"P{k+1}" for k in range(curr['punti'])]

            final_df = st.data_editor(curr['dati'], use_container_width=True, hide_index=True, key=f"editor_{idx}")
            
            # Calcolo Umidità Finale del Campionamento
            if param_u != "Nessuno":
                vol_secco_l = final_df[f"Vol {'+'.join(curr['main'])} (L)"].sum()
                h_perc = (v_h2o_nl / (v_h2o_nl + vol_secco_l)) * 100 if (v_h2o_nl + vol_secco_l) > 0 else 0
                st.metric("UMIDITÀ REALE CAMPIONAMENTO", f"{h_perc:.2f} %")

            if st.button("💾 Salva e Torna al Menu"):
                st.session_state.lista_c[idx]['dati'] = final_df
                st.session_state.camp_attivo = None; st.rerun()

# ==========================================
# 4. REPORT
# ==========================================
elif st.session_state.page == 'home':
    st.markdown("<p class='main-header'>🏭 Emissioni Pro v3.7 - Dashboard</p>", unsafe_allow_html=True)
    st.write("Seleziona una sezione dal menu laterale per operare.")
    if st.session_state.dati_anagrafica['ditta']:
        st.info(f"Operando su: **{st.session_state.dati_anagrafica['ditta']}** - Camino: **{st.session_state.dati_anagrafica['camino']}**")

elif st.session_state.page == 'rdp':
    st.header("📄 Riepilogo Dati")
    st.write(st.session_state.dati_anagrafica)
    if st.session_state.dati_dinamica:
        st.write("---")
        st.write(f"Portata di riferimento: {st.session_state.dati_dinamica['q_rif']:.0f} Nm3/h")
