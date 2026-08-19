# Adapters de fuente — cómo normalizar cada formato a una tabla canónica

El objetivo de todos es el mismo: **una tabla limpia de columnas × filas, una
fila por viaje**, sobre la que se hace el mapeo (`esquema-perfil.md`). Extrae con
cuidado: un viaje perdido acá es un camión sin asignar mañana.

## Correo con tabla en el cuerpo

1. Trae el hilo con el conector de correo en texto plano; si el cuerpo viene como
   HTML pesado, extrae el `plaintextBody` o parsea la tabla del HTML.
2. Reconstruye la tabla: primera línea = encabezados, cada fila siguiente = un
   viaje. Ojo con celdas vacías que desalinean columnas.
3. **Varias tablas:** casi siempre son el mismo formato partido por una dimensión
   (tipo de camión, zona, ventana). Únelas en una sola tabla y **guarda de qué
   grupo venía cada fila** — esa dimensión suele ser una columna del mapeo
   (p.ej. el tipo de camión → `skills_required`).
4. Ignora el saludo, la firma y los recordatorios (aunque un recordatorio como
   "usar la app Drivin" puede ser algo que el mandante quiere que se repita al
   responder — anótalo en la sección 9 del perfil).

## Excel / CSV adjunto

Usa la skill **`xlsx`** para abrir el archivo.

1. **La hoja correcta** — un libro puede tener varias hojas; identifica la de los
   viajes (a veces hay hojas de resumen o parámetros).
2. **La fila de encabezado real** — rara vez es la primera; suele haber título,
   logo o filas en blanco arriba. Detecta la fila donde aparecen los nombres de
   columna.
3. **Descarta ruido** — filas de totales, subtotales, filas vacías, notas al pie.
4. **Tipos** — las fechas de Excel pueden venir como número de serie; conviértelas
   con cuidado. Las horas pueden venir como fracción de día. Verifica contra lo
   que se ve en la celda.
5. **CSV** — detecta el separador (`,` vs `;`, común en configuraciones en
   español) y la codificación (acentos). Confirma que las columnas no se
   corrieron por comas dentro de un campo.

## PDF adjunto

Usa la skill **`pdf`** para extraer.

1. **¿Nativo o escaneado?** Si tiene texto seleccionable, extrae las tablas
   directo. Si es una imagen escaneada, corre OCR primero y trátalo como texto
   sucio.
2. **Tablas** — los PDF exportados desde sistemas suelen tener tablas con líneas;
   extráelas preservando columnas. Si la tabla se parte entre páginas, únela.
3. **Valida el conteo** — los extractores de PDF se comen o duplican filas.
   Cuenta las filas extraídas contra las que se ven en el documento y cuadra
   antes de seguir.
4. **Campos partidos** — un destino largo puede envolver en dos líneas y romper
   la fila. Revisa las filas que quedaron cortas de columnas.

## Después de cualquier adapter

- **Muéstrale la tabla extraída al usuario** y confirma que están todas las
  filas y que las columnas quedaron donde corresponde, antes de mapear.
- Si el formato varió entre las muestras que te dieron, describe la variación en
  la sección 2 del perfil: la skill de carga tiene que reconocer las dos formas.
- Guarda un par de filas de ejemplo para el ejemplo JSON del mapeo (sección 3).
