# descubrir-guia-despacho — instrucciones de uso

Skill para **enseñarle al sistema cómo se lee la guía de despacho de un mandante**, y
—cuando ya hay documentos subidos— para **medir qué tan confiable es cada dato
impreso** antes de dejar que el sistema rechace una guía por su cuenta.

Este archivo es para **la persona**. El agente lee `SKILL.md`.

---

## Cuándo usarla

- Un mandante nuevo empieza a operar y hay que enseñarle al sistema a leer su guía.
- Se están **rechazando guías que estaban buenas** y hay que entender por qué.
- El mandante **cambió su formulario**.

Si tu empresa **emite sus propias guías** en vez de recibirlas de quien la contrata,
el formulario es uno solo para todos tus clientes: el agente lo detecta y guarda la
especificación a nivel de tu cuenta, no de un cliente en particular. Te lo va a decir
al guardar.

**No es lo mismo que `descubrir-mandante`.** Esa configura cómo el mandante te **pide
viajes**; ésta, cómo se lee el **papel que firma el que recibe**. Se rehacen en
momentos distintos y no hace falta correr las dos juntas.

## Por qué no se hace al crear el mandante

Porque un mandante recién creado **todavía no tiene guías**. El papel firmado aparece
cuando empieza a operar. Corre esta skill cuando ya tengas guías suyas en la mano.

## Qué hace, y qué todavía no

**Hace: describir el formulario.** Le pasas 2 o 3 guías reales, y el agente escribe
dónde está cada dato, con qué rótulo aparece y qué cosas ese formulario no trae. Con
eso el sistema puede **leer** el documento, que es lo que evita la mayoría de los
rechazos injustos.

**Todavía no hace: medirlo.** Saber si un dato se puede *exigir* —o sea, autorizar al
sistema a rechazar una guía porque no coincide— necesita cruzar cientos de guías ya
subidas contra sus viajes y sacar la tasa de cada dato. Esa pieza está diseñada pero
no construida, así que el agente **deja las validaciones apagadas y te lo dice**.

No es un descuido: autorizar un rechazo automático es autorizar que se le devuelva
trabajo a un transportista. Eso se decide con números, y por ahora no los hay.

## Qué necesitas tener a mano

- El **MCP de Drivetech** conectado, con la empresa correcta.
- **2 o 3 guías reales** de ese mandante, ya emitidas. Si su formato cambió alguna
  vez, una de cada versión.
- Cualquier **pista tuya sobre el formulario**: dónde miran ustedes el folio, qué
  campo se confunde seguido, qué rótulo usa el mandante para el código. Tus pistas
  tienen prioridad sobre lo que lea el sistema — tú conoces la operación.

## Qué te va a preguntar

- Las pistas de arriba.
- Lo que el documento no aclara por sí solo (te lo va a mostrar como preguntas
  concretas, no como dudas vagas).
- Con qué contrastar lo que leyó: el campo donde el conductor teclea el número del
  papel al entregar (el "documento de referencia" de tu formulario de recepción), el
  folio que el viaje ya trae del sistema del mandante, o las cantidades facturadas
  contra la tabla de productos del documento.

## Qué te entrega

- La **especificación del formulario** escrita en lenguaje de operación, para que la
  puedas corregir tú el día que el mandante cambie el papel. Si no la entiendes al
  leerla, está mal escrita: dilo.
- Qué quedó **en duda**, como preguntas concretas que puedas contestar tú o
  preguntarle al mandante.
- Qué datos de ese formulario **valdría la pena medir** el día que se pueda, y cuáles
  claramente no sirven para este mandante.

## Después

Vuelve a correrla cuando el mandante **cambie su formulario**. Y cuando exista la
medición, otra vez: ahí es cuando se puede decidir qué exigirle a ese mandante, con
los números adelante.
