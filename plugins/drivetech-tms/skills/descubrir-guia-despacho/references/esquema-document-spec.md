# Anatomía del `document_spec` — contrato del artefacto

**Este archivo es el contrato del `document_spec`, no documentación de una sola
skill.** Lo escribe `descubrir-guia-despacho` (y, en su versión sin números, la
pantalla de creación de mandante del front); lo lee la **validación documental
automática**, que lo recibe en su contexto y donde **manda sobre su criterio
genérico**. Si cambia el contrato, sube `esquema` y revisa a los dos consumidores.

Vive en el campo `document_spec` **del mandante** cuando la cuenta es transportista y
cada cliente trae su formulario, o **de la cuenta** cuando es ella la que emite sus
guías y el formato es uno solo. Son dos niveles excluyentes; cuál corresponde lo
dicta la tool que guarda. Es texto libre con un encabezado estructurado adelante.

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

## Las reglas de lectura — son espejo, no originales

El `document_spec` lo pueden producir **dos superficies**: esta skill (con un agente
que mira el documento, repregunta y corrige con el usuario) y la pantalla de creación
de mandante de la plataforma, que corre una tarea de descubrimiento donde no hay nadie
del otro lado. **Las dos tienen que producir el mismo artefacto.**

Por eso estas reglas son un **espejo del contrato de esa tarea**
(`docs/simple-task-guide-spec-discovery.md` en drivetech-ia-agents, apéndice A), no
una versión propia. **Si cambian, cambian allá primero** y se replican acá. No las
reescribas en el `SKILL.md`: si las dos derivan, la spec del front y la de la skill
dejan de ser lo mismo y nadie se entera.

1. **Trabaja solo sobre lo que ves en el documento.** No supongas que otros documentos
   del mismo mandante traen campos que éste no trae, ni que los traen en el mismo
   lugar si acá no se ve.
2. **Las pistas del usuario tienen prioridad sobre tu lectura**: él conoce su
   operación y tú ves un papel. Úsalas para orientarte y confírmalas contra el
   documento. Si una pista **no coincide** con lo que ves, no elijas: dilo como duda,
   con las dos lecturas.
3. **Por cada identificador, di si aparece y dónde**, con el **rótulo exacto** que usa
   el documento y un **ejemplo** del valor. Si no aparece, dilo: es información útil y
   no una falla — significa que ese dato no sirve para cruzar en este formato.
4. **Marca como duda todo lo que no puedas determinar** con lo que tienes a la vista.
   Una duda escrita vale más que un supuesto: una persona la contesta en diez segundos
   y un supuesto equivocado se descubre meses después. Formúlala como **pregunta
   concreta**, no como advertencia vaga.
5. **Nunca inventes** un rótulo, un ejemplo ni una ubicación. Si algo está cortado,
   borroso o tapado, es duda.
6. **Si hay tabla de ítems**, di dónde empieza, cómo se reconoce dónde termina y qué
   columna es código, descripción, cantidad y precio. **Si no la hay, dilo
   explícitamente**: muchos formularios listan guías o bultos y no productos.
7. **Una estructura repetida en el formulario no significa que la operación la
   use.** Un papel con cuatro columnas de destinatario puede usarse siempre con una
   sola tienda, agrupando guías; uno con dos tablas puede llenar solo la primera.
   Desde un único documento eso **no se puede saber**. No lo escribas como regla del
   formulario: escríbelo como **duda**, con la pregunta concreta — *"¿son cuatro
   destinos distintos, o siempre el mismo con varias guías?"*. Una repetición escrita
   como regla hace leer mal todos los documentos que vengan después.
8. **La especificación es el texto principal** y el que se guarda. Completo y
   ordenado, y que se pueda leer de corrido sin haber visto el papel.

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
