#!/usr/bin/env python3
"""
Generador de dashboard para reportes diarios de inteligencia de negocios.
v2 — umbral destacada >=15, pasos siempre visibles, SEGUIMIENTO renderizado.

USO: python3 build_dashboard.py
"""

import os, re, json, glob
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

SOURCES = [
    ("oportunidades", "Oportunidades de Negocio", os.path.join(BASE, "reportes")),
    ("inmobiliario",  "Marketing Inmobiliario",   os.path.join(BASE, "reportes-inmobiliario")),
]

DESTACADA_THRESHOLD = 15   # >=15 → banner + pasos destacados
HIGH_THRESHOLD      = 13   # >=13 → verde

# ---------------------------------------------------------------------------
# PARSING
# ---------------------------------------------------------------------------

def parse_date_from_name(path):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", os.path.basename(path))
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else os.path.basename(path)

def first_match(pattern, text, default="", flags=0):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else default

def extract_first_url(text):
    m = re.search(r"https?://[^\s\)\]\n\"'<>]+", text)
    return m.group(0).rstrip(".,);") if m else ""

def parse_seguimiento(text):
    """Extrae bloques SEGUIMIENTO DE CRECIMIENTO y devuelve lista de dicts."""
    blocks = []
    pattern = re.compile(
        r"###\s+SEGUIMIENTO DE CRECIMIENTO\s*[—–-]\s*(.+?)\n"
        r"\*Activado por:([^\n\*]+)\*"
        r"(.*?)(?=^###\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in pattern.finditer(text):
        subject    = m.group(1).strip()
        activation = m.group(2).strip()
        body       = m.group(3)

        def sect(label):
            m2 = re.search(
                rf"\*\*{label}[^:]*:\*\*\s*\n?(.*?)(?=\*\*[A-ZÁÉÍÓÚÑ]|\Z)",
                body, re.DOTALL,
            )
            return m2.group(1).strip() if m2 else ""

        timeline  = sect("Línea de tiempo")
        channels  = sect("Canales de marketing")
        podcasts  = sect(r"Apariciones en podcasts")
        palanca   = sect("Palanca clave")
        replicate = sect(r"Qué replicar")

        # Numbered items from "Qué replicar" block
        replicate_items = []
        if replicate:
            for line in replicate.splitlines():
                line = line.strip()
                if re.match(r"\d+\.", line):
                    replicate_items.append(re.sub(r"^\d+\.\s*", "", line))

        # Timeline items
        timeline_items = []
        if timeline:
            for line in timeline.splitlines():
                line = line.strip().lstrip("-").strip()
                if line:
                    timeline_items.append(line)

        blocks.append({
            "subject":         subject,
            "activation":      activation,
            "palanca":         palanca,
            "replicate_items": replicate_items,
            "timeline_items":  timeline_items,
            "channels":        channels,
        })
    return blocks


def parse_report(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    date    = parse_date_from_name(path)
    title   = first_match(r"^#\s+(.+)$", text, flags=re.MULTILINE).strip("# ")
    fuentes = first_match(r"\*\*Fuentes revisadas:\*\*\s*(.+)", text)
    resumen = first_match(r"\*\*Resumen[^:]*:\*\*\s*(.+)", text)

    opps = []
    opp_pattern = re.compile(
        r"^##\s+\d+\.\s+(.+?)\s+—\s+Score\s+(\d+)/20\s*$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in opp_pattern.finditer(text):
        name  = m.group(1).strip()
        score = int(m.group(2))
        body  = m.group(3)

        axes = first_match(r"\*\(([^)]+)\)\*", body)
        desc = first_match(
            r"\*\*(?:Modelo|Qué es|Descripcion|Descripción)[^:]*:\*\*\s*(.+)", body
        )
        why  = first_match(
            r"\*\*(?:Por qué funciona|Por qué genera leads|Porque funciona)[^:]*:\*\*\s*(.+)", body
        )
        conf = first_match(r"\*\*Confianza:\s*([^\*\n]+)", body).strip()
        chile = first_match(
            r"\*\*(?:En Chile|Oportunidad en Chile|Oportunidad Chile)[^:]*:\*\*\s*(.+)", body
        )

        # Link: intenta múltiples patrones según el formato del reporte
        link = ""
        link_patterns = [
            # "**Dónde lo encontré:**\n- https://..."
            r"\*\*(?:Dónde lo encontré|Donde lo encontré|Fuente|Fuentes|Link)[^:]*:\*\*\s*\n\s*[-\*]?\s*(https?://[^\s\)\n]+)",
            # "**Fuentes:**\n- https://..."  (primera URL de la lista)
            r"\*\*(?:Dónde lo encontré|Donde lo encontré|Fuente|Fuentes|Link)[^:]*:\*\*.*?(https?://[^\s\)\n]+)",
            # Primer URL de cualquier bullet "-  https://..."
            r"^\s*[-\*]\s+(https?://[^\s\)\n]+)",
            # Primer URL de un enlace Markdown "[texto](https://...)"
            r"\]\((https?://[^\s\)\n]+)\)",
        ]
        for pat in link_patterns:
            link = first_match(pat, body, flags=re.MULTILINE)
            if link:
                link = link.rstrip(".,);")
                break
        if not link:
            link = extract_first_url(body)

        # Pasos / Plan de acción / Pasos esta semana
        pasos = []
        step_block = re.search(
            r"\*\*(?:Pasos|Plan de acci[oó]n|Pasos esta semana)[^:]*:\*\*\s*\n"
            r"((?:\d+\..*(?:\n(?!\d+\.|###|\*\*|\n).*)*\n?)+)",
            body, re.MULTILINE,
        )
        if step_block:
            raw = step_block.group(1)
            # Reconstruye pasos: junta líneas de continuación al numbered item anterior
            current = ""
            for line in raw.splitlines():
                if re.match(r"\s*\d+\.", line):
                    if current:
                        pasos.append(re.sub(r"^\d+\.\s*", "", current).strip())
                    current = line.strip()
                elif line.strip() and current:
                    current += " " + line.strip()
            if current:
                pasos.append(re.sub(r"^\d+\.\s*", "", current).strip())

        has_follow = "SEGUIMIENTO DE CRECIMIENTO" in body
        opps.append({
            "name":      name,
            "score":     score,
            "axes":      axes,
            "desc":      desc,
            "why":       why,
            "conf":      conf,
            "chile":     chile,
            "link":      link,
            "pasos":     pasos,
            "follow":    has_follow,
            "seguimiento": None,   # se rellena más abajo
        })

    # Asigna bloques de seguimiento a oportunidades (por orden de aparición)
    seguimientos = parse_seguimiento(text)
    seg_idx = 0
    for opp in opps:
        if opp["follow"] and seg_idx < len(seguimientos):
            opp["seguimiento"] = seguimientos[seg_idx]
            seg_idx += 1

    follow_count = len(seguimientos)
    avg = round(sum(o["score"] for o in opps) / len(opps), 1) if opps else 0
    return {
        "date":         date,
        "title":        title,
        "fuentes":      fuentes,
        "resumen":      resumen,
        "opps":         opps,
        "n_opps":       len(opps),
        "avg":          avg,
        "follow_count": follow_count,
    }


def collect():
    data = []
    for key, label, folder in SOURCES:
        reports = []
        for path in sorted(glob.glob(os.path.join(folder, "*.md")), reverse=True):
            try:
                reports.append(parse_report(path))
            except Exception as e:
                print(f"  ! Error parseando {path}: {e}")
        data.append({"key": key, "label": label, "reports": reports})
    return data


# ---------------------------------------------------------------------------
# HTML TEMPLATE
# ---------------------------------------------------------------------------

TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>INTELIGENCIA DE NEGOCIOS — Chile</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#F5F0E8;--paper:#FFFDF7;--black:#0A0A0A;
  --red:#D4001A;--yellow:#FFE600;--green:#008A57;--blue:#0050EE;--orange:#E06000;
  --border:3px solid #0A0A0A;--shadow:5px 5px 0 #0A0A0A;--shadow-lg:8px 8px 0 #0A0A0A;
}
body{background:var(--bg);color:var(--black);font-family:"Courier New",Courier,monospace;min-height:100vh}

/* HEADER */
.header{background:var(--black);color:var(--yellow);padding:20px 32px;border-bottom:5px solid var(--yellow);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
.header h1{font-size:clamp(18px,4vw,28px);font-weight:900;letter-spacing:2px;text-transform:uppercase}
.header .stamp{font-size:11px;color:#aaa;text-transform:uppercase;letter-spacing:1px;margin-top:4px}
.badge-chile{background:var(--red);color:#fff;font-size:11px;font-weight:900;padding:4px 10px;border:2px solid var(--yellow);letter-spacing:2px}

/* STATS BAR */
.stats-bar{display:flex;flex-wrap:wrap;border-bottom:var(--border);background:var(--paper)}
.stat{flex:1;min-width:80px;padding:16px 20px;border-right:var(--border)}
.stat:last-child{border-right:none}
.stat .num{font-size:clamp(22px,3.5vw,38px);font-weight:900;line-height:1}
.stat .num.red{color:var(--red)}
.stat .num.green{color:var(--green)}
.stat .lbl{font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-top:4px;color:#666}

/* LEGEND */
.legend{display:flex;gap:16px;flex-wrap:wrap;padding:8px 32px;background:var(--black);border-bottom:var(--border);font-size:11px;color:#aaa;letter-spacing:.5px}
.legend span{display:flex;align-items:center;gap:6px}
.ldot{width:10px;height:10px;border:2px solid;flex-shrink:0}

/* TABS */
.tabs{display:flex;padding:16px 32px;border-bottom:var(--border);background:var(--bg);flex-wrap:wrap;gap:8px}
.tab{background:var(--paper);border:var(--border);color:var(--black);padding:8px 20px;cursor:pointer;font-family:"Courier New",monospace;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px;box-shadow:3px 3px 0 var(--black);transition:transform .1s,box-shadow .1s}
.tab:hover{transform:translate(-2px,-2px);box-shadow:5px 5px 0 var(--black)}
.tab.active{background:var(--yellow);transform:translate(-2px,-2px);box-shadow:5px 5px 0 var(--black)}

/* FILTERS */
.filters{padding:12px 32px;border-bottom:var(--border);background:var(--paper);display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.filters label{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#666;margin-right:4px}
.filter-btn{font-size:11px;padding:4px 12px;border:2px solid var(--black);background:var(--bg);cursor:pointer;font-family:"Courier New",monospace;font-weight:700;letter-spacing:1px;text-transform:uppercase}
.filter-btn.active{background:var(--black);color:var(--yellow)}

/* MAIN */
.main{padding:24px 32px;max-width:1200px;margin:0 auto}

/* REPORT CARD */
.report{border:var(--border);box-shadow:var(--shadow-lg);background:var(--paper);margin-bottom:24px}
.report-head{padding:14px 18px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:12px;border-bottom:var(--border);background:var(--black);color:var(--yellow)}
.report-head:hover{background:#111}
.report-date{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#aaa}
.report-cat{font-size:11px;font-weight:900;padding:2px 8px;border:1px solid var(--yellow);color:var(--yellow);letter-spacing:1px;text-transform:uppercase}
.report-resumen{font-size:12px;color:#ccc;margin-top:4px;max-width:700px;line-height:1.5}
.report-badges{display:flex;gap:8px;align-items:center;flex-shrink:0;flex-wrap:wrap}
.pill{font-size:11px;padding:4px 10px;border:2px solid var(--yellow);color:var(--yellow);font-weight:700;letter-spacing:1px;white-space:nowrap}
.chev{font-size:18px;color:var(--yellow);transition:.2s;font-weight:900}
.report.open .chev{transform:rotate(90deg)}
.report-body{display:none;padding:20px}
.report.open .report-body{display:block}
.fuentes{font-size:11px;color:#666;border-bottom:2px dashed var(--black);padding-bottom:12px;margin-bottom:20px;line-height:1.6}

/* OPP CARD */
.opp{border:var(--border);background:var(--paper);margin-bottom:14px}
.opp.destacada{border-color:var(--green);border-width:4px;box-shadow:6px 6px 0 var(--green)}
.opp.seguimiento{border-color:var(--orange);border-width:4px;box-shadow:6px 6px 0 var(--orange)}
.opp-banner{display:none;font-size:11px;font-weight:900;letter-spacing:3px;text-transform:uppercase;padding:5px 16px;text-align:center;border-bottom:3px solid var(--black)}
.opp.destacada .opp-banner{display:block;background:var(--green);color:#fff}
.opp.seguimiento .opp-banner{display:block;background:var(--orange);color:#fff}
.opp-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:12px 14px 10px;border-bottom:2px solid #ddd;cursor:pointer}
.opp-head:hover{background:#f7f3e6}
.opp-name{font-weight:900;font-size:15px;text-transform:uppercase;letter-spacing:.5px}
.opp-axes{font-size:11px;color:#777;margin-top:3px}
.score{font-weight:900;font-size:17px;padding:5px 12px;border:var(--border);white-space:nowrap;min-width:66px;text-align:center;line-height:1.2}
.score.destacada{background:var(--green);color:#fff;border-color:var(--green);font-size:20px}
.score.high{background:#e8f7ef;color:var(--green);border-color:var(--green)}
.score.mid{background:#fffbe6;color:#7a6000;border-color:#b89a00}
.score.low{background:#eee;color:#777;border-color:#bbb}
.opp-body{display:none;padding:14px}
.opp.open .opp-body{display:block}
.opp-desc{font-size:13px;line-height:1.7;margin-bottom:12px;color:#222}
.box{padding:10px 14px;font-size:12px;margin-bottom:10px;line-height:1.6;border-left:4px solid}
.box.why{background:#FFFBE8;border-color:var(--yellow)}
.box.chile{background:#fff0f0;border-color:var(--red)}
.box strong{display:block;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;opacity:.7}
.opp-foot{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:10px}
.conf{font-size:11px;padding:3px 10px;border:2px solid;font-weight:700;letter-spacing:1px;text-transform:uppercase}
.conf-alta{border-color:var(--green);color:var(--green)}
.conf-media{border-color:#cc8800;color:#cc8800}
.conf-baja{border-color:var(--red);color:var(--red)}
.tag-seg{font-size:11px;padding:3px 10px;background:var(--orange);color:#fff;font-weight:700;letter-spacing:1px}
.src-link{display:inline-block;font-size:11px;padding:4px 12px;background:var(--blue);color:#fff;text-decoration:none;font-weight:700;border:2px solid var(--black);letter-spacing:.5px;box-shadow:2px 2px 0 var(--black)}
.src-link:hover{transform:translate(-1px,-1px);box-shadow:3px 3px 0 var(--black)}

/* PASOS */
.pasos{background:var(--black);color:var(--yellow);padding:14px;margin-top:12px;border:2px solid var(--yellow)}
.pasos h4{font-size:11px;letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;border-bottom:1px solid #555;padding-bottom:6px;color:#fff}
.paso{display:flex;gap:10px;margin-bottom:9px;font-size:12px;line-height:1.6;color:#e8e8e8}
.paso-num{background:var(--yellow);color:var(--black);font-weight:900;min-width:22px;height:22px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px}

/* SEGUIMIENTO BLOCK */
.seg-block{border:3px solid var(--orange);background:#fff8f0;margin-top:12px}
.seg-head{background:var(--orange);color:#fff;padding:8px 14px;display:flex;justify-content:space-between;align-items:center;cursor:pointer}
.seg-head span{font-size:11px;font-weight:900;letter-spacing:2px;text-transform:uppercase}
.seg-body{display:none;padding:14px}
.seg-block.open .seg-body{display:block}
.palanca{background:var(--black);color:var(--yellow);padding:10px 14px;margin-bottom:12px;border-left:4px solid var(--yellow)}
.palanca strong{display:block;font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-bottom:5px;color:#aaa}
.palanca p{font-size:13px;line-height:1.6}
.replicate-title{font-size:11px;text-transform:uppercase;letter-spacing:2px;font-weight:900;margin-bottom:8px;color:#555}
.replicate-item{display:flex;gap:10px;margin-bottom:8px;font-size:12px;line-height:1.6}
.replicate-num{background:var(--orange);color:#fff;font-weight:900;min-width:22px;height:22px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px}
.timeline-title{font-size:11px;text-transform:uppercase;letter-spacing:2px;font-weight:900;margin-top:12px;margin-bottom:8px;color:#555}
.tl-item{display:flex;gap:8px;font-size:11px;margin-bottom:5px;line-height:1.5}
.tl-dot{width:8px;height:8px;background:var(--orange);border:2px solid var(--black);flex-shrink:0;margin-top:4px}

/* MISC */
.empty{font-size:13px;color:#aaa;padding:40px;text-align:center;text-transform:uppercase;letter-spacing:2px}
.footer{background:var(--black);color:#666;font-size:11px;padding:14px 32px;text-align:center;letter-spacing:1px;text-transform:uppercase;border-top:var(--border);margin-top:32px}
</style>
</head>
<body>

<div class="header">
  <div>
    <div style="display:flex;align-items:center;gap:12px">
      <h1>&#9889; Inteligencia de Negocios</h1>
      <span class="badge-chile">&#127464;&#127473; CHILE</span>
    </div>
    <div class="stamp">Ultima actualizacion: __UPDATED__ &middot; Agente Claude automatico</div>
  </div>
  <div style="text-align:right">
    <div style="font-size:26px;font-weight:900;color:#fff">__DATE_DISPLAY__</div>
    <div style="font-size:11px;color:#aaa;letter-spacing:1px">SCORE /20 &middot; PASOS ACCIONABLES</div>
  </div>
</div>

<div class="legend">
  <span><span class="ldot" style="background:#008A57;border-color:#008A57"></span>DESTACADA &ge;15 &mdash; pasos de acci&oacute;n incluidos</span>
  <span><span class="ldot" style="background:#e8f7ef;border-color:#008A57"></span>BUENA &ge;13</span>
  <span><span class="ldot" style="background:#fffbe6;border-color:#b89a00"></span>MEDIA 10&ndash;12</span>
  <span><span class="ldot" style="background:#eee;border-color:#bbb"></span>EXPLORAR &lt;10</span>
  <span style="margin-left:auto;color:#FFE600">&#9733; = Con seguimiento de crecimiento</span>
</div>

<div class="stats-bar" id="stats"></div>
<div class="tabs" id="tabs"></div>
<div class="filters">
  <label>Filtrar:</label>
  <button class="filter-btn active" onclick="setFilter('all')">TODAS</button>
  <button class="filter-btn" onclick="setFilter('destacada')">DESTACADAS &ge;15</button>
  <button class="filter-btn" onclick="setFilter('seguimiento')">CON SEGUIMIENTO</button>
  <button class="filter-btn" onclick="setFilter('alta')">CONFIANZA ALTA</button>
</div>
<div class="main" id="content"></div>
<div class="footer">Generado por agentes remotos Claude &middot; repo: maolivare-max/inteligencia-negocios &middot; <span id="count"></span></div>

<script>
const DATA = __DATA__;
const DT   = __DESTACADA__;
const HT   = __HIGH__;

function scoreClass(s){ return s>=DT?'destacada': s>=HT?'high': s>=10?'mid': 'low' }
function confClass(c){
  c=(c||'').toLowerCase();
  if(c.includes('alta')) return 'conf-alta';
  if(c.includes('baja')) return 'conf-baja';
  return 'conf-media';
}
function esc(s){ const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }

let activeTab='all', activeFilter='all';

function renderSeg(seg){
  if(!seg) return '';
  const items = seg.replicate_items||[];
  const tl    = seg.timeline_items||[];
  const itemsHtml = items.length ? `
    <div class="replicate-title">&#9889; Qu&eacute; replicar hoy</div>
    ${items.map((s,i)=>`<div class="replicate-item"><span class="replicate-num">${i+1}</span><span>${esc(s)}</span></div>`).join('')}
  ` : '';
  const tlHtml = tl.length ? `
    <div class="timeline-title">&#128336; Hitos documentados</div>
    ${tl.map(s=>`<div class="tl-item"><span class="tl-dot"></span><span>${esc(s)}</span></div>`).join('')}
  ` : '';
  return `
  <div class="seg-block" id="seg-${Math.random().toString(36).slice(2)}">
    <div class="seg-head" onclick="this.parentNode.classList.toggle('open')">
      <span>&#9733; SEGUIMIENTO DE CRECIMIENTO &mdash; ${esc(seg.subject)}</span>
      <span style="font-size:16px;font-weight:900">&#9658;</span>
    </div>
    <div class="seg-body">
      <div style="font-size:11px;color:#888;margin-bottom:10px;border-bottom:1px dashed #ccc;padding-bottom:8px">
        Activado por: ${esc(seg.activation)}
      </div>
      ${seg.palanca ? `<div class="palanca"><strong>&#128273; Palanca clave</strong><p>${esc(seg.palanca)}</p></div>` : ''}
      ${itemsHtml}
      ${tlHtml}
    </div>
  </div>`;
}

function renderOpp(o){
  const sc  = scoreClass(o.score);
  const hasSeg = !!o.seguimiento;
  const cardClass = hasSeg ? 'seguimiento' : (sc==='destacada' ? 'destacada' : '');
  const bannerText = hasSeg
    ? '&#9733; SEGUIMIENTO DE CRECIMIENTO ACTIVO &#9733;'
    : (sc==='destacada' ? '&#9733; IDEA DESTACADA &#9733;' : '');

  const pasos = o.pasos||[];
  const pasosHtml = pasos.length ? `
    <div class="pasos">
      <h4>&#9889; Plan de acci&oacute;n &mdash; pasos concretos</h4>
      ${pasos.map((s,i)=>`<div class="paso"><span class="paso-num">${i+1}</span><span>${esc(s)}</span></div>`).join('')}
    </div>` : '';

  const whyHtml  = o.why  ? `<div class="box why"><strong>Por qu&eacute; funciona</strong>${esc(o.why)}</div>` : '';
  const chileHtml= o.chile? `<div class="box chile"><strong>&#127464;&#127473; Oportunidad en Chile</strong>${esc(o.chile)}</div>` : '';
  const linkHtml = o.link ? `<a class="src-link" href="${esc(o.link)}" target="_blank" rel="noopener">&rarr; VER FUENTE</a>` : '';
  const segHtml  = renderSeg(o.seguimiento);

  return `
  <div class="opp ${cardClass}" data-score="${o.score}" data-follow="${hasSeg?1:0}" data-conf="${(o.conf||'').toLowerCase()}">
    ${bannerText ? `<div class="opp-banner">${bannerText}</div>` : ''}
    <div class="opp-head" onclick="this.parentNode.classList.toggle('open')">
      <div>
        <div class="opp-name">${esc(o.name)}</div>
        <div class="opp-axes">${esc(o.axes)}${hasSeg?' &nbsp;&#9733; seguimiento':''}</div>
      </div>
      <div class="score ${sc}">${o.score}/20</div>
    </div>
    <div class="opp-body">
      <div class="opp-desc">${esc(o.desc)}</div>
      ${whyHtml}${chileHtml}
      <div class="opp-foot">
        ${o.conf ? `<span class="conf ${confClass(o.conf)}">Confianza: ${esc(o.conf)}</span>` : ''}
        ${hasSeg ? '<span class="tag-seg">&#9733; En seguimiento</span>' : ''}
        ${linkHtml}
      </div>
      ${pasosHtml}
      ${segHtml}
    </div>
  </div>`;
}

function applyFilter(oppsHtml, opps){
  if(activeFilter==='all') return oppsHtml;
  return opps.map((o,i)=>{
    if(activeFilter==='destacada' && o.score < DT) return '';
    if(activeFilter==='seguimiento' && !o.seguimiento)  return '';
    if(activeFilter==='alta' && !(o.conf||'').toLowerCase().includes('alta')) return '';
    return oppsHtml[i];
  }).join('');
}

function render(){
  const allReports=[];
  DATA.forEach(g=>g.reports.forEach(r=>allReports.push({...r,group:g.key,glabel:g.label})));
  const shown = activeTab==='all' ? allReports : allReports.filter(r=>r.group===activeTab);

  const totalOpps    = shown.reduce((a,r)=>a+r.n_opps,0);
  const totalFollow  = shown.reduce((a,r)=>a+r.follow_count,0);
  const allScores    = []; shown.forEach(r=>r.opps.forEach(o=>allScores.push(o.score)));
  const avg          = allScores.length ? (allScores.reduce((a,b)=>a+b,0)/allScores.length).toFixed(1) : '–';
  const destacadas   = allScores.filter(s=>s>=DT).length;
  const latestDate   = shown.length ? shown.sort((a,b)=>b.date.localeCompare(a.date))[0].date : '–';

  document.getElementById('stats').innerHTML=`
    <div class="stat"><div class="num">${shown.length}</div><div class="lbl">Reportes</div></div>
    <div class="stat"><div class="num">${totalOpps}</div><div class="lbl">Ideas totales</div></div>
    <div class="stat"><div class="num green">${destacadas}</div><div class="lbl">Destacadas &ge;${DT}</div></div>
    <div class="stat"><div class="num">${avg}</div><div class="lbl">Score prom.</div></div>
    <div class="stat"><div class="num red">${totalFollow}</div><div class="lbl">Con seguimiento</div></div>
    <div class="stat"><div class="num" style="font-size:14px">${latestDate}</div><div class="lbl">Ultimo reporte</div></div>`;

  let tabs=`<div class="tab ${activeTab==='all'?'active':''}" onclick="setTab('all')">TODOS</div>`;
  DATA.forEach(g=>{
    tabs+=`<div class="tab ${activeTab===g.key?'active':''}" onclick="setTab('${esc(g.key)}')">${esc(g.label.toUpperCase())}</div>`;
  });
  document.getElementById('tabs').innerHTML=tabs;

  const byDate=[...shown].sort((a,b)=>b.date.localeCompare(a.date));
  let html = byDate.length ? '' : '<div class="empty">No hay reportes todavia.</div>';
  byDate.forEach((r,i)=>{
    const oppHtmls = r.opps.map(renderOpp);
    const filtered = applyFilter(oppHtmls, r.opps);
    const visible  = r.opps.filter(o=>{
      if(activeFilter==='destacada' && o.score < DT) return false;
      if(activeFilter==='seguimiento' && !o.seguimiento) return false;
      if(activeFilter==='alta' && !(o.conf||'').toLowerCase().includes('alta')) return false;
      return true;
    }).length;
    if(!filtered.trim()) return;
    html+=`
    <div class="report ${i===0?'open':''}">
      <div class="report-head" onclick="this.parentNode.classList.toggle('open')">
        <div style="flex:1">
          <div style="display:flex;gap:10px;align-items:center;margin-bottom:4px">
            <span class="report-date">${esc(r.date)}</span>
            <span class="report-cat">${esc(r.glabel)}</span>
          </div>
          <div class="report-resumen">${esc(r.resumen)}</div>
        </div>
        <div class="report-badges">
          <span class="pill">${visible} IDEAS</span>
          <span class="pill">PROM ${r.avg}</span>
          ${r.follow_count>0?`<span class="pill">&#9733; ${r.follow_count} SEGUIM.</span>`:''}
          <span class="chev">&#9658;</span>
        </div>
      </div>
      <div class="report-body">
        <div class="fuentes">FUENTES: ${esc(r.fuentes)}</div>
        ${filtered||'<div class="empty">Sin ideas que coincidan con el filtro.</div>'}
      </div>
    </div>`;
  });
  document.getElementById('content').innerHTML=html;
  document.getElementById('count').textContent=allReports.length+' reportes en archivo';

  // Sync filter buttons
  document.querySelectorAll('.filter-btn').forEach(btn=>{
    btn.classList.toggle('active', btn.getAttribute('onclick').includes(`'${activeFilter}'`));
  });
}

function setTab(t){ activeTab=t; render(); }
function setFilter(f){ activeFilter=f; render(); }
render();
</script>
</body>
</html>
"""


def main():
    data         = collect()
    updated      = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_display = datetime.now().strftime("%a %d %b").upper()
    out = (TEMPLATE
           .replace("__DATA__",            json.dumps(data, ensure_ascii=False))
           .replace("__UPDATED__",         updated)
           .replace("__DATE_DISPLAY__",    date_display)
           .replace("__DESTACADA__",       str(DESTACADA_THRESHOLD))
           .replace("__HIGH__",            str(HIGH_THRESHOLD)))
    for fname in ("dashboard.html", "index.html"):
        with open(os.path.join(BASE, fname), "w", encoding="utf-8") as f:
            f.write(out)

    n_rep  = sum(len(g["reports"]) for g in data)
    n_opp  = sum(r["n_opps"]       for g in data for r in g["reports"])
    n_dest = sum(1 for g in data for r in g["reports"] for o in r["opps"] if o["score"] >= DESTACADA_THRESHOLD)
    n_seg  = sum(r["follow_count"] for g in data for r in g["reports"])
    print(f"✓ dashboard.html + index.html generados:")
    print(f"  {n_rep} reportes · {n_opp} ideas · {n_dest} destacadas ≥{DESTACADA_THRESHOLD} · {n_seg} con seguimiento")


if __name__ == "__main__":
    main()
