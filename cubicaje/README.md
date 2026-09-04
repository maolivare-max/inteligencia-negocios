# Cubicador de madera HILAM

Sistema para estimar **cuánta madera masiva (MLE / CLT) necesita una construcción**
y cuánto cuesta, usando los parámetros que entregó Lukas Villalobos (Subgerencia
Construcción en Madera, ARAUCO) en su correo del 3-sep-2026, más las fichas
técnicas de Hilam.

## Cómo se usa

**Calculadora web** — <https://maolivare-max.github.io/inteligencia-negocios/cubicaje/>
(también accesible desde el botón «Cubicador madera» del dashboard). Es un archivo
HTML sin dependencias: abrir `index.html` en el navegador funciona igual sin internet.

Tiene cuatro pestañas:

1. **Cubicaje rápido** — n.º de unidades, m² por unidad y sistema estructural →
   volumen en m³, costo en UF y CLP, desglose y calendario de pagos. Es el método
   que enseña Lukas: superficie × indicador m³/m².
2. **Detallado por elemento** — cuando ya hay planos: muros, losas y techumbre en
   m² × espesor CLT, vigas y pilares en secciones MLE. Compara el resultado contra
   el ratio de Arauco como control de cordura.
3. **Prediseño de losa CLT** — luz, apoyo y cargas → espesor mínimo de panel y
   resistencia al fuego, según las tablas de dimensionamiento de Hilam.
4. **Qué enviar a Arauco** — checklist de antecedentes y un resumen listo para
   pegar en el correo.

**Motor en Python** — mismo cálculo, para terminal o para importar:

```bash
python3 cubicador.py                                   # 20 casas de 100 m², MLE+CLT
python3 cubicador.py --m2-total 2000 --sistema clt --escenario max
python3 cubicador.py --losa 4 sa 150 200               # prediseño de losa
python3 cubicador.py --test                            # autotests
```

```python
from cubicador import cubicar, Detallado, espesor_losa
c = cubicar(2000, "mixto", unidades=20)
print(c.m3, c.total_uf, c.total_clp)
```

## Verificación

`python3 cubicador.py --test` corre 34 autotests. Los que importan:

- El ejemplo que da el propio correo (100 m² en MLE+CLT → **837,5 UF**) se
  reproduce exactamente. La calculadora web corre ese mismo autotest al cargar,
  a través de sus propios controles, y muestra el resultado en el pie de la página.
- Los rangos declarados (0,10–0,20 / 0,20–0,30 / 0,30–0,40 m³/m² y 32,8–34,1 UF/m³).
- Los tres casos de ejemplo de la ficha de losas CLT de Hilam.
- **Checksums de las 546 celdas** de las tablas de losas contra el PDF de Arauco:
  un solo dígito cambiado rompe la prueba.
- Las entradas inválidas (superficie negativa, cero unidades, UF en cero) se
  rechazan con un mensaje, en vez de producir un costo negativo.

El sistema fue auditado el 4-sep-2026 en datos y en código; lo corregido está en
la sección 12 de `PARAMETROS.md`.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | La calculadora. Autocontenida, sin dependencias externas. |
| `cubicador.py` | Motor de cálculo + CLI + autotests. Sin dependencias. |
| `PARAMETROS.md` | De dónde sale cada número, con etiqueta de origen y links. |

## Lo importante antes de usar el resultado

- Los precios (26,5 + 4,3 + 2,0–3,3 UF/m³) son **referenciales al 3-sep-2026**.
- **No incluyen** transporte, fundaciones, terminaciones, montaje ni conectores.
- El prediseño de losas es orientativo: el espesor definitivo lo fija el calculista.
- La cotización formal la emite Arauco con los antecedentes de la pestaña 4.
