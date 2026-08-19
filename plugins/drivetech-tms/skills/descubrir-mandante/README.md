# descubrir-mandante — instrucciones de uso

Skill de **onboarding**: se usa una vez por cada mandante (cliente que te manda
solicitudes de viaje) para enseñarle al sistema cómo leer su formato. El
resultado queda guardado como el "perfil" de ese mandante, y a partir de ahí la
operación diaria la hace la skill **cargar-viajes-backlog**.

Este archivo es para **la persona**. El agente lee `SKILL.md`.

---

## Cuándo usarla

- Entra un cliente/mandante nuevo y hay que configurar cómo se leen sus viajes.
- Un mandante ya configurado **cambió su formato** (nuevas columnas, otro
  archivo) y hay que rehacer su perfil.

No es una skill de todos los días. Para cargar los viajes de la jornada, usa
cargar-viajes-backlog.

## Qué necesitas tener a mano

- **Una muestra real** de cómo ese mandante manda sus viajes: un correo con la
  tabla, un Excel/CSV o un PDF ya recibido. Si el formato cambia de un envío a
  otro, ten 2–3 muestras.
- El **MCP de Drivetech** conectado (se usa para verificar destinos, orígenes y
  para una carga de prueba).

## Cómo trabaja

1. Le pasas la muestra. El agente la lee de verdad (no le cuentes el formato de
   memoria — dale el archivo).
2. Extrae la tabla de viajes y te la muestra para que confirmes que están todas.
3. Te propone el **mapeo**: qué columna es el número de guía, cuál la hora, el
   destino, si la operación usa tipos de vehículo, de dónde salen, etc.
4. Verifica los destinos y orígenes contra la plataforma, y hace una **carga de
   prueba** de uno o dos viajes para confirmar que la hora queda bien.
5. Te pregunta lo que no se ve en la muestra: cómo se reparten los viajes entre
   conductores, qué se le informa al mandante y cada cuánto, qué es primera y
   segunda vuelta.
6. Con tu visto bueno, escribe el **perfil del mandante** y lo deja listo para la
   operación diaria.

## Dónde queda el perfil

En la carpeta de la skill de carga (`cargar-viajes-backlog/mandantes/`), como un
archivo por mandante. Esa carpeta es tuya y **sobrevive a las actualizaciones**
del plugin: agregar o corregir un mandante no toca el flujo, y actualizar el
plugin no te borra los perfiles.

## Después

Valida con la primera carga real del día siguiente: revisa en la plataforma que
la hora comprometida y los tipos de vehículo hayan quedado como en la solicitud.
Si algo no calza, se corrige editando el perfil de ese mandante.
