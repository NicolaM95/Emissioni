import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Emissioni Pro v3.5 - FULL", layout="wide")

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
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'dati_anagrafica' not in st.session_state: st.session_state.dati_anagrafica = {'tecnici': []}
if 'dati_dinamica' not in st.session_state: st.session_state.dati_dinamica = {}
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
    if st.button("🏠 Home"): nav('home')
    if st.button("🗂️ Dati Generali & Tecnici"): nav('anagrafica')
    if st.button("📐 Dinamica Fumi"): nav('fumi')
    if st.button("💉 Campionamenti"): nav('camp')
    if st.button("📄 Report Finale (RdP)"): nav('rdp')

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
# ==========================================
# 3. CAMPIONAMENTI (CON VALIDAZIONE)
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
            
            st.write("#### 🟦 LINEA ISOCINETICA (es. Polveri, Metalli...)")
            m_cols = st.columns(4)
            for j, p in enumerate(PARAMETRI_BASE):
                with m_cols[j % 4]:
                    if st.checkbox(p, key=f"m_{idx}_{p}", value=(p in curr['main'])):
                        if p not in curr['main']: curr['main'].append(p)
                    else:
                        if p in curr['main']: curr['main'].remove(p)
            
            st.write("#### 🟧 LINEE SEPARATE / DERIVATE (es. COV, Aldeidi...)")
            s_cols = st.columns(4)
            for j, p in enumerate(PARAMETRI_BASE):
                with s_cols[j % 4]:
                    if st.checkbox(p, key=f"s_{idx}_{p}", value=(p in curr['sep'])):
                        if p not in curr['sep']: curr['sep'].append(p)
                    else:
                        if p in curr['sep']: curr['sep'].remove(p)

            curr['punti'] = st.number_input("Punti Campionamento", min_value=1, value=curr['punti'])
            if st.button("✅ CONFERMA E VAI ALLA TABELLA"): st.session_state.step_camp = 'tabella'; st.rerun()

        elif st.session_state.step_camp == 'tabella':
            st.subheader(f"📊 Dati Campo - Camp. {curr['id']}")
            if st.button("⬅️ TORNA A SELEZIONE"): st.session_state.step_camp = 'selezione'; st.rerun()

            # Costruzione Colonne Dinamiche
            cols = ["Punto", "ΔP (Pa)", "T Fumi (°C)"]
            if curr['main']:
                label_main = " + ".join(curr['main'])
                cols += [f"Vol. {label_main} (L)", f"T. {label_main} (°C)"]
            for s in curr['sep']:
                cols += [f"Vol. {s} (L)", f"T. {s} (°C)"]
            cols += ["Isocinetismo %"]

            # Generazione DataFrame
            if curr.get('dati') is None or len(curr['dati']) != curr['punti']:
                df_init = pd.DataFrame(0.0, index=range(curr['punti']), columns=cols)
                df_init["Punto"] = [f"P{k+1}" for k in range(curr['punti'])]
                df_init["Isocinetismo %"] = 100.0
                curr['dati'] = df_init

            # Tabella di marcia con evidenziazione automatica
            st.write("### 📝 Tabella di Marcia")
            
            # Funzione di stile per validazione
            def style_isocinetismo(val):
                color = 'lightgreen' if 95 <= val <= 115 else 'salmon'
                return f'background-color: {color}'

            # Editor
            edited_df = st.data_editor(curr['dati'], use_container_width=True, hide_index=True, key=f"edit_{idx}")
            
            # Validazione Visiva Riassuntiva
            iso_medio = edited_df["Isocinetismo %"].mean()
            if 95 <= iso_medio <= 115:
                st.success(f"✅ Isocinetismo Medio conforme: {iso_medio:.1f}%")
            else:
                st.error(f"⚠️ Isocinetismo Medio NON conforme: {iso_medio:.1f}% (Range ammesso 95-115%)")

            if st.button("💾 SALVA DEFINITIVAMENTE CAMPIONAMENTO"):
                st.session_state.lista_c[idx]['dati'] = edited_df
                st.balloons()
                st.session_state.camp_attivo = None
                st.rerun()

# ==========================================
# 4. HOME & RDP
# ==========================================
elif st.session_state.page == 'home':
    st.markdown("<p class='main-header'>🏭 Emissioni Pro v3.5</p>", unsafe_allow_html=True)
    st.write("Software professionale per la gestione dei flussi di emissione e campionamenti isocinetici.")
    st.info("Usa il menu a sinistra per iniziare l'inserimento dati.")

elif st.session_state.page == 'rdp':
    st.header("📄 Riepilogo per Rapporto di Prova")
    st.write(f"**Ditta:** {st.session_state.dati_anagrafica.get('ditta', 'N.D.')}")
    st.write(f"**Camino:** {st.session_state.dati_anagrafica.get('camino', 'N.D.')}")
    if st.session_state.dati_dinamica:
        st.write(f"**Portata Riferita:** {st.session_state.dati_dinamica['q_rif']:.0f} Nm³/h")
    
    st.write("---")
    st.write("### Stato Campionamenti")
    for c in st.session_state.lista_c:
        status = "✅ Salvato" if c['dati'] is not None else "⏳ In corso"
        st.write(f"Campionamento {c['id']}: {status}")
