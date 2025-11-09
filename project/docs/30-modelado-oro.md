
# Modelo de negocio (capa oro)

## Tablas oro

- **`Clean_encuestas`** (fuente): Granularidad **respuesta individual validada**.
- **`Kpi_area_diaria`** (agregada): Granularidad **día + área**.

## Métricas (KPI)

- **CSAT (Customer Satisfacción Score)**: `AVG(satisfaccion)` sobre `clean_encuestas`.
- **NPS (Net Promoter Score)**:
    - Promotores: % de respuestas con `satisfaccion` 9 o 10.
    - Detractores: % de respuestas con `satisfaccion` 1 a 6.
    - NPS = `% Promotores - % Detractores`.
- **Volumen de respuestas**: `COUNT(id_respuesta)`.
- **Tasa de cuarentena**: `COUNT(quarantine) / (COUNT(clean) + COUNT(quarantine))`.
## Supuestos

- `clean_encuestas` solo contiene datos validados (18-65 años, satisfacción 1-10).
- `area` está normalizada (minúsculas, sin tildes).

## Consultas base (SQL conceptual)
```sql
-- CSAT y Volumen por Área (Total)
SELECT
  area,
  AVG(satisfaccion) AS csat_promedio,
  COUNT(id_respuesta) AS total_respuestas
FROM
  clean_encuestas
GROUP BY
  area
ORDER BY
  csat_promedio DESC;

-- Evolución diaria del CSAT
SELECT
  DATE(fecha) AS dia,
  AVG(satisfaccion) AS csat_diario
FROM
  clean_encuestas
GROUP BY
  DATE(fecha)
ORDER BY
  dia;
```
