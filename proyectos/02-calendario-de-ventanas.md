# El Calendario de Ventanas

> **Estado:** Propuesto
> **Veredicto:** PILOTEAR
> **Fusión de:** La serie de 6 relanzamientos del bróker de fondos estatales (Misión 1, `reportes/2026-07-07.md` a `reportes/2026-08-04.md`, 14–17/20) + el cluster de subsidios habitacionales, 7 de las 20 mejores tácticas del corpus (Misión 2, `reportes-inmobiliario/2026-07-14.md` y otros, 17–18/20)
> **Arranque:** CLP 220.000–420.000 más 125 h propias (o CLP 2.700.000 delegado) · **Break-even:** 3 suscriptores en caja, ~29 con mantención delegada · **Primer ingreso:** mes 2 por suscripción; mes 4–6 por success fee
> **Tesis:** Las dos misiones llevan meses redescubriendo la misma mecánica —una ventana con fecha de cierre convierte muy bien— sin notar que el activo no es cada convocatoria sino el calendario que las contiene; pero el calendario solo es negocio por el lado inmobiliario, no por el lado del bróker de fondos.

## 1. Tesis y evidencia

**El diagnóstico que originó este proyecto es una falla del propio sistema.** El "bróker de fondos estatales" se lanzó como oportunidad nueva **seis veces** en cinco semanas, con títulos distintos: `reportes/2026-07-07.md`, `2026-07-18.md`, `2026-07-21.md`, `2026-07-26.md`, `2026-08-03.md` y `2026-08-04.md`. En paralelo, la Misión 2 puntuaba subsidios habitacionales en el top del ranking una y otra vez. El índice anti-repetición compara títulos, no negocios subyacentes, así que nadie vio que era una sola tesis repetida catorce veces entre las dos misiones.

Seis relanzamientos no son ruido: son convicción acumulada. Pero la conclusión correcta no es "hay seis negocios", sino "hay un activo —el calendario— y hay que decidir por qué lado se cobra".

**La evidencia de que la ventana convierte es fuerte y verificable:**
- Subsidio a la Tasa (Ley 21.748): **95.647 solicitudes elegibles contra 50.000 cupos legales = 191% de sobredemanda** (`reportes-inmobiliario/2026-08-04.md`). Eso es urgencia real, no fabricada por el marketing.
- Subsidio al Dividendo: 76.688 solicitudes elegibles, 23.050 pagos cursados, fuente ABIF (`reportes-inmobiliario/2026-07-14.md`, 18/20).
- DS-52 arriendo 2026: 170 UF en cuotas de 4,2 UF/mes, ~8.450 familias proyectadas (`reportes-inmobiliario/2026-07-07.md`).
- Del lado pyme, las dos oportunidades con score 18/20 del corpus de negocios son ventanas con fecha dura y Confianza Alta: la condonación SII-TGR de 29 comunas (`reportes/2026-07-26.md`) y la auditoría de nómina pre-reforma SIS→FAPP (`reportes/2026-07-14.md`).

**Y la evidencia en contra, que es la que decide el veredicto:** postular a Corfo y Sercotec **es gratis, y el mercado chileno ya tiene fricción reputacional instalada contra quien cobra por gestionarlo** — las propias fuentes advierten "si alguien te cobra por gestionar tu postulación, desconfía". En el estándar internacional de grant writing, el fee por porcentaje del monto adjudicado está activamente prohibido por las asociaciones profesionales. No hay evidencia de que sea ilegal en Chile, pero es una señal de riesgo real. Además, `fondos.gob.cl` ya existe, es oficial, gratuito y cubre todos los fondos públicos.

## 2. Plan de entrada

**El orden de operaciones importa más que el plan.** No se construye el calendario primero. El experimento más barato que resuelve la incógnita central va antes que cualquier construcción:

**Semana 1 — la pregunta de CLP 0.** Llamar a 10–15 corredores de la red propia y preguntar directo si pagarían por un boletín semanal que les diga qué ventana de subsidio está por cerrar, cuántos cupos quedan y con qué mensaje venderla. Si menos de 3–5 dicen que sí a un precio concreto, todo el proyecto es un lead magnet con delirios de bróker y se archiva. **Este paso cuesta cero pesos y ahorra 125 horas.**

Solo si esa pregunta pasa:

**Semanas 2–5 — construir la versión angosta.** No las 40–60 fuentes completas. Solo los subsidios habitacionales (DS1, DS-52, Ley 21.748, FOGAES): es la mitad del trabajo, es la mitad que la red propia sí compra, y es donde la sobredemanda documentada da el argumento de urgencia.

**Semana 6 — cobrar.** Boletín semanal por suscripción, cobrado desde el mes 1, sin desfase.

**La línea de bróker de fondos a pymes no se opera como servicio propio.** Se deriva a consultoras ya existentes a cambio de un fee de derivación fijo y pagado por adelantado. Eso elimina de un golpe las 10–20 horas de acompañamiento por expediente, el desfase de caja de 4–8 meses y el riesgo reputacional de cobrar un porcentaje por gestionar algo gratuito.

## 3. Resumen financiero

Tipo de cambio: **USD/CLP ≈ 930** (agosto 2026) [estimado] — Banco Central no consultado directo, fuente secundaria. **UF: CLP 40.850,06** (13-ago-2026, Banco Central) [verificado].

**Costo de arranque**

| Concepto | Horas | CLP | Origen |
|---|---|---|---|
| Mapeo de fondos pyme (Corfo/Sercotec/ChileCompra) | 40 h | 720.000 | [estimado] a tarifa freelance CLP 18.000/h |
| Plazos tributarios y laborales (SII, TGR, SIS→FAPP) | 20 h | 360.000 | [estimado] |
| Subsidios habitacionales (DS1, DS-52, Ley 21.748, FOGAES) — el más complejo por tramos y variantes regionales | 30 h | 540.000 | [estimado] |
| Verificación cruzada de cada cifra contra ≥2 fuentes primarias | 20 h | 360.000 | [estimado] control anti-error, ver Riesgo 1 |
| Setup de base de datos y alertas | 15 h | 270.000 | [estimado] |
| **Subtotal mano de obra** | **125 h** | **2.250.000** | |
| Diseño (logo, plantilla, landing) | — | 200.000 | [estimado] |
| Dominio .cl | — | 18.000 | [verificado] rango NIC Chile |
| Persona natural con boleta de honorarios | — | 0 | [verificado] no requiere constituir sociedad |
| SpA, si se formaliza para contratos de fee | — | 150.000–200.000 | [estimado] |

**Dos escenarios reales:** si el fundador investiga él mismo, la caja es de **CLP 220.000–420.000** pero cuesta **125 horas** (3–4 semanas part-time antes de tener algo publicable). Delegado por completo: **CLP 2.700.000–3.000.000**. La versión angosta propuesta en la sección 2 recorta esto a aproximadamente la mitad.

**Costo mensual.** El costo dominante no es software: es que alguien reverifique cada semana que las fechas y los cupos siguen vigentes.

| Concepto | CLP/mes | Origen |
|---|---|---|
| Airtable Team (1 seat, anual) | 18.600 | [verificado] USD 20 |
| MailerLite pagado (>1.000 suscriptores) | 9.300–17.700 | [verificado] rango |
| Automatización (Make/Zapier básico) | 8.400–15.000 | [estimado] |
| Dominio prorrateado | 1.500 | [verificado] |
| **Subtotal software** | **38.000–53.000** | |
| Mantención semanal si se delega (10–14 h/sem = 42–58 h/mes) | 760.000–1.040.000 | [estimado] a CLP 18.000/h |

Operando solo: **CLP 40.000–55.000/mes de caja más 10–14 horas semanales del fundador, indefinidamente.** Eso no es mantención liviana, es casi un medio tiempo permanente, y crece con cada línea nueva que se agregue al calendario.

**Las dos líneas de ingreso, evaluadas por separado**

*(a) Bróker de postulación a pymes.* Montos de fondos [verificado]: Capital Semilla Emprende y Capital Abeja CLP 3.500.000; Crece CLP 5.000.000–9.000.000; Semilla Inicia hasta CLP 15.000.000; Semilla Expande CLP 45.000.000–51.000.000. Success fee de referencia 10–15% [estimado] — el propio corpus lo marcó Confianza Baja, sin caso documentado de un consultor cobrando así, y esta ronda tampoco lo verificó. Tasa de adjudicación ~20% [estimado, sin fuente pública; Sercotec no publica la estadística].

| Fondo | Monto CLP | Fee 10% si adjudica | Valor esperado al 20% |
|---|---|---|---|
| Capital Semilla / Abeja | 3.500.000 | 350.000 | **70.000** |
| Crece | 5.000.000–9.000.000 | 500.000–900.000 | **100.000–180.000** |
| Semilla Inicia | hasta 15.000.000 | hasta 1.500.000 | **hasta 300.000** |
| Semilla Expande | 45.000.000–51.000.000 | 4.500.000–5.100.000 | **900.000–1.020.000** |

Los fondos chicos no cubren el costo de servirlos: CLP 70.000–180.000 de valor esperado contra 10–20 horas de acompañamiento por expediente. Solo Semilla Expande y equivalentes tienen economía, y son los más competidos. **Y el ciclo de cobro es demoledor:** Corfo informa resultados en 60–90 días (`reportes/2026-07-21.md`), adjudicado no es pagado, y los fondos se desembolsan contra rendición. Del primer contacto al primer peso: **4 a 8 meses.**

*(b) Suscripción de contenido para corredores.* Precio estimado CLP 15.000–40.000/mes por corredor u oficina [estimado, confianza baja, sin comparable chileno encontrado]. No se detectó competidor chileno cobrando por esto hoy. **Ciclo de cobro: inmediato, desde el mes 1.**

**(b) es el negocio; (a) es un complemento de alto ticket y alto riesgo.** Cuatro razones: (b) cobra mensual y de inmediato mientras (a) tiene 4–8 meses de desfase que un solo-founder sin colchón no aguanta; (b) se apalanca en la red inmobiliaria que ya existe mientras (a) exige adquirir clientes pyme desde cero; (a) carga riesgo reputacional que (b) no tiene; y la economía de (a) solo cierra en fondos escasos y muy competidos.

**Punto de equilibrio.** Pesimista (fundador solo, sin delegar): costo caja ~CLP 50.000/mes → **3 suscriptores a CLP 20.000**. Pero el techo real no es plata, es tiempo: 10–14 h/semana de mantención más venta más redacción no escala más allá de una persona, y contratar rompe la economía de solo-founder. Base (se delega mantención desde el mes 4–6): costo fijo ~CLP 570.000/mes → **~29 suscriptores a CLP 20.000**.

## 4. Timeline

| Mes | Hito | Ingreso |
|---|---|---|
| 0 | **La pregunta de CLP 0** a 10–15 corredores de la red. Si no hay 3–5 síes a precio concreto, se archiva el proyecto acá. Si pasa: construcción de la versión angosta (subsidios habitacionales), ~60–70 h. | $0 |
| 1 | Lanzamiento del boletín gratis a la red existente para validar apertura. Nada de cobrar todavía. | $0 |
| 2 | Primeros suscriptores pagados. **Primer peso real, vía la línea (b).** | Primer ingreso |
| 3–4 | Crecimiento de suscriptores. Primeras derivaciones a consultoras con fee fijo por adelantado. | Recurrente creciendo |
| 4–6 | Delegar la mantención semanal para romper el techo de tiempo del fundador. | — |
| 6 | **Punto de decisión:** si (b) no llegó a 15–20 suscriptores, el modelo no cubre el costo delegado. Volver a operación 100% solo o pivotar. | — |

## 5. Plan de marketing

El activo de distribución ya existe y es el mismo del proyecto 01: la red inmobiliaria propia. No hay que construir audiencia, hay que activarla.

- **Gancho de entrada:** la cifra de sobredemanda. "Hay 95.647 solicitudes para 50.000 cupos del subsidio a la tasa" es un mensaje que un corredor puede reenviar tal cual a sus clientes esta misma semana. La urgencia es real y verificable, que es justo lo que el corpus dice que casi ningún corredor chileno está usando: la brecha es de comunicación, no de producto (`reportes-inmobiliario/2026-08-04.md`).
- **Formato:** boletín semanal corto, con cada ventana en tres líneas —qué es, cuánto queda, cómo se vende— más el mensaje listo para copiar y pegar al cliente final. Se vende tiempo y certeza, no información.
- **Primera prueba de valor:** regalar cuatro semanas a la red propia antes de cobrar. Si a la cuarta semana los corredores no están reenviando el contenido, no hay negocio.
- **Presupuesto de adquisición pagada: CLP 0** en la fase de validación. Este proyecto no se prueba con pauta; se prueba con la red que ya contesta el WhatsApp.

## 6. Riesgos y señales de aborto

**Riesgo 1 — una cifra mal puesta destruye el activo entero.** Esto ya ocurrió dentro del propio corpus: el cupo del FOGAES tramo 4.000 UF osciló entre 2.500 y 5.000 durante más de una semana en distintos reportes, sin resolverse, por bloqueo de acceso a fuentes primarias. Un calendario no pierde credibilidad gradualmente: la pierde de una vez. Y las dos líneas de ingreso dependen al 100% de esa credibilidad.
> **Mitigación obligatoria:** ninguna cifra se publica sin dos fuentes primarias concordantes. Si solo hay una, se publica marcada como no confirmada, con la fecha de la última verificación visible al lector.

**Riesgo 2 — `fondos.gob.cl` ya existe, es oficial y es gratis.** Si el mercado no valora la interpretación y la urgencia por encima del dato crudo gratuito, la línea (b) vale cero.
> **Señal de aborto:** es exactamente lo que mide la pregunta de CLP 0 del mes 0. Menos de 3 síes de 15 corredores y se archiva.

**Riesgo 3 — cobrar un porcentaje por gestionar algo gratuito.** Si el cliente descubre a mitad de camino que postular a Sercotec no cuesta nada, la línea (a) se cae por el modelo de cobro, no por falta de demanda.
> **Mitigación ya incorporada al plan:** la línea (a) no se opera como servicio propio; se deriva con fee fijo por adelantado.

**Riesgo 4 — el techo de tiempo.** 10–14 h semanales indefinidas es casi medio tiempo. El negocio no puede crecer sin contratar, y contratar sube el break-even de 3 a ~29 suscriptores de un salto.

**Advertencia sobre el veredicto.** El Equipo C fue explícito: ejecutado como estaba planteado originalmente —con las dos líneas al mismo nivel— **esto es un lead magnet disfrazado de negocio**. El veredicto PILOTEAR aplica exclusivamente a la línea (b), con la línea (a) degradada a derivación. Si alguien retoma este dossier y vuelve a poner el bróker de fondos como motor, está reabriendo un caso ya cerrado por séptima vez.

## 7. Trazabilidad

- `reportes/2026-07-07.md`, `2026-07-18.md`, `2026-07-21.md`, `2026-07-26.md`, `2026-08-03.md`, `2026-08-04.md` — la serie completa de 6 relanzamientos del bróker de fondos estatales (14–17/20). Consolidada acá por primera vez.
- `reportes/2026-07-14.md` — Auditoría exprés de nómina pre-reforma SIS→FAPP (18/20). Ventana con fecha dura, Confianza Alta.
- `reportes/2026-07-26.md` — Condonación de emergencia SII-TGR, 29 comunas (18/20).
- `reportes-inmobiliario/2026-07-14.md` — Subsidio al Dividendo, Ley 21.748 (18/20). Cifras ABIF.
- `reportes-inmobiliario/2026-08-04.md` — Subsidio a la Tasa: 191% de sobredemanda (17/20).
- `reportes-inmobiliario/2026-07-07.md` — Subsidio de arriendo DS-52 2026 (17/20).
- `reportes-inmobiliario/2026-08-02.md` — Ventana de IVA 0% a vivienda nueva (17/20).
- `reportes-inmobiliario/2026-08-08.md` — Convenios habitacionales FFAA/Carabineros (17/20).
- `reportes-inmobiliario/2026-08-09.md` y `2026-08-11.md` — la discrepancia no resuelta del cupo FOGAES, que es la evidencia del Riesgo 1.
- `radar/aprendizajes-clave.md` — el subsidio estatal a la tasa y FOGAES/DS1 como motor comercial nativo con fecha de vencimiento.
