# Reporte de Publicidad Meta — semana del [D de mes de AAAA] (domingo)

> **NOTA DE FORMATO (esta plantilla no se publica; los archivos que empiezan con `_` quedan fuera del dashboard).**
> El parser de hallazgos toma cada `## N. Nombre — Score X/20` y lee su cuerpo **hasta el siguiente `##`**.
> Por eso: las seis secciones del informe van con `##` (sin número, para no confundirlas con hallazgos),
> cada hallazgo va con `## N. Nombre — Score X/20`, y **todo sub-bloque que no sea hallazgo va con `###`,
> nunca con `##`** (tablas de targeting, notas, seguimientos, descartes). Un `##` de más dentro de un
> hallazgo lo trunca en silencio: el dashboard lo muestra sin Confianza, sin evidencia y sin pasos, y nadie
> avisa. Detalles del formato exigido:
> - Raya EM `—` (no guion `-` ni en-dash `–`) entre el nombre y `Score`, y score **entero** (`14/20`, no `14.5/20`).
> - Confianza: negrita solo en la etiqueta `Confianza:` (dos puntos incluidos) y el valor fuera de la negrita. Si los dos puntos quedan dentro de la negrita, el parser no la reconoce y el hallazgo sale como no verificado.
> - Fuente: la línea `Dónde lo encontré:` lleva los links en formato `[texto](url)` **en la misma línea**; una lista de URLs crudas debajo deja el hallazgo sin evidencia.
> - Encabezado: `Fuentes revisadas:` y `Resumen:` en negrita, con esos nombres. Una línea llamada `Ángulo del día` no cuenta como resumen.
> - La numeración `N.` de los hallazgos es **correlativa en todo el informe** (sigue de una sección a la otra), no reinicia por sección.
> - Toda cifra de CPL / CTR / ROAS lleva etiqueta: `[verificado]` / `[verificado sin link]` / `[estimado]` / `[desconocido]`.
> Borrar este bloque al crear el informe real.

**Fuentes revisadas:** [N] ([desglose breve: búsquedas vía WebSearch, Meta Ad Library, casos publicados, reportes del repo cruzados]). Ángulo de la semana: [cuál]. Cruzado contra `radar/indice-antirepeticion.txt` (dominio `publicidad`) y contra el informe anterior `reportes-publicidad/[AAAA-MM-DD].md`.

**Resumen:** [Una sola línea: qué cambió esta semana en publicidad Meta que valga la pena para alguien que va a poner plata el lunes.]

---

## Mejores campañas del mundo

[Una línea de contexto: qué se barrió (rubros, países, fuentes) y qué criterio dejó fuera al resto. Los hallazgos de esta sección son campañas de cualquier rubro con métrica o caso documentado.]

## 1. [Nombre del hallazgo: el mecanismo, no la marca] — Score 14/20
*(Leads 4 · Facilidad 4 · Costo-eficiencia 3 · Innovación 3)*

**Qué es:** [1-2 frases. Qué hace la campaña o el anuncio, en qué formato, para quién.]

**Por qué funciona:** [Mecanismo + evidencia con cifras y etiqueta. Ej.: "CTR X % [verificado] y CPL USD X [verificado sin link] según el caso publicado por (fuente); hook rate [desconocido]". Sin cifra etiquetada, esta línea no vale.]

**En Chile:** [Cómo se replica en el mercado chileno, qué rubro local calza, qué adaptación cultural o regulatoria requiere, y qué brecha hay (¿alguien ya lo hace en Chile? ¿con qué resultado?). Si el CPL de referencia es de otro mercado: "estimado, sin caso chileno medido".]

**Dónde lo encontré:** [Nombre de la fuente](https://url-de-la-fuente) · [Meta Ad Library, anuncio activo desde AAAA-MM-DD](https://www.facebook.com/ads/library/?id=XXXXXXXX)

**Confianza:** [Alta / Media / Baja] — [por qué: fuente primaria vs. snippet, cifra de la plataforma vs. auditada por tercero].

**Pasos esta semana:**
1. [Acción concreta adaptada a Chile: qué anuncio se produce, para qué rubro, con qué presupuesto en CLP.]
2. [Acción concreta: targeting, formato, canal de respuesta.]
3. Métrica a 30 días: [KPI con umbral numérico, ej. "CPL ≤ CLP X con al menos 20 leads"].

### Guion derivado

[Solo si se produjo un guion a partir de este hallazgo: ruta `publicidad/guiones/NN-slug.md`. Si no, borrar este sub-bloque. Es `###` porque está dentro del hallazgo.]

## 2. [Segundo hallazgo de campañas del mundo] — Score [X]/20
*(Leads X · Facilidad X · Costo-eficiencia X · Innovación X)*

**Qué es:** [...]

**Por qué funciona:** [... cifra [etiqueta] ...]

**En Chile:** [...]

**Dónde lo encontré:** [Fuente](https://url)

**Confianza:** [Alta / Media / Baja]

**Pasos esta semana:**
1. [...]
2. [...]
3. Métrica a 30 días: [...]

---

## Targeting Chile

[Localización · género · intereses. Qué se aprendió esta semana sobre a quién y dónde apuntar en Chile: cambios en la plataforma (nuevas audiencias, restricciones, categorías especiales), señales de demanda (Google Trends geo=CL), benchmarks de CPL por segmento. Si un aprendizaje tiene tracción documentada y aplica como táctica, va como hallazgo numerado; si es contexto, va en `###`.]

### Tabla de targeting de la semana

[Solo filas con evidencia. La fila separadora `|---|---|` es obligatoria.]

| Segmento (localización · género · intereses) | Rubro | CPL de referencia | Origen |
|---|---|---|---|
| [Comuna o radio · género · interés] | [rubro] | [cifra CLP o USD] [etiqueta] | [ruta del corpus o link] |

## 3. [Hallazgo de targeting, si lo hay] — Score [X]/20
*(Leads X · Facilidad X · Costo-eficiencia X · Innovación X)*

**Qué es:** [...]

**Por qué funciona:** [... cifra [etiqueta] ...]

**En Chile:** [...]

**Dónde lo encontré:** [Fuente](https://url)

**Confianza:** [Alta / Media / Baja]

**Pasos esta semana:**
1. [...]
2. [...]
3. Métrica a 30 días: [...]

---

## Publicidad inmobiliaria

[Chile y mundo. Campañas y tácticas de anuncios en Meta específicas del rubro inmobiliario. Esta sección vive dentro de la Misión 5 y NO toca `reportes-inmobiliario/`: antes de reportar, cruzar contra el dominio `tendencias` del índice para no repetir lo que la Misión 2 ya indexó; si hay novedad real sobre algo ya indexado, marcarlo "Actualización" en el nombre.]

## 4. [Hallazgo inmobiliario] — Score [X]/20
*(Leads X · Facilidad X · Costo-eficiencia X · Innovación X)*

**Qué es:** [...]

**Por qué funciona:** [... cifra [etiqueta] ...]

**En Chile:** [Corredor o inmobiliaria chica: cómo lo implementa con presupuesto en CLP. Si hay caso chileno con datos, decir de quién y marcar si la cifra es de la plataforma (autorreportada) o auditada.]

**Dónde lo encontré:** [Fuente](https://url)

**Confianza:** [Alta / Media / Baja]

**Pasos esta semana:**
1. [...]
2. [...]
3. Métrica a 30 días: [...]

### Contexto inmobiliario (no puntuable)

[Datos de mercado, cambios de plataforma o señales que no son táctica con métrica y por eso no van como hallazgo. `###`, nunca `##`.]

---

## Guiones producidos esta semana

[Un ítem por guion nuevo o actualizado en `publicidad/guiones/`, con ruta, tipo y de qué hallazgo sale. Si no se produjo ninguno, decirlo: "Sin guiones nuevos esta semana" y por qué.]

- `publicidad/guiones/NN-slug.md` — [Tipo: Hook / Ángulo / Oferta / Formato / Secuencia] — derivado del hallazgo [N] de este informe. Estado: Borrador.
- `publicidad/guiones/NN-slug.md` — [Tipo] — **Actualización**: [qué cambió y por qué].

### Índice anti-repetición

[Líneas agregadas esta semana a `radar/indice-antirepeticion.txt` bajo el dominio `publicidad`, para que quede rastro en el propio informe.]

---

## Cierre

### Evaluado y descartado

- **[Nombre]:** [por qué se descarta: sin métrica, ya indexado en `tendencias`/`ideas`, claim regulado sin reformulación, no aplica a Chile]. Documentar el descarte evita redescubrirlo en tres semanas.

### Tendencias de fondo

[1-2 tendencias que se vieron esta semana en publicidad Meta, Chile vs. mundo. Sin adjetivos de venta.]

### Ángulo para la próxima semana

[2-3 fuentes o ángulos nuevos para no estancarse: rubros no barridos, países, formatos, cambios de plataforma anunciados con fecha.]
