# Lecciones aprendidas

## Qué salió bien

- La **separación `clean` / `quarantine`** funciona perfectamente. Permite analizar los datos buenos (`clean`) mientras se auditan los malos (`quarantine`).
- La **normalización de texto** en `area` (minúsculas, sin tildes, espacios) es crucial para unificar categorías (ej. "Atencion" y "atención").
- El **fallback a CSV** en `run.py` (Paso 3) si `pyarrow` no está instalado es una excelente práctica defensiva.
- El script `get_data.py` simula un escenario real de forma muy efectiva (nulos, texto en numéricos, valores fuera de rango).

## Qué mejorar

- **Lógica de `drops` frágil**: El script `run.py` (Paso 0) asume que el mes (ej. "202501") siempre termina el día "31" al crear la carpeta `drops/2025-01-31/`. Esto es un bug y fallará para febrero, abril, etc.
- **Limpieza de `comentario` agresiva**: El (Paso 2) de `run.py` **elimina _todos_ los espacios** (`\s+` -> `""`), lo que resulta en texto como `Mal serviciotodo pegado`. Debería normalizar a un solo espacio, como se hace con `area`.
- **Sin deduplicación**: El pipeline no previene la carga de `id_respuesta` duplicados si vinieran en dos ficheros fuente distintos en la misma ejecución.

## Siguientes pasos

- **Corregir el bug** de la fecha en `run.py` (Paso 0) para que calcule el último día real del mes.
- **Ajustar la regex** de limpieza de `comentario` para que normalice espacios (como `area`) en lugar de eliminarlos.
- **Implementar** un paso de deduplicación por `id_respuesta` (ej. `drop_duplicates(subset=['id_respuesta'], keep='last')`) antes de la validación.

