#!/usr/bin/env python3
"""Valida que reportes y dossiers cumplan el contrato que el parser espera.

POR QUÉ EXISTE
--------------
build_dashboard.py degrada a vacío en silencio cuando un reporte no calza con
el regex: no lanza error, no avisa, simplemente el campo queda en blanco y el
dashboard muestra menos de lo que el reporte realmente dice. La auditoría de
agosto 2026 encontró tres casos reales ya en producción:

  1. `**Confianza: Alta**` (dos puntos DENTRO de las negritas) no matchea el
     patrón `**Confianza:** Alta` → los 7 hallazgos de reportes/2026-06-24.md
     quedaron marcados como no verificados aunque el texto dice "Alta".
  2. Fuentes escritas como lista de viñetas con URLs crudas, en vez de en una
     sola línea con sintaxis [texto](url) → evidencia vacía aunque el reporte
     cite 4 links reales (mismo archivo).
  3. `**Ángulo del día:**` en vez de `**Resumen:**` → 4 de 9 reportes de
     biohacking salen con "(sin resumen)" en el dashboard.

DÓNDE CORRE
-----------
En CI este script se ejecuta DESPUÉS de generar y publicar el dashboard, no antes.
El dashboard es el único medio de entrega del usuario, así que un error de formato
en un reporte no puede dejarlo sin regenerar: para cuando esto corre, el HTML ya se
publicó. Un fallo acá pinta la corrida en rojo para que el problema se vea y se
arregle, sin haber bloqueado la entrega.

POLÍTICA DE SEVERIDAD
---------------------
ERROR (sale 1, corrida en rojo):
  - un dossier de proyectos/ que viola el contrato de la Misión 4, incluida una
    fila de tabla sin separador (que además colgaba el navegador; ver
    _validar_tablas) y un '## ' de más que trunca una sección en silencio;
  - un guion de publicidad/guiones/ que viola el contrato de la Misión 5 (misma
    severidad que los dossiers: 5 metadatos, 7 secciones en orden, tabla de
    variables, KPI con umbral, trazabilidad y cifras etiquetadas por origen);
  - un reporte con encabezados CASI válidos —guion en vez de raya, o score no
    entero—, porque ahí sí hubo intención de publicar hallazgos y se perdieron.
AVISO (sale 0):
  - drift de formato en reportes ya publicados. Son 140+ archivos históricos con
    desviaciones conocidas; se listan para arreglarlos, no para alarmar;
  - un reporte con 0 hallazgos indexables sin encabezados casi-válidos: es un día
    legítimo de solo-actualizaciones. Ojo con el diagnóstico — el reporte SÍ
    aparece en la pestaña Reportes con su resumen; lo que no ocurre es que su
    contenido entre a Explorar, Decisiones ni INDICE_IDEAS.md.

Con --estricto los avisos también rompen el build (útil al limpiar el histórico).

Uso:  python3 validar_formato.py [--estricto]
"""

import os
import re
import sys
import glob

import build_dashboard as bd

ERRORES = []
AVISOS = []


def err(archivo, msg):
    ERRORES.append(f"{archivo}: {msg}")


def avisar(archivo, msg):
    AVISOS.append(f"{archivo}: {msg}")


# ── reportes de las misiones 1-3 ────────────────────────────────────────────

RE_HALLAZGO = re.compile(r"^##\s+\d+\.\s+(.+?)\s+—\s+Score\s+(\d+)/20\s*$",
                         re.MULTILINE)
# variantes que la gente escribe y el parser NO acepta
RE_CASI_HALLAZGO = re.compile(
    r"^##\s+\d+\.\s+.+?\s+[-–]\s+Score\s+\d+/20\s*$|"      # guion o en-dash
    r"^##\s+\d+\.\s+.+?\s+—\s+Score\s+[\d.,~-]*[.,~-][\d]*\s*/\s*20\s*$",
    re.MULTILINE)
RE_CONF_OK = re.compile(r"\*\*Confianza:\*\*\s*\S")
RE_CONF_MAL = re.compile(r"\*\*Confianza:\s*[^*]+\*\*")
RE_RESUMEN_OK = re.compile(r"\*\*Resumen[^:]*:\*\*\s*\S")
RE_RESUMEN_MAL = re.compile(r"\*\*(?:[ÁA]ngulo|Panorama|S[íi]ntesis)[^:]*:\*\*")
RE_FUENTE_LINEA = re.compile(r"\*\*(?:D[oó]nde lo encontr[eé])[^:]*:\*\*\s*(.+)")
RE_LINK_MD = re.compile(r"\[([^\]]+)\]\((https?://[^\s\)]+)\)")


def validar_reporte(path, categoria):
    rel = os.path.relpath(path, bd.BASE)
    with open(path, encoding="utf-8-sig") as f:
        txt = f.read()

    hallazgos = RE_HALLAZGO.findall(txt)
    if not hallazgos:
        # Ojo con el diagnóstico: el reporte SÍ sigue apareciendo en la pestaña
        # "Reportes" con su fecha y resumen. Lo que no ocurre es que su contenido
        # entre al sistema de decisión (Explorar, Decisiones, INDICE_IDEAS.md).
        casi = RE_CASI_HALLAZGO.findall(txt)
        if casi:
            # esto sí es un bug de formato: había intención de publicar hallazgos
            err(rel, "tiene encabezados casi-válidos que el parser no reconoce "
                     "(¿guion '-' o '–' en vez de raya '—'? ¿score no entero?); "
                     "esos hallazgos se pierden en silencio")
        else:
            # día de solo-actualizaciones: legítimo según el protocolo, pero el
            # contenido queda fuera del índice y del anti-repetición
            bloques = re.findall(r"^##\s+(?!\d+\.)(.+?)\s*$", txt, re.MULTILINE)
            avisar(rel, f"0 hallazgos indexables ({len(bloques)} bloque(s) sin score: "
                        f"{', '.join(b[:34] for b in bloques[:3])}...). El reporte aparece "
                        "en la pestaña Reportes, pero su contenido NO entra a Explorar, "
                        "Decisiones ni INDICE_IDEAS.md")
        return

    for n, (nombre, score) in enumerate(hallazgos, start=1):
        if not (0 <= int(score) <= 20):
            avisar(rel, f"hallazgo {n} ('{nombre[:40]}') tiene score {score}/20 fuera de rango")

    # Confianza mal escrita: dos puntos dentro de las negritas
    if RE_CONF_MAL.search(txt) and not RE_CONF_OK.search(txt):
        avisar(rel, "usa '**Confianza: X**' — el parser exige '**Confianza:** X' "
                    "(dos puntos FUERA de las negritas); si no, queda como no verificado")

    # Resumen del reporte
    if not RE_RESUMEN_OK.search(txt):
        if RE_RESUMEN_MAL.search(txt):
            avisar(rel, "usa 'Ángulo/Panorama/Síntesis del día' — el parser solo "
                        "reconoce '**Resumen...:**'; saldrá '(sin resumen)' en el dashboard")
        else:
            avisar(rel, "sin línea '**Resumen...:**'; saldrá '(sin resumen)' en el dashboard")

    # Evidencia: la línea de fuentes debe traer links markdown en la MISMA línea
    for m in RE_FUENTE_LINEA.finditer(txt):
        if not RE_LINK_MD.search(m.group(1)):
            avisar(rel, "la línea '**Dónde lo encontré:**' no trae ningún [texto](url) "
                        "en la misma línea; ese hallazgo quedará sin evidencia")
            break


# ── dossiers de la misión 4 ────────────────────────────────────────────────

VEREDICTOS = {"CONSTRUIR YA", "PILOTEAR", "ESPERAR SEÑAL", "DESCARTAR"}
ESTADOS = {"Propuesto", "En pilotaje", "Activo", "Archivado"}
PROYECTO_SECCIONES_ESPERADAS = bd.PROYECTO_SECCIONES


def _es_fila_tabla(l):
    return re.match(r"^\s*\|.*\|\s*$", l) is not None


def _validar_tablas(rel, txt):
    """Detecta filas de tabla huérfanas — una línea que empieza y termina en '|'
    pero sin la fila separadora |---|---| debajo.

    Esto NO es cosmético: el conversor markdown→HTML del dashboard corre en el
    navegador y una fila huérfana lo dejaba en loop infinito, congelando la página
    entera (todas las pestañas, no solo Proyectos). El loop ya está arreglado en
    build_dashboard.py, pero la tabla igual saldría renderizada como texto suelto,
    así que conviene detectarla acá, en CI, y no en el navegador del usuario."""
    lineas = txt.split("\n")
    i = 0
    while i < len(lineas):
        if _es_fila_tabla(lineas[i]):
            if i + 1 < len(lineas) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lineas[i + 1]):
                i += 2
                while i < len(lineas) and _es_fila_tabla(lineas[i]):
                    i += 1
                continue
            err(rel, f"línea {i+1}: fila de tabla sin fila separadora '|---|---|' "
                     f"debajo → no se renderiza como tabla: {lineas[i].strip()[:60]}")
        i += 1


def validar_dossier(path):
    rel = os.path.relpath(path, bd.BASE)
    try:
        p = bd.parse_proyecto(path)
    except Exception as e:
        err(rel, str(e))
        return

    if p["veredicto"] not in VEREDICTOS:
        err(rel, f"Veredicto '{p['veredicto']}' no es uno de {sorted(VEREDICTOS)}")
    if p["estado"] not in ESTADOS:
        err(rel, f"Estado '{p['estado']}' no es uno de {sorted(ESTADOS)}")

    # misma codificación que parse_proyecto(): utf-8-sig para tolerar BOM
    with open(path, encoding="utf-8-sig") as f:
        txt = f.read().replace("\r\n", "\n")

    # un dossier no es un hallazgo: no debe disparar el parser de las otras misiones
    if RE_HALLAZGO.search(txt):
        err(rel, "usa el patrón '## N. Nombre — Score X/20' en un encabezado; "
                 "está reservado para hallazgos y confunde el contrato")

    if len(re.findall(r"^#\s+\S", txt, re.MULTILINE)) != 1:
        err(rel, "debe haber exactamente una línea de título con un solo '#'")

    # Un '## ' extra dentro del cuerpo corta la sección y el resto del contenido
    # se pierde sin aviso (el lookahead del parser termina en el próximo '##').
    # Para subtítulos hay que usar '###'.
    h2 = re.findall(r"^##\s+(.+?)\s*$", txt, re.MULTILINE)
    if len(h2) != len(PROYECTO_SECCIONES_ESPERADAS):
        extra = [h for h in h2 if not re.match(r"^\d+\.\s", h)]
        err(rel, f"tiene {len(h2)} encabezados '## ' y deben ser exactamente "
                 f"{len(PROYECTO_SECCIONES_ESPERADAS)}. Para subtítulos usar '###'. "
                 + (f"Sobran: {extra}" if extra else ""))

    _validar_tablas(rel, txt)

    for sec in p["secciones"]:
        if not sec["md"].strip():
            err(rel, f"la sección '{sec['nombre']}' está vacía")

    # el resumen financiero es el corazón del dossier: exigimos costos etiquetados
    fin = next((s["md"] for s in p["secciones"] if s["nombre"] == "Resumen financiero"), "")
    if not re.search(r"\[(?:verificado(?:\s+sin\s+link)?|estimado|desconocido)\b", fin):
        err(rel, "el Resumen financiero no tiene ni un costo etiquetado "
                 "[verificado]/[verificado sin link]/[estimado]/[desconocido] — "
                 "es obligatorio (MISIÓN 4)")
    if "CLP" not in fin:
        avisar(rel, "el Resumen financiero no menciona CLP; los costos deben ir en pesos")

    traz = next((s["md"] for s in p["secciones"] if s["nombre"] == "Trazabilidad"), "")
    if not re.search(r"reportes(?:-inmobiliario|-biohacking)?/\d{4}-\d{2}-\d{2}\.md", traz):
        err(rel, "la Trazabilidad no cita ningún reporte de origen con ruta "
                 "(ej. reportes/2026-07-15.md) — sin eso no se puede volver a la evidencia")


# ── guiones de la misión 5 ─────────────────────────────────────────────────

GUION_ESTADOS = {"Borrador", "Validado", "En uso", "Archivado"}
GUION_TIPOS = {"Hook", "Ángulo", "Oferta", "Formato", "Secuencia"}
GUION_PLACEHOLDERS = ["{oferta}", "{publico}", "{ciudad}", "{ticket}",
                      "{prueba_social}", "{cta}"]
GUION_SECCIONES_ESPERADAS = bd.GUION_SECCIONES
RE_ETIQUETA_ORIGEN = re.compile(
    r"\[(?:verificado(?:\s+sin\s+link)?|estimado|desconocido)\]")
# "KPI con umbral numérico": una cifra acompañada de comparador, %, moneda o
# palabra de meta. Sin esto, la sección Medición es una intención, no un KPI.
RE_UMBRAL = re.compile(
    r"[<>≤≥]\s*=?\s*(?:CLP|USD|\$)?\s*\d"                       # ≥ 20, < CLP 5.000
    r"|\d[\d.,]*\s*%"                                          # 2,5 %
    r"|(?:CLP|USD|\$)\s*\d"                                    # CLP 3.500
    r"|(?:m[íi]nimo|m[áa]ximo|umbral|meta|objetivo|al menos|m[áa]s de|menos de)"
    r"\s*(?:de|:)?\s*(?:CLP|USD|\$)?\s*\d",                      # mínimo 20 leads
    re.IGNORECASE)
RE_TRAZA_PUBLICIDAD = re.compile(r"reportes-publicidad/\d{4}-\d{2}-\d{2}\.md")


# ── cifras vigiladas (anti auto-confirmación) ──────────────────────────────
#
# El índice anti-repetición indexa por concepto (slug) y por eso no ve una cifra
# que cambia de nombre, de canal o de rubro y vuelve a entrar como dato nuevo.
# Eso fue exactamente lo que pasó con el CPL de CLP 12.000: nació como dato de
# Google Ads, reapareció titulado "Meta Ads" seis semanas después y terminó
# citado bajo cinco agencias distintas como si fueran cinco mediciones.
# radar/cifras.txt registra esas cifras; acá se avisa cuando un reporte las
# vuelve a citar sin declarar que están contaminadas.

CIFRAS_PATH = os.path.join(bd.BASE, "radar", "cifras.txt")
CIFRA_ESTADOS = {"circular", "migrante", "vigilada"}
# Decir en voz alta lo que se está citando es lo único que exime del aviso.
RE_CIFRA_DECLARADA = re.compile(
    r"circular|migrante|reatribuid|indirect[oa]|\[desconocido\]"
    r"|misma cifra|cadena de citaci|auto-?confirmaci", re.IGNORECASE)
# dominio del índice -> carpeta de reportes que le corresponde
DOMINIO_CARPETA = {v: k for k, v in bd.DOMINIO.items()}


def cargar_cifras_vigiladas():
    """[(cifra, dominio, estado, nota)] desde radar/cifras.txt."""
    out = []
    if not os.path.exists(CIFRAS_PATH):
        return out
    with open(CIFRAS_PATH, encoding="utf-8-sig") as f:
        for n, linea in enumerate(f, start=1):
            linea = linea.strip()
            if not linea or linea.startswith("#") or linea.startswith("cifra|"):
                continue
            partes = linea.split("|")
            if len(partes) < 4:
                err("radar/cifras.txt", f"línea {n}: se esperan 4 campos "
                                        f"'cifra|dominio|estado|nota', hay {len(partes)}")
                continue
            cifra, dominio, estado, nota = (p.strip() for p in partes[:4])
            if estado not in CIFRA_ESTADOS:
                err("radar/cifras.txt", f"línea {n}: estado '{estado}' no es uno de "
                                        f"{sorted(CIFRA_ESTADOS)}")
                continue
            out.append((cifra, dominio, estado, nota))
    return out


def validar_cifras_vigiladas(vigiladas):
    """Avisa cuando un reporte cita una cifra registrada sin declarar su estado.

    Severidad AVISO a propósito: la cifra puede citarse — de hecho el informe que
    la denunció tiene que citarla para documentarla. Lo que no puede es citarse
    en silencio, como si fuera una medición limpia."""
    if not vigiladas:
        return
    for key, label, folder in bd.SOURCES:
        dominio = bd.DOMINIO[key]
        aplican = [v for v in vigiladas if v[1] in (dominio, "*")]
        if not aplican:
            continue
        for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
            if os.path.basename(path).startswith("_"):
                continue
            rel = os.path.relpath(path, bd.BASE)
            with open(path, encoding="utf-8-sig") as f:
                lineas = f.read().replace("\r\n", "\n").split("\n")
            # Una sección entera puede estar dedicada a documentar la cadena (el
            # bloque de contra-evidencia, las decisiones del CEO): ahí la cifra se
            # cita a propósito, fila por fila, y exigir la palabra en CADA línea
            # llenaría el informe honesto de avisos. Se declara por sección.
            secciones_declaradas, actual, declarada = {}, 0, False
            for linea in lineas:
                if re.match(r"^#{2,4}\s", linea):
                    secciones_declaradas[actual] = declarada
                    actual += 1
                    declarada = bool(RE_CIFRA_DECLARADA.search(linea))
                elif RE_CIFRA_DECLARADA.search(linea):
                    declarada = True
            secciones_declaradas[actual] = declarada

            sec = 0
            for i, linea in enumerate(lineas, start=1):
                if re.match(r"^#{2,4}\s", linea):
                    sec += 1
                if RE_CIFRA_DECLARADA.search(linea) or secciones_declaradas.get(sec):
                    continue  # se está citando con su estado a la vista
                for cifra, _dom, estado, _nota in aplican:
                    if cifra in linea:
                        avisar(rel, f"línea {i}: cita la cifra vigilada '{cifra}' "
                                    f"({estado}, ver radar/cifras.txt) sin declarar su "
                                    f"estado en la misma línea. Si es la misma cifra "
                                    f"reciclada, decirlo; si es una medición nueva e "
                                    f"independiente, decir de quién y con qué muestra")
                        break


def validar_guion(path):
    """Contrato del guion (ESPEC Misión 5). Severidad ERROR, igual que los
    dossiers: un guion es material de trabajo que se copia y se pega en una
    campaña real, así que una variable sin tabla o un KPI sin umbral no es
    cosmético."""
    rel = os.path.relpath(path, bd.BASE)
    try:
        g = bd.parse_guion(path)
    except Exception as e:
        err(rel, str(e))
        return

    if g["estado"] not in GUION_ESTADOS:
        err(rel, f"Estado '{g['estado']}' no es uno de {sorted(GUION_ESTADOS)}")
    if g["tipo"] not in GUION_TIPOS:
        err(rel, f"Tipo '{g['tipo']}' no es uno de {sorted(GUION_TIPOS)}")

    # misma codificación que parse_guion(): utf-8-sig para tolerar BOM
    with open(path, encoding="utf-8-sig") as f:
        txt = f.read().replace("\r\n", "\n")

    # un guion no es un hallazgo: no debe disparar el parser de las otras misiones
    if RE_HALLAZGO.search(txt):
        err(rel, "usa el patrón '## N. Nombre — Score X/20' en un encabezado; "
                 "está reservado para hallazgos y confunde el contrato")

    if len(re.findall(r"^#\s+\S", txt, re.MULTILINE)) != 1:
        err(rel, "debe haber exactamente una línea de título con un solo '#'")

    # nº exacto de '## ' Y en el orden del contrato (subtítulos internos = '###')
    h2 = re.findall(r"^##\s+(.+?)\s*$", txt, re.MULTILINE)
    esperados = [f"{i}. {n}" for i, n in enumerate(GUION_SECCIONES_ESPERADAS, start=1)]
    if len(h2) != len(esperados):
        extra = [h for h in h2 if h not in esperados]
        err(rel, f"tiene {len(h2)} encabezados '## ' y deben ser exactamente "
                 f"{len(esperados)}. Para subtítulos usar '###'. "
                 + (f"Sobran: {extra}" if extra else ""))
    elif h2 != esperados:
        err(rel, f"las secciones '## ' no van en el orden del contrato: {h2}")

    _validar_tablas(rel, txt)

    for sec in g["secciones"]:
        if not sec["md"].strip():
            err(rel, f"la sección '{sec['nombre']}' está vacía")
    sec = {s["nombre"]: s["md"] for s in g["secciones"]}

    # 3. Variables a rellenar: tabla con separador + los 6 placeholders con llaves
    variables = sec.get("Variables a rellenar", "")
    if not re.search(r"^\s*\|[\s:|-]+\|\s*$", variables, re.MULTILINE):
        err(rel, "la sección 'Variables a rellenar' no trae una tabla markdown "
                 "con fila separadora '|---|---|'")
    faltan = [p for p in GUION_PLACEHOLDERS if p not in variables]
    if faltan:
        err(rel, "a 'Variables a rellenar' le faltan placeholders con llaves: "
                 + ", ".join(faltan))

    # 6. Medición: al menos un KPI con umbral numérico
    if not RE_UMBRAL.search(sec.get("Medición", "")):
        err(rel, "la sección 'Medición' no declara ningún KPI con umbral numérico "
                 "(ej. 'CPL ≤ CLP 4.000', 'CTR ≥ 1,5 %', 'mínimo 20 leads')")

    # 7. Trazabilidad: cita al informe semanal de origen
    if not RE_TRAZA_PUBLICIDAD.search(sec.get("Trazabilidad", "")):
        err(rel, "la Trazabilidad no cita ningún reportes-publicidad/AAAA-MM-DD.md "
                 "— sin eso no se puede volver a la evidencia")

    # cifras etiquetadas por origen
    if not RE_ETIQUETA_ORIGEN.search(txt):
        err(rel, "no tiene ni una cifra etiquetada [verificado]/[verificado sin link]/"
                 "[estimado]/[desconocido] — es obligatorio (MISIÓN 5)")
    if re.search(r"\d", g["metrica_ref"]) and not RE_ETIQUETA_ORIGEN.search(g["metrica_ref"]):
        err(rel, "la 'Métrica de referencia' trae una cifra sin etiqueta de origen "
                 "[verificado]/[verificado sin link]/[estimado]/[desconocido]")
    # Cifras de CPL/CTR/ROAS sueltas sin etiqueta: aviso, no error, porque el
    # regex no distingue una cifra citada de un ejemplo. Se excluye Medición:
    # ahí el umbral del KPI es una meta propia, no una cifra de origen.
    cuerpo_sin_medicion = txt.replace(sec.get("Medición", ""), "")
    for n, linea in enumerate(cuerpo_sin_medicion.split("\n"), start=1):
        if (re.search(r"\b(?:CPL|CTR|ROAS)\b", linea) and re.search(r"\d", linea)
                and not RE_ETIQUETA_ORIGEN.search(linea)):
            avisar(rel, f"cifra de CPL/CTR/ROAS sin etiqueta de origen en la misma "
                        f"línea: {linea.strip()[:70]}")


def main():
    estricto = "--estricto" in sys.argv

    n_rep = 0
    for key, label, folder in bd.SOURCES:
        for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
            if os.path.basename(path).startswith("_"):
                continue  # _plantilla.md no es un reporte (misma regla que build_dashboard.collect)
            validar_reporte(path, key)
            n_rep += 1

    n_proy = 0
    if os.path.isdir(bd.PROYECTOS_DIR):
        for path in sorted(glob.glob(os.path.join(bd.PROYECTOS_DIR, "*.md"))):
            if os.path.basename(path).startswith("_"):
                continue
            validar_dossier(path)
            n_proy += 1

    n_gui = 0
    if os.path.isdir(bd.GUIONES_DIR):
        for path in sorted(glob.glob(os.path.join(bd.GUIONES_DIR, "*.md"))):
            if not bd.es_guion_publicable(os.path.basename(path)):
                continue  # README.md / _plantilla.md no son guiones: ni se publican ni se validan
            validar_guion(path)
            n_gui += 1

    vigiladas = cargar_cifras_vigiladas()
    validar_cifras_vigiladas(vigiladas)

    print(f"Validados {n_rep} reportes, {n_proy} dossiers y {n_gui} guiones "
          f"({len(vigiladas)} cifra(s) vigilada(s)).")

    if AVISOS:
        print(f"\n⚠ {len(AVISOS)} aviso(s) de formato (no rompen el build):")
        for a in AVISOS:
            print(f"  · {a}")

    if ERRORES:
        print(f"\n✗ {len(ERRORES)} error(es) de contrato:")
        for e in ERRORES:
            print(f"  · {e}")
        return 1

    if estricto and AVISOS:
        print("\n✗ modo --estricto: los avisos cuentan como error.")
        return 1

    print("\n✓ Contrato de formato OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
