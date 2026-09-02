---
name: descubrir-mandante
description: >-
  Onboarding de un mandante nuevo para la carga de viajes al backlog del TMS de
  Drivetech. A partir de muestras reales de cómo ese mandante manda sus
  solicitudes de viaje (una tabla en el correo, un Excel/CSV adjunto o un PDF),
  descubre el formato, infiere el mapeo campo por campo a create_backlog_trips,
  lo valida contra el catálogo de la plataforma y una carga de prueba, entrevista
  al usuario por las reglas de asignación de viajes a conductores/vehículos, y
  guarda el perfil del mandante (`spec_md` + intake) en el backend de Drivetech con
  upsert_backlog_mandante, que después usa la skill de carga a diario. Úsala cuando entre un
  cliente/mandante nuevo, cuando pidan "configurar un mandante", "agregar un
  cliente", "descubrir el formato de X", "onboardear a X", o cuando un mandante
  ya configurado cambie su formato y haya que rehacer su especificación.
---

# Descubrimiento de un mandante nuevo

Onboarding, **una sola vez por mandante** (o cuando cambia su formato). El
resultado es el **perfil del mandante** guardado en el backend de Drivetech (su
`spec_md` — cómo se lee, mapea, asigna y comunica — más su intake), vía
`upsert_backlog_mandante`. Con eso, la operación diaria la hace la skill
**`cargar-viajes-backlog`**; esta no se usa todos los días.

El activo que produces no es código: es el **perfil del mandante**. Es el
conocimiento caro (qué columna es la llave, cómo se arma la hora, qué origen
aplica, si usa características de vehículo, **y cómo se asignan los viajes a los
conductores**) escrito de forma que la skill de carga lo aplique de manera
determinística y que un operador lo pueda leer y corregir.

## Regla de oro del descubrimiento

**Trabaja sobre muestras reales, nunca sobre lo que el cliente te cuente que
manda.** La descripción de memoria siempre omite la columna rara, el caso
`111111`, la segunda tabla. Pide el archivo/correo de verdad y léelo tú.

Y lo de siempre: **nunca inventes** un cliente, origen, tipo o grupo. Ante duda,
`get_tms_catalog`; si no aparece, pregunta.

## Requisitos de conexión

- **MCP de Drivetech** conectado, con acceso al módulo TMS de la empresa del
  cliente — se usa para resolver el catálogo y para la carga de prueba.
- **Las muestras del mandante**: al menos un correo/archivo real ya recibido. Si
  el formato varía (p.ej. una tabla por tipo de camión, o meses con columnas
  distintas), pide 2–3 para no perder un caso.
- No necesitas el correo conectado para descubrir: el conector de correo lo usa
  la skill de carga. Aquí basta con que el usuario te comparta la muestra.

Antes de empezar, confirma la empresa activa igual que la skill de carga: si el
token ve varias empresas y `get_current_enterprise_name` no devuelve la del
cliente, fíjala con `select_enterprise`. Si ve una sola, no hay nada que hacer.

---

## Paso 0 · ¿Mandante nuevo o re-descubrimiento?

**Antes de mirar la primera muestra, averigua si ese mandante ya existe.** Llama a
`get_backlog_settings` (sin `slug`) y búscalo en la lista.

- **No está** → mandante nuevo. Sigue en el Paso 1 y descubre todo.
- **Ya está** → es un **re-descubrimiento** (cambió el formato, o el perfil quedó
  mal). Trae el perfil completo con `get_backlog_settings(slug=…)` y **guarda el
  `spec_md` vigente antes de tocar nada.** Ese texto no es un borrador tuyo: tiene
  meses de reglas que el usuario fue dando operando (Paso 9 de la skill de carga) y
  que **no se descubren mirando una muestra**.

En un re-descubrimiento lo que cambia es **cómo se lee** el mandante (secciones 1–3
del perfil, a veces 4–6). Todo lo demás —criterio de asignación, comunicación,
trampas de la faena, reglas aprendidas en operación— **se preserva salvo que el
usuario diga explícitamente lo contrario**. Dilo en voz alta al empezar:

> *"Ferremax ya está configurado (v7). Voy a rehacer la parte de lectura y dejar
> intactas las reglas de asignación y lo aprendido en operación."*

Y no rehagas la entrevista del Paso 6 desde cero: léele al usuario lo que ya está
escrito y pregúntale **solo si algo de eso cambió**.

---

## Paso 1 · Conseguir las muestras y definir el intake

Pídele al usuario una muestra real del mandante nuevo. El **contenido** puede
venir como:

- **Tabla en el cuerpo de un correo** (reenviado o pegado).
- **Excel / CSV** (adjunto o archivo).
- **PDF** (orden de transporte, guía, planilla exportada).

Y define el **intake** — cómo van a entrar los viajes en la operación diaria, que
es distinto de en qué formato vienen:

- **`correo`** — el mandante manda la solicitud por mail (caso empresa de
  transporte). Anota los remitentes y el texto del asunto.
- **`archivo`** — el mandante genera él mismo su export y lo deja en una carpeta,
  Drive o adjunto (caso mandante de carga que sube su propio backlog). Anota la
  ubicación, el patrón de nombre y cómo se marcará uno ya cargado.

Si el formato cambia entre envíos, pide varias muestras.

### Identidad: con qué nombres aparece escrito

Anota el **nombre del mandante** (cómo lo va a llamar el cliente) — de ahí sale su
`slug` en el backend. Y pregunta además, aunque sean **opcionales**:

- **Razón social** — el nombre legal, el que va impreso en los documentos.
- **RUT**.
- **Otros nombres** con que aparece: planta, local, alias interno del mandante.

**Dile para qué es, no lo pidas a secas.** No es burocracia: el nombre del TMS y el
del papel casi nunca son el mismo. Una guía de despacho puede decir *"Embotelladora
Andina S.A."* mientras el TMS llama a ese lugar *"Rancagua KOA"* — si la razón social
no está guardada, una verificación documental los lee como dos entidades distintas y
rechaza guías que estaban buenas.

Si el usuario no los tiene a mano, **no lo trabes**: anótalos como **duda abierta**
(§11 del perfil) y sigue. Va en la sección **0 · Identidad del mandante** del
`spec_md`.

## Paso 2 · Normalizar a una tabla canónica

Cada fuente se llee distinto, pero todas terminan en lo mismo: **una tabla
limpia de columnas × filas, donde cada fila es un viaje.** Cómo extraer cada
formato está en `references/fuentes.md`. En resumen:

- **Correo con tabla** — parsea la(s) tabla(s) del cuerpo. Si hay varias, casi
  siempre son el mismo formato partido por una dimensión (tipo de camión, zona):
  únelas y guarda de qué grupo venía cada fila.
- **Excel / CSV** — usa la skill `xlsx`. Detecta la fila de encabezado real
  (rara vez es la primera), la hoja correcta, y descarta filas de totales o
  basura.
- **PDF** — usa la skill `pdf` para extraer tablas; si es escaneado, OCR primero.
  Los PDF traen tablas sucias: valida el conteo de filas contra lo que se ve.

Muéstrale al usuario la tabla que extrajiste y **confirma que están todas las
filas** antes de seguir. Un viaje perdido acá es un camión sin asignar después.

## Paso 3 · Inferir el mapeo campo por campo

Propón el mapeo de cada columna a los campos de `create_backlog_trips`. Los
campos y qué significa cada uno están en `references/esquema-perfil.md`. Los que
importan y sus trampas:

- **`code` — la llave de idempotencia.** Es lo que hace que releer el mismo
  correo no duplique. Identifícala bien: suele ser el número de guía/carga, no el
  "ID" interno. Si hay dos candidatos, pregunta cuál es el número con que el
  mandante identifica el viaje. Se manda **tal cual**, sin normalizar.
- **`date` y `hour`.** Detecta el formato de fecha (`dd-mm-yyyy` vs `yyyy-mm-dd`)
  y compón `hour` como `YYYY-MM-DD HH:MM` en **hora LOCAL**. Deja escrito en el
  perfil, en mayúsculas, que **la hora NO se convierte** — `create_backlog_trips`
  la pasa a UTC; convertirla dos veces la corre +4h. Esta es la falla más común.
- **Características de vehículo (`skills_required`).** No lo adivines: **léelo del
  catálogo** con `get_tms_catalog kind=vehicle_skills`. Eso te da dos cosas:
  - `skills_enabled` — si es `true`, la empresa **exige** que el vehículo cumpla
    la característica del viaje (al asignar se rechaza el que no cumpla), así que
    para esta operación `skills_required` es obligatorio. Si es `false`, la flota
    no se clasifica y `skills_required` va **vacío y así corresponde** — déjalo
    escrito para que nadie lo lea después como dato faltante.
  - la **lista de características** de la empresa (S28, C14, Tracto, Rampla Plana,
    Furgón Refrigerado…). Úsala para **resolver tokens misteriosos de la muestra**:
    si en el archivo aparece algo que no sabes qué es y **hace match con una
    característica** del catálogo, es `skills_required` — no una duda para
    preguntar. Va como lista de listas (`[["S28"]]`); una fila que debería traerla
    y no la trae, no se carga.

  Solo pregúntale al usuario si el token no calza con ninguna característica ni con
  otro campo conocido.
- **`origin`.** Puede ser constante, o depender de una columna (como en el ejemplo, que
  el origen sale del tipo de camión + la patente). Si ves una regla, propónla; si
  no, pregunta el origen por defecto.
- **Constantes** — `type`, `group_name`, `items`, origen por defecto. Suelen ser
  fijas para toda la operación.
- **`observations`, `order_number`** — trazabilidad y datos que el operador
  quiera ver (patente de referencia, etc.).

Marca como **duda** todo lo que no puedas mapear con confianza. No rellenes con
un supuesto.

## Paso 4 · Validar contra el catálogo

Antes de dar por bueno el mapeo, resuelve los nombres reales con
`get_tms_catalog` (`kind`: `clients`, `origins`, `trip_types`, `vehicle_groups`,
`vehicle_skills`):

- Toma los códigos de cliente/destino de la muestra y búscalos. Usa el `code` y
  `name` que devuelva la plataforma, no los del archivo.
- Verifica que el `origin`, el `type` y el `group_name` que propusiste **existan**
  tal como los escribiste.
- Contrasta cualquier token de tipo/característica contra `vehicle_skills` (con su
  nombre exacto del catálogo) y confirma `skills_enabled` para saber si es
  obligatorio.
- Cualquier código que **no aparezca en ningún catálogo** es una duda (destino
  nuevo, o mal escrito por el mandante): pregúntale al usuario, no lo inventes.

Este paso es el que atrapa los inventos antes de que lleguen al backlog.

## Paso 5 · Carga de prueba (golden sample)

Valida el mapeo con datos reales, en chico:

1. Arma **1–2 viajes** de la muestra y llama a `create_backlog_trips` con
   `dry_run=true`. Revisa que la clasificación quede como esperas.
2. Si el mandante **ya tiene viajes cargados** en la plataforma (onboarding de
   algo que hoy se hace a mano), compara tu resultado contra uno real ya
   existente: `code`, `origin`, `skills_required` y sobre todo la **hora
   comprometida** deben calzar. Si no calzan, el mapeo está mal — arréglalo antes
   de seguir.
3. Si el usuario lo aprueba, haz **una** carga real de ese viaje de prueba y
   **revisa en la plataforma** que la hora comprometida se vea igual que en la
   muestra (p.ej. 07:00, no 11:00). Una hora corrida = doble conversión.

No cargues todo el lote aquí: esto es validación. La carga del día es trabajo de
la skill `cargar-viajes-backlog`.

## Paso 6 · Entrevistar al usuario por lo que no está en la muestra

Con el formato ya validado (Pasos 2–5), **falta la otra mitad del perfil: cómo se
opera**. Esto no se deduce mirando una solicitud — se lo preguntas al usuario y lo
dejas escrito. Cuando termines este paso, el mandante queda listo para que el día a
día sea **solo cargar y asignar**.

### 6.1 · Reglas de asignación (entrevista principal)

Este es el corazón del paso. Una vez descubierto el archivo, **pregúntale al
usuario, de forma explícita y ordenada, cómo asigna los viajes a los conductores y
vehículos.** No te conformes con una respuesta general: repregunta hasta que las
reglas sean accionables. Cubre al menos:

> Ten presente que la plataforma ya valida por su cuenta (características,
> capacidad, cupo/hora del origen y restricciones del recurso), según lo que la
> cuenta tenga configurado — ver el manual *"qué valida el sistema al planificar
> desde el backlog"*. Eso es piso; esta entrevista captura el **criterio del
> mandante encima de esas validaciones**.

- **Qué determina quién toma un viaje.** ¿Hay conductor/vehículo fijo por ruta,
  cliente u origen (como en ICB, un conductor habitual por circuito)? ¿O se
  reparte entre varios?
- **Cómo se elige el vehículo.** ¿Por característica (tipo, refrigerado, tonelaje),
  por capacidad vs volumen/peso del viaje, o cualquier móvil sirve? Cruza esto con
  lo que viste en el catálogo (`vehicle_skills`, `skills_enabled`).
- **Orden y prioridad.** ¿Hay turnos/vueltas (primera en la mañana, segunda en la
  tarde)? ¿Ventanas horarias? ¿Qué se asigna primero?
- **Restricciones.** Tope de viajes por conductor, un conductor que no puede
  repetir cierto destino, rutas dedicadas, incompatibilidades.
- **Cómo se desempata** entre candidatos que cumplen (rotación, cercanía, carga
  pareja de la semana, afinidad conductor-destino).
- **Qué es fijo y qué se decide cada día** — para saber qué puede resolver la skill
  sola y qué debe preguntarte al asignar.
- **Excepciones y casos borde** que el usuario ya conozca.

Escríbelas como **reglas accionables** en la sección de asignación del `spec_md`.
Si el usuario no tiene una regla para algo, déjalo anotado como "preguntar al
asignar" — **no inventes** un criterio.

### 6.2 · Comunicación de vuelta

¿Se le confirma la asignación al mandante? ¿Se le reporta el avance del día, cada
cuánto? ¿Qué se hace cuando un viaje se atrasa? ¿A quién se le responde
(`responder_a`) y quién va en copia? Si esta operación no le reporta a nadie (p.ej.
un mandante de carga que sube su propio backlog), déjalo explícito y `responder_a`
vacío.

**El reporte de estado se arma con la plantilla de la empresa, no con una nueva.**
La config trae `extra.reporte_tipo`: el formato con que esta empresa le responde a
todos sus mandantes (estructura, columnas, reglas, colores, sobre del correo).
Léelo antes de preguntar, y pregunta solo por lo que este mandante hace **distinto**:

- ¿Le sirve el reporte tal cual, o necesita **columnas** extra (y de dónde saldría
  ese dato) o quitar alguna que no aplica?
- ¿Sus **umbrales** son otros? Ojo con la permanencia en origen: si los camiones
  pernoctan en planta, medirla desde la llegada infla todo y hay que medirla desde
  la hora comprometida de carga.
- ¿Cómo le sirve el **resumen** — por ruta, por origen, por estado, o sin resumen?
- ¿Tiene **textos** propios (saludo, asunto, cierre), otra **frecuencia**, o exige su
  propia **marca** en vez de la de la empresa?

Lo que sea distinto se guarda en el `spec_md` como una sección titulada
**"Reporte de status: ajustes"**, con **solo las diferencias** y anotando contra qué
versión de la plantilla base se escribió. Lo que no se menciona, se hereda. Si el
mandante quiere el reporte tal cual, escríbelo así de explícito y no agregues la
sección.

Si el mandante pide algo que **la plataforma no expone**, no lo prometas: déjalo
anotado como pendiente y avísale al usuario.

Y si lo que el mandante pide en realidad **le sirve a todos** (un dato que faltaba,
un arreglo del formato), eso no es delta: proponle al usuario subirlo a la plantilla
de la empresa con `set_backlog_config` (recordando que `extra` se reemplaza completo:
lee, mezcla y reenvía).

### 6.3 · Trampas de la faena

Cualquier cosa rara que el usuario sepa: que se equivocan seguido con el número de
guía, que una patente es tracto y no rampla, orígenes donde los camiones pernoctan
(y por eso los hitos de origen se leen distinto), tipos de despacho que a veces
aparecen y no están en el catálogo, etc.

Estas respuestas son la mitad del valor del perfil. No las dejes en blanco por
apuro: un perfil sin reglas de asignación obliga a improvisar cada mañana. Y
recuerda que **no se congelan acá** — la skill de carga sigue agregando reglas
nuevas al perfil a medida que el usuario las da operando (su Paso 9).

## Paso 7 · Escribir el perfil y confirmarlo

Con todo lo anterior, **propón el perfil completo al usuario y hazlo confirmar
antes de guardar nada.** Después **guárdalo en el backend de Drivetech** con
`upsert_backlog_mandante` (opera sobre la empresa de la sesión):

- `slug` (se normaliza solo, puedes pasar el nombre), `nombre`, `intake`
  (`correo`/`archivo`) y su `intake_config` (correo: `remitentes`,
  `asunto_contiene`; archivo: `ubicacion`, `patron`, `marcar_procesado`).
- `responder_a` / `copiar_a` (si se le responde).
- **`spec_md`** — la especificación de lectura completa en Markdown, siguiendo la
  anatomía de `references/esquema-perfil.md` (el **contrato** del `spec_md`, que
  también leen la skill de carga y la de seguimiento) y usando `mandantes/ejemplo.md`
  como referencia de uno bien hecho. Arranca con el **encabezado del perfil**
  (`esquema`, `actualizado`) que ese contrato define, para que quien lo lea después
  sepa contra qué versión fue escrito. Incluye mapeo, constantes, regla de origen,
  característica, **criterio de asignación** y **comunicación** — todo el know-how
  del mandante va acá. Escribe **reglas, no listas de datos** que cambian: la regla
  para reconocer un tracto, no la lista de patentes; el criterio de rotación, no la
  matriz de la semana. Se guarda **byte-idéntico** — no lo normalices.

### Si es un re-descubrimiento: read-modify-write

`upsert_backlog_mandante` **reemplaza el perfil completo**. Si mandas solo lo que
descubriste hoy, borras todo lo demás. Entonces:

1. Parte del **`spec_md` vigente** que trajiste en el Paso 0, no de una hoja en
   blanco.
2. Reescribe **solo** las secciones que cambiaron (normalmente 1–3). El resto va
   **byte-idéntico**, incluidas las "Reglas aprendidas en operación".
3. Reenvía **todos** los campos del perfil (`intake`, `intake_config`,
   `responder_a`, `copiar_a`, `enabled`), no solo los que tocaste. No mandes
   `version`: el backend versiona solo.
4. Antes de guardar, **muéstrale al usuario el diff en palabras** —qué secciones
   cambian y qué queda igual— y confirma. Después dile en qué versión quedó:
   *"Perfil de Ferremax actualizado (v8): cambió el formato de la tabla; asignación
   y comunicación quedaron igual."*

Si algo salió mal, el backend guarda las versiones anteriores:
`get_backlog_settings(slug=…, history=true)`.

### Lo que quedó sin resolver va escrito, no en tu memoria

Todo lo que marcaste como duda en el camino y **no** lograste cerrar —un código que
no está en ningún catálogo, una columna que nadie supo explicar, un criterio de
asignación que el usuario todavía no tiene definido— va en la sección **"Dudas
abiertas"** del `spec_md`, diciendo quién la tiene que resolver. Si no queda escrita
ahí, se pierde al cerrar la sesión y la vuelve a descubrir el operador a las 7 de la
mañana, con los camiones esperando.

Un perfil con dudas abiertas declaradas sirve. Un perfil con dudas tapadas por un
supuesto, no.

Si además falta config transversal de la empresa (proveedor de correo, marca de
procesado por defecto, ventana, firma, y la plantilla de reporte `extra.reporte_tipo`),
guárdala con `set_backlog_config`. Si la empresa **todavía no tiene plantilla de
reporte** y este mandante quiere reporte, ese es el momento de armarla: pídele al
usuario un reporte real que ya esté mandando, reprodúcelo, y guárdalo como plantilla
de la empresa — no como algo privado de este mandante.

El perfil vive **en el backend, por empresa** — sobrevive a updates del plugin, al
entorno efímero y al cambio de máquina, y Drivetech lo administra central. (Si esa
instalación no tiene backend, cae al modo archivo: `mandantes/<nombre>.md` +
`config.yaml` en la carpeta de datos del cliente.)

## Paso 8 · Cierre

### Si el mandante entrega guía de despacho

Es lo que sigue, pero **no ahora**: un mandante recién configurado todavía no tiene
guías suyas en el sistema — el papel firmado aparece cuando empieza a operar. Cuando
ya tenga algunas, el formato de su guía se descubre **aparte**, con la skill
**`descubrir-guia-despacho`** si esta instalación la tiene, que produce el
`document_spec` del mandante: dónde va el folio, el código de cliente, la tabla de
ítems. Es otra especificación y se rehace en otro momento — **ésta** cuando el
mandante cambia *cómo pide viajes*, **aquélla** cuando cambia *su formulario*.

Menciónaselo al usuario al cerrar, para que sepa que existe y cuándo volver. No lo
intentes acá: sin guías reales del mandante no hay nada que descubrir.

### El cierre

Dile al usuario que el mandante quedó **completo** — formato + reglas de
asignación + comunicación — y que **de ahora en adelante la operación diaria es
solo cargar y asignar** con la skill `cargar-viajes-backlog`. Recuérdale validar
con la primera carga real del día siguiente que todo quedó bien, y que cualquier
regla nueva del mandante se guarda en su perfil con `upsert_backlog_mandante`
(versiona solo) — la skill de carga lo hace sobre la marcha a medida que él va
dando instrucciones (ver su Paso 9).

---

## Reglas de oro

- **Muestras reales, no descripciones.** Lee el archivo/correo de verdad.
- **Pregunta razón social y RUT** aunque sean opcionales: son los nombres con que el
  mandante aparece en el papel. Sin ellos, la verificación documental rechaza guías
  correctas. Si no los tiene, van como duda abierta.
- **Nunca inventes catálogo.** `get_tms_catalog` resuelve; lo que no aparece se
  pregunta.
- **`code` es la llave de idempotencia.** Identifícala bien y mándala tal cual.
- **La hora va LOCAL y no se convierte.** Déjalo escrito en el perfil.
- **Características: pregunta si la operación las usa.** Si sí, obligatorias; si
  no, vacías y explícito.
- **Escribe reglas, no listas que cambian.** Patentes, conductores y dotación
  salen del catálogo en el momento, no del perfil.
- **Confirma el perfil antes de escribirlo**, y valida con una carga de prueba.
- **Un mandante que ya existe se edita, no se reescribe.** `upsert` reemplaza el
  perfil completo: parte del `spec_md` vigente y preserva asignación, comunicación
  y lo aprendido en operación.
- **Lo que quedó en duda se escribe** en la sección "Dudas abiertas" del perfil, con
  quién la resuelve. Una duda no escrita se pierde.
- **El reporte se hereda de la empresa.** En el perfil va solo el delta del mandante,
  nunca una copia de la plantilla.
- **El perfil vive con la skill de carga**, no dentro de esta.
