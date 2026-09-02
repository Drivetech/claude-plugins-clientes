# descubrir-guia-despacho — instrucciones de uso

Skill para **enseñarle al sistema cómo se lee la guía de despacho de un mandante**, y
—cuando ya hay documentos subidos— para **medir qué tan confiable es cada dato
impreso** antes de dejar que el sistema rechace una guía por su cuenta.

Este archivo es para **la persona**. El agente lee `SKILL.md`.

---

## Cuándo usarla

- Un mandante empezó a operar y sus conductores ya subieron guías: es el momento de
  descubrir su formulario y medirlo.
- Se están **rechazando guías que estaban buenas** y hay que entender por qué.
- El mandante **cambió su formulario**.
- Ya corriste esto antes sin histórico, y ahora sí hay documentos para medir.

**No es lo mismo que `descubrir-mandante`.** Esa configura cómo el mandante te **pide
viajes**; ésta, cómo se lee el **papel que firma el que recibe**. Se rehacen en
momentos distintos y no hace falta correr las dos juntas.

## Por qué no se hace al crear el mandante

Porque un mandante recién creado **todavía no tiene guías**. El papel firmado aparece
cuando empieza a operar. Corre esta skill después, cuando ya haya documentos subidos —
ahí es cuando sirve de verdad.

## Los dos caminos, y por qué no valen lo mismo

**Con histórico** (lo que conviene). El agente toma las guías que tus conductores ya
subieron, las cruza contra los viajes que las acompañan y te dice, con números, en
cuántas apareció cada dato y en cuántas coincidió. Con eso te propone **qué se le
puede exigir a ese mandante**.

**Sin histórico** (cuando todavía no hay nada). Le pasas 2 o 3 guías reales y el
agente describe el formulario igual. Sirve para leerlo — **pero no para exigir nada**:
con dos papeles se ve que un dato aparece, no con qué frecuencia. En ese caso las
validaciones quedan **apagadas a propósito**, y el agente te lo dice al terminar, para
que vuelvas a correr esto cuando haya guías.

Esa diferencia es deliberada: autorizar un rechazo automático es autorizar que se le
devuelva trabajo a un transportista. Eso se decide con números.

## Qué necesitas tener a mano

- El **MCP de Drivetech** conectado, con la empresa correcta.
- Si el mandante todavía no tiene guías subidas: **2 o 3 guías reales suyas**, ya
  emitidas. Si su formato cambió alguna vez, una de cada versión.
- Cualquier **pista tuya sobre el formulario**: dónde miran ustedes el folio, qué
  campo se confunde seguido, qué rótulo usa el mandante para el código. Tus pistas
  tienen prioridad sobre lo que lea el sistema — tú conoces la operación.

## Qué te va a preguntar

- Las pistas de arriba.
- Lo que el documento no aclara por sí solo (te lo va a mostrar como preguntas
  concretas, no como dudas vagas).
- Qué validaciones prender, **con el número de cada una a la vista**. La decisión es
  tuya; el agente trae la evidencia.

## Qué te entrega

- La **especificación del formulario** escrita en lenguaje de operación, para que la
  puedas corregir tú el día que el mandante cambie el papel. Si no la entiendes al
  leerla, está mal escrita: dilo.
- Si hubo histórico: **las tasas de cada dato**, la brecha entre entregas y documentos
  subidos, y la propuesta de qué exigir.

## Un número que conviene mirar

El agente siempre te va a decir **cuántas de tus entregas tienen documento subido**.
No es un detalle: todas las tasas están calculadas sobre esas, así que si la mitad de
las entregas no tiene guía subida, los porcentajes describen la mitad buena. Si ese
número empeora con el tiempo, algo se rompió antes del papel.

## Después

Vuelve a correrla cuando el mandante cambie su formulario. La segunda corrida compara
contra la anterior, y una caída fuerte en algún dato suele ser justamente eso: el
formulario cambió y nadie avisó.
