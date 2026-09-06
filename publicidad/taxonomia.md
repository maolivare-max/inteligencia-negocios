# Taxonomía de creativos (Misión 5)

> **Fuente:** [motion-team/creative-strategy-skills](https://github.com/motion-team/creative-strategy-skills),
> commit `8e467a3` (2026-06-11). **Licencia:** MIT (Copyright (c) 2026 Motion Creative Strategy Team —
> texto completo de la licencia en el repo de origen). El aviso de copyright se mantiene con esta
> atribución, conforme exige la licencia.
>
> Este archivo existe para que `validar_formato.py` pueda comprobar que la línea
> `· **Etiquetas:**` de cada hallazgo y cada guion usa valores de un vocabulario cerrado, en vez de
> texto libre — eso es lo que permite después buscar "todos los hooks de contraste" o detectar que
> tres hallazgos distintos usan el mismo mecanismo. Ver la regla de mejora en `CLAUDE.md`, sección
> MISIÓN 5.

## Nota de adaptación (léase antes de usar)

Esto **no es una copia literal** del repo de Motion. Se hicieron los siguientes cambios explícitos:

- **Traducción al español** de los 79 nombres y definiciones de las dos listas fuente (33 tácticas
  de hook + 46 formatos visuales). La traducción es una paráfrasis fiel del "What it is" de cada
  entrada, no una traducción palabra por palabra.
- **Conteo real vs. anunciado:** el `SKILL.md` de `hook-tactics` se autodescribe como "35+ tácticas"
  pero solo **define 33** en detalle — se listan esas 33, no 35. El de `visual-formats` se
  autodescribe como "45+" y en efecto **define 46** — se listan las 46.
- **snake_case propio:** los nombres cortos (`hook_*`, `formato_*`) son una convención nuestra para
  usarlos como etiqueta de texto; no existen así en el original (que usa Title Case en inglés).
- **Eje "Etapa de conciencia":** viene de `creative-strategy-engine/SKILL.md`, que a su vez cita el
  marco clásico de 5 etapas de Eugene Schwartz (no es una invención de Motion, Motion lo reusa).
  Se tradujeron las 5 etapas.
- **Eje "Tipo de oferta" — NO viene de Motion.** El repo de Motion no publica una lista de tipos de
  oferta; lo único que menciona el tema es la táctica de hook "Offer Only" (una entrada, no una
  taxonomía completa). El esquema de 8 ejes con "oferta" que cita el informe de mejoras viene de una
  **reseña de tercero** sobre el producto pago de Motion (adlibrary.com), no del repo MIT, y esa
  reseña no publica el vocabulario. Para no inventar una lista y presentarla como si fuera de Motion,
  se agregó acá una lista corta y explícitamente propia (6 valores) — es la única sección de este
  archivo que no tiene respaldo en el repo fuente.
- **No se adoptó** el eje "psychological triggers" (los "triggers" que Motion separa de las
  tácticas — Pattern Interrupt, Curiosity Gap, Social Proof/Credibility, etc. — ver
  `hook-tactics/SKILL.md`, sección "How Tactics Relate to Psychological Triggers"). Cada tabla de
  tácticas de hook, abajo, incluye el trigger que el original le empareja como referencia dentro de
  la columna "Explicación", pero no se creó un eje `trigger_*` separado: el informe de mejoras solo
  pidió táctica + formato + conciencia + oferta, y agregar un quinto eje encima de eso es exactamente
  el tipo de sobre-etiquetado que la sección "Lo que NO nos sirve" del informe descarta (8-15
  etiquetas por creativo es ruido con 8 hallazgos/semana).
- **No se adoptaron** los otros módulos del repo (`creative-mechanics`, `hook-voice-patterns`,
  `hook-writing`, `brand-intake`, `review-audit`): son guías de redacción/proceso, no listas
  cerradas de valores, así que no hay nada que copiar a un vocabulario de etiquetas.

## Cómo se usa

Cada hallazgo (`reportes-publicidad/AAAA-MM-DD.md`) y cada guion
(`publicidad/guiones/NN-slug.md`) trae una línea `· **Etiquetas:**` con el formato:

```
· **Etiquetas:** táctica={hook_xxx} · formato={formato_xxx} · conciencia={conciencia_N_xxx} · oferta={oferta_xxx}
```

- Un hallazgo o guion puede traer **más de un valor por eje** separados por coma, cuando el creativo
  combina tácticas o formatos (ej. `táctica={hook_contraste, hook_ancla_precio}`) — es exactamente el
  caso que el informe de mejoras señala del guion 01 (a la vez Price Anchor, Contrast y Native Text
  Overlay).
- Si un eje no aplica o no se pudo determinar, se escribe `sin_dato` en vez de omitir el eje —
  omitirlo se lee como "no revisado", `sin_dato` se lee como "revisado, no aplica o no se pudo
  determinar".
- Los valores válidos son los de la columna **Etiqueta** de las tablas de abajo, tal cual (snake_case,
  sin acentos).

---

## Eje 1 — Táctica de hook (33 valores)

Qué frase o encuadre abre el anuncio. Es "el qué", no "el cómo" (eso sería el trigger psicológico,
no adoptado como eje — ver nota de adaptación).

| Etiqueta | Original (Motion) | Explicación |
|---|---|---|
| `hook_aspiracional` | Aspirational | Apela a la identidad, estilo de vida o estatus que el espectador quiere ser, no a lo que ya es. |
| `hook_autoridad` | Authority | Genera credibilidad citando expertise, credenciales, certificaciones o respaldo institucional. |
| `hook_creencia` | Belief | Abre con la postura, misión o valores de la marca; la marca toma partido (no el del cliente — eso es Aspiracional). |
| `hook_promesa_extrema` | Bold Claim | Hace una promesa desmedida o superlativa y toma una posición categórica. |
| `hook_llamado_directo` | Call To Action First | Abre con una instrucción explícita de compra o acción, sin preámbulo. |
| `hook_desafio` | Challenge | Invita al espectador a probar, intentar o demostrar algo, en clave competitiva. |
| `hook_confesion` | Confession | Una admisión honesta y vulnerable (de la marca o una persona) que genera credibilidad. |
| `hook_contraste` | Contrast | Yuxtapone dos cosas (productos, costos, resultados) para exponer un desajuste o superioridad clara. |
| `hook_contrarian` | Contrarian | Va deliberadamente contra la sabiduría convencional o el consejo esperado (rompe una creencia, no solo compara). |
| `hook_curiosidad` | Curiosity | Abre un ciclo o intriga que el espectador necesita cerrar. |
| `hook_llamado_demografico` | Demographic Callout | Nombra directamente a un segmento de audiencia para que se autoseleccione. |
| `hook_direccion_directa` | Direct Address | Habla directa y personalmente al espectador, generando intimidad inmediata. |
| `hook_directiva` | Directive | Un imperativo que instruye a cambiar un comportamiento, hábito o forma de pensar (no una compra inmediata — eso es Llamado directo). |
| `hook_exclusividad` | Exclusivity | Señala que el acceso es selectivo o limitado, generando deseo por escasez de acceso. |
| `hook_explicador` | Explainer | Explica la razón detrás de algo con un enfoque de "por qué", educando sobre una causa o mecanismo. |
| `hook_fomo` | FOMO | Genera ansiedad por quedar fuera de una tendencia o momento social; es pertenencia, no presión de tiempo. |
| `hook_como_hacer` | How To | Promesa instructiva que enseña a lograr una tarea específica o resolver un problema puntual. |
| `hook_si_entonces` | If Then | Califica al espectador con una condición y luego entrega una promesa o acción. |
| `hook_lista_numerada` | Listicle | Enmarca la información en una lista numerada o con viñetas, sin usar la frase "razones por las que". |
| `hook_desmentido_mito` | Myth Busting | Desmiente directamente una idea errónea muy extendida, corrigiendo con hechos. |
| `hook_solo_oferta` | Offer Only | Usa un descuento o incentivo monetario como único gancho, sin urgencia ni exclusividad. |
| `hook_ancla_precio` | Price Anchor | Enmarca el costo contra una referencia familiar para que el precio se sienta más pequeño. |
| `hook_pregunta` | Question | Abre con un problema, desafío o intriga planteado en forma de pregunta. |
| `hook_razones_por_que` | Reasons Why | Abre con un número específico + la frase "razones por las que", con justificación estructurada. |
| `hook_identificacion` | Relatability | Se ancla en una escena cotidiana compartida que la audiencia reconoce de inmediato. |
| `hook_psicologia_inversa` | Reverse Psychology | Le dice al espectador que NO actúe, para gatillar el impulso de hacer lo contrario. |
| `hook_reversion_riesgo` | Risk Reversal | Reduce el riesgo percibido de comprar con garantías o redes de seguridad. |
| `hook_declaracion_shock` | Shocking Statement | Abre con una afirmación sorprendente o contraintuitiva que desafía los supuestos del espectador. |
| `hook_prueba_social` | Social Proof | Usa reseñas, testimonios o señales de popularidad para generar confianza por volumen o consenso. |
| `hook_estadistica` | Statistic | Usa evidencia cuantificada (estudios, encuestas, resultados) para establecer credibilidad o impacto. |
| `hook_narrativa` | Storytelling | Entra a mitad de una historia personal o de marca, generando tracción narrativa inmediata. |
| `hook_urgencia` | Urgency | Crea presión de tiempo o de stock para forzar una decisión ahora. |
| `hook_advertencia` | Warning | Emite una advertencia sincera que detiene el comportamiento por defecto del espectador hasta explicar por qué debería parar. |

---

## Eje 2 — Formato visual (46 valores)

Qué aspecto tiene y cómo está producido el anuncio. Es el vehículo, no el mensaje.

| Etiqueta | Original (Motion) | Medio | Explicación |
|---|---|---|---|
| `formato_animacion_ia` | AI Slop Animation | Video o estático | Imagen o video animado generado por IA para lograr un visual imposible o muy caro de filmar. |
| `formato_asmr` | ASMR | Solo video | Formato sensorial donde el sonido amplificado del producto (verter, crujir, tocar) es el gancho principal. |
| `formato_antes_despues` | Before and After | Video o estático | Contraste secuencial o lado a lado entre el estado "antes/problema" y "después/solución", mostrado explícitamente. |
| `formato_detras_camaras` | Behind the Scenes | Solo video | Acceso interno a cómo opera la marca (personal, producción, despacho); el gancho es la transparencia. |
| `formato_valla` | Billboard | Solo estático | La pieza se estiliza como un anuncio de vía pública (valla, paradero, letrero). |
| `formato_caso_estudio` | Case Study | Solo estático | Narrativa basada en datos sobre uno o más resultados de clientes, con métricas o gráficos. |
| `formato_chatgpt` | ChatGPT | Solo estático | Captura o maqueta de una conversación dentro de la interfaz de ChatGPT. |
| `formato_broll_cinematico` | Cinematic B-Roll | Solo video | Tomas de apoyo pulidas y de alta producción; el gancho es estético y aspiracional. |
| `formato_respuesta_comentario` | Comment Response | Video o estático | El creador responde en cámara a un comentario social mostrado en pantalla, con la función nativa de respuesta. |
| `formato_demo` | Demo | Solo video | Muestra directa del producto en uso real para demostrar función o desempeño. |
| `formato_experto_explica` | Expert Explainer | Solo video | Una figura de autoridad (médico, entrenador, científico) entrega contenido instructivo o educativo. |
| `formato_callout_beneficios` | Feature Benefit Callout | Solo estático | Flechas, etiquetas o textos que destacan dos o más características/beneficios sobre la imagen del producto. |
| `formato_fundador` | Founder | Solo video | El fundador o líder de la marca habla directamente sobre la marca, la misión o el producto. |
| `formato_pantalla_verde` | Greenscreen | Solo video | Una persona recortada y compuesta sobre un fondo distinto (captura de pantalla, sitio web, video). |
| `formato_grilla` | Grid Swap | Video o estático | Grilla estructurada de celdas donde escenas, textos o imágenes se alternan en casillas fijas. |
| `formato_tutorial` | How-To | Solo video | Formato instructivo paso a paso que enseña a usar, hacer o preparar algo con el producto. |
| `formato_carta` | Letter | Solo estático | Nota larga manuscrita o escrita dirigida al espectador; imita una carta personal. |
| `formato_lista` | Listicle | Video o estático | Lista con viñetas, numerada o secuenciada de características, afirmaciones o tips. |
| `formato_meme` | Meme | Video o estático | Adopta una plantilla de meme evergreen y reconocible (no ligada a una tendencia del momento). |
| `formato_texto_nativo` | Native Text Overlay | Solo estático | Foto casual de cliente o creador (no de estudio) con texto superpuesto de estilo nativo como gancho. |
| `formato_nostalgia` | Nostalgia | Video o estático | Referencia o imita épocas culturales pasadas (90s, Y2K) para evocar sentimentalismo. |
| `formato_notas` | Notes App | Solo estático | Captura de pantalla de texto dentro de la app Notas de Apple, imitando su interfaz. |
| `formato_plano_unico` | One Shot | Solo video | Un solo clip ininterrumpido, usualmente de menos de 10 segundos, con texto superpuesto conectado a lo visual. |
| `formato_interrupcion_patron` | Pattern Interrupt | Video o estático | Imagen o video surreal, chocante o inesperado diseñado para detener el scroll. |
| `formato_podcast` | Podcast | Solo video | Formato de entrevista o conversación con dos o más hablantes, escenificado y estructurado. |
| `formato_post_it` | Post It | Video o estático | Texto o mensaje escrito en una nota adhesiva mostrada a cámara; el gancho es lo informal y manuscrito. |
| `formato_prensa` | Press | Solo estático | Validación de medios de terceros: logos, titulares o citas de medios reconocidos. |
| `formato_reaccion` | Reaction | Solo video | Captura la primera impresión auténtica (visual o verbal) de alguien ante el producto o resultado. |
| `formato_resena` | Review | Solo estático | Una o más reseñas reales de clientes como elemento creativo central; debe mostrar el texto real de la reseña. |
| `formato_selfie` | Selfie | Solo estático | Imagen informal estilo selfie donde el creador es el foco (a pulso, espejo, o cámara frontal). |
| `formato_cartel` | Sign | Video o estático | Una persona sostiene o aparece con un cartel, afiche o pizarra con la propuesta o el llamado a la acción. |
| `formato_sketch` | Skit | Solo video | Escena guionizada y actuada, con personajes y diálogo, estructurada como mini-historia con planteamiento y desenlace. |
| `formato_mashup_prueba_social` | Social Proof Mashup | Solo video | Compilación de varios testimonios UGC o nativos en una sola pieza; el gancho es el volumen y variedad de voces. |
| `formato_pantalla_dividida` | Split Screen | Solo video | Video dividido de forma limpia entre un lado en video y otro con texto o gráfico. |
| `formato_estadistica` | Statistic | Solo estático | Una cifra o dato numérico independiente como foco central de la pieza ("97% de satisfacción"). |
| `formato_entrevista_calle` | Street Interview | Solo video | Formato tipo vox-pop: alguien entrevista y otra persona responde en un espacio público. |
| `formato_testimonio` | Testimonial | Solo video | Un cliente comparte su experiencia personal con el producto, en primera persona, a cámara o en off. |
| `formato_mensaje_texto` | Text Message | Solo estático | Maqueta estilo mensaje de texto o chat, con apariencia de mensajería privada. |
| `formato_timelapse` | Time Lapse | Solo video | Metraje acelerado que muestra cambio o progreso en el tiempo; el gancho es la velocidad de la progresión. |
| `formato_tendencia` | Trend | Solo video | Adopta un sonido, formato o parodia cultural vigente; debe referenciar claramente una tendencia activa. |
| `formato_probador` | Try-On | Solo video | El creador se prueba físicamente un producto vestible para mostrar calce, look y estilo. |
| `formato_unboxing` | Unboxing | Solo video | La apertura y revelación del empaque del producto es el foco central de la pieza. |
| `formato_texto_insolito` | Unconventional Text Placement | Video o estático | Texto ubicado en un lugar físico inesperado (espalda, cabeza, ropa); el gancho es la ubicación insólita. |
| `formato_nosotros_vs_ellos` | Us vs. Them | Video o estático | Comparación lado a lado o secuencial contra un competidor o alternativa. |
| `formato_vsl` | VSL (Video Sales Letter) | Solo video | Video largo (60+ segundos) que introduce y agita un problema, construye deseo, presenta el producto como solución y cierra con CTA. |
| `formato_hablando_camara` | Yapper | Solo video | Video de una sola toma, hablando directo a cámara, un solo hablante, un solo ambiente, sin cortes de material nuevo. |

---

## Eje 3 — Etapa de conciencia (5 valores, marco de Eugene Schwartz)

Dónde está el espectador en su recorrido, del "no sabe que tiene el problema" al "listo para comprar".
Fuente: `creative-strategy-engine/SKILL.md` del repo de Motion, que a su vez reusa el marco clásico de
Schwartz (no es una taxonomía original de Motion).

| Etiqueta | Original | Explicación |
|---|---|---|
| `conciencia_1_no_consciente` | Unaware | No sabe que tiene el problema ni que existe una solución. |
| `conciencia_2_consciente_problema` | Problem-Aware | Sabe que tiene el problema, no conoce las soluciones. |
| `conciencia_3_consciente_solucion` | Solution-Aware | Sabe que existen soluciones, está explorando opciones. |
| `conciencia_4_consciente_producto` | Product-Aware | Conoce el producto puntual, lo está considerando contra alternativas. |
| `conciencia_5_mas_consciente` | Most-Aware | Listo para comprar, necesita el empujón final (urgencia, garantía, oferta). |

---

## Eje 4 — Tipo de oferta (6 valores, eje propio — NO viene de Motion)

Ver la nota de adaptación arriba: esta lista no tiene respaldo en el repo MIT de Motion. Se agrega
para completar la línea de etiquetas que pide el informe de mejoras, con un vocabulario chico y
explícito en vez de texto libre.

| Etiqueta | Explicación |
|---|---|
| `oferta_gratis` | Se entrega algo gratis (informe, muestra, contenido) sin condición de compra. |
| `oferta_descuento` | Rebaja de precio directa, con o sin plazo. |
| `oferta_prueba` | Período o unidad de prueba antes de comprometerse al pago completo. |
| `oferta_garantia` | Garantía de devolución o resultado que reduce el riesgo percibido de comprar. |
| `oferta_paquete` | Combo o bundle de productos/servicios a un precio conjunto. |
| `oferta_sin_oferta` | El anuncio no trae oferta comercial explícita (es solo mensaje o marca). |
