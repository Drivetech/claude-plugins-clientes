# Lectura del requerimiento — Ferremax (ejemplo)

> esquema: v1 · actualizado: 2026-09-02

> **Ejemplo ficticio.** "Ferremax" es un retail inventado y "Transportes Andes"
> una empresa de transporte inventada; los códigos, patentes y correos son de
> muestra. Sirve como referencia de un perfil bien hecho: cópialo y reemplázalo
> con los datos reales de tu mandante (idealmente con la skill `descubrir-mandante`).

Cómo se lee el correo de **Ferremax** y cómo se convierte en viajes del backlog.
Este archivo es lo único que cambia de un mandante a otro: el flujo (conseguir la
solicitud, confirmar, cargar, asignar, responder) vive en `SKILL.md` y es igual
para todos.

---

## 0 · Identidad del mandante

| | |
|---|---|
| **Nombre en el TMS** | Ferremax |
| **Razón social** | Comercial Ferremax S.A. |
| **RUT** | 76543210-9 |
| **Otros nombres con que aparece** | "Ferremax Retail" en sus correos; "CD Ferremax Pudahuel" en los documentos del centro de distribución |

Los documentos de esta operación vienen a nombre de la **razón social**, no del
nombre corto del TMS. Los dos son el mismo mandante.

## 1 · Cómo se reconoce el correo

- **Asunto:** contiene "Ventanas de entrega", normalmente seguido de la fecha
  de entrega (`Ventanas de entrega 07-08`).
- **Cuerpo:** un saludo, una línea del tipo *"favor considerar **6** tractos
  para las entregas"*, y **una o dos tablas** — una por tipo de camión.
- Suele venir un recordatorio sobre el uso de la app de seguimiento que pide el
  mandante. No afecta la carga, pero conviene repetirlo al responder.

El número de tractos de esa línea es un **chequeo útil**: tiene que calzar con
la cantidad de tractos distintos que necesita la primera vuelta (ver §6).

## 2 · La tabla

Columnas, en este orden:

```
ID | Carga | Empresa | Tienda | Tipo camion | Codigo Tienda | Patente rampla | Retorno | Fecha entrega | Vent.1 | Hora
```

**Cada fila es un viaje.** Si hay dos tablas, son el mismo formato separado por
tipo de camión (TIPO-A y TIPO-B): procésalas juntas, no son cosas distintas.

## 3 · Mapeo a `create_backlog_trips`

| Columna del correo | Campo del viaje | Regla |
|---|---|---|
| `Carga` (G0001234) | `code` | tal cual. Es la llave de idempotencia. |
| `ID` (40012) | `order_number` | tal cual (trazabilidad). |
| `Codigo Tienda` (T012) | `client.code` | el nombre sale del catálogo, no del correo. |
| `Tienda` (Sucursal Norte) | — | solo referencia; **no** lo uses como nombre. |
| `Fecha entrega` (05-08-2026) | `date` | `dd-mm-yyyy` → `yyyy-mm-dd`. |
| `Hora` (7:00) | `hour` | hora **LOCAL** tal cual: `YYYY-MM-DD HH:MM`. |
| `Tipo camion` (TIPO-A / TIPO-B) | `skills_required` | `[["TIPO-A"]]` o `[["TIPO-B"]]`. **Obligatorio** (§4). |
| `Tipo camion` + `Patente rampla` | `origin` | regla de origen (§5). |
| `Patente rampla` (AABB11) | `observations` | **solo la patente, sin prefijo**, incluido `000000`. |
| — | `type` | constante **"Full"**. |
| — | `group_name` | constante **"RETAIL"**. |
| — | `items` | constante `[{ "sku": "01", "qty": 1, "description": "Viaje" }]`. |

`Empresa`, `Retorno` y `Vent.1` **no se usan**: la ventana ya queda reflejada
en `hour`. `service_time` **no se envía** — lo hereda del origen (=30).

Ejemplo de una fila ya mapeada:

```json
{
  "code": "G0001234",
  "order_number": "40012",
  "client": { "code": "T012", "name": "Ferremax Sucursal Norte" },
  "items": [{ "sku": "01", "qty": 1, "description": "Viaje" }],
  "type": "Full",
  "group_name": "RETAIL",
  "origin": "CD01",
  "skills_required": [["TIPO-A"]],
  "observations": "AABB11",
  "date": "2026-08-05",
  "hour": "2026-08-05 07:00"
}
```

**Nombres de tienda:** resuelve cada `Codigo Tienda` con
`get_tms_catalog(kind="clients", search=<codigo>)` y usa el `code` y `name` que
devuelva la plataforma (`T012` → "Ferremax Sucursal Norte"). Si un código no
aparece, es tienda nueva: pregunta, no inventes.

> Los nombres de característica (`TIPO-A`/`TIPO-B`), de origen (`CD01`/`CD02`) y de
> grupo (`RETAIL`) son de ejemplo. Los reales de tu operación salen del catálogo
> (`get_tms_catalog`), no de este archivo.

## 4 · Característica de vehículo — obligatoria

**Ningún viaje de esta operación puede quedar sin característica.** Todo viaje
trae `Tipo camion` = **TIPO-A** o **TIPO-B** y eso viaja SIEMPRE en
`skills_required`: `[["TIPO-A"]]` o `[["TIPO-B"]]`. Nunca `[]`, nunca ausente,
nunca `null`.

Esta empresa tiene `skills_enabled=true` (léelo de
`get_tms_catalog kind=vehicle_skills`), así que la característica es **lo único**
que impide asignarle a la guía un móvil que no corresponde. Un viaje sin
característica acepta cualquier vehículo y el error recién se ve en terreno.

Si una fila trae el `Tipo camion` vacío, ilegible o con un valor distinto de los
del catálogo, **no la cargues**: pregunta. No asumas una.

## 5 · Regla de origen

Se lee la `Patente rampla`, aunque su valor vaya a `observations`:

- `Tipo camion == "TIPO-B"` **y** `Patente rampla == "000000"` → `origin = "CD02"`
  (Centro de Distribución Sur).
- En cualquier otro caso → `origin = "CD01"` (Centro de Distribución Norte).

## 6 · Ventanas: primera y segunda vuelta

- **Primera vuelta:** las salidas de **07:00 / 07:30 / 08:00**, una por tracto.
- **Segunda vuelta:** de **11:00 en adelante** (11:00, 12:00, 13:00, 14:00).
  Son repeticiones de los mismos tractos.

La cantidad de tractos distintos de la primera vuelta debería calzar con el
"considerar N tractos" del correo.

## 7 · Rampla vs tracto — la trampa de esta operación

La columna se llama `Patente rampla`, pero **no significa lo mismo en los dos
tipos de camión**:

- **TIPO-B → es el TRACTO.** La patente del correo es el móvil que hace el viaje.
  Propón ese vehículo y su conductor habitual como default. Excepción:
  `000000` = sin vehículo definido, hay que preguntar cuál usar.
- **TIPO-A → es una RAMPLA de verdad.** Las ramplas están registradas como
  vehículos de la faena (patente sin nombre de móvil, varias con la característica
  TIPO-A), así que es fácil confundirlas con tractos. **No las asignes.**

**Cómo distinguirlos** — no hay lista acá a propósito: la flota cambia. Sácalos
de `get_assignable_resources`, donde se separan solos:

- **Tracto** — trae `name` (nombre de móvil, tipo `T###`) y `conductor_habitual`.
- **Rampla** — viene **sin** nombre de móvil y sin conductor habitual, aunque
  tenga la característica.

Si algo no calza con esa regla, no adivines: pregúntale al usuario.

En ningún caso la rampla se asigna como acoplado (`trailer`): su patente ya
quedó en las observaciones del viaje.

## 8 · Criterio de asignación — rotación de tiendas

Sobre la regla dura de características (§4), que se cumple siempre, el criterio
de esta operación es:

> **En la semana, un conductor no debería repetir tienda. Al menos en la primera
> vuelta.**

Cómo aplicarlo:

- **La primera vuelta es donde el criterio manda.** Ahí trata de que a cada
  conductor le toque una tienda que no haya hecho en la semana. Normalmente hay
  más tiendas distintas en el día que tractos disponibles, así que casi siempre
  se puede.
- **En las segundas vueltas se relaja.** Ahí pesa más quién se desocupó y dónde
  quedó (§6): si la única opción razonable repite tienda, repite — pero dilo.
- **Mira la semana, no solo ayer.** Un conductor puede no haber ido ayer a esa
  tienda y sí anteayer. Arma la matriz con 5–7 días.
- **Los destinos lejanos** (las sucursales de otra región) son donde más se
  repite: son tramos largos y siempre caen en los mismos. Sacarlos de ahí es
  parte de rotar, pero alguien tiene que quedar disponible para esos viajes en la
  tarde. Cuando propongas sacarlos, adviértelo.

## 9 · Comunicación con el mandante

Todo va **en el mismo hilo** del correo de la solicitud, a los `responder_a`
configurados para este mandante.

**Confirmación de asignación.** Al cerrar la primera vuelta: tabla con tienda,
hora comprometida, patente y conductor. Deja dicho que es la primera vuelta y
que las ventanas de la tarde se confirman más tarde. Cierra repitiendo el
**recordatorio del uso de la app de seguimiento**, que es lo que ellos piden en
cada correo.

**Reportes durante el día.** *(Reglas por definir con el usuario — no inventes
una cadencia.)* Antes de dejar esto en automático hay que acordar con él:

- Cada cuánto va el reporte (¿al cierre de la primera vuelta? ¿mediodía y cierre?
  ¿solo cuando pasa algo?).
- Si les interesan los hitos de **origen** o solo los de destino.
- Si quieren la **permanencia en tienda** — probable, porque las ventanas de
  entrega son acotadas y la permanencia es lo que las hace calzar.
- Qué se informa cuando un viaje se atrasa respecto de su ventana: si se avisa
  apenas se detecta o recién en el reporte siguiente.

Mientras no esté acordado: arma el reporte solo cuando el usuario lo pida, y
déjaselo siempre como borrador.

### Cómo se leen los hitos en esta operación

Los dos orígenes (**CD01** Norte y **CD02** Sur) son **de la propia empresa de
transporte**, y **los camiones duermen ahí**. Eso cambia la lectura de dos campos:

- **`origin_arrival_datetime` es casi siempre del día anterior** — es cuando el
  móvil entró a pernoctar, no cuando llegó a cargar. **No lo reportes como
  "llegada al origen"**: queda absurdo y no mide nada. El hito útil del origen es
  la **salida** (`origin_departure_datetime`).
- **Los viajes de primera vuelta normalmente NO traen `load_datetime`**, porque
  se planifican el día anterior y el camión ya está en casa. Su ausencia **no es
  un incumplimiento**: no lo reportes como tal. En las segundas vueltas sí suele
  aparecer, porque se asignan durante el día con hora de carga planificada.

Los hitos de destino también vienen disparejos: es frecuente que un viaje
entregado tenga llegada pero no salida, y ahí **no hay permanencia que calcular**.
Informa la permanencia solo de los que tienen los dos hitos y di cuántos quedaron
sin dato.

## 10 · Particularidades de esta faena

- **Se equivocan seguido con el número de carga.** Que un `code` ya exista NO
  significa "ya se hizo": es frecuente que repitan o tipeen mal la guía. Trátalo
  siempre con el usuario (ver Paso 5.1 de `SKILL.md`), nunca lo ignores.
- **Formatos de carga mezclados.** Casi todas las guías son `G000xxxx`, pero de
  vez en cuando aparece una con otro formato (p.ej. `197818`). Cárgala tal cual
  —es la llave de idempotencia— pero **avísale al usuario**, porque suele ser un
  error de tipeo del mandante.
- **La faena puede no traer conductores propios en algunas consultas.**
  `get_assignable_resources` puede devolver vehículos y `drivers: []` cuando la
  llamas acotada con `search`. Llámala sin `search` para ver la dotación
  completa.

## 11 · Dudas abiertas

- [ ] El destino `88231` apareció en la muestra del 28-08 y **no está en el
      catálogo de clientes**. ¿Tienda nueva o typo del mandante? — preguntar a
      Ferremax antes de la próxima carga que lo traiga (abierta 2026-08-28).
- [ ] No hay regla escrita para desempatar cuando dos conductores califican igual
      y ninguno tiene la tienda asignada por rotación; hoy **se pregunta al
      asignar** — definir con el jefe de operaciones (abierta 2026-08-28).

Cuando una de estas se responda, la regla se escribe en la sección que corresponda
(§8 si es de asignación, §5 si es de origen, etc.) y la línea se borra de acá.
