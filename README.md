# Drivetech · Marketplace de plugins para clientes

Marketplace público de [Claude Code](https://code.claude.com) con los plugins que
Drivetech ofrece a sus clientes para automatizar su operación con Drivetech (TMS,
flota, monitoreo y más). A medida que sumemos plugins, todos viven acá.

## Cómo lo usa un cliente

En Claude Code (o Cowork), agregar el marketplace y luego instalar el plugin:

```bash
/plugin marketplace add Drivetech/claude-plugins-clientes
/plugin install drivetech-tms@drivetech-clientes
```

> Al ser un repo **público**, el cliente no necesita autenticarse para agregarlo.
> El nombre del marketplace es `drivetech-clientes` (distinto del interno
> `drivetech`, para que ambos puedan convivir en un mismo equipo).

También pueden abrir el explorador interactivo con `/plugin` (pestañas *Discover*,
*Installed*, *Marketplaces*).

## Plugins disponibles

| Plugin | Qué hace |
|---|---|
| **drivetech-tms** — Operación TMS | Descubrimiento del formato de cada mandante (onboarding), carga diaria al backlog + asignación, y estatus de los viajes. Sirve a mandantes de carga (intake por archivo propio) y a empresas de transporte (intake por correo). *Próximamente: análisis de la operación.* |

## Estructura del repositorio

```
drivetech-marketplace/
├── .claude-plugin/
│   └── marketplace.json        # catálogo del marketplace
├── plugins/
│   └── drivetech-tms/      # cada plugin en su carpeta
│       ├── .claude-plugin/plugin.json
│       ├── skills/
│       └── README.md
└── README.md
```

## Para el equipo Drivetech — agregar o actualizar un plugin

1. Crea la carpeta del plugin en `plugins/<nombre>/` con su
   `.claude-plugin/plugin.json` y sus `skills/`.
2. Agrega (o actualiza) su entrada en `.claude-plugin/marketplace.json`,
   subiendo la `version` cuando publiques cambios.
3. Valida antes de publicar:
   ```bash
   claude plugin validate ./.claude-plugin/marketplace.json
   claude plugin validate ./plugins/<nombre>
   ```
4. Commit y push a `main`. Los clientes reciben la actualización al correr
   `/plugin marketplace update drivetech-clientes` (o en la actualización
   automática).

Este marketplace es **público** y separado del marketplace privado de plugins
internos de la empresa.
