# TrendML: versión 3, corrección del promedio histórico

14 de octubre de 2026. Jose Manuel Castro Reina · Grupo 14 · Docente Matias Arellano.

## Cambio y método

Se implementaron dos modelos que aprenden a corregir el promedio de ventas de cuatro semanas. Las entradas incluyen ventas recientes, media semanal de 56 días, frecuencia de días sin ventas en 28/56 días, variabilidad relativa, tendencia, precio y calendario. No se añadieron identificadores de producto como números ordinales; cada producto se caracteriza por su propio historial conocido.

Objetivo de entrenamiento: `(ventas siguientes 7 días − promedio 4 semanas)/(promedio 4 semanas + 1)`. Al inferir se reconstruyen unidades mediante `max(0, promedio + (promedio + 1) * corrección)`. Se pondera cada ejemplo por `promedio + 1`; en el boosting con pérdida absoluta esto recupera el peso del error en unidades. El recorte a cero impide ventas negativas.

Candidatos fijados antes de ejecutar: Random Forest residual (150 árboles, profundidad 8, mínimo 10 ejemplos por hoja) y HistGradientBoosting residual (pérdida absoluta, 100 iteraciones, 15 hojas, mínimo 20 ejemplos por hoja, regularización 1, sin early stopping aleatorio). Semilla 42; no hubo ajustes posteriores para mejorar noviembre.

## Comparación justa y límites

Se conserva la cohorte seleccionada al 1 de agosto de 2011. Se necesitan 56 días completos de historial y se descartan los primeros 55. La v2 se vuelve a entrenar sobre las mismas filas elegibles. Cada corte (1 de agosto, septiembre y octubre) usa solo objetivos ya conocidos y evalúa cuatro ventanas semanales. Son 120 casos de validación y 40 de comparación en noviembre. Las cifras de v2 pueden cambiar respecto de su experimento original por el recorte de entrenamiento.

**Todos estos períodos ya fueron consultados durante el desarrollo.** La elección entre candidatos usa agosto–octubre, antes de calcular noviembre, pero las ideas de esta versión se inspiraron en resultados previos. Por tanto, ninguna de estas cifras es una evaluación final independiente ni prueba de mejora estadísticamente significativa. Se necesita un período o fuente nueva antes de decidir uso operativo.

| Método | MAE agosto–octubre | MAE noviembre |
|---|---:|---:|
| Random Forest v2 | 428.58 | 485.43 |
| Corrección RF v3 | 404.36 | 489.13 |
| Corrección boosting v3 | 374.26 | 479.06 |
| Semana anterior | 445.79 | 562.35 |
| Promedio de cuatro semanas | 380.00 | 492.77 |

Menor MAE (unidades por producto y semana) es mejor. El boosting residual fue el mejor método promedio en esta ejecución: mejora aproximadamente 1,5% frente al promedio de cuatro semanas en agosto–octubre. La mejora es pequeña y no uniforme: en septiembre su error fue 265,55 frente a 230,22 de la referencia.

## Análisis de errores

En noviembre, el modelo elegido mejora al promedio de cuatro semanas en 7 de 10 productos. Sin embargo, POPCORN HOLDER presenta MAE 1.728,73 frente a 934,75 de ese promedio y 535,00 de repetir la última semana. El modelo subestima sus semanas de alto volumen. No se eliminaron estos casos ni se creó una regla especial usando sus resultados; tampoco puede atribuirse el pico a promociones o stock sin datos que lo respalden.

Cinco mayores errores del modelo elegido:

| Producto | Origen | Ventas reales siguientes 7 días | Estimación |
|---|---|---:|---:|
| POPCORN HOLDER | 2011-11-08 | 3704 | 1152.61 |
| JUMBO BAG RED RETROSPOT | 2011-11-08 | 2934 | 887.87 |
| POPCORN HOLDER | 2011-11-01 | 2843 | 1105.43 |
| POPCORN HOLDER | 2011-11-15 | 2665 | 1143.84 |
| ASSORTED COLOUR BIRD ORNAMENT | 2011-11-08 | 2070 | 699.49 |

## Uso y reproducción

Abrir http://localhost:3000/training . La v3 aparece primero; la comparación v2 puede desplegarse más abajo. Se incluyen resultados por corte, por producto, predicciones semanales filtrables y los cinco errores más grandes.

Desde la raíz del repositorio, con los datos preparados para v2:

```sh
backend/.venv/bin/python scripts/train_uci_v3.py
```

La preparación inicial está documentada en `docs/ENTRENAMIENTO_UCI_V2.md`. Esta ejecución reutiliza `work/uci/prepared-v2.json`, sin descargar datos ni modificar la base operativa.

Se guardan `work/uci/evaluation-v3.json`, `frontend/public/training-results-v3.json` y `work/uci/weekly-model-v3.joblib`. El artefacto final se ajusta con todo el historial disponible y debe inferirse mediante `predict_residual`, que aplica la reconstrucción y el recorte indicados; el estimador solo devuelve correcciones normalizadas. Sus pronósticos posteriores al final del historial no están validados. Este modelo no sustituye automáticamente el flujo operativo.

## Comprobaciones

26 pruebas unitarias aprobadas, incluida invariancia de las variables ante cambios futuros, reconstrucción de la referencia con corrección cero, recorte no negativo, ventana de 56 días y separación de objetivos conocidos. Comprobación TypeScript sin errores. Se recargó el artefacto guardado para reproducir sus pronósticos y se recalcularon los MAE a partir de todos los casos exportados.

Fuente: Daqing Chen (2015), UCI Online Retail, DOI 10.24432/C5BW33, CC BY 4.0. https://archive.ics.uci.edu/dataset/352/online+retail . Datos históricos 2010–2011, ventas brutas elegibles, no demanda actual de Mercado Libre.
