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
# 2. DINAMICA FUMI (RIGHE DINAMICHE DA EXCEL)
# ==========================================
elif st.session_state.page == 'fumi':
    st.header("📐 Dinamica dei Fumi - Mappatura Excel")
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("Parametri Condotto")
        # Diametro (Cella A1 del tuo Excel)
        d_cam = st.number_input("Diametro Camino (m)", value=1.4, format="%.3f")
        
        # Coefficienti estratti dal tuo file Excel (A3-A12)
        # Questi coefficienti moltiplicati per il diametro danno l'affondamento
        coeff_excel = [0.032, 0.105, 0.194, 0.323, 0.500, 0.677, 0.806, 0.895, 0.968]
        
        # Calcoliamo quanti punti sono validi (nel tuo excel se superano il diametro o sono 0 si fermano)
        # Qui impostiamo il numero di punti in base a quanti ne servono per la normativa o quanti ne vuoi visualizzare
        n_punti_default = st.number_input("Punti da visualizzare (max 10)", value=4, min_value=1, max_value=10)
        
        k_pit = st.number_input("K Pitot", value=0.69)
        
        st.write("---")
        unit_dp = st.radio("Unità di misura ΔP:", ["mmH2O", "Pa"], horizontal=True)
        
        st.write("---")
        t_fumi = st.number_input("T. Fumi (°C)", value=259.0)
        p_atm = st.number_input("P. Atmosferica (hPa)", value=1013.25)
        p_stat_pa = st.number_input("P. Statica (Pa)", value=-10.0)
        p_ass_hpa = p_atm + (p_stat_pa / 100)
        st.metric("Pressione Assoluta", f"{p_ass_hpa:.2f} hPa")

    with c2:
        st.subheader(f"Tabella Pressioni ({unit_dp})")
        
        # --- GENERAZIONE AUTOMATICA RIGHE ---
        # Creiamo la lista degli affondamenti usando i coefficienti del tuo Excel
        affondamenti_reali = []
        for i in range(int(n_punti_default)):
            if i < len(coeff_excel):
                # Calcolo esatto come nel tuo Excel: Diametro * Coefficiente
                valor_aff = round(d_cam * coeff_excel[i], 3)
                affondamenti_reali.append(valor_aff)
        
        # Il numero di righe della tabella si adatta ora automaticamente a n_punti_default
        df_mappa = pd.DataFrame({
            "Punto": [f"P{i+1}" for i in range(len(affondamenti_reali))],
            "Affondamento (m)": affondamenti_reali,
            f"ΔP Asse X ({unit_dp})": [0.0] * len(affondamenti_reali),
            f"ΔP Asse Y ({unit_dp})": [0.0] * len(affondamenti_reali)
        })

        # L'editor mostrerà SOLO il numero di righe calcolate sopra
        edit_mappa = st.data_editor(
            df_mappa, 
            hide_index=True, 
            use_container_width=True,
            key=f"mappa_dinamica_{n_punti_default}_{d_cam}" # La chiave cambia se cambia il diametro o i punti per resettare correttamente
        )
        
        # --- CALCOLI FISICI ---
        col_x = f"ΔP Asse X ({unit_dp})"
        col_y = f"ΔP Asse Y ({unit_dp})"
        valori_dp = pd.concat([edit_mappa[col_x], edit_mappa[col_y]])
        dp_medio_in = valori_dp.mean()

        # Conversione mmH2O -> Pa per la formula della velocità
        dp_pa = dp_medio_in * 9.80665 if unit_dp == "mmH2O" else dp_medio_in
        dp_visual_mmH2O = dp_medio_in if unit_dp == "mmH2O" else dp_medio_in / 9.80665

        rho_fumi = 1.293 * (p_ass_hpa / 1013.25) * (273.15 / (t_fumi + 273.15))
        v_fumi = k_pit * np.sqrt((2 * dp_pa) / rho_fumi) if rho_fumi > 0 else 0
        area = (np.pi * d_cam**2) / 4
        
        q_aq = v_fumi * area * 3600
        q_un_s = (q_aq * (273.15/(t_fumi+273.15)) * (p_ass_hpa/1013.25)) * (1 - h_in/100)
        
        # Logica O2
        o2_rif = st.session_state.get('o2_rif', 8.0) # Recupero se presente
        q_rif = q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif)) if o2_mis < 20.8 else q_un_s

        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.write(f"**Risultato medio:** {dp_visual_mmH2O:.3f} mmH2O")
        res_c1, res_c2 = st.columns(2)
        res_c1.write(f"**Velocità:** {v_fumi:.2f} m/s")
        res_c2.write(f"**Portata Riferita:** {q_rif:.0f} Nm³/h")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("💾 Salva Mappatura"):
            st.session_state.dati_dinamica = {
                'v': v_fumi, 
                'q_rif': q_rif, 
                'tabella': edit_mappa.to_dict()
            }
            st.success(f"Mappatura a {len(affondamenti_reali)} punti salvata!")

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
