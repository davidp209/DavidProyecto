# BDA_Proyecto_UT1_RA1 · Ingesta y Reporte de Encuestas

Versión limpia y reproducible del pipeline de la Unidad de Trabajo 1 (UT1). Incluye:

- `project/` — Código Python: generación de datos, ingesta, limpieza/validación y reporte.
- `site/` — Sitio web (Quartz) con la documentación y los reportes (como submódulo).

---

## ✨ Resumen rápido

Este repositorio realiza un pipeline medallion simple:

- Bronce (raw): `project/data/raw/encuestas_*.xlsx` (origen)
- Plata (clean): `project/output/parquet/clean_encuestas.parquet` (datos limpios listos para análisis)
- Oro (reporte): `project/output/reporte.md` (informe generado en Markdown)

Además el resultado se publica en la web de `site/` (Quartz → GitHub Pages).

## � Requisitos

- Python 3.8+
- Recomendado: `pyarrow` para Parquet
- Node.js + `npx` para ejecutar Quartz (si trabajas con el sitio)

**Instala dependencias** Python desde el fichero de requirements:

```powershell
# crear/activar entorno (Windows PowerShell)
python -m venv .venv; .\.venv\Scripts\Activate.ps1
# Instalar librerías
pip install -r project/requirements.txt
```

Si vas a trabajar con el sitio (`site/`) necesitas Node.js. Para servir localmente Quartz:

```powershell
npx quartz build --serve
```

Si `npx quartz build --serve` no abre en localhost revisa el puerto y logs; verás ayuda en la sección *Solución de problemas* abajo.

## 🚀 Uso (pipeline local)

1. Generar datos de ejemplo (opcional):

```powershell
python project/ingest/get_data.py
```

2. Ejecutar la ingesta y generar artefactos:

```powershell
python project/ingest/run.py
```

Salida principal:

- `project/output/parquet/clean_encuestas.parquet` — parquet limpio
- `project/output/sql/encuestas.db` — sqlite con tablas raw/clean/quarantine
- `project/output/encuestas_dump.sql` — volcado SQL (puede comprimirse)
- `project/output/reporte.md` — reporte en Markdown

## 🖥️ Servir y probar el sitio (Quartz)

El directorio `site/` contiene la web (submódulo). Para servir localmente:

```powershell
cd site
npx quartz build --serve
# abre http://localhost:3000 (o el puerto que indique el log)
```

Si no ves nada en `http://localhost:3000`:

- Revisa los logs de `npx quartz build --serve` (errores de compilación o puerto ocupado).
- Asegúrate de estar en la carpeta `site/` donde está el proyecto Quartz.
- Si el submódulo tiene cambios pendientes, comprueba `git status` dentro de `site/`.

## 🧰 Estructura del repo

```
README.md
project/
	ingest/    # scripts: get_data.py, run.py
	requirements.txt
	data/raw/  # ficheros de entrada (drops/)
	output/    # parquet, sql, reporte.md
site/        # sitio Quartz (submódulo)
```

## 🛠️ Solución de problemas comunes

- `sqlite3.OperationalError: unable to open database file` → Asegúrate de que `project/output/sql/` existe. El script crea la carpeta `output/sql` automáticamente, pero verifica permisos en Windows.
- `npx quartz build --serve` no responde → comprueba puerto y logs, y que Node.js esté instalado. En PowerShell ejecuta:

```powershell
# ver procesos que usan puertos (ej. 3000)
netstat -ano | Select-String ":3000"
```

- Submódulo `site/` marcado como modificado en `git status` → si hiciste cambios dentro de `site/`, commítalos y púshalos en el subrepositorio antes de actualizar el puntero del superproyecto.

## ✅ Consejos y buenas prácticas

- Usa Parquet con compresión (snappy/zstd) para ahorrar espacio y mejorar I/O.
- Mantén la lógica de reporte separada (por ejemplo `project/report/generate_report.py`) y haz que `run.py` la invoque.
- Comprime el dump SQL (`.sql.gz`) si lo vas a almacenar.

## Licencia

Este repositorio se entrega como material docente. Reutiliza/redistribuye con atribución.
