---
name: analizar-operacion
description: >-
  Análisis experto de la operación de transporte de una empresa sobre un período:
  revisa primero si el instrumento de medición es confiable (cobertura de hitos y
  salud de las geocercas), después mide los tiempos reales de origen, ruta y destino,
  las vueltas por vehículo y el desempeño por conductor, marca lo que se desvía
  contra la calibración de ESA empresa, y termina proponiendo qué cambiar —incluida
  la configuración de la plataforma y las geocercas— con su evidencia, su efecto
  esperado y qué rompe cada cambio. La primera corrida calibra: mide la distribución
  real y le pregunta al usuario qué es normal en su operación, y eso queda guardado.
  Úsala cuando pidan "analizar la operación", "cómo viene la flota", "informe de
  gestión", "dónde estamos perdiendo tiempo", "revisar los tiempos de carga",
  "desempeño de los conductores", "auditar las geocercas" o "qué conviene cambiar".
---

# Análisis de la operación

`seguimiento-operacion` dice **qué está pasando hoy**. Esta skill dice **qué
significa** y **qué conviene cambiar**.

Es la primera skill del plugin cuyo producto es una **interpretación**, no una
configuración ni una acción. Eso la pone entera del lado peligroso de una línea que
conviene tener presente todo el tiempo:

> **Un dato bien medido no autoriza su interpretación.** Que la permanencia promedio
> en origen sea 1:47 es un hecho. Que eso sea "malo", que se deba a la operación, o
> que se arregle moviendo una geocerca, son tres afirmaciones distintas y ninguna
> viene con el número.

Actúas como **experto en logística y transporte**, y el informe tiene que servir para
**decidir**. Pero un análisis que afirma de más no es más útil: es más difícil de
creer, y la primera cifra dudosa se lleva puesto al resto.

## Los cuatro capítulos, y por qué en ese orden

| | capítulo | pregunta |
|---|---|---|
| **1** | El instrumento | ¿Los datos con que voy a medir son confiables? |
| **2** | La operación | ¿Qué está pasando, con qué denominador? |
| **3** | Lo que se desvía | ¿Qué se sale de lo normal **en esta empresa**? |
| **4** | Qué se puede hacer | ¿Qué cambio, con qué efecto, y qué rompe? |

**El orden no es estético: cada uno condiciona al siguiente.** Si el capítulo 1 dice
que una de cada cuatro entregas no tiene hitos completos, el capítulo 2 no puede
presentar promedios como si describieran la operación — describen la parte de la
operación que la geocerca alcanzó a ver. Saltarse el 1 y arrancar por los promedios es
el error que hace que todo el informe sea elegante y esté mal.

## La tool computa, tú interpretas

**No pidas datos crudos para calcular promedios.** `get_operation_diagnostics` devuelve
**distribuciones ya calculadas, cada una con su denominador**; tu trabajo empieza
después: decir qué significan, qué se sale de lo normal en esta empresa y qué conviene
cambiar.

Hacer aritmética sobre mil y pico de viajes dentro del modelo es el peor lugar posible
para hacerla: caro, y con el error escondido en un paso que nadie revisa. Si en algún
punto te ves escribiendo *"sumo las permanencias y divido"*, **no lo hagas**: falta una
sección en la tool y eso se reporta, no se improvisa.

### `como_leerlo` se lee antes de interpretar

Cada respuesta trae, además de `datos`, un campo **`como_leerlo`**: una advertencia
escrita para esa sección, puesta ahí precisamente para que **no saques la conclusión
fácil**. No es relleno ni un disclaimer legal — es la parte del contrato que sabe algo
sobre esos números que tú no puedes ver mirándolos.

**Léelo antes de escribir una sola línea del capítulo**, y si contradice tu lectura,
gana él. Si lo que dice cambia lo que ibas a afirmar, eso ya es material del informe.

Dos consecuencias más que valen como regla:

- **Los nombres los pone la tool.** Conductores, geocercas, clientes, orígenes: tal
  cual vienen. No los normalices ni los unifiques. Si un conductor aparece con dos
  grafías, **eso es un hallazgo del capítulo 4**, no algo que arregles en silencio.
- **El `n` viaja siempre.** Va en el texto y en el informe, junto al número — no en una
  nota al pie. Un número sin denominador deja de ser defendible en la primera pregunta
  que le hagan.

## Requisitos de conexión

- **MCP de Drivetech** conectado, con la empresa correcta. Si el token ve varias
  empresas, confírmala al empezar (`get_current_enterprise_name`; si no es la
  esperada, `select_enterprise`) — se vence sola, y el error posterior dice *"la
  empresa no tiene contratado el módulo de tms"*, que parece un problema de permisos y
  no lo es.
- **`get_operation_diagnostics`** — la tool que trae el diagnóstico. Una sección por
  capítulo (`section`: `instrumento`, `operacion`, `conductores`, `configuracion`), con
  `start_date` y `end_date` opcionales (sin fechas: últimos 60 días), `group_name` para
  acotar a la faena de un mandante, `origin`, y `min_trips` (por defecto 5) para el
  corte de la ficha por conductor.
- **El período**. Si el usuario no lo dice, propón 60 días y confirma: menos que eso
  deja los denominadores demasiado chicos para hablar de un conductor o una geocerca.
- **La calibración de esta empresa** (Paso 1). Sin ella no puedes escribir el capítulo
  3, porque no sabrías contra qué.

---

## Paso 0 · Contexto antes de medir

1. **La config de la empresa y los perfiles**, con `get_backlog_settings`. De ahí sale
   la plantilla de reporte (`extra.reporte_tipo`) —que define **el formato y la marca**
   del informe— y, si ya se corrió antes, la **calibración**.
2. **De quién es el análisis.** Puede ser de toda la operación o de un mandante. Si es
   de uno, lee su `spec_md`: ahí están sus particularidades y los ajustes que hace
   distinto (sección "Reporte de status: ajustes"). Un origen donde los camiones
   pernoctan cambia por completo cómo se lee la permanencia.
3. **¿Hay calibración?** Si no la hay, la primera corrida **no es un informe**: es el
   Paso 1.

---

## Paso 1 · Capítulo 1 · El instrumento

**Antes de leer la medición, revisa el aparato.**

Los hitos de origen y destino los produce el **paso por una geocerca**. Si el polígono
es chico, está mal centrado, o el camión estaciona afuera del patio, el hito no se
registra — y ese viaje desaparece de todos los promedios.

Pide `get_operation_diagnostics(section="instrumento")`. Trae el `total` de la
operación —los cinco conteos de hitos y los **orígenes invertidos**— más `origenes` y
`destinos`, cada uno con viajes, `con_llegada`, `con_salida` y `entra_y_no_sale`. Lo que
sale de ahí va **al principio del informe**, no en un anexo:

- **Cobertura de hitos**: de los viajes del período, qué porcentaje tiene los cuatro
  hitos completos. En operaciones reales medidas, esa cifra va de **76 % a 85 %** —
  o sea que entre una de cada cuatro y una de cada siete entregas no se puede medir
  completa.
- **Por geocerca**: qué porcentaje produjo entrada **y** salida, cuántas entradas
  quedaron sin salida, y los **rebotes** — entra, sale y vuelve a entrar en pocos
  minutos. El rebote es el síntoma clásico de un polígono que **corta el patio por la
  mitad**: el camión no se fue, cruzó el borde.
- **Orígenes y destinos sin geocerca.** Ésos no producen hitos **nunca**, así que no
  son un porcentaje bajo: son un agujero completo, y todo viaje que pase por ahí queda
  fuera de la medición. Van listados aparte de los que miden mal.
- **Orígenes fuera de catálogo** (`fuera_de_catalogo`). Un origen que aparece en los
  viajes pero no está en el catálogo no tiene geocerca ni la va a tener, y además
  delata que se está escribiendo a mano algo que debería elegirse de una lista.
- **Origen invertido** (`origen_invertido`). Viajes donde origen y destino parecen
  estar al revés. No lo presentes como un error de la geocerca: es un dato mal
  cargado, y lo que hay que revisar es de dónde salió esa carga.

### ¿Fue el mismo instrumento todo el período?

El capítulo 1 no pregunta solo *"¿el instrumento es confiable?"*, sino **"¿fue el mismo
instrumento de principio a fin?"**.

Si el período pasa de unas pocas semanas, **pide la serie**: `bucket="semana"` (o
`"mes"`) en `instrumento` y en `operacion`. Devuelve la evolución por período, más un
`por_que_la_serie` que explica para qué mirarla.

**Busca un escalón, no una tendencia.** Un caso real, cobertura de los cuatro hitos por
semana:

```
62% · 70% · 65% · 65% · 59%   →   95% · 97% · 95% · 91%
```

Eso no es una operación que mejoró: es **un cambio de plataforma con fecha**. El
promedio del período —78 %— es el promedio de un sistema roto y uno sano, **y no
describe a ninguna de las dos mitades**.

Cuando encuentres un escalón:

1. **Dilo, con la fecha.** Y pregúntale al usuario qué pasó ahí: un despliegue, un
   cambio de equipos, una geocerca redibujada. Él lo sabe y tú no.
2. **Analiza el tramo posterior**, no el período completo. Promediar encima de un
   quiebre produce un número que no le pasó a nadie.
3. **No mandes a arreglar lo que ya se arregló.** Sin este corte, un informe honesto
   manda al cliente a redibujar geocercas sanas por un problema que se resolvió hace un
   mes.

La regla general, que vale más allá de las geocercas: **un período que contiene un
cambio de plataforma no es comparable consigo mismo**, y cualquier tendencia calculada
encima mide el despliegue, no la operación.

Y la consecuencia, escrita explícita en el informe:

> **Los viajes que no se pudieron medir no son un dato faltante repartido al azar.**
> Son sistemáticamente los que la geocerca no alcanzó a ver, y hay razones para
> pensar que son los raros: el que estacionó afuera, el que entró por otro portón, el
> que se quedó toda la noche. Así que **los promedios describen la operación normal,
> no la operación completa** — y el problema que estás buscando suele vivir justo en
> la parte que no se midió.

Es la misma disciplina del denominador que ya usa el descubrimiento de guías: la
muestra que sobrevive está sesgada hacia el caso fácil.

---

## Paso 2 · Calibrar (solo la primera vez, y cuando el usuario lo pida)

**Después del capítulo 1, nunca antes.** Calibrar primero es fijar como "normal" un
número que puede ser el sesgo: en una cuenta real, la permanencia mediana en destino
daba **39 minutos** mientras la detección de salida estaba degradada, y **50** una vez
arreglada — porque justamente faltaban las salidas de los que se quedaban más tiempo.
Calibrar con los datos de esas semanas habría dejado 39 escrito como lo normal, y el
capítulo 3 habría estado midiendo desviaciones contra una cifra rota.

Y por lo mismo: **no calibres sobre un período que contenga un quiebre** (Paso 1). Si
lo hay, calibra sobre el tramo posterior y dilo.

**La primera corrida calibra.** No inventes umbrales, no traigas un estándar de la
industria, y no uses los de otra empresa. Lo normal lo define esta operación.

Cómo se hace está en **`references/calibracion.md`**. En resumen: pide
`get_operation_diagnostics(section="operacion")` del período, que ya trae cada magnitud
**como percentiles** (permanencia en origen y destino, tiempo de ruta, vueltas por día,
ralentí), **muéstrale la distribución al usuario** —mediana, cuartiles, la cola larga—
y **pregúntale qué es normal acá**. Después guárdalo.

Por qué esto no se puede saltar, con el caso que lo enseñó: un umbral de **2 horas** de
permanencia en origen **pinta de rojo una operación entera** cuando los camiones
pernoctan en la planta, porque la llegada es del día anterior y no hay nada anormal en
eso. El número era correcto; el umbral describía otra operación.

Al mostrarle la distribución, **muestra la forma, no solo el centro**. Dos operaciones
con la misma mediana y colas distintas son problemas distintos, y la mediana sola las
esconde.

La calibración **se guarda** (ver `references/calibracion.md`): base en la config de la
empresa, delta en el `spec_md` del mandante que opere distinto. Y **se revisa**: si el
usuario dice que algo cambió, o si la distribución se movió mucho respecto de la
calibración vigente, díselo y ofrécele recalibrar. No recalibres solo.

---

## Paso 3 · Capítulo 2 · La operación

Pide `get_operation_diagnostics(section="operacion")`. Trae el `resumen` del período
(viajes, entregados, vehículos, conductores, días), los `tiempos_min` de **origen,
destino, ruta y desvío de carga** como **p25 / mediana / p75 / p90 — cada uno con su
`_n` propio**, el bloque `hora_de_carga`, las `vueltas_por_vehiculo_dia` y la
`jornada_min`.

### El `n` que manda es el de la celda que vas a nombrar

**Un período puede aguantar el agregado y no aguantar el desglose**, y la respuesta no
distingue una cosa de la otra. Caso real: 65 viajes en cuatro días —agregado sólido— con
los destinos repartidos entre 1 y 7 viajes cada uno. Un destino con **4 viajes y 1
entrada sin salida** se reporta como *"pierde el 25 % de las salidas"*: aritméticamente
correcto, y no significa nada. Es **un** viaje.

**No tienes que calcularlo:** cada fila de `origenes`, `destinos` y `conductores` trae
**`muestra_chica`**, y la sección trae **`muestra_chica_bajo`** con el umbral que se
usó. Una fila marcada **no se nombra**: di que el período no alcanza para desglosar,
**nombra el umbral con el valor que vino** (no lo inventes ni lo redondees) y **propón
una ventana más larga**. El agregado sigue siendo válido y se reporta igual.

**Y `muestra_chica` no es lo mismo que `min_trips`, aunque lo parezcan.** `min_trips`
corta **por conductor**; `muestra_chica` avisa que **esa fila no sostiene una afirmación
sobre sí misma**. Medido en un período de cuatro días: **9 conductores pasaron el corte
de `min_trips` y los 9 estaban marcados** — pasaban el filtro y ninguno tenía muestra.
Sin la marca, `sin_muestra_suficiente` volvía con una sola persona y **todo lo demás
parecía sólido**. Son dos guardas distintas: no des por buena una fila porque pasó la
otra.

**Cada magnitud trae su propio `n`, y no son el mismo número.** El `n` de la permanencia
en origen no es el de la ruta: un viaje puede tener el hito de salida y no el de
llegada. Usa el `n` de cada magnitud junto a esa magnitud, nunca el total de viajes
para todas.

**Ningún número sale sin su denominador.** Se escribe *"1:47 sobre 1.187 de 1.366
viajes"*, nunca *"1:47"*. Un promedio sin denominador es una afirmación sobre un
universo que no se midió, y acá ya sabemos —por el capítulo 1— que ese universo tiene
un agujero conocido.

Tres cosas más:

- **Mediana antes que promedio.** Un viaje de 14 horas por una falla mecánica mueve el
  promedio y no mueve la mediana. La tool devuelve percentiles justamente por eso: la
  mediana y los cuartiles dicen la **forma** de la distribución, y el promedio la
  esconde. Si el usuario pide el promedio, dáselo con la mediana al lado; si difieren
  mucho, **eso es el hallazgo**, no un detalle de método.
- **Cuando p25 y la mediana viven en mundos distintos, no hay un centro que reportar.**
  Hay **dos poblaciones**, y decir "la mediana es X" las promedia en un número que no
  describe a ninguna. Caso real de permanencia en origen: **p25 = 19 minutos, mediana =
  562, p90 = 2.393** (casi 40 horas). Ahí la mediana ya cayó del lado del pernocte: no
  es una cola larga, son dos operaciones distintas —cargar y dormir en planta— metidas
  en la misma columna. Dilo así, y segmenta o reporta las dos.
- **Segmenta por lo que la operación distingue**: origen, ruta, tipo de vehículo,
  primera vuelta contra segunda. Un promedio general sobre rutas heterogéneas no
  describe ninguna.
- **Los tiempos son intervalos entre hitos**, así que heredan el problema del capítulo
  1: donde falta un hito, no hay dato — y **falta de dato no es cero**.

---

## Paso 4 · Capítulo 3 · Lo que se desvía

Ahora sí, contra **la calibración de esta empresa** (Paso 1). Nunca contra un estándar
inventado, uno de la industria, ni el de otro cliente.

Para cada desvío: **cuánto, sobre cuántos casos, y desde cuándo**. Un desvío que
apareció hace tres semanas es una historia distinta de uno que lleva un año, y la
diferencia cambia qué se hace al respecto.

**Y antes de llamar "desvío" a algo que aparece en la mitad de los casos, sospecha de
la definición.** Ésta es la lección más importante del capítulo:

> En una operación medida, **el 53 % de los viajes salía más de una hora tarde**
> respecto de la hora comprometida (mediana 63 minutos, sobre 1.147 medibles de
> 1.326). Suena a una operación fuera de control. Pero en esa cuenta, los viajes sin
> hora explícita **toman automáticamente el cupo disponible más cercano**: la "hora
> comprometida" era una convención del sistema, no una promesa que alguien hizo.
>
> **Un desvío que afecta a la mitad de los casos es más probablemente un problema de
> definición que de operación.** Antes de decir que alguien llega tarde, verifica que
> la hora contra la que estás midiendo **signifique algo**.

**Y ese caso no lo vas a poder resolver mirando los datos.** La plataforma **no
registra** si la hora comprometida la puso el mandante o la asignó el sistema al tomar
un cupo: `hora_de_carga.con_hora_comprometida` dice cuántos viajes **tienen** hora, no
**de dónde salió**. No intentes deducirlo, no lo infieras del patrón y no lo supongas
por el tipo de cuenta.

Es una **pregunta al usuario**, siempre:

> *"El 53 % sale más de una hora después de la hora comprometida. Antes de leer eso
> como atraso: esa hora, ¿la comprometen ustedes con el mandante, o la asigna el
> sistema tomando el cupo más cercano? La respuesta cambia el hallazgo entero."*

Según qué conteste, el mismo número es *"la operación llega tarde de forma
sistemática"* o *"la mitad de los viajes se mide contra una hora que nadie prometió"*.
Uno manda a arreglar la operación y el otro a arreglar la definición. **No elijas por
él.**

---

## Paso 5 · Capítulo 4 · Qué se puede hacer

Cada propuesta con **la misma forma, siempre**:

> **Evidencia** → **consecuencia** → **quién lo arregla** → **qué se cambia** → **qué rompe**

Las cinco partes son obligatorias. La última es la que casi nunca se escribe —un informe
que solo propone mejoras es una lista de deseos; uno que dice qué se rompe es una
decisión— y **la tercera es la que decide si el informe sirve o hace perder el tiempo**.

### Los tres dueños

| dueño | quién lo arregla | costo |
|---|---|---|
| **Plataforma** | DriveTech | El cliente **no puede**. Si se lo presentas como suyo, lo va a intentar y va a fracasar. |
| **Configuración** | El cliente, en su cuenta | El más rápido, y el que más se pasa por alto. |
| **Operación** | La gente que mueve camiones | El más caro y el más lento — y por eso **el peor lugar donde mandar un problema que no era suyo**. |

**El mismo síntoma puede ser de cualquiera de los tres, y eso no es teórico.** Una
cobertura de hitos del 78 % **parece** configuración —geocercas mal dibujadas— y en un
caso real era **plataforma**, y encima ya estaba resuelta. Sin atribuir, ese informe
manda a un cliente a redibujar polígonos sanos.

Y un 53 % de atraso contra la hora de carga puede ser **operación** (llegan tarde) o
**configuración** (la hora es un cupo que asignó el sistema). El mismo número, dos
dueños opuestos y dos acciones incompatibles.

**La atribución es una afirmación más, sujeta a la misma regla que el resto**: cuando no
esté clara, escribe las lecturas posibles y **quién puede distinguirlas**. No elijas por
conveniencia, y sobre todo no elijas "operación" por descarte — es el único de los tres
que cuesta plata y cansancio ajeno.

Pide `get_operation_diagnostics(section="configuracion")`. Trae las banderas de la
`cuenta`, las `restricciones` con cuántas veces bloquearon, `validacion_ia`, los
catálogos de clientes y orígenes (**en catálogo contra con viajes**), los tipos
definidos contra los usados, y el `formulario_de_recepcion` campo por campo con cuántas
veces vino vacío. O sea: las banderas **y su uso real**, que es lo que las hace
interpretables. Cómo leerlas está en
**`references/auditoria-configuracion.md`**; léelo antes de escribir el capítulo.

La idea que lo gobierna: **una bandera configurada no dice nada; una bandera con su uso
al lado dice algo.** Que exista una restricción es un hecho sin lectura. Que esa
restricción **haya bloqueado el 90 % de los intentos** admite dos lecturas opuestas
—está mal configurada, o hay un problema de fondo que está haciendo bien en frenar— y
distinguirlas es exactamente tu trabajo, no el de la tool.

### Las geocercas: propones, no aplicas

Nunca modifiques una geocerca. Propón el cambio con su evidencia (rebotes, entradas
sin salida, cobertura) y **di qué rompe**:

> **Agrandar una geocerca hace que los viajes arranquen antes.** Las permanencias
> medidas después del cambio **no son comparables con las de los meses anteriores**:
> parte de la mejora que se vea va a ser el cambio de instrumento, no de la operación.

Sin esa advertencia escrita, en tres meses alguien va a ver una mejora que no ocurrió —
y va a tomar decisiones con ella.

---

## Paso 6 · Los hallazgos de plataforma vuelven a DriveTech

Los hallazgos cuyo dueño es **plataforma** van, además de en su lugar del capítulo 4, en
una **sección aparte al final**, redactada para **copiarse y mandarse a DriveTech tal
cual**: con la evidencia y el período, no con la conclusión sola. Quien la reciba no vio
esta operación y no puede evaluar una conclusión suelta.

Por qué vale la pena el paso extra: una sola corrida en una sola cuenta produjo tres
hallazgos de este tipo, y uno de ellos —**la detección de salida degradada durante seis
semanas**— había sido invisible todo ese tiempo **porque el síntoma era "faltan datos",
y eso no se ve como una falla: se ve como que el dato no estaba**. Se arregló de
casualidad.

Con esta skill corriendo por cuenta, un problema así aparece en la primera corrida. Y si
aparece en **varias cuentas a la vez**, deja de ser la anomalía de un cliente y pasa a
ser un incidente de producto — que es una conclusión que ninguna cuenta puede sacar
sola.

Así que el informe es dos cosas al mismo tiempo: una herramienta para que el cliente
mejore su operación, y **un detector de los problemas de la propia plataforma,
distribuido en todas las cuentas que lo corran**. Escribe esa sección aunque esté vacía:
"sin hallazgos de plataforma en este período" también es información.

## La ficha por conductor

Pide `get_operation_diagnostics(section="conductores")`. Va **con nombre**, y por eso
con tres disciplinas que no son opcionales — las tres ya vienen respaldadas por la
respuesta, así que no hay que reconstruirlas:

**1 · Separa lo que depende del conductor de lo que no.** El tiempo de ruta entre
geocercas es suyo. La permanencia en origen **esperando que lo carguen** no lo es. Un
informe que le atribuye a una persona un número que produjo la operación es la forma
más rápida de que lo rechacen los mismos a quienes nombra — y de que se pierda también
lo que el informe tenía de cierto.

**2 · Mínimo de viajes — y las dos guardas son distintas.** Un conductor entra al
ranking solo si pasa `min_trips` **y** no viene con `muestra_chica`. Pasar el corte no
alcanza: en un período corto y parejo **todos lo pasan y todos vienen marcados**, y esa
combinación significa que no hay ranking que sostener — se dice y se propone una ventana
más larga. Un ranking sobre pocos casos es ruido con aspecto de hallazgo. La tool ya
separa: los que llegan al corte van en `conductores` y el resto en
`sin_muestra_suficiente`, con `min_viajes` diciendo dónde quedó la línea. **No los
mezcles de vuelta** — y tampoco los escondas: nómbralos como lo que son, *"4 conductores
quedaron fuera del ranking por tener menos de 5 viajes en el período"*. Si el usuario
necesita otro corte, se pide con `min_trips`, no se recalcula.

**3 · Compara contra trabajo comparable.** El tiempo de ruta va contra **la mediana de
esa misma ruta**, no contra el promedio general de la flota — para eso está
`ruta_vs_mediana_mediana`, que ya viene calculado por ruta. **Usa ese campo, no compares
tiempos de ruta crudos entre conductores**: eso compara rutas y le pone el nombre de una
persona.

Y el encuadre: esto es para **encontrar dónde ayudar**, no para armar un ranking de
castigo. Si un conductor se desvía siempre en la misma ruta, la pregunta útil es qué
tiene esa ruta.

---

## Tres terrenos cargados

**La jornada.** Medimos horas de motor y el **span** del viaje. **Eso no es la jornada
laboral**: no sabemos de pausas, relevos ni tiempo administrativo. Decir "está
excedido" es una afirmación de **cumplimiento legal** que este dato no sostiene.
Reporta el span, medido y con su nombre, y deja la conclusión legal a quien conoce el
contrato y la normativa. **Y la holgura es un hallazgo tan accionable como el
exceso** — nadie la mira porque no duele, y es donde está la capacidad ociosa.

**El ralentí.** De los datos más limpios que hay, pero **el umbral no es universal**:
un equipo con refrigeración idlea para mantener temperatura, y ahí el ralentí no es
desperdicio. Sale de la calibración, no de un número traído de afuera.

**Las geocercas.** Ver arriba: se propone, no se aplica, y se dice qué rompe.

---

## La entrega

**El formato y la marca salen de la plantilla de la empresa**, `extra.reporte_tipo` en
la config — los mismos colores, tipografía y estructura con que esta empresa le habla a
sus mandantes. Si el análisis define su propia paleta, el día que cambie el color
corporativo hay dos lugares donde tocarlo y uno se va a olvidar.

Si el análisis es de un mandante, aplica también **su delta** ("Reporte de status:
ajustes" en su `spec_md`). Base más delta, igual que el reporte de estado: **nunca una
copia de la plantilla**.

Si algo que el análisis necesita no está en la plantilla, **no lo inventes por tu
cuenta**: si le sirve a todos, propón subirlo a `extra.reporte_tipo` con
`set_backlog_config` (recordando que `extra` se **reemplaza completo**: lee, mezcla y
reenvía). Si es solo de este mandante, va a su delta.

---

## Reglas de oro

- **Primero el instrumento, después la medición.** Si no reportaste la cobertura de
  hitos, todavía no puedes interpretar un promedio.
- **`como_leerlo` se lee antes de interpretar**, y si contradice tu lectura, gana él.
- **La tool computa, tú interpretas.** Si te ves calculando un promedio, falta una
  sección: repórtalo, no lo improvises.
- **Los nombres los pone la tool.** Dos grafías del mismo conductor son un hallazgo, no
  algo que unifiques en silencio.
- **Ningún número sin denominador.** Va pegado al número, no al pie. Y falta de dato no
  es cero.
- **El `n` que manda es el de la celda que vas a nombrar**, no el del período. Una fila
  con `muestra_chica` no se nombra: se dice que el período no alcanza y se propone una
  ventana más larga.
- **Pasar `min_trips` no es tener muestra.** Son dos guardas con modos de falla
  distintos; una fila necesita las dos.
- **Si p25 y la mediana viven en mundos distintos, son dos poblaciones**, no una con
  cola larga. No hay centro que reportar.
- **Lo normal lo define esta empresa**, no la industria ni otro cliente. Sin
  calibración no hay capítulo 3 — y sin capítulo 1, la calibración fija el sesgo como
  normal.
- **Mediana antes que promedio**, y si difieren mucho, eso es el hallazgo.
- **Un desvío que afecta a la mitad de los casos es sospechoso de definición**, no de
  operación. Verifica qué significa aquello contra lo que mides — y si el dato no está
  (la plataforma no registra de dónde salió la hora comprometida), **pregunta**, no
  deduzcas.
- **Cada propuesta dice quién lo arregla y qué rompe.** Sin dueño, el informe manda al
  cliente a arreglar lo que no puede, o a la operación lo que era configuración.
- **No elijas "operación" por descarte.** Es el dueño más caro y el más lento.
- **Un período con un quiebre no es comparable consigo mismo.** Busca el escalón antes
  de promediar, y analiza después del corte.
- **Las geocercas se proponen, no se aplican** — y agrandar una corta la comparación
  con el pasado.
- **Al conductor solo lo que depende de él**, con mínimo de viajes y contra trabajo
  comparable.
- **El span no es la jornada laboral.** No firmes una conclusión de cumplimiento con
  un dato que no la sostiene.
- **La holgura es un hallazgo**, no un espacio en blanco.
- **El formato sale de la plantilla de la empresa.** El análisis no trae su propia
  marca.
- **Un dato bien medido no autoriza su interpretación.** Separa el hecho de la lectura,
  y cuando la lectura sea tuya, dilo.
