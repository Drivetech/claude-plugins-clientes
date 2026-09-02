# Medir la confiabilidad de cada identificador

Esto es lo que separa una especificación de una **especificación con permiso para
rechazar**. La pregunta que contesta es una sola: *"¿confío tanto en que este dato va
impreso como para rechazarle una guía a un transportista?"*. Sin números, esa pregunta
se contesta con intuición.

## ⚠️ Hoy esto no se corre desde la skill

Falta la capacidad del lado de la plataforma: no hay tool que traiga las guías **con
su adjunto** y los datos del viaje que las acompaña (`get_trip_status` y
`get_tms_dispatches_by_status` devuelven el viaje pero no `custom_form_values`, que es
donde está la ruta del documento), y correr la extracción sobre cientos de documentos
y cruzarlos es **trabajo por lotes**, no algo que un agente haga en una conversación.

Lo que corresponde es una tool que **corra la medición del lado del servidor y
devuelva las tasas**. Este archivo es, mientras tanto, dos cosas:

- **La especificación de lo que esa capacidad tiene que hacer y devolver.**
- **El criterio con que se leen las tasas cuando existan** — que no cambia según quién
  las calcule.

Se corrió a mano, con un script contra la base y el endpoint, y de ahí salen los
números de más abajo. Eso no es reproducible desde una skill, y por eso la skill dice
que no puede medir en vez de aparentar que sí.

---

## La secuencia

**1 · Traer las guías con adjunto** del mandante en la ventana, cada una **con los
datos del viaje que la acompaña**: código de viaje, folio digitado si lo hay, patente,
conductor y RUT, cliente, origen y fecha. Ese es el otro lado del cruce.

**2 · Traer el denominador**, en la misma consulta o al lado: **entregas totales del
período** contra **entregas con adjunto**. No se puede reconstruir después y es la
mitad de lo que hace honesta a la medición (ver *El sesgo*).

**3 · Correr la extracción** sobre cada documento con el centinela
`Sin instrucciones adicionales.` en el texto del usuario, para que los chequeos de
contenido vuelvan vacíos. Acá se mide **extracción**, no criterio de contenido: son
dos cosas distintas y mezclarlas hace ilegible el resultado.

Notas del terreno: 15–25 s por documento; concurrencia baja (el endpoint tiene pocos
workers); los PDF se aceptan directo, multipágina, y son la mayoría de los adjuntos
reales.

**4 · Guardar la evidencia cruda** de cada corrida, tal como volvió. Sin esto no se
puede **reprocesar en frío** cuando cambie un criterio — y va a cambiar. Reprocesar
cuesta cero; volver a llamar se cobra de nuevo, porque cada llamada analiza otra vez.

**5 · Cruzar, normalizando.** Ver abajo.

**6 · Contar por identificador** y reportar.

---

## Normalizar antes de comparar — no es opcional

Comparar strings crudos produce rechazos falsos **en el primer documento que
pruebes**. Verificado sobre una guía real:

| dato | el papel dice | el sistema tiene | ¿contradice? |
|---|---|---|---|
| número de documento | `576115` | `576115` | no — idéntico |
| patente | `PPWR 55` | `PPWR55` | **no**, pero solo si quitas espacios |
| fecha | `01-09-2026` | `2026-09-01` | **no**, pero solo si parseas ambos |
| código de viaje | `T00055718` | `T00055718` | no — idéntico |

Antes de comparar: **mayúsculas**, **sin espacios ni guiones** (patentes), **RUT sin
puntos**, **fechas parseadas** a fecha real, y **ceros a la izquierda descartados** —
hay mandantes que imprimen el código como `0049420309` contra un código de `49420309`.

Si un valor trae varios candidatos separados por `/` (pasa cuando el documento lleva
más de un folio), **cada uno cuenta como candidato**: basta que uno coincida.

Cuando la normalización **no logra interpretar** un valor, el resultado es *escala*,
nunca *rechaza*.

---

## Los tres resultados del cruce

| resultado | cuándo |
|---|---|
| **coincide** | ambos lados tienen el dato y, normalizados, son iguales |
| **contradice** | ambos lados tienen el dato y son distintos |
| **no participa** | **alguno de los dos lados no tiene el dato** |

**"No participa" no cuenta para ningún lado.** Que el documento no traiga la patente
no dice nada; que **el sistema** no tenga el dato, tampoco. Las dos mitades importan:
hay operaciones con un campo vacío en el 100 % de sus guías, y un cruce ingenuo contra
ese campo las rechazaría todas.

Una precisión que evita acusaciones injustas: una diferencia de **un solo dígito** en
el número de documento (`576062` contra `576061`) no cuenta como contradicción —
escala. Aparece en datos reales y es un tipeo, no otro viaje.

---

## El sesgo: la brecha del denominador

Las guías del histórico son **las que el conductor logró subir**. Y la selección la
hace exactamente el mecanismo que estás midiendo: quien reintentó tres veces hasta que
la foto salió legible aporta una guía buena y esconde dos malas; quien se rindió no
aporta nada.

**La muestra está sesgada hacia el caso fácil, y la dirección del sesgo es siempre la
misma: las tasas son un techo, no un promedio.**

Un caso real: 719 entregas en 30 días, **371 con documento subido**. El 48 % del
volumen no está en ninguna tasa.

Qué hacer con eso:

- **La tasa se enuncia con su denominador pegado.** *"El folio se lee en el 86 % de
  las guías que llegaron a la base (371 de 719 entregas)"*, no *"el folio se lee en el
  86 %"*. Una tasa sin denominador es una afirmación sobre un universo que no se midió.
- **La brecha se reporta siempre**, aunque nadie la pida, y con su lectura: es, al
  mismo tiempo, el margen de error de todo lo demás.
- **La brecha es una serie, no un número.** Si sube, algo se rompió: la app, el
  formulario, la instrucción al conductor.
- **Si no está repartida pareja** entre conductores, rutas o destinos, no es adopción:
  es que algo específico no se puede subir. Eso es un hallazgo operativo.
- **No la corrijas.** No hay con qué estimar el sesgo desde adentro de la muestra, y
  una corrección inventada es peor que una tasa honesta con su límite declarado.

Y para lo que importa —autorizar un rechazo automático— el sesgo empuja en la
dirección conservadora: la tasa que justifica el rechazo está medida sobre el
subconjunto donde todo salió bien.

---

## Cómo se leen las tasas

Ejemplo real de un mandante transportista, sobre 116 guías:

| identificador | coincide | contradice | lectura |
|---|---|---|---|
| número de documento | 100 | 9 | fuerte — se puede exigir |
| nombre del destino | 102 | 1 | fuerte |
| código de viaje | 96 | 8 | fuerte; es el cruce que identifica el viaje exacto |
| código de cliente | 54 de 62 | 4 | sirve |
| patente | 22 | 70 | **no dictamina nunca** |
| conductor (RUT) | 30 | 75 | **no dictamina nunca** |
| código de origen | 0 de 8 | — | se midió y **no sirve**: no volver a intentarlo |

Las dos filas de "no dictamina nunca" **no son errores de lectura**: la guía se emite
en el origen con el vehículo y el transportista de ese momento, y la plataforma carga
después los reales. Los dos datos son correctos y describen instantes distintos. El
dato bueno es el del sistema, no el del papel. Reportar ese desacuerdo como
discrepancia es fabricar alarmas sobre el funcionamiento normal.

El código de origen es el ejemplo del **tercer estado**: se midió, dio que no sirve, y
esa conclusión hay que escribirla — si no, alguien lo va a volver a medir cada seis
meses.

**El mismo identificador es confiable en un mandante e inservible en otro.** En un
formulario el nombre del destino coincide 102 de 103; en otro, el papel nombra a la
razón social del mandante mientras el sistema nombra el punto de entrega, y ese mismo
cruce rechazaba **12 guías correctas de 12**. Por eso la lista no puede vivir en el
código, y por eso esta medición se hace **por mandante**.

---

## Re-medir: las tasas vencen en silencio

Una tasa medida sobre el histórico deja de valer justo cuando el mandante cambia el
formulario — el mismo evento que dispara el re-descubrimiento.

Por eso la segunda corrida **compara la tasa nueva contra la vieja**: una **caída
brusca en un identificador** es la señal de que cambió el formulario, y es una señal
barata que llega antes de que alguien note el problema por otro lado. Guarda contra
qué ventana se midió cada vez, para que la comparación sea entre cosas comparables.
