# Plan y resultados de pruebas — TrendML

Jose Manuel Castro Reina · Grupo 14 individual · Docente Matias Arellano
Preparado el 1 de noviembre de 2026. Este documento registra pruebas ejecutadas, no pruebas supuestas.

## 1. Alcance y entorno

Se verifican las funcionalidades convencionales (registro, acceso, sesión, tendencias, alertas, permisos) y la funcionalidad de IA (preparación de datos, separación temporal, entrenamiento, carga del artefacto e inferencia). Las pruebas automatizadas usan SQLite en memoria o temporal; no modifican `work/academic.db`, no envían correos y no ejecutan pagos.

Comandos usados:

```bash
backend/.venv/bin/python -m unittest discover -s tests -v
cd frontend && npx tsc --noEmit && npm run build
```

Resultado: **37 pruebas aprobadas**, TypeScript sin errores y compilación de Next.js correcta. La prueba que usa el artefacto real se ejecutó porque el modelo y los datos preparados estaban disponibles; en un clon sin entrenamiento previo se marca omitida de forma explícita.

## 2. Pruebas convencionales y de contrato

| Área | Qué se comprueba | Evidencia |
| --- | --- | --- |
| Registro | Alta válida, correo duplicado, correo/contraseña inválidos, hash y ausencia de contraseña en la respuesta | `test_registration_duplicate_validation_and_hash` |
| Acceso | Login válido e inválido, token inválido, usuario inactivo y rutas protegidas | `test_login_invalid_session_and_inactive_user` |
| Planes | Starter no accede a alertas/predicciones; Premium no es administrador; listas vacías no se confunden con permisos | `test_plans_empty_data_and_admin_is_not_premium` |
| Tendencias | Solo el último snapshot por producto; precio 100→80 produce alerta; precio anterior cero no produce alerta | `test_price_drop_and_latest_trend_only` |
| Predicción operativa | Sin datos suficientes no se inventa una cifra; fuente no verificada produce `unverified_data`; error del modelo conserva análisis convencional | `test_weekly_model.py` |
| Datos y contador | Series diarias completas, reinicios del acumulado, duplicados, valores no finitos y observaciones faltantes | `test_weekly_model.py`, `test_uci_v2.py` |
| Separación temporal | Los objetivos de entrenamiento terminan antes del origen de prueba; no se usan ventas futuras como variables | `test_uci_v2.py`, `test_uci_v3.py` |
| Pipeline UCI | Cancelaciones, duplicados, selección de productos con datos hasta el corte y purga de objetivos solapados | `test_uci_pipeline.py` |
| Inferencia real | Catálogo, plan Pro, producto inexistente, horizonte de siete días, metadatos y fuente | `test_real_saved_model_inference` |
| Fallos controlados | Producto inexistente → 404; modelo ausente → 503; entrada inválida → 422; sin sesión/plan → 401/403 | `test_live_inference_permissions_and_missing_model` |
| Modo académico | Checkout bloqueado y plan sin cambios | `test_academic_mode_disables_checkout` |

## 3. Pruebas de calidad de la funcionalidad de IA

Se tomaron diez productos con el mismo origen histórico, 1 de noviembre de 2011. La entrada es el historial disponible hasta ese día; la salida es la estimación de unidades de los siete días siguientes. El valor real se conoce porque el conjunto UCI continúa después del corte. La referencia es el promedio de las cuatro semanas previas.

Criterio de este registro: una salida es **comparativamente favorable** si su error absoluto no supera el de la referencia de cuatro semanas. No es un umbral comercial ni una medida de precisión porcentual.

| Producto | Real | IA | Error IA | Referencia 4 semanas | Error referencia | ¿Favorable? |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| UCI-15036 | 41 | 166.7 | 125.7 | 148.5 | 107.5 | No |
| UCI-21212 | 1092 | 576.5 | 515.5 | 495.8 | 596.2 | Sí |
| UCI-21977 | 108 | 365.7 | 257.7 | 353.0 | 245.0 | No |
| UCI-22197 | 2843 | 1105.4 | 1737.6 | 1481.8 | 1361.3 | No |
| UCI-22616 | 791 | 369.7 | 421.3 | 367.8 | 423.3 | Sí |
| UCI-23166 | 39 | 65.1 | 26.1 | 59.5 | 20.5 | No |
| UCI-84077 | 1296 | 1041.7 | 254.3 | 1929.8 | 633.8 | Sí |
| UCI-84879 | 634 | 656.4 | 22.4 | 716.5 | 82.5 | Sí |
| UCI-85099B | 1179 | 941.9 | 237.1 | 1342.5 | 163.5 | No |
| UCI-85123A | 1708 | 426.5 | 1281.5 | 415.3 | 1292.8 | Sí |

Resultado: 5 de 10 casos fueron comparativamente favorables en este origen. El promedio global de noviembre es mejor que la referencia, pero el resultado no es uniforme. Los 40 casos de noviembre y los 120 de validación están en `training-results-v3.json` y `evaluation-v3.json`.

**Lectura correcta:** el MAE de validación de la v3 fue 374,26 unidades por producto y semana frente a 380,00 de la referencia. Es una mejora pequeña, medida en períodos ya examinados durante el desarrollo. No es un test independiente ni una garantía para Mercado Libre.

## 4. Casos límite y adversarios

| Entrada o situación | Respuesta esperada | Resultado observado |
| --- | --- | --- |
| `product_id` vacío | Error de validación, no una predicción | HTTP 422 |
| Sin token | Acceso rechazado | HTTP 403 |
| Cuenta Starter | Acceso rechazado; no se cambia el plan | HTTP 403 |
| Producto fuera del catálogo | No se inventa un resultado | HTTP 404 |
| Artefacto ausente o incompatible | Error controlado y mensaje legible | HTTP 503; el resto de la aplicación sigue disponible |
| Serie de observaciones vacía | Rechazo explícito | `ValueError` |
| Unidades diarias negativas, NaN o infinito | Rechazo explícito | `ValueError` |
| Fechas duplicadas o días faltantes | Rechazo explícito | `ValueError` |
| Contador acumulado que retrocede | Se descarta el segmento anterior al reinicio | Prueba de reinicio aprobada |
| Historial insuficiente para siete días | No se genera una predicción semanal falsa | Diccionario vacío o estado sin cifra |
| Fuente desconocida o `DEMO-` | Se marca como no verificada, sin número válido | `unverified_data` |
| Precio anterior cero | No se divide por cero ni se crea una alerta | Lista de alertas vacía |

Todos los casos anteriores están cubiertos por pruebas automatizadas o por el contrato de la API. Los casos de IA no se validan solo por “no fallar”: se registra además si la salida fue razonable frente a la realidad histórica.

## 5. Recorrido HTTP verificado

El 1 de noviembre de 2026 se levantó la API en un puerto temporal con una base SQLite temporal y se ejecutó el recorrido real:

1. `POST /api/auth/login` con la cuenta demo Pro.
2. `GET /api/auth/me` devolvió la cuenta Pro.
3. `GET /api/trending`, `/api/price-alerts` y `/api/predictions` devolvieron los tres productos sintéticos; las predicciones indicaron `unverified_data`, sin cifras inventadas.
4. `GET /api/lab/products` devolvió 10 productos históricos UCI, versión `weekly-residual-v3`, 3.060 pares de entrenamiento y objetivos conocidos hasta 2011-12-08.
5. `POST /api/lab/forecast` para `UCI-22616` devolvió 496,62 unidades, referencia 674,5, corte 2011-12-08, horizonte 2011-12-09 a 2011-12-15 y estado `historical_forecast_unvalidated`.

La captura `demo-inferencia.png` corresponde a una ejecución anterior del mismo recorrido. Las diez respuestas actuales están en `inferencias.json`.

## 6. Defectos encontrados y correcciones

| Defecto | Corrección | Verificación |
| --- | --- | --- |
| Validación de contraseña solo en el navegador | Validación también en la API (`Field(min_length=8, max_length=128)`) | Prueba de registro inválido |
| Predicciones antiguas podían mostrarse como actuales | Última observación válida y estado explícito por producto | Pruebas de modelo y de API |
| El objetivo original no representaba exactamente siete días | Objetivo por diferencia de acumulado a siete días, con purga temporal | Pruebas de horizonte y separación |
| Datos sintéticos podían confundirse con ventas reales | Procedencia en `PriceHistory` y estado `unverified_data` | Pruebas de fuente y UI |
| Un fallo del modelo rompía el análisis convencional | Captura del error, estado `model_error` y persistencia del resto | `test_failure_keeps_conventional_analytics` |
| Premium podía confundirse con administrador | Lista explícita `ADMIN_EMAILS` | Prueba de permisos |
| La pantalla de entrenamiento parecía ejecutar IA en vivo | Se separó laboratorio y API de inferencia; la UI muestra resultados calculados | README y prueba de inferencia real |
| El artefacto no conservaba métricas ni fecha de entrenamiento | Se añadieron `trained_through`, `training_pairs`, MAE de validación y referencia | `test_real_saved_model_inference` |

## 7. Límites de esta verificación

- No existe todavía una evaluación independiente en un período no examinado. Los resultados de agosto–noviembre se usaron para decidir y deben considerarse de desarrollo.
- No se validó con una cuenta vendedora real de Mercado Libre ni con ventas propias.
- No se ejecutaron pruebas con PostgreSQL ni con Docker; la entrega validada es SQLite local.
- La interfaz se verificó con `npm run build`, TypeScript y una ejecución HTTP; no hay una prueba automatizada de navegador.
- Las capturas del tablero son evidencia de gestión, no de precisión del modelo.

## 8. Reproducción

```bash
bash scripts/setup_local.sh
bash scripts/train_academic.sh
bash scripts/check_academic.sh
bash scripts/start_academic.sh
```

Abrir http://localhost:3000/login, pulsar **Entrar como demo**, ir a **Predecir**, elegir un producto y ejecutar el cálculo. Para revisar la evaluación, abrir **Entrenamiento**. Los resultados no reemplazan una validación comercial.
