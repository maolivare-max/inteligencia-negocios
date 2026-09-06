# Equipo de agentes — Misión 5 (Publicidad Meta)

Cada archivo `.md` de esta carpeta es un subagente de Claude Code. El frontmatter YAML
define su nombre, para qué se usa, con qué modelo corre y qué herramientas tiene; el
cuerpo es su prompt. Claude Code los carga solo al abrir una sesión en este repo.

## Quién es quién

| Agente | Modelo | Rol | Entrega (en la carpeta de trabajo) |
|---|---|---|---|
| `pub-ceo` | sonnet | Orquestador. No investiga: cruza las entregas, exige segunda pasada cuando la evidencia no cierra, pisa a los equipos con registro, escribe el informe y los guiones. | `ronda2.md`, `reportes-publicidad/YYYY-MM-DD.md`, `publicidad/guiones/NN-slug.md`, `entrega.md` |
| `pub-anuncios` | sonnet | Mejores campañas del mercado, cualquier lugar y rubro, diseccionadas (hook, ángulo, oferta, prueba social, CTA, formato, mecanismo). | `anuncios.md` (fichas A-N) |
| `pub-busqueda` | sonnet | Rastrea métricas publicadas: Ad Library, casos, agencias, benchmarks, prensa. Tabla de evidencia con link, fecha, etiqueta y modo de verificación. | `busqueda.md` (filas B-N) |
| `pub-chile` | sonnet | Cómo se segmenta hoy en Chile (localización · género · intereses), benchmarks en CLP, restricciones de Meta (categorías especiales) y brecha de adopción. | `chile.md` (bloques C-N) |
| `pub-inmobiliario` | sonnet | Anuncios inmobiliarios concretos, Chile y mundo, con métrica y con el puente a lo que necesitamos. | `inmobiliario.md` (casos I-N) |
| `pub-auditor` | fable | Audita informe y guiones antes del commit: contrato, etiquetas, links, repetición, vicios del corpus, módulo de métricas apagado. Corre `validar_formato.py`. No edita. | Acta de auditoría (mensaje final) |

## Cómo cambiar el modelo de un agente

Una línea por archivo. Abre el `.md` del agente y edita el campo `model:` del
frontmatter:

```yaml
---
name: pub-anuncios
description: ...
model: sonnet      # ← valores válidos: opus · sonnet · haiku · fable
tools: ...
---
```

Configuración vigente (decisión del usuario, 2026-09-06): los cuatro equipos de
investigación y el CEO en `sonnet`; el auditor en `fable`. La separación importa más
que el modelo concreto: quien escribe y quien audita no pueden ser el mismo criterio, y
por eso el auditor se deja distinto aunque cambie el resto. Si en alguna semana el
cruce del CEO se ve pobre —contradicciones que no detecta, cifras que deja pasar— el
primer candidato a subir de vuelta a `opus` es `pub-ceo`, que es el que decide.

**OJO, esto cambió:** antes este README decía que cambiar el modelo no obliga a tocar
nada más. Es falso. La Routine de la Misión 5 tiene su PROPIO campo de modelo, que
gobierna la sesión que orquesta las rondas —no a los agentes, que sí obedecen su
frontmatter—. Si cambias el equipo acá y no cambias la Routine, la sesión del domingo
sigue corriendo con el modelo viejo. Se ajusta con `update_trigger` sobre
`trig_0157myVkPuxCAAGADmh3g4Ft`, o desde `claude.ai/code/routines`.

## Cómo se convoca la mesa

**Automático:** la Routine 5 (`Publicidad Meta · semanal`, domingos, después de la Mesa
de Proyectos) ejecuta la MISIÓN 5 de `CLAUDE.md`, que a su vez sigue el protocolo de
rondas del CEO.

**A mano:** en una sesión de Claude Code con este repo:

> "convoca la mesa de publicidad"

o, para dirigir un ángulo:

> "convoca la mesa de publicidad con ángulo: anuncios click-to-WhatsApp en LATAM"

## Cómo corre el ciclo (lo que la sesión principal ejecuta)

Un subagente no puede lanzar a otro, así que el CEO no "llama" a los equipos: define
el protocolo y la sesión principal lo ejecuta.

```
0. brief.md          sesión principal: fecha, ángulo, lista de exclusión (dominio
                     `publicidad` de radar/indice-antirepeticion.txt + INDICE_IDEAS.md)
1. Ronda 1           pub-anuncios · pub-busqueda · pub-chile · pub-inmobiliario
                     EN PARALELO, cada uno con brief.md → escriben su archivo
2. Ronda 2           pub-ceo lee los cuatro → escribe ronda2.md (preguntas cruzadas
                     por equipo). Obligatoria si hay candidato a guion sin métrica,
                     contradicción entre equipos o candidato sin veredicto de Chile.
                     La sesión principal relanza SOLO a los equipos con preguntas →
                     escriben *-r2.md
3. Ronda 3           pub-ceo escribe reportes-publicidad/YYYY-MM-DD.md, los guiones
                     publicidad/guiones/NN-slug.md, actualiza el índice anti-repetición
                     y deja entrega.md
4. Ronda 4           pub-auditor → acta. RECHAZADO / CON CORRECCIONES → pub-ceo corrige
                     solo lo señalado → nueva acta. Máximo dos vueltas.
5. Commit + push     sesión principal, solo los .md y radar/indice-antirepeticion.txt,
                     a main. Nunca dashboard.html / index.html.
```

Carpeta de trabajo por defecto: `<scratchpad>/mision5/` (la sesión principal la indica
en el prompt de cada agente). Los archivos de ronda no se commitean.

## Lo que ningún agente hace

- `git add`, `git commit`, `git push` — lo hace la sesión principal después del acta.
- Inventar cifras, hooks o links. Cifra sin etiqueta de origen es error de contrato.
- Tocar `publicidad/metricas/` o citar datos de la cuenta propia de Meta: el módulo
  está apagado (`config.json` → `"conectado": false`).
- Rellenar. "Esta semana no hay hallazgo/guion que supere el umbral" es un resultado
  válido.

## Agregar un agente nuevo

Copia el frontmatter de uno existente, cambia `name` (prefijo `pub-` para que se
reconozca como parte de esta mesa), escribe una `description` que diga cuándo usarlo y
qué entrega, y define su archivo de salida y sus códigos (A-N, B-N, C-N, I-N están
tomados). Después agrégalo a la tabla de arriba y al protocolo del CEO
(`pub-ceo.md` → "Insumos que recibes"), o el CEO no lo leerá.
