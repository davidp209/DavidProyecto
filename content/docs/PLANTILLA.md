---
title: "Pipeline de Encuestas Mensuales"
tags: ["UT1", "RA1", "pipeline", "ETL", "pandas"]
version: "1.0.0"
owner: "equipo-alumno"
status: "published"
---

# 1. Objetivo
Construir un pipeline mínimo de datos que procese encuestas mensuales recibidas en formato Excel “humano” y las transforme en datos limpios, estructurados y listos para análisis.

El objetivo es automatizar el flujo:
**Ingesta → Limpieza/Modelado → Almacenamiento → Reporte**,  
garantizando trazabilidad, control de calidad y generación de KPIs básicos.

---

# 2. Alcance
## Cubre
- Ingesta semanal (batch) de archivos `encuestas_YYYYMM.xlsx` desde `data/raw/`.
- Limpieza, normalización y validación de dominios:
  - Mapeo `NS/NC` → nulo.
  - Dominio `satisfacción ∈ [1,10]`.
- Modelado y almacenamiento:
  - CSV homogéneo (`data/drops/`).
  - Parquet limpio (`data/clean/`).
  - Base de datos SQLite (`data/sqlite/raw_encuestas.db`).
- Reporte Markdown con distribución y evolución mensual.
- Informe de calidad en Excel con conteos de errores.

## No cubre
- Dashboards visuales (sin gráficos).
- APIs de ingestión en tiempo real.
- Persistencia histórica de todos los lotes (solo el más reciente).

---

# 3. Decisiones / Reglas
- **Estrategia de ingestión:** batch semanal, lectura desde Excel y conversión a CSV homogéneo.
- **Clave natural:** `id_respuesta`.
- **Idempotencia:** el pipeline puede ejecutarse múltiples veces sin duplicar registros (reemplazo de tablas y archivos).
- **Validaciones:**
  - Coerción de tipos (`fecha` → datetime, `edad` → entero, `satisfacción` → numérico).
  - Valores nulos reconocidos (`NS/NC`, “No sabe”, “No contesta”).
  - Dominio de `satisfacción`: valores fuera de rango se aíslan en *quarantine*.
- **Reglas de negocio:**
  - `edad` puede ser nula.
  - `satisfacción` fuera de rango → quarantine.
  - Columnas opcionales se crean si faltan en la fuente.

---

# 4. Procedimiento / Pasos

### 1️⃣ Crear datos de ejemplo
```bash
python project/ingest/get_data.py
python project/ingest/run.py

ℹ️ Archivo drops previo eliminado: data\drops\2025-01-31\encuestas_202501.csv
✅ Convertido encuestas_202501.xlsx → data\drops\2025-01-31\encuestas_202501.csv
ℹ️ Archivo de salida previo eliminado: output\parquet\raw_encuestas.parquet
ℹ️ Archivo de salida previo eliminado: output\parquet\clean_encuestas.parquet
ℹ️ Archivo de salida previo eliminado: output\parquet\quarantine_encuestas.parquet
✅ Encuestas RAW: output\parquet\raw_encuestas.parquet
✅ Encuestas limpias: output\parquet\clean_encuestas.parquet
⚠️ Encuestas en cuarentena: output\parquet\quarantine_encuestas.parquet
ℹ️ Generando reporte markdown...
✅ Reporte generado en: output\reporte.md
Total filas: 10000 · Buenas: 9420 · Cuarentena: 580

# 5. Evidencias
![[Pasted image 20251109225756.png]]

# 6. Resultados
```
- Ve a tu carpeta `output/` y abre el archivo `reporte.md`.
  
	- **KPIs:** `CSAT Promedio (1-10): 8.12`
	- **Métricas calculadas:** La tabla de "CSAT por Área" y "Resumen por Día".
	- **Resumen de hallazgos:** `Titular: CSAT promedio 8.12 con 9,420 respuestas válidas.`
```
  

# 7. Lecciones aprendidas

```
## Qué salió bien
- La **separación `clean` / `quarantine`** funciona perfectamente. Permite analizar los datos buenos (`clean`) mientras se auditan los malos (`quarantine`).
- La **normalización de texto** en `area` (minúsculas, sin tildes, espacios) es crucial para unificar categorías (ej. "Atencion" y "atención").
- El **fallback a CSV** en `run.py` (Paso 3) si `pyarrow` no está instalado es una excelente práctica defensiva.

## Qué mejorar
- **Lógica de `drops` frágil**: El script `run.py` (Paso 0) asume que el mes (ej. "202501") siempre termina el día "31" al crear la carpeta `drops/2025-01-31/`. Esto es un bug y fallará para febrero, abril, etc.
- **Limpieza de `comentario` agresiva**: El (Paso 2) de `run.py` **elimina *todos* los espacios** (`\s+` -> `""`), lo que resulta en texto como `Mal serviciotodo pegado`. Debería normalizar a un solo espacio, como se hace con `area`.
- **Sin deduplicación**: El pipeline no previene la carga de `id_respuesta` duplicados.
```
