# Estudio de Ficha

> **Estado:** Propuesto
> **Veredicto:** PILOTEAR
> **Fusión de:** AI Virtual Staging (Misión 2, `reportes-inmobiliario/2026-06-23.md`, 18/20) + AI Video Generator de fotos a video (Misión 2, `reportes-inmobiliario/2026-06-24.md`, 18/20) + HeadshotPro como patrón de productización de IA generativa (Misión 1, `reportes/2026-07-28.md`, 18/20) + Senja, que ya nombra a los corredores como comprador (Misión 1, `reportes/2026-07-26.md`, 17/20)
> **Arranque:** CLP 140.000–150.000 · **Break-even:** menos de 1 paquete/mes cubre herramientas; 35 paquetes/mes pagan un sueldo · **Primer ingreso:** semana 4
> **Tesis:** El staging con IA tiene las métricas más consistentes de todo el corpus inmobiliario y una adopción chilena bajo el 10%, pero las herramientas cuestan USD 19 al mes y son de autoservicio — así que el negocio no vende tecnología, vende las 2,2 horas por propiedad que el corredor no tiene, y eso todavía nadie lo ha comprobado en Chile.

## 1. Tesis y evidencia

**La evidencia del efecto es la más sólida del corpus entero.** El staging virtual es la única táctica donde las fuentes casi no se contradicen entre sí a lo largo de 66 reportes:
- +90% de CTR, +44% de consultas calificadas, +72% de tráfico, y venta 73% más rápida — 29–31 días contra 52 (`reportes-inmobiliario/2026-06-23.md`, 18/20, repetido y confirmado en `2026-06-30.md` y `2026-07-23.md`).
- Video generado con IA desde fotos: +403% de consultas contra la foto estática; 73% de los propietarios prefieren agentes que usan video (`reportes-inmobiliario/2026-06-24.md`, 18/20).
- Caso chileno con cifra dura: el video corto bajó el CPL de CLP 12.000 a CLP 5.800, un 52% (`reportes-inmobiliario/2026-08-05.md`).

**Y la brecha de adopción es igual de clara:** menos del 10% de adopción de video en cualquier formato en Chile, menos del 2% en video cinematográfico (`reportes-inmobiliario/2026-06-24.md`); staging con IA usado solo por entre 5% y 40% de las inmobiliarias **grandes** (`reportes-inmobiliario/2026-06-23.md`).

**Pero hay que decir con todas sus letras lo que la evidencia NO dice.** Todas esas cifras miden el *efecto* del staging y del video sobre la venta de la propiedad. **Ninguna mide la disposición de un corredor chico a pagarle a un tercero por tercerizarlo.** Ningún hallazgo del corpus documenta a corredores chilenos comprando este servicio. Ese es el supuesto central del proyecto y está sin validar.

La analogía que lo sostiene —y es analogía, no evidencia— es que el mercado de fotografía inmobiliaria tradicional en Chile cobra entre CLP 70.000 y 300.000 por sesión cuando cualquiera podría sacar fotos con el celular gratis. Se paga por tiempo y consistencia, no por la tecnología. Si eso se transfiere al staging con IA, hay negocio. Si no, no lo hay.

## 2. Plan de entrada

**Primero, corregir la oferta.** El paquete originalmente incluía un plano, y eso no se puede cumplir: no existe ninguna herramienta verificada que genere un plano medido a partir de fotos crudas. CubiCasa (USD 15–65 por plano) y MagicPlan (USD 25–40 por proyecto) exigen escaneo AR *in situ* con la app, recorriendo la propiedad. Lo único posible de forma remota es un plano esquemático dibujado a mano en Canva a partir de las fotos y las medidas que dé el corredor: ilustrativo, impreciso, y 30–45 minutos de trabajo humano por paquete.

**Decisión:** se saca el plano medido de la promesa. El paquete es **staging + video vertical de 30s + descripción**, entregado en 24–48 horas sin pisar la propiedad. Prometer un plano medido y entregar un dibujo rompe la confianza en la primera entrega.

**La secuencia de validación, que es lo que define el proyecto:**

1. **Semanas 1–3: producir 3 fichas piloto gratis** con propiedades propias o de conocidos. Esto tiene dos propósitos, y el segundo importa más que el primero: armar portafolio, y **medir la tasa real de reintento y el tiempo real por paquete**, que hoy son supuestos modelados, no datos.
2. **Semana 3, la pregunta que decide todo.** A cada uno de los 3 corredores piloto, textual: *"¿Pagarías CLP 49.000 por esto, o lo harías tú o tu asistente con Amueblia a 644 pesos la foto?"* La respuesta a esa pregunta vale más que todo el modelo financiero.
3. **Semana 4: cerrar 3–5 clientes pagando** solo si la respuesta de la semana 3 fue sí.

## 3. Resumen financiero

Tipo de cambio: **USD/CLP 914** (15-ago-2026) [verificado, confianza Media — cifra de snippet de búsqueda, no consulta directa a Banco Central].

**Costo de arranque**

| Concepto | CLP | Origen |
|---|---|---|
| REimagineHome Pro, primer mes (USD 29, 150 créditos) | 26.506 | [verificado] |
| Crédito prepago de video Seedance (USD 0,056/seg) | ~20.000 | [verificado] la tarifa · [estimado] el monto a cargar |
| Suscripción LLM para descripciones | 18.280 | [verificado] |
| CapCut, tier gratis | 0 | [verificado] |
| 3 fichas piloto gratis para portafolio | 12.900 | [estimado] 3× el costo unitario base |
| Landing simple + WhatsApp Business | 0–15.000 | [estimado] |
| Dominio .cl anual | 15.000 | [estimado] |
| Boleta de honorarios, persona natural | 0 | [verificado] no requiere sociedad |
| Colchón operativo del mes 2 | 46.500 | [estimado] |
| Laptop | 0 | [estimado] se asume que ya la tiene; si no, +500.000–600.000 |
| **Total** | **≈ 140.000–150.000** | ≈ USD 155–165 |

El filtro de "arranque bajo USD 10.000" no es el limitante acá: el arranque real es un sexto del tope. El limitante es el margen neto y el tiempo.

**Costo unitario real por paquete.** Supuesto: 5 ambientes con staging, video vertical de 30s, descripción. **La tasa de reintento es modelada, no verificada** — es el supuesto más frágil de todo el dossier: base de 1,6 generaciones por ambiente útil (se descarta ~40% al primer intento) y 1,8× de segundos generados contra segundos finales en video; pesimista 2,2× en ambos.

| Componente | BASE | PESIMISTA |
|---|---|---|
| Staging 5 ambientes | 1.413 (REimagineHome, 176,6 CLP/crédito) | 3.212 (Collov, USD 0,32/foto [verificado]) |
| Video 30s | 2.765 (Seedance, 51,2 CLP/seg) | 9.006 (Runway Gen-4.5, 12 créditos/seg [verificado]) |
| Descripción con LLM | ~150 | ~150 |
| **Herramientas** | **4.328** | **12.368** |
| Tiempo del fundador | 2,2 h → 26.400 | 2,75 h → 33.000 |
| **Costo total por paquete** | **≈ 30.700** | **≈ 45.400** |

Tiempo humano desglosado (base): 10 min de selección de fotos, 25 de curar el staging, 40 de armar y editar el video, 10 de pulir la descripción, 15 de control de calidad y entrega. El video es el componente más caro y el de mayor varianza entre herramientas: ahí está casi toda la diferencia entre el escenario base y el pesimista.

**Precio y margen.** Benchmark chileno [verificado]: la fotografía inmobiliaria tradicional cobra CLP 70.000–300.000 por sesión, con packs básicos desde CLP 25.000. Y el competidor que más importa: **Amueblia, staging virtual con IA en Chile, a CLP 644 por foto, sin suscripción** — es el "hazlo tú mismo" barato que compite de frente.

Precio propuesto: **CLP 49.000** por paquete (rango 39.000–65.000 según tamaño), o **CLP 320.000 por 8 propiedades** al mes.

| | BASE (precio 49.000) | PESIMISTA (precio 45.000) |
|---|---|---|
| Margen bruto sobre herramientas | 44.700 (91%) | 32.632 (73%) |
| **Margen neto, valorando el tiempo del fundador** | **18.300 (37%)** | **≈ –368 (pérdida)** |

**El escenario pesimista no deja margen.** Si la tasa de reintento real se acerca a 2,2×, el proyecto trabaja gratis.

Para un sueldo de CLP 1.500.000 netos: **35 paquetes/mes en el caso base** (77 h de producción, ~18 h/semana, deja tiempo para vender) o **47 en el pesimista** (129 h, ~30 h/semana, casi no deja tiempo para vender).

## 4. Timeline

| Semana | Acción |
|---|---|
| 1 | Elegir stack definitivo aprovechando los trials gratis (REimagineHome/ApplyDesign, Seedance/MagicHour). Conseguir 3 propiedades para el piloto. |
| 2 | Landing simple y WhatsApp Business. Contactar 15–20 corredores de la red. Ofrecer ficha gratis a 3 a cambio de testimonio. |
| 3 | **Producir las 3 fichas y cronometrar todo.** Medir tasa de reintento y tiempo real por paquete: esta es la validación crítica del modelo, no un trámite. Hacer la pregunta de la sección 2. |
| 4 | Reajustar precio y tiempos con datos propios. Cerrar 3–5 clientes pagando. **Primer peso.** |
| 5–6 | Referidos de los primeros clientes y grupos/gremios de corredores. Publicar los casos como prueba social. |
| 7–8 | Si se sostienen más de 15 paquetes/mes, evaluar delegación. Recalcular margen real contra el modelado. |

## 5. Plan de marketing

**El producto es su propia demostración**, y eso es una ventaja que los otros dos proyectos no tienen. Un antes y después de staging se entiende en dos segundos sin explicación.

- **Pieza de entrada:** el antes/después de una propiedad real que el corredor reconozca, mandado por WhatsApp sin texto de venta. La imagen hace el pitch.
- **Canal 1 — la red propia**, igual que en los proyectos 01 y 02. Es el mismo activo de distribución, y es la tercera vez que aparece como canal principal: eso confirma que la red es el activo transversal de toda la cartera.
- **Canal 2 — prospección desde los portales.** Portalinmobiliario y TocToc son una lista pública y gratuita de propiedades con fotos malas. Cada aviso con fotos de departamento vacío y mala luz es un prospecto identificado por nombre. El pitch se manda con el antes/después de **su propia** propiedad ya hecho: costo de producción de la muestra, CLP ~4.300 base.
- **Métrica a 30 días:** de 20 antes/después enviados sin costo, cuántos contestan y cuántos compran. Si de 20 muestras producidas no hay al menos 2 ventas, el costo de adquisición no cierra contra un ticket de CLP 49.000.
- **Presupuesto de pauta: CLP 0** en la fase de validación. Este negocio se prueba con muestras, no con anuncios.

## 6. Riesgos y señales de aborto

**Riesgo 1 — el supuesto central no está validado y puede matar el proyecto entero.** ¿Por qué pagaría un corredor CLP 49.000 si Amueblia cuesta CLP 644 por foto y CapCut es gratis? La hipótesis es que se paga por tiempo y consistencia, no por tecnología —las 2,2 horas y el criterio de diseño que el corredor no tiene—, y es coherente con que la fotografía tradicional cobre CLP 70.000–300.000 cuando el celular es gratis. Pero es una analogía, no evidencia.
> **Señal de aborto:** si los 3 corredores piloto de la semana 3 dicen que lo harían ellos mismos, el proyecto no sobrevive aunque el modelo financiero cierre. Se archiva ahí, habiendo gastado CLP ~13.000.

**Riesgo 2 — la tasa de reintento es un número inventado por el modelo.** 1,6× y 1,8× son estimaciones sin respaldo. Con interiores complejos, mala luz o propiedades grandes, el reintento sube y el margen neto —que en el pesimista ya está en cero— desaparece.
> **Se resuelve en la semana 3**, cronometrando las 3 fichas piloto. Hasta entonces, ninguna cifra de margen de este dossier debe tratarse como firme.

**Riesgo 3 — el plano no se puede cumplir como se prometía.** Ya corregido en la sección 2: se saca de la oferta. Queda anotado para que nadie lo reintroduzca.

**Riesgo 4 — el cuello de botella llega antes de lo que parece.** Entre 40 y 55 paquetes al mes el fundador satura. Delegar cuesta CLP 15.000–20.000 por paquete a freelance, o CLP 700.000–870.000 al mes por alguien part-time que cubre hasta ~40 paquetes. Tras delegar, el margen base baja a ~CLP 27.200 por paquete (55%), que sigue siendo sano. Conviene delegar apenas se superan los 25–30 paquetes mensuales sostenidos, sin esperar a tocar el techo.

## 7. Trazabilidad

- `reportes-inmobiliario/2026-06-23.md` — AI Virtual Staging (18/20). Las métricas más consistentes del corpus.
- `reportes-inmobiliario/2026-06-24.md` — AI Video Generator (18/20). +403% de consultas; adopción chilena <10% y <2%.
- `reportes-inmobiliario/2026-06-30.md` y `2026-07-23.md` — confirmaciones independientes de las cifras de staging.
- `reportes-inmobiliario/2026-08-05.md` — video corto en Chile: CPL de CLP 12.000 a 5.800.
- `reportes/2026-07-28.md` — HeadshotPro (18/20). El patrón de productizar IA generativa en un vertical.
- `reportes/2026-07-26.md` — Senja (17/20), que nombra explícitamente a los corredores como comprador.
- `reportes/2026-07-05.md` y `2026-07-06.md` — videos faceless: el mismo motor de imagen y video en español, listado como activo reutilizable del corpus.
- `radar/aprendizajes-clave.md` — staging virtual entre las apuestas que convierten contactos de la red inmobiliaria en primeros clientes.
