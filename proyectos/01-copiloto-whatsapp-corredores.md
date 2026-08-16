# Copiloto de WhatsApp para corredores chicos

> **Estado:** Propuesto
> **Veredicto:** PILOTEAR
> **Fusión de:** Recepcionista/Dispatcher IA por WhatsApp (Misión 1, `reportes/2026-07-15.md`, 17/20) + Agencia de Agentes de Voz IA sobre stack white-label (Misión 1, `reportes/2026-07-07.md`, 17/20) + LIDZ.IA y el hueco de precio del corredor chico (Misión 2, `reportes-inmobiliario/2026-06-30.md`, 18/20) + Chatbot de respuesta <60 seg (Misión 2, `reportes-inmobiliario/2026-06-01.md`, 18/20)
> **Arranque:** CLP 30.000–60.000 (fundador opera) / CLP 900.000 (con freelancer) · **Break-even:** 1 cliente cubre costos, 8–9 pagan un sueldo · **Primer ingreso:** semana 5–6
> **Tesis:** El corredor chico chileno pierde el lead del sábado por la noche, y la única herramienta que resuelve eso en Chile no le publica el precio — pero Meta acaba de regalar el motor, así que el negocio ya no es vender la tecnología sino configurarla y operarla.

## 1. Tesis y evidencia

El mecanismo está probado de forma independiente en tres mercados, lo que lo separa de una moda:

- **El primero que contesta se lleva el cliente.** 78% de los compradores termina trabajando con el primer agente que responde (NAR, vía `reportes-inmobiliario/2026-06-01.md`). En Brasil, responder en <5 min multiplica por 9 la conversión (`reportes-inmobiliario/2026-08-03.md`).
- **Funciona en Chile, con cifras de terceros.** LIDZ.ai reporta 92% de contactabilidad contra 20% de la industria y 3 segundos contra 60 horas de respuesta; la tasa contacto→visita sube de 1-3% a 15-25% (`reportes-inmobiliario/2026-06-30.md`). Houm + Bird: +64% leads calificados y respuesta de 2 días a casi inmediata (`reportes-inmobiliario/2026-08-10.md`, marcado DUAL en su origen).
- **El segmento está desatendido y es identificable.** Los brokerages independientes chicos son el único segmento chileno que no cruzó el umbral de adopción de IA (`reportes-inmobiliario/2026-08-09.md`). LIDZ.ai cubre ~25% de las propiedades nuevas vendidas en Chile pero **su precio no es público** — dato buscado y no encontrado en 9 reportes distintos del corpus y verificado de nuevo por el Equipo C en esta ronda. Un producto sin precio público no se vende solo al corredor de 3 propiedades.

**El hecho que cambia la tesis, y que ningún reporte conectó hasta ahora.** El 3 de junio de 2026 Meta liberó globalmente el *Meta Business Agent*: un agente de IA dentro de WhatsApp Business que responde preguntas, recomienda, **califica leads y agenda citas**, hoy gratis, con tiers pagos anunciados sin fecha. El rollout incluye Chile. Está documentado en `reportes/2026-08-10.md` con Confianza Alta (TechCrunch + blog oficial de Meta).

Ese hallazgo estaba invisible para el sistema de decisión: su encabezado es `## Actualización de alta prioridad — ...`, no `## N. Nombre — Score X/20`, así que el parser nunca lo indexó. No aparece en Explorar, ni en Decisiones, ni en `INDICE_IDEAS.md`. Sin la mesa, este dossier se habría escrito seis días después de que Meta regalara el motor, sin enterarse.

**Consecuencia directa:** vender "te construyo un bot de IA para WhatsApp" es un negocio en extinción — el propio corpus ya marcó esa categoría como saturada en Chile el 9 de agosto. Lo que no se extingue es que **la pyme y el corredor no saben que la función existe, ni la configuran bien**. El negocio se mueve de *vender tecnología* a *auditar, configurar, entrenar y operar*, con la calificación específicamente inmobiliaria (UF de presupuesto, pre-aprobación, comuna, plazo) como la capa que Meta no trae de fábrica.

## 2. Plan de entrada

**Propuesta de valor, en el idioma del corredor:**
> "Contesto cada WhatsApp de tus propiedades en menos de 10 segundos, incluso un sábado a las 11 de la noche — y te agendo la visita."

Variantes a testear: *"El comprador se queda con el primer corredor que le contesta. El tuyo va a ser siempre el primero."* / *"Nunca más pierdes el lead que te escribió el fin de semana mientras mostrabas otra casa."*

**Oferta de entrada: piloto pagado de 30 días con garantía de devolución.** Precio reducido (orden de CLP 40.000–60.000) contra el fee pleno, y devolución del 100% si en 30 días no agenda más visitas que la operación actual, con el umbral fijado por escrito en el kickoff. Cobra desde el día uno —que es lo que valida disposición a pagar— y quita el riesgo percibido, que es lo que frena a un segmento escéptico. Se descartó el setup gratis (atrae curiosos que abandonan en la semana 2) y el pago por lead calificado (imposible de tarificar sin baseline propio).

**Qué se promete:** respuesta en segundos los 7 días, calificación antes de pasar el lead, y visita agendada en el calendario del corredor.
**Qué NO se promete:** cerrar ventas (eso es del corredor), que el cliente jamás note que hay un sistema detrás, ni integración con cualquier CRM legacy sin evaluar.

**Canales para los primeros 10 clientes, en orden:**

| # | Canal | Tiempo al primer contacto | Por qué ahí |
|---|---|---|---|
| 1 | Red inmobiliaria propia | Mismo día | La ventaja injusta declarada en `radar/aprendizajes-clave.md`: contactos que ya contestan el WhatsApp, cero pitch frío |
| 2 | Referidos de los primeros pilotos | Día 15–30 | La tasa de cierre más alta y casi gratis, pero exige 2–3 pilotos vivos primero |
| 3 | Grupos de WhatsApp/Facebook de corredores | 1–2 semanas | Acceso directo, pero hay que aportar valor antes de vender o hay riesgo de expulsión por spam |
| 4 | Gremios: ACOP, COPROCH, ANACOPRO | 3–6 semanas | Volumen y validación de marca, ciclo institucional lento — sirve para escalar, no para el cliente 1 |
| 5 | LinkedIn a dueños de corredoras chicas | 1–3 semanas | Buena credibilidad, respuesta más lenta que WhatsApp directo |
| 6 | Portales (Portalinmobiliario, TocToc) | — | No es canal de venta: es prospección, para detectar corredores con avisos activos y respuesta lenta |

**Guion del primer contacto** (WhatsApp, a un corredor de la red propia, listo para copiar):

> Hola [Nombre], ¿cómo va todo? Te escribo porque esto te puede servir de inmediato: armé un sistema que contesta tus WhatsApp de propiedades en segundos —aunque sea de noche o fin de semana—, pregunta presupuesto, comuna y plazo, y te agenda la visita solo. Te lo muestro en 3 minutos con un caso tuyo real, ¿tienes 10 min esta semana? El primer mes es piloto a precio reducido y con devolución si no funciona.

**Las tres objeciones y su respuesta textual:**

- *"Ya tengo secretaria."* → "Buenísimo, esto no la reemplaza — la cubre cuando ella no está: 11 de la noche, domingo, o cuando le llegan 3 WhatsApp al mismo tiempo. El 78% de los compradores termina trabajando con el primero que le contesta; esto asegura que siempre seas tú."
- *"Es caro."* → "El piloto son 30 días a precio reducido, con devolución si no agenda más visitas que hoy. Antes de decidir si es caro: ¿cuánto vale UNA venta que se te escapó por no contestar el sábado?"
- *"Los clientes se dan cuenta que es un bot."* → "Sí, se nota que responde rápido y ordenado, y no lo escondemos. Pero la gente no elige entre bot o humano: elige entre quien le contesta y quien no. En Brasil, contestar bajo 5 minutos multiplica por 9 la conversión."

**La demo de 3 minutos que cierra.** Se conecta el copiloto a un aviso real y activo que el propio corredor elige. Alguien manda un WhatsApp en vivo simulando al comprador del sábado a las 23:00. El copiloto contesta en segundos, califica conversando (no como formulario), agenda la visita en el calendario del corredor y le manda la ficha: *"María, presupuesto UF 3.000–3.500, busca en Ñuñoa, con pre-aprobación, quiere visitar el sábado."* Se cierra con una sola pregunta: **"¿Cuántos de estos perdiste el fin de semana pasado?"**

## 3. Resumen financiero

Tipo de cambio: **1 USD = CLP 913,6** (Dólar Observado, Banco Central de Chile, 15-ago-2026). Stack del caso base: WhatsApp Cloud API directa de Meta (sin markup de BSP) + n8n self-hosted + Claude Haiku como motor + Cal.com free. Es la única combinación compatible con el techo de arranque de la mesa.

**Costo de arranque**

| Concepto | CLP | Origen |
|---|---|---|
| Meta Business + WhatsApp Cloud API (habilitación) | 0 | [verificado] Meta no cobra por habilitar, solo por mensajes |
| Verificación de Meta Business Manager | 0 | [verificado] solo exige documentos |
| Número dedicado (SIM o VoIP) | 10.000–20.000 | [estimado] precio típico de línea prepago/VoIP en Chile |
| VPS para n8n self-hosted (primer mes) | ~11.000 | [verificado] DigitalOcean 2GB, USD 12, convertido |
| Dominio + SSL | 0–15.000 | [estimado] Let's Encrypt gratis |
| Cal.com plan Free | 0 | [verificado] cubre 1 agenda por corredor |
| Freelancer: flujo n8n + prompt + integración (25–35 h) | 500.000–700.000 | [estimado] tarifa CLP 15.000–30.000/h en Chile; **CLP 0 si lo arma el fundador** |
| Constitución de SpA | 0–150.000 | [verificado] **opcional en semana 1**: se parte con boleta de honorarios |
| Créditos de prueba para templates (~100 msj) | 5.000–10.000 | [estimado] |
| Precio de LIDZ.ai (referencia competitiva) | — | **[desconocido]** buscado y no encontrado por décima vez |

**Total: CLP 30.000–60.000** si el fundador lo arma; **CLP 530.000–900.000** con freelancer. Ambos muy por debajo del techo de CLP 2.000.000. El arranque no es el problema de este proyecto.

**Costo mensual.** Supuesto explícito de volumen: 60 leads nuevos/mes por corredor, de los cuales ~90% escriben ellos primero y caen en la ventana de servicio de 24h de Meta, que es gratis. Se estiman ~45 mensajes salientes fuera de esa ventana (25 *utility*, 20 *marketing*).

| Concepto | CLP/mes | Origen |
|---|---|---|
| Mensajería Meta *utility* (~25 msj) | 180–230 | [estimado] extrapolado de tarifas México/Argentina — **no hay tarifa Chile accesible públicamente** |
| Mensajería Meta *marketing* (~20 msj) | 550–650 | [estimado] mismo problema de fuente, rango LatAm USD 0,03–0,06/msj |
| Claude Haiku, motor del agente (~60 conversaciones) | 550–600 | [estimado] ~4.500 tokens/conversación |
| **Variable por cliente** | **~1.300–1.500** | |
| VPS n8n (escala a decenas de clientes) | 11.000–22.000 | [verificado] fijo del negocio |
| Dominio + correo | ~5.500 | [estimado] fijo |
| Contabilidad PyME (solo con SpA constituida) | 30.000–80.000 | [estimado] fijo |
| Alternativa managed: Wati / Respond.io / ManyChat | 54.000–182.000 | [verificado] Wati Growth USD 59 · Respond.io Starter USD 99 · ManyChat Pro USD 29 |

**Precio, margen y equilibrio.** Ancla: la comisión de corretaje en Chile es 2% + IVA por parte [verificado]. Sobre un departamento de UF 3.500 (≈ CLP 143.000.000) eso es ~CLP 2.860.000 de comisión bruta. Un fee de CLP 120.000/mes es 3–5% de **una sola** comisión.

| | BASE | PESIMISTA |
|---|---|---|
| Setup (único) | CLP 200.000 | CLP 100.000 |
| Fee mensual | CLP 120.000 | CLP 70.000 |
| Costo variable/cliente | CLP 1.500 | CLP 4.000 |
| **Margen bruto/cliente** | **CLP 118.500 (98,7%)** | **CLP 66.000 (94%)** |
| Costo fijo del negocio | CLP 80.000 | CLP 400.000–500.000 |
| **Break-even operativo** | **1 cliente** | **7–8 clientes** |
| **Clientes para un sueldo de ~CLP 950.000** | **8–9** | **15** |

El break-even de 1 cliente es cierto pero engañoso: cubre el gasto, no paga un sueldo. La cifra que importa es **8–9 clientes en el caso base y 15 en el pesimista**, y conseguir 15 corredores pagando en el único segmento que nunca cruzó el umbral de adopción de IA no es trivial. El cuello de botella de este negocio no es el costo — es la venta.

## 4. Timeline

| Semana | Qué pasa | Horas/sem |
|---|---|---|
| 1 | Solicitar verificación de Meta Business Manager (**el cuello de botella real**: 2–7 días hábiles limpio, hasta 2–3 semanas con fricción documental). Dominio, VPS, n8n. Diseñar el flujo de calificación y el prompt. Listar 5–8 corredores de la red. Sin SpA todavía: boleta de honorarios. | 25–30 |
| 2 | Verificación en curso. Activar número dedicado. Enviar templates *utility* a aprobación (24–48h tras verificar el WABA). Configurar Cal.com. | 20–25 |
| 3 | Verificación lista (base) o pendiente (pesimista, corre todo +1–2 semanas). Pruebas end-to-end con leads simulados. Ajuste de prompt. **Onboarding del primer piloto**, gratis o a CLP 30.000 simbólico. | 20 |
| 4 | Piloto con leads reales. QA manual diario de las conversaciones — nadie entrega su canal de venta a una IA sin supervisión las primeras semanas. Definir precio final con datos propios. Contactar a los 5–8 corredores con métricas en mano. | 20 |
| **5–6** | **Cierre de 1–2 clientes pagando (setup + primera mensualidad) → primer ingreso.** Si Meta se demoró o el piloto necesitó más ajuste, esto se corre a semana 8–9. | 20 |
| 7–12 | Escalar a 5–8 clientes si el piloto convirtió; si no, iterar producto antes de seguir vendiendo (¿el problema es el agente o el precio?). Con 3+ clientes firmes, recién ahí constituir SpA. | 15–20 |

Régimen de mantención: ~4–6 h de onboarding por cliente nuevo y ~2–3 h/mes de soporte por cliente activo.

## 5. Plan de marketing

| Semana | Acción | Costo CLP | Meta |
|---|---|---|---|
| 1 | Outreach directo con el guion a 15–20 contactos de la red propia | 0 | 5 demos agendadas |
| 2 | Cerrar 2–4 pilotos con la demo en vivo. Compartir la demo (no venta) en 3–4 grupos de corredores + LinkedIn a ~30 corredores independientes | 0–20.000 | 3 pilotos por referido |
| 3 | Activar referidos (2 por piloto exitoso). Test pagado chico: Click-to-WhatsApp Ads segmentando corredoras chicas | 100.000–150.000 | 2–3 pilotos más |
| 4 | Gremio (ACOP o COPROCH): newsletter o espacio en capacitación, usando los pilotos como caso | [desconocido] cuota no publicada | Cerrar los 10, recoger testimonios |

**Total de canal pagado: CLP 100.000–170.000** en 4 semanas. El resto es tiempo del fundador.

**Sobre el CPL, con la honestidad que el corpus no ha tenido.** El corpus documenta CPL de USD 1–5 con Click-to-WhatsApp contra USD 5–25 con landing (`reportes-inmobiliario/2026-06-21.md`), pero **esa cifra es para captar compradores de propiedades, no para captar corredores como clientes B2B**. Usarla acá sería sacarla de contexto. Para adquisición de corredores-cliente el rango es **CLP 5.000–15.000 por lead calificado — estimado, sin caso chileno medido**, y es el número a validar en la semana 3, no a repetir como dato.

Los canales 1 y 2 son el motor real de los primeros 10 clientes; el pagado es un experimento barato para ver si existe un segundo canal escalable después.

## 6. Riesgos y señales de aborto

**Riesgo 1 — Meta se come el producto (el más grave).** El Meta Business Agent ya califica leads y agenda citas, gratis, en Chile. Hoy es genérico y orientado a catálogo/comercio, y no trae la calificación inmobiliaria específica. Pero Meta anunció tiers pagos sin fecha, y podría empujar a las pymes hacia agencias certificadas propias.
> **Señal de aborto:** si el Meta Business Agent nativo califica bien un lead inmobiliario chileno (presupuesto en UF, pre-aprobación, comuna, plazo) sin capa encima, el proyecto pierde su razón de ser como producto y debe reconvertirse enteramente en servicio de configuración. **Se verifica en la semana 1**, antes de gastar una hora en el flujo: auditar 5 pymes de la red que ya usen WhatsApp Business.

**Riesgo 2 — Meta no aprueba la verificación.** Sin WABA verificada no hay producto. Cuentas nuevas sin historial, RUT que no calza con el nombre comercial o documentos incompletos estiran esto a 3–4 semanas, y no hay nada que el fundador pueda hacer para acelerarlo.
> **Señal:** si a los 10 días hábiles no hay verificación, activar la vía managed (Wati/360dialog, que resuelven el onboarding) aunque suba el costo fijo.

**Riesgo 3 — el corredor chico no paga fijo.** El segmento cierra ventas de forma irregular (1 cada 2–3 meses), y un gasto fijo mensual compite mal contra ingresos irregulares. Que sea el único segmento sin adoptar IA se puede leer como oportunidad o como que ya lo evaluaron y no les calza.
> **Señal:** si de 10 pilotos menos de 4 renuevan al segundo mes, migrar a pago por resultado (por visita agendada), lo que rehace todo el break-even de arriba.

**Riesgo 4 — la promesa y el costo están en tensión.** El modelo mantiene el costo variable bajo porque asume que el lead escribe primero. Pero replicar el 92% de contactabilidad de LIDZ exige reenganche activo a leads fríos, que son mensajes *marketing*, los más caros. Bajar el costo y cumplir la promesa no son compatibles por defecto: si no reengancha, el producto deja de ser una máquina de contactabilidad y pasa a ser "un chatbot que responde rápido", bastante más difícil de vender a CLP 120.000/mes.

**Limitación de esta evaluación.** No se pudo confirmar la tarifa de mensajería de Meta específica para Chile: `developers.facebook.com` y otros devolvieron `EGRESS_BLOCKED` en este entorno. Todo lo que toca esa tarifa está etiquetado [estimado] a partir de proxies de México, Argentina y Colombia. Antes de fijar precio fino, conviene que un humano revise la tabla de Meta seleccionando Chile.

## 7. Trazabilidad

- `reportes/2026-07-15.md` — Recepcionista/Dispatcher IA por WhatsApp para oficios de terreno (17/20). Aporta el mecanismo y el ángulo de dolor.
- `reportes/2026-07-07.md` — Agencia de Agentes de Voz IA, stack Callin.io + n8n + Cal.com (17/20). Aporta la arquitectura white-label sin tecnología propia.
- `reportes/2026-06-09.md` — AI Setter de Leads vía WhatsApp (17/20). Agendamiento automático.
- `reportes/2026-08-05.md` — Vambe, agentes de IA de ventas por WhatsApp (15/20). Serie A US$14M, +2.000 clientes: el mercado existe y está capitalizado.
- `reportes/2026-08-09.md` — reventa white-label de chatbots marcada como saturada en Chile.
- **`reportes/2026-08-10.md` — Meta Business Agent vivo y gratis, incluido Chile (Confianza Alta).** El hallazgo que reencuadra todo el proyecto y que estaba fuera del índice.
- `reportes-inmobiliario/2026-06-01.md` — Chatbot de respuesta <60 seg (18/20). NAR: 78%.
- `reportes-inmobiliario/2026-06-21.md` — Click-to-WhatsApp Ads (18/20). CPL USD 1–5, adopción <3% en Chile.
- `reportes-inmobiliario/2026-06-30.md` — LIDZ.IA (18/20). 92% contactabilidad, 25% del mercado, sin precio público.
- `reportes-inmobiliario/2026-08-03.md` — WhatsApp Brasil: <5 min = 9x conversión.
- `reportes-inmobiliario/2026-08-09.md` — brokerages independientes, único segmento sin cruzar el umbral de IA.
- `reportes-inmobiliario/2026-08-10.md` — Houm + Bird, +64% leads calificados (marcado DUAL en origen).
- `radar/aprendizajes-clave.md` — la red inmobiliaria como ventaja injusta y canal de primeros clientes.
