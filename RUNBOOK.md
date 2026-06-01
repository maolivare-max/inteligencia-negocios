# RUNBOOK — Operación diaria

Guía para dejar el sistema corriendo en automático y para operarlo a mano si hace falta.

---

## Arquitectura

```
CLAUDE.md                            ← memoria: 2 misiones (oportunidades + inmobiliario)
build_dashboard.py                   ← genera dashboard.html desde los reportes
dashboard.html                       ← tablero visual (offline, doble clic)
reportes/YYYY-MM-DD.md               ← MISIÓN 1: oportunidades de negocio
reportes-inmobiliario/YYYY-MM-DD.md  ← MISIÓN 2: marketing inmobiliario
```

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

## 2. Crear las dos Routines (entrega automática 08:00)

En https://claude.ai/code/routines → **New routine**. Crear DOS, ambas con:
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

---

## 3. Ver el dashboard

Abre `dashboard.html` en el navegador (doble clic). Se regenera solo tras cada reporte.
Para regenerarlo a mano:

```bash
python3 build_dashboard.py
```

---

## 4. Operación manual (si una routine falla)

Pídele a Claude Code, dentro de una sesión con este repo:
> "Ejecuta el flujo de CLAUDE.md para hoy" (genera, guarda, actualiza dashboard, commit + push).

---

## Notas

- El entorno de la nube es efímero: la persistencia vive en GitHub. Sin push, se pierde.
- Una Routine cuenta contra el límite diario de runs de tu plan.
- Si una fuente queda bloqueada por red, cambia el entorno de la routine a Network: Full.
