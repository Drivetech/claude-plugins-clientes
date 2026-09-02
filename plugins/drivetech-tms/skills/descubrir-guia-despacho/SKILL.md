---
name: descubrir-guia-despacho
description: >-
  Descubre cómo se lee la guía de despacho (o formulario de transporte) de un
  mandante y, cuando hay histórico, mide qué tan confiable es cada identificador
  impreso. A partir de documentos reales ya subidos por los conductores —o de 2-3
  muestras si el mandante todavía no tiene ninguno— escribe la especificación del
  formulario en lenguaje de operación (dónde va el folio, el código de cliente, la
  tabla de ítems), la valida contra guías ya digitadas a mano, cruza el histórico
  contra los viajes para sacar la tasa de cada identificador, y recién con esos
  números propone qué se puede exigir. Guarda el resultado en el `document_spec`
  del mandante, que después usa la validación documental automática. Úsala cuando
  pidan "descubrir el formato de la guía de X", "documentar la guía de despacho",
  "por qué se están rechazando las guías de X", "medir qué tan confiable es el
  folio", "configurar la validación de documentos de un mandante", o cuando un
  mandante cambie su formulario.
---

# Descubrimiento de la guía de despacho de un mandante

El activo que produces es el **`document_spec` del mandante**: la especificación de
cómo se lee su formulario, más —cuando hay con qué medir— **las tasas por
identificador** y la propuesta de qué se puede exigir. La validación documental
automática recibe ese texto en su contexto y **manda sobre su criterio genérico**.

Es una skill **hermana de `descubrir-mandante`, no un paso suyo.** Un mandante recién
configurado todavía no tiene guías: el papel firmado aparece cuando empieza a operar.
Y las dos se rehacen en momentos distintos — aquélla cuando el mandante cambia **cómo
pide viajes**, ésta cuando cambia **su formulario**.

## Las tres reglas de oro

**1 · Documentos reales, nunca la descripción de memoria.** Igual que en el
descubrimiento del mandante: pide el papel de verdad y léelo tú. Si el formato varía,
pide varios.

**2 · Describe el papel, no le des instrucciones a un modelo.** La especificación la
va a **corregir un jefe de operaciones** el día que el mandante cambie su formulario,
no un programador ni alguien que sepa de prompts.

> **Bien:** *"El folio va en el recuadro superior derecho, rotulado «N° documento
> Transporte»."*
> **Mal:** *"Extraer el campo numero_documento del sector superior derecho."*

Si lo escribes en el segundo estilo, lo único que puede mantenerlo es quien sepa
escribir prompts — y ese es exactamente el problema que esta skill viene a resolver.

**3 · Prender una bandera se decide con números, no con una observación.** Una bandera
autoriza a **rechazarle una guía a un transportista**. Con dos muestras se ve que un
dato *aparece*; no se ve con qué frecuencia ni si coincide con lo que el sistema
tiene. Eso necesita una tasa medida. Sin tasa, la spec se guarda igual y las banderas
quedan apagadas — **a propósito y dicho**, no por accidente.

## Requisitos de conexión

- **MCP de Drivetech** conectado, con la empresa correcta. Si el token ve varias
  empresas, confírmala al empezar (`get_current_enterprise_name`; si no es la
  esperada, `select_enterprise`) — la selección se vence sola y el error que
  aparece después dice *"la empresa no tiene contratado el módulo de tms"*, que
  parece un problema de permisos y no lo es.
- **La tool de configuración documental del mandante** (la que escribe
  `document_spec` y las banderas de cruce). Hace **merge por campo**: lo que no
  mandas, no se toca. **Búscala en tu listado antes de empezar.** Si no está, esta
  instalación todavía no puede guardar lo que descubras: dile al usuario y no
  arranques — descubrir sin poder guardar es trabajo que se pierde al cerrar la
  sesión.
- **Documentos**: el histórico del mandante (camino A) o 2–3 guías reales que aporte
  el usuario (camino B). Ver Paso 1.

---

## Paso 0 · Qué mandante es, y por qué camino vas

### El mandante

Igual que en `descubrir-mandante`: lista los mandantes con `get_backlog_settings`
(sin `slug`) y **compara el nombre del usuario contra esa lista**. El slug lo da el
backend — no lo calcules tú.

Trae el mandante con `get_backlog_settings(slug=…)`: el GET ya devuelve el
`document_spec` vigente, la razón social, el RUT y las banderas de cruce.

- **Sin `document_spec`** → es un descubrimiento nuevo.
- **Con `document_spec`** → es un **re-descubrimiento**. Guarda el texto vigente antes
  de tocar nada y trabaja por diff (Paso 7). Las dos razones típicas para llegar acá
  son que el mandante cambió su formulario, o que la primera corrida fue por el
  camino B y ahora sí hay histórico que medir. **El segundo caso no es un arreglo: es
  el segundo escalón previsto.**

### Quién emite el documento

El formato lo pone **quien emite la guía**, y eso lo declara la empresa en
`document_issued_by`; no lo infieras:

- **`mandante`** (cuenta transportista, tipo CCTI) — cada mandante trae su propio
  formulario. Es el caso de esta skill: la spec vive en el mandante.
- **`enterprise`** (la cuenta emite sus propias guías, tipo ABInBev) — el formato es
  uno solo para toda la empresa. Las banderas del mandante no se usan; lo que
  descubras va al nivel de empresa. Si estás acá, dilo antes de seguir.

### El camino

| | cuándo | qué produce |
|---|---|---|
| **A · histórico** *(preferido)* | el mandante ya opera y sus conductores vinieron subiendo guías | la especificación **y las tasas medidas por identificador**, y con eso la propuesta de banderas |
| **B · muestras aportadas** | todavía no hay ningún documento subido | la especificación, con **las banderas apagadas** y la medición pendiente |

Mira cuántas guías con adjunto tiene el mandante en los últimos 30 días. Si hay un
puñado, es camino A. Si no hay ninguna, es B — y **díselo al usuario en voz alta al
empezar**, no al final: *"Este mandante todavía no tiene guías subidas, así que voy a
poder describir el formulario pero no medirlo. Las banderas van a quedar apagadas
hasta que haya con qué medir."*

---

## Paso 1 · Conseguir los documentos

### Camino A · el histórico

Trae las guías **con adjunto** del mandante en la ventana (30 días es un buen punto de
partida), junto con **los datos del viaje que las acompaña**: código, folio digitado
si lo hay, patente, conductor y RUT, cliente, origen y fecha. Esos datos son el otro
lado del cruce del Paso 4.

Trae también el **denominador**: cuántas entregas tuvo el mandante en ese período,
con adjunto y sin adjunto. Lo vas a necesitar en el Paso 4 y **no se puede
reconstruir después**.

### Camino B · muestras aportadas

Pídele al usuario **2–3 guías reales ya emitidas** de ese mandante. Una sola alcanza
para una spec utilizable, pero varias te muestran qué cambia entre documentos —y lo
que cambia entre dos guías es justamente lo que un modelo confunde con una constante.

Si el formato varía (una guía por tipo de destino, o un formulario viejo y uno nuevo
conviviendo), pide una de cada uno y **descríbelos como variantes** en la spec.

---

## Paso 2 · Descubrir la especificación

Manda **un documento** a la tarea de descubrimiento del `/simple-task` de
drivetech-ia-agents, con:

- **Las pistas del usuario en sus palabras.** Pregúntaselas antes: *"¿hay algo que
  sepas de este formulario que me convenga saber? ¿dónde miran ustedes el folio?"*.
  Las pistas **tienen prioridad sobre la lectura del modelo** — el usuario conoce su
  operación y el modelo ve un papel. Si no tiene ninguna, va el centinela
  `Sin instrucciones adicionales.` (el endpoint rechaza el texto vacío).
- El **mandante** y la lista de identificadores que el sistema cruza.

Qué vuelve, y cómo leerlo:

- **`encontrado: false` es información útil, no una falla.** Dice que ese
  identificador **no sirve para este formato**. Escríbelo así en la spec; si lo dejas
  en blanco se lee como que faltó mirar.
- **`dudas`** son las preguntas que el modelo no pudo resolver. **No las contestes tú
  ni las descartes**: pásaselas al usuario, y lo que quede sin respuesta va escrito en
  la spec (Paso 3). Una duda escrita la contesta una persona en diez segundos; un
  supuesto equivocado se descubre meses después.

Con varias muestras (camino B) o varios documentos (camino A), corre sobre 2–3 y
**contrasta**: lo que aparece igual en todos es del formulario; lo que cambia es del
documento. No escribas como regla lo que viste una sola vez.

---

## Paso 3 · Escribir la especificación

El contrato del artefacto —encabezado, orden, qué va en cada parte— está en
**`references/esquema-document-spec.md`**. Léelo antes de escribir. En resumen: se
reconoce el documento, después dónde está cada dato, al final las particularidades
del formulario, y **se tiene que poder leer de corrido sin haber visto el papel**.

Tres cosas que se olvidan siempre:

- **Los rótulos van con las palabras exactas del documento**, entre comillas. *"la
  casilla «Sello Llegada»"* le sirve al operador; *"el campo de sello"* no.
- **Lo que el formulario no tiene, se dice.** *"No tiene tabla de productos: lista
  números de guías bajo el rótulo «Guías»"* evita que después alguien la busque.
- **Lo que la operación no produce, se dice y se explica.** Si el destino acredita con
  timbre y no con firma, escríbelo — pedir firma rechaza entregas correctas. Esa línea
  sola, en un mandante real, valía 44 rechazos falsos.

Muéstrasela al usuario y **hazla confirmar** antes de guardar. Está escrita para que
él la lea: si no la entiende, está mal escrita.

---

## Paso 4 · Medir (solo camino A)

Acá es donde esta skill se gana el nombre. La secuencia completa —qué traer, cómo
normalizar, cómo contar— está en **`references/medicion.md`**. Lo esencial:

1. Por cada guía con adjunto, corre la **tarea de validación** con el centinela
   `Sin instrucciones adicionales.` para que devuelva `checks` vacío: acá se mide
   **extracción**, no criterio de contenido.
2. **Guarda la evidencia cruda** de cada corrida. Sin eso no puedes reprocesar en
   frío cuando cambies un criterio, y vas a cambiarlo — reprocesar cuesta cero,
   volver a llamar se cobra de nuevo.
3. **Normaliza antes de comparar. No es opcional.** Mayúsculas, sin espacios ni
   guiones, RUT sin puntos, fechas parseadas, **ceros a la izquierda descartados**.
   Comparar strings crudos produce rechazos falsos en el primer documento: `PPWR 55`
   contra `PPWR55`, `01-09-2026` contra `2026-09-01`.
4. **Cuenta por identificador**: coincide / contradice / **no participa**. "No
   participa" es cuando **alguno de los dos lados no tiene el dato**, y no cuenta para
   ningún lado. Un cruce que trata la ausencia como contradicción rechaza operaciones
   enteras.

Al reportar las tasas, **la tasa va con su denominador pegado**:

> *"El folio se lee en el 86 % de las guías que llegaron a la base — 371 de 719
> entregas del período tienen documento subido."*

No *"el folio se lee en el 86 %"* a secas. Y **reporta siempre la brecha**, aunque
nadie la pida: las guías del histórico son las que el conductor **logró subir**, así
que la muestra está sesgada hacia el caso fácil y **las tasas son un techo, no un
promedio**. La brecha es ese sesgo, medido. No la corrijas con una estimación
inventada: una tasa honesta con su límite declarado vale más.

Si la brecha **no está repartida pareja** entre conductores, rutas o destinos, eso ya
no es adopción: es que algo específico no se puede subir. Dilo — es un hallazgo
operativo, no ruido.

---

## Paso 5 · Proponer las banderas (solo camino A)

Con los números a la vista, propón **qué identificadores pueden dictaminar**. Solo
estos seis pueden, y cada uno con su bandera:

| identificador | bandera |
|---|---|
| número de documento | `reference_printed_on_document` |
| código de viaje | `code_printed_on_document` |
| cliente / destino | `destination_named_as_in_tms` |
| código de cliente | `client_code_printed_on_document` |
| código de origen | `origin_code_printed_on_document` |
| folio de guía o factura | `bill_printed_on_document` |

**Todo lo demás solo informa.** Y hay dos que **nunca dictaminan, midan lo que
midan**: `patente` y `conductor`. Su desacuerdo **no es un hallazgo ni una anomalía**
— la guía se emite en el origen con el vehículo y el transportista de ese momento, y
la plataforma carga después los reales. Los dos datos son correctos y describen
instantes distintos. Reportarlo como discrepancia es fabricar alarmas sobre el
funcionamiento normal. `fecha` tampoco: el año se lee mal de forma sistemática.

**Ningún identificador participa por defecto.** Propón prender solo los que la
medición sostenga, y di el número al proponerlo: *"el código de viaje coincide 96
veces y contradice 8: lo prendería. El código de origen no apareció en ninguna de las
8 que lo tenían: lo dejaría apagado y no volvería a intentarlo."*

**Y distingue los tres estados**, que no son dos:

| estado | qué significa | qué hacer |
|---|---|---|
| **nunca se midió** | camino B, o identificador que no se evaluó | volver a correr cuando haya histórico |
| **se midió y no da** | la tasa dice que ese dato no sirve en este formulario | **no volver a intentarlo**, y dejar escrito por qué |
| **se midió y da** | la tasa lo sostiene | proponer prenderla |

Los dos primeros se ven iguales desde afuera y piden acciones opuestas. Si no los
separas, el operador re-mide para siempre un identificador que ese mandante
simplemente no imprime.

La decisión de prender es **del usuario**, no tuya. Tú traes la evidencia.

---

## Paso 6 · Golden sample

Antes de dar por descubierto el formato, **valídalo contra guías ya digitadas a
mano** de ese mandante: corre la extracción sobre ellas y compara **campo por campo**
—folio, código de cliente, ítems— contra lo que un humano ya había digitado.

Sin esto, el descubrimiento es una opinión del modelo sobre sí mismo.

Si algo no calza, el que está mal es el mapeo, no el humano: arregla la spec y vuelve
a correr. Y si el desacuerdo es sistemático en un campo (siempre el mismo, siempre
igual), eso no es error de lectura — es que la spec dice que el dato está en un lugar
donde no está.

En el camino B, donde no hay histórico, este paso se hace con las muestras del usuario
y con lo que él pueda confirmar leyendo el papel. Vale menos, y se dice.

---

## Paso 7 · Guardar

**Propón el resultado completo al usuario y hazlo confirmar antes de guardar nada.**

El `document_spec` arranca con su encabezado de evidencia (contrato completo en
`references/esquema-document-spec.md`):

```
> esquema: v1 · evidencia: historico · n: 371 · medido: 2026-09-02 · ventana: 30d
> esquema: v1 · evidencia: muestras · n: 2 · medido: —
```

**Ese encabezado no es decorativo.** La validación documental corre **sin humano al
lado** y lo lee como barrera: con `evidencia: muestras`, ninguna bandera de cruce
aplica aunque esté prendida. No lo escribas de memoria y no lo omitas — sin
encabezado se asume sin evidencia.

Guárdalo con la tool de configuración documental del mandante. **Hace merge por
campo**: lo que no mandas no se toca, así que a diferencia de
`upsert_backlog_mandante` no hay riesgo de borrar lo que no viste. Aun así, en un
re-descubrimiento **trabaja por diff y muéstraselo al usuario en palabras** —qué
cambia y qué queda igual— porque el `document_spec` puede tener correcciones que hizo
el operador a mano y que no salen de ninguna medición.

Guarda también, si los descubriste y faltaban, la **razón social** y el **RUT** del
mandante: son lo que hace que el cruce del destino funcione cuando el papel dice
*"Embotelladora Andina S.A."* y el TMS dice *"Rancagua KOA"*.

---

## Paso 8 · Cierre

**Camino A.** Dile al usuario qué quedó medido, con qué números, cuál es la brecha del
denominador, qué banderas propusiste y cuáles descartaste **para siempre**. Y
recuérdale que las tasas vencen: la próxima corrida compara contra éstas, y **una
caída brusca en un identificador es la señal de que el mandante cambió su
formulario**.

**Camino B.** Dilo derecho, sin adornarlo:

> *"La especificación quedó guardada y sirve para leer el documento. Las banderas
> quedaron apagadas porque con dos muestras no hay con qué medir. Cuando este mandante
> tenga guías subidas, volvé a correr esto para medir y recién ahí decidir qué se
> puede exigir."*

La skill no se queda a medias por accidente: se queda a medias **a propósito y
dicho**.

---

## Reglas de oro

- **Documentos reales, no descripciones.** Y varios, si el formato varía.
- **Describe el papel, no le des instrucciones a un modelo.** Lo corrige un jefe de
  operaciones. Rótulos textuales entre comillas.
- **Prender una bandera se decide con números.** Sin tasa medida, apagadas y dicho.
- **El encabezado de evidencia es una barrera, no un comentario.** Va siempre, con su
  `n` y su fecha.
- **La tasa va con su denominador.** Y la brecha se reporta aunque nadie la pida: las
  guías que están son las que se lograron subir, así que las tasas son un techo.
- **Normaliza antes de comparar.** Sin eso, dos rechazos falsos en el primer documento.
- **Ausencia no es contradicción**, de ninguno de los dos lados.
- **`patente`, `conductor` y `fecha` nunca dictaminan.** Su desacuerdo es el
  funcionamiento normal de la operación, no un hallazgo.
- **Tres estados, no dos:** nunca medido ≠ medido y no sirve.
- **Lo que quedó en duda se escribe** en la spec, con quién lo resuelve. Las reglas
  persisten solas; las dudas se evaporan si no las escribes.
- **El golden sample no es opcional.** Sin él, el descubrimiento es una opinión del
  modelo sobre sí mismo.
- **La spec vive en el mandante** (o en la empresa, si ella emite), nunca en la skill.
