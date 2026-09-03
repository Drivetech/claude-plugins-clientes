# Calibrar: qué es normal en esta empresa

Sin calibración no hay capítulo 3. "Se desvía" es una afirmación relativa, y lo que
está del otro lado de la comparación tiene que ser **esta operación**, no un estándar
de la industria ni el de otro cliente.

## Se calibra DESPUÉS del capítulo 1

Calibrar antes de revisar el instrumento fija como normal un número que puede ser el
sesgo. Medido en una cuenta real: la permanencia mediana en destino daba **39 minutos**
mientras la detección de salida estaba degradada, y **50** una vez arreglada — faltaban
justamente las salidas de los que se quedaban más tiempo. **El sesgo no era ruido: tenía
dirección.**

Si hubiera calibrado en esas semanas, 39 quedaba escrito como lo normal y el capítulo 3
habría medido desviaciones contra una cifra rota, indefinidamente.

Y si el período contiene un quiebre (Paso 1), calibra **sobre el tramo posterior** y
dilo.

## Por qué no se puede saltar

Un umbral de **2 horas** de permanencia en origen pinta de rojo una operación entera
cuando los camiones **pernoctan en la planta**: la llegada es del día anterior y no hay
nada anormal. El número medido era correcto; el umbral describía otra operación.

Ese caso ya está anotado en la plantilla de reporte de una empresa real y sigue siendo
cierto. Es el recordatorio de que **el dato no trae su interpretación puesta**.

## Qué se calibra

| magnitud | qué se pregunta |
|---|---|
| Permanencia en origen | ¿Cuánto es una carga normal? ¿Hay orígenes donde se pernocta, y desde qué hito se debería medir ahí? |
| Permanencia en destino | ¿Cuánto tarda una descarga normal? ¿Cambia por tipo de cliente? |
| Tiempo de ruta | ¿Se compara por ruta? ¿Hay rutas con peaje, cordillera o urbano que no son comparables entre sí? |
| Vueltas por vehículo | ¿Cuántas se esperan en un día normal? ¿Hay primera y segunda vuelta con lógicas distintas? |
| Ralentí | ¿Qué equipos idlean **por diseño** (refrigeración) y no deberían contarse igual? |
| Span de jornada | ¿Cuál es el rango habitual? (Ojo: esto **no** es la jornada laboral — ver el `SKILL.md`.) |
| Hora comprometida | ¿Es una promesa real, o la asigna el sistema por cupo? **La plataforma no registra esto**, así que es pregunta obligada: sin la respuesta, cualquier "atraso" que reportes puede no significar nada. |

## Cómo se hace

1. **Pide la distribución real** con `get_operation_diagnostics(section="operacion")`
   del período. Ya viene en percentiles (p25 / mediana / p75 / p90), cada magnitud con
   su propio `n`. Lee el `como_leerlo` de la respuesta antes de mostrar nada.
2. **Muéstrasela al usuario con su forma, no solo con su centro.** Mediana, cuartiles y
   la cola. Dos operaciones con la misma mediana y colas distintas son problemas
   distintos, y la mediana sola los esconde.
3. **Pregúntale qué es normal acá**, magnitud por magnitud, y con la distribución
   delante — no en abstracto. La pregunta útil es *"el 25 % de tus cargas pasa de 2:40:
   ¿eso es un problema o es cómo funciona ese origen?"*, no *"¿cuál es tu umbral?"*.
4. **Anota también las excepciones**, no solo el número: el origen donde se pernocta,
   los equipos que idlean por diseño, la ruta que no se compara con ninguna. Una
   calibración sin excepciones vuelve a pintar de rojo lo mismo.
5. **Guárdala** (ver abajo) y dile al usuario que quedó guardada y desde cuándo.

## Dónde se guarda

Sigue la arquitectura que ya usa el reporte de estado: **base de empresa + delta por
mandante.**

- **La base**, en la config de la empresa, con `set_backlog_config` — bajo `extra`,
  junto a `reporte_tipo`. Recuerda que **`extra` se reemplaza completo**: lee, mezcla
  tu cambio y reenvía el resto.
- **El delta**, en el `spec_md` del mandante que opere distinto, con
  `upsert_backlog_mandante` (read-modify-write: esa tool reemplaza el perfil entero).
  Solo lo que ese mandante hace **diferente**; lo que no se menciona, se hereda.

La misma pregunta de siempre resuelve dónde va cada cosa: **¿a quién le sirve?** Si el
umbral vale para toda la operación, va a la empresa. Si es de un mandante, a su delta.
Meter en la base algo de un solo mandante ensucia el análisis de todos.

## Cuándo se recalibra

- **Cuando el usuario lo pida.**
- **Cuando la distribución se haya movido mucho** respecto de la calibración vigente.
  Ahí **no recalibres solo**: díselo, muéstrale las dos distribuciones y ofrécelo. Una
  calibración que se actualiza sola convierte cualquier deterioro gradual en la nueva
  normalidad, que es exactamente lo que el capítulo 3 tiene que detectar.

Anota **cuándo** se calibró y **sobre qué período**. Una calibración sin fecha no se
puede juzgar, y la de hace un año puede estar describiendo una flota que ya no existe.
