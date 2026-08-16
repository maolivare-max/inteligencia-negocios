# RUNBOOK — Operación diaria

Guía para dejar el sistema corriendo en automático y para operarlo a mano si hace falta.

---

## Arquitectura

```
CLAUDE.md                            ← memoria: 3 misiones (oportunidades + inmobiliario + biohacking)
build_dashboard.py                   ← genera dashboard.html desde los reportes
dashboard.html                       ← tablero visual (offline, doble clic)
reportes/YYYY-MM-DD.md               ← MISIÓN 1: oportunidades de negocio
reportes-inmobiliario/YYYY-MM-DD.md  ← MISIÓN 2: marketing inmobiliario
reportes-biohacking/YYYY-MM-DD.md    ← MISIÓN 3: biohacking y longevidad
proyectos/NN-slug.md                 ← MISIÓN 4: dossiers de la Mesa de Proyectos
validar_formato.py                   ← valida el contrato antes de generar
```

Las misiones 1-3 son scouts diarios (traen hallazgos sueltos). La misión 4 corre
semanal y no busca nada nuevo: fusiona lo que los scouts ya trajeron y lo aterriza
a plan de entrada, costos en CLP y timeline.

Flujo diario (08:00): generar reporte → guardar .md → `python3 build_dashboard.py`
→ commit + push. La revisión se hace en el dashboard (sin email).

---

## 1. Subir el repo a GitHub (una sola vez)

1. Crea un repo vacío en https://github.com/new (sin README). Copia la URL.
2. En la carpeta del proyecto:

```bash
git branch -M main
git remote add origin https://github.com/TU-USUARIO/NOMBRE-REPO.git
git push -u origin main
```

> Autenticación: usar un Personal Access Token de GitHub (scope `repo`) como contraseña,
> o configurar SSH con `git@github.com:TU-USUARIO/NOMBRE-REPO.git`.

---

## 2. Crear las tres Routines (entrega automática 08:00)

En https://claude.ai/code/routines → **New routine**. Crear TRES, todas con:
- Trigger: **Schedule → Daily → 08:00** (hora local)
- Repositorio: el subido en el paso 1
- Permisos: **Allow unrestricted branch pushes** activado (para que pueda escribir en main)

> NOTA: la entrega NO es por email. El reporte queda en el dashboard tras commit + push.
> No es necesario el conector de Gmail.

### Routine 1 — Oportunidades de Negocio
Nombre: `Reporte diario · Oportunidades`

```
Ejecuta la MISIÓN 1 definida en CLAUDE.md (Analista de Oportunidades de Negocio).
Rastrea las fuentes de alta señal (Indie Hackers, Hacker News, Reddit, Product Hunt,
YC RFS, Exploding Topics, Starter Story). Aplica los TRES filtros y el scoring /20.
Compara con el último archivo en reportes/ para NO repetir oportunidades; marca
"Actualización" si algo cambió. Activa el bloque SEGUIMIENTO DE CRECIMIENTO en toda
oportunidad que supere la media o cumpla el criterio de activación. Guarda el reporte
en reportes/YYYY-MM-DD.md, ejecuta `python3 build_dashboard.py` para actualizar el
dashboard, y haz commit y push de los cambios. NO envíes email: el dashboard es el medio
de revisión.
```

### Routine 2 — Marketing Inmobiliario
Nombre: `Reporte diario · Inmobiliario`

```
Ejecuta la MISIÓN 2 definida en CLAUDE.md (Analista de Tendencias de Marketing
Inmobiliario). Rastrea fuentes de Chile (Portalinmobiliario, Toctoc, CChC, DF,
PropTech chilena) y del mundo (NAR, Inman, The Close, Zillow/Redfin, PropTech US/EU
y LATAM). Busca ideas innovadoras que generen leads con métricas (CPL, conversión,
volumen) y actualiza la sección "FORMA DE VENTA — qué cambió". Aplica los TRES filtros
y el scoring /20. Compara con el último archivo en reportes-inmobiliario/ para priorizar
lo nuevo. Guarda en reportes-inmobiliario/YYYY-MM-DD.md, ejecuta
`python3 build_dashboard.py`, y haz commit y push. NO envíes email: el dashboard es el
medio de revisión.
```

### Routine 3 — Biohacking y Longevidad
Nombre: `Reporte diario · Biohacking`

```
Ejecuta la MISIÓN 3 definida en CLAUDE.md (Analista de Oportunidades de Negocio en
Biohacking/Longevidad). Rastrea fuentes de negocio del rubro (Longevity.Technology,
Fitt Insider, Reddit r/Biohackers/r/QuantifiedSelf/r/longevity, Hacker News, Examine.com
para validar evidencia científica) y señal chilena (MercadoLibre, Falabella, ISP Chile,
laboratorios/clínicas de medicina funcional). Aplica los filtros de solo-founder <USD 10.000
y el scoring /20, MÁS el gate regulatorio obligatorio: cualquier hallazgo que implique
diagnóstico/tratamiento sin médico habilitado se descarta o se marca "⚠ ZONA GRIS
REGULATORIA CHILE" con mitigación explícita. Compara con el último archivo en
reportes-biohacking/ para no repetir. Guarda en reportes-biohacking/YYYY-MM-DD.md, ejecuta
`python3 build_dashboard.py`, y haz commit y push. NO envíes email: el dashboard es el
medio de revisión.
```

---

### Routine 4 — Mesa de Proyectos (semanal, domingos)
Nombre: `Mesa de Proyectos · semanal`
Trigger: **Schedule → Weekly → domingo 09:30** (después de los tres scouts).

```
Ejecuta la MISIÓN 4 definida en CLAUDE.md (Orquestador — Mesa de Proyectos). NO
busques nada nuevo en internet: tu materia prima es lo que las misiones 1, 2 y 3 ya
trajeron. Lee INDICE_IDEAS.md y los corpus de las tres carpetas de reportes. Convoca
los tres equipos: FUSIÓN (detecta qué combinar, con prioridad a las fusiones cruzadas
Misión 1 × Misión 2), CREATIVO (cómo se consiguen los primeros 10 clientes pagando) y
EVALUADOR (costos en CLP etiquetados [verificado]/[estimado]/[desconocido], punto de
equilibrio y timeline). Aplica las reglas de fusión y el veredicto de la mesa. Guarda
el dossier en proyectos/NN-slug.md siguiendo el contrato de formato exacto, corre
`python3 validar_formato.py` y que pase, y haz commit y push a main de SOLO el .md.
Si en la semana no hay ninguna fusión que supere el umbral, el resultado válido es
"esta semana no hay proyecto nuevo" con el registro de qué se evaluó. NO envíes email
ni commitees dashboard.html/index.html.
```

---

## 3. Ver el dashboard

En línea: https://maolivare-max.github.io/inteligencia-negocios/ (sirve desde `main`).
También se puede abrir `dashboard.html` local con doble clic. Se regenera solo vía la
GitHub Action tras cada push a `main` que toque `reportes*/` o `proyectos/`.

Pestañas: Panorama · Explorar · Decisiones · **Proyectos** · Reportes · Mi radar.
La pestaña Proyectos muestra los dossiers de la Misión 4 (plan de entrada, resumen
financiero, timeline), que es contenido distinto de los hallazgos diarios.

Para regenerar y validar a mano:

```bash
python3 validar_formato.py    # contrato de formato; falla si un dossier está mal
python3 build_dashboard.py    # regenera dashboard.html, index.html e INDICE_IDEAS.md
```

`validar_formato.py` distingue dos severidades: los **errores** (dossier que viola el
contrato) rompen el build; los **avisos** (drift de formato en reportes históricos) no,
pero se listan para arreglarlos. Con `--estricto` los avisos también rompen.

---

## 4. Operación manual (si una routine falla)

Pídele a Claude Code, dentro de una sesión con este repo:
> "Ejecuta el flujo de CLAUDE.md para hoy" (genera, guarda, actualiza dashboard, commit + push).

---

## Notas

- El entorno de la nube es efímero: la persistencia vive en GitHub. Sin push, se pierde.
- Una Routine cuenta contra el límite diario de runs de tu plan.
- Si una fuente queda bloqueada por red, cambia el entorno de la routine a Network: Full.
