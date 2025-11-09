from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --------------------------
# CONFIGURACIÓN
# --------------------------
BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
OUT = BASE / "output"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "parquet").mkdir(parents=True, exist_ok=True)

N = 10000
MES = "2025-01"
FILE_NAME = f"encuestas_{MES.replace('-', '')}.xlsx"
excel_path = RAW / FILE_NAME

# --------------------------
# SEMILLAS Y PARÁMETROS
# --------------------------
random.seed(42)
np.random.seed(42)

areas = ["Atención", "Soporte", "Ventas", "Postventa"]
comentarios_pos = ["Excelente", "Muy bien", "Rápido", "Amables", "Todo correcto"]
comentarios_neg = ["Demora", "Mal servicio", "No resolvieron", "Regular", "Poco claro"]

# Fechas del mes (1–31)
fechas = pd.date_range(start="2025-01-01", end="2025-01-31")

# --------------------------
# GENERACIÓN DE DATOS
# --------------------------
ids = [f"R{i:05d}" for i in range(1, N + 1)]
fechas_respuesta = np.random.choice(fechas, size=N)

# Edades (18–65), con 5% nulas
edades = np.random.randint(18, 66, size=N).astype("float")
mask_null_edad = np.random.rand(N) < 0.05
edades[mask_null_edad] = np.nan

# Introducir algunos valores negativos como datos erróneos/anómalos (0.5%)
# Esto simula entradas inválidas en la columna de edad
mask_neg = np.random.rand(N) < 0.005
if mask_neg.sum() > 0:
    # edades negativas entre -1 y -99
    neg_vals = -np.random.randint(1, 100, size=mask_neg.sum())
    edades[mask_neg] = neg_vals

# Áreas aleatorias
areas_respuesta = np.random.choice(areas, size=N, p=[0.35, 0.3, 0.25, 0.1])

# Satisfacción base (1–10)
satisfaccion = np.random.randint(1, 11, size=N).astype("object")

# Introducir ruido:
#  - 3% “NS/NC”
#  - 1% fuera de dominio (12)
mask_ns = np.random.rand(N) < 0.03
mask_out = np.random.rand(N) < 0.01
satisfaccion[mask_ns] = "NS/NC"
satisfaccion[mask_out] = 12

# Comentarios aleatorios
comentarios = []
for s in satisfaccion:
    if isinstance(s, str) and s == "NS/NC":
        comentarios.append("")
    elif isinstance(s, (int, np.integer)) and s >= 8:
        comentarios.append(random.choice(comentarios_pos))
    else:
        # 50% chance of comment for others
        comentarios.append(random.choice(comentarios_neg) if random.random() < 0.5 else "")

# --------------------------
# CONSTRUIR DATAFRAME
# --------------------------
df = pd.DataFrame({
    "id_respuesta": ids,
    "fecha": fechas_respuesta,
    "edad": edades,
    "area": areas_respuesta,
    "satisfaccion": satisfaccion,
    "comentario": comentarios
})

# --------------------------
# GUARDAR ARCHIVO EXCEL
# --------------------------
# Si existe un archivo previo, eliminarlo para recrearlo desde cero
try:
    if excel_path.exists():
        excel_path.unlink()
        print(f"ℹ️ Archivo existente eliminado: {excel_path}")
except Exception as e:
    print(f"⚠️ No se pudo eliminar el archivo existente ({excel_path}): {e}")

df.to_excel(excel_path, index=False, engine="openpyxl")
print(f"✅ Archivo de ejemplo creado con {len(df):,} registros en:\n   {excel_path}")
