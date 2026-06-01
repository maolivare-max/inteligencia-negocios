#!/usr/bin/env python3
"""
Generador de dashboard local para los reportes diarios.
Lee reportes/ (oportunidades) y reportes-inmobiliario/ (marketing inmobiliario),
parsea cada informe y produce un dashboard.html autocontenido (funciona offline).

USO: python3 build_dashboard.py
Se ejecuta automáticamente al final de cada flujo de generación de reportes.
"""
import os, re, json, glob, html
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCES = [
    ("oportunidades", "Oportunidades de Negocio", os.path.join(BASE, "reportes")),
    ("inmobiliario", "Marketing Inmobiliario", os.path.join(BASE, "reportes-inmobiliario")),
]

MESES = {"enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
         "julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,"diciembre":12}

def parse_date_from_name(path):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", os.path.basename(path))
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return os.path.basename(path)

def first_match(pattern, text, default=""):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else default

def parse_report(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    date = parse_date_from_name(path)
    title = first_match(r"^#\s+(.+)$", text).strip("# ")
    fuentes = first_match(r"\*\*Fuentes revisadas:\*\*\s*(.+)", text)
    resumen = first_match(r"\*\*Resumen[^:]*:\*\*\s*(.+)", text)

    opps = []
    # Cada oportunidad arranca con "## N. Nombre — Score X/20"
    pattern = re.compile(
        r"^##\s+\d+\.\s+(.+?)\s+—\s+Score\s+(\d+)/20\s*$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL)
    for m in pattern.finditer(text):
        name = m.group(1).strip()
        score = int(m.group(2))
        body = m.group(3)
        axes = first_match(r"\*\(([^)]+)\)\*", body)
        desc = first_match(r"\*\*(?:Modelo|Qué es)[^:]*:\*\*\s*(.+)", body)
        why = first_match(r"\*\*(?:Por qué funciona|Por qué genera leads)[^:]*:\*\*\s*(.+)", body)
        conf = first_match(r"\*\*Confianza:\s*([^\*]+)\*\*", body)
        has_follow = "SEGUIMIENTO DE CRECIMIENTO" in body
        opps.append({"name": name, "score": score, "axes": axes,
                     "desc": desc, "why": why, "conf": conf.strip(),
                     "follow": has_follow})
    # Bloques de seguimiento (pueden ir entre oportunidades)
    follow_count = len(re.findall(r"SEGUIMIENTO DE CRECIMIENTO", text))
    cierre = first_match(r"##\s+(?:TENDENCIAS DE FONDO|FORMA DE VENTA).*?\n+(?:\d+\.\s*)?\*\*?(.+?)\*\*?", text)
    avg = round(sum(o["score"] for o in opps)/len(opps), 1) if opps else 0
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

TEMPLATE = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard de Inteligencia</title>
<style>
:root{--bg:#0d1117;--card:#161b22;--card2:#1c2230;--border:#2d333b;--txt:#e6edf3;
--muted:#8b949e;--accent:#58a6ff;--green:#3fb950;--amber:#d29922;--grey:#6e7681;--red:#f85149;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.5;padding:24px;max-width:1100px;margin:0 auto}
h1{font-size:24px;margin-bottom:4px}
.sub{color:var(--muted);font-size:13px;margin-bottom:20px}
.stats{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px}
.stat{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 18px;flex:1;min-width:130px}
.stat .num{font-size:26px;font-weight:700;color:var(--accent)}
.stat .lbl{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.tabs{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap}
.tab{background:var(--card);border:1px solid var(--border);color:var(--txt);padding:8px 16px;border-radius:20px;cursor:pointer;font-size:14px;transition:.15s}
.tab:hover{border-color:var(--accent)}
.tab.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.report{background:var(--card);border:1px solid var(--border);border-radius:12px;margin-bottom:16px;overflow:hidden}
.report-head{padding:16px 20px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:12px}
.report-head:hover{background:var(--card2)}
.report-head .meta{flex:1}
.report-date{font-size:13px;color:var(--accent);font-weight:600}
.report-title{font-size:16px;font-weight:600;margin:2px 0}
.report-resumen{font-size:13px;color:var(--muted)}
.report-badges{display:flex;gap:8px;align-items:center;white-space:nowrap}
.pill{font-size:12px;padding:3px 9px;border-radius:12px;background:var(--card2);border:1px solid var(--border);color:var(--muted)}
.chev{color:var(--muted);transition:.2s}
.report.open .chev{transform:rotate(90deg)}
.report-body{display:none;padding:0 20px 16px}
.report.open .report-body{display:block}
.fuentes{font-size:12px;color:var(--muted);border-top:1px solid var(--border);padding:12px 0;margin-bottom:8px}
.opp{background:var(--card2);border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:10px}
.opp-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.opp-name{font-weight:600;font-size:15px}
.opp-axes{font-size:12px;color:var(--muted);margin-top:2px}
.score{font-weight:700;font-size:15px;padding:4px 10px;border-radius:8px;white-space:nowrap}
.score.high{background:rgba(63,185,80,.18);color:var(--green)}
.score.mid{background:rgba(210,153,34,.18);color:var(--amber)}
.score.low{background:rgba(110,118,129,.2);color:var(--grey)}
.opp-desc{font-size:13px;color:var(--txt);margin-top:8px}
.opp-foot{display:flex;gap:8px;margin-top:8px;align-items:center;flex-wrap:wrap}
.conf{font-size:11px;padding:2px 8px;border-radius:10px}
.conf-alta{background:rgba(63,185,80,.18);color:var(--green)}
.conf-media{background:rgba(210,153,34,.18);color:var(--amber)}
.conf-baja{background:rgba(248,81,73,.18);color:var(--red)}
.tag-follow{font-size:11px;padding:2px 8px;border-radius:10px;background:rgba(88,166,255,.18);color:var(--accent)}
.empty{color:var(--muted);text-align:center;padding:40px}
.footer{text-align:center;color:var(--muted);font-size:12px;margin-top:30px}
</style></head><body>
<h1>📊 Dashboard de Inteligencia</h1>
<div class="sub">Generado automáticamente · última actualización: __UPDATED__</div>
<div class="stats" id="stats"></div>
<div class="tabs" id="tabs"></div>
<div id="content"></div>
<div class="footer">Actualizado por el flujo de CLAUDE.md tras cada reporte · <span id="count"></span></div>
<script>
const DATA = __DATA__;
function scoreClass(s){return s>=15?'high':s>=12?'mid':'low'}
function confClass(c){c=(c||'').toLowerCase();if(c.includes('alta'))return 'conf-alta';if(c.includes('baja'))return 'conf-baja';return 'conf-media'}
function esc(s){const d=document.createElement('div');d.textContent=s||'';return d.innerHTML}
let active='all';
function render(){
  const allReports=[];DATA.forEach(g=>g.reports.forEach(r=>allReports.push({...r,group:g.key,glabel:g.label})));
  const shown=active==='all'?allReports:allReports.filter(r=>r.group===active);
  // stats
  const totalOpps=shown.reduce((a,r)=>a+r.n_opps,0);
  const totalFollow=shown.reduce((a,r)=>a+r.follow_count,0);
  const allScores=[];shown.forEach(r=>r.opps.forEach(o=>allScores.push(o.score)));
  const avg=allScores.length?(allScores.reduce((a,b)=>a+b,0)/allScores.length).toFixed(1):'–';
  document.getElementById('stats').innerHTML=
    stat(shown.length,'Reportes')+stat(totalOpps,'Oportunidades')+stat(avg,'Score promedio')+stat(totalFollow,'Seguimientos');
  // tabs
  let tabs=`<div class="tab ${active==='all'?'active':''}" onclick="setTab('all')">Todos</div>`;
  DATA.forEach(g=>{tabs+=`<div class="tab ${active===g.key?'active':''}" onclick="setTab('${g.key}')">${esc(g.label)}</div>`});
  document.getElementById('tabs').innerHTML=tabs;
  // content
  const byDate=[...shown].sort((a,b)=>b.date.localeCompare(a.date));
  let html=byDate.length?'':'<div class="empty">No hay reportes todavía.</div>';
  byDate.forEach((r,i)=>{
    const opps=r.opps.map(o=>`
      <div class="opp">
        <div class="opp-head">
          <div><div class="opp-name">${esc(o.name)}</div><div class="opp-axes">${esc(o.axes)}</div></div>
          <div class="score ${scoreClass(o.score)}">${o.score}/20</div>
        </div>
        <div class="opp-desc">${esc(o.desc)}</div>
        <div class="opp-foot">
          ${o.conf?`<span class="conf ${confClass(o.conf)}">Confianza: ${esc(o.conf)}</span>`:''}
          ${o.follow?'<span class="tag-follow">★ Seguimiento de crecimiento</span>':''}
        </div>
      </div>`).join('');
    html+=`
    <div class="report ${i===0?'open':''}">
      <div class="report-head" onclick="this.parentNode.classList.toggle('open')">
        <div class="meta">
          <div class="report-date">${esc(r.date)} · ${esc(r.glabel)}</div>
          <div class="report-title">${esc(r.title)}</div>
          <div class="report-resumen">${esc(r.resumen)}</div>
        </div>
        <div class="report-badges">
          <span class="pill">${r.n_opps} ideas</span>
          <span class="pill">prom ${r.avg}</span>
          <span class="chev">▶</span>
        </div>
      </div>
      <div class="report-body">
        <div class="fuentes">📚 ${esc(r.fuentes)}</div>
        ${opps||'<div class="empty">Sin oportunidades parseadas.</div>'}
      </div>
    </div>`;
  });
  document.getElementById('content').innerHTML=html;
  document.getElementById('count').textContent=allReports.length+' reportes totales en el archivo';
}
function stat(n,l){return `<div class="stat"><div class="num">${n}</div><div class="lbl">${l}</div></div>`}
function setTab(t){active=t;render()}
render();
</script></body></html>"""

def main():
    data = collect()
    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = (TEMPLATE
           .replace("__DATA__", json.dumps(data, ensure_ascii=False))
           .replace("__UPDATED__", updated))
    # Escribe dashboard.html y también index.html (para GitHub Pages).
    for fname in ("dashboard.html", "index.html"):
        with open(os.path.join(BASE, fname), "w", encoding="utf-8") as f:
            f.write(out)
    n_rep = sum(len(g["reports"]) for g in data)
    n_opp = sum(r["n_opps"] for g in data for r in g["reports"])
    print(f"✓ dashboard.html + index.html generados: {n_rep} reportes, {n_opp} oportunidades")

if __name__ == "__main__":
    main()
