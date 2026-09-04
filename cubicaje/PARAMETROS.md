# Parámetros de cubicaje — madera masiva HILAM (Arauco)

Fuente primaria de todo lo que calcula este sistema. Cada número de abajo tiene
etiqueta de origen: **[mail]** = viene textual del correo de Lukas Villalobos;
**[ficha]** = viene de una ficha técnica PDF publicada por Hilam; **[estimado]**
= supuesto propio del sistema, no de Arauco (siempre configurable por el usuario).

---

## 1. Origen

**Correo:** Lukas Villalobos Gallardo — Ingeniero Desarrollo, Subgerencia
Construcción en Madera, ARAUCO. `lukas.villalobos@arauco.com` · +569 6703 4915
**Asunto:** "Re: Cotización" · **Fecha:** 3 de septiembre de 2026, 19:35 UTC
**Contexto:** posterior a la reunión del 3-sep-2026 en Av. El Golf 150, piso 12.
**Proyecto de referencia del usuario:** 20 casas de 100 m² (2.000 m² totales).

Fichas técnicas descargadas de <https://arauco.com/hilam/documentos-descargables/>.

---

## 2. Indicador de eficiencia de material: m³ de madera por m² de proyecto

Es el corazón del método que entrega Lukas: se cubica multiplicando la superficie
del proyecto por un ratio, según el sistema estructural elegido. **[mail]**

| Sistema | Ratio m³/m² | Qué incluye | Qué falta después |
|---|---|---|---|
| **MLE** (solo vigas y pilares de madera laminada) | **0,10 – 0,20** | Estructura de vigas y pilares | Muros y losas: panel SIP, entramado ligero o Metalcon |
| **MLE + CLT** (vigas laminadas + paneles) | **0,20 – 0,30** | Estructura mixta | Más eficiente en material que CLT puro, pero puede requerir más mano de obra |
| **CLT** (solo paneles contralaminados) | **0,30 – 0,40** | Estructura completa de paneles | Revestimiento exterior y sobrelosa |

Cita textual del correo: *"inicialmente medimos la eficiencia del uso del material
utilizamos un indicador de cantidad de metros cúbicos de material por cada m2 de
proyecto (m3/m2)"*.

---

## 3. Costo referencial del material (UF por m³)

**[mail]** — "Actualmente, el costo referencial del material es:"

| Partida | UF/m³ |
|---|---|
| Madera | 26,5 |
| Impregnación | 4,3 |
| Mecanizado CNC | 2,0 – 3,3 |
| **Total aproximado** | **32,8 – 34,1** |

**No incluye:** transporte, fundaciones, terminaciones ni otros costos asociados
al proyecto. **[mail]**

Nota del correo: en algunos casos la madera puede quedar a la vista en interiores
y funcionar como terminación arquitectónica (es decir, el costo de terminación
interior baja, pero eso no está cuantificado en el correo).

### Valor de referencia del CNC usado por defecto en el sistema

El sistema ofrece 2,0 (mínimo) · **2,7 (referencia)** · 3,3 (máximo). El 2,7 **no
aparece escrito en el correo**: es el único valor que reproduce exactamente el
ejemplo de 837,5 UF que entrega Lukas (ver punto 4).

Lo más probable es que Lukas no haya "elegido" 2,7 como precio de CNC, sino que
haya redondeado: el punto medio real del rango 2,0–3,3 es 2,65, y el del total
32,8–34,1 es 33,45 → 33,5. Es decir, **2,7 es un artefacto de redondeo, no una
tarifa de Arauco**. Para el total da exactamente lo mismo; importa al leer el
desglose, donde el sistema muestra el CNC como partida propia.

---

## 4. Ejemplo de validación entregado por Lukas

**[mail]** — *"para un proyecto de 100 m² con una solución MLE + CLT, el costo
aproximado de la estructura de madera impregnada y mecanizada sería de 837,5 UF"*.

Reconstrucción del cálculo:

```
100 m²  ×  0,25 m³/m²          = 25 m³        (0,25 = centro del rango 0,20–0,30)
26,5 + 4,3 + 2,7               = 33,5 UF/m³   (madera + impregnación + CNC ref.)
25 m³   ×  33,5 UF/m³          = 837,5 UF     ✓ coincide exactamente
```

El sistema corre este cálculo como autotest en cada carga de la página y muestra
el resultado en el pie. Si alguna vez deja de dar 837,5 UF, hay un error en los
parámetros.

---

## 5. Condiciones comerciales estándar

**[mail]** — Calendario de pagos y plazos:

| Hito | % | Plazo declarado |
|---|---|---|
| Anticipo para desarrollo del modelo en software especializado | 5 % | 15 a 30 días, según volumen y cantidad de elementos |
| Previo al inicio de fabricación | 45 % | Fabricación: 45 a 60 días una vez aprobado e ingresado el modelo final |
| Saldo previo al despacho desde fábrica hacia obra | 50 % | — |

Plazo desde el anticipo hasta el despacho: **60 a 90 días** **[estimado]** — es la
suma de los dos plazos declarados; el correo no da un total. Trátalo como un
**piso**, no como una estimación: no incluye el tiempo que tome aprobar el modelo
ni la gestión del pago del 45 %.

Existen alternativas de financiamiento (líneas de crédito), evaluadas caso a caso. **[mail]**

**Cotizador web:** el correo dice, textual, que para proyectos de **5 a 30 m³**
recomiendan el cotizador web. Que fuera de ese rango corresponda "cotización
directa" es **inferencia del sistema [estimado]**: el correo no lo dice, y para
volúmenes muy chicos la ficha MLE estándar apunta a distribuidores, que es otra
vía. La URL <https://arauco.com/hilam/cotizador/> viene del correo de `hilam@arauco.com`
del 28-ago-2026, no del de Lukas.

---

## 6. Servicio de asesoría incluido

**[mail]** — El servicio de asesoría y proyectos mecanizados incluye:

- Ingeniería básica: análisis técnico y predimensionamiento.
- Modelos BIM 3D para mecanización precisa.
- Coordinación de fabricación y logística.

Considera coordinaciones (**no** capacitaciones) previas con la empresa a cargo
del montaje, y está **sujeto al volumen del proyecto**.

---

## 7. Antecedentes que Arauco pide para cotizar

**[mail]** — Lista textual:

- Planos (formato `.dwg`) y Especificaciones Técnicas (EE.TT.) de arquitectura
- Planos de ingeniería y memoria de cálculo
- Modelo BIM en formato IFC (deseable)
- Estado o etapa de la obra: En estudio / En diseño / En licitación / En ejecución
- Material: CLT / MLE / Ambos
- Superficie aproximada (m² estimados)
- Fecha estimada de entrega de la madera en obra
- Fecha máxima de entrega de la cotización

---

## 8. Dimensiones de producto (para el modo detallado)

### CLT — Madera Contralaminada **[ficha]**
Ficha técnica CLT 2025: <https://arauco.com/hilam/wp-content/uploads/sites/29/2025/10/CLT-Ficha-Tecnica-2025_2.pdf>

- **Espesores disponibles (mm):** 56, 80, 90, 100, 110, 120, 130, 150, 160, 170,
  180, 200, 210, 240, 250, 280
- **Número de capas:** 3 capas (56–120 mm) · 5 capas (130–200 mm) · 7 capas (210–280 mm)
- **Ancho máximo:** 3,4 m (sobre 2,6 m requiere transporte especial e incluso escolta)
- **Largo máximo:** hasta 13,5 m
- **Densidad para diseño y transporte:** 500 kg/m³ (Catálogo CLT, pág. 22)
- Pino radiata C16/C24, adhesivo poliuretano (PUR). Calidades: a la vista / no a la vista.

> ⚠ **56 mm vs. 60 mm.** El panel más delgado del catálogo es de **56 mm**, pero la
> ficha de dimensionamiento de losas (2025) tabula **60 mm**. No son el mismo panel
> y el de 56 mm salva menos luz: en simplemente apoyado con pp 150 y carga 200,
> el catálogo le da 1,75 m contra los 2,25 m del de 60 mm. Por eso, cuando el
> prediseño de losas arroja 60 mm, el sistema avisa y sugiere pasar a 80 mm o
> confirmar el 56 mm con Arauco; y el modo detallado solo acepta espesores de
> catálogo.

### MLE — Madera Laminada **[ficha]**
Ficha técnica MLE 2025: <https://arauco.com/hilam/wp-content/uploads/sites/29/2025/10/MLE-Ficha-tecnica-2025_2.pdf>

- **Anchos estándar (mm):** 42, 65, 90, 120, 130, 138, 150, 185, 200, 250, 280, 300
- **Altos estándar (mm):** 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390
  (múltiplos de 30 mm)
- **Largo:** limitado por el transporte — ancho máx. 2,5 m y largo máx. 15 m para
  transporte normal; elementos rectos o curvos de hasta 40 m según proyecto.
- **Densidad de referencia:** 500 kg/m³ · **Humedad:** 7 % a 15 %
- Clases estructurales: mle24c, mle24h, mle20h (NCh2165:2023) o A-B-A (NCh2165:1991).
- ⚠ La ficha advierte que **anchos y espesores fuera de los estándares tabulados
  tienen recargo** (los altos van en múltiplos de 30 mm; varios anchos estándar
  —42, 65, 138, 185, 250, 280— no lo son y no llevan recargo).

---

## 9. Prediseño de losas CLT (módulo orientativo)

Ficha: **Tablas de dimensionamiento de losas de CLT Hilam** (2025)
<https://arauco.com/hilam/wp-content/uploads/sites/29/2025/07/CLT-Dimensionamiento-de-losas-2025.pdf>

Las **dos** tablas de esa ficha están incorporadas al sistema: luz máxima por
espesor, y resistencia al fuego de la misma solución. Se leyeron de la **capa de
texto del PDF** (con PyMuPDF), no por OCR.

Verificación: los autotests comparan la **suma de cada fila** contra la del PDF
(546 celdas, 78 checksums) y corren los tres casos de ejemplo de la ficha. Los
checksums existen porque una auditoría posterior encontró una celda mal transcrita
que ninguna otra prueba detectaba — ver la nota al final de esta sección.

Es un **prediseño referencial**, no un cálculo estructural: el espesor definitivo
lo fija el calculista del proyecto.

**Espesores tabulados (mm):** 60, 80, 90, 100, 110, 120, 130, 150, 160, 170, 180,
200, 210. **Condiciones:** simplemente apoyado (1 tramo), continuo (2 tramos),
voladizo (1 tramo). **Columnas:** peso propio adicional de 50 kgf/m² con cargas de
uso 100/200/300/500, y de 150 kgf/m² con 200/300/500 (la ficha no publica pp 150
con carga 100).

Supuestos de la tabla **[ficha]**: láminas longitudinales C24 y transversales C16
(EN 338); cargas de uso NCh1537; deformaciones NCh1198; vibraciones NDS2018 y
criterio CLT Handbook Canadá/EE.UU. La resistencia al fuego se calcula con el CLT
**a la vista por debajo**, sin revestimiento; protegerlo con yeso cartón la sube.

Dato normativo citado en la ficha **[ficha]**: según OGUC se exige **F-60** para
losas en edificaciones residenciales de hasta 4 pisos; **F-30** aplica a viviendas
de hasta 2 pisos.

Definiciones de carga, según el Catálogo CLT (pág. 46) — son las que decide qué
columna usar:

- **Peso propio adicional** (peso de la estructura): 50 kgf/m² = CLT más pavimento ·
  150 kgf/m² = CLT más losa de hormigón y pavimento.
- **Carga de uso** (muebles, personas): 100 = techo · 200 = piso residencial ·
  300 = piso en oficinas · 500 = piso en lugares públicos de uso masivo.

### Discrepancia detectada en la propia ficha

Los casos de ejemplo 1 y 2 de la ficha se reproducen exactamente (120 mm / F-60 y
90 mm / F-30). El **caso 3** no: para voladizo con pp 150 kgf/m², carga de uso
200 kgf/m² y luz de 2 m, el texto concluye 120 mm, pero la tabla de la misma ficha
da **1,75 m** de luz máxima para ese panel — los 2,00 m recién se alcanzan con
**130 mm**. El sistema sigue la tabla, que es el dato duro y además el resultado
más conservador. Los autotests de `cubicador.py` dejan esa diferencia registrada.

### Error corregido en la transcripción (4-sep-2026)

La auditoría encontró **una celda mal transcrita** de las 546: resistencia al fuego,
condición continua (2 tramos), panel de 110 mm, peso propio 50 con carga de uso 200.
Decía F-60 y la ficha dice **F-30**. Efecto: para una losa continua en esa condición
con luz entre 4,25 y 4,50 m, el sistema habría dicho que 110 mm cumple F-60 cuando
la ficha exige 120 mm. Corregido en `cubicador.py` e `index.html`.

Ni la prueba de monotonía ni los tres casos de ejemplo lo detectaban: el valor
erróneo respetaba la monotonía y caía fuera de los casos. De ahí vienen los
checksums por fila, que sí lo habrían atrapado.

---

## 10. Supuestos propios del sistema (NO vienen de Arauco)

| Supuesto | Valor por defecto | Por qué |
|---|---|---|
| **Merma / despunte** en el modo detallado | 10 % **[estimado]** | Optimización de corte de paneles y despuntes. No aparece en el correo ni en las fichas. Editable, se puede poner en 0. |
| **Vanos de puertas y ventanas** | No se descuentan **[estimado]** | En CLT el vano se mecaniza *desde* el panel (la propia ficha muestra paneles con ventanas mecanizadas): el panel se paga completo. El sistema no tiene una opción de vanos — si tu proyecto justifica descontarlos, ingresa directamente la superficie neta de muro. |
| **Valor de la UF** | $40.879,04 al 4-sep-2026 **[verificado]** | Banco Central. Editable — se debe actualizar al día de la cotización. |
| **Holgura sobre el ratio** | 0 % **[estimado]** | Colchón opcional del usuario. En 0, el cubicaje es estrictamente el de Arauco. Si se usa, queda declarado en el resumen que va al correo. |

---

## 11. Qué este sistema NO calcula

- Transporte a obra, fundaciones y terminaciones — el correo los excluye textualmente.
- **Montaje, conectores y fijaciones [estimado]:** el correo no los menciona ni
  para incluirlos ni para excluirlos. El sistema asume que están fuera, que es lo
  habitual, pero conviene confirmarlo con Arauco antes de presupuestar el resto.
- Ingeniería estructural: los espesores y secciones que se ingresen deben venir
  del calculista.
- Precios finales: 26,5 / 4,3 / 2,0–3,3 UF/m³ son **referenciales** al 3-sep-2026.
  La cotización formal la emite Arauco con los antecedentes del punto 7.

---

## 12. Auditoría del 4-sep-2026

El sistema se auditó en dos frentes independientes: exactitud de los datos contra
el correo y las fichas (546 celdas de las tablas de losas comparadas una a una), y
código (bugs, casos de borde y paridad entre los dos motores).

Corregido a partir de esa auditoría:

1. La celda de resistencia al fuego de la sección 9 (el único error de datos).
2. El desglose de costos en Python cobraba la impregnación y dejaba el mecanizado
   en negativo cuando se pedía sin impregnar. El total siempre estuvo bien; el
   desglose no.
3. Entradas negativas: producían volúmenes y costos negativos con apariencia de
   cifra válida. Ahora se rechazan (Python) o se tratan como cero (web).
4. El resumen para el correo decía "estimación central" aunque el escenario fuera
   otro, no declaraba la holgura propia, e incluía el cubicaje de las partidas de
   ejemplo precargadas. Los tres corregidos.
5. Comillas y signos `<` `>` en la descripción de una partida truncaban el texto y
   podían inyectar HTML. Ahora se escapan.
6. Mensajes de error del CLI: ya no son *tracebacks* de Python.
7. Etiquetas de origen: los puntos marcados **[estimado]** de este documento que
   antes aparecían como si vinieran del correo.
