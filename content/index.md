---
title: "Inicio | Proyecto Pipeline de Datos (UT1)"
---

# 🚀 Proyecto UT1: Pipeline de Datos de Encuestas

Bienvenido al sitio de documentación y resultados del **Proyecto de Ingesta y Reporte (UT1)**.

> Este proyecto implementa un pipeline ETL completo y reproducible. El proceso transforma ficheros "sucios" de encuestas (Excel) en un conjunto de datos limpio (Parquet), separando los registros erróneos en cuarentena y generando un reporte de KPIs (CSAT) listo para el análisis.

---

## 🏛️ Explorar el Proyecto

Aquí encontrarás los artefactos más importantes del proyecto.

### 📊 El Resultado Principal: Reporte de KPIs

Este es el informe final generado automáticamente por el pipeline, con el análisis de satisfacción (CSAT) por área y el resumen de calidad de datos.

> [!TIP] Ver el Reporte de KPIs
> **Ir al reporte → [[reporte/reporte |Reporte de Satisfacción (Encuestas)]]**

---

### 🧠 Documentos de Diseño

Estas notas documentan las decisiones de arquitectura y limpieza que se tomaron para construir el pipeline.

* **[[docs/10-diseno-ingesta|1. Diseño de Ingestión]]**: Cómo entran los datos (batch, trazabilidad, etc.).
* **[[docs/20-limpieza-calidad|2. Reglas de Limpieza y Calidad]]**: Criterios para `clean` vs. `quarantine`.
* **[[docs/30-modelado-oro|3. Modelado (KPIs)]]**: Definición de las métricas clave (CSAT).
* **[[docs/99-lecciones-aprendidas|4. Lecciones Aprendidas]]**: Retrospectiva del proyecto.

---

### 🧑‍💻 Código Fuente

El código completo del pipeline (Python) y de este sitio (Quartz) está disponible en el repositorio.

> [!NOTE] Ver el Código
> **[Ir al repositorio en GitHub →](https://github.com/davidp209/DavidProyecto)**