# Drivetech · Carga de viajes al backlog

Plugin para cargar al TMS de Drivetech los viajes que cada mandante manda en su
propio formato. Resuelve el dolor de siempre: **cada cliente entrega sus viajes
distinto** (una tabla en el correo, un Excel, un PDF) y convertirlos al formato
de la plataforma es lento y propenso a errores.

La idea central: **descubrir una vez, cargar todos los días.**

## Las tres skills

| Skill | Cuándo se usa | Qué hace |
|---|---|---|
| **descubrir-mandante** | Una vez por mandante (o si cambia su formato) | Lee muestras reales del mandante, infiere el mapeo a viajes del backlog, lo valida contra la plataforma y una carga de prueba, entrevista las reglas de asignación, y guarda el **perfil** del mandante. |
| **cargar-viajes-backlog** | Todos los días | Consigue la solicitud del mandante (correo o archivo, según su intake), carga los viajes al backlog y propone la asignación de vehículo/conductor. |
| **seguimiento-operacion** | Durante el día | Panorama de los viajes (estado, permanencias, tiempo en ruta), detecta anomalías y audita contra geocercas para separar un problema real de uno de geocerca; arma el estado interno o para el mandante. |

## El modelo: un perfil por mandante

Todo lo específico de un mandante vive en su **perfil** (`spec_md`): cómo se
reconoce su solicitud, el mapeo campo por campo, si usa tipos de vehículo, las
reglas de origen, el criterio de asignación, qué se le reporta y los umbrales de
seguimiento. El **flujo** (conseguir, cargar, asignar, seguir) es igual para todos
y vive en las skills.

Esto sirve para los dos tipos de cliente por igual, gracias a que el **intake**
(cómo entran los viajes) está separado del core de mapeo y carga:

- **Mandante de carga** (sube su propio backlog con su agente): intake `archivo`
  — su agente levanta el export que él genera desde una carpeta/Drive y lo carga.
  Un perfil, el suyo. `descubrir-mandante` en el onboarding; `cargar-viajes-backlog`
  a diario.
- **Empresa de transporte** (recibe pedidos de muchos clientes): intake
  `correo` — el agente lee el mail del mandante. Un perfil por cada uno de sus
  clientes. `descubrir-mandante` una vez por cliente; `cargar-viajes-backlog` a
  diario para todos.

Ambos suben al backlog por el mismo MCP de Drivetech, cada uno contra su empresa.

Los perfiles y la config **son datos del cliente** y viven en el **backend de
Drivetech, por empresa** (vía MCP): sobreviven a las actualizaciones del plugin,
al entorno efímero y al cambio de equipo. (Con fallback a archivos locales si una
instalación no tiene backend.)

## Requisitos

- **MCP de Drivetech** conectado, con acceso al módulo TMS de la empresa.
- **Un conector de correo** (Gmail u Outlook) para la skill de carga.
  - En Gmail, marcar los correos como procesados necesita scope `gmail.modify`.
  - Para enviar respuestas se necesita permiso de envío; sin él, la skill deja el
    correo como borrador.

## Puesta en marcha

1. Instala el plugin.
2. **Configura la instalación:** invoca `cargar-viajes-backlog` y pídele que la
   configure, o copia `config.example.yaml` a `config.yaml` y complétalo.
3. **Agrega tu primer mandante:** invoca `descubrir-mandante` con una muestra real
   de sus viajes. Deja escrito su perfil.
4. **Opera:** a diario, `cargar-viajes-backlog` hace el resto. Puedes dispararla a
   pedido o programarla para que revise el correo sola.

## Estado — v0.0.1 (en desarrollo)

Plugin en construcción; aún lo estamos probando con operaciones reales antes de
publicarlo. Lo de abajo es el avance funcional a la fecha.

### Avance

- **Persistencia en el backend de Drivetech** (por empresa, vía MCP:
  `get_backlog_settings`, `upsert_backlog_mandante`, `set_backlog_config`,
  `delete_backlog_mandante`). Config y perfiles (`spec_md`) viven ahí, no en
  archivos; con fallback a archivos si el backend no está.
- **Perfil vivo:** las reglas de casos borde que el usuario da mientras asigna se
  guardan en el `spec_md` del mandante sobre la marcha (Paso 9), versionadas.
- **Descubrimiento completo:** tras validar el formato, la skill entrevista al
  usuario por las reglas de asignación de viajes a conductores/vehículos y las deja
  en el perfil, de modo que el día a día sea solo cargar y asignar. Validado con un
  cliente real (ICB, intake archivo).

- **Características de vehículo desde el catálogo.** El descubrimiento y la carga
  leen `get_tms_catalog kind=vehicle_skills`: el flag `skills_enabled` dice si son
  obligatorias, y la lista de características resuelve tokens desconocidos del
  archivo (un "S28", un "C14") como `skills_required` en vez de preguntar.
- **Dónde vive el estado del cliente.** `config.yaml` y los perfiles viven en una
  carpeta de datos **fuera del plugin**, para que un update del marketplace no los
  pise (interino). El destino es el backend de Drivetech por MCP; ver
  `spec-backlog-perfiles-backend.md`.

## Notas de la versión 0.2.0

- **Intake abstraído** en la skill de carga: `correo` (empresa de transporte) y
  `archivo` (mandante de carga que sube su propio export). El core de mapeo,
  validación y carga es el mismo para ambos.
- Fuentes de descubrimiento soportadas: correo con tabla, Excel/CSV y PDF.
- Incluye un perfil de ejemplo ficticio (`mandantes/ejemplo.md`) como referencia
  de cómo se ve un perfil bien hecho.
- La rama de Outlook de la skill de carga está escrita pero validada
  principalmente contra Gmail; acompaña la primera corrida con Outlook.
- El intake `archivo` está escrito y listo para probar; conviene acompañar la
  primera corrida de una instalación que lo use.
