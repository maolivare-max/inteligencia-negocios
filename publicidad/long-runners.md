# Long-runners — registro de anuncios de larga corrida (Ad Library)

Ver `CLAUDE.md`, sección MISIÓN 5 → "TIER DE LONGEVIDAD (AD LIBRARY)", para la definición de los
tiers y la regla de publicación. Este archivo es el registro persistente de los patrones evaluados
por tiempo activo en la Biblioteca de Anuncios de Meta — no es un informe semanal ni un guion, así
que no lo lee `build_dashboard.py` ni lo valida `validar_formato.py`; es memoria de trabajo para que
el equipo `pub-anuncios`/`pub-busqueda` no vuelva a levantar desde cero un patrón ya evaluado, y para
que el CEO pueda citar "ya lo vimos, seguía corriendo a la fecha X" en vez de re-consultar la Ad
Library cada semana.

No confundir con `radar/indice-antirepeticion.txt` (dominio `publicidad`): ese índice es por
concepto/hallazgo ya publicado; este archivo es la evidencia cruda de longevidad que sostiene (o no)
la publicación de un hallazgo.

## Cómo se llena

Una fila por patrón/mecánica evaluado, con la fecha de consulta explícita (la longevidad cambia cada
semana, así que una fila sin fecha de consulta queda obsoleta sin que nadie lo note). Si el patrón no
alcanzó el tier mínimo para publicarse como hallazgo, se registra igual — es lo que evita que
`pub-anuncios` lo vuelva a levantar como "nuevo" en unas semanas cuando siga sin alcanzar el umbral.

| Anunciante(s) | Copy / mecánica | Inicio observado | Días activos | Variantes | Tier | Consultado | ¿Publicado como hallazgo? |
|---|---|---|---|---|---|---|---|
| Dr. Squatch | "a laundry list of chemical products" — reencuadre de categoría contra jabón de supermercado | no declarado (solo días activos) | 1.390 [verificado] | 2 (pieza principal + segunda de la cuenta, 552 días) | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 1 |
| MUD\WTR | "It's not coffee or tea — it's better" — niega la categoría | no declarado | 367 [verificado] | 2 piezas sosteniendo esa duración | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 1 |
| GORUCK | Explica por qué caminar con peso, no cuánto ahorras (sin descuento en toda la cuenta) | no declarado | >180 (33 de 155 anuncios de la cuenta sobre ese umbral) [verificado] | 33 de 155 anuncios totales | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 1 |
| Rose Rock Orthodontics | "Ask about our $99 New Patient Special!" — ancla de precio | no declarado | 8,3 años ≈ 3.030 días [verificado] | 1 | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 2 / guion 02 |
| Guru Dental Group | Ancla de precio, misma familia de Rose Rock | no declarado | 5,4 años ≈ 1.971 días [verificado] | 1 | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 2 / guion 02 |
| The Smilist | Ancla de precio, misma familia de Rose Rock | no declarado | 4,7 años ≈ 1.716 días [verificado] | 1 | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 2 / guion 02 |
| Global International | Ruta de autodiagnóstico ("$59 A/C Tuneup") | no declarado | 1.500+ [verificado] | 1 | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 2 / guion 02 |
| (sin nombre de anunciante — climatización/techos) | "Leaky Roof?" — autodiagnóstico en dos palabras | no declarado | 900+ [verificado] | 1 | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 2 / guion 02 |
| Cobex Construction | "SACRAMENTO HOMEOWNERS" — llamado demográfico/geográfico | no declarado | 770+ [verificado] | 1 | `tier_90_mas` | 2026-09-06 | No en el informe (solo en guion 02, sección 1) |
| DiPietro Law Group | Pregunta sobre la vida del lector, no credencial | no declarado | 6,4 años ≈ 2.336 días [verificado] | 1 | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 2 / guion 02 |
| Amanda Howard Sotheby's | "Do you know the REAL value of your home?" — contraste contra Zillow | dic-2024 | 575+ [verificado] | 1 | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 6 / guion 01 |
| Teresa Robertson (Keller Williams) | "free, no-obligation Home Value report" — miedo neutralizado | no declarado | 440+ [verificado] | 1 | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 6 / guion 01 |
| Jordan Myers (eXp) | "your home might be worth more than you think" — afirmación atenuada | no declarado | 150+ [verificado] | 1 | `tier_90_mas` | 2026-09-06 | Sí — hallazgo 6 / guion 01 |
| Coldwell Banker OnTrack | "in today's market" — caduca la tasación vieja | no declarado | 75+ [verificado] | 1 | `tier_60_89` | 2026-09-06 | Sí — hallazgo 6 / guion 01 |
| HexClad (contraejemplo, NO es long-runner) | Reposición industrial, sin evergreen | no declarado | 97% de sus 300 anuncios lanzados en los últimos 90 días (147 solo en abril) [verificado] | 300 (rotación alta, no una pieza sostenida) | no aplica — es el contraejemplo del patrón, no un long-runner | 2026-09-06 | Sí — hallazgo 1, como contraejemplo |

**Fuente de las 15 filas:** `reportes-publicidad/2026-09-06.md` (hallazgos 1, 2 y 6) y
`publicidad/guiones/{01-tasacion-cifra-de-referencia,02-puerta-de-entrada-barata}.md` (sección 1,
"Anatomía del original"). Todas las cifras de días activos llevan `[verificado]` en la fuente
original (runtime público de la Biblioteca de Anuncios o de los censos de terceros citados en esos
hallazgos); ninguna es `[estimado]` ni `[desconocido]`. Sembrado 2026-09-07 en la vuelta 1 de
auditoría de la taxonomía (MENOR-2 del acta), para que `pub-anuncios` no vuelva a levantar estos
anunciantes como "nuevo hallazgo" sin revisar primero esta tabla.
