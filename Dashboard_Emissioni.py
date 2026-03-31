<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Emissioni Pro v6</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0f1117;
    --surface: #161b27;
    --surface2: #1e2535;
    --border: #2a3347;
    --accent: #3b82f6;
    --accent2: #10b981;
    --warn: #f59e0b;
    --danger: #ef4444;
    --purple: #8b5cf6;
    --text: #e2e8f0;
    --text-muted: #64748b;
    --text-dim: #94a3b8;
    --mono: 'JetBrains Mono', monospace;
    --sans: 'Syne', sans-serif;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--bg); color:var(--text); font-family:var(--sans); min-height:100vh; display:flex; }

  /* ── SIDEBAR ── */
  #sidebar {
    width:220px; min-height:100vh; background:var(--surface);
    border-right:1px solid var(--border); display:flex; flex-direction:column;
    position:fixed; top:0; left:0; bottom:0; z-index:100;
  }
  .sidebar-logo { padding:24px 20px 18px; border-bottom:1px solid var(--border); }
  .sidebar-logo .logo-tag { font-family:var(--mono); font-size:10px; color:var(--accent); letter-spacing:3px; text-transform:uppercase; margin-bottom:4px; }
  .sidebar-logo h1 { font-size:18px; font-weight:800; color:var(--text); letter-spacing:-0.5px; }
  .sidebar-logo .version { font-family:var(--mono); font-size:10px; color:var(--text-muted); margin-top:2px; }
  .nav-section { padding:14px 12px 6px; }
  .nav-label { font-family:var(--mono); font-size:9px; letter-spacing:2px; color:var(--text-muted); text-transform:uppercase; padding:0 8px; margin-bottom:6px; }
  .nav-item {
    display:flex; align-items:center; gap:10px; padding:9px 12px;
    border-radius:8px; cursor:pointer; font-size:13px; font-weight:600;
    color:var(--text-dim); transition:all .15s; margin-bottom:2px; border:1px solid transparent;
  }
  .nav-item:hover { background:var(--surface2); color:var(--text); }
  .nav-item.active { background:rgba(59,130,246,.15); color:var(--accent); border-color:rgba(59,130,246,.3); }
  .nav-item .nav-icon { font-size:14px; width:18px; text-align:center; }
  .nav-badge { margin-left:auto; font-family:var(--mono); font-size:9px; padding:2px 6px; border-radius:4px; background:var(--surface2); color:var(--text-muted); }
  .save-indicator { margin-left:auto; font-family:var(--mono); font-size:9px; color:var(--accent2); opacity:0; transition:opacity .4s; }
  .save-indicator.show { opacity:1; }
  .sidebar-footer { margin-top:auto; padding:14px 20px; border-top:1px solid var(--border); }
  .sidebar-footer-label { font-family:var(--mono); font-size:9px; color:var(--text-muted); line-height:1.7; }

  /* ── MAIN ── */
  #main { margin-left:220px; flex:1; min-height:100vh; display:flex; flex-direction:column; }
  #topbar {
    height:52px; background:var(--surface); border-bottom:1px solid var(--border);
    display:flex; align-items:center; padding:0 28px; gap:16px; position:sticky; top:0; z-index:50;
  }
  .topbar-breadcrumb { font-family:var(--mono); font-size:11px; color:var(--text-muted); display:flex; align-items:center; gap:8px; }
  .topbar-breadcrumb .sep { color:var(--border); }
  .topbar-breadcrumb .current { color:var(--accent); font-weight:700; }
  .topbar-actions { margin-left:auto; display:flex; align-items:center; gap:10px; }
  .topbar-btn {
    font-family:var(--mono); font-size:10px; padding:5px 12px; border-radius:5px; cursor:pointer;
    border:1px solid var(--border); background:var(--surface2); color:var(--text-dim);
    transition:all .15s; letter-spacing:1px; text-transform:uppercase;
  }
  .topbar-btn:hover { border-color:var(--accent); color:var(--accent); }
  .topbar-btn.green { border-color:rgba(16,185,129,.4); color:var(--accent2); background:rgba(16,185,129,.08); }
  .topbar-btn.green:hover { background:rgba(16,185,129,.15); }
  .status-dot { width:6px; height:6px; border-radius:50%; background:var(--accent2); animation:pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

  /* ── CONTENT ── */
  #content { padding:24px 28px; flex:1; overflow-y:auto; }
  .page { animation:fadeIn .2s ease; }
  @keyframes fadeIn { from{opacity:0;transform:translateY(5px)} to{opacity:1;transform:none} }

  /* ── HOME ── */
  .home-header { margin-bottom:28px; }
  .home-header .greeting { font-family:var(--mono); font-size:11px; color:var(--accent); letter-spacing:2px; text-transform:uppercase; margin-bottom:8px; }
  .home-header h2 { font-size:26px; font-weight:800; letter-spacing:-0.5px; }
  .home-header p { font-size:13px; color:var(--text-muted); margin-top:6px; }
  .module-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
  .module-card {
    background:var(--surface); border:1px solid var(--border); border-radius:12px;
    padding:22px; cursor:pointer; transition:all .2s; position:relative; overflow:hidden;
  }
  .module-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:var(--accent); opacity:0; transition:opacity .2s; }
  .module-card:hover { border-color:var(--accent); transform:translateY(-2px); }
  .module-card:hover::before { opacity:1; }
  .card-icon { font-size:26px; margin-bottom:12px; }
  .card-title { font-size:14px; font-weight:800; margin-bottom:5px; }
  .card-desc { font-size:11px; color:var(--text-muted); line-height:1.5; }
  .card-status { margin-top:14px; font-family:var(--mono); font-size:10px; letter-spacing:1px; padding:3px 7px; border-radius:4px; display:inline-block; }
  .card-status.active { background:rgba(16,185,129,.15); color:var(--accent2); }

  /* ── SHARED PANELS ── */
  .page-title { font-size:19px; font-weight:800; letter-spacing:-0.3px; margin-bottom:3px; }
  .page-subtitle { font-family:var(--mono); font-size:10px; color:var(--text-muted); margin-bottom:20px; }
  .layout-cols { display:grid; gap:18px; }
  .layout-2col { grid-template-columns:270px 1fr; }
  .param-panel { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:18px; }
  .panel-title { font-family:var(--mono); font-size:9px; letter-spacing:2px; color:var(--accent); text-transform:uppercase; margin-bottom:14px; display:flex; align-items:center; gap:8px; }
  .panel-title::after { content:''; flex:1; height:1px; background:var(--border); }
  .field-group { margin-bottom:10px; }
  .field-label { display:block; font-family:var(--mono); font-size:9px; color:var(--text-muted); letter-spacing:1px; text-transform:uppercase; margin-bottom:4px; }
  .field-input {
    width:100%; background:var(--bg); border:1px solid var(--border); border-radius:6px;
    padding:7px 10px; font-family:var(--mono); font-size:12px; color:var(--text);
    outline:none; transition:border-color .15s;
  }
  .field-input:focus { border-color:var(--accent); }
  .field-input:hover { border-color:var(--text-muted); }
  .field-row { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
  .divider { height:1px; background:var(--border); margin:14px 0; }
  .right-col { display:flex; flex-direction:column; gap:16px; }

  /* ── ΔP TABLE ── */
  .dp-section { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:18px; }
  .unit-toggle { display:flex; background:var(--bg); border:1px solid var(--border); border-radius:6px; padding:2px; width:fit-content; margin-bottom:14px; }
  .unit-toggle button { padding:4px 12px; border:none; border-radius:4px; font-family:var(--mono); font-size:11px; cursor:pointer; transition:all .15s; background:transparent; color:var(--text-muted); font-weight:600; }
  .unit-toggle button.active { background:var(--accent); color:#fff; }
  .dp-table { width:100%; border-collapse:collapse; }
  .dp-table th { font-family:var(--mono); font-size:9px; letter-spacing:2px; color:var(--text-muted); text-transform:uppercase; text-align:left; padding:7px 8px; border-bottom:1px solid var(--border); background:var(--bg); }
  .dp-table td { padding:5px 6px; border-bottom:1px solid rgba(42,51,71,.5); vertical-align:middle; }
  .dp-table td:first-child { font-family:var(--mono); font-size:11px; color:var(--accent); font-weight:700; width:44px; }
  .dp-table td:nth-child(2) { font-family:var(--mono); font-size:11px; color:var(--text-dim); width:80px; }
  .dp-table tr:last-child td { border-bottom:none; }
  .dp-input { width:100%; background:var(--bg); border:1px solid var(--border); border-radius:4px; padding:4px 7px; font-family:var(--mono); font-size:12px; color:var(--text); outline:none; transition:border-color .15s; }
  .dp-input:focus { border-color:var(--accent); }
  .dp-avg-row { display:flex; align-items:center; justify-content:flex-end; gap:10px; margin-top:8px; padding-top:8px; border-top:1px solid var(--border); }
  .dp-avg-label { font-family:var(--mono); font-size:9px; color:var(--text-muted); letter-spacing:1px; }
  .dp-avg-val { font-family:var(--mono); font-size:14px; font-weight:700; color:var(--warn); }

  /* ── RESULTS ── */
  .results-row { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin-bottom:14px; }
  .res-card { background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:14px; text-align:center; transition:border-color .2s; }
  .res-card:hover { border-color:var(--accent); }
  .res-label { font-family:var(--mono); font-size:8px; letter-spacing:2px; color:var(--text-muted); text-transform:uppercase; margin-bottom:6px; display:block; }
  .res-value { font-family:var(--mono); font-size:20px; font-weight:700; color:var(--accent); display:block; line-height:1; }
  .res-unit { font-family:var(--mono); font-size:9px; color:var(--text-muted); margin-top:3px; display:block; }
  .target-box { background:rgba(59,130,246,.08); border:1px solid rgba(59,130,246,.3); border-radius:10px; padding:14px 20px; display:flex; align-items:center; gap:16px; margin-bottom:14px; }
  .target-label { font-family:var(--mono); font-size:9px; letter-spacing:2px; color:var(--text-muted); text-transform:uppercase; }
  .target-value { font-family:var(--mono); font-size:26px; font-weight:700; color:var(--accent); }
  .target-unit { font-family:var(--mono); font-size:11px; color:var(--text-dim); }
  .info-chips { display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }
  .info-chip { background:var(--surface2); border:1px solid var(--border); border-radius:5px; padding:4px 8px; font-family:var(--mono); font-size:9px; color:var(--text-dim); }
  .info-chip span { color:var(--accent); font-weight:700; }

  /* ══════════════════════════════════════
     CAMPIONAMENTO PAGE
  ══════════════════════════════════════ */
  .camp-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px; }
  .camp-table { width:100%; border-collapse:collapse; }
  .camp-table th { font-family:var(--mono); font-size:9px; letter-spacing:1.5px; color:var(--text-muted); text-transform:uppercase; padding:7px 10px; border-bottom:1px solid var(--border); background:var(--bg); text-align:left; }
  .camp-table td { padding:5px 8px; border-bottom:1px solid rgba(42,51,71,.4); font-family:var(--mono); font-size:11px; color:var(--text-dim); vertical-align:middle; }
  .camp-table tr:last-child td { border-bottom:none; }
  .camp-table td:first-child { color:var(--accent); font-weight:700; width:60px; }
  .camp-table input { width:100%; background:var(--bg); border:1px solid var(--border); border-radius:4px; padding:4px 7px; font-family:var(--mono); font-size:11px; color:var(--text); outline:none; }
  .camp-table input:focus { border-color:var(--accent); }
  .camp-kpi-row { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:14px; }
  .camp-kpi { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:12px 14px; }
  .camp-kpi .ck-label { font-family:var(--mono); font-size:8px; letter-spacing:2px; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px; }
  .camp-kpi .ck-value { font-family:var(--mono); font-size:17px; font-weight:700; }
  .camp-kpi .ck-value.ok { color:var(--accent2); }
  .camp-kpi .ck-value.warn { color:var(--warn); }
  .camp-kpi .ck-value.bad { color:var(--danger); }
  .camp-kpi .ck-unit { font-family:var(--mono); font-size:9px; color:var(--text-muted); }
  .iso-status-bar { border-radius:8px; padding:12px 18px; display:flex; align-items:center; gap:14px; margin-bottom:14px; font-family:var(--mono); font-size:12px; font-weight:700; }
  .iso-status-bar.ok { background:rgba(16,185,129,.1); border:1px solid rgba(16,185,129,.3); color:var(--accent2); }
  .iso-status-bar.warn { background:rgba(245,158,11,.1); border:1px solid rgba(245,158,11,.3); color:var(--warn); }
  .iso-status-bar.bad { background:rgba(239,68,68,.1); border:1px solid rgba(239,68,68,.3); color:var(--danger); }
  .iso-big { font-size:22px; }

  /* ══════════════════════════════════════
     REPORT PAGE
  ══════════════════════════════════════ */
  .report-meta-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:18px; }
  .report-preview {
    background:var(--surface); border:1px solid var(--border); border-radius:10px;
    padding:28px 32px; font-family:var(--mono); font-size:11px; line-height:1.8; color:var(--text-dim);
    white-space:pre-wrap; max-height:420px; overflow-y:auto; margin-bottom:16px;
  }
  .report-preview .rp-title { font-size:14px; font-weight:700; color:var(--text); margin-bottom:16px; border-bottom:1px solid var(--border); padding-bottom:10px; }
  .report-preview .rp-section { color:var(--accent); font-size:10px; letter-spacing:2px; text-transform:uppercase; margin:14px 0 6px; }
  .report-preview .rp-row { display:flex; gap:12px; }
  .report-preview .rp-key { color:var(--text-muted); min-width:200px; }
  .report-preview .rp-val { color:var(--text); font-weight:600; }
  .export-actions { display:flex; gap:10px; flex-wrap:wrap; }
  .export-btn {
    font-family:var(--mono); font-size:11px; padding:9px 18px; border-radius:7px;
    cursor:pointer; border:1px solid var(--border); background:var(--surface2);
    color:var(--text-dim); transition:all .15s; font-weight:600; letter-spacing:0.5px;
  }
  .export-btn:hover { transform:translateY(-1px); }
  .export-btn.primary { background:rgba(59,130,246,.15); border-color:rgba(59,130,246,.4); color:var(--accent); }
  .export-btn.primary:hover { background:rgba(59,130,246,.25); }
  .export-btn.green { background:rgba(16,185,129,.1); border-color:rgba(16,185,129,.3); color:var(--accent2); }
  .export-btn.green:hover { background:rgba(16,185,129,.2); }
  .export-btn.purple { background:rgba(139,92,246,.1); border-color:rgba(139,92,246,.3); color:var(--purple); }
  .export-btn.purple:hover { background:rgba(139,92,246,.2); }

  /* ── TOAST ── */
  #toast {
    position:fixed; bottom:24px; right:24px; background:var(--surface2);
    border:1px solid var(--border); border-radius:8px; padding:12px 18px;
    font-family:var(--mono); font-size:11px; color:var(--text); z-index:999;
    opacity:0; transform:translateY(8px); transition:all .25s; pointer-events:none;
  }
  #toast.show { opacity:1; transform:translateY(0); }
  #toast.ok { border-color:rgba(16,185,129,.5); color:var(--accent2); }
  #toast.warn { border-color:rgba(245,158,11,.5); color:var(--warn); }

  ::-webkit-scrollbar { width:5px; }
  ::-webkit-scrollbar-track { background:var(--bg); }
  ::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
</style>
</head>
<body>

<!-- ═══ SIDEBAR ═══ -->
<nav id="sidebar">
  <div class="sidebar-logo">
    <div class="logo-tag">Tecnico Emissioni</div>
    <h1>EMISSIONI<br>PRO</h1>
    <div class="version">v6.0 · ISO 16911-1</div>
  </div>

  <div class="nav-section">
    <div class="nav-label">Principale</div>
    <div class="nav-item active" id="nav-home" onclick="showPage('home')">
      <span class="nav-icon">⬛</span> Dashboard
    </div>
  </div>

  <div class="nav-section" id="sidebar-emissioni" style="display:none;">
    <div class="nav-label">Modulo Emissioni</div>
    <div class="nav-item" id="nav-fumi" onclick="showPage('fumi')">
      <span class="nav-icon">💨</span> Dinamica Fumi
    </div>
    <div class="nav-item" id="nav-campionamento" onclick="showPage('campionamento')">
      <span class="nav-icon">⚗️</span> Campionamento
    </div>
    <div class="nav-item" id="nav-report" onclick="showPage('report'); buildReport()">
      <span class="nav-icon">📋</span> Report
    </div>
  </div>

  <div class="sidebar-footer">
    <div class="sidebar-footer-label">
      UNI EN 15259<br>ISO 16911-1<br>
      <span style="color:var(--accent2);" id="session-info">Sessione: —</span>
    </div>
  </div>
</nav>

<!-- ═══ MAIN ═══ -->
<div id="main">
  <div id="topbar">
    <div class="topbar-breadcrumb">
      <span>EMISSIONI PRO</span>
      <span class="sep">›</span>
      <span class="current" id="breadcrumb-text">Dashboard</span>
    </div>
    <div class="topbar-actions">
      <button class="topbar-btn green" onclick="salvaSessione()">💾 Salva Sessione</button>
      <button class="topbar-btn" onclick="caricaSessione()">📂 Carica</button>
      <button class="topbar-btn" onclick="nuovaSessione()">✕ Nuova</button>
      <div class="status-dot" style="margin-left:6px;"></div>
    </div>
  </div>

  <div id="content">

    <!-- ══════════════════════════════════
         HOME
    ══════════════════════════════════ -->
    <div id="page-home" class="page">
      <div class="home-header">
        <div class="greeting">BENVENUTO</div>
        <h2>Dashboard Principale</h2>
        <p>Seleziona un modulo per accedere agli strumenti di campionamento e calcolo.</p>
      </div>
      <div class="module-grid">
        <div class="module-card" onclick="openModule('emissioni')">
          <div class="card-icon">🌿</div>
          <div class="card-title">EMISSIONI</div>
          <div class="card-desc">Dinamica fumi, isocinetismo, portate normali e riferite. Campionamento isocinético. Report tecnico.</div>
          <div class="card-status active">● ATTIVO</div>
        </div>
        <div class="module-card" style="opacity:.4;cursor:not-allowed;">
          <div class="card-icon">📜</div>
          <div class="card-title">CERTIFICATI</div>
          <div class="card-desc">Generazione certificati di campionamento e report analitici strutturati.</div>
          <div class="card-status" style="background:rgba(100,116,139,.1);color:var(--text-muted);">— IN SVILUPPO</div>
        </div>
        <div class="module-card" style="opacity:.4;cursor:not-allowed;">
          <div class="card-icon">🔥</div>
          <div class="card-title">FORNI</div>
          <div class="card-desc">Gestione campagne su forni industriali, vetro e ceramica. Bilanci termici.</div>
          <div class="card-status" style="background:rgba(100,116,139,.1);color:var(--text-muted);">— IN SVILUPPO</div>
        </div>
      </div>

      <!-- Sessioni salvate -->
      <div style="margin-top:28px;">
        <div class="panel-title" style="margin-bottom:12px;">Sessioni Salvate</div>
        <div id="sessions-list" style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;"></div>
      </div>
    </div>

    <!-- ══════════════════════════════════
         DINAMICA FUMI
    ══════════════════════════════════ -->
    <div id="page-fumi" class="page" style="display:none;">
      <div class="page-title">Dinamica Fumi & Portate</div>
      <div class="page-subtitle">PITOT S · ISO 16911-1 · CALCOLO PORTATE NORMALI E RIFERITE</div>

      <div class="layout-cols layout-2col">
        <!-- LEFT -->
        <div>
          <div class="param-panel">
            <div class="panel-title">Geometria & Pitot</div>
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">Ø Camino (m)</label>
                <input class="field-input" type="number" id="d_cam" value="1.4" step="0.01" oninput="calcola()">
              </div>
              <div class="field-group">
                <label class="field-label">Kp Pitot</label>
                <input class="field-input" type="number" id="k_pit" value="0.69" step="0.001" oninput="calcola()">
              </div>
            </div>
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">T. Fumi (°C)</label>
                <input class="field-input" type="number" id="t_fumi" value="259" step="0.1" oninput="calcola()">
              </div>
              <div class="field-group">
                <label class="field-label">T. Amb. (°C)</label>
                <input class="field-input" type="number" id="t_amb" value="20" step="0.1" oninput="calcola()">
              </div>
            </div>
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">P. Atm (hPa)</label>
                <input class="field-input" type="number" id="p_atm" value="1013.25" step="0.01" oninput="calcola()">
              </div>
              <div class="field-group">
                <label class="field-label">P. Statica (Pa)</label>
                <input class="field-input" type="number" id="p_stat" value="-10" step="1" oninput="calcola()">
              </div>
            </div>
            <div class="divider"></div>
            <div class="panel-title">Gas & Umidità</div>
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">H₂O (%)</label>
                <input class="field-input" type="number" id="h2o" value="4.68" step="0.01" oninput="calcola()">
              </div>
              <div class="field-group">
                <label class="field-label">O₂ mis. (%)</label>
                <input class="field-input" type="number" id="o2_mis" value="14.71" step="0.01" oninput="calcola()">
              </div>
            </div>
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">CO₂ mis. (%)</label>
                <input class="field-input" type="number" id="co2_mis" value="12.0" step="0.01" oninput="calcola()">
              </div>
              <div class="field-group">
                <label class="field-label">O₂ rif. (%)</label>
                <input class="field-input" type="number" id="o2_rif" value="8.0" step="0.1" oninput="calcola()">
              </div>
            </div>
            <div class="divider"></div>
            <div class="panel-title">Ugello Target</div>
            <div class="field-group">
              <label class="field-label">Ø Ugello (mm)</label>
              <input class="field-input" type="number" id="d_ugello" value="6.0" step="0.5" oninput="calcola()">
            </div>
            <div class="info-chips" id="density-chips"></div>
          </div>
        </div>

        <!-- RIGHT -->
        <div class="right-col">
          <div class="dp-section">
            <div class="panel-title">Mappatura ΔP — Punti di Misura</div>
            <div class="unit-toggle">
              <button class="active" id="btn-mmh2o" onclick="setUnit('mmH2O')">mmH₂O</button>
              <button id="btn-pa" onclick="setUnit('Pa')">Pa</button>
            </div>
            <table class="dp-table">
              <thead><tr><th>Punto</th><th>Affond. (cm)</th><th>Asse 1</th><th>Asse 2</th></tr></thead>
              <tbody id="dp-tbody"></tbody>
            </table>
            <div class="dp-avg-row">
              <span class="dp-avg-label">ΔP MEDIO VALIDO</span>
              <span class="dp-avg-val" id="dp-avg">—</span>
            </div>
          </div>

          <div>
            <div class="results-row">
              <div class="res-card"><span class="res-label">Velocità</span><span class="res-value" id="r-vel">—</span><span class="res-unit">m/s</span></div>
              <div class="res-card"><span class="res-label">Q Camino</span><span class="res-value" id="r-qaq">—</span><span class="res-unit">Am³/h</span></div>
              <div class="res-card"><span class="res-label">Q Umida</span><span class="res-value" id="r-quu">—</span><span class="res-unit">Nm³/h u</span></div>
              <div class="res-card"><span class="res-label">Q Secca</span><span class="res-value" id="r-qus">—</span><span class="res-unit">Nm³/h s</span></div>
              <div class="res-card"><span class="res-label">Q Rif.</span><span class="res-value" id="r-qrif">—</span><span class="res-unit">Nm³/h</span></div>
            </div>
            <div class="target-box" id="target-box" style="display:none;">
              <div>
                <div class="target-label">Target Pompa — Ø <span id="target-ugello">—</span> mm</div>
                <div style="display:flex;align-items:baseline;gap:8px;margin-top:4px;">
                  <span class="target-value" id="r-qpompa">—</span>
                  <span class="target-unit">L/min</span>
                </div>
              </div>
              <div style="margin-left:auto;text-align:right;">
                <div style="font-family:var(--mono);font-size:9px;color:var(--text-muted);margin-bottom:4px;">PORTATE CORRETTE</div>
                <div class="info-chip">p_ass / p_atm · T_amb / T_fumi</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════
         CAMPIONAMENTO ISOCINÉTICO
    ══════════════════════════════════ -->
    <div id="page-campionamento" class="page" style="display:none;">
      <div class="page-title">Campionamento Isocinético</div>
      <div class="page-subtitle">VERIFICA ISOCINETISMO · ISO 16911-1 SEC. 8 · DATI DA DINAMICA FUMI</div>

      <!-- Status bar isocinetismo -->
      <div class="iso-status-bar ok" id="iso-status-bar">
        <span class="iso-big" id="iso-icon">✓</span>
        <div>
          <div id="iso-status-title" style="font-size:13px;">In attesa dati</div>
          <div id="iso-status-sub" style="font-size:10px;font-weight:400;opacity:.7;margin-top:2px;">Inserire dati campionamento per calcolare isocinetismo</div>
        </div>
        <div style="margin-left:auto;font-size:20px;font-weight:800;" id="iso-pct-big">—</div>
      </div>

      <!-- KPI row -->
      <div class="camp-kpi-row">
        <div class="camp-kpi">
          <div class="ck-label">% Isocinetismo</div>
          <div class="ck-value ok" id="ck-iso">—</div>
          <div class="ck-unit">target: 95–105%</div>
        </div>
        <div class="camp-kpi">
          <div class="ck-label">V campionato totale</div>
          <div class="ck-value" id="ck-vcamp" style="color:var(--text);">—</div>
          <div class="ck-unit">L (ambiente)</div>
        </div>
        <div class="camp-kpi">
          <div class="ck-label">Vol. teorico isocinético</div>
          <div class="ck-value" id="ck-vteor" style="color:var(--text-dim);">—</div>
          <div class="ck-unit">L (ambiente)</div>
        </div>
        <div class="camp-kpi">
          <div class="ck-label">Portata effettiva pompa</div>
          <div class="ck-value" id="ck-qeff" style="color:var(--text);">—</div>
          <div class="ck-unit">L/min (media)</div>
        </div>
      </div>

      <div class="layout-cols layout-2col">
        <!-- LEFT: parametri campionamento -->
        <div>
          <div class="param-panel">
            <div class="panel-title">Parametri Campione</div>
            <div class="field-group">
              <label class="field-label">N° Punti campionati</label>
              <input class="field-input" type="number" id="c_npunti" value="6" min="1" max="12" oninput="buildCampTable(); calcolaCamp()">
            </div>
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">Durata per punto (min)</label>
                <input class="field-input" type="number" id="c_durata" value="10" step="1" oninput="calcolaCamp()">
              </div>
              <div class="field-group">
                <label class="field-label">Ø Ugello usato (mm)</label>
                <input class="field-input" type="number" id="c_ugello" value="6.0" step="0.5" oninput="calcolaCamp()">
              </div>
            </div>
            <div class="divider"></div>
            <div class="panel-title">Condizioni Misuratore</div>
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">T gas cont. (°C)</label>
                <input class="field-input" type="number" id="c_t_cont" value="20" step="0.1" oninput="calcolaCamp()">
              </div>
              <div class="field-group">
                <label class="field-label">P cont. (hPa)</label>
                <input class="field-input" type="number" id="c_p_cont" value="1013.25" step="0.1" oninput="calcolaCamp()">
              </div>
            </div>
            <div class="divider"></div>
            <div class="panel-title">Parametri da Dinamica Fumi</div>
            <div class="info-chips" id="camp-fumi-chips">
              <div class="info-chip" style="color:var(--text-muted);">Completa prima la Dinamica Fumi</div>
            </div>
          </div>
        </div>

        <!-- RIGHT: tabella punti campionamento -->
        <div>
          <div class="param-panel">
            <div class="panel-title">Dati per Punto di Campionamento</div>
            <table class="camp-table" id="camp-table">
              <thead>
                <tr>
                  <th>Punto</th>
                  <th>Aff. (cm)</th>
                  <th>Q pompa (L/min)</th>
                  <th>Vol. letto (L)</th>
                  <th>T filtro (°C)</th>
                </tr>
              </thead>
              <tbody id="camp-tbody"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════
         REPORT
    ══════════════════════════════════ -->
    <div id="page-report" class="page" style="display:none;">
      <div class="page-title">Report Tecnico</div>
      <div class="page-subtitle">GENERAZIONE RAPPORTO · ESPORTAZIONE DATI</div>

      <div class="layout-cols layout-2col">
        <div>
          <div class="param-panel">
            <div class="panel-title">Dati Intestazione</div>
            <div class="field-group">
              <label class="field-label">Committente</label>
              <input class="field-input" type="text" id="r_committente" placeholder="Ragione sociale..." oninput="buildReport()">
            </div>
            <div class="field-group">
              <label class="field-label">Impianto / Camino</label>
              <input class="field-input" type="text" id="r_impianto" placeholder="es. Forno vetro — Camino 1" oninput="buildReport()">
            </div>
            <div class="field-row">
              <div class="field-group">
                <label class="field-label">Data campionamento</label>
                <input class="field-input" type="date" id="r_data" oninput="buildReport()">
              </div>
              <div class="field-group">
                <label class="field-label">Tecnico campionatore</label>
                <input class="field-input" type="text" id="r_tecnico" placeholder="Nome..." oninput="buildReport()">
              </div>
            </div>
            <div class="field-group">
              <label class="field-label">Note / Condizioni operative</label>
              <textarea class="field-input" id="r_note" rows="3" placeholder="Condizioni meteo, note campo..." style="resize:vertical;" oninput="buildReport()"></textarea>
            </div>
            <div class="divider"></div>
            <div class="panel-title">Esportazione</div>
            <div class="export-actions">
              <button class="export-btn primary" onclick="exportTXT()">📄 Esporta TXT</button>
              <button class="export-btn green" onclick="exportCSV()">📊 Esporta CSV</button>
              <button class="export-btn purple" onclick="exportJSON()">{ } Esporta JSON</button>
              <button class="export-btn" onclick="window.print()">🖨️ Stampa</button>
            </div>
          </div>
        </div>

        <div>
          <div class="panel-title">Anteprima Report</div>
          <div class="report-preview" id="report-preview">
            <div class="rp-title">RAPPORTO DI CAMPIONAMENTO — EMISSIONI PRO v6</div>
            <div style="color:var(--text-muted);font-size:10px;">← Compila i campi a sinistra e completa la Dinamica Fumi per generare il report.</div>
          </div>
        </div>
      </div>
    </div>

  </div><!-- /content -->
</div><!-- /main -->

<!-- TOAST -->
<div id="toast"></div>

<script>
// ═══════════════════════════════════════════════════════════
//  STATE GLOBALE
// ═══════════════════════════════════════════════════════════
let currentUnit = 'mmH2O';
let currentPage = 'home';
let numPunti = 0;
let numCampPunti = 0;
let calcState = {
  v_fumi: 0, q_aq: 0, q_un_u: 0, q_un_s: 0, q_rif: 0,
  q_pompa: 0, d_cam: 0, t_fumi: 0, p_atm: 0, p_ass_hpa: 0,
  rho_fumi: 0, h2o: 0, o2_mis: 0, co2_mis: 0, o2_rif: 0,
  dp_avg: 0, d_ugello: 0, t_amb: 0
};

// ═══════════════════════════════════════════════════════════
//  NAVIGAZIONE
// ═══════════════════════════════════════════════════════════
function showPage(page) {
  document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + page).style.display = 'block';
  const nav = document.getElementById('nav-' + page);
  if (nav) nav.classList.add('active');
  const labels = { home:'Dashboard', fumi:'Dinamica Fumi', campionamento:'Campionamento Isocinético', report:'Report Tecnico' };
  document.getElementById('breadcrumb-text').textContent = labels[page] || page;
  currentPage = page;
  if (page === 'campionamento') { syncCampFumiChips(); calcolaCamp(); }
  if (page === 'report') buildReport();
}

function openModule(mod) {
  if (mod === 'emissioni') {
    document.getElementById('sidebar-emissioni').style.display = 'block';
    showPage('fumi');
    buildTable();
    calcola();
  }
}

// ═══════════════════════════════════════════════════════════
//  DINAMICA FUMI — TABELLA ΔP
// ═══════════════════════════════════════════════════════════
function getCoeffs(d) {
  if (d < 0.35) return [0.500];
  if (d < 1.10) return [0.146, 0.854];
  if (d < 1.60) return [0.067, 0.250, 0.750, 0.933];
  return [0.044, 0.146, 0.296, 0.704, 0.854, 0.956];
}

function buildTable() {
  const d = parseFloat(document.getElementById('d_cam').value) || 1.4;
  const coeffs = getCoeffs(d);
  numPunti = coeffs.length;
  const tbody = document.getElementById('dp-tbody');
  tbody.innerHTML = '';
  coeffs.forEach((c, i) => {
    const aff = (d * c * 100).toFixed(1);
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>P${i+1}</td><td>${aff}</td>
      <td><input class="dp-input" type="number" id="dp_a${i}" placeholder="—" step="0.1" oninput="calcola()"></td>
      <td><input class="dp-input" type="number" id="dp_b${i}" placeholder="—" step="0.1" oninput="calcola()"></td>`;
    tbody.appendChild(tr);
  });
}

function setUnit(u) {
  currentUnit = u;
  document.getElementById('btn-mmh2o').classList.toggle('active', u === 'mmH2O');
  document.getElementById('btn-pa').classList.toggle('active', u === 'Pa');
  calcola();
}

// ═══════════════════════════════════════════════════════════
//  CALCOLO PRINCIPALE — logica invariata dal Streamlit
// ═══════════════════════════════════════════════════════════
function calcola() {
  const d_cam   = parseFloat(document.getElementById('d_cam').value)   || 0;
  const k_pit   = parseFloat(document.getElementById('k_pit').value)   || 0;
  const t_fumi  = parseFloat(document.getElementById('t_fumi').value)  || 0;
  const t_amb   = parseFloat(document.getElementById('t_amb').value)   || 20;
  const p_atm   = parseFloat(document.getElementById('p_atm').value)   || 1013.25;
  const p_stat  = parseFloat(document.getElementById('p_stat').value)  || 0;
  const h2o     = parseFloat(document.getElementById('h2o').value)     || 0;
  const o2_mis  = parseFloat(document.getElementById('o2_mis').value)  || 0;
  const co2_mis = parseFloat(document.getElementById('co2_mis').value) || 0;
  const o2_rif  = parseFloat(document.getElementById('o2_rif').value)  || 8;
  const d_u     = parseFloat(document.getElementById('d_ugello').value)|| 6;

  const coeffs = getCoeffs(d_cam);
  if (coeffs.length !== numPunti) buildTable();

  const dp_list = [];
  for (let i = 0; i < numPunti; i++) {
    const va = parseFloat(document.getElementById('dp_a' + i)?.value);
    const vb = parseFloat(document.getElementById('dp_b' + i)?.value);
    if (!isNaN(va) && va > 0) dp_list.push(va);
    if (!isNaN(vb) && vb > 0) dp_list.push(vb);
  }

  const dp_avg = dp_list.length > 0 ? dp_list.reduce((a,b) => a+b,0) / dp_list.length : 0;
  document.getElementById('dp-avg').textContent = dp_avg > 0
    ? dp_avg.toFixed(2) + (currentUnit === 'mmH2O' ? ' mmH₂O' : ' Pa') : '—';

  const p_ass_pa  = (p_atm * 100) + p_stat;
  const p_ass_hpa = p_ass_pa / 100;

  const m_wet = (
    (o2_mis/100 * 31.999) +
    (co2_mis/100 * 44.01) +
    ((100 - o2_mis - co2_mis)/100 * 28.013)
  ) * (1 - h2o/100) + (18.015 * h2o/100);

  const rho_fumi = (p_ass_pa * m_wet) / (8314.47 * (t_fumi + 273.15));

  document.getElementById('density-chips').innerHTML = `
    <div class="info-chip">M_wet: <span>${m_wet.toFixed(3)}</span> g/mol</div>
    <div class="info-chip">ρ_fumi: <span>${rho_fumi.toFixed(4)}</span> kg/m³</div>
    <div class="info-chip">P_ass: <span>${p_ass_hpa.toFixed(2)}</span> hPa</div>`;

  let v_fumi = 0;
  if (dp_list.length > 0 && rho_fumi > 0) {
    const factor = currentUnit === 'mmH2O' ? 9.80665 : 1.0;
    const v_vals = dp_list.map(dp => Math.sqrt(k_pit) * Math.sqrt((2 * dp * factor) / rho_fumi));
    v_fumi = v_vals.reduce((a,b) => a+b,0) / v_vals.length;
  }

  const A_cam  = Math.PI * d_cam * d_cam / 4;
  const q_aq   = v_fumi * A_cam * 3600;
  const q_un_u = q_aq * (273.15 / (t_fumi + 273.15)) * (p_ass_hpa / 1013.25);
  const q_un_s = q_un_u * (1 - h2o/100);
  const q_rif  = o2_mis < 20.8 ? q_un_s * ((20.9 - o2_mis) / (20.9 - o2_rif)) : q_un_s;

  const fmt = (v, dec=0) => v > 0 ? v.toFixed(dec) : '—';
  document.getElementById('r-vel').textContent  = fmt(v_fumi, 2);
  document.getElementById('r-qaq').textContent  = fmt(q_aq);
  document.getElementById('r-quu').textContent  = fmt(q_un_u);
  document.getElementById('r-qus').textContent  = fmt(q_un_s);
  document.getElementById('r-qrif').textContent = fmt(q_rif);

  const tbox = document.getElementById('target-box');
  let q_pompa = 0;
  if (v_fumi > 0) {
    const A_ugello = Math.PI * Math.pow(d_u/1000, 2) / 4;
    q_pompa = (v_fumi * A_ugello * 3600 * 1000 / 60) * (p_ass_hpa / p_atm) * ((t_amb + 273.15) / (t_fumi + 273.15));
    document.getElementById('r-qpompa').textContent = q_pompa.toFixed(2);
    document.getElementById('target-ugello').textContent = d_u;
    tbox.style.display = 'flex';
  } else {
    tbox.style.display = 'none';
  }

  // Aggiorna stato globale per gli altri moduli
  calcState = { v_fumi, q_aq, q_un_u, q_un_s, q_rif, q_pompa,
    d_cam, t_fumi, p_atm, p_ass_hpa, rho_fumi, h2o, o2_mis, co2_mis, o2_rif,
    dp_avg, d_ugello: d_u, t_amb, k_pit };
}

// ═══════════════════════════════════════════════════════════
//  CAMPIONAMENTO ISOCINÉTICO
// ═══════════════════════════════════════════════════════════
function buildCampTable() {
  const n = parseInt(document.getElementById('c_npunti').value) || 6;
  numCampPunti = n;
  const d = calcState.d_cam || 1.4;
  const coeffs = getCoeffs(d);

  const tbody = document.getElementById('camp-tbody');
  tbody.innerHTML = '';
  for (let i = 0; i < n; i++) {
    const aff = coeffs[i] !== undefined ? (d * coeffs[i] * 100).toFixed(1) : '—';
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>P${i+1}</td><td>${aff}</td>
      <td><input type="number" id="c_q${i}" value="${calcState.q_pompa > 0 ? calcState.q_pompa.toFixed(2) : ''}" step="0.01" oninput="calcolaCamp()"></td>
      <td><input type="number" id="c_v${i}" step="0.01" oninput="calcolaCamp()"></td>
      <td><input type="number" id="c_tf${i}" value="${calcState.t_fumi || 259}" step="0.1" oninput="calcolaCamp()"></td>`;
    tbody.appendChild(tr);
  }
}

function syncCampFumiChips() {
  const cs = calcState;
  const chips = document.getElementById('camp-fumi-chips');
  if (cs.v_fumi > 0) {
    chips.innerHTML = `
      <div class="info-chip">v: <span>${cs.v_fumi.toFixed(2)}</span> m/s</div>
      <div class="info-chip">Q_rif: <span>${cs.q_rif.toFixed(0)}</span> Nm³/h</div>
      <div class="info-chip">T fumi: <span>${cs.t_fumi}</span> °C</div>
      <div class="info-chip">Q_pompa: <span>${cs.q_pompa.toFixed(2)}</span> L/min</div>
      <div class="info-chip">Ø cam: <span>${cs.d_cam}</span> m</div>`;
    // pre-fill ugello se non già modificato
    const cu = document.getElementById('c_ugello');
    if (cs.d_ugello) cu.value = cs.d_ugello;
  } else {
    chips.innerHTML = '<div class="info-chip" style="color:var(--warn);">⚠ Completa prima la Dinamica Fumi</div>';
  }
}

function calcolaCamp() {
  if (numCampPunti === 0) buildCampTable();
  const durata   = parseFloat(document.getElementById('c_durata').value)  || 10;
  const d_u      = parseFloat(document.getElementById('c_ugello').value)  || 6;
  const t_cont   = parseFloat(document.getElementById('c_t_cont').value)  || 20;
  const p_cont   = parseFloat(document.getElementById('c_p_cont').value)  || 1013.25;
  const cs       = calcState;

  // Raccolta dati punti
  let q_list = [], v_list = [];
  for (let i = 0; i < numCampPunti; i++) {
    const q = parseFloat(document.getElementById('c_q' + i)?.value);
    const v = parseFloat(document.getElementById('c_v' + i)?.value);
    if (!isNaN(q) && q > 0) q_list.push(q);
    if (!isNaN(v) && v > 0) v_list.push(v);
  }

  const q_avg   = q_list.length > 0 ? q_list.reduce((a,b)=>a+b,0)/q_list.length : 0;
  const v_camp  = v_list.reduce((a,b)=>a+b, 0); // totale volumi letto

  // Volume teorico isocinético (portata pompa target × durata totale × n punti)
  // v_teor = Q_iso_pompa [L/min] × durata [min] × n_punti
  const v_teor = cs.q_pompa > 0
    ? cs.q_pompa * durata * numCampPunti
    : 0;

  // Isocinetismo %: rapporto tra volume campionato e volume teorico
  const iso_pct = v_teor > 0 && v_camp > 0 ? (v_camp / v_teor) * 100 : 0;

  // Portata effettiva media pompa (L/min)
  const q_eff = q_avg;

  // KPI display
  const setKPI = (id, val, unit, cls) => {
    const el = document.getElementById(id);
    el.textContent = val;
    el.className = 'ck-value ' + (cls || '');
  };

  if (iso_pct > 0) {
    const cls = iso_pct >= 95 && iso_pct <= 105 ? 'ok' : iso_pct >= 90 && iso_pct <= 110 ? 'warn' : 'bad';
    setKPI('ck-iso', iso_pct.toFixed(1) + '%', '', cls);
    setKPI('ck-vcamp', v_camp.toFixed(2), '', '');
    setKPI('ck-vteor', v_teor.toFixed(2), '', '');
    setKPI('ck-qeff', q_eff.toFixed(2), '', '');

    const bar = document.getElementById('iso-status-bar');
    bar.className = 'iso-status-bar ' + cls;
    document.getElementById('iso-pct-big').textContent = iso_pct.toFixed(1) + '%';
    document.getElementById('iso-icon').textContent = cls === 'ok' ? '✓' : cls === 'warn' ? '⚠' : '✕';
    if (cls === 'ok') {
      document.getElementById('iso-status-title').textContent = 'Campionamento CONFORME';
      document.getElementById('iso-status-sub').textContent = 'Isocinetismo entro range normativo 95–105% (ISO 16911-1)';
    } else if (cls === 'warn') {
      document.getElementById('iso-status-title').textContent = 'Campionamento ACCETTABILE con riserva';
      document.getElementById('iso-status-sub').textContent = 'Isocinetismo fuori range ottimale (95–105%) — verificare procedura';
    } else {
      document.getElementById('iso-status-title').textContent = 'Campionamento NON CONFORME';
      document.getElementById('iso-status-sub').textContent = 'Isocinetismo fuori range accettabile — campionamento da ripetere';
    }
  } else {
    ['ck-iso','ck-vcamp','ck-vteor','ck-qeff'].forEach(id => {
      document.getElementById(id).textContent = '—';
      document.getElementById(id).className = 'ck-value';
    });
    document.getElementById('iso-status-bar').className = 'iso-status-bar ok';
    document.getElementById('iso-pct-big').textContent = '—';
    document.getElementById('iso-status-title').textContent = 'In attesa dati';
    document.getElementById('iso-status-sub').textContent = 'Inserire volumi letto per punto per calcolare isocinetismo';
  }

  // Aggiorna stato globale campionamento
  calcState.iso_pct = iso_pct;
  calcState.v_camp  = v_camp;
  calcState.v_teor  = v_teor;
  calcState.q_eff   = q_eff;
  calcState.durata  = durata;
  calcState.d_u_camp = d_u;
}

// ═══════════════════════════════════════════════════════════
//  REPORT
// ═══════════════════════════════════════════════════════════
function buildReport() {
  const cs        = calcState;
  const comm      = document.getElementById('r_committente')?.value || '—';
  const imp       = document.getElementById('r_impianto')?.value    || '—';
  const data      = document.getElementById('r_data')?.value        || '—';
  const tec       = document.getElementById('r_tecnico')?.value     || '—';
  const note      = document.getElementById('r_note')?.value        || '—';

  const now = new Date().toLocaleString('it-IT');
  const prev = document.getElementById('report-preview');

  prev.innerHTML = `
<div class="rp-title">RAPPORTO DI CAMPIONAMENTO — EMISSIONI PRO v6</div>
<div class="rp-section">INTESTAZIONE</div>
<div class="rp-row"><span class="rp-key">Generato il:</span><span class="rp-val">${now}</span></div>
<div class="rp-row"><span class="rp-key">Committente:</span><span class="rp-val">${comm}</span></div>
<div class="rp-row"><span class="rp-key">Impianto / Camino:</span><span class="rp-val">${imp}</span></div>
<div class="rp-row"><span class="rp-key">Data campionamento:</span><span class="rp-val">${data}</span></div>
<div class="rp-row"><span class="rp-key">Tecnico campionatore:</span><span class="rp-val">${tec}</span></div>
<div class="rp-row"><span class="rp-key">Note operative:</span><span class="rp-val">${note}</span></div>

<div class="rp-section">GEOMETRIA & MISURA</div>
<div class="rp-row"><span class="rp-key">Diametro camino:</span><span class="rp-val">${cs.d_cam || '—'} m</span></div>
<div class="rp-row"><span class="rp-key">N° punti misura:</span><span class="rp-val">${numPunti}</span></div>
<div class="rp-row"><span class="rp-key">Costante Pitot (Kp):</span><span class="rp-val">${cs.k_pit || '—'}</span></div>
<div class="rp-row"><span class="rp-key">ΔP medio:</span><span class="rp-val">${cs.dp_avg > 0 ? cs.dp_avg.toFixed(2) + ' ' + currentUnit : '—'}</span></div>

<div class="rp-section">CONDIZIONI FUMI</div>
<div class="rp-row"><span class="rp-key">Temperatura fumi:</span><span class="rp-val">${cs.t_fumi || '—'} °C</span></div>
<div class="rp-row"><span class="rp-key">Temperatura ambiente:</span><span class="rp-val">${cs.t_amb || '—'} °C</span></div>
<div class="rp-row"><span class="rp-key">P. atmosferica:</span><span class="rp-val">${cs.p_atm || '—'} hPa</span></div>
<div class="rp-row"><span class="rp-key">P. assoluta fumi:</span><span class="rp-val">${cs.p_ass_hpa ? cs.p_ass_hpa.toFixed(2) : '—'} hPa</span></div>
<div class="rp-row"><span class="rp-key">H₂O:</span><span class="rp-val">${cs.h2o || '—'} %</span></div>
<div class="rp-row"><span class="rp-key">O₂ misurato:</span><span class="rp-val">${cs.o2_mis || '—'} %</span></div>
<div class="rp-row"><span class="rp-key">CO₂ misurato:</span><span class="rp-val">${cs.co2_mis || '—'} %</span></div>
<div class="rp-row"><span class="rp-key">O₂ riferimento:</span><span class="rp-val">${cs.o2_rif || '—'} %</span></div>
<div class="rp-row"><span class="rp-key">Densità fumi:</span><span class="rp-val">${cs.rho_fumi ? cs.rho_fumi.toFixed(4) : '—'} kg/m³</span></div>

<div class="rp-section">RISULTATI PORTATE</div>
<div class="rp-row"><span class="rp-key">Velocità media fumi:</span><span class="rp-val">${cs.v_fumi ? cs.v_fumi.toFixed(2) : '—'} m/s</span></div>
<div class="rp-row"><span class="rp-key">Q effettiva (camino):</span><span class="rp-val">${cs.q_aq ? cs.q_aq.toFixed(0) : '—'} Am³/h</span></div>
<div class="rp-row"><span class="rp-key">Q normale umida:</span><span class="rp-val">${cs.q_un_u ? cs.q_un_u.toFixed(0) : '—'} Nm³/h</span></div>
<div class="rp-row"><span class="rp-key">Q normale secca:</span><span class="rp-val">${cs.q_un_s ? cs.q_un_s.toFixed(0) : '—'} Nm³/h</span></div>
<div class="rp-row"><span class="rp-key">Q riferita O₂ (${cs.o2_rif}%):</span><span class="rp-val">${cs.q_rif ? cs.q_rif.toFixed(0) : '—'} Nm³/h</span></div>

<div class="rp-section">CAMPIONAMENTO ISOCINÉTICO</div>
<div class="rp-row"><span class="rp-key">Ø ugello campionamento:</span><span class="rp-val">${cs.d_u_camp || cs.d_ugello || '—'} mm</span></div>
<div class="rp-row"><span class="rp-key">Portata target pompa:</span><span class="rp-val">${cs.q_pompa ? cs.q_pompa.toFixed(2) : '—'} L/min</span></div>
<div class="rp-row"><span class="rp-key">Volume campionato totale:</span><span class="rp-val">${cs.v_camp ? cs.v_camp.toFixed(2) : '—'} L</span></div>
<div class="rp-row"><span class="rp-key">Volume teorico isocinético:</span><span class="rp-val">${cs.v_teor ? cs.v_teor.toFixed(2) : '—'} L</span></div>
<div class="rp-row"><span class="rp-key">Isocinetismo:</span><span class="rp-val" style="color:${
  !cs.iso_pct ? 'var(--text-muted)' :
  cs.iso_pct >= 95 && cs.iso_pct <= 105 ? 'var(--accent2)' :
  cs.iso_pct >= 90 && cs.iso_pct <= 110 ? 'var(--warn)' : 'var(--danger)'
}">${cs.iso_pct ? cs.iso_pct.toFixed(1) + '%' : '—'} ${
  cs.iso_pct >= 95 && cs.iso_pct <= 105 ? '✓ CONFORME' :
  cs.iso_pct >= 90 && cs.iso_pct <= 110 ? '⚠ ACCETTABILE' :
  cs.iso_pct > 0 ? '✕ NON CONFORME' : ''
}</span></div>

<div style="margin-top:20px;padding-top:14px;border-top:1px solid var(--border);font-size:9px;color:var(--text-muted);letter-spacing:1px;">
EMISSIONI PRO v6 · ISO 16911-1 · UNI EN 15259 · Generato: ${now}
</div>`;
}

// ═══════════════════════════════════════════════════════════
//  ESPORTAZIONE
// ═══════════════════════════════════════════════════════════
function getReportData() {
  return {
    meta: {
      committente: document.getElementById('r_committente')?.value || '',
      impianto: document.getElementById('r_impianto')?.value || '',
      data: document.getElementById('r_data')?.value || '',
      tecnico: document.getElementById('r_tecnico')?.value || '',
      note: document.getElementById('r_note')?.value || '',
      generato: new Date().toISOString()
    },
    dinamica: {
      d_cam: calcState.d_cam, k_pit: calcState.k_pit,
      t_fumi: calcState.t_fumi, t_amb: calcState.t_amb,
      p_atm: calcState.p_atm, p_ass_hpa: calcState.p_ass_hpa,
      h2o: calcState.h2o, o2_mis: calcState.o2_mis,
      co2_mis: calcState.co2_mis, o2_rif: calcState.o2_rif,
      rho_fumi: calcState.rho_fumi, dp_avg: calcState.dp_avg
    },
    risultati: {
      v_fumi: calcState.v_fumi, q_aq: calcState.q_aq,
      q_un_u: calcState.q_un_u, q_un_s: calcState.q_un_s, q_rif: calcState.q_rif
    },
    campionamento: {
      d_ugello: calcState.d_u_camp || calcState.d_ugello,
      q_pompa: calcState.q_pompa, v_camp: calcState.v_camp,
      v_teor: calcState.v_teor, iso_pct: calcState.iso_pct
    }
  };
}

function exportTXT() {
  const prev = document.getElementById('report-preview').innerText;
  download('emissioni_pro_report.txt', prev, 'text/plain');
  toast('Report TXT esportato', 'ok');
}

function exportCSV() {
  const d = getReportData();
  const rows = [
    ['Campo','Valore','Unità'],
    ['Committente', d.meta.committente, ''],
    ['Impianto', d.meta.impianto, ''],
    ['Data', d.meta.data, ''],
    ['Tecnico', d.meta.tecnico, ''],
    ['Ø Camino', d.dinamica.d_cam, 'm'],
    ['Kp Pitot', d.dinamica.k_pit, ''],
    ['T Fumi', d.dinamica.t_fumi, '°C'],
    ['T Amb', d.dinamica.t_amb, '°C'],
    ['P Atm', d.dinamica.p_atm, 'hPa'],
    ['P Ass', d.dinamica.p_ass_hpa, 'hPa'],
    ['H2O', d.dinamica.h2o, '%'],
    ['O2 mis', d.dinamica.o2_mis, '%'],
    ['CO2 mis', d.dinamica.co2_mis, '%'],
    ['O2 rif', d.dinamica.o2_rif, '%'],
    ['Densità fumi', d.dinamica.rho_fumi, 'kg/m³'],
    ['ΔP medio', d.dinamica.dp_avg, currentUnit],
    ['Velocità', d.risultati.v_fumi, 'm/s'],
    ['Q camino', d.risultati.q_aq, 'Am³/h'],
    ['Q norm umida', d.risultati.q_un_u, 'Nm³/h'],
    ['Q norm secca', d.risultati.q_un_s, 'Nm³/h'],
    ['Q riferita', d.risultati.q_rif, 'Nm³/h'],
    ['Q pompa target', d.campionamento.q_pompa, 'L/min'],
    ['V campionato', d.campionamento.v_camp, 'L'],
    ['V teorico iso', d.campionamento.v_teor, 'L'],
    ['Isocinetismo', d.campionamento.iso_pct, '%'],
  ];
  const csv = rows.map(r => r.map(c => `"${String(c||'').replace(/"/g,'""')}"`).join(';')).join('\r\n');
  download('emissioni_pro_dati.csv', csv, 'text/csv;charset=utf-8');
  toast('CSV esportato', 'ok');
}

function exportJSON() {
  const d = getReportData();
  download('emissioni_pro_dati.json', JSON.stringify(d, null, 2), 'application/json');
  toast('JSON esportato', 'ok');
}

function download(filename, content, mime) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([content], {type: mime}));
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

// ═══════════════════════════════════════════════════════════
//  SALVATAGGIO SESSIONE (localStorage)
// ═══════════════════════════════════════════════════════════
function raccogliInputs() {
  const ids = ['d_cam','k_pit','t_fumi','t_amb','p_atm','p_stat','h2o','o2_mis','co2_mis','o2_rif','d_ugello',
               'c_npunti','c_durata','c_ugello','c_t_cont','c_p_cont',
               'r_committente','r_impianto','r_data','r_tecnico','r_note'];
  const vals = {};
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) vals[id] = el.value;
  });
  // ΔP table
  vals._dp = [];
  for (let i = 0; i < numPunti; i++) {
    vals._dp.push({
      a: document.getElementById('dp_a' + i)?.value || '',
      b: document.getElementById('dp_b' + i)?.value || ''
    });
  }
  // Camp table
  vals._camp = [];
  for (let i = 0; i < numCampPunti; i++) {
    vals._camp.push({
      q: document.getElementById('c_q' + i)?.value || '',
      v: document.getElementById('c_v' + i)?.value || '',
      tf: document.getElementById('c_tf' + i)?.value || ''
    });
  }
  return vals;
}

function salvaSessione() {
  const comm = document.getElementById('r_committente')?.value || 'Sessione';
  const timestamp = new Date().toISOString();
  const key = 'ep_session_' + Date.now();
  const data = {
    key, timestamp, label: comm,
    unit: currentUnit,
    inputs: raccogliInputs(),
    calcState: { ...calcState }
  };
  localStorage.setItem(key, JSON.stringify(data));
  // Lista sessioni
  let list = JSON.parse(localStorage.getItem('ep_sessions') || '[]');
  list.push({ key, timestamp, label: comm });
  localStorage.setItem('ep_sessions', JSON.stringify(list));
  toast('✓ Sessione salvata: ' + comm, 'ok');
  aggiornaSessionInfo();
  renderSessionList();
}

function caricaSessione() {
  const list = JSON.parse(localStorage.getItem('ep_sessions') || '[]');
  if (list.length === 0) { toast('Nessuna sessione salvata', 'warn'); return; }
  // Prendi l'ultima
  const last = list[list.length - 1];
  loadSessionByKey(last.key);
}

function loadSessionByKey(key) {
  const raw = localStorage.getItem(key);
  if (!raw) { toast('Sessione non trovata', 'warn'); return; }
  const data = JSON.parse(raw);
  const inp = data.inputs || {};
  // Apri modulo emissioni
  document.getElementById('sidebar-emissioni').style.display = 'block';
  showPage('fumi');
  buildTable();
  // Ripristina valori
  const ids = Object.keys(inp).filter(k => !k.startsWith('_'));
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = inp[id];
  });
  calcola();
  // Ripristina ΔP (dopo buildTable)
  setTimeout(() => {
    if (inp._dp) {
      inp._dp.forEach((row, i) => {
        if (document.getElementById('dp_a' + i)) document.getElementById('dp_a' + i).value = row.a;
        if (document.getElementById('dp_b' + i)) document.getElementById('dp_b' + i).value = row.b;
      });
      calcola();
    }
    // Ripristina camp table
    if (inp._camp && inp._camp.length > 0) {
      buildCampTable();
      setTimeout(() => {
        inp._camp.forEach((row, i) => {
          if (document.getElementById('c_q' + i)) document.getElementById('c_q' + i).value = row.q;
          if (document.getElementById('c_v' + i)) document.getElementById('c_v' + i).value = row.v;
          if (document.getElementById('c_tf' + i)) document.getElementById('c_tf' + i).value = row.tf;
        });
        calcolaCamp();
      }, 50);
    }
    if (data.unit) setUnit(data.unit);
  }, 80);
  toast('✓ Sessione caricata: ' + data.label, 'ok');
  aggiornaSessionInfo();
}

function nuovaSessione() {
  if (!confirm('Azzerare tutti i dati?')) return;
  location.reload();
}

function aggiornaSessionInfo() {
  const list = JSON.parse(localStorage.getItem('ep_sessions') || '[]');
  const el = document.getElementById('session-info');
  if (list.length > 0) {
    const last = list[list.length-1];
    el.textContent = '💾 ' + last.label;
  }
}

function renderSessionList() {
  const list = JSON.parse(localStorage.getItem('ep_sessions') || '[]');
  const container = document.getElementById('sessions-list');
  if (!container) return;
  if (list.length === 0) {
    container.innerHTML = '<div style="color:var(--text-muted);font-family:var(--mono);font-size:11px;">Nessuna sessione salvata.</div>';
    return;
  }
  container.innerHTML = list.slice().reverse().map(s => `
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px;cursor:pointer;transition:border-color .15s;"
         onclick="loadSessionByKey('${s.key}')"
         onmouseover="this.style.borderColor='var(--accent)'"
         onmouseout="this.style.borderColor='var(--border)'">
      <div style="font-family:var(--mono);font-size:10px;color:var(--accent);margin-bottom:4px;">💾 SESSIONE</div>
      <div style="font-size:13px;font-weight:700;margin-bottom:4px;">${s.label}</div>
      <div style="font-family:var(--mono);font-size:9px;color:var(--text-muted);">${new Date(s.timestamp).toLocaleString('it-IT')}</div>
    </div>`).join('');
}

// ═══════════════════════════════════════════════════════════
//  TOAST
// ═══════════════════════════════════════════════════════════
function toast(msg, type) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'show ' + (type || '');
  clearTimeout(el._t);
  el._t = setTimeout(() => el.className = '', 2800);
}

// ═══════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  showPage('home');
  aggiornaSessionInfo();
  renderSessionList();
  // Imposta data odierna nel report
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('r_data').value = today;
});
</script>
</body>
</html>
