---
name: descubrir-guia-despacho
description: >-
  Descubre cómo se lee la guía de despacho (o formulario de transporte) de un
  mandante y escribe la especificación de su formulario en lenguaje de operación:
  dónde va el folio, el código de cliente, la patente, la tabla de ítems, y qué no
  trae. Trabaja sobre 2-3 guías reales del mandante y las pistas del usuario, valida
  contra guías ya digitadas a mano, y guarda el resultado en el `document_spec` del
  mandante —o de la cuenta, si es ella la que emite sus guías— con set_document_spec,
  que después usa la validación documental automática. Deja las banderas de cruce apagadas y lo dice: autorizar un rechazo
  automático necesita tasas medidas sobre el histórico, que hoy no se pueden calcular
  desde acá. Úsala cuando pidan "descubrir el formato de la guía de X", "documentar
  la guía de despacho", "configurar la validación de documentos de un mandante",
  "por qué se rechazan las guías de X", o cuando un mandante cambie su formulario.
---

# Descubrimiento de la guía de despacho de un mandante

El activo que produces es el **`document_spec` del mandante**: la especificación de
cómo se lee su formulario. La validación documental automática recibe ese texto en su
contexto y **manda sobre su criterio genérico**.

Es una skill **hermana de `descubrir-mandante`, no un paso suyo.** Un mandante recién
configurado todavía no tiene guías: el papel firmado aparece cuando empieza a operar.
Y las dos se rehacen en momentos distintos — aquélla cuando el mandante cambia **cómo
pide viajes**, ésta cuando cambia **su formulario**.

## Qué hace hoy, y qué no

**Hace: describir el formulario.** Sobre 2–3 guías reales, escribe dónde está cada
dato, con qué rótulo y qué no trae. Eso alcanza para que la validación **lea** el
documento, y es lo que evita la mayoría de los rechazos injustos.

**No hace: medirlo.** Saber *con qué frecuencia* un dato aparece impreso y *si
coincide* con lo que el sistema tiene exige cruzar el histórico de guías del mandante
contra sus viajes — cientos de documentos, en lote. **Esa capacidad todavía no existe
del lado de la plataforma** (ver *La medición* al final). Así que esta skill termina
con las **banderas de cruce apagadas**, y **lo dice**.

No es una limitación que convenga disimular: es la misma disciplina que la skill le
pide al usuario. Prender una bandera autoriza a **rechazarle una guía a un
transportista**. Eso se decide con números, y hoy no los hay.

## Las tres reglas de oro

**1 · Documentos reales, nunca la descripción de memoria.** Igual que en el
descubrimiento del mandante: pide el papel de verdad y míralo tú. Si el formato varía,
pide uno de cada variante.

**2 · Describe el papel, no le des instrucciones a un modelo.** La especificación la
va a **corregir un jefe de operaciones** el día que el mandante cambie su formulario,
no un programador ni alguien que sepa de prompts.

> **Bien:** *"El folio va en el recuadro superior derecho, rotulado «N° documento
> Transporte»."*
> **Mal:** *"Extraer el campo numero_documento del sector superior derecho."*

Si lo escribes en el segundo estilo, lo único que puede mantenerlo es quien sepa
escribir prompts — y ese es exactamente el problema que esta skill viene a resolver.

**3 · Sin tasa medida, las banderas quedan apagadas.** Con dos muestras se ve que un
dato *aparece*; no con qué frecuencia ni si coincide. La spec se guarda igual y sirve;
las banderas quedan en cero **a propósito y dicho**, no por accidente.

## Requisitos de conexión

- **MCP de Drivetech** conectado, con la empresa correcta. Si el token ve varias
  empresas, confírmala al empezar (`get_current_enterprise_name`; si no es la
  esperada, `select_enterprise`) — la selección se vence sola y el error que aparece
  después dice *"la empresa no tiene contratado el módulo de tms"*, que parece un
  problema de permisos y no lo es.
- **`set_document_spec`** — la tool que guarda. Si no está en tu listado, esta
  instalación no puede guardar lo que descubras: dile al usuario y no arranques.
  Descubrir sin poder guardar es trabajo que se pierde al cerrar la sesión.
- **2–3 guías reales** del mandante, ya emitidas. Las aporta el usuario.

---

## Paso 0 · Qué mandante es, y quién emite el documento

### El mandante

Igual que en `descubrir-mandante`: lista los mandantes con `get_backlog_settings`
(sin `slug`) y **compara el nombre del usuario contra esa lista**. El slug lo da el
backend — no lo calcules tú.

Trae el mandante con `get_backlog_settings(slug=…)`: el GET ya devuelve el
`document_spec` vigente, la razón social, el RUT y las banderas de cruce.

- **Sin `document_spec`** → es un descubrimiento nuevo.
- **Con `document_spec`** → es un **re-descubrimiento**. Guarda el texto vigente antes
  de tocar nada y trabaja por diff (Paso 5). Puede tener correcciones que hizo el
  operador a mano, que no salen de ningún descubrimiento y no se pisan.

### Quién emite el documento, y dónde va la spec

El formato lo pone **quien emite la guía**, y eso define **dos niveles excluyentes**:

- **La cuenta es transportista** (`document_issued_by: mandante`) — cada cliente que
  la contrata trae su propio formulario. La spec va **en el mandante**: se guarda
  **con `slug`**.
- **La cuenta emite sus propias guías** (`document_issued_by: enterprise`) — el
  formato es **uno solo para todos sus clientes**. La spec va **en la cuenta**: se
  guarda **sin `slug`**. Ojo con el encuadre: acá no estás descubriendo el formulario
  *de un mandante*, sino **el de la cuenta**, aunque hayas llegado mirando la guía de
  un destino puntual. Dilo así, o el usuario va a creer que configuró un cliente.

**No lo adivines ni se lo preguntes al usuario.** Mira `document_issued_by` para saber
qué esperar — y déjalo ahí: **la autoridad es la tool**. `set_document_spec` rechaza el
nivel que no corresponde, y el mensaje del rechazo dice cuál es el de esta cuenta. El
flujo correcto es **intentar y leer el rechazo**, no razonar por adelantado.

Un rechazo de ese tipo **no es un error tuyo ni una falla de la skill**: es la
respuesta a la pregunta. Corrige el nivel y vuelve a llamar.

---

## Paso 1 · Conseguir las guías y las pistas

Pídele al usuario **2–3 guías reales ya emitidas** de ese mandante. Una sola alcanza
para una spec utilizable, pero varias te muestran qué cambia entre documentos — y lo
que cambia entre dos guías es justamente lo que se confunde con una constante.

Si el formato varía (un formulario por tipo de destino, o uno viejo y uno nuevo
conviviendo), pide uno de cada uno y **descríbelos como variantes**.

**Y pídele las pistas antes de mirar**: *"¿hay algo que sepas de este formulario que
me convenga saber? ¿dónde miran ustedes el folio? ¿qué campo se confunde seguido?"*.

Las pistas del usuario **tienen prioridad sobre tu lectura**: él conoce su operación y
tú ves un papel. Úsalas para orientarte y **confírmalas contra el documento**. Si una
pista **no coincide** con lo que ves, no elijas: dilo como duda y muestra las dos
lecturas.

---

## Paso 2 · Leer el documento

**Míralo tú.** Tienes visión, y además puedes lo que un extractor no puede:
repreguntar, volver a mirar y corregir con lo que el usuario te aclare.

**Las reglas de lectura no se improvisan.** Están en
`references/esquema-document-spec.md`, y son **espejo del contrato de la tarea de
descubrimiento de la plataforma** — la que corre en el front cuando no hay un agente
del otro lado. Las dos superficies tienen que producir **el mismo artefacto**: si
derivan, la spec que sale del front y la que sale de acá dejan de ser lo mismo y nadie
se entera. Léelas antes de escribir; no escribas tu propia versión.

Lo que más se olvida:

- **Trabaja solo sobre lo que ves.** No supongas que otros documentos del mismo
  mandante traen campos que éste no trae, ni que los traen en el mismo lugar.
- **Un identificador que no aparece es información útil, no una falla.** Significa que
  ese dato **no sirve para este formato**. Escríbelo; en blanco se lee como que faltó
  mirar.
- **Nunca inventes** un rótulo, un ejemplo ni una ubicación. Lo cortado, borroso o
  tapado es **duda**, y la duda se escribe como pregunta concreta.

Con varias muestras, **contrasta**: lo que aparece igual en todas es del formulario;
lo que cambia es del documento. No escribas como regla lo que viste una sola vez.

### La trampa que más se cobra: la estructura repetida (regla 7)

Un formulario con cuatro columnas de "Destinatario" **parece** admitir cuatro destinos.
En la práctica puede que las cuatro sean **la misma tienda** — grupos de guías de una
sola entrega. Desde un documento eso **no se puede saber**.

La regla dice **buscar primero un contador impreso** —*"Tiendas a visitar: 00001"*,
*"Bultos: 3"*— porque un formulario que repite una estructura suele decir en algún lado
cuántas veces la usa de verdad. Si está, la duda tiene respuesta en el papel.

Si no está, la regla dice escribirlo como **duda**, nunca como regla del formulario. Y
ahí tienes una ventaja que el descubridor del front no tiene: **puedes preguntar**.
Úsala — *"¿son cuatro tiendas distintas, o siempre la misma con varias guías?"*— y
escribe la respuesta. Si el usuario tampoco la sabe, entonces sí queda como duda
abierta.

Lo que no puedes hacer es resolverla por tu cuenta: una repetición escrita como regla
hace leer mal todos los documentos que vengan después.

### Preguntar puede cambiar la regla, no solo confirmarla

No des por buena la regla que viste en las muestras solo porque el usuario no te
contradijo. Preguntá aunque tu lectura parezca clara — y sobre todo **cuando parezca
clara**.

Caso real: tres de tres documentos traían **una sola tienda**, y la regla escrita
habría sido *"siempre una tienda por documento"*. El usuario contestó otra cosa: *"no
sé, pero al menos una debe coincidir"* — más floja y **más correcta**. La regla medida
habría rechazado guías multi-tienda válidas.

Lo que ves en pocas muestras te da **la regla más estrecha que las explica**, no la
regla real. La distancia entre esas dos es exactamente lo que se rechaza mal después.
Y esa distancia no se cierra mirando más papeles: se cierra preguntando.

---

## Paso 3 · Escribir la especificación

El contrato del artefacto —encabezado, orden, qué va en cada parte— está en
`references/esquema-document-spec.md`. En resumen: **cómo se reconoce el documento →
dónde está cada dato → particularidades del formulario → dudas abiertas**, y se tiene
que poder **leer de corrido sin haber visto el papel**.

Tres cosas que se olvidan siempre:

- **Los rótulos van con las palabras exactas del documento**, entre comillas. *"la
  casilla «Sello Llegada»"* le sirve al operador; *"el campo de sello"* no.
- **Lo que el formulario no tiene, se dice.** *"No tiene tabla de productos: lista
  números de guías bajo el rótulo «Guías»"* evita que después alguien la busque.
- **Lo que la operación no produce, se dice y se explica.** Si el destino acredita con
  timbre y no con firma, escríbelo — pedir firma rechaza entregas correctas. Esa línea
  sola, en un mandante real, valía 44 rechazos falsos.

Muéstrasela al usuario y **hazla confirmar**. Está escrita para que él la lea: si no
la entiende, está mal escrita.

---

## Paso 4 · Golden sample

Antes de dar por descubierto el formato, **contrasta tu lectura contra un dato que una
persona sacó de ese mismo papel**. Sin esto, el descubrimiento es una opinión del
modelo sobre sí mismo.

### Cuál es el dato, porque casi nada está digitado a mano

Cuidado con esto: **el destino, el código de cliente y la patente no los digita
nadie** — los pone el sistema al crear el viaje. Compararlos contra el papel no es un
golden sample: **es el cruce de validación**, justamente lo que esta skill todavía no
puede medir. Si haces eso creyendo que validaste la lectura, no validaste nada.

Lo que **sí** escribió una persona leyendo el documento son dos cosas, y hay que ir a
buscarlas:

1. **El campo de referencia del formulario de recepción** — el que la empresa configuró
   para que el conductor teclee el número que ve en el papel (en una operación real se
   llama *"Doc. de Referencia"*). Ése es el golden sample de verdad: un humano leyó ese
   número **del mismo documento** y lo escribió.
2. **El folio de guía o factura que el viaje trae del ERP del mandante**, cuando está
   poblado. En un mandante real venía en 2.146 de 2.185 entregas.

Busca esos dos **antes de darte por vencido**. El paso parece imposible si lo lees como
"comparar todo contra lo digitado", y es perfectamente posible si sabes que lo que se
contrasta es, casi siempre, **un campo**.

### Qué hacer con el resultado

Si no calza, el que está mal es tu lectura, no el humano: corrige la spec y vuelve a
mirar. Y si el desacuerdo es **sistemático** (siempre el mismo campo, siempre igual),
eso no es error de lectura — es que la spec dice que el dato está donde no está.

Si el mandante **no tiene ninguno de los dos**, entonces sí: el golden sample no se
puede hacer. **Dilo** — quedó sin hacer y la spec vale menos. No lo omitas en
silencio.

---

## Paso 5 · Guardar

**Propón el resultado completo al usuario y hazlo confirmar antes de guardar nada.**

El `document_spec` arranca con su encabezado de evidencia (contrato completo en
`references/esquema-document-spec.md`):

```
> esquema: v1 · evidencia: muestras · n: 3 · medido: —
```

**Ese encabezado no es decorativo.** La validación documental corre **sin humano al
lado** y lo lee como barrera: con `evidencia: muestras`, **ninguna bandera de cruce
aplica** aunque esté prendida. No lo escribas de memoria y no lo omitas — sin
encabezado se asume sin evidencia.

Guarda con **`set_document_spec`**, en el nivel que corresponda (Paso 0):

- **Con `slug`** — la spec es de ese mandante.
- **Sin `slug`** — la spec es de la cuenta, porque es ella la que emite. En este caso
  **no va identidad**: `business_name` y `rut` son de un mandante, y una cuenta se
  conoce a sí misma.

Si te equivocaste de nivel, la tool rechaza y el mensaje dice cuál corresponde:
corrige y vuelve a llamar.

**La identidad siempre pasa.** La razón social y el RUT de un mandante se pueden
escribir en los dos tipos de cuenta — lo que cambia de nivel es el **formato**, no la
identidad. Guárdalos si los descubriste y faltaban: son lo que hace que el cruce del
destino funcione cuando el papel dice *"Embotelladora Andina S.A."* y el TMS dice
*"Rancagua KOA"*.

**Hace merge por campo:** lo que no mandas no se toca, así que —a diferencia de
`upsert_backlog_mandante`— no hay riesgo de borrar lo que no viste. Un `false`
explícito en una bandera **sí** se escribe: apagar un cruce es una decisión, no una
omisión.

**Sin `slug` hay control de versión.** Si alguien tocó la configuración de la cuenta
mientras preparabas la tuya, la tool devuelve `resultado: "conflicto"` con lo vigente.
**No reintentes**: un reintento a ciegas es exactamente el pisotón que la versión
existe para evitar. Lee lo que volvió, mira si tu cambio sigue teniendo sentido sobre
esa base, y decide — o cuéntaselo al usuario. Recién ahí volvés a llamar.

**Si la puerta de cuenta responde 404**, no concluyas que el nivel está mal: hoy
producción puede estar corriendo una imagen anterior a ese endpoint. Díselo al usuario
tal cual —la spec quedó sin guardar por una versión del servidor, no por lo que
descubriste— y **no busques otra forma de escribirla**.

**No prendas banderas.** Si el usuario te pide prender alguna igual, adviértele: la
tool devuelve una advertencia cuando se prenden banderas sobre una spec que no dice
`evidencia: historico`, porque **la política no las va a aplicar**. Pasásela tal cual;
no lo dejes creyendo que quedaron activas.

En un re-descubrimiento, **muéstrale el diff en palabras** antes de guardar —qué
cambia y qué queda igual— y dile en qué quedó.

---

## Paso 6 · Cierre

Dilo derecho, sin adornarlo:

> *"La especificación quedó guardada y sirve para que el sistema lea el documento. Las
> banderas de cruce quedaron apagadas: con tres guías se ve que un dato aparece, no
> con qué frecuencia coincide con lo que tenemos, y eso es lo que haría falta para
> autorizar un rechazo automático."*

Y déjale dicho **qué habría que medir** en este mandante para poder exigir algo —
cuáles identificadores se ven prometedores en el papel y cuáles claramente no están.
Eso es lo que va a orientar la medición el día que se pueda correr.

**Y decile cómo se va a enterar de que hay que rehacer esto.** No hace falta que lo
vigile: cuando la validación lee un documento con esta spec y el dato no está donde
ella dice, **lo reporta como desajuste**. Un desajuste suelto es ruido; varios seguidos
en el mismo campo son la señal de que el mandante cambió su formulario. Ahí se vuelve
a correr esta skill.

La skill no se queda a medias por accidente: se queda a medias **a propósito y dicho**.

---

## La medición — el escalón siguiente

Lo que falta para poder prender una bandera es **cruzar el histórico de guías del
mandante contra sus viajes** y sacar, por identificador, en cuántas apareció y en
cuántas coincidió.

**Hoy no se puede correr desde acá, y no conviene fingir que sí:**

- No hay tool que traiga las guías **con su adjunto** y los datos del viaje que las
  acompaña: `get_trip_status` y `get_tms_dispatches_by_status` devuelven el viaje pero
  no `custom_form_values`, que es donde está la ruta del documento.
- Y aunque la hubiera, correr la extracción sobre cientos de documentos y cruzarlos es
  **trabajo por lotes**, no algo que un agente haga en una conversación.

Lo que corresponde es una **tool que corra la medición del lado del servidor y
devuelva las tasas**. Cuando exista, esta skill gana un paso: pedir la medición,
interpretarla y proponer banderas con su evidencia.

**`references/medicion.md` ya tiene esa mitad escrita** — la secuencia, la
normalización obligatoria, los tres resultados del cruce, el sesgo del denominador y
cómo se leen las tasas. Está ahí porque el criterio no cambia cuando cambie quién lo
ejecuta, y porque es la especificación de lo que esa capacidad tiene que devolver.

Si el usuario pregunta por qué las banderas no se pueden prender, **muéstrale eso**:
la respuesta no es "no se puede", es "falta esta pieza y así se vería cuando esté".

---

## Reglas de oro

- **Documentos reales, no descripciones.** Y varios, si el formato varía.
- **Las pistas del usuario tienen prioridad sobre tu lectura**, pero se confirman
  contra el papel. Si no coinciden, es duda: no elijas.
- **Describe el papel, no le des instrucciones a un modelo.** Lo corrige un jefe de
  operaciones. Rótulos textuales entre comillas.
- **Las reglas de lectura son espejo, no tuyas.** Están en `references/`; si cambian,
  cambian en el contrato de la plataforma primero. Dos superficies, un artefacto.
- **Un identificador que no aparece es información**, no un campo que faltó llenar.
- **Nunca inventes** un rótulo, un ejemplo ni una ubicación. Lo dudoso es duda.
- **Lo que la operación no produce, se dice y se explica.** Ahí se evitan los rechazos
  injustos.
- **El encabezado de evidencia es una barrera, no un comentario.** Va siempre.
- **Las banderas quedan apagadas y se dice.** Prenderlas exige tasas medidas, no una
  observación sobre tres papeles.
- **El golden sample se contrasta contra lo que digitó una persona** —el campo de
  referencia del formulario, el folio del ERP—, no contra lo que puso el sistema. Eso
  último es el cruce de validación, no una verificación de tu lectura.
- **Una estructura repetida en el papel no significa que la operación la use.** Es
  duda, no regla.
- **El golden sample no es opcional**, y si no se pudo hacer, se dice.
- **Lo que quedó en duda se escribe** en la spec, con quién lo resuelve. Las reglas
  persisten solas; las dudas se evaporan si no las escribes.
- **El nivel lo dicta la tool, no tu razonamiento.** Intenta y lee el rechazo: te dice
  cuál corresponde. Un rechazo de nivel no es una falla de la skill.
- **Sin `slug` no va identidad**, y un `conflicto` no se reintenta: se relee y se
  decide.
- **La spec vive en el mandante** (o en la cuenta, si ella emite), nunca en la skill.
