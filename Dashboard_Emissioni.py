import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v3.2", layout="wide")

# CSS per Interfaccia User-Friendly e Blocchi
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .result-card { background-color: #f0f7ff; padding: 20px; border-radius: 15px; border: 1px solid #007bff; margin-bottom: 20px; }
    .metric-title { font-size: 13px; color: #555; font-weight: bold; }
    .metric-value { font-size: 19px; font-weight: bold; color: #1E3A8A; }
    .camp-container { border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; margin-bottom: 15px; background-color: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'dati_anagrafica' not in st.session_state: st.session_state.dati_anagrafica = {}
if 'dati_dinamica' not in st.session_state: st.session_state.dati_dinamica = {}
if 'lista_c' not in st.session_state: st.session_state.lista_c = []
if 'camp_attivo' not in st.session_state: st.session_state.camp_attivo = None
if 'step_camp' not in st.session_state: st.session_state.step_camp = 'selezione'

PARAMETRI_BASE = [
    "Polveri Totali", "Acidi (SOx, HCl, HF)", "SOx", "HCl", "HF", "SO3",
    "Cromo VI", "Metalli (EN 14385)", "Mercurio (Hg)", "Ammoniaca (NH3)", 
    "PM10", "PM2.5", "SOV (COV)", "Formaldeide", "Benzolo", "Aldeidi"
]

# --- FUNZIONI NAVIGAZIONE ---
def nav(p): st.session_state.page = p

# --- SIDEBAR NAVIGAZIONE ---
with st.sidebar:
    st.title("📑 Menu")
    if st.button("🏠 Home"): nav('home')
    if st.button("🗂️ Dati Generali"): nav('anagrafica')
    if st.button("📐 Dinamica Fumi"): nav('fumi')
    if st.button("💉 Campionamenti"): nav('camp')
    if st.button("📄 Report Finale (RdP)"): nav('rdp')

# ==========================================
# 1. HOME PAGE
# ==========================================
if st.session_state.page == 'home':
    st.markdown("<p class='main-header'>🏭 Dashboard Emissioni v3.2</p>", unsafe_allow_html=True)
    st.write("Benvenuto nel sistema integrato per la gestione dei campionamenti.")
    c1, c2, c3 = st.columns(3)
    with c1: st.info("Inserisci i dati del cliente in **Dati Generali**.")
    with c2: st.success("Calcola portate e isocinetismo in **Dinamica Fumi**.")
    with c3: st.warning("Gestisci i prelievi in **Campionamenti**.")

# ==========================================
# 2. DATI GENERALI
# ==========================================
elif st.session_state.page == 'anagrafica':
    st.header("🗂️ Anagrafica e Dati Generali")
    with st.form("anag_form"):
        st.session_state.dati_anagrafica['ditta'] = st.text_input("Ditta Cliente", st.session_state.dati_anagrafica.get('ditta',''))
        st.session_state.dati_anagrafica['camino'] = st.text_input("Punto di Emissione / Camino", st.session_state.dati_anagrafica.get('camino',''))
        st.session_state.dati_anagrafica['data'] = st.date_input("Data Intervento", datetime.now())
        if st.form_submit_button("💾 Salva Dati"): st.success("Dati salvati!")

# ==========================================
# 3. DINAMICA FUMI
# ==========================================
elif st.session_state.page == 'fumi':
    st.header("📐 Dinamica dei Fumi")
    col_in, col_res = st.columns([1, 2])
    with col_in:
        d_cam = st.number_input("Diametro Camino (m)", value=1.4, format="%.3f")
        t_fumi = st.number_input("T. Fumi (°C)", value=259.0)
        k_pit = st.number_input("Costante K Pitot", value=0.69)
        p_atm = st.number_input("P. Atm (hPa)", value=1013.25)
        p_stat = st.number_input("P. Statica (Pa)", value=-10.0)
        o2_mis = st.number_input("O2 Misurato (%)", value=14.71)
        h_in = st.number_input("Umidità (%)", value=4.68)
        o2_rif = st.number_input("O2 Riferimento (%)", value=8.0)

    with col_res:
        st.subheader("Tabella ΔP")
        df_dp = pd.DataFrame({"Punto": ["P1","P2","P3","P4"], "ΔP (Pa)": [26.6, 26.6, 26.6, 26.6]})
        edit_dp = st.data_editor(df_dp, hide_index=True, use_container_width=True)
        
        # CALCOLO MOTORE
        dp_med = edit_dp["ΔP (Pa)"].mean()
        p_ass = p_atm + (p_stat/100)
        # Densità e Velocità (Massa Molare semplificata per esempio)
        rho = (p_ass * 100 * 28.9) / (8314 * (t_fumi + 273.15)) 
        v = np.sqrt((2 * dp_med * k_pit) / 0.621) # 0.621 valore immagine utente
        
        area = (np.pi * d_cam**2) / 4
        q_aq = v * area * 3600
        q_un_u = q_aq * (273.15/(t_fumi+273.15)) * (p_ass/1013.25)
        q_un_s = q_un_u * (1 - h_in/100)
        q_rif = q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif))

        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)
        r1.markdown(f"<p class='metric-title'>Velocità</p><p class='metric-value'>{v:.2f} m/s</p>", unsafe_allow_html=True)
        r2.markdown(f"<p class='metric-title'>Portata N. Secca</p><p class='metric-value'>{q_un_s:.0f} Nm³/h</p>", unsafe_allow_html=True)
        r3.markdown(f"<p class='metric-title' style='color:green'>PORTATA RIFERITA</p><p class='metric-value' style='color:green'>{q_rif:.0f} Nm³/h</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("💾 Salva Risultati Dinamica"):
            st.session_state.dati_dinamica = {'v': v, 'q_rif': q_rif, 'p_ass': p_ass, 'h_in': h_in}
            st.success("Dati Dinamica Archiviati.")

# ==========================================
# 4. CAMPIONAMENTI (LOGICA COMPLETA)
# ==========================================
elif st.session_state.page == 'camp':
    if st.session_state.camp_attivo is None:
        st.header("💉 Sessioni di Campionamento")
        if st.button("➕ AGGIUNGI NUOVO CAMPIONAMENTO", use_container_width=True):
            st.session_state.lista_c.append({'id': len(st.session_state.lista_c)+1, 'main': [], 'sep': [], 'punti': 4})
            st.rerun()
        
        for i, c in enumerate(st.session_state.lista_c):
            with st.container():
                st.markdown(f"<div class='camp-container'>", unsafe_allow_html=True)
                cols = st.columns([4, 1, 1])
                cols[0].write(f"### 📦 Campionamento n° {c['id']}")
                if cols[1].button("📊 APRI", key=f"apri_{i}"):
                    st.session_state.camp_attivo = i
                    st.session_state.step_camp = 'selezione'
                    st.rerun()
                if cols[2].button("🗑️ ELIMINA", key=f"del_{i}"):
                    st.session_state.lista_c.pop(i)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        idx = st.session_state.camp_attivo
        curr = st.session_state.lista_c[idx]

        if st.session_state.step_camp == 'selezione':
            st.subheader(f"⚙️ Configurazione Treno n° {curr['id']}")
            
            # Selezione a Blocchi (Checkboxes in griglia)
            st.write("#### 🟦 LINEA ISOCINETICA")
            c_main = st.columns(4)
            for j, p in enumerate(PARAMETRI_BASE):
                with c_main[j % 4]:
                    if st.checkbox(p, key=f"m_{idx}_{p}", value=(p in curr['main'])):
                        if p not in curr['main']: curr['main'].append(p)
                    else:
                        if p in curr['main']: curr['main'].remove(p)
            
            st.write("#### 🟧 LINEE SEPARATE")
            c_sep = st.columns(4)
            for j, p in enumerate(PARAMETRI_BASE):
                with c_sep[j % 4]:
                    if st.checkbox(p, key=f"s_{idx}_{p}", value=(p in curr['sep'])):
                        if p not in curr['sep']: curr['sep'].append(p)
                    else:
                        if p in curr['sep']: curr['sep'].remove(p)

            curr['punti'] = st.number_input("Punti Mappatura", min_value=1, value=curr['punti'])
            
            if st.button("✅ CONFERMA E VAI ALLA TABELLA", use_container_width=True):
                st.session_state.step_camp = 'tabella'; st.rerun()
            if st.button("⬅️ Lista Campionamenti"): st.session_state.camp_attivo = None; st.rerun()

        elif st.session_state.step_camp == 'tabella':
            st.subheader(f"📊 Dati Campo - Camp. {curr['id']}")
            if st.button("⬅️ MODIFICA SELEZIONE"): st.session_state.step_camp = 'selezione'; st.rerun()

            # Umidità
            st.markdown("---")
            st.write("### 💧 Determinazione Umidità")
            u_sel = st.selectbox("Linea per Umidità:", ["Nessuna"] + curr['main'] + curr['sep'])
            if u_sel != "Nessuna":
                if "Polveri" in u_sel:
                    c1, c2 = st.columns(2)
                    c1.number_input("Iniz. Serp. (g)", 0.0); c1.number_input("Fin. Serp. (g)", 0.0)
                    c2.number_input("Iniz. Gel (g)", 0.0); c2.number_input("Fin. Gel (g)", 0.0)
                else:
                    c1, c2 = st.columns(2)
                    c1.number_input("Somma Iniz. Gorg. (g)", 0.0); c2.number_input("Somma Fin. Gorg. (g)", 0.0)

            # Tabella
            st.write("### 📝 Punti di Prelievo")
            col_nomi = ["Punto", "ΔP (Pa)", "T Fumi (°C)"]
            if curr['main']: col_nomi += ["Vol. Main (L)", "T. Cont Main (°C)"]
            for s in curr['sep']: col_nomi += [f"Vol. {s} (L)", f"T. {s} (°C)"]
            col_nomi += ["Isocinetismo %"]
            
            df_campo = pd.DataFrame([{c: 0.0 for c in col_nomi} for _ in range(curr['punti'])])
            df_campo["Punto"] = [f"P{k+1}" for k in range(curr['punti'])]
            st.data_editor(df_campo, use_container_width=True, hide_index=True)

# ==========================================
# 5. REPORT FINALE (RdP)
# ==========================================
elif st.session_state.page == 'rdp':
    st.header("📄 Report Finale (Rapporto di Prova)")
    if not st.session_state.dati_anagrafica:
        st.warning("Nessun dato anagrafico inserito.")
    else:
        st.subheader("Riepilogo Risultati")
        st.write(f"**Ditta:** {st.session_state.dati_anagrafica.get('ditta')}")
        st.write(f"**Camino:** {st.session_state.dati_anagrafica.get('camino')}")
        st.write(f"**Portata Riferita:** {st.session_state.dati_dinamica.get('q_rif',0):.0f} Nm³/h")
        
        st.write("---")
        st.write("Campionamenti eseguiti:")
        for c in st.session_state.lista_c:
            st.write(f"- Camp. {c['id']}: {', '.join(c['main'] + c['sep'])}")
        
        st.button("📥 Esporta Documento (RdP)")

