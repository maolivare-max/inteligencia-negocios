#!/usr/bin/env python3
"""
Generador de dashboard brutalista para reportes diarios de inteligencia de negocios.
Lee reportes/ (oportunidades) y reportes-inmobiliario/ (marketing inmobiliario),
parsea cada informe y produce index.html + dashboard.html autocontenidos.

USO: python3 build_dashboard.py
Se ejecuta automaticamente al final de cada flujo de generacion de reportes.
"""

import os, re, json, glob
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

SOURCES = [
    ("oportunidades", "Oportunidades de Negocio", os.path.join(BASE, "reportes")),
    ("inmobiliario",  "Marketing Inmobiliario",   os.path.join(BASE, "reportes-inmobiliario")),
]

def parse_date_from_name(path):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", os.path.basename(path))
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else os.path.basename(path)

def first_match(pattern, text, default=""):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else default

def parse_report(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    date    = parse_date_from_name(path)
    title   = first_match(r"^#\s+(.+)$", text).strip("# ")
    fuentes = first_match(r"\*\*Fuentes revisadas:\*\*\s*(.+)", text)
    resumen = first_match(r"\*\*Resumen[^:]*:\*\*\s*(.+)", text)
    opps = []
    opp_pattern = re.compile(
        r"^##\s+\d+\.\s+(.+?)\s+—\s+Score\s+(\d+)/20\s*$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL)
    for m in opp_pattern.finditer(text):
        name  = m.group(1).strip()
        score = int(m.group(2))
        body  = m.group(3)
        axes  = first_match(r"\*\(([^)]+)\)\*", body)
        desc  = first_match(r"\*\*(?:Modelo|Qué es)[^:]*:\*\*\s*(.+)", body)
        why   = first_match(r"\*\*(?:Por qué funciona|Por qué genera leads)[^:]*:\*\*\s*(.+)", body)
        conf  = first_match(r"\*\*Confianza:\s*([^\*\n]+)", body).strip()
        chile = first_match(r"\*\*(?:En Chile|Oportunidad en Chile)[^:]*:\*\*\s*(.+)", body)
        link  = first_match(r"\*\*(?:Fuente|Link)[^:]*:\*\*\s*(https?://[^\s\)]+)", body)
        if not link:
            link = first_match(r"\((https?://[^\)]+)\)", body)
        pasos = []
        pasos_block = re.search(
            r"\*\*(?:Pasos|Plan de acci[oó]n)[^:]*:\*\*\s*\n((?:\d+\..+\n?)+)", body)
        if pasos_block:
            pasos = [re.sub(r"^\d+\.\s*", "", l).strip()
                     for l in pasos_block.group(1).strip().splitlines() if l.strip()]
        has_follow = "SEGUIMIENTO DE CRECIMIENTO" in body
        opps.append({"name": name, "score": score, "axes": axes,
                     "desc": desc, "why": why, "conf": conf,
                     "chile": chile, "link": link, "pasos": pasos,
                     "follow": has_follow})
    follow_count = len(re.findall(r"SEGUIMIENTO DE CRECIMIENTO", text))
    avg = round(sum(o["score"] for o in opps) / len(opps), 1) if opps else 0
    return {"date": date, "title": title, "fuentes": fuentes, "resumen": resumen,
            "opps": opps, "n_opps": len(opps), "avg": avg, "follow_count": follow_count}

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

# HTML TEMPLATE (brutalismo)

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
  --red:#E8001C;--yellow:#FFE600;--green:#00A86B;--blue:#0057FF;
  --border:3px solid #0A0A0A;--shadow:5px 5px 0 #0A0A0A;--shadow-lg:8px 8px 0 #0A0A0A;
}
body{background:var(--bg);color:var(--black);font-family:"Courier New",Courier,monospace;min-height:100vh}
.header{background:var(--black);color:var(--yellow);padding:20px 32px;border-bottom:5px solid var(--yellow);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
.header h1{font-size:clamp(18px,4vw,30px);font-weight:900;letter-spacing:2px;text-transform:uppercase}
.header .stamp{font-size:11px;color:#aaa;text-transform:uppercase;letter-spacing:1px;margin-top:4px}
.badge-chile{background:var(--red);color:#fff;font-size:11px;font-weight:900;padding:4px 10px;border:2px solid var(--yellow);letter-spacing:2px}
.stats-bar{display:flex;border-bottom:var(--border);background:var(--paper)}
.stat{flex:1;padding:20px 24px;border-right:var(--border);min-width:100px}
.stat:last-child{border-right:none}
.stat .num{font-size:clamp(24px,4vw,42px);font-weight:900;line-height:1}
.stat .num.red{color:var(--red)}
.stat .lbl{font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-top:4px;color:#555}
.legend{display:flex;gap:16px;flex-wrap:wrap;padding:10px 32px;background:var(--black);border-bottom:var(--border);font-size:11px;color:#aaa;letter-spacing:.5px}
.legend span{display:flex;align-items:center;gap:6px}
.dot{width:10px;height:10px;border:2px solid;flex-shrink:0}
.tabs{display:flex;padding:16px 32px;border-bottom:var(--border);background:var(--bg);flex-wrap:wrap;gap:8px}
.tab{background:var(--paper);border:var(--border);color:var(--black);padding:8px 20px;cursor:pointer;font-family:"Courier New",monospace;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px;box-shadow:3px 3px 0 var(--black);transition:transform .1s,box-shadow .1s}
.tab:hover{transform:translate(-2px,-2px);box-shadow:5px 5px 0 var(--black)}
.tab.active{background:var(--yellow);transform:translate(-2px,-2px);box-shadow:5px 5px 0 var(--black)}
.main{padding:24px 32px;max-width:1200px;margin:0 auto}
.report{border:var(--border);box-shadow:var(--shadow-lg);background:var(--paper);margin-bottom:24px}
.report-head{padding:16px 20px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:12px;border-bottom:var(--border);background:var(--black);color:var(--yellow)}
.report-head:hover{background:#111}
.report-date{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#aaa}
.report-cat{font-size:11px;font-weight:900;padding:2px 8px;border:1px solid var(--yellow);color:var(--yellow);letter-spacing:1px;text-transform:uppercase}
.report-resumen{font-size:12px;color:#ccc;margin-top:4px;max-width:700px}
.report-badges{display:flex;gap:8px;align-items:center;flex-shrink:0;flex-wrap:wrap}
.pill{font-size:11px;padding:4px 10px;border:2px solid var(--yellow);color:var(--yellow);font-weight:700;letter-spacing:1px;white-space:nowrap}
.chev{font-size:20px;color:var(--yellow);transition:.2s;font-weight:900}
.report.open .chev{transform:rotate(90deg)}
.report-body{display:none;padding:20px}
.report.open .report-body{display:block}
.fuentes{font-size:11px;color:#666;border-bottom:2px dashed var(--black);padding-bottom:12px;margin-bottom:20px}
.opp{border:var(--border);background:var(--paper);margin-bottom:16px}
.opp.elite{border-color:var(--red);border-width:4px;box-shadow:6px 6px 0 var(--red)}
.opp-banner{display:none;background:var(--red);color:#fff;font-size:11px;font-weight:900;letter-spacing:3px;text-transform:uppercase;padding:6px 16px;text-align:center;border-bottom:3px solid var(--black)}
.opp.elite .opp-banner{display:block}
.opp-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:14px 16px 10px;border-bottom:2px solid #ddd;cursor:pointer}
.opp-head:hover{background:#f9f5e8}
.opp-name{font-weight:900;font-size:16px;text-transform:uppercase;letter-spacing:.5px}
.opp-axes{font-size:11px;color:#777;margin-top:4px}
.score{font-weight:900;font-size:18px;padding:6px 14px;border:var(--border);white-space:nowrap;min-width:72px;text-align:center}
.score.elite{background:var(--red);color:#fff;border-color:var(--red);font-size:22px}
.score.high{background:var(--green);color:#fff;border-color:var(--green)}
.score.mid{background:var(--yellow);color:var(--black)}
.score.low{background:#ddd;color:#555}
.opp-body{display:none;padding:16px}
.opp.open .opp-body{display:block}
.opp-desc{font-size:13px;line-height:1.7;margin-bottom:12px}
.opp-why{background:#FFFBE8;border-left:4px solid var(--yellow);padding:10px 14px;font-size:12px;margin-bottom:12px;line-height:1.6}
.opp-why strong{display:block;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;color:#888}
.opp-foot{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.conf{font-size:11px;padding:3px 10px;border:2px solid;font-weight:700;letter-spacing:1px;text-transform:uppercase}
.conf-alta{border-color:var(--green);color:var(--green)}
.conf-media{border-color:#cc8800;color:#cc8800}
.conf-baja{border-color:var(--red);color:var(--red)}
.tag-follow{font-size:11px;padding:3px 10px;background:var(--black);color:var(--yellow);font-weight:700;letter-spacing:1px}
.action-plan{background:var(--black);color:var(--yellow);padding:16px;margin-top:12px;border:2px solid var(--yellow)}
.action-plan h4{font-size:12px;letter-spacing:3px;text-transform:uppercase;margin-bottom:12px;border-bottom:1px solid var(--yellow);padding-bottom:8px}
.action-step{display:flex;gap:12px;margin-bottom:10px;font-size:12px;line-height:1.6}
.step-num{background:var(--yellow);color:var(--black);font-weight:900;width:22px;height:22px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px}
.src-link{display:inline-block;font-size:11px;padding:4px 12px;background:var(--blue);color:#fff;text-decoration:none;font-weight:700;border:2px solid var(--black);letter-spacing:.5px;box-shadow:2px 2px 0 var(--black)}
.src-link:hover{transform:translate(-1px,-1px);box-shadow:3px 3px 0 var(--black)}
.empty{font-size:14px;color:#aaa;padding:40px;text-align:center;text-transform:uppercase;letter-spacing:2px}
.footer{background:var(--black);color:#666;font-size:11px;padding:16px 32px;text-align:center;letter-spacing:1px;text-transform:uppercase;border-top:var(--border);margin-top:32px}
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
    <div style="font-size:28px;font-weight:900;color:#fff">__DATE_DISPLAY__</div>
    <div style="font-size:11px;color:#aaa;letter-spacing:1px">IDEAS FILTRABLES &middot; SCORE /20</div>
  </div>
</div>
<div class="legend">
  <span><span class="dot" style="background:#E8001C;border-color:#E8001C"></span>ELITE &#8805;17 &mdash; pasos de accion incluidos</span>
  <span><span class="dot" style="background:#00A86B;border-color:#00A86B"></span>BUENA &#8805;15</span>
  <span><span class="dot" style="background:#FFE600;border-color:#aa9900"></span>MEDIA 12-14</span>
  <span><span class="dot" style="background:#ddd;border-color:#999"></span>EXPLORAR &lt;12</span>
  <span style="margin-left:auto;color:#FFE600">&#9733; = Seguimiento activo de crecimiento</span>
</div>
<div class="stats-bar" id="stats"></div>
<div class="tabs" id="tabs"></div>
<div class="main" id="content"></div>
<div class="footer">Generado por agentes remotos Claude &middot; repo: maolivare-max/inteligencia-negocios &middot; <span id="count"></span></div>
<script>
const DATA = __DATA__;
function scoreClass(s){return s>=17?'elite':s>=15?'high':s>=12?'mid':'low'}
function confClass(c){c=(c||'').toLowerCase();if(c.includes('alta'))return 'conf-alta';if(c.includes('baja'))return 'conf-baja';return 'conf-media'}
function esc(s){const d=document.createElement('div');d.textContent=s||'';return d.innerHTML}
let active='all';
function renderOpp(o){
  const sc=scoreClass(o.score);
  const isElite=sc==='elite';
  const steps=o.pasos&&o.pasos.length?o.pasos:[];
  const stepsHtml=isElite&&steps.length?`
    <div class="action-plan">
      <h4>&#9889; Plan de accion &mdash; como hacerlo en Chile</h4>
      ${steps.map((s,i)=>`<div class="action-step"><span class="step-num">${i+1}</span><span>${esc(s)}</span></div>`).join('')}
    </div>`:'';
  const chileHtml=o.chile?`<div class="opp-why"><strong>&#127464;&#127473; Oportunidad en Chile</strong>${esc(o.chile)}</div>`:'';
  const whyHtml=o.why?`<div class="opp-why"><strong>Por que funciona</strong>${esc(o.why)}</div>`:'';
  const linkHtml=o.link?`<a class="src-link" href="${esc(o.link)}" target="_blank" rel="noopener">&rarr; VER FUENTE</a>`:'';
  return `
  <div class="opp ${isElite?'elite':''}">
    ${isElite?'<div class="opp-banner">&#9733; IDEA ELITE &mdash; ACCIONABLE EN CHILE &#9733;</div>':''}
    <div class="opp-head" onclick="this.parentNode.classList.toggle('open')">
      <div>
        <div class="opp-name">${esc(o.name)}</div>
        <div class="opp-axes">${esc(o.axes)}</div>
      </div>
      <div class="score ${sc}">${o.score}/20</div>
    </div>
    <div class="opp-body">
      <div class="opp-desc">${esc(o.desc)}</div>
      ${whyHtml}${chileHtml}
      <div class="opp-foot">
        ${o.conf?`<span class="conf ${confClass(o.conf)}">Confianza: ${esc(o.conf)}</span>`:''}
        ${o.follow?'<span class="tag-follow">&#9733; Seguimiento activo</span>':''}
        ${linkHtml}
      </div>
      ${stepsHtml}
    </div>
  </div>`;
}
function render(){
  const allReports=[];DATA.forEach(g=>g.reports.forEach(r=>allReports.push({...r,group:g.key,glabel:g.label})));
  const shown=active==='all'?allReports:allReports.filter(r=>r.group===active);
  const totalOpps=shown.reduce((a,r)=>a+r.n_opps,0);
  const totalFollow=shown.reduce((a,r)=>a+r.follow_count,0);
  const allScores=[];shown.forEach(r=>r.opps.forEach(o=>allScores.push(o.score)));
  const avg=allScores.length?(allScores.reduce((a,b)=>a+b,0)/allScores.length).toFixed(1):'&ndash;';
  const eliteCount=allScores.filter(s=>s>=17).length;
  document.getElementById('stats').innerHTML=`
    <div class="stat"><div class="num">${shown.length}</div><div class="lbl">Reportes</div></div>
    <div class="stat"><div class="num">${totalOpps}</div><div class="lbl">Ideas totales</div></div>
    <div class="stat"><div class="num red">${eliteCount}</div><div class="lbl">Elite &ge;17pts</div></div>
    <div class="stat"><div class="num">${avg}</div><div class="lbl">Score prom.</div></div>
    <div class="stat"><div class="num">${totalFollow}</div><div class="lbl">En seguimiento</div></div>`;
  let tabs=`<div class="tab ${active==='all'?'active':''}" onclick="setTab('all')">TODOS</div>`;
  DATA.forEach(g=>{tabs+=`<div class="tab ${active===g.key?'active':''}" onclick="setTab('${esc(g.key)}')">${esc(g.label.toUpperCase())}</div>`});
  document.getElementById('tabs').innerHTML=tabs;
  const byDate=[...shown].sort((a,b)=>b.date.localeCompare(a.date));
  let html=byDate.length?'':'<div class="empty">No hay reportes todavia.</div>';
  byDate.forEach((r,i)=>{
    const opps=r.opps.map(renderOpp).join('');
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
          <span class="pill">${r.n_opps} IDEAS</span>
          <span class="pill">PROM ${r.avg}</span>
          <span class="chev">&#9658;</span>
        </div>
      </div>
      <div class="report-body">
        <div class="fuentes">FUENTES: ${esc(r.fuentes)}</div>
        ${opps||'<div class="empty">Sin oportunidades parseadas.</div>'}
      </div>
    </div>`;
  });
  document.getElementById('content').innerHTML=html;
  document.getElementById('count').textContent=allReports.length+' reportes en archivo';
}
function setTab(t){active=t;render()}
render();
</script>
</body>
</html>
"""

def main():
    data = collect()
    updated      = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_display = datetime.now().strftime("%a %d %b").upper()
    out = (TEMPLATE
           .replace("__DATA__",         json.dumps(data, ensure_ascii=False))
           .replace("__UPDATED__",      updated)
           .replace("__DATE_DISPLAY__", date_display))
    for fname in ("dashboard.html", "index.html"):
        with open(os.path.join(BASE, fname), "w", encoding="utf-8") as f:
            f.write(out)
    n_rep = sum(len(g["reports"]) for g in data)
    n_opp = sum(r["n_opps"] for g in data for r in g["reports"])
    elite = sum(1 for g in data for r in g["reports"] for o in r["opps"] if o["score"] >= 17)
    print(f"✓ dashboard.html + index.html generados: {n_rep} reportes, {n_opp} oportunidades ({elite} elite ≥17pts)")

if __name__ == "__main__":
    main()
