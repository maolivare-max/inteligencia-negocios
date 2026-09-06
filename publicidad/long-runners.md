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

*(Sin filas todavía — este archivo se crea como scaffolding del tier de longevidad (ver CLAUDE.md,
MISIÓN 5); la primera corrida de la misión que evalúe longevidad de Ad Library agrega sus filas
acá.)*
