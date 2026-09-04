#!/usr/bin/env python3
"""
Cubicador de madera masiva HILAM — motor de cálculo.

Misma lógica que cubicaje/index.html, para usar desde la terminal o importar
en otro script (por ejemplo, para cubicar varias tipologías de una vez).

Todos los parámetros vienen del correo de Lukas Villalobos (Arauco, Subgerencia
Construcción en Madera) del 3-sep-2026 y de las fichas técnicas Hilam. El origen
de cada número está documentado en cubicaje/PARAMETROS.md.

USO
    python3 cubicador.py                          # ejemplo: 20 casas de 100 m², MLE+CLT
    python3 cubicador.py --casas 20 --m2 100 --sistema mixto
    python3 cubicador.py --m2-total 2000 --sistema clt --escenario max --uf 40879
    python3 cubicador.py --test                   # corre los autotests

El escenario 'mid' (por defecto) usa el punto medio del rango que entrega Arauco.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field

# ─────────────────────────────────────────────────────────────────────────────
# PARÁMETROS — [mail] = textual del correo · [ficha] = ficha técnica Hilam
# ─────────────────────────────────────────────────────────────────────────────

# m³ de madera por m² de proyecto, por sistema estructural. [mail]
SISTEMAS = {
    "mle":   {"nombre": "Estructura MLE",       "min": 0.10, "max": 0.20},
    "mixto": {"nombre": "Estructura MLE + CLT", "min": 0.20, "max": 0.30},
    "clt":   {"nombre": "Estructura CLT",       "min": 0.30, "max": 0.40},
}

PRECIO_MADERA = 26.5        # UF/m³ [mail]
PRECIO_IMPREG = 4.3         # UF/m³ [mail]
PRECIO_CNC = {              # UF/m³ [mail] — el rango es 2,0 a 3,3
    "min": 2.0,
    "ref": 2.7,             # no está escrito en el correo: es el que reproduce
    "max": 3.3,             # su ejemplo de 837,5 UF (ver PARAMETROS.md §4)
}

UF_CLP = 40879.04           # Banco Central, 4-sep-2026 [verificado]

# Calendario de pagos estándar. [mail]
PAGOS = [
    (5,  "Anticipo — desarrollo del modelo",
         "Modelación en software especializado. 15 a 30 días según volumen y n.º de elementos."),
    (45, "Previo al inicio de fabricación",
         "Fabricación de 45 a 60 días una vez aprobado e ingresado el modelo final."),
    (50, "Saldo previo al despacho",
         "Antes del despacho desde fábrica hacia obra."),
]

# Dimensiones de producto. [ficha]
CLT_ESPESORES = [56, 80, 90, 100, 110, 120, 130, 150, 160, 170, 180, 200, 210, 240, 250, 280]
MLE_ANCHOS = [42, 65, 90, 120, 130, 138, 150, 185, 200, 250, 280, 300]
MLE_ALTOS = [60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390]

COTIZADOR_WEB_MIN, COTIZADOR_WEB_MAX = 5, 30   # m³ [mail]


def clt_capas(espesor_mm: int) -> int:
    """N.º de capas del panel CLT según espesor. [ficha]"""
    return 3 if espesor_mm <= 120 else (5 if espesor_mm <= 200 else 7)


# ─────────────────────────────────────────────────────────────────────────────
# CUBICAJE RÁPIDO (indicador m³/m²)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Cubicaje:
    """Resultado de cubicar por el indicador m³/m² del correo."""
    superficie_m2: float
    sistema: str
    unidades: int
    m3_min: float
    m3_mid: float
    m3_max: float
    # Los tres componentes del precio se guardan por separado: si se guardara
    # solo el total, el desglose tendría que deducir el CNC restando las
    # constantes del módulo y saldría negativo cuando no hay impregnación.
    precio_madera: float
    precio_impreg: float
    precio_cnc: float
    holgura_pct: float = 0.0
    uf_clp: float = UF_CLP
    escenario: str = "mid"

    @property
    def precio_uf_m3(self) -> float:
        return self.precio_madera + self.precio_impreg + self.precio_cnc

    @property
    def m3(self) -> float:
        return {"min": self.m3_min, "mid": self.m3_mid, "max": self.m3_max}[self.escenario]

    @property
    def m3_por_unidad(self) -> float:
        return self.m3 / self.unidades if self.unidades else 0.0

    @property
    def total_uf(self) -> float:
        return self.m3 * self.precio_uf_m3

    @property
    def total_clp(self) -> float:
        return self.total_uf * self.uf_clp

    @property
    def uf_por_m2(self) -> float:
        return self.total_uf / self.superficie_m2 if self.superficie_m2 else 0.0

    @property
    def ratio(self) -> float:
        """m³/m² efectivamente aplicado (incluye la holgura propia, si la hay)."""
        return self.m3 / self.superficie_m2 if self.superficie_m2 else 0.0

    @property
    def ratio_base(self) -> float:
        """m³/m² del correo de Arauco, sin la holgura propia."""
        return self.ratio / (1 + self.holgura_pct / 100)

    def desglose(self) -> list[tuple[str, float, float]]:
        """[(partida, UF/m³, UF total)] — suma exactamente total_uf."""
        return [
            ("Madera", self.precio_madera, self.m3 * self.precio_madera),
            ("Impregnación", self.precio_impreg, self.m3 * self.precio_impreg),
            ("Mecanizado CNC", self.precio_cnc, self.m3 * self.precio_cnc),
        ]

    def pagos(self) -> list[tuple[int, str, float, float, str]]:
        return [(pct, tit, self.total_uf * pct / 100, self.total_clp * pct / 100, det)
                for pct, tit, det in PAGOS]


def cubicar(superficie_m2: float, sistema: str = "mixto", *, unidades: int = 1,
            escenario: str = "mid", cnc: str = "ref", impregnacion: bool = True,
            holgura_pct: float = 0.0, uf_clp: float = UF_CLP) -> Cubicaje:
    """Cubica una construcción con el indicador m³/m² que entrega Arauco.

    superficie_m2 -- superficie construida total del proyecto (todos los pisos)
    sistema       -- 'mle' | 'mixto' | 'clt'
    escenario     -- 'min' | 'mid' | 'max' dentro del rango del sistema
    cnc           -- 'min' | 'ref' | 'max' del rango 2,0–3,3 UF/m³
    holgura_pct   -- colchón propio sobre el ratio (0 = estricto Arauco)
    """
    if sistema not in SISTEMAS:
        raise ValueError(f"sistema debe ser uno de {list(SISTEMAS)}, no {sistema!r}")
    if escenario not in ("min", "mid", "max"):
        raise ValueError("escenario debe ser 'min', 'mid' o 'max'")
    if cnc not in PRECIO_CNC:
        raise ValueError(f"cnc debe ser uno de {list(PRECIO_CNC)}")
    if unidades < 1:
        raise ValueError("tiene que haber al menos una unidad")
    if superficie_m2 < 0:
        raise ValueError("la superficie no puede ser negativa")
    if holgura_pct < 0:
        raise ValueError("la holgura no puede ser negativa (0 = estricto Arauco)")
    if uf_clp <= 0:
        raise ValueError("el valor de la UF tiene que ser mayor que cero")

    s = SISTEMAS[sistema]
    h = 1 + holgura_pct / 100

    return Cubicaje(
        superficie_m2=superficie_m2,
        sistema=sistema,
        unidades=unidades,
        m3_min=superficie_m2 * s["min"] * h,
        m3_mid=superficie_m2 * (s["min"] + s["max"]) / 2 * h,
        m3_max=superficie_m2 * s["max"] * h,
        precio_madera=PRECIO_MADERA,
        precio_impreg=PRECIO_IMPREG if impregnacion else 0.0,
        precio_cnc=PRECIO_CNC[cnc],
        holgura_pct=holgura_pct,
        uf_clp=uf_clp,
        escenario=escenario,
    )


# ─────────────────────────────────────────────────────────────────────────────
# CUBICAJE DETALLADO (por geometría de elementos)
# ─────────────────────────────────────────────────────────────────────────────

def volumen_clt(superficie_m2: float, espesor_mm: float) -> float:
    """m³ de panel CLT. Los vanos NO se descuentan: se mecanizan del panel."""
    return superficie_m2 * espesor_mm / 1000


def volumen_mle(cantidad: int, largo_m: float, ancho_mm: float, alto_mm: float) -> float:
    """m³ de piezas de madera laminada de sección rectangular."""
    return cantidad * largo_m * (ancho_mm / 1000) * (alto_mm / 1000)


@dataclass
class Detallado:
    """Cubicaje por elemento, con control contra el ratio m³/m² de Arauco."""
    merma_pct: float = 10.0        # [supuesto propio, no viene del correo]
    partidas: list = field(default_factory=list)

    def clt(self, desc: str, superficie_m2: float, espesor_mm: int) -> "Detallado":
        if espesor_mm not in CLT_ESPESORES:
            raise ValueError(
                f"{espesor_mm} mm no es un espesor de catálogo. Arauco fabrica: "
                f"{', '.join(str(e) for e in CLT_ESPESORES)} mm. "
                "(Ojo: la tabla de losas tabula 60 mm, pero el catálogo comercial parte en 56 mm.)")
        self.partidas.append(("CLT", desc, volumen_clt(superficie_m2, espesor_mm),
                              f"{superficie_m2:g} m² × {espesor_mm} mm"))
        return self

    def mle(self, desc: str, cantidad: int, largo_m: float,
            ancho_mm: int, alto_mm: int) -> "Detallado":
        self.partidas.append(("MLE", desc, volumen_mle(cantidad, largo_m, ancho_mm, alto_mm),
                              f"{cantidad} u × {largo_m:g} m × {ancho_mm}×{alto_mm} mm"))
        return self

    def neto(self, producto: str | None = None) -> float:
        return sum(v for p, _, v, _ in self.partidas if producto in (None, p))

    def total(self, producto: str | None = None) -> float:
        return self.neto(producto) * (1 + self.merma_pct / 100)

    def control(self, superficie_ref_m2: float, sistema: str = "mixto") -> str:
        """Compara el cubicaje detallado contra el rango m³/m² del correo."""
        if not superficie_ref_m2:
            return "Sin superficie de referencia: no se puede comparar."
        s, r = SISTEMAS[sistema], self.total() / superficie_ref_m2
        rango = f"{s['min']:.2f}–{s['max']:.2f}"
        if r < s["min"]:
            return (f"{r:.3f} m³/m² — BAJO el rango {rango} de {s['nombre']}. "
                    "Puede que falten partidas por ingresar.")
        if r > s["max"]:
            return (f"{r:.3f} m³/m² — SOBRE el rango {rango} de {s['nombre']}. "
                    "Revisa espesores y merma: hay margen de optimización.")
        return f"{r:.3f} m³/m² — dentro del rango {rango} de {s['nombre']}. Consistente."


# ─────────────────────────────────────────────────────────────────────────────
# PREDISEÑO DE LOSAS CLT
# ─────────────────────────────────────────────────────────────────────────────
# Tablas de la ficha "Tablas de dimensionamiento de losas de CLT Hilam" (2025),
# extraídas del PDF por su capa de texto (no por OCR).
# Columnas, en este orden: peso propio adicional 50 kgf/m² con cargas de uso
# [100, 200, 300, 500], luego pp 150 kgf/m² con [200, 300, 500] — la ficha no
# publica la combinación pp 150 con carga 100.
# PREDISEÑO REFERENCIAL: el espesor definitivo lo fija el calculista.

LOSA_ESPESORES = [60, 80, 90, 100, 110, 120, 130, 150, 160, 170, 180, 200, 210]

# Luz máxima [m] que salva cada panel.
_LOSA = {
    "sa": [
        [2.75, 2.50, 2.25, 1.75, 2.25, 2.00, 1.75],
        [3.75, 3.00, 3.00, 2.50, 3.00, 2.75, 2.50],
        [4.25, 3.25, 3.25, 2.75, 3.25, 3.00, 2.75],
        [4.50, 3.50, 3.50, 3.00, 3.25, 3.25, 3.00],
        [5.00, 4.00, 4.00, 3.50, 3.75, 3.75, 3.50],
        [5.50, 4.00, 4.00, 3.50, 4.00, 4.00, 3.50],
        [5.75, 4.25, 4.25, 4.00, 4.25, 4.25, 3.75],
        [6.25, 4.75, 4.75, 4.25, 4.75, 4.75, 4.25],
        [6.50, 4.75, 4.75, 4.25, 4.75, 4.75, 4.25],
        [7.00, 5.25, 5.25, 4.50, 5.25, 5.25, 4.50],
        [7.00, 5.50, 5.50, 5.00, 5.50, 5.50, 4.75],
        [7.50, 5.75, 5.75, 5.50, 5.50, 5.75, 5.00],
        [7.50, 5.75, 5.75, 5.50, 5.75, 5.75, 5.00],
    ],
    "cont": [
        [3.75, 3.00, 3.00, 2.50, 3.00, 2.75, 2.25],
        [5.00, 3.50, 3.50, 3.25, 3.50, 3.50, 3.25],
        [5.50, 4.00, 4.00, 3.75, 4.00, 4.00, 3.50],
        [6.00, 4.25, 4.25, 4.25, 4.25, 4.25, 3.75],
        [6.50, 4.50, 4.50, 4.25, 4.50, 4.50, 4.25],
        [7.00, 4.75, 4.75, 4.50, 4.75, 4.75, 4.50],
        [7.25, 5.00, 5.00, 4.75, 5.00, 5.00, 4.75],
        [7.75, 5.50, 5.50, 5.50, 5.50, 5.50, 5.25],
        [8.00, 5.75, 5.75, 5.50, 5.75, 5.75, 5.50],
        [8.50, 6.25, 6.00, 6.00, 6.25, 6.00, 5.75],
        [8.50, 6.50, 6.50, 6.25, 6.50, 6.50, 6.00],
        [9.50, 6.75, 6.50, 6.75, 6.75, 6.50, 6.50],
        [9.50, 6.75, 6.75, 6.75, 6.75, 6.75, 6.50],
    ],
    "vol": [
        [1.25, 1.00, 1.00, 0.75, 1.00, 0.75, 0.75],
        [1.75, 1.50, 1.25, 1.00, 1.25, 1.25, 1.00],
        [2.00, 1.50, 1.50, 1.25, 1.50, 1.25, 1.25],
        [2.00, 1.75, 1.50, 1.25, 1.50, 1.50, 1.25],
        [2.25, 2.00, 1.75, 1.50, 1.50, 1.50, 1.25],
        [2.50, 2.25, 2.00, 1.75, 1.75, 1.75, 1.50],
        [2.75, 2.25, 2.00, 1.75, 2.00, 1.75, 1.50],
        [3.00, 2.50, 2.25, 2.00, 2.00, 2.00, 1.75],
        [3.00, 2.75, 2.50, 2.00, 2.25, 2.00, 1.75],
        [3.25, 3.00, 2.50, 2.25, 2.50, 2.25, 2.00],
        [3.50, 3.00, 2.75, 2.50, 2.50, 2.50, 2.00],
        [3.75, 3.25, 3.00, 2.50, 2.75, 2.50, 2.25],
        [3.75, 3.50, 3.00, 2.75, 3.00, 2.75, 2.50],
    ],
}

# Resistencia al fuego [minutos] de la misma solución, con el CLT a la vista por
# debajo (sin revestimiento). Segunda tabla de la misma ficha.
# OGUC: se exige F-60 para losas residenciales de hasta 4 pisos; F-30 hasta 2 pisos.
_RF = {
    "sa": [
        [30, 30, 30, 30, 30, 30, 15],
        [60, 60, 30, 30, 30, 30, 30],
        [60, 60, 30, 30, 30, 30, 30],
        [60, 60, 30, 30, 30, 30, 30],
        [90, 90, 60, 60, 60, 60, 60],
        [90, 90, 60, 60, 60, 60, 60],
        [90, 90, 60, 60, 60, 60, 60],
        [90, 90, 90, 90, 90, 90, 90],
        [90, 90, 90, 90, 90, 90, 90],
        [90, 90, 90, 90, 90, 90, 90],
        [120, 120, 120, 120, 120, 120, 90],
        [120, 120, 120, 120, 120, 120, 120],
        [120, 120, 120, 120, 120, 120, 120],
    ],
    "cont": [
        [30, 15, 15, 15, 15, 15, 15],
        [30, 30, 30, 30, 30, 30, 30],
        [30, 30, 30, 30, 30, 30, 30],
        [30, 30, 30, 30, 30, 30, 30],
        [60, 30, 30, 30, 30, 30, 30],
        [60, 60, 60, 30, 60, 60, 30],
        [60, 60, 60, 60, 60, 60, 60],
        [60, 90, 90, 90, 60, 60, 90],
        [60, 90, 90, 90, 60, 60, 90],
        [90, 90, 90, 90, 90, 90, 90],
        [120, 120, 120, 90, 120, 120, 90],
        [120, 120, 120, 90, 120, 120, 90],
        [120, 120, 120, 90, 120, 120, 90],
    ],
    "vol": [
        [30, 30, 30, 30, 30, 30, 30],
        [60, 60, 60, 60, 60, 60, 60],
        [60, 60, 60, 60, 60, 60, 60],
        [90, 60, 60, 60, 60, 60, 60],
        [90, 90, 90, 90, 90, 90, 90],
        [90, 90, 90, 90, 90, 90, 90],
        [90, 90, 90, 90, 90, 90, 90],
        [90, 90, 90, 90, 90, 90, 90],
        [90, 90, 90, 90, 90, 90, 90],
        [90, 90, 90, 90, 90, 90, 90],
        [120, 120, 120, 120, 120, 120, 120],
        [120, 120, 120, 120, 120, 120, 120],
        [120, 120, 120, 120, 120, 120, 120],
    ],
}

_COL = {50: {100: 0, 200: 1, 300: 2, 500: 3}, 150: {200: 4, 300: 5, 500: 6}}


def espesor_losa(luz_m: float, apoyo: str = "sa", peso_propio: int = 150,
                 carga_uso: int = 200) -> tuple[int, float, int] | None:
    """Prediseño de losa CLT: (espesor mm, luz máxima del panel m, resistencia al fuego min).

    apoyo -- 'sa' (simplemente apoyado), 'cont' (continuo 2 tramos), 'vol' (voladizo)
    Devuelve None si ningún panel tabulado cubre esa luz.
    PREDISEÑO REFERENCIAL — validar con el calculista y con la ficha original.
    """
    if apoyo not in _LOSA:
        raise ValueError("apoyo debe ser 'sa', 'cont' o 'vol'")
    if peso_propio not in _COL or carga_uso not in _COL[peso_propio]:
        raise ValueError("combinación de peso propio / carga de uso no tabulada por Arauco")
    col = _COL[peso_propio][carga_uso]
    for i, esp in enumerate(LOSA_ESPESORES):
        if _LOSA[apoyo][i][col] >= luz_m:
            return esp, _LOSA[apoyo][i][col], _RF[apoyo][i][col]
    return None


# ─────────────────────────────────────────────────────────────────────────────
# SALIDA POR CONSOLA
# ─────────────────────────────────────────────────────────────────────────────

def _n(v: float, d: int = 2) -> str:
    """Número en formato chileno: 1.234,56"""
    return f"{v:,.{d}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def _clp(v: float) -> str:
    return "$" + _n(v, 0)


ESCENARIOS = {"min": "eficiente (extremo bajo del rango)",
              "mid": "central (punto medio del rango)",
              "max": "intensivo (extremo alto del rango)"}


def informe(c: Cubicaje) -> str:
    s = SISTEMAS[c.sistema]
    L = ["=" * 68,
         "CUBICAJE PRELIMINAR — ESTRUCTURA EN MADERA MASIVA HILAM",
         "Parámetros: correo de Lukas Villalobos (ARAUCO), 3-sep-2026",
         "=" * 68, "",
         "PROYECTO",
         f"  Unidades              {c.unidades}",
         f"  Superficie total      {_n(c.superficie_m2, 0)} m²",
         f"  Sistema               {s['nombre']}  ({_n(s['min'])}–{_n(s['max'])} m³/m²)",
         f"  Escenario             {ESCENARIOS[c.escenario]}"]
    if c.holgura_pct:
        L.append(f"  Holgura aplicada      +{_n(c.holgura_pct, 0)} % sobre el ratio "
                 f"— supuesto propio, NO de Arauco")
        L.append(f"                        ratio {_n(c.ratio_base, 3)} → {_n(c.ratio, 3)} m³/m²")
    L += ["",
          "VOLUMEN DE MADERA",
          f"  Rango del sistema     {_n(c.m3_min, 1)} a {_n(c.m3_max, 1)} m³",
          f"  Estimación aplicada   {_n(c.m3, 1)} m³   ({_n(c.m3_por_unidad)} m³ por unidad)", "",
          f"COSTO REFERENCIAL DE MATERIAL  ({_n(c.precio_uf_m3)} UF/m³)"]
    for nombre, uf_m3, uf in c.desglose():
        L.append(f"  {nombre:<20} {_n(uf_m3):>6} UF/m³   {_n(uf, 1):>10} UF   {_clp(uf * c.uf_clp):>16}")
    L += [f"  {'TOTAL':<20} {_n(c.precio_uf_m3):>6} UF/m³   {_n(c.total_uf, 1):>10} UF   {_clp(c.total_clp):>16}",
          f"  Por m²: {_n(c.uf_por_m2)} UF/m²   ·   UF = {_clp(c.uf_clp)}",
          '  El correo excluye "transporte, fundaciones, terminaciones ni otros costos',
          "  asociados al proyecto\". Montaje y conectores: confirmar con Arauco.", "",
          "CALENDARIO DE PAGOS (condiciones estándar Arauco)"]
    for pct, tit, uf, clp_, det in c.pagos():
        L.append(f"  {pct:>3}%  {_n(uf, 1):>10} UF  {_clp(clp_):>16}   {tit}")
        L.append(f"        {det}")
    L += ["  Piso estimado hasta el despacho desde fábrica: 60 a 90 días (suma de los dos",
          "  plazos del correo; no incluye el tiempo de aprobación del modelo).", ""]

    if COTIZADOR_WEB_MIN <= c.m3 <= COTIZADOR_WEB_MAX:
        L.append(f"NOTA: {_n(c.m3, 1)} m³ está en el rango 5–30 m³ → Arauco recomienda su cotizador web:")
        L.append("      https://arauco.com/hilam/cotizador/")
    else:
        L.append(f"NOTA: {_n(c.m3, 1)} m³ está fuera del rango 5–30 m³ del cotizador web;")
        L.append("      consultar la vía de cotización con Construcción en Madera.")
    L += ["", "ANTECEDENTES QUE PIDE ARAUCO PARA COTIZAR",
          "  [ ] Planos .dwg + EE.TT. de arquitectura",
          "  [ ] Planos de ingeniería y memoria de cálculo",
          "  [ ] Modelo BIM en IFC (deseable)",
          "  [ ] Estado de la obra (estudio / diseño / licitación / ejecución)",
          "  [ ] Material: CLT / MLE / ambos",
          "  [ ] Superficie aproximada en m²",
          "  [ ] Fecha estimada de entrega de la madera en obra",
          "  [ ] Fecha máxima de entrega de la cotización"]
    return "\n".join(L)


# ─────────────────────────────────────────────────────────────────────────────
# AUTOTESTS
# ─────────────────────────────────────────────────────────────────────────────

def _tests() -> int:
    fallos = []

    def check(nombre, cond, detalle=""):
        print(f"  {'✓' if cond else '✗'} {nombre}" + (f"  {detalle}" if detalle and not cond else ""))
        if not cond:
            fallos.append(nombre)

    print("Autotests del cubicador\n")

    # El ejemplo que entrega Lukas en el correo: 100 m² en MLE+CLT → 837,5 UF.
    c = cubicar(100, "mixto")
    check("Ejemplo del correo: 100 m² MLE+CLT = 25 m³", abs(c.m3 - 25) < 1e-9, f"da {c.m3}")
    check("Ejemplo del correo: precio 33,5 UF/m³", abs(c.precio_uf_m3 - 33.5) < 1e-9, f"da {c.precio_uf_m3}")
    check("Ejemplo del correo: total 837,5 UF", abs(c.total_uf - 837.5) < 1e-9, f"da {c.total_uf}")

    # Rangos declarados en el correo.
    check("Rango total del material 32,8–34,1 UF/m³",
          abs(cubicar(1, "mle", cnc="min").precio_uf_m3 - 32.8) < 1e-9
          and abs(cubicar(1, "mle", cnc="max").precio_uf_m3 - 34.1) < 1e-9)
    check("MLE 0,10–0,20 m³/m²", (cubicar(100, "mle").m3_min, cubicar(100, "mle").m3_max) == (10, 20))
    check("CLT 0,30–0,40 m³/m²", (cubicar(100, "clt").m3_min, cubicar(100, "clt").m3_max) == (30, 40))

    check("MLE+CLT 0,20–0,30 m³/m²", (cubicar(100, "mixto").m3_min, cubicar(100, "mixto").m3_max) == (20, 30))

    # El desglose cobra cada partida a su propio precio (no deducido por resta).
    d0 = c.desglose()
    check("Desglose usa los precios del correo",
          [round(v, 2) for _, v, _ in d0] == [26.5, 4.3, 2.7])
    check("Desglose suma el total", abs(sum(uf for _, _, uf in d0) - c.total_uf) < 1e-9)
    # Los pagos suman el 100 %.
    check("Pagos suman 100%", abs(sum(uf for _, _, uf, _, _ in c.pagos()) - c.total_uf) < 1e-9)

    # Sin impregnación baja exactamente 4,3 UF/m³ — y el desglose lo refleja:
    # la impregnación queda en 0 y el CNC NO se vuelve negativo.
    sin_imp = cubicar(100, "mixto", impregnacion=False, cnc="max")
    check("Sin impregnación: -4,3 UF/m³", abs(sin_imp.precio_uf_m3 - 29.8) < 1e-9)
    check("Sin impregnación: desglose 26,5 / 0 / 3,3 (CNC nunca negativo)",
          [round(v, 2) for _, v, _ in sin_imp.desglose()] == [26.5, 0.0, 3.3],
          f"da {[round(v, 2) for _, v, _ in sin_imp.desglose()]}")

    # Holgura del 10 % sube el volumen un 10 % y queda registrada para el informe.
    hol = cubicar(100, "mixto", holgura_pct=10)
    check("Holgura 10% sube 10% el volumen", abs(hol.m3 - 27.5) < 1e-9)
    check("Holgura queda visible en el informe",
          abs(hol.ratio - 0.275) < 1e-9 and abs(hol.ratio_base - 0.25) < 1e-9
          and "Holgura" in informe(hol) and "NO de Arauco" in informe(hol))

    # Entradas inválidas: error explicado, no un resultado negativo.
    for etiqueta, kwargs in [("superficie negativa", {"superficie_m2": -100}),
                             ("0 unidades", {"unidades": 0}),
                             ("holgura negativa", {"holgura_pct": -50}),
                             ("UF en 0", {"uf_clp": 0})]:
        base = {"superficie_m2": 100, "sistema": "mixto"}
        base.update(kwargs)
        try:
            cubicar(base.pop("superficie_m2"), base.pop("sistema"), **base)
            check(f"Rechaza {etiqueta}", False, "no lanzó ValueError")
        except ValueError:
            check(f"Rechaza {etiqueta}", True)

    # Los tres casos de ejemplo que publica la propia ficha Hilam validan que la
    # tabla esté bien transcrita y bien alineada por columnas.
    # Caso 1: simplemente apoyado, pp 150, carga 200, luz 4 m → 120 mm, F-60.
    r = espesor_losa(4.0, "sa", 150, 200)
    check("Ficha Hilam caso 1: SA, pp150, 200 kgf/m², 4 m → CLT 120 mm / F-60",
          r == (120, 4.00, 60), f"da {r}")
    # Caso 2: misma condición pero continuo en 2 tramos → 90 mm, F-30.
    r2 = espesor_losa(4.0, "cont", 150, 200)
    check("Ficha Hilam caso 2: continuo, pp150, 200 kgf/m², 4 m → CLT 90 mm / F-30",
          r2 == (90, 4.00, 30), f"da {r2}")
    # Caso 3: voladizo, pp150, carga 200, luz 2 m. La ficha concluye 120 mm, pero
    # su propia tabla da 1,75 m para ese panel: 2,00 m recién se alcanza con
    # 130 mm. Se respeta la tabla, que es el dato duro y además el conservador.
    r3 = espesor_losa(2.0, "vol", 150, 200)
    check("Ficha Hilam caso 3: voladizo, pp150, 200 kgf/m², 2 m → CLT 130 mm (tabla) / F-90",
          r3 == (130, 2.00, 90), f"da {r3}")
    check("Caso 3: el panel de 120 mm que menciona la ficha no llega a 2 m",
          _LOSA["vol"][LOSA_ESPESORES.index(120)][_COL[150][200]] == 1.75)
    # Luz imposible.
    check("Luz fuera de tabla devuelve None", espesor_losa(12.0, "sa", 150, 500) is None)

    # Coherencia interna: más espesor nunca salva menos luz ni resiste menos fuego.
    mono = all(t[k][i][c_] <= t[k][i + 1][c_]
               for t in (_LOSA, _RF) for k in t
               for i in range(len(t[k]) - 1) for c_ in range(7))
    check("Tablas de losa monótonas respecto del espesor", mono)
    check("Tablas de losa completas (13 espesores × 7 columnas)",
          all(len(t[k]) == len(LOSA_ESPESORES) and all(len(f) == 7 for f in t[k])
              for t in (_LOSA, _RF) for k in t))

    # Suma de cada fila, tomada del PDF de Arauco. Un solo dígito cambiado en
    # cualquiera de las 546 celdas rompe su checksum. La monotonía no basta:
    # una celda equivocada puede respetarla (así se coló un F-60 donde la ficha
    # dice F-30, en continuo 110 mm).
    CHECKSUM_LUZ = {  # (sa, cont, vol) por espesor
        60: (15.25, 20.25, 6.50), 80: (20.50, 25.50, 9.00), 90: (22.50, 28.75, 10.25),
        100: (24.00, 31.00, 10.75), 110: (27.50, 33.00, 11.75), 120: (28.50, 35.00, 13.50),
        130: (30.50, 36.75, 14.00), 150: (33.75, 40.50, 15.50), 160: (34.00, 42.00, 16.25),
        170: (37.00, 44.75, 17.75), 180: (38.75, 46.75, 18.75), 200: (40.75, 49.25, 20.00),
        210: (41.00, 49.75, 21.25)}
    CHECKSUM_RF = {
        60: (195, 120, 210), 80: (270, 210, 420), 90: (270, 210, 420),
        100: (270, 210, 450), 110: (480, 240, 630), 120: (480, 360, 630),
        130: (480, 420, 630), 150: (630, 540, 630), 160: (630, 540, 630),
        170: (630, 630, 630), 180: (810, 780, 840), 200: (840, 780, 840),
        210: (840, 780, 840)}
    malas = []
    for i, esp in enumerate(LOSA_ESPESORES):
        for tabla, esperado, nombre in ((_LOSA, CHECKSUM_LUZ, "luz"), (_RF, CHECKSUM_RF, "fuego")):
            for j, cond in enumerate(("sa", "cont", "vol")):
                if abs(sum(tabla[cond][i]) - esperado[esp][j]) > 1e-9:
                    malas.append(f"{nombre}/{cond}/{esp}mm")
    check("Checksums de las 546 celdas contra el PDF de Arauco", not malas, f"difieren: {malas}")

    # Geometría del modo detallado.
    check("CLT: 100 m² × 120 mm = 12 m³", abs(volumen_clt(100, 120) - 12) < 1e-9)
    check("MLE: 10 u × 5 m × 120×300 mm = 1,8 m³", abs(volumen_mle(10, 5, 120, 300) - 1.8) < 1e-9)
    d = Detallado(merma_pct=10).clt("muros", 100, 100).mle("vigas", 10, 5, 120, 300)
    check("Detallado aplica merma", abs(d.total() - (10 + 1.8) * 1.1) < 1e-9)
    check("Detallado separa por producto", abs(d.total("CLT") - 11.0) < 1e-9)
    try:
        Detallado().clt("losa", 100, 60)
        check("Rechaza un espesor CLT fuera de catálogo (60 mm)", False, "no lanzó ValueError")
    except ValueError:
        check("Rechaza un espesor CLT fuera de catálogo (60 mm)", True)

    # Las tres ramas del control de cordura contra el ratio del correo.
    check("Control: dentro del rango", "dentro del rango" in
          Detallado(merma_pct=0).clt("m", 100, 250).control(100, "mixto"))
    check("Control: bajo el rango", "BAJO el rango" in
          Detallado(merma_pct=0).clt("m", 100, 100).control(100, "clt"))
    check("Control: sobre el rango", "SOBRE el rango" in
          Detallado(merma_pct=0).clt("m", 100, 250).control(100, "mle"))
    check("Control: sin superficie de referencia", "no se puede comparar" in
          Detallado().clt("m", 100, 100).control(0))

    # El informe se arma sin reventar y trae las cifras clave.
    inf = informe(c)
    check("informe() incluye total, pagos y checklist",
          "837,5 UF" in inf and "5%" in inf and "IFC" in inf and "33,50 UF/m³" in inf)

    print(f"\n{'TODO OK' if not fallos else f'{len(fallos)} FALLO(S): ' + ', '.join(fallos)}")
    return 0 if not fallos else 1


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(
        description="Cubicador de madera masiva HILAM (parámetros Arauco, 3-sep-2026).",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--casas", type=int, default=20, help="n.º de unidades iguales (default 20)")
    p.add_argument("--m2", type=float, default=100, help="m² construidos por unidad (default 100)")
    p.add_argument("--m2-total", type=float,
                   help="superficie total del proyecto; reemplaza a --casas × --m2 para el volumen "
                        "(las unidades se deducen de --casas si lo pasas, o de --m2-total / --m2)")
    p.add_argument("--sistema", choices=list(SISTEMAS), default="mixto")
    p.add_argument("--escenario", choices=["min", "mid", "max"], default="mid")
    p.add_argument("--cnc", choices=list(PRECIO_CNC), default="ref", help="mecanizado CNC (default ref = 2,7)")
    p.add_argument("--sin-impregnacion", action="store_true")
    p.add_argument("--holgura", type=float, default=0.0, help="%% de holgura propia sobre el ratio")
    p.add_argument("--uf", type=float, default=UF_CLP, help=f"valor de la UF en CLP (default {UF_CLP})")
    p.add_argument("--losa", nargs=4, metavar=("LUZ", "APOYO", "PP", "CARGA"),
                   help="prediseño de losa CLT: LUZ(m) APOYO(sa|cont|vol) PP(50|150) CARGA(100|200|300|500)")
    p.add_argument("--test", action="store_true", help="corre los autotests y sale")
    a = p.parse_args()

    if a.test:
        return _tests()

    if a.losa:
        # Errores de tipeo salen como mensaje de argparse, no como traceback.
        try:
            luz, apoyo = float(a.losa[0]), a.losa[1]
            pp, cu = int(float(a.losa[2])), int(float(a.losa[3]))
        except ValueError:
            p.error("--losa espera LUZ y cargas numéricas, por ejemplo: --losa 4 sa 150 200")
        if not (luz > 0):
            p.error("la luz tiene que ser mayor que cero, por ejemplo: --losa 4 sa 150 200")
        try:
            r = espesor_losa(luz, apoyo, pp, cu)
        except ValueError as e:
            p.error(f"{e}. Combinaciones válidas: APOYO sa|cont|vol · "
                    "PP 50 con CARGA 100|200|300|500 · PP 150 con CARGA 200|300|500")
        if r is None:
            print(f"Ningún panel tabulado cubre {_n(luz)} m en esa condición. "
                  "Reduce la luz con un apoyo intermedio o pasa a solución mixta CLT+MLE.")
        else:
            esp, lmax, rf = r
            print(f"Losa CLT: espesor mínimo {esp} mm ({clt_capas(esp)} capas) — "
                  f"salva hasta {_n(lmax)} m (pides {_n(luz)} m).")
            if esp == 60:
                print("      OJO: el catálogo comercial no ofrece 60 mm; el panel equivalente es de")
                print("      56 mm y salva MENOS luz. Usa 80 mm o confirma el 56 mm con Arauco.")
            print(f"Volumen: {esp/1000:.3f} m³ por m² de losa · peso propio ≈ {_n(esp/1000*500, 0)} kg/m².")
            print(f"Resistencia al fuego: F-{rf} con el CLT a la vista por debajo (sin revestimiento).")
            if rf < 60:
                print("      OGUC exige F-60 en losas residenciales de hasta 4 pisos (F-30 hasta 2 pisos):")
                print("      sube el espesor o protege con yeso cartón si necesitas más.")
            print("PREDISEÑO REFERENCIAL — validar con el calculista y con la ficha de Arauco.")
        return 0

    # --casas explícito manda siempre sobre la deducción a partir de --m2-total.
    casas_explicito = any(x.startswith("--casas") for x in sys.argv[1:])
    if a.m2_total is not None:
        sup = a.m2_total
        unidades = a.casas if casas_explicito else max(round(sup / a.m2) if a.m2 else 1, 1)
    else:
        sup, unidades = a.casas * a.m2, a.casas

    try:
        c = cubicar(sup, a.sistema, unidades=unidades, escenario=a.escenario, cnc=a.cnc,
                    impregnacion=not a.sin_impregnacion, holgura_pct=a.holgura, uf_clp=a.uf)
    except ValueError as e:
        p.error(str(e))
    print(informe(c))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
