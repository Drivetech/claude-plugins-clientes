# Auditar la configuración de la cuenta

Es el capítulo que más se puede accionar: son cambios que se hacen en la plataforma, sin
comprar nada ni cambiar la operación.

`get_operation_diagnostics(section="configuracion")` trae las banderas de la cuenta
**y su uso real**. Esa segunda mitad es la que hace interpretable a la primera.

> **Una bandera configurada no dice nada. Una bandera con su uso al lado dice algo.**

## La forma de cada hallazgo

Siempre las cuatro partes, y la última es la que casi nunca se escribe:

> **Evidencia** → **consecuencia** → **qué se cambia** → **qué rompe**

Un informe que solo propone mejoras es una lista de deseos. Uno que dice qué se rompe
es una decisión.

## Qué revisar

**Geocercas faltantes o malas.** Sale del capítulo 1. Un origen sin geocerca no produce
hitos nunca; uno con rebotes tiene el polígono cortando el patio. *Qué rompe:* agrandar
una geocerca hace que los viajes arranquen antes, así que **las permanencias dejan de
ser comparables con los meses anteriores**.

**Restricciones que bloquean casi todo.** Una restricción que frenó el 90 % de los
intentos admite **dos lecturas opuestas**: está mal configurada, o hay un problema real
de fondo que está haciendo bien en frenar. **Distinguirlas es tu trabajo, no el de la
tool** — mira qué se intentó y qué pasó después de cada bloqueo. Y dilo con esa
ambigüedad si no puedes resolverla: una restricción mal desactivada abre justo lo que
protegía.

**Banderas que tapan un problema crónico.** Una bandera que permite cargar fuera de
hora es útil como excepción y es un problema como norma: si se usa en la mayoría de los
viajes, ya no está absorbiendo excepciones, está **escondiendo un atraso estructural**
y desactivando la señal que lo mostraría. *Qué rompe:* apagarla va a hacer aparecer de
golpe un montón de rechazos que hoy pasan — que es el punto, pero hay que avisarlo
antes y no después.

**Características exigidas que la flota no cumple.** Si un tipo de viaje exige una
característica que **ninguna parte de la flota tiene**, esos viajes no se pueden
asignar y alguien los está resolviendo a mano todos los días. Es de los hallazgos más
baratos de arreglar.

**Catálogo con clientes muertos.** En una cuenta real medida: **72 clientes cargados y
33 con viajes** en 60 días. Los 39 restantes ensucian el autocompletado y son
candidatos a que una carga resuelva un nombre contra **el destino equivocado** — que no
es un problema estético, es un viaje mal dirigido. *Qué rompe:* desactivar un cliente
que vuelve en temporada obliga a recrearlo; propón revisar, no borrar en bloque.

**Campos obligatorios del formulario que nadie llena.** Un campo obligatorio vacío en la
mayoría de las entregas significa que la operación encontró cómo saltárselo, o que pide
algo que en terreno no existe. Las dos cosas se arreglan, y ninguna se arregla
insistiendo.

**Formularios sin campo de referencia.** Si el formulario de recepción solo tiene el
adjunto y **ningún campo donde el conductor teclee el número del papel**, la validación
documental **no tiene contra qué cruzar** — y además el descubrimiento de la guía se
queda sin su golden sample. Agregar un campo de referencia es un cambio chico con
efecto en dos features.

**Nombres duplicados.** Un conductor, cliente u origen que aparece con dos grafías es un
hallazgo de este capítulo. **No lo unifiques tú**: repórtalo, porque unificarlo en
silencio en el informe esconde el problema que hay que arreglar en la base.

## Lo que no se hace desde acá

**No apliques ningún cambio.** Este capítulo **propone**. La skill no toca geocercas, no
apaga banderas y no desactiva clientes. Cada propuesta va con su evidencia y su costo,
y la decisión es de quien opera la cuenta.

Y si un hallazgo depende de un dato que la sección no trajo, **dilo como pendiente**.
Un capítulo de configuración con un hueco declarado sigue siendo útil; uno que rellena
el hueco con una suposición hace perder la confianza en los otros seis hallazgos.
