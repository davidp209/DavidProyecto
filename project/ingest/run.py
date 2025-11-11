from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import sqlite3
import unidecode

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
DROPS = DATA / "drops"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "parquet").mkdir(parents=True, exist_ok=True)
# Crear carpeta para artefactos SQL (DB + dump)
(OUT / "sql").mkdir(parents=True, exist_ok=True)


# --------------------------
# 0) Convertir Excel de raw a CSV en drops automáticamente
# --------------------------
excel_files = RAW.glob("encuestas_*.xlsx")
for excel_file in excel_files:
    df_excel = pd.read_excel(excel_file, engine="openpyxl")
    # Crear carpeta drops con fecha
    fecha_str = excel_file.stem.split("_")[1]  # "202501"
    carpeta_drops = DROPS / f"{fecha_str[:4]}-{fecha_str[4:]}-31"
    carpeta_drops.mkdir(parents=True, exist_ok=True)
    csv_file = carpeta_drops / f"{excel_file.stem}.csv"
    # Si existe un CSV anterior para este Excel, eliminarlo primero para recrearlo limpio
    try:
        if csv_file.exists():
            csv_file.unlink()
            print(f"ℹ️ Archivo drops previo eliminado: {csv_file}")
    except Exception as e:
        print(f"⚠️ No se pudo eliminar el drops previo ({csv_file}): {e}")

    df_excel.to_csv(csv_file, index=False)
    print(f"✅ Convertido {excel_file.name} → {csv_file}")

# --------------------------
# 1) Ingestión
# --------------------------
ENCUESTA_DATA = DROPS.glob("**/encuestas_*.csv")
encuestas = []
for f in ENCUESTA_DATA:
    df = pd.read_csv(f, dtype=str)
    df["_source_file"] = f.name
    df["_ingest_ts"] = datetime.now(timezone.utc).isoformat()
    # Coerción de tipos básicos
    df["fecha"] = pd.to_datetime(df.get("fecha"), errors="coerce")
    df["edad"] = pd.to_numeric(df.get("edad"), errors="coerce")
    df["satisfaccion"] = pd.to_numeric(df.get("satisfaccion"), errors="coerce")
    # NS/NC → NaN (evitar chained-assignment/inplace)
    df["satisfaccion"] = df["satisfaccion"].replace({"NS/NC": None, "No sabe": None, "No contesta": None})
    encuestas.append(df)

if encuestas:
    df_encuestas = pd.concat(encuestas, ignore_index=True)
else:
    df_encuestas = pd.DataFrame(columns=[
        "id_respuesta","fecha","edad","area","satisfaccion","comentario","_source_file","_ingest_ts"
    ])
    
df_encuestas = df_encuestas.drop_duplicates(subset=['id_respuesta'], keep='last')

# --------------------------
# 2) Limpieza y validación
# --------------------------
# Trim y quitar tildes para 'area' (normalizar espacios)
if "area" in df_encuestas.columns:
    df_encuestas["area"] = (
        df_encuestas["area"]
        .fillna("")
        .astype(str)
        .apply(unidecode.unidecode)
        .str.replace("\u00A0", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.lower()

    )

# Para 'comentario' concatenar todo: eliminar cualquier espacio/tab/salto de línea (dejamos todo junto)
if "comentario" in df_encuestas.columns:
    df_encuestas["comentario"] = (
        df_encuestas["comentario"]
        .fillna("")
        .astype(str)
        .apply(unidecode.unidecode)
        # eliminar NBSP explícitamente
        .str.replace("\u00A0", "", regex=False)
        # eliminar cualquier whitespace (espacios, tabs, newlines) dejando todo junto
        .str.replace(r"\s+", "", regex=True)
        # pasar a minúsculas
        .str.lower()
    )

# Filtrado de filas válidas
valid = (
    df_encuestas["edad"].between(18, 65) &
    df_encuestas["satisfaccion"].between(1, 10)
)

clean = df_encuestas[valid].copy()
quarantine = df_encuestas[~valid].copy()

# --------------------------
# 3) Persistencia
# --------------------------

clean_file = OUT / "parquet" / "clean_encuestas.parquet"
# Queremos: mantener sólo parquet para los datos limpios. Los datos raw y
# cuarentena se persistirán en una base SQLite y se exportará un volcado SQL
db_file = OUT / "sql" / "encuestas.db"
sql_dump = OUT / "sql" / "encuestas_dump.sql"

# Eliminar artefactos de salida previos relevantes (sin try/except)
for old in (clean_file, clean_file.with_suffix('.csv'), db_file, sql_dump):
    if old.exists():
        old.unlink()
        print(f"ℹ️ Archivo de salida previo eliminado: {old}")

# 1) Escribir solo el parquet de clean (sin manejo de excepciones aquí)
clean.to_parquet(clean_file, index=False)
print(f"✅ Encuestas limpias (parquet): {clean_file}")

# 2) Persistir raw (df_encuestas), clean y quarantine en SQLite y generar volcado SQL
conn = sqlite3.connect(str(db_file))
# Escribir tablas: raw_encuestas, clean_encuestas, quarantine_encuestas
df_encuestas.to_sql("raw_encuestas", conn, if_exists="replace", index=False)
clean.to_sql("clean_encuestas", conn, if_exists="replace", index=False)
quarantine.to_sql("quarantine_encuestas", conn, if_exists="replace", index=False)
conn.commit()


conn.close()
print(f"✅ Base SQLite creada: {db_file}")
print(f"✅ Volcado SQL creado: {sql_dump}")


# --------------------------
# 4) Generación de Reporte
# --------------------------
print("ℹ️ Generando reporte markdown...")
report_path = OUT / "reporte.md"
now_ts = datetime.now(timezone.utc).isoformat()

# --- Fallback si 'clean' está vacío ---
if clean.empty:
    print("⚠️ No hay datos limpios (clean) para generar el reporte.")
    report_content = f"""# Reporte UT1 · Encuestas de Satisfacción
**Periodo:** N/A · **Fuente:** clean_encuestas (Parquet) · **Generado:** {now_ts}

## 1. Titular
**ERROR: No se encontraron datos limpios (clean) para generar el reporte.**

## 5. Calidad y cobertura
- Filas totales ingeridas: {len(df_encuestas):,}
- Filas limpias (plata): 0
- Filas en cuarentena: {len(quarantine):,}
"""
# --- Generación normal del reporte ---
else:
    # Calcular KPIs
    period_start = clean["fecha"].min().strftime("%Y-%m-%d")
    period_end = clean["fecha"].max().strftime("%Y-%m-%d")
    total_raw = len(df_encuestas)
    total_clean = len(clean)
    total_quar = len(quarantine)
    csat_avg = clean["satisfaccion"].mean()
    total_respuestas = len(clean)

    # 3. CSAT por Área (Puntuacion de satisfaccion del cliente )
    csat_by_area = clean.groupby("area")["satisfaccion"] \
        .agg(csat_promedio='mean', respuestas='count') \
        .sort_values(by="csat_promedio", ascending=False)
    
    md_table_area = csat_by_area.to_markdown(floatfmt=",.2f")

    # 4. Resumen por Día
    daily_summary = clean.groupby(clean['fecha'].dt.date)["satisfaccion"] \
        .agg(csat_promedio='mean', respuestas='count')
    daily_summary.index.name = "fecha"
    
    md_table_daily = daily_summary.to_markdown(floatfmt=",.2f")

    # Construir el reporte
    report_content = f"""# Reporte UT1 · Encuestas de Satisfacción
**Periodo:** {period_start} a {period_end} · **Fuente:** clean_encuestas (Parquet) · **Generado:** {now_ts}

## 1. Titular
CSAT promedio **{csat_avg:.2f}** con **{total_respuestas:,}** respuestas válidas.

## 2. KPIs
- **CSAT Promedio (1-10):** {csat_avg:.2f}
- **Total Respuestas Válidas:** {total_respuestas:,}
- **Respuestas en Cuarentena:** {total_quar:,}

## 3. CSAT por Área
{md_table_area}

## 4. Resumen por Día (CSAT y Volumen)
{md_table_daily}

## 5. Calidad y cobertura
- Filas totales ingeridas: {total_raw:,}
- Filas limpias (plata): {total_clean:,}
- Filas en cuarentena: {total_quar:,}

## 6. Persistencia
- Parquet (Clean): {clean_file}
- SQLite (DB): {db_file}
- SQL Dump: {sql_dump}

## 7. Conclusiones
- Revisar áreas con bajo CSAT (si aplica).
- Auditar las {total_quar} filas en cuarentena para identificar problemas de origen.
"""

# --- Escribir el archivo ---
try:
    report_path.write_text(report_content, encoding="utf-8")
    print(f"✅ Reporte generado en: {report_path}")
except Exception as e:
    print(f"‼️ No se pudo generar el reporte: {e}")