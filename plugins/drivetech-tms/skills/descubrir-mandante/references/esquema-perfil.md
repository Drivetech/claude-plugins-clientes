# Anatomía de un perfil de mandante — contrato del `spec_md`

**Este archivo es el contrato del `spec_md`, no documentación de una sola skill.**
Lo escribe `descubrir-mandante`, lo lee literal `cargar-viajes-backlog` (para
mapear, cargar y asignar) y lo consulta `seguimiento-operacion` (umbrales, hitos y
reporte). Cualquiera de las tres que necesite saber qué forma tiene un perfil, mira
acá. **Si cambia el contrato, sube `esquema` y revisa las tres.**

Un perfil es un Markdown que dice **cómo se lee un mandante y cómo se traduce su
solicitud a viajes del backlog**. Es lo único que cambia de un mandante a otro; el
flujo vive en los `SKILL.md` y es igual para todos. Se guarda en el backend, en el
campo `spec_md` del mandante (`upsert_backlog_mandante`); en instalaciones sin
backend, como `mandantes/<nombre>.md`.

Toma `cargar-viajes-backlog/mandantes/ejemplo.md` como el ejemplo de referencia de
uno bien hecho. Esta es la anatomía a completar. No todas las secciones aplican a
todos los mandantes — omite las que no correspondan, pero no omitas una por no
haber preguntado.

## Encabezado del perfil

Todo `spec_md` arranca con este bloque, para que quien lo lea sepa contra qué
contrato fue escrito:

```
# Lectura del requerimiento — <Mandante>

> esquema: v1 · actualizado: <YYYY-MM-DD>
```

**`esquema` es la versión de este documento**, no la del perfil (esa la lleva el
backend y sube sola en cada `upsert`). Hoy el contrato es **v1**.

- Si un perfil trae un `esquema` **menor** que el de acá, fue escrito contra un
  contrato viejo: léelo igual, pero avísale al usuario que conviene rehacerlo con
  `descubrir-mandante`.
- Si **no** trae `esquema`, asúmelo v1.
- Al editar un perfil (Paso 9 de la skill de carga, o un re-descubrimiento),
  actualiza `actualizado` y deja `esquema` como está — salvo que hayas reescrito el
  perfil entero contra el contrato nuevo.

## Cómo se guarda — la semántica de escritura no es la misma en todas

Confundirlas borra datos sin que nada falle:

- **`upsert_backlog_mandante` reemplaza el documento completo.** Lo que no mandes se
  pierde. Para tocar un campo: leer con `get_backlog_settings(slug)`, cambiar solo
  eso y reenviar todo lo demás byte-idéntico. Direcciona **por slug**, así que un
  slug que colisiona escribe encima de otro mandante sin avisar — el slug se toma de
  la lista del backend, nunca se calcula.
- **`set_backlog_config` hace merge**, con una excepción: **`extra` se reemplaza
  completo**. Para tocar una llave de `extra`, leer, mezclar y reenviar el resto.
- **Otros endpoints del backend actualizan por campo:** lo que no viene, no se toca.
  Así se guarda la especificación del documento del mandante (`document_spec`).

Antes de escribir, ten claro en cuál de las tres estás. Ante la duda, **lee primero
y reenvía completo**: es correcto en las tres.

## Secciones

**0 · Identidad del mandante.** Cómo se llama en el TMS y **con qué otros nombres
aparece escrito**, sobre todo en papel: **razón social**, **RUT**, y cualquier alias
o nombre de planta/local con que sale impreso. Razón social y RUT son opcionales,
pero **se preguntan siempre**: son lo que permite reconocer al mandante cuando el
nombre del documento no es el del sistema. Una guía que dice *"Embotelladora Andina
S.A."* mientras el TMS llama a ese lugar *"Rancagua KOA"* es el mismo lugar — sin la
razón social guardada, una verificación documental los lee como distintos y rechaza
guías correctas. Lo que el usuario no tenga a mano va a §11 como duda abierta, nunca
en blanco.

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
de avance y cada cuánto; qué se informa ante un atraso; a quién se responde.
Incluye cómo se leen los hitos en esta operación si tienen una lectura especial
(p.ej. origen que es de la propia empresa y por eso `origin_arrival_datetime` es del
día anterior).

El **formato** del reporte no va acá: sale de la plantilla de la empresa
(`extra.reporte_tipo` en la config). Lo que este mandante hace distinto va en una
subsección titulada **"Reporte de status: ajustes"**, con solo las diferencias
—columnas que agrega o quita (declarando de dónde sale el dato), umbrales propios,
cómo agrupa el resumen, orden del detalle, textos del correo, colores— y abriendo la
subsección con una línea `> reporte_base: <versión o fecha de extra.reporte_tipo>`
que declare contra qué versión de la plantilla se escribió el delta. Lo que no se
menciona, se hereda. Si el mandante usa el reporte tal cual, escríbelo explícito y
no pongas la subsección.

**10 · Particularidades.** Cualquier cosa propia: que se equivocan con el número
de guía seguido, formatos de carga mezclados, faenas sin conductores propios en
ciertas consultas, etc.

**11 · Dudas abiertas.** Lo que quedó sin resolver y **hay que preguntar**: un
código que no aparece en ningún catálogo, una columna que nadie supo explicar, un
criterio de asignación que el usuario todavía no tiene definido. Una línea por duda,
con **quién la resuelve** y **desde cuándo está abierta**:

```
- [ ] El destino `88231` no está en el catálogo de clientes. ¿Tienda nueva o typo
      del mandante? — preguntar a Operaciones (abierta 2026-09-02).
- [ ] No hay regla para desempatar cuando dos conductores califican igual;
      hoy se pregunta al asignar — definir con el usuario (abierta 2026-09-02).
```

Una duda escrita acá **sobrevive a la sesión**; una duda que quedó solo en la
conversación se pierde y la vuelve a descubrir el operador a las 7 de la mañana. Se
cierran igual que se abren: cuando el usuario la responde operando, la regla pasa a
la sección que corresponda y la línea se borra de acá (Paso 9 de la skill de carga).
Si no hay dudas, escribe "Ninguna" — el silencio se lee como olvido.

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
- **Un re-descubrimiento no empieza en blanco.** Cambiar el formato de un mandante
  toca las secciones 1–3 (y a veces 4–6). Las secciones 8, 9 y 10, más "Reglas
  aprendidas en operación", son know-how ganado operando: se preservan
  byte-idénticas salvo que el usuario diga lo contrario.
