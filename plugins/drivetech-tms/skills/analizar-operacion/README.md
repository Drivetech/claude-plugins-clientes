# analizar-operacion — instrucciones de uso

Skill de **análisis**: mira un período de tu operación y te dice qué está pasando, qué
se sale de lo normal **en tu operación** y qué conviene cambiar — incluida la
configuración de la plataforma y las geocercas.

Este archivo es para **la persona**. El agente lee `SKILL.md`.

---

## En qué se diferencia de `seguimiento-operacion`

`seguimiento` te dice **qué está pasando hoy**: qué viajes van atrasados, cuáles no
arrancaron, dónde hay una permanencia rara. Es del día.

Ésta te dice **qué significa** y **qué conviene hacer**, mirando un período largo. Es
para sentarse a decidir, no para resolver la mañana.

## Cada hallazgo te dice quién lo arregla

Es lo que hace que el informe sirva. Un mismo síntoma puede ser de tres dueños
distintos:

- **Plataforma** — lo arregla DriveTech. Vos no podés, y si el informe no lo dijera,
  perderías tiempo intentándolo.
- **Configuración** — lo arreglás vos en tu cuenta. Es lo más rápido y lo que más se
  pasa por alto.
- **Operación** — lo cambia la gente que mueve camiones. Es lo más caro y lo más lento.

Un caso real: una cobertura de datos del 78 % **parecía** que había geocercas mal
dibujadas, y era un problema de la plataforma **que ya estaba arreglado**. Sin esa
distinción, el informe mandaba a redibujar polígonos sanos.

Los hallazgos de plataforma además salen en una sección aparte al final, lista para
mandarnos a nosotros.

## La primera vez no te va a dar un informe

Y es a propósito. La primera corrida **calibra**: te muestra cómo se distribuyen de
verdad tus tiempos —cuánto tarda una carga normal, cuánto una descarga, cuántas vueltas
hace un camión— y **te pregunta qué es normal en tu operación**.

Sin eso, cualquier umbral sería inventado. El caso que lo enseñó: un límite de 2 horas
de permanencia en el origen pinta de rojo una operación entera cuando los camiones
**duermen en la planta** — el número estaba bien medido y la conclusión era falsa.

Lo que contestes queda guardado. De ahí en adelante, las corridas siguientes sí son
informes.

## Los cuatro capítulos

**1 · El instrumento.** Antes de mostrarte un solo promedio —y antes incluso de la
calibración— te dice **cuánto de tu operación se pudo medir**. Los tiempos salen de que el camión entre y salga de una
geocerca; si el polígono es chico o el camión estaciona afuera, ese viaje no se midió.
En operaciones reales, entre una de cada cuatro y una de cada siete entregas queda
fuera.

Esto va primero porque cambia cómo se lee todo lo demás: **los promedios describen los
viajes que la geocerca alcanzó a ver**, que tienden a ser los normales.

También revisa si **fue el mismo instrumento durante todo el período**. Si a mitad de
camino cambió algo —un despliegue, una geocerca redibujada—, el promedio del período
completo es el promedio de dos operaciones distintas y no describe a ninguna. Cuando
eso pasa, el agente te lo dice con fecha y analiza el tramo posterior en vez de
promediar encima.

**2 · La operación.** Tus tiempos reales de carga, ruta y descarga, vueltas por camión
y jornadas. Cada número **con cuántos viajes lo respaldan**, siempre.

**3 · Lo que se desvía.** Contra lo que vos dijiste que es normal, no contra un
estándar de manual.

**4 · Qué se puede hacer.** Cada propuesta con: la evidencia, qué efecto esperar,
**quién lo arregla**, y **qué se rompe si lo hacés**. Esa última parte es la que hace
que sea una decisión y no una lista de deseos.

## Sobre los conductores

El informe puede incluir desempeño **por conductor, con nombre**, y está pensado para
**encontrar dónde ayudar**, no para armar un ranking de castigo. Tres cuidados que el
agente aplica siempre:

- **Solo lo que depende de él.** El tiempo de ruta es suyo; esperar a que lo carguen en
  el origen, no.
- **Nadie entra al ranking con pocos viajes.** Un promedio sobre tres viajes es ruido.
- **Se compara contra la misma ruta**, no contra el promedio general. Si no, se compara
  la ruta y se le pone el nombre de la persona.

## Dos cosas que el informe no va a afirmar

**Que alguien excede su jornada laboral.** Se mide el tiempo entre que arranca y
termina, pero no sabemos de pausas, relevos ni tiempo administrativo. El dato te lo da;
la conclusión legal la saca quien conoce el contrato.

**Que una geocerca hay que moverla, y moverla.** Te la propone con la evidencia y te
avisa el costo: al agrandar una geocerca los viajes empiezan a contar antes, así que
**los tiempos dejan de ser comparables con los meses anteriores**. Parte de la mejora
que veas después va a ser el cambio de instrumento, no de la operación.

## Qué te conviene tener a mano

- **El período** que querés mirar. Por defecto, 60 días.
- Un rato para la calibración, la primera vez. Son preguntas concretas sobre tus
  propios números, no un cuestionario.
- Si el análisis es de un mandante en particular, decilo: sus reglas propias ya están
  guardadas y el agente las aplica.

## El formato

Sale de la **plantilla de tu empresa** — los mismos colores, tipografía y estructura con
que le respondés a tus mandantes. El análisis no trae marca propia: si la trajera, el
día que cambies el color corporativo habría dos lugares donde tocarlo.
