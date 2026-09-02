---
name: cargar-viajes-backlog
description: >-
  Lee los correos con solicitudes de viaje que mandan los mandantes
  configurados (por ejemplo las "Ventanas de entrega" a tiendas de retail), extrae
  los viajes y los carga al backlog del TMS de Drivetech. Después asigna
  vehículo y conductor, y acompaña la jornada informándole al mandante quién
  hace cada viaje y cómo van saliendo (realizados con sus horas y permanencia,
  en ruta con su ETA, pendientes). Úsala cuando llegue o pidan procesar una
  solicitud de viajes, cargar ventanas de entrega, asignar los viajes del día,
  mandarle el estado al mandante, revisar el correo del mandante, o cuando
  corras el chequeo periódico de correos.
---

# Carga de solicitudes de viaje al backlog

Automatiza lo que hoy es manual: conseguir la solicitud de viajes del día,
cargarla al **backlog** del TMS, asignarla y (si corresponde) avisarle de vuelta
al mandante.

## Dos formas de entrada (intake), un mismo core

Los viajes pueden entrar de dos maneras, y esta skill sirve a las dos porque el
**cómo entran** (intake) está separado del **qué se hace con ellos** (mapear,
validar, cargar, asignar):

- **`correo`** — una empresa de transporte recibe la solicitud por correo de su
  mandante (p.ej. recibe las "Ventanas de entrega" de un retail). El agente busca
  el correo y lo procesa.
- **`archivo`** — un mandante de carga genera él mismo su archivo de viajes (un
  export de su ERP/WMS) y su agente lo levanta desde una carpeta/Drive/adjunto y
  lo carga a su propio backlog.

El intake de cada mandante se define en su perfil (backend). Todo lo que viene después
del intake —leer el formato, resolver el catálogo, cargar, asignar, comunicar— es
idéntico para los dos.

## Arquitectura — flujo acá, estado en el backend

| Dónde | Qué tiene | Cambia entre clientes |
|---|---|---|
| `SKILL.md` (este) | **El flujo.** Intake, confirmar, cargar, asignar, responder, aprender. | No |
| **Backend de Drivetech** (por empresa, vía MCP) | **La config** de la instalación y **el perfil de cada mandante** (`spec_md`): cómo se lee, cómo se mapea, cómo se asigna, cómo se comunica. | Sí |
| `README.md` | Instrucciones de uso **para la persona**. No lo necesitas para operar. | — |

Todos los mandantes siguen el mismo flujo; lo que cambia es cómo entra la
solicitud (intake), el formato en que viene y las reglas propias de su operación.
Por eso el flujo está acá y el perfil está en el backend.

### Dónde viven la config y los perfiles — IMPORTANTE

El estado del cliente **vive en el backend de Drivetech, por empresa**, y se
lee/escribe por MCP. No vive en archivos dentro del plugin (un update lo pisaría)
ni depende del disco de una máquina: así sobrevive a las actualizaciones, al
entorno efímero y al cambio de equipo, y Drivetech lo administra de forma central.

Tools de almacenamiento (todas operan sobre la empresa de la sesión):

- **`get_backlog_settings`** — sin `slug`: bootstrap (config + lista de mandantes
  **sin** `spec_md`). Es lo **primero** que llamas al arrancar. Con `slug`: el
  perfil completo de ese mandante **con** su `spec_md`. Con `slug` + `history=true`:
  versiones anteriores para comparar o revertir.
- **`upsert_backlog_mandante`** — crea o **reemplaza** el perfil de un mandante
  (`intake`, `intake_config`, `responder_a`, `copiar_a`, `spec_md`, `enabled`). El
  backend versiona solo (no mandes `version`). Como **reemplaza el perfil
  completo**, para tocar un solo campo lee primero con `get_backlog_settings(slug)`
  y reenvía el resto igual.
- **`set_backlog_config`** — config transversal de la empresa (proveedor de correo,
  marca de procesado por defecto, ventana, firma) y el bloque **`extra`**, donde vive
  la **plantilla de reporte de estado de la empresa** (`extra.reporte_tipo`): el
  formato con que se le responde a cualquier mandante que pida reporte. Hace merge,
  pero `extra` se **reemplaza completo** — para tocar una llave, lee primero y
  reenvía el resto.
- **`delete_backlog_mandante`** — deshabilita (soft) un mandante; se reactiva con
  `upsert(enabled=true)`.

**`spec_md` es Markdown opaco:** lo escribe el descubrimiento y lo lee literal la
carga. No lo interpretes, no lo resumas, no lo reescribas al pasarlo — se guarda y
vuelve byte-idéntico.

Su forma la define un solo lugar, compartido por las tres skills:
**`descubrir-mandante/references/esquema-perfil.md`** — qué secciones tiene un
perfil, el encabezado `esquema: vN` con que arranca, y la tabla de campos de
`create_backlog_trips`. Míralo ahí en vez de deducirlo del perfil que te tocó. Si un
perfil trae un `esquema` menor que el del contrato, léelo igual pero avísale al
usuario que conviene rehacerlo con `descubrir-mandante`.

Si el MCP de Drivetech **no expone** estas tools (instalación sin backend), cae al
modo archivo: `config.yaml` y `mandantes/*.md` en una carpeta de datos fuera del
plugin (`./drivetech-tms/` o `~/.drivetech-tms/`), usando `config.example.yaml` y
`mandantes/ejemplo.md` del plugin como referencia. El flujo es el mismo.

**Al arrancar:** lee este archivo y llama `get_backlog_settings` (sin slug) para la
config y la lista de mandantes; el `spec_md` de cada uno se pide con `slug` recién
cuando hay trabajo para él.

## Requisitos de conexión

- **MCP de Drivetech** conectado. Siempre.
- **Según el intake de cada mandante:**
  - Intake `correo` → **un conector de correo** (Gmail u Outlook) para buscar,
    marcar como procesado y responder.
  - Intake `archivo` → **acceso a la ubicación** donde el mandante deja su archivo
    (una carpeta conectada, un Drive, o el adjunto de un correo). Para responder
    de vuelta —si esa instalación lo hace— igual necesita el conector de correo.

**La empresa es una sola por instalación**, no una por mandante: el cliente opera
su propia cuenta. Un mandante es quien le manda las solicitudes de viaje, no otra
empresa en la plataforma.

- **Si el token tiene acceso a una sola empresa** (el caso de un cliente), el MCP
  la fija solo y no hay nada que hacer: `select_enterprise` ni siquiera aparece
  en el listado de tools. Ignora `empresa_drivetech` si está vacío.
- **Si el token tiene acceso a varias** (el caso de una cuenta de Drivetech),
  **confirma la empresa activa al empezar cada corrida**, no solo la primera vez:
  la selección se pierde sola (vence el TTL, se reconecta el MCP) y las tools del
  TMS empiezan a responder *"la empresa no tiene contratado el módulo de tms"*,
  que parece un problema de permisos y no lo es. Si `get_current_enterprise_name`
  no devuelve la empresa esperada, fíjala con `select_enterprise` antes de seguir.

## Cuándo corre

El chequeo es **cada ~5 minutos**. Puedes dispararlo:
- En Claude Code: `/loop 5m` sobre esta skill, o una rutina programada.
- En Claude Desktop / web: invocándola o programándola.

En cada corrida: busca una solicitud nueva (correo o archivo, según el intake) →
si hay, procesa → si no, termina en silencio (no molestes al usuario si no llegó
nada).

---

## Paso 0 · Puesta en marcha (solo si `get_backlog_settings` viene vacío)

Si `get_backlog_settings` devuelve config en cero y lista vacía, la empresa no
tiene nada configurado todavía.

**Nunca corras este paso de forma desatendida.** Si la skill se disparó sola
(rutina programada, `/loop`, cron) y no hay configuración, **no hagas nada** más
que dejar constancia de que falta configurar. El asistente solo corre cuando hay
alguien al otro lado que pueda responder.

Con el usuario presente, pregúntale y **guarda en el backend**: la config con
`set_backlog_config` y cada mandante con `upsert_backlog_mandante`.

1. **Mandantes** — para cada uno: nombre y su **intake** (va en `upsert`):
   - `correo`: de qué direcciones llega la solicitud, qué dice el asunto y a quién
     se le responde.
   - `archivo`: dónde deja el mandante su archivo (carpeta conectada, Drive o
     adjunto), cómo se reconoce (nombre/patrón) y cómo se marca uno ya procesado.

   La empresa **no** se pregunta por mandante: es una sola para toda la
   instalación (la de la sesión MCP).
2. **Conector de correo** (si algún mandante usa intake `correo`, o si se
   responde de vuelta) — no lo preguntes de entrada: mira qué conector tienes en
   la sesión y úsalo. Pregunta **solo si hay más de uno**. Va en
   `set_backlog_config(proveedor_correo=...)`.
3. **Marca de procesado** — para intake `correo`, una etiqueta (Gmail) o
   categoría/carpeta (Outlook), en `set_backlog_config`. Para intake `archivo`, la
   convención de "ya cargado" (mover a `procesados/`, un sufijo, etc.), en el
   `intake_config` del mandante.
4. **Perfil de lectura** (`spec_md`) de cada mandante. Si aún no existe, ve a
   "Cómo agregar un mandante nuevo" al final (lo produce `descubrir-mandante` y se
   guarda con `upsert_backlog_mandante`).

Después **verifica que la instalación funcione** y dile al usuario qué falta:

- ¿Puedes **conseguir la solicitud** de cada mandante? Para `correo`, busca y
  muestra uno encontrado; para `archivo`, lista lo que hay en la ubicación.
- ¿Puedes **marcar como procesado**? En `correo` con Gmail necesita scope
  `gmail.modify`; en `archivo`, permiso de escritura en la ubicación. Si falla,
  avísale — la carga igual no duplica, pero cada corrida va a reprocesar lo mismo.
- ¿Puedes **crear un borrador** de respuesta? (Solo si esta instalación responde
  al mandante.)
- ¿El MCP de Drivetech responde y la empresa activa es la correcta?

Es mejor que el cliente se entere de un permiso que falta en la puesta en marcha
y no a las 7 de la mañana con los camiones esperando.

---

## Paso 1 · Conseguir la solicitud (intake)

Para cada mandante de `get_backlog_settings` (bootstrap), consigue las solicitudes
nuevas según su `intake`. En ambos casos: si no hay nada nuevo, termina sin avisar;
si hay varias, procésalas de más antigua a más nueva, una por una; y **anota de qué
mandante es cada una** — eso define qué perfil (`spec_md`) usar y (si aplica) a
quién se le responde.

### Intake `correo`

Busca hilos de alguno de sus `remitentes`, con `asunto_contiene` en el asunto,
dentro de `ventana_busqueda`, y **no** procesados aún (según `marca_procesado`).

La sintaxis depende del proveedor — traduce el filtro al conector que tengas:

```
# Gmail
from:<remitente> subject:"<asunto_contiene>" -label:<marca_procesado> newer_than:3d

# Outlook / Graph — no hay operadores equivalentes para todo:
# filtra por remitente y asunto en la búsqueda, y descarta después
# los que ya tengan la categoría o estén en la carpeta de procesados.
```

Con varios remitentes, busca por todos (en Gmail, `{from:a@x from:b@y}`).

Si el archivo de viajes viene como **adjunto** del correo, bájalo y trátalo como
en el intake `archivo` de aquí abajo para la extracción.

### Intake `archivo`

El mandante deja su propio archivo (export de su ERP/WMS) en la `ubicacion`
configurada — una carpeta conectada, un Drive o similar. Lista lo que hay y
quédate con los **no procesados** según la convención configurada (los que no
están en `procesados/`, o sin el sufijo de cargado, etc.).

- Reconoce los archivos del mandante por el patrón de nombre configurado (p.ej.
  `viajes_*.xlsx`). Ignora temporales y ocultos.
- Si un archivo aún se está escribiendo (tamaño cambiando, bloqueo), déjalo para
  la próxima corrida.
- No borres ni muevas nada todavía: el archivo se marca como procesado recién en
  el Paso 5, cuando la carga quedó sin duplicados pendientes.

## Paso 2 · Extraer los viajes

**Trae el perfil del mandante** con `get_backlog_settings(slug=<mandante>)` y sigue
su `spec_md`: ahí está el formato de la solicitud, el mapeo campo por campo, las
constantes de esa operación, las reglas de asignación y las de comunicación.

Sea cual sea el mandante, estas cuatro cosas **no cambian**:

- **`code` es la llave de idempotencia.** Es lo que hace que reprocesar la misma
  solicitud (correo o archivo) no duplique. Mándalo tal cual viene, sin normalizar
  ni "arreglar".
- **`hour` va en hora LOCAL — NO la conviertas tú.** Manda la hora de la solicitud
  tal cual, en `YYYY-MM-DD HH:MM`. `create_backlog_trips` la convierte a UTC según
  la zona de la empresa; si la conviertes tú también, queda corrida (+4h).
- **Si el mandante define tipos de vehículo, son obligatorios.** Van en
  `skills_required` como lista de listas (`[["S28"]]`), y si una fila no lo trae,
  no la cargues: pregunta. **Si el mandante no usa características** —flota
  homogénea, no se clasifica por tipo— entonces `skills_required` va vacío y así
  corresponde: no preguntes ni inventes una. Lo dice su especificación.
- **Nunca inventes** un cliente, origen, tipo o grupo. Ante duda,
  `get_tms_catalog`; si no aparece en ningún catálogo, pregunta. Si el token que no
  reconoces **hace match con una característica** (`vehicle_skills`), es
  `skills_required`, no una duda.

## Paso 3 · Resolver los nombres contra el catálogo

Antes de cargar, resuelve los nombres con `get_tms_catalog` (`kind`: `clients`,
`origins`, `trip_types`, `vehicle_groups`, `vehicle_skills`) y usa el `code` y
`name` que devuelva la plataforma, no los del correo. Así no renombras algo
existente ni creas un duplicado por una tilde.

Para las características: `vehicle_skills` trae la lista de la empresa y el flag
`skills_enabled`. Un token de tipo de vehículo de la solicitud que calce con una
característica se resuelve como `skills_required` con su nombre exacto del
catálogo. Si `skills_enabled=true`, la característica es obligatoria.

Si un código **no aparece en ningún catálogo**, márcalo como duda y pregúntale al
usuario. Puede ser un destino nuevo — pero eso lo decide él, no tú.

## Paso 4 · Avisar y (si corresponde) pedir confirmación

Arma un resumen para el usuario:

> Llegó una solicitud de viajes de **\<mandante\>** — *\<asunto\>*: **N viajes**.

- Si `auto_crear = false`: muestra la lista y **pide confirmación** antes de
  cargar. Si el usuario dice "no me preguntes más" / "créalos directo", trata
  `auto_crear` como `true` de ahí en adelante en esta sesión (y avísale que para
  dejarlo permanente hay que fijarlo en el perfil del mandante —queda como una
  regla más de su `spec_md`, ver Paso 9—).
- Si `auto_crear = true`: carga directo y solo informa el resultado.

## Paso 5 · Cargar al backlog

Llama a `create_backlog_trips` con **todos** los viajes en una sola llamada. La
primera vez que proceses una solicitud nueva, conviene una pasada con
`dry_run=true` para revisar la clasificación antes de escribir.

Interpreta la respuesta por canasta:
- **created** — cargados. Cuéntalos.
- **needs_clarification** — nombre ambiguo o no encontrado (trae candidatos).
  No se cargaron: resuélvelos con `get_tms_catalog` o pregúntale al usuario.
- **already_loaded** — la guía (`code`) ya existe → **NO la ignores**. Ver 5.1.
- **errors** — rechazo del sistema. Muestra el detalle y ofrece reintentar ese
  viaje corregido.

Cuando **no queden guías duplicadas sin resolver**, **marca la solicitud como
procesada** según su intake:
- Intake `correo` → etiqueta (Gmail) o categoría/carpeta (Outlook), según
  `marca_procesado`. Si el conector no tiene permiso de escritura (en Gmail,
  *"insufficient authentication scopes"*), avísale al usuario qué permiso le falta
  —scope `gmail.modify`.
- Intake `archivo` → aplica la convención configurada (mover a `procesados/`,
  renombrar con sufijo, etc.). Si no tienes permiso de escritura en la ubicación,
  avísale.

Si no puedes marcar, sigue igual: reprocesar **no duplica**, porque los `code` ya
cargados vuelven como `already_loaded`. Solo significa que la próxima corrida
volverá a revisar lo mismo.

Dos avisos sobre timeouts de api-v2:
- Si la respuesta viene como **indeterminate**, NO afirmes que falló. Vuelve a
  llamar a `create_backlog_trips` con los mismos viajes: los que sí quedaron
  aparecen como `already_loaded` y los que no, se cargan. Reintentar no duplica.
- `get_trip_status` **no sirve para verificar de inmediato** después de un
  timeout: hay lag y puede devolver `not_found` para viajes que sí se
  escribieron. Confía en el reintento de `create_backlog_trips`.

## Paso 5.1 · Guías repetidas (ya existen)

Que un `code` ya exista **no** significa siempre "ya se hizo": los mandantes
repiten o se equivocan en el número de guía. Por **cada** viaje en
`already_loaded`, muéstraselo al usuario (código, destino, hora) y pregúntale:

1. **"Ya se hizo, quítalo"** → sácalo del listado.
2. **"Es un error del mandante, corrige el número"** → pídele el **nuevo número
   de guía** y cámbiaselo. Queda pendiente de cargar con el código corregido.

Cuando hayas resuelto todas, **vuelve a llamar `create_backlog_trips`** con la
lista actualizada. Reintentar es idempotente: los ya cargados vuelven como
`already_loaded` y se saltan solos. Repite hasta que quede vacío.

Informa al usuario:

> Cargué **N viajes** al backlog. *(M quedaron con dudas: …)*
> ¿Quieres que los asigne?

## Paso 6 · Asignar (si el usuario acepta)

### 6.0 · Primero la primera vuelta, después la segunda

**Nunca asignes el día completo de una sola vez.** Se asignan **solo las primeras
vueltas** — el bloque de salidas de la mañana, una por móvil. Las **segundas
vueltas** quedan **pendientes en el backlog** y se asignan más tarde, **según
cómo le fue a cada conductor en su primera vuelta**: quién volvió a tiempo, quién
se atrasó, quién quedó cerca del próximo origen.

Qué ventanas son primera y cuáles segunda lo dice la especificación del mandante.

Cuando el usuario pida asignar, propón **solo la primera vuelta**, dile
explícitamente que las segundas quedan para después, y ofrécele retomarlas más
tarde en el día.

### 6.1 · Criterios de asignación

Hay dos niveles y no se mezclan: **las validaciones de la cuenta** (duras, las
aplica la plataforma) y **el criterio del mandante** (encima de ellas).

#### Validaciones de la cuenta — las aplica el sistema al planificar

Al asignar, la plataforma corre hasta **cuatro validaciones, y cada cuenta activa
las que necesita** (pueden estar todas apagadas o todas exigiendo). Para el detalle
consulta el manual con `ask_drivetech_knowledge_base` (*"qué valida el sistema al
planificar desde el backlog"*). Son:

1. **Características** — lo que el viaje pide en `skills_required` debe estar en las
   del vehículo.
2. **Capacidad** — que la unidad sea capaz de llevar la carga.
3. **Cupo y hora en el origen** — el origen agenda por cupos/horarios (Plan de
   Agenda): hora de carga válida según cupo, tope por faena y antelación mínima
   (ver §6.2, `get_backlog_load_slots`).
4. **Restricciones del recurso** — documentación, mantención, cuestionarios,
   bloqueo temporal, GPS caído, hallazgos. Un vehículo o conductor que las incumple
   **no se puede asignar**.

**No le pases el trabajo a la tool de rechazar:** `get_assignable_resources` ya te
dice quién cumple y quién trae `bloqueos` (y por qué). Propón solo recursos
asignables; un rechazo delante del usuario es una propuesta mal hecha, no un
control que funcionó. Qué validaciones estén activas depende de la cuenta — **no
asumas**, míralo en lo que devuelven las tools.

Sobre las **características** en particular:

**Lo que el viaje pida en `skills_required` tiene que estar en las `skills` del
vehículo.** Un viaje que pide S28 va en un móvil con S28; uno que pide C14, en
uno con C14. No hay excepción, no hay "por esta vez", no hay criterio del
mandante que la pase a llevar.

**Un viaje puede legítimamente no exigir ninguna característica.** Hay
operaciones donde la flota es homogénea y no se clasifica por tipo de vehículo:
ahí `skills_required` viene **vacío y está bien**. No lo trates como un dato
faltante, no preguntes por él y no inventes una característica. Con
`skills_required` vacío **cualquier vehículo de la faena califica**, y el reparto
lo decide únicamente el criterio del mandante.

Si esa operación **sí** usa características, su especificación lo dice. Ante la
duda, es la especificación del mandante la que manda, no lo que traiga un viaje
suelto.

#### Criterios del mandante — encima de lo anterior, nunca en vez de.

Cumplida la característica, **cómo se reparte entre los que cumplen lo define la
especificación del mandante**: rotación, cercanía, afinidad conductor-destino,
carga pareja de la semana, lo que sea que esa operación acordó. Léelo ahí.

Si la especificación **no define un criterio**, pregúntale al usuario cuál usar y
déjalo escrito en el archivo del mandante. No inventes uno ni asumas que el
"conductor habitual" del vehículo es el criterio: ese campo dice quién maneja
normalmente ese móvil, no quién debería hacer ese viaje.

#### Receta: cuando el criterio es rotación

Saca el historial reciente (sin hitos, que acá no aportan):

```
get_trip_status(date=<hace 5-7 días>, date_to=<ayer>,
                group_name=<faena>, include_timestamps=False)
```

Arma la matriz **conductor × destino** con la fecha de la última vez. Asigna
prefiriendo, para cada viaje, al conductor que **hace más tiempo (o nunca) no va
a ese destino**, y resuelve primero los viajes con menos candidatos libres de
repetición — si dejas para el final el que tiene una sola opción, te quedas sin
ella.

Cuidado con los **tramos largos**: suelen quedar pegados a los mismos conductores.
Rotar de verdad significa sacarlos de ahí de vez en cuando, pero alguien tiene
que quedar disponible para esos tramos. Cuando lo propongas, dilo.

Y recuerda el 6.3: la matriz se arma con lo que **efectivamente pasó**, no con lo
que se propuso, porque las asignaciones cambian durante el día.

### 6.2 · Elegir vehículo, conductor y hora de carga

1. **Recursos:** `get_assignable_resources(code=<code>)` — vehículos y conductores
   de la faena para esa fecha, en una sola llamada. Cada candidato trae su
   **`agenda`** del día (los viajes que ya tiene, para **no pisarle la hora**) y el
   **`conductor_habitual`** del vehículo cuando existe. Llámala **sin `search`**
   para ver la dotación completa. Ojo:
   - Los **ocupados no se esconden** — en una faena chica un conductor hace varios
     viajes al día; usa la `agenda` para no solaparlo.
   - Si la cuenta valida **tipos de vehículo**, las **rampas/trailers vienen en una
     lista aparte** (`trailers`) y los tractos vienen marcados con
     **`requiere_trailer`**.
   - Los recursos que incumplen una **restricción** traen **`bloqueos`** con el
     motivo y quedan al final: **no los propongas.**

2. **Hora de carga:** si el viaje **no trae hora comprometida** y la cuenta agenda
   por cupos en el origen, pide los horarios con **`get_backlog_load_slots(code)`**
   (vienen en hora local, ya descontados los cupos tomados, el tope por faena y la
   antelación mínima). Elige uno disponible; **no ofrezcas los atrasados** salvo que
   no haya ninguno, y ahí avisa el atraso (`se_pueden_tomar_con_atraso` dice si la
   cuenta siquiera lo permite). Si el usuario dicta una hora, úsala para confirmar
   contra los slots.

3. **Propón y confirma:** solo recursos **asignables** (cumplen características/
   capacidad, sin `bloqueos`), respetando la `agenda` y el criterio del mandante
   (§6.1). Si la cuenta usa tipos, propón el **par tracto + rampa**. No adivines si
   hay más de un candidato: pregunta.

4. **Asigna:** `assign_backlog_trip(code, vehicle, driver, [trailer], [copilot],
   [load_datetime])`. `vehicle`/`driver` pueden ir como patente, nombre, RUT o id;
   la tool los resuelve, y si hay **ambigüedad devuelve candidatos** → pregunta, no
   adivines. Maneja los tres bloqueos que la tool puede pedir confirmar:
   - **Otra faena** → confirma con el usuario y reintenta con `confirm_other_group=true`.
   - **Carga atrasada** (el slot llega tarde y la cuenta lo permite) → confirma y
     reintenta con `confirm_late_load=true`.
   - **Tipos de vehículo** → rechaza una rampa como principal y **exige `trailer`**
     cuando el principal es un tracto camión: manda el par.
   - Cualquier otro rechazo (característica, capacidad, restricción) → lee el motivo,
     elige otro recurso; no insistas con el mismo.

Asigna **de a un viaje a la vez**, nunca en paralelo: asignar **no es
idempotente** (el backlog se consume). Si una llamada se cae por timeout, **no
reintentes**: verifica primero con `get_trip_status`.

### 6.3 · Reasignar es normal, no es un error

La primera vuelta se planifica **el día anterior**, así que el día del viaje pasa
seguido que el conductor o el vehículo ya no están disponibles y hay que
cambiarlos. Que un viaje aparezca con otro móvil o conductor del que propusiste
**no significa que algo salió mal**: significa que la operación se ajustó.

Consecuencias prácticas:

- **La verdad es lo que dice `get_trip_status`**, no lo que asignaste tú. Antes de
  informarle al mandante quién hace cada viaje, o de evaluar la rotación contra
  el historial, lee la asignación vigente. Nunca reportes de memoria.
- **Todavía no hay tool para reasignar.** Hoy el cambio se hace en la plataforma.
  Si el usuario te lo pide, dile que hay que hacerlo ahí y ofrécele releer el
  estado después para dejar la información al día.

## Paso 7 · Mostrar el estado

Cuando termines de asignar, llama a
`get_trip_status(codes=[...], include_timestamps=False)` y muéstrale al usuario
una tabla: código, destino, hora comprometida, estado (`stage` backlog/dispatch),
vehículo y conductor asignados. Deja visible qué quedó pendiente para la segunda
vuelta.

Acá `include_timestamps=False` es lo correcto: recién asignaste, no hay hitos que
mirar y la respuesta queda ~40% más liviana. Los tiempos se piden en el Paso 8.2,
cuando la pregunta pasa a ser de cumplimiento.

## Paso 8 · Comunicación con el mandante (solo si el mandante la requiere)

Algunos mandantes esperan que les cuenten **quién va a hacer cada viaje** (la
confirmación de asignación) y/o **cómo van saliendo durante el día** (el reporte de
estado). **Otros no requieren nada** — típicamente un mandante de carga que sube su
propio backlog no se responde a sí mismo. Cada cosa es **opcional y por mandante**.

Dos condiciones para responder, y tienen que cumplirse las dos:

1. **El perfil del mandante lo requiere.** Su `spec_md` (sección de comunicación)
   dice si quiere confirmación de asignación, reporte de estado, ambos o ninguno, y
   con qué datos y frecuencia. Si no lo requiere, **no le respondas** — aunque
   técnicamente pudieras.
2. **Hay a quién responder.** `responder_a` tiene destinatarios (con `copiar_a` en
   copia si está). Si está vacío, sáltate el paso completo.

Siempre sobre el **mismo hilo** del correo original. El concepto es igual para
todos; qué se informa, con qué frecuencia y en qué formato lo define el perfil.

### 8.1 · Confirmación de asignación (si el mandante la requiere)

Si el mandante pide que se le confirme quién hace sus viajes: apenas termines de
asignar (la primera vuelta, cuando aplique), **arma la confirmación** — tabla de
viajes con destino, hora comprometida, patente y conductor — como **borrador** a
`responder_a`, y **no la envíes sin visto bueno** del usuario. Deja explícito que
es la primera vuelta y que el resto se confirma más tarde, para no comprometer algo
que todavía no está decidido.

Si el mandante **no** requiere la confirmación de asignación, sáltate este punto
aunque tenga `responder_a` (puede querer solo el reporte de estado, o nada).

### 8.2 · Reporte de estado durante el día (si el mandante lo requiere)

**El formato NO lo inventas: lo lee la plantilla de la empresa.** La config trae
`extra.reporte_tipo` (Markdown), que es la **base** — estructura, columnas, de dónde
sale cada dato, reglas de cálculo, semáforo, colores y el sobre del correo. Encima de
esa base va el **delta del mandante**: si su `spec_md` tiene una sección
**"Reporte de status: ajustes"**, contiene *solo las diferencias* (columnas que
agrega o quita, umbrales propios, cómo agrupa el resumen, textos, colores). Base +
delta, y lo que el delta no menciona se hereda.

Los dos son Markdown opaco: **léelos y aplícalos literal**, no los resumas ni los
reinterpretes. Si la base pide una columna cuyo dato la plataforma no expone, la
columna sale marcada como pendiente y se lo dices al usuario — **nunca inventes el
dato ni dejes la celda en blanco**.

Para armar el reporte, **una sola llamada** trae todo el día:

```
get_trip_status(date=<día>, group_name=<grupo del mandante>,
                include=["trailer", "observations", "reception"],
                include_timestamps=True, limit=200)
```

Los tres `include` importan: `trailer` da la patente de la rampla, `observations` las
indicaciones y comentarios de cierre, y `reception` el formulario de recepción con sus
campos ya resueltos a nombre (números de documento, fotos, firma). Sin ellos esas
columnas vienen vacías y parecen datos faltantes cuando no lo son. Sube el `limit` si
el día trae más viajes. Complementa con `get_fleet_vehicles(vehicle_filter=[patentes])`
cuando la plantilla pida el nombre interno del móvil o su tipo.

**Si la empresa todavía no tiene plantilla** (`extra.reporte_tipo` vacío), usa el
formato genérico de tres grupos y ofrécele al usuario dejarlo guardado como plantilla
de la empresa:

- **Realizados** — hora de llegada al destino, hora de salida y **tiempo de
  permanencia** (salida − llegada). Si el mandante lo pide, también la llegada y
  salida del origen.
- **En ruta** — ETA al destino y hora comprometida, para que se vea si va en
  hora o atrasado.
- **Pendientes** — los que aún no salen, con su ventana comprometida. Incluye
  acá lo que todavía está en backlog esperando segunda vuelta.

De dónde sale cada dato, con `get_trip_status`:

| Dato | Campo |
|---|---|
| Estado / subestado | `state`, `substate`, `substate_reason` |
| Hora comprometida / de carga | `hour`, `load_datetime` |
| ETA | `eta` |
| Llegada y salida del origen | `origin_arrival_datetime`, `origin_departure_datetime` |
| Llegada y salida del destino | `destiny_arrival_datetime`, `destiny_departure_datetime` |
| Permanencia en destino | `destiny_departure_datetime` − `destiny_arrival_datetime` |
| Vehículo y conductor | `vehicle_plate`, `vehicle_name`, `driver_name` |
| Rampla | `trailer_plate` (con `include=["trailer"]`) |
| Tipo de viaje | `trip_type` — **tal cual lo entrega el TMS**, no lo traduzcas |
| Documentos y respaldos | `reception_form` (campo → valor, y `file_url` de las fotos), `form_completed` |

**Con una sola llamada te alcanza.** `get_trip_status` trae los hitos de
origen/destino también cuando pides varios códigos (o por `date` /
`group_name`), así que el reporte completo del día sale de una consulta. No
consultes viaje por viaje.

- `include_timestamps=False` saca los hitos y ahorra ~40% de la respuesta. Úsalo
  **solo** cuando la pregunta no sea de cumplimiento — un panorama de dónde va
  cada uno. Para un reporte al mandante, déjalo en `True`.
- La **bitácora** de un viaje (quién lo asignó, cuándo, qué se editó) sí requiere
  pedir **ese código solo**. Sirve para explicar un caso puntual, no para el
  reporte diario.

⚠️ **Un hito ausente NO significa que no ocurrió**, significa que no quedó
registrado. Muchas empresas ni siquiera comprometen `load_datetime`. Esto importa
el doble acá: estás informándole a un tercero sobre el desempeño de un conductor.
Si falta el dato, dilo como dato faltante — nunca lo reportes como atraso ni como
incumplimiento.

En la práctica los hitos vienen **disparejos**: es normal que un viaje entregado
tenga llegada al destino pero no salida, y por lo tanto no se le pueda calcular
la permanencia. Reporta la permanencia solo de los que tienen los dos hitos y di
cuántos quedaron sin dato, en vez de mostrar una columna a medio llenar.

⚠️ **Un mismo hito puede significar cosas distintas según la operación.** Antes
de traducir una hora a una frase, revisa qué dice la especificación del mandante:
según cómo funcione la faena, "llegó al origen" puede ser del día anterior (camiones
que pernoctan en planta), o `load_datetime` puede no existir sin que eso sea un
incumplimiento. Ese es justamente el tipo de cosa que el delta del mandante corrige
—por ejemplo, medir la permanencia de origen desde `load_datetime` en vez de desde la
llegada.

### 8.3 · Antes de enviar

1. Redacta el correo **en el mismo hilo del requerimiento** del mandante, con el
   saludo, las tablas y el cierre que indique la plantilla, y firmado con la `firma`
   de la config (`get_backlog_settings`). Si el requerimiento **no llegó por correo**
   (planilla, carpeta, mensaje, teléfono), arma igual un **borrador nuevo** con el
   mismo cuerpo y un asunto que identifique mandante y fecha.
2. Créalo como **borrador de respuesta** y muéstraselo al usuario.
3. **Nunca lo envíes sin visto bueno.** Es correo que sale de la empresa hacia un
   tercero: el usuario decide si sale y con qué texto. Si la instalación quiere
   reportes automáticos sin revisar cada uno, tiene que ser una decisión
   explícita del usuario, no un default tuyo.
4. Si la conexión de correo no permite enviar, dile que el borrador quedó listo y
   que lo mande él.

---

## Paso 9 · Aprender y persistir reglas nuevas

**El perfil de un mandante es vivo, no se congela en el descubrimiento.** Operando
—sobre todo al asignar— el usuario va a ir dando instrucciones para casos borde y
situaciones puntuales ("a esta tienda mándale siempre tal conductor", "si viene
sin patente, tal cosa", "los viajes a la costa no antes de las 11"). **Todo lo que
generalice se guarda en el backend**, en el `spec_md` de ese mandante. Nada de eso
puede perderse al cerrar la sesión: la próxima corrida, en otra máquina o dentro de
seis meses, tiene que seguir valiendo.

Cómo hacerlo, cada vez que el usuario te dé una instrucción así:

1. **Distingue durable de una-sola-vez.** Una regla que se va a repetir ("de ahora
   en adelante…", "siempre que…", "para esta tienda…") es durable. Un ajuste solo
   para el viaje de hoy, no. Ante la duda, **pregunta**: *"¿lo dejo como regla
   permanente para \<mandante\> o es solo por hoy?"*.
2. **Ubícala en la sección correcta** del `spec_md`: mapeo, regla de origen,
   característica, criterio de asignación, comunicación, o "Particularidades". Si no
   calza en ninguna, agrégala bajo una sección **"Reglas aprendidas en operación"**.
3. **Read-modify-write:** trae el perfil actual con `get_backlog_settings(slug)`,
   edita el `spec_md` (agrega/ajusta esa regla, deja el resto **byte-idéntico**) y
   guárdalo con `upsert_backlog_mandante` reenviando todos los campos. El backend
   sube la versión y deja snapshot solo — no mandes `version`.
4. **Actualiza la fecha** del encabezado del perfil (`actualizado: YYYY-MM-DD`).
   `esquema` no se toca.
5. **Confírmalo en una línea**: *"Anotado en el perfil de \<mandante\> (v\<N\>):
   \<regla\>"*, para que el usuario sepa que quedó guardado y desde cuándo.

**Las dudas abiertas se cierran igual.** El perfil trae una sección **"Dudas
abiertas"** con lo que quedó sin resolver en el descubrimiento (un destino que no
está en el catálogo, un criterio que nadie tenía definido). Cuando el usuario
conteste una de ellas operando, hazlo en el mismo `upsert`: escribe la regla en la
sección que corresponda y **borra la línea de "Dudas abiertas"**. Y al revés — si
operando aparece una pregunta que el usuario no puede contestar ahora, **agrégala
ahí** en vez de dejarla en la conversación: la próxima corrida es otra sesión.

No reescribas ni "mejores" el resto del perfil de paso: toca solo lo que cambió.
Si dos cambios entran juntos, agrúpalos en un solo `upsert`.

**Un caso especial: los cambios al reporte.** Antes de guardarlo, pregúntate a quién
le sirve:

- **A este mandante nada más** ("a Easy mándale también la temperatura", "para ellos
  la permanencia se mide desde la hora de carga") → va al **delta**, en la sección
  "Reporte de status: ajustes" de su `spec_md`, con `upsert_backlog_mandante`.
- **A todos** (una columna que faltaba, el color corporativo, el saludo del correo) →
  va a la **plantilla de la empresa**, `extra.reporte_tipo`, con `set_backlog_config`.
  Recuerda que `extra` se **reemplaza completo**: lee la config, mezcla tu cambio y
  reenvía el resto.

Ante la duda, pregunta. Meter en la base algo que era de un solo mandante ensucia el
reporte de todos; meter en el delta algo que era de todos obliga a repetirlo N veces.

---

## Reglas de oro

- **Nombres como en la plataforma.** Ante duda, `get_tms_catalog`. Nunca inventes.
- **Los datos que cambian no se escriben en la skill.** Patentes, conductores,
  tiendas, dotación: eso sale del catálogo y de `get_assignable_resources` en el
  momento. En los archivos va la **regla para reconocerlos**, nunca la lista —
  una lista escrita queda vieja sin avisar y se arrastra a cada cliente que
  reciba una copia.
- **`code` = el número de guía del mandante.** Es lo que hace que reprocesar la
  misma solicitud (correo o archivo) no duplique.
- **Lo que se aprende se guarda (Paso 9).** Toda regla nueva de un mandante va al
  `spec_md` en el backend vía `upsert_backlog_mandante`. Nada de know-how operativo
  se queda solo en la memoria de la sesión.
- **El perfil se edita, nunca se pisa.** `upsert_backlog_mandante` reemplaza el
  perfil completo: lee con `get_backlog_settings(slug)`, cambia solo lo que cambió y
  reenvía el resto byte-idéntico.
- **Confirma antes de crear** salvo que `auto_crear = true`.
- **Las características que el viaje exija se respetan siempre.** El vehículo
  tiene que cumplir las `skills_required` del viaje: ningún criterio de mandante
  las pasa a llevar. Si el mandante usa características y el correo no las trae,
  pregunta — no cargues sin ellas. Si **no** las usa, `skills_required` vacío es
  lo correcto y cualquier vehículo califica.
- **Respeta las validaciones de la cuenta.** Al asignar, la plataforma valida
  características, capacidad, cupo/hora del origen y restricciones del recurso —
  cuáles están activas lo define la cuenta. Propón solo recursos asignables
  (`get_assignable_resources` marca los `bloqueos`), pide la hora con
  `get_backlog_load_slots` cuando el origen agenda por cupos, y no asumas: míralo en
  las tools.
- **Cómo repartir entre los que cumplen lo define el mandante.** Está en su
  especificación; si no está, pregunta y déjalo escrito ahí. El "conductor
  habitual" es referencia de vehículo, no criterio de asignación.
- **Respeta la agenda del recurso.** Un conductor/vehículo ocupado no se esconde;
  usa su `agenda` del día para no solaparle la hora.
- **Primero las primeras vueltas.** Las segundas se asignan después, viendo cómo
  le fue a cada conductor en la mañana. Nunca asignes el día completo de una vez.
- **Al mandante solo si lo requiere.** La confirmación de asignación y el reporte de
  estado se le mandan **únicamente si su perfil lo pide** y hay `responder_a`. Y
  siempre como borrador: nunca envíes correo sin visto bueno.
- **El formato del reporte no se improvisa.** Sale de `extra.reporte_tipo` (la
  plantilla de la empresa) más el delta del mandante, aplicados literal. Lo que la
  plataforma no expone se marca pendiente; no se inventa.
- **No proceses dos veces:** marca la solicitud al terminar (etiqueta el correo o
  mueve el archivo a procesados) y filtra por esa marca en la próxima corrida.

---

## Cómo agregar un mandante nuevo

Usa la skill **`descubrir-mandante`**. Hace justo esto y no hay una versión corta
que valga la pena: lee muestras reales, infiere el mapeo campo por campo, lo valida
contra el catálogo y contra una carga de prueba, entrevista al usuario por las
reglas de asignación y comunicación, y guarda el perfil con
`upsert_backlog_mandante`. Si el mandante **ya existe** (cambió de formato), esa
skill parte del perfil vigente y preserva lo aprendido en operación.

`SKILL.md` no se toca al agregar un mandante — todo lo que cambia entre mandantes
vive en su `spec_md`.

Si por alguna razón lo armas a mano, la forma del perfil (secciones, encabezado
`esquema`, campos de `create_backlog_trips`) está en
**`descubrir-mandante/references/esquema-perfil.md`**, y `mandantes/ejemplo.md` es
un perfil bien hecho para copiar. Lo mínimo que no puedes saltarte:

- Trabaja sobre **una muestra real ya recibida**, no sobre lo que el usuario te
  cuente que trae.
- Hazle **confirmar el mapeo** antes de guardar; lo que no reconozcas, pregúntalo.
- Valida con **un viaje** (`dry_run=true`, después real) y **revisa en la
  plataforma** que la hora comprometida se vea como en la solicitud. Si aparece
  corrida, estás convirtiendo la hora dos veces.
