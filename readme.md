# Pipeline de «Descompilando el mundo»

Este proyecto transforma `Lo_que_continua_indice.md` en tres ediciones:

- `Descompilando_el_mundo.epub`, un EPUB 3 con portada, metadatos, tabla de contenido e índice enlazado.
- `output/pdf/Descompilando_el_mundo.pdf`, una edición PDF paginada, con marcadores, portada e índice enlazado.
- `Descompilando_el_mundo.html`, una edición web autocontenida, navegable y adaptable a móvil.

El manuscrito original no se modifica. Los archivos `Lo_que_continua_indice.normalized.md` y `sections/` son artefactos intermedios regenerables.

## Requisitos

- Python 3.10 o posterior.
- Conexión a Internet sólo durante la instalación inicial de dependencias.

La única dependencia externa está declarada en `requirements.txt`.

## Ejecución exacta en Windows PowerShell

Abrir PowerShell en esta carpeta y ejecutar, en este orden:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_pipeline.py
```

Al terminar deben existir:

```text
Descompilando_el_mundo.epub
output/pdf/Descompilando_el_mundo.pdf
Descompilando_el_mundo.html
```

Para abrir la edición web mediante un servidor local:

```powershell
.\.venv\Scripts\python.exe serve_web.py
```

El navegador abrirá `http://127.0.0.1:8432/Descompilando_el_mundo.html`. Para detener el servidor, presionar `Ctrl+C`. El HTML también se puede abrir directamente con doble clic porque lleva incorporados el texto, los estilos, el JavaScript y la portada. En la cabecera aparecen los botones `Descargar EPUB` y `Descargar PDF`; por eso los tres archivos deben conservar su estructura de carpetas.

Después de editar `Lo_que_continua_indice.md`, no hace falta recrear el entorno ni reinstalar dependencias. Sólo hay que ejecutar:

```powershell
.\.venv\Scripts\python.exe run_pipeline.py
```

## Qué ejecuta `run_pipeline.py`

La secuencia interna es estrictamente ésta:

1. `normalize_md.py`: normaliza codificación y saltos de línea, sin reescribir la estructura del manuscrito.
2. `split_md.py`: separa índice, apertura, partes, 50 capítulos, 6 interludios, epílogo y 5 apéndices; luego crea `sections/manifest.json`.
3. `build_index_links.py`: enlaza las 73 entradas navegables del índice con sus secciones.
4. `md2epub_sugerido.py`: genera el EPUB 3 usando `cover.jpg`.
5. `build_pdf.py`: genera y valida el PDF, sus metadatos, paginación y marcadores internos.
6. `build_web.py`: genera un único HTML offline, adapta los enlaces EPUB a anclas web y agrega las descargas EPUB/PDF.
7. El propio orquestador valida el ZIP EPUB, todos sus XML/XHTML, el número de secciones, los enlaces internos de la web y la existencia de ambos descargables.

Si una etapa falla, el proceso termina con un mensaje y no informa el pipeline como completado.

## Metadatos y nombres de salida

Por defecto se usa:

```text
Título: Descompilando el mundo
Autoría: Miyu Rory Schrank y Vera
Idioma: es
Portada: cover.jpg
```

El título se toma automáticamente del primer encabezado `#` del manuscrito. La autoría y las rutas de salida se pueden cambiar al ejecutar el orquestador:

```powershell
.\.venv\Scripts\python.exe run_pipeline.py `
  --author "Nombre de autoría" `
  --epub-out "otra_edicion.epub" `
  --pdf-out "output/pdf/otra_edicion.pdf" `
  --html-out "otra_edicion.html"
```

También están disponibles `--title`, `--source` y `--cover`. Para ver todas las opciones:

```powershell
.\.venv\Scripts\python.exe run_pipeline.py --help
```

## Ejecución manual de las etapas

Normalmente conviene usar `run_pipeline.py`, porque además verifica los resultados. Para depurar una etapa concreta, la secuencia equivalente es:

```powershell
.\.venv\Scripts\python.exe normalize_md.py
.\.venv\Scripts\python.exe split_md.py
.\.venv\Scripts\python.exe build_index_links.py
.\.venv\Scripts\python.exe md2epub_sugerido.py --sections sections --title "Descompilando el mundo" --author "Miyu Rory Schrank y Vera" --lang es --cover cover.jpg --out Descompilando_el_mundo.epub
.\.venv\Scripts\python.exe build_pdf.py --sections sections --title "Descompilando el mundo" --author "Miyu Rory Schrank y Vera" --cover cover.jpg --out output/pdf/Descompilando_el_mundo.pdf
.\.venv\Scripts\python.exe build_web.py --sections sections --title "Descompilando el mundo" --author "Miyu Rory Schrank y Vera" --cover cover.jpg --out Descompilando_el_mundo.html
```

## Linux o macOS

La misma secuencia usa el ejecutable del entorno virtual de esta forma:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python run_pipeline.py
./.venv/bin/python serve_web.py
```
