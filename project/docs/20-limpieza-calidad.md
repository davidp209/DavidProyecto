# Reglas de limpieza y calidad

## Tipos y formatos

- `fecha`: `datetime`. Se coacciona con `pd.to_datetime(..., errors="coerce")`.
- `edad`: `float` (para permitir `NaN`). Se coacciona con `pd.to_numeric(..., errors="coerce")`.
- `satisfaccion`: `float` (para permitir `NaN`). Se coacciona con `pd.to_numeric(..., errors="coerce")`.
- `satisfaccion` (lógica): Valores de texto ("NS/NC", "No sabe", etc.) se fuerzan a `NaN` durante la coerción numérica y luego se envían a cuarentena.

## Nulos

- **Campos obligatorios:** `edad` y `satisfaccion` son funcionalmente obligatorios. Si son `NaN` (ya sea originalmente, o por coerción de "NS/NC"), la fila no pasará la validación de rangos.
- **Tratamiento:** Las filas inválidas (incluyendo las que tienen nulos en campos obligatorios) se mueven a **quarantine**.

## Rangos y dominios

- `edad`: Debe estar en el rango `[18, 65]`. (Valores negativos o < 18 van a cuarentena).
- `satisfaccion`: Debe estar en el rango `[1, 10]`. (Valores fuera de rango, como el `12` generado, o los `NaN` de "NS/NC", van a cuarentena).

## Deduplicación

- **Clave natural:** `id_respuesta`.
- **Política:** No se aplica (ver `[[10-diseno-ingesta]]`).

## Estandarización de texto

- `area`:
    1. `fillna("")`
    2. `unidecode` (quita tildes).
    3. `str.replace(r"\s+", " ", regex=True)` (normaliza espacios múltiples).
    4. `str.strip()` (quita espacios al inicio/final).
    5. `str.lower()` (minúsculas).
- `comentario`:
    1. `fillna("")`
    2. `unidecode` (quita tildes).
    3. `str.replace(r"\s+", "", regex=True)` (**Elimina TODOS los espacios**, juntando palabras).
    4. `str.lower()` (minúsculas).

## Trazabilidad

- Se mantienen `_ingest_ts` y `_source_file` en las salidas `clean` y `quarantine`.
