# cargar-viajes-backlog — instrucciones de uso

Skill para cargar al TMS de Drivetech las solicitudes de viaje del día, ya sea
que lleguen **por correo** (empresa de transporte que recibe de su mandante) o
como un **archivo que el propio mandante genera** (mandante de carga que sube su
backlog). Cómo entran los viajes (el *intake*) se configura por mandante; el resto
del ciclo es igual. Cubre el día completo:

1. Consigue la solicitud del mandante (correo o archivo, según su intake).
2. La carga al **backlog** del TMS.
3. Asigna vehículo y conductor.
4. Si corresponde, le informa al mandante quién hace cada viaje y cómo van saliendo.

Este archivo es para **la persona**. El agente lee `SKILL.md`.

---

## Dónde vive qué

| Qué | Dónde | ¿Lo tocas tú? |
|---|---|---|
| El flujo | `SKILL.md`, igual para todos | No. Se actualiza con la skill. |
| Tu config (correo, marca, firma) | En el **backend de Drivetech**, por empresa | Una vez, en la puesta en marcha. |
| El perfil de cada mandante (cómo se lee, mapea, asigna, comunica) | En el **backend de Drivetech** | Al agregar el mandante, y se va afinando solo con el uso. |

Que la config y los perfiles vivan en el backend hace que **actualizar la skill no
te borre nada**, que valgan en cualquier equipo, y que las reglas que le vayas
enseñando a un mandante queden guardadas para siempre. (Si tu instalación no tiene
backend, la skill cae a archivos locales — `config.yaml` y `mandantes/*.md` — sin
cambiar el flujo.)

---

## Requisitos

- **Un conector de correo** por MCP (Gmail u Outlook).
  - En Gmail, para marcar los correos ya procesados hace falta scope
    `gmail.modify`. Sin eso igual funciona, pero cada corrida vuelve a revisar el
    mismo hilo.
  - Para **enviar** se necesita permiso de envío. Si no lo tienes, la skill deja
    el correo como borrador y lo mandas tú.
- **El MCP de Drivetech** conectado, con acceso al módulo TMS.
  - Si tu cuenta ve una sola empresa, no hay nada que elegir.
  - Si ve varias, la skill fija la correcta al empezar cada corrida.

---

## Puesta en marcha

**Primera vez:** invoca la skill y pídele que la configure. Si la empresa no tiene
nada guardado, el agente te va a preguntar lo necesario, lo va a **guardar en el
backend**, y después va a **probar la instalación**: que puede buscar correos,
marcarlos, redactar un borrador y hablar con el TMS. Si algo falta, te lo dice ahí
y no a las 7 de la mañana con los camiones esperando.

---

## Uso diario

**A pedido** — invócala y pídele lo que necesites:

- *"Cárgame los viajes al backlog"* → busca el correo, muestra lo que encontró,
  pide confirmación y carga.
- *"Asigna la primera vuelta"* → propone la repartición según el criterio del
  mandante y asigna lo que apruebes.
- *"Asigna las segundas vueltas"* → más tarde en el día, mirando cómo volvió cada
  conductor.
- *"Mándale el estado al mandante"* → arma el reporte y lo deja como borrador.

**Automática** — para que revise el correo sola:

- En Claude Code: `/loop 5m` sobre la skill, o una rutina programada.
- En Claude Desktop / web: prográmala.

Si no llegó correo nuevo, termina en silencio. Si nunca fue configurada, **no
pregunta nada** en una corrida automática: deja constancia y espera a que estés.

---

## Cómo trabaja (para saber qué esperar)

- **Pide confirmación antes de cargar.** Para que cargue directo, díselo y que lo
  deje como regla del mandante.
- **Aprende sobre la marcha.** Cuando le das una instrucción nueva para un
  mandante (un caso borde, una excepción), te pregunta si la deja permanente y la
  guarda en el perfil de ese mandante — no se pierde al cerrar.
- **Asigna solo la primera vuelta.** Las segundas se deciden más tarde, viendo
  quién volvió a tiempo y dónde quedó. No asigna el día completo de una vez.
- **Respeta siempre las características del viaje** (S28 / C14 y equivalentes).
  Esa regla no la negocia ningún criterio de mandante.
- **No manda correo sin tu visto bueno.** Siempre te muestra el borrador primero.
- **Cargar el mismo correo dos veces no duplica**: la llave es el número de guía.

---

## Agregar un mandante

Pídeselo al agente y ten a mano **un correo de ejemplo ya recibido** de ese
cliente. Va a leerlo, proponerte el mapeo campo por campo, hacértelo confirmar, y
recién ahí **guardar el perfil del mandante en el backend**. (Lo hace la skill
`descubrir-mandante`.)

Lo que hay que dejar acordado, además del formato del correo:

- El **criterio de asignación** de esa operación (rotación, cercanía, lo que sea).
- Qué se le informa de vuelta, **cada cuánto** y con qué datos.
- Qué se hace cuando un viaje se atrasa.

Después valida con una carga chica: un viaje en `dry_run`, luego real, y revisa
en la plataforma que la **hora comprometida** se vea igual que en el correo.

---

## Entregársela a un cliente

Instala el plugin desde el marketplace; su config y sus perfiles se guardan en el
**backend, en su propia empresa**, así que parte en limpio y su puesta en marcha
crea lo suyo. No se copian archivos de configuración entre clientes.

Ten presente que su cuenta ve **una sola empresa**, así que no tiene que elegir
ninguna — y si alguna vez le aparece *"la empresa no tiene contratado el módulo
de tms"*, no es que se le haya cambiado la empresa: es que de verdad no tiene TMS
contratado.

---

## Limitaciones conocidas

- **No sabe reasignar.** Cambiar el vehículo o conductor de un viaje ya asignado
  se hace hoy en la plataforma. La skill sí relee el estado después para dejar la
  información al día.
- **La rama de Outlook no está probada.** El flujo está escrito, pero se validó
  contra Gmail. Acompaña la primera corrida de una instalación con Outlook.
- **Los hitos de origen y destino vienen disparejos.** Muchos viajes entregados
  no tienen hora de salida del destino, así que no siempre se puede calcular la
  permanencia. La skill informa cuántos quedaron sin dato en vez de inventarlo.
