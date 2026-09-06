# Módulo de métricas de cuenta propia — APAGADO

Este módulo conecta el dashboard con la cuenta publicitaria de Meta del usuario para
mostrar gasto, CPL, CTR y ROAS reales. **Hoy está apagado** (`config.json` →
`"conectado": false`). Está preparado para encenderse con un cambio de configuración,
sin tocar código.

## Por qué está apagado

Decisión del usuario al crear la Misión 5: **inteligencia primero, cuenta después.**
El dashboard de Publicidad arranca como tablero de inteligencia (anuncios de terceros,
biblioteca de guiones, targeting Chile). El módulo de métricas de cuenta propia se deja
listo pero sin activar, por tres razones:

1. No hay confirmación de que exista una cuenta de Meta Ads activa con gasto que valga
   la pena leer.
2. Encender un conector implica autorizar acceso de lectura (y en algunos casos de
   escritura) a la cuenta publicitaria; eso lo decide el usuario, no una rutina.
3. Mientras el módulo esté apagado, la rutina semanal **no hace ninguna llamada a un
   MCP de métricas** (ni Windsor.ai, ni Supermetrics, ni Motion). Cero llamadas, no
   "llamadas que fallan en silencio".

## La regla dura

**Mientras `"conectado"` sea `false`, el dashboard no muestra ninguna cifra de cuenta
propia. Ni de ejemplo, ni simulada, ni "de demostración".** El bloque de métricas se
renderiza como apagado (un aviso de que el módulo existe y cómo encenderlo), no como un
tablero con números grises.

Un número inventado en un tablero de gasto publicitario es peor que un tablero vacío:
alguien lo va a leer como real, va a decidir con él, y no hay forma de distinguirlo
después de una cifra verdadera. El corpus de este repo ya tuvo el problema de cifras de
otro mercado presentadas como locales; no se repite con la plata del usuario.

Esta regla obliga también a quien edite `build_dashboard.py` o los agentes: no hay
"datos de prueba" para este módulo. Para probar el render, se enciende contra una
cuenta real o se prueba el estado apagado.

## Qué contiene `config.json`

```json
{
  "conectado": false,
  "proveedor": null,
  "cuentas": [],
  "ultima_sincronizacion": null,
  "nota": "Módulo de métricas de cuenta propia apagado. Ver README.md para encenderlo."
}
```

| Campo | Apagado | Encendido |
|---|---|---|
| `conectado` | `false` | `true` |
| `proveedor` | `null` | `"windsor"`, `"supermetrics"` o `"motion"` (uno solo) |
| `cuentas` | `[]` | lista de cuentas de Meta Ads a leer; propuesta: objetos `{"id": "act_XXXXXXXX", "nombre": "descripción corta"}` — la forma final la fija quien implemente la lectura en `build_dashboard.py` |
| `ultima_sincronizacion` | `null` | fecha-hora ISO 8601 de la última lectura exitosa, la escribe la rutina |
| `nota` | texto fijo | se puede borrar o reemplazar por notas operativas |

`config.json` es la única fuente de verdad sobre si el módulo está encendido. El
dashboard y los agentes lo leen; nadie lo infiere de otra cosa.

## Conectores disponibles en el entorno para encenderlo

Los tres están instalados como servidores MCP en el entorno de Claude Code. Ninguno se
llama mientras el módulo esté apagado.

| Conector | Qué lee | Alcance | Cuándo conviene |
|---|---|---|---|
| **Windsor.ai** | Meta Ads y 350+ fuentes (Google Ads, TikTok, GA4, CRM) | Lectura y escritura (crear/pausar campañas, ajustar presupuestos) | Si más adelante se quiere cruzar Meta con Google Ads o GA4 en el mismo tablero. La escritura exige confirmación explícita del usuario por acción |
| **Supermetrics** | Meta Ads y 150+ fuentes de marketing | Lectura (consultas asíncronas por rango de fechas) | Si se quiere un extracto tabular estable para el dashboard, sin escribir en la cuenta |
| **Motion Creative Analytics** | **Solo Meta/Facebook** | Lectura: rendimiento por creativo, hook rate, desgloses demográficos, inspiración de competidores | Si lo que importa es qué creativo funciona (que es justamente el foco de la biblioteca de guiones), no el gasto agregado |

Elegir **uno** como `proveedor`. Si en el futuro se leen dos, se amplía el esquema;
no se improvisa.

## Pasos para encenderlo

En este orden. Ninguno es automatizable por la rutina; los da el usuario.

1. **Confirmar que existe una cuenta de Meta Ads activa** (Business Manager con cuenta
   publicitaria, con gasto reciente o campañas listas para salir). Sin cuenta no hay
   nada que conectar, y conectar una cuenta vacía solo produce un tablero de ceros que
   se confunde con un tablero roto.
2. **Autorizar el conector elegido** desde su propio flujo (Windsor.ai:
   `get_connector_authorization_url` para Meta Ads; Supermetrics: `accounts_discovery`
   sobre la fuente de Meta Ads; Motion: `get_auth_context` y el workspace con la cuenta).
   La autorización la hace el usuario en su navegador; la rutina solo puede pedir la URL.
3. **Editar `config.json`:** `"conectado": true`, `"proveedor"` con uno de los tres
   valores, y `"cuentas"` con la o las cuentas de Meta Ads que se van a leer.
   `"ultima_sincronizacion"` se deja en `null`: la escribe la primera lectura.
4. **Regenerar el dashboard:** hacer commit y push a `main` de `config.json`; la GitHub
   Action corre `build_dashboard.py` y publica. (Localmente se puede correr
   `python3 build_dashboard.py` para validar, descartando después los cambios en
   `dashboard.html` e `index.html`, que no se commitean a mano.)
5. **Primera lectura supervisada:** la primera vez que la rutina traiga cifras, el
   usuario las compara contra el Administrador de anuncios de Meta. Si no calzan, se
   vuelve a `"conectado": false` hasta entender por qué. Una cifra mal leída y publicada
   viola la regla dura igual que una inventada.

## Para apagarlo

`"conectado": false`. Nada más. El resto de la configuración puede quedar para no
tener que reconstruirla; el dashboard vuelve al estado apagado y la rutina deja de
llamar al conector.
