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
- Si los tienes: la **razón social** y el **RUT** del mandante. No son obligatorios,
  pero conviene tenerlos — son el nombre con que ese mandante aparece **impreso en
  los documentos**, que casi nunca es el nombre corto que usa el sistema. Sin ellos,
  la verificación de guías puede rechazar documentos que estaban buenos. Si no los
  tienes a mano, el agente los deja anotados como pendiente.

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

En el **backend de Drivetech**, asociado a tu empresa. No es un archivo en tu
computador: por eso **sobrevive a las actualizaciones** del plugin, vale en
cualquier equipo y no se pierde si cambias de máquina. Drivetech además guarda las
versiones anteriores, así que un perfil se puede comparar o revertir.

(Si tu instalación no tiene backend, el perfil cae a un archivo local
`mandantes/<mandante>.md` en la carpeta de datos de la skill de carga. El flujo es
el mismo.)

## Después

Valida con la primera carga real del día siguiente: revisa en la plataforma que
la hora comprometida y los tipos de vehículo hayan quedado como en la solicitud.
Si algo no calza, se corrige editando el perfil de ese mandante.

## Y la guía de despacho, ¿cuándo?

Después, y por separado. Un mandante recién configurado todavía no tiene guías
suyas en el sistema: el papel aparece cuando empieza a operar. Cuando ya tenga
algunas, se descubre el formato de su guía aparte. El agente te lo recuerda al
cerrar.

## Si el mandante cambia de formato

Vuelve a usar esta skill con una muestra del formato **nuevo**. El agente detecta
que ese mandante ya existe y **rehace solo la parte de lectura**: las reglas de
asignación, la comunicación y todo lo que le fuiste enseñando operando quedan
intactas. Antes de guardar te muestra qué cambia y qué queda igual.
