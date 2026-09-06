#!/usr/bin/env python3
"""
Generador de dashboard — v4.
Reescritura con la presentación de investigacion-tendencias-2026-07:
tabs (Panorama / Explorar / Decisiones / Reportes / Mi radar), buscador,
filtros por chip, tarjetas, modal de ficha completa y marcas persistentes
en localStorage (visto/favorito/nota). Sin dependencias externas.

Sigue leyendo las mismas fuentes que v3 (reportes/*.md y
reportes-inmobiliario/*.md, parseadas con regex) y cruza cada hallazgo
contra radar/indice-antirepeticion.txt para heredar veredicto_chile,
accion, nivel y prioridad ya decididos por las misiones diarias.

USO: python3 build_dashboard.py
"""

import os, re, glob, json, hashlib
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))

SOURCES = [
    ("oportunidades", "Oportunidades de negocio", os.path.join(BASE, "reportes")),
    ("tendencias",     "Tendencias inmobiliarias", os.path.join(BASE, "reportes-inmobiliario")),
    ("biohacking",     "Biohacking y longevidad", os.path.join(BASE, "reportes-biohacking")),
    ("publicidad",     "Publicidad Meta",         os.path.join(BASE, "reportes-publicidad")),
]

# el dominio usado en radar/indice-antirepeticion.txt para cada fuente
DOMINIO = {"oportunidades": "ideas", "tendencias": "tendencias", "biohacking": "biohacking",
           "publicidad": "publicidad"}

INDICE_PATH        = os.path.join(BASE, "radar", "indice-antirepeticion.txt")
IDEAS_INDEX_PATH    = os.path.join(BASE, "INDICE_IDEAS.md")

# ── MISIÓN 4 (Mesa de Proyectos) ────────────────────────────────────────────
# Pipeline PARALELO y deliberadamente separado del de hallazgos: un dossier de
# proyecto no es un hallazgo (no tiene score /20 ni veredicto Chile) y forzarlo
# al esquema de SOURCES/_parse_opps perdería contenido. Nada de lo de abajo
# toca SOURCES, DOMINIO, build_dataset() ni match_indice().
PROYECTOS_DIR = os.path.join(BASE, "proyectos")

# Las 7 secciones del contrato, en orden. Definido acá y reusado por
# validar_formato.py para que el contrato tenga una sola fuente de verdad.
PROYECTO_SECCIONES = [
    "Tesis y evidencia",
    "Plan de entrada",
    "Resumen financiero",
    "Timeline",
    "Plan de marketing",
    "Riesgos y señales de aborto",
    "Trazabilidad",
]
PROYECTO_META_CAMPOS = ["Estado", "Veredicto", "Fusión de", "Arranque", "Tesis"]

# ── MISIÓN 5 (Publicidad Meta): biblioteca de guiones ────────────────────────
# Pipeline PARALELO al de la Mesa de Proyectos y separado de él a propósito: un
# guion tampoco es un hallazgo (no lleva score /20 ni veredicto Chile), y no es
# un dossier (otros metadatos, otras secciones). Los informes semanales de
# reportes-publicidad/ SÍ entran por SOURCES como hallazgos normales.
# Estas constantes son la única fuente de verdad del contrato del guion y las
# reusa validar_formato.py, igual que PROYECTO_SECCIONES.
GUIONES_DIR = os.path.join(BASE, "publicidad", "guiones")
METRICAS_CONFIG_PATH = os.path.join(BASE, "publicidad", "metricas", "config.json")

GUION_SECCIONES = [
    "Anatomía del original",
    "Guion adaptable",
    "Variables a rellenar",
    "Targeting Chile",
    "Producción",
    "Medición",
    "Trazabilidad",
]
GUION_META_CAMPOS = ["Estado", "Tipo", "Origen", "Métrica de referencia", "Tesis"]


def es_guion_publicable(nombre_archivo):
    """El contrato nombra los guiones `NN-slug.md`. Todo lo demás que viva en la
    carpeta (README.md, _plantilla.md, notas) no es un guion: ni se publica ni
    se valida como tal. Reusado por validar_formato.py."""
    return (not nombre_archivo.startswith("_")
            and re.match(r"^\d+-.+\.md$", nombre_archivo) is not None)

DESTACADA = 15
HIGH      = 13

# ── helpers ──────────────────────────────────────────────────────────────

def _re(pattern, text, default="", flags=0):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else default

def parse_date(path):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    return m.group(1) if m else os.path.basename(path)

def slug(s, n=64):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:n]

# ── índice anti-repetición (veredicto_chile/accion/nivel/prioridad) ───────

def load_indice():
    """dominio -> lista de (nombre_truncado_lower, dict_campos), ya que el
    índice trunca el nombre a ~70 caracteres. Usamos coincidencia por
    prefijo (el nombre completo del hallazgo empieza igual)."""
    out = {"ideas": [], "tendencias": [], "biohacking": [], "publicidad": []}
    if not os.path.exists(INDICE_PATH):
        return out
    with open(INDICE_PATH, encoding="utf-8") as f:
        next(f, None)  # cabecera
        for line in f:
            parts = line.rstrip("\n").split("|")
            if len(parts) < 7:
                continue
            dominio, idx_id, nombre, veredicto, accion, nivel, prioridad = parts[:7]
            if dominio not in out:
                out[dominio] = []
            out[dominio].append({
                "id": idx_id,
                "nombre_lower": nombre.strip().lower(),
                "veredicto_chile": veredicto.strip(),
                "accion": accion.strip(),
                "nivel": nivel.strip().lstrip("Nn"),
                "prioridad": prioridad.strip().lstrip("Pp"),
            })
    return out

_STOP = set("""
de la el los las un una unos unas y o u a en con para por sobre del al
que se su sus como es son al mas más menos entre sin desde hasta ya no
via vs contra su tu mi este esta estos estas ese esa esos esas
""".split())

def _tokens(s):
    s = re.sub(r"[^a-záéíóúñü0-9%\s]", " ", s.lower())
    return set(w for w in s.split() if len(w) > 2 and w not in _STOP)

def match_indice(dominio_list, nombre, min_score=0.22):
    """El índice antirrepetición guarda una PARÁFRASIS del nombre (no el
    título literal del reporte), así que ni la coincidencia exacta ni el
    prefijo sirven. Usamos solapamiento de palabras clave (Jaccard sobre
    tokens con stopwords fuera) y nos quedamos con el mejor puntaje por
    encima de un umbral mínimo."""
    tn = _tokens(nombre)
    if not tn:
        return None
    best, best_score = None, 0.0
    for entry in dominio_list:
        en = entry["nombre_lower"]
        if not en:
            continue
        te = entry.get("_tokens")
        if te is None:
            te = _tokens(en)
            entry["_tokens"] = te
        if not te:
            continue
        inter = tn & te
        union = tn | te
        score = len(inter) / len(union) if union else 0
        if score > best_score:
            best, best_score = entry, score
    return best if best_score >= min_score else None

# ── parser de hallazgos dentro de un reporte diario ───────────────────────

def _parse_evidencia(body):
    """Extrae [texto](url) de la sección 'Dónde lo encontré' como lista de
    {fuente, url}."""
    m = re.search(r"\*\*(?:D[oó]nde lo encontr[eé])[^:]*:\*\*\s*(.+)", body)
    if not m:
        return []
    linea = m.group(1)
    out = []
    for texto, url in re.findall(r"\[([^\]]+)\]\((https?://[^\s\)]+)\)", linea):
        out.append({"fuente": texto.strip(), "url": url.strip().rstrip(".,);")})
    return out

def _parse_pasos(body):
    pasos, metrica = [], ""
    sb = re.search(
        r"\*\*(?:Pasos|Plan de acci[oó]n|Pasos esta semana)[^:]*:\*\*\s*\n"
        r"((?:\s*\d+\..*(?:\n(?!\s*\d+\.|###|\*\*|\n).*)*\n?)+)",
        body, re.MULTILINE)
    if sb:
        cur = ""
        for line in sb.group(1).splitlines():
            if re.match(r"\s*\d+\.", line):
                if cur:
                    pasos.append(re.sub(r"^\s*\d+\.\s*", "", cur).strip())
                cur = line.strip()
            elif line.strip() and cur:
                cur += " " + line.strip()
        if cur:
            pasos.append(re.sub(r"^\s*\d+\.\s*", "", cur).strip())
    for p in pasos:
        mm = re.search(r"(?:M[ée]trica[^:]*:|Medir a \d+ d[ií]as:)\s*(.+)", p, re.IGNORECASE)
        if mm:
            metrica = mm.group(1).strip()
    return pasos, metrica

def _parse_opps(text):
    opps = []
    pat = re.compile(
        r"^##\s+(?:\d+\.\s+)?([^\n]+?)\s+—\s+Score\s+(\d+)/20\s*$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL)
    for m in pat.finditer(text):
        name  = m.group(1).strip()
        score = int(m.group(2))
        body  = m.group(3)

        axes = _re(r"\*\(([^)]+)\)\*", body)
        desc = _re(r"\*\*(?:Modelo|Qu[ée] es|Descripci[oó]n)[^:]*:\*\*\s*(.+)", body)
        why  = _re(r"\*\*(?:Por qu[ée] funciona|Por qu[ée] genera leads|Por qu[ée] es relevante|Porque funciona)[^:]*:\*\*\s*(.+)", body)
        conf = _re(r"\*\*Confianza:\*\*\s*([^\n]+)", body).strip()
        chile = _re(r"\*\*(?:En Chile|Oportunidad en Chile|D[oó]nde funciona)[^:]*:\*\*\s*(.+)", body)

        evidencia = _parse_evidencia(body)
        pasos, metrica = _parse_pasos(body)
        has_follow = "SEGUIMIENTO" in body

        opps.append({
            "name": name, "score": score, "axes": axes,
            "desc": desc, "why": why, "conf": conf, "chile": chile,
            "evidencia": evidencia, "pasos": pasos, "metrica": metrica,
            "follow": has_follow,
        })
    return opps

def parse_report(path, group_key):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    date    = parse_date(path)
    fuentes = _re(r"\*\*Fuentes revisadas:\*\*\s*(.+)", text)
    resumen = _re(r"\*\*Resumen[^:]*:\*\*\s*(.+)", text)
    opps    = _parse_opps(text)
    return {"date": date, "fuentes": fuentes, "resumen": resumen,
            "opps": opps, "n_opps": len(opps),
            "avg": round(sum(o["score"] for o in opps) / len(opps), 1) if opps else 0}

def collect():
    result = []
    for key, label, folder in SOURCES:
        reports = []
        for path in sorted(glob.glob(os.path.join(folder, "*.md")), reverse=True):
            if os.path.basename(path).startswith("_"):
                continue  # misma convención que proyectos/ y guiones: _plantilla.md no es un reporte
            try:
                reports.append(parse_report(path, key))
            except Exception as e:
                print(f"  ! Error parseando {path}: {e}")
        result.append({"key": key, "label": label, "reports": reports})
    return result


# ── MISIÓN 4: parser de dossiers de proyecto ────────────────────────────────

def parse_proyecto(path):
    """Parsea un dossier de proyectos/. Devuelve dict, o lanza ValueError si el
    archivo no cumple el contrato (ver MISIÓN 4 en CLAUDE.md).

    A diferencia del parser de hallazgos, este NO degrada a vacío en silencio:
    un dossier mal formado es un error ruidoso. El corpus ya arrastra tres
    fallas silenciosas por esa razón (Confianza, evidencia, resumen)."""
    # utf-8-sig: un BOM invisible haría que la línea 1 sea "﻿# Título" y el
    # dossier se excluiría del dashboard por un carácter que nadie ve.
    # Normalizar CRLF evita \r residuales dentro del markdown de cada sección.
    with open(path, encoding="utf-8-sig") as f:
        txt = f.read().replace("\r\n", "\n")

    m = re.search(r"^#\s+(.+?)\s*$", txt, re.MULTILINE)
    if not m:
        raise ValueError("falta el título '# Nombre del proyecto'")
    titulo = m.group(1).strip()

    meta = {}
    for campo in PROYECTO_META_CAMPOS:
        mm = re.search(r"^>\s*\*\*" + re.escape(campo) + r":\*\*\s*(.+?)\s*$",
                       txt, re.MULTILINE)
        if not mm:
            raise ValueError(f"falta la línea de metadatos '> **{campo}:** ...'")
        meta[campo] = mm.group(1).strip()

    # Cada sección va desde su encabezado hasta el próximo '## ' o el fin.
    secciones, faltantes = {}, []
    for i, nombre in enumerate(PROYECTO_SECCIONES, start=1):
        pat = (r"^##\s+" + str(i) + r"\.\s+" + re.escape(nombre) +
               r"\s*$(.*?)(?=^##\s|\Z)")
        sm = re.search(pat, txt, re.MULTILINE | re.DOTALL)
        if not sm:
            faltantes.append(f"## {i}. {nombre}")
            continue
        secciones[nombre] = sm.group(1).strip()
    if faltantes:
        raise ValueError("faltan secciones: " + ", ".join(faltantes))

    # El nº correlativo sale del nombre de archivo (01-slug.md).
    base = os.path.basename(path)
    orden = int(base.split("-", 1)[0]) if base.split("-", 1)[0].isdigit() else 999

    return {
        "id": "proy-" + slug(base.rsplit(".", 1)[0]),
        "orden": orden,
        "archivo": base,
        "titulo": titulo,
        "estado": meta["Estado"],
        "veredicto": meta["Veredicto"],
        "fusion": meta["Fusión de"],
        "arranque": meta["Arranque"],
        "tesis": meta["Tesis"],
        "secciones": [{"nombre": n, "md": secciones[n]} for n in PROYECTO_SECCIONES],
    }


def collect_proyectos():
    if not os.path.isdir(PROYECTOS_DIR):
        return []
    out = []
    for path in sorted(glob.glob(os.path.join(PROYECTOS_DIR, "*.md"))):
        if os.path.basename(path).startswith("_"):
            continue  # convención: _plantilla.md y afines no se publican
        try:
            out.append(parse_proyecto(path))
        except Exception as e:
            print(f"  ! Dossier inválido, excluido: {path}: {e}")
    out.sort(key=lambda p: p["orden"])
    return out


# ── MISIÓN 5: parser de guiones y estado del módulo de cuenta propia ────────

def parse_guion(path):
    """Parsea un guion de publicidad/guiones/. Devuelve dict, o lanza ValueError
    si el archivo no cumple el contrato (ESPEC Misión 5: 5 líneas '>' y 7
    secciones '##' con nombres exactos). Misma filosofía que parse_proyecto():
    un guion mal formado es un error ruidoso, no un hueco silencioso."""
    with open(path, encoding="utf-8-sig") as f:
        txt = f.read().replace("\r\n", "\n")

    m = re.search(r"^#\s+(.+?)\s*$", txt, re.MULTILINE)
    if not m:
        raise ValueError("falta el título '# Nombre del guion'")
    titulo = m.group(1).strip()

    meta = {}
    for campo in GUION_META_CAMPOS:
        mm = re.search(r"^>\s*\*\*" + re.escape(campo) + r":\*\*\s*(.+?)\s*$",
                       txt, re.MULTILINE)
        if not mm:
            raise ValueError(f"falta la línea de metadatos '> **{campo}:** ...'")
        meta[campo] = mm.group(1).strip()

    secciones, faltantes = {}, []
    for i, nombre in enumerate(GUION_SECCIONES, start=1):
        pat = (r"^##\s+" + str(i) + r"\.\s+" + re.escape(nombre) +
               r"\s*$(.*?)(?=^##\s|\Z)")
        sm = re.search(pat, txt, re.MULTILINE | re.DOTALL)
        if not sm:
            faltantes.append(f"## {i}. {nombre}")
            continue
        secciones[nombre] = sm.group(1).strip()
    if faltantes:
        raise ValueError("faltan secciones: " + ", ".join(faltantes))

    base = os.path.basename(path)
    orden = int(base.split("-", 1)[0]) if base.split("-", 1)[0].isdigit() else 999

    return {
        "id": "guion-" + slug(base.rsplit(".", 1)[0]),
        "orden": orden,
        "archivo": base,
        "titulo": titulo,
        "estado": meta["Estado"],
        "tipo": meta["Tipo"],
        "origen": meta["Origen"],
        "metrica_ref": meta["Métrica de referencia"],
        "tesis": meta["Tesis"],
        "secciones": [{"nombre": n, "md": secciones[n]} for n in GUION_SECCIONES],
    }


def collect_guiones():
    if not os.path.isdir(GUIONES_DIR):
        return []  # carpeta ausente = biblioteca vacía, sin romper el build
    out = []
    for path in sorted(glob.glob(os.path.join(GUIONES_DIR, "*.md"))):
        if not es_guion_publicable(os.path.basename(path)):
            continue  # README.md, _plantilla.md y afines no son guiones
        try:
            out.append(parse_guion(path))
        except Exception as e:
            print(f"  ! Guion inválido, excluido: {path}: {e}")
    out.sort(key=lambda g: g["orden"])
    return out


def load_metricas_config():
    """Estado del módulo 'Métricas de mi cuenta Meta' (MISIÓN 5). Por diseño
    arranca APAGADO: si config.json no existe, no es JSON válido, no es un objeto
    o 'conectado' no es exactamente true, el dashboard muestra el estado apagado
    y ninguna cifra. Ni acá ni en el JS se inventan datos de ejemplo: lo único
    que se muestra son los escalares de primer nivel que el archivo declare."""
    cfg = {"conectado": False, "existe": False, "campos": {}}
    if not os.path.exists(METRICAS_CONFIG_PATH):
        return cfg
    try:
        with open(METRICAS_CONFIG_PATH, encoding="utf-8-sig") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"  ! publicidad/metricas/config.json ilegible, módulo tratado como apagado: {e}")
        return cfg
    if not isinstance(raw, dict):
        print("  ! publicidad/metricas/config.json no es un objeto JSON; módulo tratado como apagado")
        return cfg
    cfg["existe"] = True
    cfg["conectado"] = raw.get("conectado") is True
    cfg["campos"] = {k: v for k, v in raw.items()
                     if k != "conectado" and isinstance(v, (str, int, float, bool))}
    return cfg

# ── mapeo score → impacto/costo (heurístico, la mission no reporta estos
#    dos ejes por separado con nombres consistentes entre ambas misiones) ──

def conf_es_alta(conf):
    """True solo si la confianza declarada ES Alta, no si la palabra 'alta'
    aparece en alguna parte del texto.

    El campo se escribe como 'Alta (múltiples fuentes coinciden)' o
    'Media-Alta (cifras de un vendedor)': la confianza es la primera palabra y
    lo que sigue es la justificación. Un `"alta" in conf` marcaba las 86 fichas
    de 'Media-Alta' como verificadas y les quitaba el ⚠ del dashboard."""
    primera = re.split(r"[^a-záéíóúñ-]+", (conf or "").strip().lower(), maxsplit=1)
    return bool(primera) and primera[0] == "alta"


def score_tier(score):
    if score >= DESTACADA: return "destacada"
    if score >= HIGH:      return "alta"
    if score >= 10:        return "media"
    return "baja"

def impacto_de(score):
    return "alto" if score >= HIGH else ("medio" if score >= 10 else "bajo")

def costo_de(axes):
    """Busca un eje de costo/eficiencia o velocidad en el texto de ejes y
    usa su valor numérico (1-5) para inferir costo; si no hay pista,
    'medio' por defecto."""
    m = re.search(r"(?:Costo|Velocidad)[^\d]*(\d)", axes or "", re.IGNORECASE)
    if not m:
        return "medio"
    v = int(m.group(1))
    return "bajo" if v >= 4 else ("alto" if v <= 2 else "medio")

# ── construir el dataset unificado (una fila por hallazgo) ────────────────

def build_dataset(data, indice):
    rows = []
    for g in data:
        dominio = DOMINIO[g["key"]]
        idx_list = indice.get(dominio, [])
        for r in g["reports"]:
            for i, o in enumerate(r["opps"]):
                match = match_indice(idx_list, o["name"])
                _id = (match["id"] if match else slug(o["name"])) + "-" + r["date"]
                veredicto = match["veredicto_chile"] if match else ("APLICA" if o["score"] >= HIGH else "APLICA_CON_AJUSTES")
                accion = match["accion"] if match else (
                    "ADOPTAR_YA" if o["score"] >= DESTACADA else
                    "PILOTEAR" if o["score"] >= HIGH else
                    "OBSERVAR" if o["score"] >= 10 else "DESCARTAR")
                nivel = int(match["nivel"]) if (match and match["nivel"].isdigit()) else min(5, max(1, round(o["score"] / 4)))
                prioridad = int(match["prioridad"]) if (match and match["prioridad"].isdigit()) else None
                rows.append({
                    "id": _id,
                    "nombre": o["name"],
                    "categoria": g["key"],
                    "categoria_label": g["label"],
                    "fecha": r["date"],
                    "score": o["score"],
                    "score_tier": score_tier(o["score"]),
                    "descripcion": o["desc"] or o["why"] or "",
                    "razon": o["why"],
                    "adaptacion_chile": o["chile"],
                    "canal": o["axes"],
                    "evidencia": o["evidencia"],
                    "pasos": o["pasos"],
                    "metrica_exito": o["metrica"],
                    "confianza": o["conf"],
                    # OJO: no basta con buscar "alta" dentro del texto. 86 hallazgos
                    # dicen "Media-Alta (...)" y quedaban marcados como verificados,
                    # sin el ⚠ de "Confianza no alta" — el dashboard inflaba la
                    # confianza aparente justo donde el analista declaró una reserva.
                    # La confianza es la PRIMERA palabra; el resto es la justificación.
                    "verificado": conf_es_alta(o["conf"]),
                    "veredicto_chile": veredicto,
                    "accion": accion,
                    "nivel": nivel,
                    "prioridad": prioridad,
                    "impacto": impacto_de(o["score"]),
                    "costo_implementacion": costo_de(o["axes"]),
                    "seguimiento": o["follow"],
                    "fuente_reporte": f"{g['key']}/{r['date']}.md",
                })
    rows.sort(key=lambda x: (x["fecha"], -x["score"]), reverse=True)
    return rows

# ── plantilla HTML (estilo investigacion-tendencias-2026-07) ─────────────

TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Radar de Inteligencia de Negocios · Chile</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650&family=Archivo:wght@400;500;600;700&display=swap');
:root{
  --bg:#0d1117; --panel:#151b24; --panel2:#1b2330; --panel3:#212b3a; --line:#26303f;
  --txt:#e9e4d8; --muted:#8b95a7; --muted2:#5d6878;
  --oro:#d8a953; --oro2:#f2cd88; --oro-dim:rgba(216,169,83,.14);
  --verde:#46c08a; --verde-dim:rgba(70,192,138,.14);
  --ambar:#e3a93c; --ambar-dim:rgba(227,169,60,.13);
  --azul:#5d9bff; --azul-dim:rgba(93,155,255,.13);
  --gris:#7c8696; --gris-dim:rgba(124,134,150,.14);
  --rojo:#e0726a; --rojo-dim:rgba(224,114,106,.13);
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--txt);font-family:'Archivo',system-ui,sans-serif;font-size:15px;line-height:1.55;
  background-image:radial-gradient(1100px 500px at 85% -10%, rgba(216,169,83,.06), transparent 60%),radial-gradient(900px 480px at -10% 110%, rgba(93,155,255,.05), transparent 55%)}
h1,h2,h3,h4{font-family:'Fraunces',serif;font-weight:650;letter-spacing:.2px}
a{color:var(--oro2)}
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-thumb{background:#2b3648;border-radius:6px}
::-webkit-scrollbar-track{background:transparent}
.topbar{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:22px;flex-wrap:wrap;
  padding:14px 26px;background:rgba(13,17,23,.88);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:12px}
.logo{width:40px;height:40px;border-radius:11px;background:linear-gradient(140deg,var(--oro),#9c742f);display:flex;align-items:center;justify-content:center;font-size:20px;color:#14110a;font-weight:700;font-family:'Fraunces',serif}
.brand h1{font-size:19px;line-height:1.1}
.brand .sub{font-size:11.5px;color:var(--muted);letter-spacing:.4px}
.tabs{display:flex;gap:4px;flex-wrap:wrap}
.tab{background:none;border:1px solid transparent;color:var(--muted);font:inherit;font-weight:600;font-size:13.5px;
  padding:8px 14px;border-radius:9px;cursor:pointer;transition:.18s}
.tab:hover{color:var(--txt);background:var(--panel2)}
.tab.active{color:var(--oro2);background:var(--oro-dim);border-color:rgba(216,169,83,.35)}
.tab .pill{display:inline-block;min-width:20px;padding:0 6px;margin-left:5px;border-radius:99px;background:var(--panel3);font-size:11px;color:var(--muted)}
/* Enlace a una herramienta externa: mismo look que .tab pero fuera del switcher
   de pestañas (el JS captura .tab, así que esta clase NO puede llamarse .tab). */
.tabx{border:1px solid transparent;color:var(--muted);font:inherit;font-weight:600;font-size:13.5px;
  padding:8px 14px;border-radius:9px;cursor:pointer;transition:.18s;text-decoration:none}
.tabx:hover{color:var(--txt);background:var(--panel2)}
.progresswrap{margin-left:auto;display:flex;align-items:center;gap:10px}
.progresstxt{font-size:12.5px;color:var(--muted);white-space:nowrap}
.progresstxt b{color:var(--verde)}
.progressbar{width:130px;height:7px;border-radius:99px;background:var(--panel3);overflow:hidden}
.progressbar i{display:block;height:100%;width:0%;border-radius:99px;background:linear-gradient(90deg,var(--verde),#7ee0b2);transition:width .4s}
main{max-width:1500px;margin:0 auto;padding:24px 26px 80px}
.tabpane{display:none}
.tabpane.active{display:block}
.chip{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:600;letter-spacing:.5px;text-transform:uppercase;
  padding:3px 9px;border-radius:99px;border:1px solid var(--line);color:var(--muted);background:var(--panel2);white-space:nowrap}
.chip.acc-ADOPTAR_YA,.chip.acc-EMPEZAR_YA{color:var(--verde);background:var(--verde-dim);border-color:rgba(70,192,138,.4)}
.chip.acc-PILOTEAR,.chip.acc-PROTOTIPAR{color:var(--ambar);background:var(--ambar-dim);border-color:rgba(227,169,60,.4)}
.chip.acc-OBSERVAR{color:var(--azul);background:var(--azul-dim);border-color:rgba(93,155,255,.4)}
.chip.acc-DESCARTAR{color:var(--gris);background:var(--gris-dim);border-color:rgba(124,134,150,.4)}
.chip.ver-APLICA{color:var(--verde);background:var(--verde-dim);border-color:rgba(70,192,138,.4)}
.chip.ver-APLICA_CON_AJUSTES{color:var(--oro2);background:var(--oro-dim);border-color:rgba(216,169,83,.4)}
.chip.ver-NO_APLICA_AUN{color:var(--rojo);background:var(--rojo-dim);border-color:rgba(224,114,106,.4)}
.chip.cat-oportunidades{color:var(--azul);background:var(--azul-dim);border-color:rgba(93,155,255,.4)}
.chip.cat-tendencias{color:var(--oro2);background:var(--oro-dim);border-color:rgba(216,169,83,.4)}
.chip.cat-biohacking{color:var(--verde);background:var(--verde-dim);border-color:rgba(70,192,138,.4)}
.chip.cat-publicidad{color:var(--rojo);background:var(--rojo-dim);border-color:rgba(224,114,106,.4)}
.chip.tipo{color:var(--oro2);background:var(--oro-dim);border-color:rgba(216,169,83,.4)}
.prio{display:inline-flex;align-items:center;justify-content:center;min-width:30px;height:22px;padding:0 7px;border-radius:7px;
  font-size:11.5px;font-weight:700;letter-spacing:.5px}
.prio.p1{background:linear-gradient(135deg,var(--oro),#b07f2e);color:#181206}
.prio.p2{background:var(--oro-dim);color:var(--oro2);border:1px solid rgba(216,169,83,.45)}
.prio.p3,.prio.p4,.prio.p5{background:var(--panel3);color:var(--muted);border:1px solid var(--line)}
.prio.p0{background:transparent;color:var(--muted2);border:1px dashed var(--line)}
.explorar-wrap{display:grid;grid-template-columns:280px 1fr;gap:22px;align-items:start}
.filtros{position:sticky;top:86px;max-height:calc(100vh - 110px);overflow:auto;background:var(--panel);
  border:1px solid var(--line);border-radius:16px;padding:18px}
.filtros h3{font-size:14px;color:var(--oro2);margin-bottom:12px;display:flex;justify-content:space-between;align-items:center}
.filtros .reset{font-size:11.5px;color:var(--muted);background:none;border:none;cursor:pointer;text-decoration:underline;font-family:inherit}
.buscar{width:100%;padding:9px 12px;border-radius:10px;border:1px solid var(--line);background:var(--panel2);color:var(--txt);
  font:inherit;font-size:13.5px;margin-bottom:14px}
.buscar:focus{outline:none;border-color:var(--oro)}
.fgrupo{margin-bottom:14px}
.fgrupo .ftit{font-size:11px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);margin-bottom:7px}
.fops{display:flex;flex-wrap:wrap;gap:5px}
.fop{font:inherit;font-size:12px;font-weight:600;padding:4px 10px;border-radius:99px;border:1px solid var(--line);
  background:var(--panel2);color:var(--muted);cursor:pointer;transition:.15s}
.fop:hover{color:var(--txt);border-color:var(--muted2)}
.fop.on{color:var(--oro2);background:var(--oro-dim);border-color:rgba(216,169,83,.5)}
.fsel{width:100%;padding:7px 10px;border-radius:9px;border:1px solid var(--line);background:var(--panel2);color:var(--txt);font:inherit;font-size:13px}
.toggleverif{display:flex;align-items:center;gap:8px;font-size:12.5px;color:var(--muted);cursor:pointer;user-select:none}
.toggleverif input{accent-color:var(--oro)}
.res-header{display:flex;align-items:baseline;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.res-header h2{font-size:22px}
.res-header .n{color:var(--muted);font-size:13.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:16px 16px 13px;cursor:pointer;
  transition:transform .16s, border-color .16s, box-shadow .16s;position:relative;display:flex;flex-direction:column;gap:9px}
.card:hover{transform:translateY(-2px);border-color:rgba(216,169,83,.45);box-shadow:0 10px 28px rgba(0,0,0,.35)}
.card.vista{opacity:.5}
.card.vista:hover{opacity:.85}
.card .fila1{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.card .fila1 .sp{flex:1}
.card h3{font-size:15.5px;line-height:1.32;font-family:'Archivo',sans-serif;font-weight:700}
.card .desc{font-size:13px;color:var(--muted);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.card .meta{display:flex;gap:6px;flex-wrap:wrap;margin-top:auto;padding-top:4px}
.mark{background:none;border:1px solid var(--line);border-radius:8px;width:30px;height:26px;cursor:pointer;font-size:13px;
  color:var(--muted2);display:inline-flex;align-items:center;justify-content:center;transition:.15s}
.mark:hover{border-color:var(--muted)}
.mark.on-visto{color:var(--verde);border-color:rgba(70,192,138,.5);background:var(--verde-dim)}
.mark.on-fav{color:var(--oro2);border-color:rgba(216,169,83,.5);background:var(--oro-dim)}
.tag-vista{position:absolute;top:-8px;right:12px;font-size:10px;font-weight:700;letter-spacing:1px;color:var(--verde);
  background:#11221b;border:1px solid rgba(70,192,138,.5);border-radius:99px;padding:2px 9px}
.warn{color:var(--ambar);font-size:12px}
.vacio{padding:50px 20px;text-align:center;color:var(--muted);border:1px dashed var(--line);border-radius:16px}
.statgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:13px;margin-bottom:24px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:16px 18px}
.stat .v{font-family:'Fraunces',serif;font-size:31px;font-weight:650;line-height:1.05}
.stat .l{font-size:12px;color:var(--muted);margin-top:3px;letter-spacing:.3px}
.stat.gold .v{color:var(--oro2)} .stat.green .v{color:var(--verde)} .stat.amber .v{color:var(--ambar)} .stat.blue .v{color:var(--azul)} .stat.red .v{color:var(--rojo)}
.pan-cols{display:grid;grid-template-columns:1.25fr .75fr;gap:20px;align-items:start}
.panel-box{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:22px 24px;margin-bottom:20px}
.panel-box>h2{font-size:19px;color:var(--oro2);margin-bottom:14px}
.barrow{display:grid;grid-template-columns:150px 1fr 34px;align-items:center;gap:10px;margin-bottom:8px;font-size:12.5px}
.barrow .bl{color:var(--muted);text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.barrow .bt{height:9px;border-radius:99px;background:var(--panel3);overflow:hidden}
.barrow .bt i{display:block;height:100%;border-radius:99px}
.barrow .bn{color:var(--txt);font-weight:600;font-size:12px}
.hint{font-size:13px;color:var(--muted);border-left:3px solid var(--oro);padding:2px 0 2px 12px;margin-top:14px}
.dec-grupo{margin-bottom:26px}
.dec-grupo>header{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.dec-grupo>header h2{font-size:19px}
.dec-grupo>header .n{font-size:13px;color:var(--muted)}
.dec-grupo.g-ADOPTAR_YA>header h2,.dec-grupo.g-EMPEZAR_YA>header h2{color:var(--verde)}
.dec-grupo.g-PILOTEAR>header h2,.dec-grupo.g-PROTOTIPAR>header h2{color:var(--ambar)}
.dec-grupo.g-OBSERVAR>header h2{color:var(--azul)}
.dec-grupo.g-DESCARTAR>header h2{color:var(--gris)}
.dec-row{display:grid;grid-template-columns:minmax(220px,1.1fr) 1.6fr 150px 40px;gap:14px;align-items:center;
  background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:11px 16px;margin-bottom:7px;cursor:pointer;transition:.15s}
.dec-row:hover{border-color:rgba(216,169,83,.45)}
.dec-row.vista{opacity:.5}
.dec-row .nom{font-weight:700;font-size:13.5px;line-height:1.3}
.dec-row .imp{font-size:12.5px;color:var(--muted)}
.dec-row .pz{font-size:12px;color:var(--muted)}
.dec-row .pz b{display:block;color:var(--txt);font-size:12px;font-weight:600}
.acordeon{background:var(--panel);border:1px solid var(--line);border-radius:16px;margin-bottom:14px;overflow:hidden}
.acordeon summary{cursor:pointer;list-style:none;padding:16px 22px;display:flex;align-items:center;gap:12px;
  font-size:14px;font-weight:600;color:var(--oro2)}
.acordeon summary::-webkit-details-marker{display:none}
.acordeon summary .flecha{margin-left:auto;transition:.2s;color:var(--muted)}
.acordeon[open] summary .flecha{transform:rotate(90deg)}
.acordeon .cuerpo{padding:4px 24px 22px;border-top:1px solid var(--line)}
.acordeon .resumen{font-size:13px;color:#cfd6e0;margin:10px 0 14px}
.acordeon .fuentes{font-size:11.5px;color:var(--muted2);border-top:1px dashed var(--line);padding-top:10px;margin-top:6px}
.proy-intro{font-size:13px;color:var(--muted);max-width:760px;margin:-6px 0 18px;line-height:1.5}
.proy-meta{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 16px}
.proy-tesis{font-size:14px;color:#e6ecf3;line-height:1.55;border-left:3px solid var(--oro2);
  padding:2px 0 2px 14px;margin:4px 0 18px}
.proy-fusion{font-size:12px;color:var(--muted2);margin:0 0 16px;line-height:1.5}
.proy-sec{border-top:1px solid var(--line);padding-top:14px;margin-top:16px}
.proy-sec > h4{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--oro2);margin:0 0 10px}
.proy-md{font-size:13.5px;line-height:1.6;color:#cfd6e0}
.proy-md p{margin:0 0 10px}
.proy-md ul,.proy-md ol{margin:0 0 10px;padding-left:20px}
.proy-md li{margin-bottom:5px}
.proy-md h3{font-size:13.5px;color:#e6ecf3;margin:16px 0 8px}
.proy-md strong{color:#fff}
.proy-md code{background:var(--panel2);padding:1px 5px;border-radius:4px;font-size:12.5px}
.proy-md a{color:var(--oro2)}
.proy-md .tablawrap{overflow-x:auto;margin:0 0 12px}
.proy-md table{border-collapse:collapse;width:100%;font-size:12.5px;min-width:420px}
.proy-md th,.proy-md td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
.proy-md th{background:var(--panel2);color:var(--oro2);font-weight:600;white-space:nowrap}
.ver-construir{background:rgba(74,163,110,.16);border-color:rgba(74,163,110,.5);color:#7fd6a3}
.ver-pilotear{background:rgba(216,169,83,.16);border-color:rgba(216,169,83,.5);color:#e5c07b}
.ver-esperar{background:rgba(90,150,220,.16);border-color:rgba(90,150,220,.5);color:#8fbcf0}
.ver-descartar{background:rgba(200,90,90,.16);border-color:rgba(200,90,90,.5);color:#e08b8b}
.pub-estado{display:flex;gap:12px;align-items:flex-start;font-size:14px;color:#cfd6e0}
.pub-dot{flex:0 0 auto;width:10px;height:10px;border-radius:99px;margin-top:7px}
.pub-dot.on{background:var(--verde);box-shadow:0 0 0 4px var(--verde-dim)}
.pub-dot.off{background:var(--gris);box-shadow:0 0 0 4px var(--gris-dim)}
.pub-falta{font-size:12.5px;color:var(--muted);margin-top:5px}
.pub-kv{font-size:12.5px;color:var(--muted);line-height:1.45}
.pub-kv b{display:block;font-size:10.5px;letter-spacing:1px;text-transform:uppercase;color:var(--muted2)}
.mini-card{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin-bottom:9px;cursor:pointer}
.mini-card:hover{border-color:rgba(216,169,83,.4)}
.mini-card .t{font-weight:700;font-size:13.5px;margin-bottom:5px}
.radar-cols{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}
.lista-mini .item{display:flex;align-items:flex-start;gap:10px;padding:11px 14px;background:var(--panel2);border:1px solid var(--line);
  border-radius:11px;margin-bottom:7px;cursor:pointer;transition:.15s}
.lista-mini .item:hover{border-color:rgba(216,169,83,.45)}
.lista-mini .item .tt{font-weight:600;font-size:13.5px;line-height:1.3}
.lista-mini .item .nt{font-size:12px;color:var(--muted);margin-top:3px;font-style:italic}
.botonera{display:flex;gap:9px;flex-wrap:wrap;margin-top:14px}
.btn{font:inherit;font-size:13px;font-weight:600;padding:9px 16px;border-radius:10px;border:1px solid var(--line);
  background:var(--panel2);color:var(--txt);cursor:pointer;transition:.15s}
.btn:hover{border-color:var(--oro)}
.btn.peligro:hover{border-color:var(--rojo);color:var(--rojo)}
.overlay{position:fixed;inset:0;background:rgba(5,8,12,.72);backdrop-filter:blur(4px);z-index:100;display:none;align-items:flex-start;justify-content:center;padding:4vh 18px}
.overlay.abierto{display:flex}
.modal{background:var(--panel);border:1px solid #303c4e;border-radius:18px;max-width:900px;width:100%;max-height:90vh;overflow:auto;
  box-shadow:0 30px 80px rgba(0,0,0,.55)}
.modal-head{position:sticky;top:0;background:linear-gradient(180deg,var(--panel) 82%,transparent);padding:22px 26px 14px;z-index:2}
.modal-head .fila{display:flex;gap:7px;flex-wrap:wrap;align-items:center;margin-bottom:10px}
.modal-head h2{font-size:22px;line-height:1.25;padding-right:40px}
.cerrar{position:absolute;top:16px;right:16px;width:34px;height:34px;border-radius:10px;border:1px solid var(--line);
  background:var(--panel2);color:var(--muted);font-size:16px;cursor:pointer}
.cerrar:hover{color:var(--txt);border-color:var(--muted)}
.modal-cuerpo{padding:6px 26px 26px}
.msec{margin-bottom:20px}
.msec>h4{font-size:11.5px;letter-spacing:1.6px;text-transform:uppercase;color:var(--oro);margin-bottom:7px;font-family:'Archivo',sans-serif;font-weight:700}
.msec p,.msec li{font-size:14px;color:#cfd6e0}
.msec ul{margin-left:20px}
.msec li{margin:5px 0}
.kv{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:9px}
.kv .k{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:9px 12px}
.kv .k b{display:block;font-size:10.5px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);margin-bottom:3px}
.kv .k span{font-size:13px}
.notabox{width:100%;min-height:74px;background:var(--panel2);border:1px solid var(--line);border-radius:11px;color:var(--txt);
  font:inherit;font-size:13.5px;padding:11px 13px;resize:vertical}
.notabox:focus{outline:none;border-color:var(--oro)}
.modal-nav{display:flex;justify-content:space-between;align-items:center;padding:0 26px 22px;gap:10px}
.modal-nav .btn{flex:0 0 auto}
.guardado{font-size:11.5px;color:var(--verde);opacity:0;transition:.3s}
.guardado.ok{opacity:1}
@media (max-width:980px){
  .explorar-wrap{grid-template-columns:1fr}
  .filtros{position:static;max-height:none}
  .pan-cols{grid-template-columns:1fr}
  .radar-cols{grid-template-columns:1fr}
  .dec-row{grid-template-columns:1fr;gap:6px}
  .progresswrap{margin-left:0;width:100%}
  main{padding:18px 14px 70px}
  .topbar{padding:12px 14px}
}
</style>
</head>
<body>

<header class="topbar">
  <div class="brand">
    <div class="logo">◬</div>
    <div><h1>Radar de Inteligencia de Negocios</h1><span class="sub">__SUB__</span></div>
  </div>
  <nav class="tabs">
    <button class="tab active" data-tab="panorama">Panorama</button>
    <button class="tab" data-tab="explorar">Explorar <span class="pill" id="pillExplorar"></span></button>
    <button class="tab" data-tab="decisiones">Decisiones</button>
    <button class="tab" data-tab="proyectos">Proyectos <span class="pill" id="pillProy"></span></button>
    <button class="tab" data-tab="publicidad">Publicidad <span class="pill" id="pillPub"></span></button>
    <button class="tab" data-tab="reportes">Reportes</button>
    <button class="tab" data-tab="miradar">Mi radar <span class="pill" id="pillFav"></span></button>
    <a class="tabx" href="cubicaje/" title="Cubicador de madera masiva HILAM (parámetros Arauco)">Cubicador madera ↗</a>
  </nav>
  <div class="progresswrap">
    <span class="progresstxt"><b id="vistasNum">0</b> / <span id="totalNum"></span> vistas</span>
    <div class="progressbar"><i id="progressFill"></i></div>
  </div>
</header>

<main>

<section class="tabpane active" id="tab-panorama">
  <div class="statgrid" id="statgrid"></div>
  <div class="pan-cols">
    <div>
      <div class="panel-box">
        <h2>Últimos resúmenes ejecutivos</h2>
        <div id="resumenes"></div>
        <p class="hint">Haz clic en cualquier hallazgo para ver su ficha completa. Marca con 👁 lo que ya revisaste y con ⭐ lo que te interesa: queda guardado en este navegador y puedes verlo en «Mi radar».</p>
      </div>
    </div>
    <div>
      <div class="panel-box"><h2>Por decisión</h2><div id="chartAccion"></div></div>
      <div class="panel-box"><h2>Por veredicto Chile</h2><div id="chartVeredicto"></div></div>
      <div class="panel-box"><h2>Por misión</h2><div id="chartCat"></div></div>
    </div>
  </div>
</section>

<section class="tabpane" id="tab-explorar">
  <div class="explorar-wrap">
    <aside class="filtros">
      <h3>Filtros <button class="reset" id="btnReset">limpiar</button></h3>
      <input class="buscar" id="buscar" type="search" placeholder="Buscar… (nombre, descripción, canal)">
      <div id="gruposFiltro"></div>
      <div class="fgrupo">
        <div class="ftit">Ordenar por</div>
        <select class="fsel" id="orden">
          <option value="fecha">Fecha (recientes primero)</option>
          <option value="prioridad">Prioridad (P1 primero)</option>
          <option value="score">Score (mayor primero)</option>
          <option value="nombre">Nombre A→Z</option>
        </select>
      </div>
      <label class="toggleverif"><input type="checkbox" id="soloVerif"> Solo confianza alta</label>
    </aside>
    <div>
      <div class="res-header"><h2>Hallazgos</h2><span class="n" id="resN"></span></div>
      <div class="grid" id="grid"></div>
    </div>
  </div>
</section>

<section class="tabpane" id="tab-decisiones">
  <div class="res-header"><h2>Matriz de decisión</h2><span class="n">qué hacer con cada hallazgo — haz clic para abrir la ficha</span></div>
  <div id="decGrupos"></div>
</section>

<section class="tabpane" id="tab-proyectos">
  <div class="res-header"><h2>Mesa de Proyectos</h2><span class="n" id="proyN"></span></div>
  <p class="proy-intro">Fusiones de hallazgos de las tres misiones, aterrizadas a plan de entrada,
  costos en CLP, punto de equilibrio y timeline. Un hallazgo no es un negocio: acá están los que sí lo son.</p>
  <div id="listaProyectos"></div>
</section>

<section class="tabpane" id="tab-publicidad">
  <div class="res-header"><h2>Publicidad Meta</h2><span class="n" id="pubN"></span></div>
  <p class="proy-intro">Tablero de inteligencia publicitaria: anuncios de terceros que ya funcionan,
  guiones plug-and-play para cualquier rubro y targeting Chile. Los informes semanales aparecen en
  Explorar y Reportes como cualquier misión; acá viven la biblioteca de guiones y el módulo de cuenta propia.</p>
  <div class="panel-box"><h2>Métricas de mi cuenta Meta</h2><div id="metricasMeta"></div></div>
  <div class="res-header"><h2>Biblioteca de guiones</h2><span class="n">haz clic en un guion para ver las 7 secciones</span></div>
  <div class="grid" id="listaGuiones"></div>
</section>

<section class="tabpane" id="tab-reportes">
  <div class="res-header"><h2>Reportes diarios</h2><span class="n" id="repN"></span></div>
  <div id="listaReportes"></div>
</section>

<section class="tabpane" id="tab-miradar">
  <div class="radar-cols">
    <div class="panel-box">
      <h2>⭐ Me interesan <span class="n" id="nFav"></span></h2>
      <div class="lista-mini" id="listaFav"></div>
    </div>
    <div class="panel-box">
      <h2>👁 Ya vistas <span class="n" id="nVistas"></span></h2>
      <div class="lista-mini" id="listaVistas"></div>
    </div>
  </div>
  <div class="panel-box">
    <h2>Respaldo de tus marcas</h2>
    <p style="color:var(--muted);font-size:13.5px">Tus marcas y notas viven en este navegador (localStorage). Exporta un respaldo si vas a cambiar de equipo o navegador.</p>
    <div class="botonera">
      <button class="btn" id="btnExport">⬇ Exportar marcas y notas</button>
      <button class="btn" id="btnImport">⬆ Importar respaldo</button>
      <input type="file" id="fileImport" accept="application/json" style="display:none">
      <button class="btn peligro" id="btnLimpiar">Borrar todas las marcas</button>
    </div>
  </div>
</section>

</main>

<div class="overlay" id="overlay">
  <div class="modal" id="modal">
    <div class="modal-head" id="modalHead"></div>
    <div class="modal-cuerpo" id="modalCuerpo"></div>
    <div class="modal-nav">
      <button class="btn" id="navPrev">‹ Anterior</button>
      <span class="guardado" id="guardado">✓ nota guardada</span>
      <button class="btn" id="navNext">Siguiente ›</button>
    </div>
  </div>
</div>

<script id="datos" type="application/json">__DATA__</script>
<script id="reportesJson" type="application/json">__REPORTES__</script>
<script id="proyectosJson" type="application/json">__PROYECTOS__</script>
<script id="guionesJson" type="application/json">__GUIONES__</script>
<script id="metricasJson" type="application/json">__METRICAS__</script>
<script>
'use strict';
var DATA = JSON.parse(document.getElementById('datos').textContent);
var REPORTES = JSON.parse(document.getElementById('reportesJson').textContent);
var PROYECTOS = JSON.parse(document.getElementById('proyectosJson').textContent);
var GUIONES = JSON.parse(document.getElementById('guionesJson').textContent);
var METRICAS = JSON.parse(document.getElementById('metricasJson').textContent);
DATA.forEach(function(t, i){ t._i = i });

var LSKEY = 'radar-negocios-v1';
var estado = {};
try { estado = JSON.parse(localStorage.getItem(LSKEY) || '{}') } catch (e) { estado = {} }
function st(id){ return estado[id] || {} }
function setSt(id, patch){
  estado[id] = Object.assign({}, estado[id] || {}, patch);
  try { localStorage.setItem(LSKEY, JSON.stringify(estado)) } catch (e) {}
  renderTodo();
}

var ACCION_TXT = { ADOPTAR_YA: 'Adoptar ya', EMPEZAR_YA: 'Empezar ya', PROTOTIPAR: 'Prototipar', PILOTEAR: 'Pilotear', OBSERVAR: 'Observar', DESCARTAR: 'Descartar' };
var VER_TXT = { APLICA: '▲ Aplica', APLICA_CON_AJUSTES: '▲ Con ajustes', NO_APLICA_AUN: '▼ No aún' };
var CAT_TXT = {};
DATA.forEach(function(t){ CAT_TXT[t.categoria] = t.categoria_label });

function esc(s){ return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;') }

var GRUPOS = [
  { k: 'categoria', titulo: 'Misión', ops: Object.keys(CAT_TXT).map(function(c){ return [c, CAT_TXT[c]] }) },
  { k: 'veredicto', titulo: 'Veredicto Chile', ops: [['APLICA','▲ Aplica'],['APLICA_CON_AJUSTES','▲ Con ajustes'],['NO_APLICA_AUN','▼ No aún']] },
  { k: 'accion', titulo: 'Decisión', ops: [['ADOPTAR_YA','Adoptar ya'],['EMPEZAR_YA','Empezar ya'],['PROTOTIPAR','Prototipar'],['PILOTEAR','Pilotear'],['OBSERVAR','Observar'],['DESCARTAR','Descartar']] },
  { k: 'score_tier', titulo: 'Score', ops: [['destacada','Destacada ≥15'],['alta','Alta 13-14'],['media','Media 10-12'],['baja','Baja <10']] },
  { k: 'impacto', titulo: 'Impacto', ops: [['alto','Alto'],['medio','Medio'],['bajo','Bajo']] },
  { k: 'costo_implementacion', titulo: 'Costo', ops: [['bajo','Bajo'],['medio','Medio'],['alto','Alto']] },
  { k: 'estado', titulo: 'Mi estado', ops: [['novisto','Sin ver'],['visto','👁 Vistas'],['fav','⭐ Me interesan']] }
];
var sel = {}; GRUPOS.forEach(function(g){ sel[g.k] = [] });
var q = '', orden = 'fecha', soloVerif = false;

function valorDe(t, k){
  if (k === 'veredicto') return t.veredicto_chile;
  return t[k];
}
function pasaEstado(t, vals){
  var s = st(t.id);
  return vals.some(function(v){
    if (v === 'visto') return !!s.visto;
    if (v === 'novisto') return !s.visto;
    if (v === 'fav') return !!s.fav;
    return false;
  });
}
function filtrar(){
  var ql = q.toLowerCase();
  return DATA.filter(function(t){
    if (soloVerif && !t.verificado) return false;
    for (var i = 0; i < GRUPOS.length; i++) {
      var g = GRUPOS[i], vals = sel[g.k];
      if (!vals.length) continue;
      if (g.k === 'estado') { if (!pasaEstado(t, vals)) return false; continue }
      if (vals.indexOf(String(valorDe(t, g.k))) < 0) return false;
    }
    if (ql) {
      var blob = (t.nombre + ' ' + t.descripcion + ' ' + t.canal + ' ' + (t.adaptacion_chile || '') + ' ' + t.categoria_label).toLowerCase();
      if (blob.indexOf(ql) < 0) return false;
    }
    return true;
  });
}
function ordenar(lista){
  var l = lista.slice();
  if (orden === 'fecha') l.sort(function(a, b){ return b.fecha.localeCompare(a.fecha) || b.score - a.score });
  else if (orden === 'prioridad') l.sort(function(a, b){ return ((a.prioridad || 9) - (b.prioridad || 9)) || (b.score - a.score) });
  else if (orden === 'score') l.sort(function(a, b){ return b.score - a.score });
  else l.sort(function(a, b){ return a.nombre.localeCompare(b.nombre, 'es') });
  return l;
}

function chipsDe(t, conMeta){
  var h = '';
  if (t.prioridad) h += '<span class="prio p' + t.prioridad + '">P' + t.prioridad + '</span>';
  h += '<span class="chip cat-' + t.categoria + '">' + esc(t.categoria_label) + '</span>';
  h += '<span class="chip ver-' + t.veredicto_chile + '">' + (VER_TXT[t.veredicto_chile] || t.veredicto_chile) + '</span>';
  if (t.accion) h += '<span class="chip acc-' + t.accion + '">' + (ACCION_TXT[t.accion] || t.accion) + '</span>';
  if (conMeta) {
    h += '<span class="chip">Score ' + t.score + '/20</span>';
    h += '<span class="chip">' + esc(t.fecha) + '</span>';
  }
  if (!t.verificado) h += '<span class="warn" title="Confianza no alta">⚠︎</span>';
  return h;
}
function botonesMark(t){
  var s = st(t.id);
  return '<button class="mark ' + (s.visto ? 'on-visto' : '') + '" data-mk="visto" data-id="' + esc(t.id) + '" title="Marcar como vista">👁</button>' +
         '<button class="mark ' + (s.fav ? 'on-fav' : '') + '" data-mk="fav" data-id="' + esc(t.id) + '" title="Me interesa">⭐</button>';
}

var listaActual = [];
function renderGrid(){
  var l = ordenar(filtrar());
  listaActual = l;
  document.getElementById('resN').textContent = l.length + ' de ' + DATA.length;
  document.getElementById('pillExplorar').textContent = l.length;
  var g = document.getElementById('grid');
  if (!l.length) { g.innerHTML = '<div class="vacio">Nada calza con estos filtros. Prueba quitando alguno.</div>'; return }
  g.innerHTML = l.map(function(t){
    var s = st(t.id);
    return '<article class="card ' + (s.visto ? 'vista' : '') + '" data-open="' + t._i + '">' +
      (s.visto ? '<span class="tag-vista">VISTA</span>' : '') +
      '<div class="fila1">' + chipsDe(t, false) + '<span class="sp"></span>' + botonesMark(t) + '</div>' +
      '<h3>' + esc(t.nombre) + '</h3>' +
      '<p class="desc">' + esc(t.descripcion) + '</p>' +
      '<div class="meta"><span class="chip">Score ' + t.score + '/20</span><span class="chip">' + esc(t.fecha) + '</span></div>' +
      '</article>';
  }).join('');
}

function renderDecisiones(){
  var grupos = ['ADOPTAR_YA', 'EMPEZAR_YA', 'PROTOTIPAR', 'PILOTEAR', 'OBSERVAR', 'DESCARTAR'];
  var cont = document.getElementById('decGrupos');
  cont.innerHTML = grupos.map(function(acc){
    var items = ordenar(DATA.filter(function(t){ return t.accion === acc }));
    if (!items.length) return '';
    return '<div class="dec-grupo g-' + acc + '"><header><h2>' + (ACCION_TXT[acc] || acc) + '</h2><span class="n">' + items.length + ' hallazgos</span></header>' +
      items.map(function(t){
        var s = st(t.id);
        return '<div class="dec-row ' + (s.visto ? 'vista' : '') + '" data-open="' + t._i + '">' +
          '<div class="nom">' + (t.prioridad ? '<span class="prio p' + t.prioridad + '">P' + t.prioridad + '</span> ' : '') + esc(t.nombre) + '</div>' +
          '<div class="imp">' + esc(t.metrica_exito || t.razon || '').slice(0, 140) + '</div>' +
          '<div class="pz"><b>' + esc(t.fecha) + '</b>' + esc(t.categoria_label) + '</div>' +
          '<div>' + (s.fav ? '⭐' : '') + '</div></div>';
      }).join('') + '</div>';
  }).join('');
}

function cuenta(fn){ var m = {}; DATA.forEach(function(t){ var k = fn(t); m[k] = (m[k] || 0) + 1 }); return m }
function barras(elId, pares, colores){
  var max = Math.max.apply(null, pares.map(function(p){ return p[1] })) || 1;
  document.getElementById(elId).innerHTML = pares.map(function(p, i){
    var c = colores ? colores[i] : 'linear-gradient(90deg,var(--oro),var(--oro2))';
    return '<div class="barrow"><span class="bl">' + esc(p[0]) + '</span><span class="bt"><i style="width:' + Math.round(p[1] / max * 100) + '%;background:' + c + '"></i></span><span class="bn">' + p[1] + '</span></div>';
  }).join('');
}
function renderPanorama(){
  var arriba = DATA.filter(function(t){ return t.veredicto_chile !== 'NO_APLICA_AUN' }).length;
  var acc = cuenta(function(t){ return t.accion });
  var ver = cuenta(function(t){ return t.veredicto_chile });
  var vistas = DATA.filter(function(t){ return st(t.id).visto }).length;
  var favs = DATA.filter(function(t){ return st(t.id).fav }).length;
  document.getElementById('statgrid').innerHTML =
    '<div class="stat"><div class="v">' + DATA.length + '</div><div class="l">hallazgos totales</div></div>' +
    '<div class="stat"><div class="v">' + REPORTES.length + '</div><div class="l">reportes diarios</div></div>' +
    '<div class="stat gold"><div class="v">' + arriba + '</div><div class="l">▲ aplican a Chile</div></div>' +
    '<div class="stat green"><div class="v">' + ((acc.ADOPTAR_YA || 0) + (acc.EMPEZAR_YA || 0)) + '</div><div class="l">adoptar/empezar ya</div></div>' +
    '<div class="stat amber"><div class="v">' + (acc.PILOTEAR || 0) + '</div><div class="l">pilotear</div></div>' +
    '<div class="stat blue"><div class="v">' + (acc.OBSERVAR || 0) + '</div><div class="l">observar</div></div>' +
    '<div class="stat"><div class="v">' + vistas + '</div><div class="l">👁 ya vistas</div></div>' +
    '<div class="stat gold"><div class="v">' + favs + '</div><div class="l">⭐ me interesan</div></div>';
  barras('chartAccion', [['Adoptar/empezar ya', (acc.ADOPTAR_YA || 0) + (acc.EMPEZAR_YA || 0)], ['Pilotear', acc.PILOTEAR || 0], ['Observar', acc.OBSERVAR || 0], ['Descartar', acc.DESCARTAR || 0]],
    ['var(--verde)', 'var(--ambar)', 'var(--azul)', 'var(--gris)']);
  barras('chartVeredicto', [['Aplica', ver.APLICA || 0], ['Aplica con ajustes', ver.APLICA_CON_AJUSTES || 0], ['No aún', ver.NO_APLICA_AUN || 0]],
    ['var(--verde)', 'var(--oro2)', 'var(--rojo)']);
  var cat = cuenta(function(t){ return t.categoria_label });
  barras('chartCat', Object.keys(cat).map(function(c){ return [c, cat[c]] }));

  var recientes = REPORTES.slice(0, 4);
  document.getElementById('resumenes').innerHTML = recientes.map(function(r){
    return '<div style="margin-bottom:14px"><div style="font-size:12.5px;color:var(--oro2);font-weight:700;margin-bottom:4px">' +
      esc(r.fecha) + ' · ' + esc(r.categoria_label) + '</div><p style="font-size:13.5px;color:#cfd6e0">' + esc(r.resumen || '(sin resumen)') + '</p></div>';
  }).join('') || '<p style="color:var(--muted)">Aún no hay reportes.</p>';
}

function itemMini(t){
  var s = st(t.id);
  return '<div class="item" data-open="' + t._i + '"><div style="flex:1"><div class="tt">' + esc(t.nombre) + '</div>' +
    (s.nota ? '<div class="nt">📝 ' + esc(s.nota) + '</div>' : '') + '</div>' +
    '<span class="chip acc-' + t.accion + '">' + (ACCION_TXT[t.accion] || '') + '</span></div>';
}
function renderMiRadar(){
  var favs = ordenar(DATA.filter(function(t){ return st(t.id).fav }));
  var vistas = ordenar(DATA.filter(function(t){ return st(t.id).visto }));
  document.getElementById('nFav').textContent = '(' + favs.length + ')';
  document.getElementById('nVistas').textContent = '(' + vistas.length + ')';
  document.getElementById('pillFav').textContent = favs.length;
  document.getElementById('listaFav').innerHTML = favs.length ? favs.map(itemMini).join('') : '<div class="vacio">Marca hallazgos con ⭐ y aparecerán aquí.</div>';
  document.getElementById('listaVistas').innerHTML = vistas.length ? vistas.map(itemMini).join('') : '<div class="vacio">Lo que marques con 👁 aparecerá aquí.</div>';
}

function renderReportes(){
  document.getElementById('repN').textContent = REPORTES.length + ' reportes';
  document.getElementById('listaReportes').innerHTML = REPORTES.map(function(r, i){
    var items = DATA.filter(function(t){ return t.fecha === r.fecha && t.categoria === r.categoria });
    return '<details class="acordeon"' + (i < 2 ? ' open' : '') + '><summary>' + esc(r.fecha) + ' · ' + esc(r.categoria_label) +
      ' <span class="chip">' + r.n_opps + ' hallazgos</span><span class="flecha">›</span></summary>' +
      '<div class="cuerpo">' +
      '<p class="resumen">' + esc(r.resumen || '(sin resumen)') + '</p>' +
      items.map(function(t){
        return '<div class="mini-card" data-open="' + t._i + '"><div class="t">' + esc(t.nombre) + '</div>' + chipsDe(t, true) + '</div>';
      }).join('') +
      '<div class="fuentes">FUENTES: ' + esc(r.fuentes || '—') + '</div>' +
      '</div></details>';
  }).join('') || '<div class="vacio">No hay reportes todavía.</div>';
}

// Mini conversor markdown→HTML. El script no admite dependencias externas, y los
// dossiers usan un subconjunto acotado y documentado en el contrato: encabezados
// ###, listas, tablas, negrita, código, links. Todo se escapa antes de convertir.
function mdInline(s){
  s = esc(s);
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
        '<a href="$2" target="_blank" rel="noopener">$1</a>');
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');   // cursiva: va DESPUÉS de la negrita
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  return s;
}
function mdToHtml(md){
  var lineas = (md || '').split('\n'), out = [], i = 0;
  function esFilaTabla(l){ return /^\s*\|.*\|\s*$/.test(l) }
  function celdas(l){
    return l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(function(c){ return c.trim() });
  }
  while (i < lineas.length){
    var l = lineas[i];
    if (!l.trim()){ i++; continue }
    // tabla: fila de encabezado + separador |---|---|
    if (esFilaTabla(l) && i + 1 < lineas.length && /^\s*\|[\s:|-]+\|\s*$/.test(lineas[i+1])){
      var head = celdas(l), filas = [];
      i += 2;
      while (i < lineas.length && esFilaTabla(lineas[i])){ filas.push(celdas(lineas[i])); i++ }
      out.push('<div class="tablawrap"><table><thead><tr>' +
        head.map(function(c){ return '<th>' + mdInline(c) + '</th>' }).join('') +
        '</tr></thead><tbody>' +
        filas.map(function(f){
          return '<tr>' + f.map(function(c){ return '<td>' + mdInline(c) + '</td>' }).join('') + '</tr>';
        }).join('') + '</tbody></table></div>');
      continue;
    }
    var h = l.match(/^#{3,6}\s+(.+)$/);
    if (h){ out.push('<h3>' + mdInline(h[1]) + '</h3>'); i++; continue }
    if (/^\s*[-*]\s+/.test(l) || /^\s*\d+\.\s+/.test(l)){
      var orden = /^\s*\d+\.\s+/.test(l), items = [];
      // Solo se consumen ítems del MISMO tipo: si la lista cambia de numerada a
      // viñeta (o al revés), empieza una lista nueva en vez de colapsar las dos.
      while (i < lineas.length && (orden ? /^\s*\d+\.\s+/.test(lineas[i])
                                        : /^\s*[-*]\s+/.test(lineas[i]))){
        items.push(lineas[i].replace(/^\s*(?:[-*]|\d+\.)\s+/, ''));
        i++;
      }
      out.push('<' + (orden ? 'ol' : 'ul') + '>' +
        items.map(function(t){ return '<li>' + mdInline(t) + '</li>' }).join('') +
        '</' + (orden ? 'ol' : 'ul') + '>');
      continue;
    }
    if (/^\s*>/.test(l)){
      var cita = [];
      while (i < lineas.length && /^\s*>/.test(lineas[i])){ cita.push(lineas[i].replace(/^\s*>\s?/, '')); i++ }
      out.push('<p>' + mdInline(cita.join(' ')) + '</p>');
      continue;
    }
    var parr = [];
    while (i < lineas.length && lineas[i].trim() && !esFilaTabla(lineas[i]) &&
           !/^#{3,6}\s/.test(lineas[i]) && !/^\s*[-*]\s+/.test(lineas[i]) &&
           !/^\s*\d+\.\s+/.test(lineas[i]) && !/^\s*>/.test(lineas[i])){
      parr.push(lineas[i]); i++;
    }
    if (parr.length) out.push('<p>' + mdInline(parr.join(' ')) + '</p>');
    // Fallback obligatorio: una línea que parece fila de tabla pero no lo es
    // (sin fila separadora |---|) no la consume ninguna rama de arriba. Sin este
    // else, 'i' no avanza y el while queda en loop infinito, congelando el hilo
    // principal y con él TODO el dashboard, no solo esta pestaña.
    else { out.push('<p>' + mdInline(l) + '</p>'); i++; }
  }
  return out.join('');
}

function claseVeredicto(v){
  var t = (v || '').toUpperCase();
  if (t.indexOf('CONSTRUIR') >= 0) return 'ver-construir';
  if (t.indexOf('PILOTEAR')  >= 0) return 'ver-pilotear';
  if (t.indexOf('ESPERAR')   >= 0) return 'ver-esperar';
  return 'ver-descartar';
}

function renderProyectos(){
  document.getElementById('pillProy').textContent = PROYECTOS.length || '';
  document.getElementById('proyN').textContent =
    PROYECTOS.length + (PROYECTOS.length === 1 ? ' proyecto' : ' proyectos');
  document.getElementById('listaProyectos').innerHTML = PROYECTOS.map(function(p, i){
    return '<details class="acordeon"' + (i === 0 ? ' open' : '') + '><summary>' +
      esc(p.titulo) + ' <span class="chip ' + claseVeredicto(p.veredicto) + '">' +
      esc(p.veredicto) + '</span><span class="flecha">›</span></summary>' +
      '<div class="cuerpo">' +
      '<div class="proy-meta">' +
        '<span class="chip">' + esc(p.estado) + '</span>' +
        // la línea de Arranque trae 2-3 datos separados por '·': un chip por dato,
        // pasados por mdInline para que la negrita del contrato no salga cruda
        p.arranque.split('·').map(function(x){
          return x.trim() ? '<span class="chip">' + mdInline(x.trim()) + '</span>' : '';
        }).join('') +
      '</div>' +
      '<p class="proy-tesis">' + mdInline(p.tesis) + '</p>' +
      '<p class="proy-fusion"><b>Fusión de:</b> ' + mdInline(p.fusion) + '</p>' +
      p.secciones.map(function(s){
        return '<div class="proy-sec"><h4>' + esc(s.nombre) + '</h4>' +
               '<div class="proy-md">' + mdToHtml(s.md) + '</div></div>';
      }).join('') +
      '</div></details>';
  }).join('') || '<div class="vacio">Todavía no hay proyectos en la mesa.</div>';
}

function renderPublicidad(){
  document.getElementById('pillPub').textContent = GUIONES.length || '';
  document.getElementById('pubN').textContent =
    GUIONES.length + (GUIONES.length === 1 ? ' guion' : ' guiones');

  // Módulo de cuenta propia: APAGADO por diseño hasta que config.json declare
  // "conectado": true. Nunca se pintan cifras de ejemplo ni placeholders
  // numéricos: apagado = se dice que está apagado y qué falta, y punto.
  var m = document.getElementById('metricasMeta');
  var campos = METRICAS.campos || {};
  if (!METRICAS.conectado) {
    var falta = campos.pendiente || campos.que_falta || campos.nota ||
      (METRICAS.existe
        ? 'Falta: poner "conectado": true en publicidad/metricas/config.json y conectar la fuente de datos de la cuenta (ver publicidad/metricas/README.md).'
        : 'Falta: crear publicidad/metricas/config.json con "conectado": true y conectar la fuente de datos de la cuenta (ver publicidad/metricas/README.md).');
    m.innerHTML = '<div class="pub-estado"><span class="pub-dot off"></span><div>' +
      '<b>Módulo no conectado</b> — el dashboard no muestra datos de cuenta propia todavía.' +
      '<div class="pub-falta">' + esc(falta) + '</div></div></div>';
  } else {
    var ks = Object.keys(campos);
    m.innerHTML = '<div class="pub-estado"><span class="pub-dot on"></span><div><b>Módulo conectado</b>' +
      (ks.length ? '' : ' — config.json no declara ningún dato todavía; no hay nada que mostrar.') +
      '</div></div>' +
      (ks.length ? '<div class="kv" style="margin-top:12px">' + ks.map(function(k){
        return '<div class="k"><b>' + esc(k) + '</b><span>' + esc(String(campos[k])) + '</span></div>';
      }).join('') + '</div>' : '');
  }

  document.getElementById('listaGuiones').innerHTML = GUIONES.map(function(g, i){
    return '<article class="card" data-guion="' + i + '">' +
      '<div class="fila1"><span class="chip tipo">' + esc(g.tipo) + '</span><span class="chip">' + esc(g.estado) + '</span></div>' +
      '<h3>' + esc(g.titulo) + '</h3>' +
      '<p class="desc">' + esc(g.tesis) + '</p>' +
      '<div class="pub-kv"><b>Origen</b>' + mdInline(g.origen) + '</div>' +
      '<div class="pub-kv"><b>Métrica de referencia</b>' + mdInline(g.metrica_ref) + '</div>' +
      '</article>';
  }).join('') || '<div class="vacio">Todavía no hay guiones en la biblioteca.</div>';
}

function renderHeader(){
  var vistas = DATA.filter(function(t){ return st(t.id).visto }).length;
  document.getElementById('vistasNum').textContent = vistas;
  document.getElementById('totalNum').textContent = DATA.length;
  document.getElementById('progressFill').style.width = (DATA.length ? Math.round(vistas / DATA.length * 100) : 0) + '%';
}
function renderTodo(){ renderHeader(); renderGrid(); renderDecisiones(); renderPanorama(); renderMiRadar(); renderReportes(); renderProyectos(); renderPublicidad(); if (modalIdx >= 0) refrescarMarksModal() }

var modalLista = [], modalIdx = -1, notaTimer = null;
// El overlay/modal es uno solo y lo comparten hallazgos y guiones; modalTipo
// dice cuál está abierto para que ‹/› y las marcas actúen sobre el correcto.
var modalTipo = 'hallazgo';
function secKV(pares){
  var vivos = pares.filter(function(p){ return p[1] });
  if (!vivos.length) return '';
  return '<div class="kv">' + vivos.map(function(p){ return '<div class="k"><b>' + p[0] + '</b><span>' + esc(p[1]) + '</span></div>' }).join('') + '</div>';
}
function abrirModal(lista, idx){
  modalLista = lista; modalIdx = idx; modalTipo = 'hallazgo';
  var t = lista[idx];
  var s = st(t.id);
  document.getElementById('modalHead').innerHTML =
    '<button class="cerrar" id="btnCerrar">✕</button>' +
    '<div class="fila">' + chipsDe(t, true) + '</div>' +
    '<h2>' + esc(t.nombre) + '</h2>' +
    '<div class="fila" style="margin-top:9px" id="marksModal">' + botonesMark(t) + '<span style="font-size:12px;color:var(--muted)">' + esc(t.fuente_reporte) + '</span></div>';
  var c = '';
  c += '<div class="msec"><h4>Qué es</h4><p>' + esc(t.descripcion) + '</p></div>';
  if (t.razon) c += '<div class="msec"><h4>Por qué es relevante</h4><p>' + esc(t.razon) + '</p></div>';
  if (t.evidencia && t.evidencia.length) c += '<div class="msec"><h4>Evidencia (' + t.evidencia.length + ')</h4><ul>' + t.evidencia.map(function(e){
    return '<li><a href="' + esc(e.url) + '" target="_blank" rel="noopener">' + esc(e.fuente) + '</a></li>';
  }).join('') + '</ul></div>';
  if (t.adaptacion_chile) c += '<div class="msec"><h4>🇨🇱 Dónde funciona / adaptación Chile</h4><p>' + esc(t.adaptacion_chile) + '</p></div>';
  c += '<div class="msec"><h4>Filtro Chile</h4><p><span class="chip ver-' + t.veredicto_chile + '">' + (VER_TXT[t.veredicto_chile] || t.veredicto_chile) + '</span></p></div>';
  c += '<div class="msec"><h4>Decisión de negocio</h4><p><span class="chip acc-' + t.accion + '">' + (ACCION_TXT[t.accion] || t.accion) + '</span></p>' +
    secKV([['Confianza', t.confianza], ['Impacto', t.impacto], ['Costo', t.costo_implementacion], ['Métrica de éxito', t.metrica_exito]]) + '</div>';
  if (t.pasos && t.pasos.length) c += '<div class="msec"><h4>⚡ Pasos esta semana</h4><ul>' + t.pasos.map(function(p){ return '<li>' + esc(p) + '</li>' }).join('') + '</ul></div>';
  c += '<div class="msec"><h4>📝 Mi nota</h4><textarea class="notabox" id="notaBox" placeholder="Apunta aquí tu idea, a quién se la encargas, qué quieres probar…">' + esc(s.nota || '') + '</textarea></div>';
  document.getElementById('modalCuerpo').innerHTML = c;
  document.getElementById('navPrev').disabled = idx <= 0;
  document.getElementById('navNext').disabled = idx >= lista.length - 1;
  document.getElementById('overlay').classList.add('abierto');
  document.body.style.overflow = 'hidden';
  document.getElementById('btnCerrar').onclick = cerrarModal;
  document.getElementById('notaBox').oninput = function(){
    var v = this.value;
    clearTimeout(notaTimer);
    var id = t.id;
    notaTimer = setTimeout(function(){
      estado[id] = Object.assign({}, estado[id] || {}, { nota: v });
      try { localStorage.setItem(LSKEY, JSON.stringify(estado)) } catch (e) {}
      var g = document.getElementById('guardado'); g.classList.add('ok');
      setTimeout(function(){ g.classList.remove('ok') }, 1200);
      renderMiRadar();
    }, 450);
  };
}
function abrirGuion(lista, idx){
  modalLista = lista; modalIdx = idx; modalTipo = 'guion';
  var g = lista[idx];
  document.getElementById('modalHead').innerHTML =
    '<button class="cerrar" id="btnCerrar">✕</button>' +
    '<div class="fila"><span class="chip tipo">' + esc(g.tipo) + '</span><span class="chip">' + esc(g.estado) + '</span>' +
    '<span class="chip">' + esc(g.archivo) + '</span></div>' +
    '<h2>' + esc(g.titulo) + '</h2>';
  document.getElementById('modalCuerpo').innerHTML =
    '<p class="proy-tesis">' + mdInline(g.tesis) + '</p>' +
    '<p class="proy-fusion"><b>Origen:</b> ' + mdInline(g.origen) +
    '<br><b>Métrica de referencia:</b> ' + mdInline(g.metrica_ref) + '</p>' +
    g.secciones.map(function(s){
      return '<div class="proy-sec"><h4>' + esc(s.nombre) + '</h4>' +
             '<div class="proy-md">' + mdToHtml(s.md) + '</div></div>';
    }).join('');
  document.getElementById('navPrev').disabled = idx <= 0;
  document.getElementById('navNext').disabled = idx >= lista.length - 1;
  document.getElementById('overlay').classList.add('abierto');
  document.body.style.overflow = 'hidden';
  document.getElementById('btnCerrar').onclick = cerrarModal;
}
function navModal(delta){
  var n = modalIdx + delta;
  if (modalIdx < 0 || n < 0 || n >= modalLista.length) return;
  if (modalTipo === 'guion') abrirGuion(modalLista, n); else abrirModal(modalLista, n);
}
function refrescarMarksModal(){
  if (modalIdx < 0 || modalTipo !== 'hallazgo') return;
  var t = modalLista[modalIdx];
  var el = document.getElementById('marksModal');
  if (el) el.innerHTML = botonesMark(t) + '<span style="font-size:12px;color:var(--muted)">' + esc(t.fuente_reporte) + '</span>';
}
function cerrarModal(){ document.getElementById('overlay').classList.remove('abierto'); document.body.style.overflow = ''; modalIdx = -1 }
document.getElementById('overlay').addEventListener('click', function(e){ if (e.target === this) cerrarModal() });
document.getElementById('navPrev').onclick = function(){ navModal(-1) };
document.getElementById('navNext').onclick = function(){ navModal(1) };
document.addEventListener('keydown', function(e){
  if (modalIdx < 0) return;
  if (e.key === 'Escape') cerrarModal();
  if (e.key === 'ArrowLeft') navModal(-1);
  if (e.key === 'ArrowRight') navModal(1);
});

document.addEventListener('click', function(e){
  var mk = e.target.closest('.mark');
  if (mk) {
    e.stopPropagation();
    var id = mk.getAttribute('data-id'), tipo = mk.getAttribute('data-mk');
    var cur = st(id), patch = {};
    patch[tipo] = !cur[tipo];
    setSt(id, patch);
    return;
  }
  var gi = e.target.closest('[data-guion]');
  if (gi) { abrirGuion(GUIONES, parseInt(gi.getAttribute('data-guion'), 10)); return; }
  var op = e.target.closest('[data-open]');
  if (op) {
    var i = parseInt(op.getAttribute('data-open'), 10);
    var t = DATA[i];
    var lista = listaActual.length ? listaActual : DATA;
    var idx = lista.indexOf(t);
    if (idx < 0) { lista = [t]; idx = 0 }
    abrirModal(lista, idx);
  }
});

document.querySelectorAll('.tab').forEach(function(b){
  b.onclick = function(){
    document.querySelectorAll('.tab').forEach(function(x){ x.classList.remove('active') });
    document.querySelectorAll('.tabpane').forEach(function(x){ x.classList.remove('active') });
    b.classList.add('active');
    document.getElementById('tab-' + b.getAttribute('data-tab')).classList.add('active');
    window.scrollTo({ top: 0 });
  };
});

(function(){
  var cont = document.getElementById('gruposFiltro');
  cont.innerHTML = GRUPOS.map(function(g){
    return '<div class="fgrupo"><div class="ftit">' + g.titulo + '</div><div class="fops">' +
      g.ops.map(function(o){ return '<button class="fop" data-g="' + g.k + '" data-v="' + esc(o[0]) + '">' + o[1] + '</button>' }).join('') +
      '</div></div>';
  }).join('');
  cont.addEventListener('click', function(e){
    var b = e.target.closest('.fop');
    if (!b) return;
    var g = b.getAttribute('data-g'), v = b.getAttribute('data-v');
    var arr = sel[g], ix = arr.indexOf(v);
    if (ix < 0) arr.push(v); else arr.splice(ix, 1);
    b.classList.toggle('on');
    renderGrid();
  });
})();
document.getElementById('buscar').oninput = function(){ q = this.value.trim(); renderGrid() };
document.getElementById('orden').onchange = function(){ orden = this.value; renderGrid() };
document.getElementById('soloVerif').onchange = function(){ soloVerif = this.checked; renderGrid() };
document.getElementById('btnReset').onclick = function(){
  GRUPOS.forEach(function(g){ sel[g.k] = [] });
  q = ''; soloVerif = false;
  document.getElementById('buscar').value = '';
  document.getElementById('soloVerif').checked = false;
  document.querySelectorAll('.fop.on').forEach(function(b){ b.classList.remove('on') });
  renderGrid();
};

document.getElementById('btnExport').onclick = function(){
  var blob = new Blob([JSON.stringify({ app: 'radar-negocios', exportado: new Date().toISOString(), estado: estado }, null, 2)], { type: 'application/json' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'radar-marcas-respaldo.json';
  a.click();
};
document.getElementById('btnImport').onclick = function(){ document.getElementById('fileImport').click() };
document.getElementById('fileImport').onchange = function(){
  var f = this.files[0];
  if (!f) return;
  var r = new FileReader();
  r.onload = function(){
    try {
      var j = JSON.parse(r.result);
      var nuevo = j.estado || j;
      Object.keys(nuevo).forEach(function(id){ estado[id] = Object.assign({}, estado[id] || {}, nuevo[id]) });
      localStorage.setItem(LSKEY, JSON.stringify(estado));
      renderTodo();
      alert('Respaldo importado: marcas combinadas con las actuales.');
    } catch (e) { alert('No pude leer ese archivo: ' + e.message) }
  };
  r.readAsText(f);
};
document.getElementById('btnLimpiar').onclick = function(){
  if (confirm('¿Borrar TODAS tus marcas, favoritas y notas? Esto no se puede deshacer (exporta un respaldo primero).')) {
    estado = {};
    localStorage.removeItem(LSKEY);
    renderTodo();
  }
};

renderTodo();
</script>
</body>
</html>"""

# ── índice de ideas ya cubiertas (compatibilidad con la rutina diaria) ────

def write_ideas_index(rows):
    lines = [
        "# Índice de ideas ya cubiertas",
        "",
        "_Generado automáticamente por `build_dashboard.py` — no editar a mano. "
        "Se regenera solo en cada push a `main` vía "
        "`.github/workflows/rebuild-dashboard.yml`._",
        "",
    ]
    for t in rows:
        lines.append(f"- {t['fecha']} · {t['categoria_label']} · {t['nombre']} (Score {t['score']}/20)")
    lines.append("")
    with open(IDEAS_INDEX_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return len(rows)

# ── main ────────────────────────────────────────────────────────────────

def main():
    data = collect()
    indice = load_indice()
    rows = build_dataset(data, indice)

    reportes_meta = []
    for g in data:
        for r in g["reports"]:
            reportes_meta.append({
                "fecha": r["date"], "categoria": g["key"], "categoria_label": g["label"],
                "resumen": r["resumen"], "fuentes": r["fuentes"], "n_opps": r["n_opps"],
            })
    reportes_meta.sort(key=lambda x: x["fecha"], reverse=True)

    proyectos = collect_proyectos()
    guiones = collect_guiones()
    metricas = load_metricas_config()

    latest = max((r["fecha"] for r in reportes_meta), default=None)
    n_rep = len(reportes_meta)
    n_dom = len(set(r["categoria"] for r in reportes_meta))
    sub = f"{len(rows)} hallazgos · {n_rep} reportes · {n_dom} misiones"
    if proyectos:
        sub += f" · {len(proyectos)} proyectos"
    if guiones:
        sub += f" · {len(guiones)} " + ("guion" if len(guiones) == 1 else "guiones")
    sub += f" · actualizado {latest or '—'}"

    html = TEMPLATE
    html = html.replace("__SUB__", sub)
    data_json = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    reportes_json = json.dumps(reportes_meta, ensure_ascii=False).replace("</", "<\\/")
    proyectos_json = json.dumps(proyectos, ensure_ascii=False).replace("</", "<\\/")
    guiones_json = json.dumps(guiones, ensure_ascii=False).replace("</", "<\\/")
    metricas_json = json.dumps(metricas, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace("__DATA__", data_json)
    html = html.replace("__REPORTES__", reportes_json)
    html = html.replace("__PROYECTOS__", proyectos_json)
    html = html.replace("__GUIONES__", guiones_json)
    html = html.replace("__METRICAS__", metricas_json)

    with open(os.path.join(BASE, "dashboard.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    n_idx = write_ideas_index(rows)

    n_dest = sum(1 for t in rows if t["score_tier"] == "destacada")
    print("✓ dashboard generado (v4 — estilo investigacion-tendencias):")
    print(f"  {len(rows)} hallazgos · {n_rep} reportes · {n_dest} destacados ≥{DESTACADA}")
    print(f"✓ INDICE_IDEAS.md regenerado: {n_idx} ideas indexadas")
    print(f"  {len(proyectos)} proyectos · {len(guiones)} guiones · módulo Meta "
          + ("conectado" if metricas["conectado"] else "apagado"))

if __name__ == "__main__":
    main()
