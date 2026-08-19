---
name: seguimiento-operacion
description: >-
  Seguimiento intradía de la operación de viajes ya cargados y asignados en el TMS
  de Drivetech. Da el panorama del día (estado de cada viaje, hora comprometida,
  ETA, permanencia en origen/destino, tiempo en ruta), detecta anomalías (atrasos,
  viajes sin iniciar, permanencias o rutas demasiado largas, GPS sin reportar) y
  audita contra geocercas para distinguir un problema real de un problema de
  geocerca (el viaje se inicia/cierra con la entrada/salida a las geocercas de
  origen y destino, y eso a veces falla). Consulta el manual del centro de
  conocimiento sobre inicio/cierre automático de guías para no confundir el
  comportamiento normal con un problema, y cuando la causa es la geocerca recomienda
  ajustarla. Sirve tanto a la empresa de transporte
  (vista interna) como para armarle el estado al mandante. Úsala cuando pidan
  "cómo va la operación", "revisar los viajes de hoy", "el estado del día",
  "estadías", "tiempos en ruta", "qué viajes están atrasados", "auditar un viaje",
  "problemas de geocerca", o el reporte de avance para el mandante.
---

# Seguimiento de la operación

Una vez que los viajes están cargados y asignados (skill `cargar-viajes-backlog`),
esta skill acompaña la jornada: **panorama → anomalías → auditoría de geocercas**,
y de ahí el reporte interno o para el mandante.

## Requisitos

- **MCP de Drivetech** conectado, con la **empresa activa correcta**. Si el token
  ve varias empresas, confírmala al empezar (`get_current_enterprise_name`; si no
  es la esperada, `select_enterprise`) — la selección se pierde sola.
- El **perfil del mandante** (`get_backlog_settings(slug=…)`) trae, en su `spec_md`,
  cómo se lee esta operación (qué hitos importan, umbrales propios, qué quiere ver
  el mandante en el reporte). Léelo antes de interpretar tiempos.

## Idea base — hito ausente ≠ incumplimiento

Los viajes se inician y cierran con la **entrada/salida a las geocercas** de origen
y destino. Si un hito no está, puede ser (a) que de verdad no pasó, o (b) que la
geocerca no lo registró (geocerca chica, el camión estacionó afuera, GPS sin
reportar). **Nunca reportes un atraso o incumplimiento sin antes descartar el
problema de geocerca** (Paso 3). Un dato faltante se informa como dato faltante.

## Cómo el sistema inicia y cierra las guías — CONSULTA EL MANUAL

Antes de interpretar cualquier hito raro, **consulta el manual del centro de
conocimiento** con `ask_drivetech_knowledge_base` (query: *"cómo se inician y
finalizan automáticamente las guías al salir del origen y del cliente"*). Es la
mecánica real y evita falsos positivos. Lo esencial:

- **El viaje NO inicia al entrar al origen, sino al SALIR de él** — y solo si el
  vehículo estuvo dentro de la geocerca el **tiempo mínimo de permanencia
  configurado**. Una salida muy breve puede no gatillar el inicio.
- **Una salida inicia UN viaje.** Si el móvil tiene varias guías pendientes en ese
  origen, el sistema toma una como cabecera (por nº de viaje / hora de carga / hora
  comprometida) y **las demás quedan pendientes para la próxima salida**. Por eso
  una guía puede quedar "sin iniciar" aunque el camión ya haya salido.
- **El cierre NO es inmediato.** Tras salir del cliente hay un **tiempo de
  finalización automática (por defecto ~30 min)** antes de marcar Entregada; y la
  cuenta no corre mientras el vehículo siga dentro. Tope de espera: **3 horas**.
- **Excepción:** si la operación recibe guías ya iniciadas desde un sistema externo
  de facturación, la salida del origen sella todas las pendientes de esa geocerca y
  no aplica la agrupación.

Usa esto como el **libro de reglas** del Paso 3: muchas cosas que "parecen"
anomalía son el comportamiento esperado (una guía recién salida del cliente dentro
de la ventana de ~30 min **no** está atrasada en cerrar; una guía "sin iniciar"
puede estar esperando la próxima salida o no haber cumplido la permanencia mínima).

## Paso 1 · Panorama del día

Llama `get_trip_status` por `date` (hoy) y/o `group_name`, con
`include_timestamps=True`. Con eso arma la vista por estado:

- **Pendientes / Sin asignar** — cargados que aún no salen.
- **Asignados** — con conductor/vehículo, aún sin iniciar.
- **En ruta** — con salida de origen y sin llegada a destino.
- **Entregados** — con llegada (y ojalá salida) de destino.

Calcula, cuando estén los dos hitos:

- **Permanencia en origen** = `origin_departure_datetime` − `origin_arrival_datetime`.
- **Permanencia en destino** = `destiny_departure_datetime` − `destiny_arrival_datetime`.
- **Tiempo en ruta** = `destiny_arrival_datetime` − `origin_departure_datetime`.
- **Cumplimiento** — `hour` (comprometida) y `eta` vs. lo real. Si la operación no
  usa `hour` (p.ej. ICB), no inventes una ventana: mide contra lo que sí exista.

Reporta permanencia/ruta **solo de los que tienen los dos hitos**, y di cuántos
quedaron sin dato — no muestres una columna a medio llenar.

## Paso 2 · Detección de anomalías

Marca como anomalía (umbrales **por defecto**, ajustables por mandante en su
`spec_md` — ver Paso 5):

| Anomalía | Regla por defecto |
|---|---|
| **Atrasado** | hay `hour` comprometida, ya pasó y el viaje no avanzó, o `eta` la supera por > **30 min**. |
| **Sin iniciar** | ya debió partir (pasó su hora/carga por > **30 min**) y sigue sin hito de salida de origen. |
| **Permanencia excesiva en origen** | > **60 min**. |
| **Permanencia excesiva en destino** | > **45 min**. |
| **En ruta demasiado tiempo** | salió de origen hace > **4 h** sin llegada a destino (o > 50% sobre lo típico de esa ruta si el perfil lo define). |
| **Hitos inconsistentes** | llegada a destino sin salida de origen, etc. |
| **GPS sin reportar** | el móvil no reporta hace > 24 h (lo marca `get_vehicles_inside_geofence`). |

**No marques como anomalía lo que es comportamiento normal del sistema** (ver la
sección del manual): una guía que **salió del cliente hace < ~30 min y aún no
figura Entregada** está en su ventana de cierre automático, **no** es un atraso de
cierre; una guía "sin iniciar" cuyo par ya salió puede estar esperando la próxima
salida del origen. Descártalo antes de alertar.

Cada anomalía que **huela a problema de hito/geocerca** (sin iniciar pese a que el
móvil salió, en ruta eterno, entregado sin salida, hitos inconsistentes) pasa al
Paso 3 **automáticamente**. Las demás (permanencia real, atraso con hitos
completos) se reportan directo.

## Paso 3 · Auditoría de geocercas

Objetivo: para un viaje sospechoso, decidir si es **problema real** o **problema de
geocerca/registro**. Corre **auto** en los sospechosos del Paso 2, y **on-demand**
cuando te pidan auditar un código puntual.

Interpreta todo con el **libro de reglas del manual** (sección anterior). Para el
viaje (tienes su patente, origen y destino del `get_trip_status`):

1. **¿Está adentro ahora?** `get_vehicles_inside_geofence(plates=[patente])` — si el
   móvil está dentro de la geocerca de destino hace rato pero el viaje no figura
   "entregado", el hito de cierre no se gatilló: **problema de registro**, no
   atraso. Si sale `gps_sin_reportar`, el GPS está caído: no concluyas atraso.
2. **¿Hubo visita cerrada?** `get_geofence_visits(plates=[patente], start_date, end_date, min_minutes=0)`
   sobre el día — busca entradas/salidas en las geocercas de **origen** y **destino**
   (empareja por nombre con `origin_name` / `client_name`). Cruza contra la mecánica:
   - Si hay visita al **origen** pero el viaje no inició → mira la **duración de esa
     visita**: si fue muy breve, probablemente **no cumplió la permanencia mínima**
     y por eso la salida no gatilló el inicio. O el viaje quedó fuera de la
     agrupación de esa salida (otra guía fue cabecera) y espera la próxima.
   - Si hay visita al **destino** (entró y salió) pero no cerró → ¿fue hace < ~30
     min? Es la ventana normal de cierre, espera. ¿Fue hace más? El cierre falló.
3. **Si aún hay duda**, `get_vehicle_history(patente, start_date, end_date)` en la
   ventana del viaje: mira si el móvil pasó por/paró en el origen o destino aunque
   la geocerca no lo capturara (estacionó afuera, geocerca chica/mal ubicada).

Concluye con **causa probable + acción sugerida**, sin arreglar nada solo:

- *Problema de geocerca* (el móvil sí pasó pero el hito no se gatilló: visita muy
  breve, estacionó afuera, borde mal puesto) → di la causa y **recomienda ajustar
  la geocerca**: agrandarla o reposicionarla para que capture bien las entradas/
  salidas, o revisar el **tiempo de permanencia mínima** si está cortando inicios
  legítimos. Esto es clave: no basta con cerrar el viaje a mano hoy — si la geocerca
  no se ajusta, **el problema se repite todos los días**. Mientras tanto, cerrar/
  iniciar la guía manual desde la plataforma.
- *Comportamiento normal del sistema* (ventana de cierre de ~30 min, guía esperando
  la próxima salida) → dilo como tal, no como problema.
- *Problema real* → "no hay evidencia de que llegara; el móvil está en otro lado."
- *GPS caído* → "sin reporte del equipo; no se puede confirmar, revisar dispositivo."

**Nunca cierres, reasignes ni edites** viajes automáticamente: propón y deja que el
usuario decida en la plataforma.

## Paso 4 · Reporte

Según a quién sea (puede ser a los dos):

- **Interno (empresa de transporte):** panorama + lista de anomalías con su causa
  probable y qué revisar. Directo y accionable.
- **Al mandante:** arma el estado **según las reglas de comunicación del perfil**
  (`spec_md`): qué datos quiere (¿permanencia? ¿hitos de origen?), cada cuánto, y
  cómo se leen los hitos en esa operación. Déjalo como **borrador** a `responder_a`
  y **no lo envíes sin visto bueno**. Si `responder_a` está vacío, esta operación no
  le reporta a un tercero: sáltatelo.

En todos los casos: un hito ausente se informa como dato faltante, y una anomalía
que resultó ser problema de geocerca se dice como tal, no como incumplimiento del
conductor.

## Paso 5 · Umbrales y reglas — del perfil, y se aprenden

Los umbrales del Paso 2 son **defaults**. Si el `spec_md` del mandante define los
suyos (permanencia máxima en planta, atraso tolerable, tiempo típico de una ruta),
usa esos. Y si operando el usuario te da un criterio nuevo de seguimiento ("en la
ruta a Guacolda más de 90 min es alerta", "esta geocerca siempre falla, avísame
directo"), **persístelo en el perfil** con `upsert_backlog_mandante` (read-modify-
write del `spec_md`, byte-idéntico, el backend versiona) — igual que el Paso 9 de
la skill de carga. El seguimiento también hace al perfil más inteligente con el uso.

## Cuándo corre

On-demand ("¿cómo va la operación?", "revisa los viajes de hoy", "audita el
2329126"). Puede programarse un chequeo periódico que reporte solo si hay anomalías.

## Reglas de oro

- **Consulta el manual primero.** `ask_drivetech_knowledge_base` para la mecánica de
  inicio/cierre; es lo que separa una anomalía real del comportamiento normal.
- **Hito ausente ≠ incumplimiento.** Descarta problema de geocerca antes de reportar.
- **Si la geocerca es la causa, recomienda ajustarla.** Cerrar el viaje a mano tapa
  el hoy; ajustar la geocerca (o la permanencia mínima) evita que se repita mañana.
- **No concluyas con GPS caído.** `gps_sin_reportar` = no se puede afirmar nada.
- **No edites la operación.** Propón; el usuario cierra/reasigna en la plataforma.
- **Nombres y umbrales del perfil.** Lo que el mandante definió manda sobre los defaults.
- **Al mandante, siempre borrador.** Nunca envías sin visto bueno.
