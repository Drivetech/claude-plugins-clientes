# Anatomía de un perfil de mandante (`mandantes/<nombre>.md`)

Un perfil es un archivo Markdown que le dice a la skill de carga **cómo se lee un
mandante y cómo se traduce su solicitud a viajes del backlog**. Es lo único que
cambia de un mandante a otro; el flujo vive en el `SKILL.md` de la skill de carga
y es igual para todos.

Toma `cargar-viajes-backlog/mandantes/ejemplo.md` como el ejemplo de referencia de
uno bien hecho. Esta es la anatomía a completar. No todas las secciones aplican a
todos los mandantes — omite las que no correspondan, pero no omitas una por no
haber preguntado.

## Secciones

**1 · Cómo se reconoce la solicitud.** Según el intake: para `correo`, asunto y
remitente; para `archivo`, la ubicación y el patrón de nombre. La forma del
contenido (cuerpo, adjunto, planilla). Cualquier chequeo útil (p.ej. "dice
*considerar N tractos*" que debe calzar con la primera vuelta). El intake mismo se
guarda en el `intake_config` del perfil (backend); acá va cómo se reconoce y se lee.

**2 · El formato de la solicitud.** Si es tabla: las columnas en orden y qué es
una fila. Si es Excel/CSV: hoja, fila de encabezado, columnas. Si es PDF: cómo se
ve la tabla. Deja claro qué es **un viaje** (normalmente, una fila).

**3 · Mapeo campo por campo** a `create_backlog_trips` (ver tabla de campos
abajo). Una fila por columna del origen, con la regla de conversión. Incluye un
ejemplo de una fila ya mapeada en JSON.

**4 · Características de vehículo — sí o no.** Si la operación clasifica por tipo
(S28/C14 o equivalentes): es **obligatoria**, va en `skills_required`, y una fila
sin ella no se carga. Si **no** clasifica: `skills_required` va **vacío** y
cualquier vehículo califica — déjalo escrito explícito para que no se lea como
dato faltante.

**5 · Regla de origen.** Constante, o dependiente de alguna columna. Escribe la
regla, con los códigos de origen reales del catálogo.

**6 · Ventanas: primera y segunda vuelta.** Qué horas/ventanas son salidas de la
mañana (una por móvil) y cuáles repeticiones de la tarde. La skill asigna primero
solo las primeras vueltas.

**7 · Trampas de la faena.** Lo que confunde: una columna que se llama de una
forma pero significa otra, ramplas que parecen tractos, orígenes donde los
camiones pernoctan, etc.

**8 · Reglas de asignación.** El corazón operativo del perfil (sale de la
entrevista del Paso 6.1). Escribe como reglas accionables: qué determina quién
toma un viaje (conductor/vehículo fijo por ruta/cliente/origen, o reparto), cómo
se elige el vehículo (característica, capacidad vs volumen/peso, o cualquiera),
orden y prioridad (turnos/vueltas, ventanas, qué va primero), restricciones (tope
por conductor, destinos que no se repiten, rutas dedicadas), cómo se desempata
entre candidatos, y qué es fijo vs. qué se decide cada día. Lo que no esté
definido: "preguntar al usuario al asignar" — nunca lo inventes.

**9 · Comunicación con el mandante.** Qué se confirma al asignar; si hay reporte
de avance, cada cuánto y con qué datos (¿permanencia en destino? ¿hitos de
origen?); qué se informa ante un atraso; a quién se responde. Incluye cómo se
leen los hitos en esta operación si tienen una lectura especial (p.ej. origen que
es de la propia empresa y por eso `origin_arrival_datetime` es del día anterior).

**10 · Particularidades.** Cualquier cosa propia: que se equivocan con el número
de guía seguido, formatos de carga mezclados, faenas sin conductores propios en
ciertas consultas, etc.

## Campos de `create_backlog_trips`

| Campo | Qué es | Notas |
|---|---|---|
| `code` | Llave de idempotencia (nº de guía/carga del mandante). | Tal cual, sin normalizar. Releer no duplica gracias a esto. |
| `order_number` | Nº de orden/ID interno del mandante. | Trazabilidad. |
| `client.code` | Código del cliente/destino. | Resolver el `name` con `get_tms_catalog`, no tomarlo del archivo. |
| `date` | Fecha de entrega. | `yyyy-mm-dd`. |
| `hour` | Hora comprometida. | `YYYY-MM-DD HH:MM`, **hora LOCAL — NO convertir**. La tool la pasa a UTC. |
| `skills_required` | Características exigidas. | Lista de listas (`[["S28"]]`). Vacío si la operación no clasifica. |
| `origin` | Origen del viaje. | Código de origen del catálogo. Puede ser constante o por regla. |
| `type` | Tipo de viaje. | Constante de la operación (p.ej. "Full"). Debe existir en el catálogo. |
| `group_name` | Grupo/faena de vehículos. | Constante de la operación. Debe existir en el catálogo. |
| `items` | Ítems del viaje. | Suele ser constante (p.ej. `[{ "sku": "01", "qty": 1, "description": "Viaje" }]`). |
| `observations` | Texto libre. | Datos de referencia para el operador (patente, notas). |

`service_time` normalmente **no se envía**: lo hereda del origen. No lo agregues
salvo que la operación lo requiera explícitamente.

## Principios al escribir el perfil

- **Reglas, no listas que cambian.** La regla para reconocer un tracto, no la
  lista de patentes. El criterio de rotación, no la matriz de la semana. Una
  lista escrita queda vieja sin avisar.
- **Todo verificado.** Marca qué está confirmado contra viajes ya cargados y qué
  es supuesto por confirmar.
- **Explícito sobre lo ausente.** Si algo no aplica (características vacías,
  sin reporte de avance acordado), escríbelo — el silencio se lee como olvido.
