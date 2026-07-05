#!/usr/bin/env python3
"""
Generador de dashboard — v3.
Python pre-renderiza todo el HTML; JavaScript solo gestiona
colapsos y filtros. Sin dependencias externas.

USO: python3 build_dashboard.py
"""

import os, re, glob, html as _html
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

SOURCES = [
    ("oportunidades", "Oportunidades de Negocio",
     os.path.join(BASE, "reportes")),
    ("inmobiliario",  "Marketing Inmobiliario",
     os.path.join(BASE, "reportes-inmobiliario")),
]

DESTACADA = 15
HIGH      = 13

esc = _html.escape   # safe HTML escaping

# ── helpers ────────────────────────────────────────────────────────────────

def _re(pattern, text, default="", flags=0):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else default

def _first_url(text):
    m = re.search(r"https?://[^\s\)\]\n\"'<>]+", text)
    return m.group(0).rstrip(".,);>") if m else ""

def parse_date(path):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    return m.group(1) if m else os.path.basename(path)

# ── seguimiento block parser ────────────────────────────────────────────────

def _parse_seguimientos(text):
    blocks = []
    pat = re.compile(
        r"###\s+SEGUIMIENTO DE CRECIMIENTO\s*[—–-]\s*(.+?)\n"
        r"\*Activado por:([^\n\*]+)\*"
        r"(.*?)(?=^###|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in pat.finditer(text):
        subject    = m.group(1).strip()
        activation = m.group(2).strip()
        body       = m.group(3)

        def _sect(label):
            m2 = re.search(
                rf"\*\*{label}[^:]*:\*\*\s*\n?(.*?)(?=\*\*[A-ZÁÉÍÓÚÑ]|\Z)",
                body, re.DOTALL)
            return m2.group(1).strip() if m2 else ""

        palanca   = _sect("Palanca clave")
        replicate = _sect(r"Qué replicar")
        timeline  = _sect("Línea de tiempo")

        r_items = [re.sub(r"^\d+\.\s*", "", l).strip()
                   for l in replicate.splitlines()
                   if re.match(r"\s*\d+\.", l)]
        tl_items = [l.strip().lstrip("-").strip()
                    for l in timeline.splitlines() if l.strip()]

        blocks.append({
            "subject":    subject,
            "activation": activation,
            "palanca":    palanca,
            "r_items":    r_items,
            "tl_items":   tl_items,
        })
    return blocks

# ── opportunity parser ──────────────────────────────────────────────────────

def _parse_opps(text):
    opps = []
    pat  = re.compile(
        r"^##\s+\d+\.\s+(.+?)\s+—\s+Score\s+(\d+)/20\s*$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL)
    for m in pat.finditer(text):
        name  = m.group(1).strip()
        score = int(m.group(2))
        body  = m.group(3)

        axes  = _re(r"\*\(([^)]+)\)\*", body)
        desc  = _re(r"\*\*(?:Modelo|Qué es|Descripci[oó]n)[^:]*:\*\*\s*(.+)", body)
        why   = _re(r"\*\*(?:Por qué funciona|Por qué genera leads|Porque funciona)[^:]*:\*\*\s*(.+)", body)
        conf  = _re(r"\*\*Confianza:\*\*\s*([^\n]+)", body).strip()
        chile = _re(r"\*\*(?:En Chile|Oportunidad en Chile)[^:]*:\*\*\s*(.+)", body)

        # Link — try several field headings then first URL in bullets
        link = ""
        for pat2 in [
            r"\*\*(?:Dónde lo encontré|Donde lo encontré|Fuentes?|Link)[^:]*:\*\*\s*\n\s*[-\*]?\s*(https?://[^\s\)\n]+)",
            r"\*\*(?:Dónde lo encontré|Donde lo encontré|Fuentes?|Link)[^:]*:\*\*.*?(https?://[^\s\)\n]+)",
            r"^\s*[-\*]\s+(https?://[^\s\)\n]+)",
            r"\]\((https?://[^\s\)\n]+)\)",
        ]:
            link = _re(pat2, body, flags=re.MULTILINE)
            if link:
                link = link.rstrip(".,);")
                break
        if not link:
            link = _first_url(body)

        # Steps
        pasos = []
        sb = re.search(
            r"\*\*(?:Pasos|Plan de acci[oó]n|Pasos esta semana)[^:]*:\*\*\s*\n"
            r"((?:\d+\..*(?:\n(?!\d+\.|###|\*\*|\n).*)*\n?)+)",
            body, re.MULTILINE)
        if sb:
            cur = ""
            for line in sb.group(1).splitlines():
                if re.match(r"\s*\d+\.", line):
                    if cur:
                        pasos.append(re.sub(r"^\d+\.\s*", "", cur).strip())
                    cur = line.strip()
                elif line.strip() and cur:
                    cur += " " + line.strip()
            if cur:
                pasos.append(re.sub(r"^\d+\.\s*", "", cur).strip())

        has_follow = "SEGUIMIENTO DE CRECIMIENTO" in body
        opps.append({
            "name": name, "score": score, "axes": axes,
            "desc": desc, "why": why, "conf": conf,
            "chile": chile, "link": link, "pasos": pasos,
            "follow": has_follow, "seguimiento": None,
        })
    return opps

# ── report parser ───────────────────────────────────────────────────────────

def parse_report(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    date    = parse_date(path)
    fuentes = _re(r"\*\*Fuentes revisadas:\*\*\s*(.+)", text)
    resumen = _re(r"\*\*Resumen[^:]*:\*\*\s*(.+)", text)
    opps    = _parse_opps(text)
    segs    = _parse_seguimientos(text)
    # Assign seguimientos to opps in order
    si = 0
    for o in opps:
        if o["follow"] and si < len(segs):
            o["seguimiento"] = segs[si]; si += 1
    avg = round(sum(o["score"] for o in opps) / len(opps), 1) if opps else 0
    return {
        "date": date, "fuentes": fuentes, "resumen": resumen,
        "opps": opps, "n_opps": len(opps), "avg": avg,
        "follow_count": len(segs),
    }

def collect():
    result = []
    for key, label, folder in SOURCES:
        reports = []
        for path in sorted(glob.glob(os.path.join(folder, "*.md")), reverse=True):
            try:
                reports.append(parse_report(path))
            except Exception as e:
                print(f"  ! Error parseando {path}: {e}")
        result.append({"key": key, "label": label, "reports": reports})
    return result

# ── HTML rendering (pure Python) ────────────────────────────────────────────

def score_class(s):
    if s >= DESTACADA: return "destacada"
    if s >= HIGH:      return "high"
    if s >= 10:        return "mid"
    return "low"

def conf_class(c):
    c = (c or "").lower()
    if "alta" in c:  return "conf-alta"
    if "baja" in c:  return "conf-baja"
    return "conf-media"

def render_seguimiento(seg, uid):
    if not seg:
        return ""
    palanca_html = ""
    if seg["palanca"]:
        palanca_html = f"""
      <div class="palanca">
        <strong>&#128273; Palanca clave</strong>
        <p>{esc(seg['palanca'])}</p>
      </div>"""
    items_html = ""
    if seg["r_items"]:
        items_html = '<div class="replicate-title">&#9889; Qu&eacute; replicar hoy</div>'
        for i, s in enumerate(seg["r_items"], 1):
            items_html += f'<div class="replicate-item"><span class="r-num">{i}</span><span>{esc(s)}</span></div>'
    tl_html = ""
    if seg["tl_items"]:
        tl_html = '<div class="tl-title">&#128336; Hitos documentados</div>'
        for s in seg["tl_items"]:
            tl_html += f'<div class="tl-item"><span class="tl-dot"></span><span>{esc(s)}</span></div>'
    return f"""
  <div class="seg-block" id="seg-{uid}">
    <button class="seg-head" onclick="tog('seg-body-{uid}')" aria-expanded="false">
      <span>&#9733; SEGUIMIENTO &mdash; {esc(seg['subject'])}</span>
      <span class="seg-chev">&#9658;</span>
    </button>
    <div class="seg-body" id="seg-body-{uid}" hidden>
      <p class="seg-act">Activado por: {esc(seg['activation'])}</p>
      {palanca_html}{items_html}{tl_html}
    </div>
  </div>"""

def render_opp(opp, uid):
    sc       = score_class(opp["score"])
    has_seg  = opp["seguimiento"] is not None
    card_cls = "seguimiento" if has_seg else ("destacada" if sc == "destacada" else "")
    if has_seg:
        banner = '<div class="opp-banner seg-banner">&#9733; SEGUIMIENTO DE CRECIMIENTO ACTIVO &#9733;</div>'
    elif sc == "destacada":
        banner = '<div class="opp-banner dest-banner">&#9733; IDEA DESTACADA &#9733;</div>'
    else:
        banner = ""

    why_html = (f'<div class="box why"><strong>Por qu&eacute; funciona</strong>'
                f'{esc(opp["why"])}</div>') if opp.get("why") else ""
    chile_html = (f'<div class="box chile"><strong>&#127464;&#127473; Oportunidad en Chile</strong>'
                  f'{esc(opp["chile"])}</div>') if opp.get("chile") else ""

    link_html = ""
    if opp.get("link"):
        link_html = f'<a class="src-link" href="{esc(opp["link"])}" target="_blank" rel="noopener">&rarr; VER FUENTE</a>'

    steps_html = ""
    if opp.get("pasos"):
        rows = "".join(
            f'<div class="paso"><span class="paso-num">{i}</span><span>{esc(s)}</span></div>'
            for i, s in enumerate(opp["pasos"], 1)
        )
        steps_html = f'<div class="pasos"><h4>&#9889; Plan de acci&oacute;n</h4>{rows}</div>'

    seg_html = render_seguimiento(opp.get("seguimiento"), f"{uid}-seg")

    conf_tag = (f'<span class="conf {conf_class(opp["conf"])}">Confianza: {esc(opp["conf"])}</span>'
                if opp.get("conf") else "")
    seg_tag  = '<span class="tag-seg">&#9733; En seguimiento</span>' if has_seg else ""

    axes_extra = " &nbsp;&#9733; seguimiento" if has_seg else ""

    # data attributes for filter
    conf_val = (opp.get("conf") or "").lower()
    return f"""
<div class="opp {card_cls}"
     data-score="{opp['score']}"
     data-seg="{1 if has_seg else 0}"
     data-conf="{esc(conf_val)}">
  {banner}
  <button class="opp-head" onclick="tog('opp-{uid}')" aria-expanded="false">
    <div>
      <div class="opp-name">{esc(opp['name'])}</div>
      <div class="opp-axes">{esc(opp.get('axes',''))}{axes_extra}</div>
    </div>
    <div class="score {sc}">{opp['score']}/20</div>
  </button>
  <div class="opp-body" id="opp-{uid}" hidden>
    <p class="opp-desc">{esc(opp.get('desc',''))}</p>
    {why_html}{chile_html}
    <div class="opp-foot">{conf_tag}{seg_tag}{link_html}</div>
    {steps_html}{seg_html}
  </div>
</div>"""

def render_report(report, group_key, group_label, report_idx):
    uid_base   = f"{group_key}-{report['date']}"
    is_first   = (report_idx == 0)   # más reciente → abierto por defecto en el HTML
    opps_html  = "".join(
        render_opp(o, f"{uid_base}-{i}")
        for i, o in enumerate(report["opps"])
    )
    follow_pill = (f'<span class="pill">&#9733; {report["follow_count"]} SEGUIM.</span>'
                   if report["follow_count"] > 0 else "")
    # El primer reporte (más reciente) aparece abierto sin necesitar JavaScript
    body_hidden  = "" if is_first else " hidden"
    head_expanded = "true" if is_first else "false"
    chev_style   = 'style="transform:rotate(90deg)"' if is_first else ""
    return f"""
<div class="report" data-group="{esc(group_key)}" id="rep-{esc(uid_base)}">
  <button class="report-head" onclick="togRep('{esc(uid_base)}')" aria-expanded="{head_expanded}">
    <div style="flex:1">
      <div style="display:flex;gap:10px;align-items:center;margin-bottom:4px">
        <span class="report-date">{esc(report['date'])}</span>
        <span class="report-cat">{esc(group_label)}</span>
      </div>
      <div class="report-resumen">{esc(report.get('resumen',''))}</div>
    </div>
    <div class="report-badges">
      <span class="pill">{report['n_opps']} IDEAS</span>
      <span class="pill">PROM {report['avg']}</span>
      {follow_pill}
      <span class="chev" {chev_style}>&#9658;</span>
    </div>
  </button>
  <div class="report-body" id="rep-body-{esc(uid_base)}"{body_hidden}>
    <div class="fuentes">FUENTES: {esc(report.get('fuentes',''))}</div>
    {opps_html or '<div class="empty">Sin oportunidades parseadas.</div>'}
  </div>
</div>"""

# ── full page ────────────────────────────────────────────────────────────────

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#F5F0E8;--paper:#FFFDF7;--black:#0A0A0A;
  --red:#D4001A;--yellow:#FFE600;--green:#008A57;--blue:#0050EE;--orange:#C85000;
  --border:3px solid #0A0A0A;--shadow:5px 5px 0 #0A0A0A;
}
body{background:var(--bg);color:var(--black);font-family:"Courier New",Courier,monospace;min-height:100vh}
button{font-family:inherit;cursor:pointer;background:none;border:none;text-align:left;width:100%}

/* HEADER */
.header{background:var(--black);color:var(--yellow);padding:20px 28px;border-bottom:5px solid var(--yellow);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
.header h1{font-size:clamp(16px,3.5vw,26px);font-weight:900;letter-spacing:2px;text-transform:uppercase}
.stamp{font-size:11px;color:#aaa;text-transform:uppercase;letter-spacing:1px;margin-top:4px}
.badge-chile{background:var(--red);color:#fff;font-size:11px;font-weight:900;padding:4px 10px;border:2px solid var(--yellow);letter-spacing:2px}
.header-right{text-align:right}
.header-date{font-size:24px;font-weight:900;color:#fff}
.header-sub{font-size:11px;color:#aaa;letter-spacing:1px}

/* STATS */
.stats-bar{display:flex;flex-wrap:wrap;border-bottom:var(--border);background:var(--paper)}
.stat{flex:1;min-width:80px;padding:14px 18px;border-right:var(--border)}
.stat:last-child{border-right:none}
.stat .num{font-size:clamp(20px,3vw,36px);font-weight:900;line-height:1}
.stat .num.green{color:var(--green)} .stat .num.red{color:var(--red)}
.stat .lbl{font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-top:4px;color:#666}

/* LEGEND */
.legend{display:flex;gap:14px;flex-wrap:wrap;padding:8px 28px;background:var(--black);border-bottom:var(--border);font-size:11px;color:#aaa}
.legend span{display:flex;align-items:center;gap:5px}
.ldot{width:9px;height:9px;border:2px solid;flex-shrink:0}

/* CONTROLS */
.controls{display:flex;flex-wrap:wrap;gap:0;border-bottom:var(--border);background:var(--bg)}
.ctrl-group{display:flex;flex-wrap:wrap;gap:8px;padding:10px 28px;align-items:center;border-right:var(--border)}
.ctrl-group:last-child{border-right:none}
.ctrl-label{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#666;margin-right:2px}
.tab,.filter-btn{background:var(--paper);border:var(--border);color:var(--black);padding:6px 16px;font-family:inherit;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;box-shadow:3px 3px 0 var(--black);cursor:pointer;transition:transform .1s,box-shadow .1s}
.tab:hover,.filter-btn:hover{transform:translate(-1px,-1px);box-shadow:4px 4px 0 var(--black)}
.tab.active,.filter-btn.active{background:var(--yellow);transform:translate(-1px,-1px);box-shadow:4px 4px 0 var(--black)}

/* MAIN */
.main{padding:20px 28px;max-width:1200px;margin:0 auto}

/* REPORT */
.report{border:var(--border);box-shadow:var(--shadow);background:var(--paper);margin-bottom:20px}
.report[hidden]{display:none}
.report-head{padding:12px 16px;display:flex;justify-content:space-between;align-items:center;gap:12px;border-bottom:var(--border);background:var(--black);color:var(--yellow);width:100%}
.report-head:hover{background:#111}
.report-date{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#aaa}
.report-cat{font-size:11px;font-weight:900;padding:2px 8px;border:1px solid var(--yellow);color:var(--yellow);letter-spacing:1px;text-transform:uppercase}
.report-resumen{font-size:12px;color:#ccc;margin-top:4px;max-width:680px;line-height:1.5}
.report-badges{display:flex;gap:6px;align-items:center;flex-shrink:0;flex-wrap:wrap}
.pill{font-size:11px;padding:3px 9px;border:2px solid var(--yellow);color:var(--yellow);font-weight:700;letter-spacing:1px;white-space:nowrap}
.chev{font-size:16px;color:var(--yellow);transition:transform .2s;font-weight:900;display:inline-block}
.report-head[aria-expanded="true"] .chev{transform:rotate(90deg)}
.report-body{padding:18px}
.report-body[hidden]{display:none}
.fuentes{font-size:11px;color:#666;border-bottom:2px dashed #ccc;padding-bottom:10px;margin-bottom:18px;line-height:1.6}

/* OPP */
.opp{border:var(--border);background:var(--paper);margin-bottom:12px}
.opp[hidden]{display:none}
.opp.destacada{border-color:var(--green);border-width:4px;box-shadow:5px 5px 0 var(--green)}
.opp.seguimiento{border-color:var(--orange);border-width:4px;box-shadow:5px 5px 0 var(--orange)}
.opp-banner{font-size:10px;font-weight:900;letter-spacing:3px;text-transform:uppercase;padding:5px 14px;text-align:center;border-bottom:3px solid var(--black)}
.dest-banner{background:var(--green);color:#fff}
.seg-banner{background:var(--orange);color:#fff}
.opp-head{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;padding:10px 12px 8px;border-bottom:2px solid #ddd;width:100%}
.opp-head:hover{background:#f7f3e6}
.opp-name{font-weight:900;font-size:14px;text-transform:uppercase;letter-spacing:.5px}
.opp-axes{font-size:11px;color:#777;margin-top:3px}
.score{font-weight:900;font-size:16px;padding:5px 11px;border:var(--border);white-space:nowrap;min-width:62px;text-align:center;flex-shrink:0}
.score.destacada{background:var(--green);color:#fff;border-color:var(--green);font-size:19px}
.score.high{background:#e8f7ef;color:var(--green);border-color:var(--green)}
.score.mid{background:#fffbe6;color:#7a6000;border-color:#b89a00}
.score.low{background:#eee;color:#777;border-color:#bbb}
.opp-body{padding:14px}
.opp-body[hidden]{display:none}
.opp-desc{font-size:13px;line-height:1.7;margin-bottom:12px;color:#222}
.box{padding:9px 13px;font-size:12px;margin-bottom:9px;line-height:1.6;border-left:4px solid}
.box.why{background:#FFFBE8;border-color:var(--yellow)}
.box.chile{background:#fff0f0;border-color:var(--red)}
.box strong{display:block;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;opacity:.6}
.opp-foot{display:flex;gap:7px;align-items:center;flex-wrap:wrap;margin-top:8px;margin-bottom:2px}
.conf{font-size:11px;padding:3px 9px;border:2px solid;font-weight:700;letter-spacing:1px;text-transform:uppercase}
.conf-alta{border-color:var(--green);color:var(--green)}
.conf-media{border-color:#cc8800;color:#cc8800}
.conf-baja{border-color:var(--red);color:var(--red)}
.tag-seg{font-size:11px;padding:3px 9px;background:var(--orange);color:#fff;font-weight:700;letter-spacing:1px}
.src-link{display:inline-block;font-size:11px;padding:4px 11px;background:var(--blue);color:#fff;text-decoration:none;font-weight:700;border:2px solid var(--black);letter-spacing:.5px;box-shadow:2px 2px 0 var(--black)}
.src-link:hover{transform:translate(-1px,-1px);box-shadow:3px 3px 0 var(--black)}

/* PASOS */
.pasos{background:var(--black);color:var(--yellow);padding:12px;margin-top:12px;border:2px solid var(--yellow)}
.pasos h4{font-size:10px;letter-spacing:3px;text-transform:uppercase;margin-bottom:9px;border-bottom:1px solid #444;padding-bottom:5px;color:#fff}
.paso{display:flex;gap:9px;margin-bottom:8px;font-size:12px;line-height:1.6;color:#e8e8e8}
.paso-num{background:var(--yellow);color:var(--black);font-weight:900;min-width:21px;height:21px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px}

/* SEGUIMIENTO */
.seg-block{border:3px solid var(--orange);background:#fff8f0;margin-top:12px}
.seg-head{background:var(--orange);color:#fff;padding:7px 13px;display:flex;justify-content:space-between;align-items:center;width:100%}
.seg-head span:first-child{font-size:10px;font-weight:900;letter-spacing:2px;text-transform:uppercase}
.seg-chev{font-size:14px;font-weight:900;transition:transform .2s;display:inline-block}
.seg-head[aria-expanded="true"] .seg-chev{transform:rotate(90deg)}
.seg-body{padding:12px}
.seg-body[hidden]{display:none}
.seg-act{font-size:11px;color:#888;margin-bottom:10px;border-bottom:1px dashed #ccc;padding-bottom:8px}
.palanca{background:var(--black);color:var(--yellow);padding:9px 13px;margin-bottom:11px;border-left:4px solid var(--yellow)}
.palanca strong{display:block;font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;color:#aaa}
.palanca p{font-size:13px;line-height:1.6}
.replicate-title,.tl-title{font-size:10px;text-transform:uppercase;letter-spacing:2px;font-weight:900;margin-bottom:7px;color:#555}
.tl-title{margin-top:11px}
.replicate-item{display:flex;gap:9px;margin-bottom:7px;font-size:12px;line-height:1.6}
.r-num{background:var(--orange);color:#fff;font-weight:900;min-width:21px;height:21px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px}
.tl-item{display:flex;gap:7px;font-size:11px;margin-bottom:5px;line-height:1.5}
.tl-dot{width:7px;height:7px;background:var(--orange);border:2px solid var(--black);flex-shrink:0;margin-top:4px}

/* MISC */
.empty{font-size:13px;color:#aaa;padding:36px;text-align:center;text-transform:uppercase;letter-spacing:2px}
.footer{background:var(--black);color:#666;font-size:11px;padding:13px 28px;text-align:center;letter-spacing:1px;text-transform:uppercase;border-top:var(--border);margin-top:28px}
"""

JS = """
// Toggle any element by its explicit id; button must be its previousElementSibling
function tog(id) {
  var el = document.getElementById(id);
  if (!el) return;
  var btn = el.previousElementSibling;
  var isHidden = el.hasAttribute('hidden');
  if (isHidden) {
    el.removeAttribute('hidden');
    if (btn) btn.setAttribute('aria-expanded', 'true');
  } else {
    el.setAttribute('hidden', '');
    if (btn) btn.setAttribute('aria-expanded', 'false');
  }
}

function togRep(uid) {
  var body = document.getElementById('rep-body-' + uid);
  if (!body) return;
  var btn = document.querySelector('#rep-' + uid + ' .report-head');
  var isHidden = body.hasAttribute('hidden');
  if (isHidden) {
    body.removeAttribute('hidden');
    if (btn) btn.setAttribute('aria-expanded','true');
  } else {
    body.setAttribute('hidden','');
    if (btn) btn.setAttribute('aria-expanded','false');
  }
}

// Tabs
var activeTab = 'all';
function setTab(t) {
  activeTab = t;
  document.querySelectorAll('.tab').forEach(function(b) {
    b.classList.toggle('active', b.dataset.tab === t);
  });
  applyFilters();
}

// Filters
var activeFilter = 'all';
function setFilter(f) {
  activeFilter = f;
  document.querySelectorAll('.filter-btn').forEach(function(b) {
    b.classList.toggle('active', b.dataset.filter === f);
  });
  applyFilters();
}

function applyFilters() {
  var DEST = parseInt(document.body.dataset.dest || '15');
  document.querySelectorAll('.report').forEach(function(rep) {
    var grp = rep.dataset.group;
    if (activeTab !== 'all' && grp !== activeTab) {
      rep.setAttribute('hidden',''); return;
    }
    rep.removeAttribute('hidden');
    var visible = 0;
    rep.querySelectorAll('.opp').forEach(function(opp) {
      var score = parseInt(opp.dataset.score || '0');
      var seg   = opp.dataset.seg === '1';
      var conf  = opp.dataset.conf || '';
      var show  = true;
      if (activeFilter === 'destacada' && score < DEST) show = false;
      if (activeFilter === 'seguimiento' && !seg) show = false;
      if (activeFilter === 'alta' && !conf.includes('alta')) show = false;
      if (show) { opp.removeAttribute('hidden'); visible++; }
      else        opp.setAttribute('hidden','');
    });
  });
}

// Open most recent report on load
document.addEventListener('DOMContentLoaded', function() {
  var reports = document.querySelectorAll('.report');
  if (reports.length > 0) {
    var body = document.getElementById(reports[0].id.replace('rep-','rep-body-'));
    var btn  = reports[0].querySelector('.report-head');
    if (body) { body.removeAttribute('hidden'); }
    if (btn)  { btn.setAttribute('aria-expanded','true'); }
  }
  applyFilters();
});
"""

def build_page(data, updated, date_display):
    # Aggregate stats
    all_reports = [(r, g["key"], g["label"])
                   for g in data for r in g["reports"]]
    all_scores  = [o["score"] for r, _, _ in all_reports for o in r["opps"]]
    n_rep       = len(all_reports)
    n_opp       = sum(r["n_opps"] for r, _, _ in all_reports)
    n_dest      = sum(1 for s in all_scores if s >= DESTACADA)
    n_seg       = sum(r["follow_count"] for r, _, _ in all_reports)
    avg         = round(sum(all_scores) / len(all_scores), 1) if all_scores else "–"
    latest      = max((r["date"] for r, _, _ in all_reports), default="–")

    stats_html = f"""
<div class="stat"><div class="num">{n_rep}</div><div class="lbl">Reportes</div></div>
<div class="stat"><div class="num">{n_opp}</div><div class="lbl">Ideas totales</div></div>
<div class="stat"><div class="num green">{n_dest}</div><div class="lbl">Destacadas &ge;{DESTACADA}</div></div>
<div class="stat"><div class="num">{avg}</div><div class="lbl">Score prom.</div></div>
<div class="stat"><div class="num red">{n_seg}</div><div class="lbl">Con seguimiento</div></div>
<div class="stat"><div class="num" style="font-size:14px">{latest}</div><div class="lbl">&Uacute;ltimo reporte</div></div>"""

    tabs_html = '<span class="ctrl-label">Categor&iacute;a:</span>'
    tabs_html += '<button class="tab active" data-tab="all" onclick="setTab(\'all\')">TODAS</button>'
    for g in data:
        tabs_html += (f'<button class="tab" data-tab="{esc(g["key"])}" '
                      f'onclick="setTab(\'{esc(g["key"])}\')">'
                      f'{esc(g["label"].upper())}</button>')

    # Sort all reports newest first
    sorted_reports = sorted(all_reports, key=lambda x: x[0]["date"], reverse=True)
    reports_html = "".join(
        render_report(r, gk, gl, i)
        for i, (r, gk, gl) in enumerate(sorted_reports)
    ) or '<div class="empty">No hay reportes todav&iacute;a.</div>'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Inteligencia de Negocios &mdash; Chile</title>
<style>{CSS}</style>
</head>
<body data-dest="{DESTACADA}">

<div class="header">
  <div>
    <div style="display:flex;align-items:center;gap:12px">
      <h1>&#9889; Inteligencia de Negocios</h1>
      <span class="badge-chile">&#127464;&#127473; Chile</span>
    </div>
    <div class="stamp">Actualizado: {esc(updated)} &middot; Agente Claude</div>
  </div>
  <div class="header-right">
    <div class="header-date">{esc(date_display)}</div>
    <div class="header-sub">Score /20 &middot; Pasos accionables</div>
  </div>
</div>

<div class="legend">
  <span><span class="ldot" style="background:#008A57;border-color:#008A57"></span>Destacada &ge;{DESTACADA}</span>
  <span><span class="ldot" style="background:#e8f7ef;border-color:#008A57"></span>Buena &ge;{HIGH}</span>
  <span><span class="ldot" style="background:#fffbe6;border-color:#b89a00"></span>Media 10&ndash;12</span>
  <span><span class="ldot" style="background:#eee;border-color:#bbb"></span>Explorar &lt;10</span>
  <span style="margin-left:auto;color:#FFE600">&#9733; = Con seguimiento de crecimiento</span>
</div>

<div class="stats-bar">{stats_html}</div>

<div class="controls">
  <div class="ctrl-group">{tabs_html}</div>
  <div class="ctrl-group">
    <span class="ctrl-label">Filtro:</span>
    <button class="filter-btn active" data-filter="all"        onclick="setFilter('all')">TODAS</button>
    <button class="filter-btn"        data-filter="destacada"  onclick="setFilter('destacada')">DESTACADAS &ge;{DESTACADA}</button>
    <button class="filter-btn"        data-filter="seguimiento" onclick="setFilter('seguimiento')">CON SEGUIMIENTO</button>
    <button class="filter-btn"        data-filter="alta"       onclick="setFilter('alta')">CONFIANZA ALTA</button>
  </div>
</div>

<div class="main">{reports_html}</div>

<div class="footer">
  Generado por agentes remotos Claude &middot;
  repo: maolivare-max/inteligencia-negocios &middot;
  {n_rep} reportes &middot; {n_opp} ideas en archivo
</div>

<script>{JS}</script>
</body>
</html>"""

# ── main ────────────────────────────────────────────────────────────────────

def main():
    data         = collect()
    updated      = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_display = datetime.now().strftime("%a %d %b %Y").upper()
    page         = build_page(data, updated, date_display)

    for fname in ("dashboard.html", "index.html"):
        with open(os.path.join(BASE, fname), "w", encoding="utf-8") as f:
            f.write(page)

    n_rep  = sum(len(g["reports"]) for g in data)
    n_opp  = sum(r["n_opps"] for g in data for r in g["reports"])
    n_dest = sum(1 for g in data for r in g["reports"]
                 for o in r["opps"] if o["score"] >= DESTACADA)
    n_seg  = sum(r["follow_count"] for g in data for r in g["reports"])
    print(f"✓ dashboard generado (v3 pre-renderizado):")
    print(f"  {n_rep} reportes · {n_opp} ideas · {n_dest} destacadas ≥{DESTACADA} · {n_seg} con seguimiento")

if __name__ == "__main__":
    main()
