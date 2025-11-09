# Diseño de ingestión

## Resumen

El pipeline ingiere ficheros de encuestas en un proceso **batch**. Lee los archivos fuente (`.xlsx`), los convierte a un formato intermedio (`.csv` en `drops`), y luego los carga en memoria, aplicando tipos y añadiendo metadatos de trazabilidad.

## Fuente

- **Origen:** `data/raw/encuestas_*.xlsx`. El script `run.py` los procesa y los convierte a `data/drops/YYYY-MM-DD/encuestas_*.csv`, que es la fuente real de la ingestión.
- **Formato:** CSV (convertido desde Excel).
- **Frecuencia:** Batch (ejecución manual bajo demanda).

## Estrategia

- **Modo:** `batch`.
- **Incremental:** Es un **full-refresh controlado**. El script `run.py` elimina explícitamente los ficheros Parquet/CSV de `output/` (Paso 3) y los CSV de `drops/` (Paso 0) antes de cada ejecución para evitar duplicados, procesando toda la data de origen cada vez.
- **Particionado:** La ingesta (Paso 0) crea una partición de "caída" (drop) basada en la fecha del fichero, ej: `data/drops/2025-01-31/`.

## Idempotencia y deduplicación

- **batch_id:** No se utiliza un ID de batch. La idempotencia se logra mediante la **eliminación de las salidas (outputs) previas** antes de la nueva escritura.
- **Clave natural:** `id_respuesta`
- **Política:** **No se aplica deduplicación** explícita por `id_respuesta` entre diferentes ficheros de origen. Si dos ficheros CSV en `drops/` contuvieran el mismo `id_respuesta`, ambos serían ingeridos.

## Checkpoints y trazabilidad

- **Checkpoints/offset:** No aplica (es batch).
- **Trazabilidad:** Se añaden las columnas:
	- `_source_file`: Nombre del fichero CSV de origen (ej. `encuestas_202501.csv`).
	- `_ingest_ts`: Timestamp (ISO UTC) de cuándo se ejecutó el script `run.py`.
- **DLQ/quarantine:** Los registros que fallan las reglas de negocio (Paso 2) se desvían a `output/parquet/quarantine_encuestas.parquet`.

## SLA

- **Disponibilidad:** No aplica (proceso manual).
- **Alertas:** No aplica.

## Riesgos / Antipatrones

- **Lógica de partición frágil:** El script (Paso 0) asume que todos los meses terminan en `"-31"` al crear la carpeta `drops`. Esto fallará para meses como febrero.
- **Falta de deduplicación:** El pipeline no protege contra `id_respuesta` duplicados si provienen de múltiples ficheros de origen en la misma ejecución.
