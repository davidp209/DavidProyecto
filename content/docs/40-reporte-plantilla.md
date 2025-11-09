# Reporte de Calidad y Satisfacción (Ene-2025)

> **Titular**: **CSAT Ene-2025: 8.1** (NPS: +35). Foco en 'Soporte' (7.2). **5.8%** de datos en cuarentena por errores de entrada.

## 1) Métricas clave de Satisfacción

- **CSAT Promedio**: **8.1**
- **NPS**: **+35** (Promotores: 50% / Pasivos: 30% / Detractores: 15%)
- **Respuestas Válidas**: **9,420** (vs. 10,000 procesadas)

## 2) Contribución por producto

|   Área    | CSAT Promedio | Respuestas |
| :-------: | :-----------: | :--------: |
|  Ventas   |      8.8      |   2,350    |
| Postventa |      8.5      |    950     |
| Atención  |      8.1      |   3,120    |
|  Soporte  |      7.2      |   3,000    |

## 3) Evolución diaria

- El CSAT se mantuvo estable la primera quincena.
- **Pico (8.9)**: 15-Ene (coincide con promoción).
- **Valle (7.0)**: 22-Ene (caída reportada en 'Soporte').

## 4) Calidad de datos
- **Filas procesadas**: 10,000
- **Filas Limpias (Clean)**: 9,420 (94.2%)
- **Filas en Cuarentena (Quarantine)**: 580 (5.8%)
- **Motivos principales de quarantine**:
	- **Edad inválida**: 5.5% (incluye 5.0% nulos y 0.5% edades negativas).
    - **Satisfacción inválida**: 4.0% (incluye 3.0% "NS/NC" y 1.0% fuera de rango "12"). _(Nota: una fila puede tener múltiples errores)_

## 5) Próximos pasos
- **Analizar** los `comentarios` de 'Soporte' (CSAT 7.2) para identificar la causa raíz.
- **Investigar** el origen de las entradas de `edad` negativas en el sistema fuente.
