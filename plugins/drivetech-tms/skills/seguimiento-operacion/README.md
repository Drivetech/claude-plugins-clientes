# seguimiento-operacion — instrucciones de uso

Skill para **seguir la operación durante el día**: ver cómo van los viajes ya
cargados y asignados, detectar problemas y auditar contra geocercas. Sirve tanto
para la vista interna de la empresa de transporte como para armarle el estado al
mandante.

Este archivo es para **la persona**. El agente lee `SKILL.md`.

## Qué hace

1. **Panorama del día** — estado de cada viaje (pendiente / asignado / en ruta /
   entregado), hora comprometida, ETA, permanencia en origen y destino, y tiempo
   en ruta.
2. **Anomalías** — atrasos, viajes que no han iniciado, permanencias o rutas
   demasiado largas, hitos inconsistentes, GPS sin reportar.
3. **Auditoría de geocercas** — los viajes se inician y cierran con la entrada/
   salida a las geocercas de origen y destino, y eso a veces falla. Para un viaje
   sospechoso, la skill cruza con las visitas de geocerca y el historial del móvil
   para decir si es un **problema real** (no llegó) o un **problema de geocerca**
   (sí pasó, pero el hito no se registró) — y qué revisar.

## Cómo usarla

Pídele lo que necesites:

- *"¿Cómo va la operación hoy?"* → panorama + anomalías.
- *"¿Qué viajes están atrasados / sin iniciar?"* → solo lo que requiere atención.
- *"Audita el viaje 2329126"* → cruce con geocercas y causa probable.
- *"Ármame el estado para el mandante"* → borrador según las reglas de su perfil.

## Cómo trabaja (para saber qué esperar)

- **Se apoya en el manual de Drivetech.** Consulta el artículo del centro de
  conocimiento sobre cómo se inician y cierran las guías, para no confundir el
  comportamiento normal (p.ej. la ventana de ~30 min para cerrar) con un problema.
- **Un hito ausente no es un incumplimiento.** Antes de reportar un atraso,
  descarta que sea un problema de geocerca o de GPS.
- **Si el problema es la geocerca, te recomienda ajustarla.** Cerrar el viaje a
  mano resuelve el día; ajustar la geocerca (tamaño/posición o el tiempo mínimo de
  permanencia) evita que el problema se repita.
- **No cierra ni reasigna viajes.** Te dice qué pasa y qué conviene hacer; los
  cambios los haces tú en la plataforma.
- **Los umbrales** (cuánto atraso o permanencia es "anomalía") vienen con valores
  por defecto y se ajustan por mandante en su perfil. Si le das un criterio nuevo,
  queda guardado para la próxima.
- **Al mandante siempre como borrador**, con lo que ese mandante quiere ver, y no
  se envía sin tu visto bueno.
