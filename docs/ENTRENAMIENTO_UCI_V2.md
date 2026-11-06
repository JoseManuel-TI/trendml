# TrendML: versión 2 con ventas recientes

Ejecución: 14 de octubre de 2026. Jose Manuel Castro Reina, grupo 14. Docente: Matias Arellano.

Se implementó un experimento reproducible con ventas de 7, 14 y 28 días, media y dispersión diaria, diferencia entre semanas, precio y cambio de precio, mes y día de semana. Todas las entradas se calculan al cierre del día del pronóstico, con datos de ese día o anteriores. El objetivo conserva las unidades de los siete días siguientes. No se rellenan huecos desconocidos: el proceso exige una serie diaria completa. En UCI, los ceros provienen de la preparación del registro de transacciones.

## Evaluación

Para evitar seleccionar productos con información futura, esta cohorte de diez productos se eligió por ventas conocidas al 1 de agosto de 2011. Difiere en un producto de la cohorte original. Se usan cortes el 1 de agosto, septiembre y octubre; cada uno evalúa cuatro semanas no solapadas, con 40 casos. Los modelos entrenan solo con objetivos terminados al corte. Se excluyen los primeros 27 días sin historial suficiente y todos los métodos comparten filas, productos y fechas.

Se comparan el Random Forest v1 (50 árboles), Random Forest v2 (150 árboles, profundidad máxima 10, mínimo 5 ejemplos por hoja), HistGradientBoosting v2 (100 iteraciones, 15 hojas, regularización 1, sin early stopping aleatorio), repetir la última semana y el promedio de cuatro semanas. Semilla 42. Estas configuraciones se fijaron antes de ver los resultados v2, sin búsqueda sobre noviembre.

El modelo v2 se elige por menor MAE promedio en los tres cortes. La referencia también participa en la elección del mejor método global. Noviembre se calcula después de esa selección; como ya fue consultado en el experimento anterior, sigue siendo una comparación exploratoria, no una prueba final independiente.

| Método | MAE validación agosto–octubre | MAE noviembre |
|---|---:|---:|
| Modelo actual (v1) | 568.51 | 1283.26 |
| Random Forest v2 | 414.65 | 485.37 |
| Boosting v2 | 429.38 | 509.57 |
| Semana anterior | 445.79 | 562.35 |
| Promedio de cuatro semanas | 380.00 | 492.77 |

El MAE está expresado en unidades por producto y semana; menor es mejor. El mejor modelo v2 fue Random Forest, pero el mejor método en la validación fue el promedio de cuatro semanas. La mejora en noviembre no basta para promover automáticamente el modelo a decisiones operativas. En particular, POPCORN HOLDER tiene MAE de 1.592,2 con Random Forest v2 frente a 535,0 con repetir la semana anterior; el promedio global oculta esa debilidad.

## Uso y reproducción

Abrir http://localhost:3000/training . La nueva sección incluye comparación de cinco métodos, resultados de cada corte, errores por producto y un filtro para las predicciones semanales. El experimento original permanece identificado más abajo.

Desde la raíz del proyecto, con el archivo UCI ya descargado y openpyxl instalado:

```sh
backend/.venv/bin/python scripts/prepare_uci.py --selection-cutoff 2011-08-01 --output work/uci/prepared-v2.json
backend/.venv/bin/python scripts/train_uci_v2.py
```

Para repetir solo el entrenamiento, basta el segundo comando. Ver `docs/ENTRENAMIENTO_UCI.md` para descargar el archivo original. La preparación inicial de v2 usó el Python de Codex con pandas/openpyxl; entrenamiento y pruebas usaron el entorno del proyecto.

Archivos generados:

- `work/uci/prepared-v2.json`: cohorte e historial con procedencia y SHA256.
- `work/uci/evaluation-v2.json`: resultados de todos los cortes y predicciones.
- `work/uci/weekly-model-v2.joblib`: Random Forest v2 reentrenado con todo el historial disponible, con sus características y fuente. Las estimaciones posteriores al final del historial no están validadas. No confundir este ajuste final con los modelos evaluados en cada corte.
- `frontend/public/training-results-v2.json`: resultados que consume la pantalla, sin identificadores de clientes.

El experimento no cambia la base de datos ni sustituye el modelo del flujo operativo. Su siguiente evaluación debe utilizar datos o un período no consultado para ajustar decisiones. Los datos UCI son históricos, de 2010–2011; no acreditan desempeño en Mercado Libre actual.

## Validación técnica

23 pruebas unitarias aprobadas, incluidas invariancia de características ante cambios futuros, alineación de siete días, rechazo de huecos/duplicados y separación temporal compartida entre productos. TypeScript sin errores. Se verificó el filtro v2 en el navegador. El modelo guardado se volvió a cargar y reproduce sus pronósticos; los MAE fueron recalculados a partir de los casos exportados.

Fuente: Daqing Chen (2015), UCI Online Retail, DOI 10.24432/C5BW33, CC BY 4.0. https://archive.ics.uci.edu/dataset/352/online+retail
