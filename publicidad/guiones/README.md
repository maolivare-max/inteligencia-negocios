# Biblioteca de guiones — Misión 5 (Publicidad Meta)

## Qué es

Una colección de **guiones genéricos plug-and-play** para anuncios en Meta (Facebook e
Instagram). Cada archivo captura un mecanismo publicitario que ya demostró funcionar
en algún mercado —un hook, un ángulo, una oferta, un formato o una secuencia— y lo
reescribe como plantilla neutra con variables entre llaves, para que se pueda rellenar
para cualquier rubro sin volver a pensar el anuncio desde cero.

La biblioteca no es un archivo de anuncios ajenos: es la destilación de lo que el
informe semanal (`reportes-publicidad/AAAA-MM-DD.md`) detecta como mejor campaña, ya
convertido en algo que se puede producir el lunes.

Qué entra:
- Mecanismos con métrica o caso documentado en su origen.
- Guiones que sobreviven al cambio de rubro (si solo funciona para la marca original,
  no es un guion, es una anécdota).

Qué no entra:
- Copias literales de un anuncio ajeno.
- Guiones cuyo gancho es un claim regulado (rentabilidad garantizada, salud, crédito)
  sin reformulación.

## Cómo se numera

- Cada guion vive en `publicidad/guiones/NN-slug.md`.
- `NN` es un **correlativo de dos dígitos** (`01-`, `02-`, ... `10-`, `11-`), asignado
  por orden de creación. Para saber el siguiente, listar la carpeta y sumar uno al
  mayor. Un número nunca se reutiliza, aunque el guion se archive.
- `slug` va en minúsculas, sin tildes, palabras separadas por guion, y describe el
  mecanismo, no la marca de origen (`03-hook-objecion-anticipada.md`, no
  `03-anuncio-de-marca-x.md`).
- Los archivos que empiezan con `_` (como `_plantilla.md`) **no se publican en el
  dashboard**. Sirven para plantillas y borradores de trabajo. Cuando un guion está
  listo, se renombra al siguiente `NN-`.

## Contrato de formato

Copiar `_plantilla.md` y rellenar. El parser del dashboard depende de esta estructura
exacta; `python3 validar_formato.py` tiene que pasar antes de commitear.

```
# [Nombre del guion]

> **Estado:** Borrador | Validado | En uso | Archivado
> **Tipo:** Hook | Ángulo | Oferta | Formato | Secuencia
> **Origen:** [marca/anunciante — país — dónde se vio + fecha]
> **Métrica de referencia:** [cifra + [verificado]/[verificado sin link]/[estimado]/[desconocido]]
> **Tesis:** una sola frase de por qué funciona.

## 1. Anatomía del original
## 2. Guion adaptable
## 3. Variables a rellenar
## 4. Targeting Chile
## 5. Producción
## 6. Medición
## 7. Trazabilidad
```

Reglas duras:
- El título es la **única** línea que empieza con un solo `# `.
- Las 5 líneas `>` son obligatorias, en ese orden y con esos nombres exactos.
- Las 7 secciones `##` van numeradas, con esos nombres exactos, en ese orden. Ninguna
  puede quedar vacía. Los subtítulos internos van con `###`: un `##` de más corta la
  sección y el resto del contenido se pierde sin aviso.
- La sección 3 trae una tabla markdown con su fila separadora `|---|---|` y las seis
  variables `{oferta}`, `{publico}`, `{ciudad}`, `{ticket}`, `{prueba_social}`, `{cta}`.
  Una fila de tabla sin separador debajo cuelga el conversor markdown del dashboard.
- La sección 6 declara al menos un KPI con umbral numérico.
- La sección 7 cita al menos un `reportes-publicidad/AAAA-MM-DD.md` con fecha real.

### Ciclo de vida del campo Estado

- **Borrador:** recién extraído del informe semanal, sin producir.
- **Validado:** producido y testeado con gasto propio; la sección 6 tiene cifras reales.
- **En uso:** corriendo en una campaña activa.
- **Archivado:** dejó de funcionar o el mecanismo quedó obsoleto. Se conserva con su
  número para que el scout no lo redescubra.

## Regla de etiquetas de origen (obligatoria en toda cifra)

Toda cifra de **CPL, CTR, ROAS, hook rate, alcance o costo** que aparezca en un guion
lleva una de estas cuatro etiquetas, pegada a la cifra:

| Etiqueta | Cuándo se usa |
|---|---|
| `[verificado]` | Cifra pública o medida en cuenta propia, **y el link o la ruta va en la sección 7** |
| `[verificado sin link]` | Se consultó la fuente pero no quedó registrada la URL: sirve para decidir, no para comprometer gasto sin reconfirmar |
| `[estimado]` | Extrapolación; se dice de qué (otro mercado, otro rubro, regla general). Si viene de fuera de Chile, agregar "sin caso chileno medido" |
| `[desconocido]` | No se pudo obtener. Se dice, no se inventa |

**Cifra sin etiqueta = error de contrato.** Un benchmark de otro país presentado como
si fuera chileno es exactamente el error que esta biblioteca existe para no cometer.
Vale también para los números que entran por `{ticket}` y `{prueba_social}`.

## Un guion NO es un hallazgo

Los informes de las Misiones 1, 2, 3 y 5 indexan hallazgos con el patrón
`## N. Nombre — Score X/20`. Ese regex dispara el parser de hallazgos del dashboard,
que los mete en Explorar, Decisiones e `INDICE_IDEAS.md`.

Un guion no tiene score /20 ni veredicto Chile: es una pieza de producción, no una
oportunidad. Por eso está **prohibido el patrón `— Score X/20` en cualquier encabezado
`##` dentro de `publicidad/`**. Si un guion lo usa, el dashboard lo confunde con un
hallazgo y el contrato se rompe en ambos lados.

## Relación con el informe semanal y el índice anti-repetición

- La sección 5 del informe semanal ("Guiones producidos esta semana") enlaza cada
  guion nuevo o actualizado por su ruta `publicidad/guiones/NN-slug.md`.
- Cada guion nuevo se agrega a `radar/indice-antirepeticion.txt` bajo el dominio
  `publicidad`, respetando el formato del archivo (una línea, campos separados por `|`,
  sin encabezado nuevo):

  ```
  publicidad|<slug del archivo>|<nombre, máx. ~70 caracteres>|<veredicto_chile>|<accion>|<nivel>|<prioridad>
  ```

  Los vocabularios de `veredicto_chile` (`APLICA`, `APLICA_CON_AJUSTES`,
  `NO_APLICA_AUN`), `nivel` (`N1`-`N5`) y `prioridad` (`P1`-`P5`) son los que ya usa el
  archivo. Para `accion` usar el vocabulario de `tendencias` (`ADOPTAR_YA`, `PILOTEAR`,
  `OBSERVAR`, `DESCARTAR`), que es el más cercano a "producir o no este guion". Sin
  esta línea, el scout redescubre el guion en tres semanas.
