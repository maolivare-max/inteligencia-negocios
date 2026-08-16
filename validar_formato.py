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

POLÍTICA DE SEVERIDAD
---------------------
ERROR (rompe el build):
  - un dossier de proyectos/ que viola el contrato de la Misión 4;
  - un reporte del que no se extrae NINGÚN hallazgo (desaparece del dashboard
    entero sin dejar rastro visible para quien solo mira el tablero).
AVISO (no rompe el build):
  - drift de formato en reportes ya publicados. Son 140+ archivos históricos
    con desviaciones conocidas; romper CI por ellos dejaría el dashboard sin
    poder regenerarse. Se listan para que se arreglen, no para bloquear.

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
    with open(path, encoding="utf-8") as f:
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

    with open(path, encoding="utf-8") as f:
        txt = f.read()

    # un dossier no es un hallazgo: no debe disparar el parser de las otras misiones
    if RE_HALLAZGO.search(txt):
        err(rel, "usa el patrón '## N. Nombre — Score X/20' en un encabezado; "
                 "está reservado para hallazgos y confunde el contrato")

    if len(re.findall(r"^#\s+\S", txt, re.MULTILINE)) != 1:
        err(rel, "debe haber exactamente una línea de título con un solo '#'")

    for sec in p["secciones"]:
        if not sec["md"].strip():
            err(rel, f"la sección '{sec['nombre']}' está vacía")

    # el resumen financiero es el corazón del dossier: exigimos costos etiquetados
    fin = next((s["md"] for s in p["secciones"] if s["nombre"] == "Resumen financiero"), "")
    if not re.search(r"\[(?:verificado|estimado|desconocido)\]", fin):
        err(rel, "el Resumen financiero no tiene ni un costo etiquetado "
                 "[verificado]/[estimado]/[desconocido] — es obligatorio (MISIÓN 4)")
    if "CLP" not in fin:
        avisar(rel, "el Resumen financiero no menciona CLP; los costos deben ir en pesos")

    traz = next((s["md"] for s in p["secciones"] if s["nombre"] == "Trazabilidad"), "")
    if not re.search(r"reportes(?:-inmobiliario|-biohacking)?/\d{4}-\d{2}-\d{2}\.md", traz):
        err(rel, "la Trazabilidad no cita ningún reporte de origen con ruta "
                 "(ej. reportes/2026-07-15.md) — sin eso no se puede volver a la evidencia")


def main():
    estricto = "--estricto" in sys.argv

    n_rep = 0
    for key, label, folder in bd.SOURCES:
        for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
            validar_reporte(path, key)
            n_rep += 1

    n_proy = 0
    if os.path.isdir(bd.PROYECTOS_DIR):
        for path in sorted(glob.glob(os.path.join(bd.PROYECTOS_DIR, "*.md"))):
            if os.path.basename(path).startswith("_"):
                continue
            validar_dossier(path)
            n_proy += 1

    print(f"Validados {n_rep} reportes y {n_proy} dossiers.")

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
