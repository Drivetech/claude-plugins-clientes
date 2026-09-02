# Anatomía del `document_spec` — contrato del artefacto

**Este archivo es el contrato del `document_spec`, no documentación de una sola
skill.** Lo escribe `descubrir-guia-despacho` (y, en su versión sin números, la
pantalla de creación de mandante del front); lo lee la **validación documental
automática**, que lo recibe en su contexto y donde **manda sobre su criterio
genérico**. Si cambia el contrato, sube `esquema` y revisa a los dos consumidores.

Vive en el campo `document_spec` del mandante. Es texto libre con un encabezado
estructurado adelante.

---

## Encabezado de evidencia

Todo `document_spec` arranca con esta línea:

```
> esquema: v1 · evidencia: historico · n: 371 · medido: 2026-09-02 · ventana: 30d
```

| clave | qué es |
|---|---|
| `esquema` | La versión de **este contrato**. Hoy, `v1`. No la emite el modelo: la estampa quien guarda. |
| `evidencia` | `historico` (se midió contra guías reales cruzadas con sus viajes) o `muestras` (se describió sobre 2–3 documentos aportados, sin medir). |
| `n` | Cuántos documentos respaldan la afirmación. |
| `medido` | Fecha de la medición. Con `evidencia: muestras`, `—`. |
| `ventana` | Qué período del histórico se midió. Solo con `evidencia: historico`. |

**El encabezado es una barrera, no un comentario.** La validación corre sin humano al
lado: con `evidencia: muestras`, **ninguna bandera de cruce aplica** aunque esté
prendida. Sin encabezado se asume sin evidencia. Por eso no se escribe de memoria ni
se omite, y por eso la barrera se aplica del lado de la política y no del criterio del
modelo — una convención se puede olvidar, una barrera no.

`esquema` no se toca al corregir la prosa; `medido`, `n` y `evidencia` se actualizan
cada vez que se vuelve a medir.

---

## La prosa

Tres partes, en este orden, y **se tiene que poder leer de corrido sin haber visto el
papel**:

**1 · Cómo se reconoce este documento.** Título impreso, nombre del emisor, y la
forma general (cuántas columnas, si son una entrega o varias, si hay algo que lo
distinga de otro formulario del mismo mandante).

**2 · Dónde está cada dato.** Una línea por identificador: **dónde** está, con **qué
rótulo exacto** (entre comillas, con las palabras del documento) y un **ejemplo** del
valor. Un identificador que no aparece **se dice que no aparece** — eso significa que
no sirve para este formato, y dejarlo en blanco se lee como que faltó mirar.

**3 · Particularidades del formulario.** Lo que confunde y lo que la operación no
produce: que no hay tabla de productos sino una lista de guías, que el origen viene
manuscrito o no viene, que la entrega se acredita con timbre y no con firma. Esta
parte es la que evita rechazos injustos, y cada línea suele venir de un caso real.

**4 · Dudas abiertas.** Lo que no se pudo determinar, **como pregunta concreta** y con
quién la resuelve. Si no hay ninguna, "Ninguna".

## Cómo se escribe

**Para que lo corrija un jefe de operaciones**, el día que el mandante cambie su
formulario. No es un fragmento de prompt: es la descripción del papel, como se la
darías por teléfono a alguien que lo tiene en la mano.

> **Bien:** *"El folio va en el recuadro superior derecho, rotulado «N° documento
> Transporte»."*
> **Mal:** *"Extraer el campo numero_documento usando el sector superior derecho."*

Esa distinción es el motivo de existir del artefacto. Un texto escrito en el segundo
estilo solo lo puede mantener quien sepa de prompts, y entonces no lo mantiene nadie.

- **Reglas, no listas que cambian.** Dónde vive el folio en ese formulario, no la
  lista de folios vistos.
- **Nunca inventes** un rótulo, un ejemplo ni una ubicación. Lo cortado, borroso o
  tapado es duda.
- **Explícito sobre lo ausente.** Lo que el formulario no tiene, se dice.

## Ejemplo

```
> esquema: v1 · evidencia: historico · n: 371 · medido: 2026-09-02 · ventana: 30d

Este documento se reconoce por el título "Formulario Documento de transporte" en
la parte superior y el nombre del mandante en la esquina superior izquierda. Está
organizado en cuatro columnas verticales; en la práctica las cuatro corresponden
a la misma tienda y son grupos de guías de una misma entrega.

- Número de documento: esquina superior izquierda, bajo el nombre de la empresa,
  rotulado "N° documento Transporte". Ejemplo: 576115.
- Código del viaje: estampado dentro de cada columna, en la casilla "Sello
  Llegada". Empieza con T. Ejemplo: T00055718.
- Código de la tienda: parte superior de cada columna, rotulado "Destinatario".
  Ejemplo: E511.
- Patente: esquina superior derecha, en el campo "Tractor/Remolque".
- Conductor y RUT: parte inferior, rotulados "Conductor" y "RUT". El RUT es el de
  la persona, no el de la empresa del encabezado.
- Fecha: esquina superior derecha, rotulada "Fecha".
- Destino: el nombre completo de la tienda aparece dentro del timbre de
  "RECEPCIÓN" que estampa el local al recibir.

Particularidades:
- No tiene tabla de productos. Lista números de guías bajo el rótulo "Guías".
- El origen no viene impreso: aparece manuscrito cuando aparece.
- La entrega se acredita con el timbre de recepción del local, no con firma
  manuscrita. Pedir firma rechaza entregas correctas.

Dudas abiertas:
- ¿El número de "Sello Llegada" es el mismo en todas las guías de una entrega, o
  cambia por columna? — preguntar al mandante.
```

La línea del timbre salió de 44 rechazos falsos. Ese es el tipo de frase que hace que
este archivo valga la pena.
