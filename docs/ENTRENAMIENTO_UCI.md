# Entrenamiento y evaluación histórica de TrendML

Ejecución: 14 de octubre de 2026. Responsable: Jose Manuel Castro Reina, grupo 14.

Se entrenó el Random Forest actual con ventas reales históricas de **UCI Online Retail**, de Daqing Chen (2015), DOI 10.24432/C5BW33, licencia CC BY 4.0. Fuente: https://archive.ics.uci.edu/dataset/352/online+retail . Son transacciones de un comercio británico de 2010–2011, con precios en GBP; no representan el mercado actual de Mercado Libre.

## Preparación y separación temporal

Del archivo de 541.909 filas se eliminaron duplicados exactos, cancelaciones, cantidades o precios no positivos y códigos ajenos al formato de productos seleccionado. Se descartó el último día parcial, 9 de diciembre. Se eligieron los 10 productos con más unidades vendidas usando exclusivamente datos hasta el 1 de noviembre de 2011. Se generaron 3.680 observaciones diarias.

Los días sin transacciones elegibles tienen cero ventas bajo el supuesto de un registro completo; esto no acredita disponibilidad de stock. El precio es el promedio diario ponderado por unidades, completado hacia adelante. Las fechas representan cierres diarios. El objetivo es unidades positivas vendidas durante los siete días siguientes, excluyendo devoluciones y cancelaciones: no ventas netas. No se exportan identificadores de clientes. Las características de reseñas ausentes se fijan en cero.

El modelo se ajustó con 3.240 pares cuyo objetivo ya se conocía al cierre del 1 de noviembre. La evaluación usa cuatro ventanas consecutivas sin solapamiento con orígenes 1, 8, 15 y 22 de noviembre: 40 casos producto-semana. No se ajustaron hiperparámetros con esos casos. La referencia repite las ventas de los siete días previos a cada origen.

## Resultado observado

| Método | Error absoluto medio (unidades por producto y semana) |
|---|---:|
| Random Forest actual | 1.284,56 |
| Repetir la semana anterior | 572,60 |

Menor error es mejor. **El modelo no supera la referencia.** El MAE no es un porcentaje de precisión. Esta prueba valida el funcionamiento del proceso y muestra una limitación predictiva concreta; no justifica su uso para decidir compras o stock. Solo se evaluaron diez productos de alto volumen durante cuatro semanas de un comercio histórico.

Tras congelar la evaluación se reentrenó un modelo final con todos los pares disponibles, guardado en `work/uci/weekly-model.joblib`. Sus pronósticos desde el 8 al 15 de diciembre están marcados como no validados porque exceden el historial disponible. La evaluación anterior corresponde al ajuste del 1 de noviembre, no a este artefacto final.

## Cómo usarlo

Con la aplicación levantada, abrir http://localhost:3000/training o elegir **Entrenamiento** en la navegación. Permite filtrar por producto y comparar ventas observadas, modelo y referencia. Es un experimento separado de la base de datos operativa.

Para repetir el entrenamiento con los datos ya preparados, desde la raíz del proyecto:

```sh
backend/.venv/bin/python scripts/train_uci.py
```

Para reproducir también la descarga y preparación (requiere internet solo para descargar y para instalar openpyxl si falta):

```sh
backend/.venv/bin/python -m pip install openpyxl==3.1.5
backend/.venv/bin/python scripts/download_uci.py
backend/.venv/bin/python scripts/prepare_uci.py
backend/.venv/bin/python scripts/train_uci.py
```

El archivo original, datos intermedios y modelo quedan en `work/uci`, ignorado por Git. La huella SHA256 del archivo fuente figura en los JSON. `frontend/public/training-results.json` contiene los resultados agregados que consume la pantalla. Volver a entrenar reemplaza el modelo y los resultados del experimento.

Validación realizada: 19 pruebas unitarias aprobadas, comprobación TypeScript sin errores y filtro de producto verificado en navegador. La extracción inicial utilizó el Python disponible en Codex con pandas/openpyxl; el entrenamiento utilizó el entorno virtual del proyecto.

## Próxima mejora

Incorporar ventas de los últimos 7 y 28 días y variables de calendario; comparar contra la referencia mediante validación temporal dentro del período de entrenamiento. Reservar otro período sin consultar para evaluar esa nueva versión. La prueba de noviembre ya fue observada y no debe usarse para afirmar una mejora imparcial tras ajustar el modelo a sus resultados. La transferencia a Mercado Libre requiere datos propios y una evaluación nueva.
