# RUNBOOK — Operación diaria

Guía para dejar el sistema corriendo en automático y para operarlo a mano si hace falta.

---

## Arquitectura

```
CLAUDE.md                            ← memoria: 5 misiones (oportunidades + inmobiliario +
                                        biohacking + mesa de proyectos + publicidad Meta)
build_dashboard.py                   ← genera dashboard.html desde los reportes
dashboard.html                       ← tablero visual (offline, doble clic)
reportes/YYYY-MM-DD.md               ← MISIÓN 1: oportunidades de negocio
reportes-inmobiliario/YYYY-MM-DD.md  ← MISIÓN 2: marketing inmobiliario
reportes-biohacking/YYYY-MM-DD.md    ← MISIÓN 3: biohacking y longevidad
proyectos/NN-slug.md                 ← MISIÓN 4: dossiers de la Mesa de Proyectos
reportes-publicidad/YYYY-MM-DD.md    ← MISIÓN 5: informe semanal de publicidad Meta
publicidad/guiones/NN-slug.md        ← MISIÓN 5: biblioteca de guiones plug-and-play
publicidad/guiones/_plantilla.md     ← plantilla del guion (los `_*` no se publican)
publicidad/metricas/                 ← MISIÓN 5: módulo de cuenta propia, APAGADO
                                        (config.json → "conectado": false)
.claude/agents/pub-*.md              ← MISIÓN 5: el equipo de agentes (CEO, anuncios,
                                        búsqueda, Chile, inmobiliario, auditor)
radar/indice-antirepeticion.txt      ← índice anti-repetición compartido (dominios:
                                        ideas · tendencias · biohacking · proyectos · publicidad)
validar_formato.py                   ← valida el contrato antes de generar
```

Las misiones 1-3 son scouts diarios (traen hallazgos sueltos). La misión 4 corre
semanal y no busca nada nuevo: fusiona lo que los scouts ya trajeron y lo aterriza
a plan de entrada, costos en CLP y timeline. La misión 5 corre semanal, después de
la 4, y sí investiga: desarma los mejores anuncios de Meta (mundo, Chile, inmobiliario)
y los convierte en guiones plug-and-play. Su equipo vive en `.claude/agents/` y lo
dirige un CEO que cruza a los equipos y pisa con registro; un auditor (`pub-auditor`)
revisa antes del commit. Ver `.claude/agents/README.md` para cambiar modelos o
convocarla a mano.

Flujo diario (08:00): generar reporte → guardar .md → `python3 build_dashboard.py`
→ commit + push. La revisión se hace en el dashboard (sin email).

Flujo semanal (domingos): 09:30 Mesa de Proyectos → 10:15 Publicidad Meta (brief →
ronda 1 en paralelo → ronda 2 de cruce → informe + guiones → auditoría → commit + push
de solo los .md y el índice anti-repetición).

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

## 2. Crear las Routines (tres diarias a las 08:00 + dos semanales los domingos)

En https://claude.ai/code/routines → **New routine**. Crear las tres diarias con:
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

### Routine 5 — Publicidad Meta (semanal, domingos)
Nombre: `Publicidad Meta · semanal`
Trigger: **Schedule → Weekly → domingo 10:15** (escalonada después de la Mesa de Proyectos).

```
Ejecuta la MISIÓN 5 definida en CLAUDE.md (Publicidad Meta — tablero de interacción y
biblioteca de guiones). Sigue el protocolo de rondas: escribe brief.md (fecha, ángulo
de la semana, lista de exclusión con el dominio `publicidad` de
radar/indice-antirepeticion.txt e INDICE_IDEAS.md pegados literal); lanza EN PARALELO
los agentes pub-anuncios, pub-busqueda, pub-chile y pub-inmobiliario con ese brief;
lanza pub-ceo para la ronda 2 de cruce y relanza SOLO a los equipos con preguntas;
lanza pub-ceo para escribir reportes-publicidad/YYYY-MM-DD.md, los guiones en
publicidad/guiones/NN-slug.md (contrato exacto de CLAUDE.md) y actualizar el índice
anti-repetición; lanza pub-auditor y, si el acta no es APROBADO, devuelve las
correcciones a pub-ceo (máximo dos vueltas). Corre `python3 validar_formato.py` y que
pase. Commit + push a main de SOLO los .md del informe y guiones y
radar/indice-antirepeticion.txt. El módulo publicidad/metricas/ está APAGADO: ninguna
cifra de cuenta propia, ninguna llamada a MCP de Meta. Si nada supera el umbral, el
resultado válido es "esta semana no hay hallazgo/guion nuevo" con el registro de qué se
evaluó. NO envíes email ni commitees dashboard.html/index.html.
```

---

## 3. Ver el dashboard

En línea: https://maolivare-max.github.io/inteligencia-negocios/ (sirve desde `main`).
También se puede abrir `dashboard.html` local con doble clic. Se regenera solo vía la
GitHub Action tras cada push a `main` que toque `reportes*/`, `proyectos/` o
`publicidad/`.

Pestañas: Panorama · Explorar · Decisiones · **Proyectos** · **Publicidad** · Reportes ·
Mi radar. La pestaña Proyectos muestra los dossiers de la Misión 4 (plan de entrada,
resumen financiero, timeline), que es contenido distinto de los hallazgos diarios. La
pestaña Publicidad muestra el informe semanal de la Misión 5 (campañas del mundo,
targeting Chile, publicidad inmobiliaria) y la biblioteca de guiones; el módulo de
métricas de la cuenta propia aparece apagado hasta que `publicidad/metricas/config.json`
diga `"conectado": true` (decisión manual del usuario, no de la rutina).

Para regenerar y validar a mano:

```bash
python3 validar_formato.py    # contrato de formato; falla si un dossier está mal
python3 build_dashboard.py    # regenera dashboard.html, index.html e INDICE_IDEAS.md
```

`validar_formato.py` distingue dos severidades: los **errores** (dossier que viola el
contrato) rompen el build; los **avisos** (drift de formato en reportes históricos) no,
pero se listan para arreglarlos. Con `--estricto` los avisos también rompen. Para la
Misión 5, además del validador, el `pub-auditor` emite un acta (contrato del guion,
cifras sin etiqueta, links, repetición, módulo apagado) que debe estar en APROBADO
antes del commit.

---

## 4. Operación manual (si una routine falla)

Pídele a Claude Code, dentro de una sesión con este repo:
> "Ejecuta el flujo de CLAUDE.md para hoy" (genera, guarda, actualiza dashboard, commit + push).

Para la Mesa de Proyectos: "convoca la mesa de proyectos". Para Publicidad Meta:
"convoca la mesa de publicidad" (opcionalmente "... con ángulo: X"). El ciclo de
rondas y cómo cambiar el modelo de cada agente están en `.claude/agents/README.md`.

---

## Notas

- El entorno de la nube es efímero: la persistencia vive en GitHub. Sin push, se pierde.
- Una Routine cuenta contra el límite diario de runs de tu plan.
- Si una fuente queda bloqueada por red, cambia el entorno de la routine a Network: Full.
