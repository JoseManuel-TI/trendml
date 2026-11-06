# TrendML guía para exponer en clase

Jose Manuel Castro Reina · Grupo 14 individual
Profesor Matias Arellano · 31 de octubre de 2026 · Revisión: 6 de noviembre de 2026
Duración orientativa 8 a 10 minutos

Esta guía sirve para explicar el problema, demostrar la aplicación y defender las decisiones del modelo. Preparar las ventanas de Login, Predecir, Entrenamiento y Notion antes de comenzar. Leer las ideas y ensayar con palabras propias.

## Apertura y problema un minuto

“Soy Jose Manuel Castro Reina, del grupo 14. Mi proyecto se llama TrendML. Está pensado para pequeños vendedores que necesitan revisar productos, cambios de precio y posibles ventas de la próxima semana. Reutilicé una aplicación propia y la adapté a la consigna de desarrollar un sistema con IA y con asistencia de IA.”

“La versión que presento combina una demo de datos sintéticos para las funciones convencionales y un laboratorio con transacciones históricas reales de UCI. Todavía no tengo ventas propias ni una cuenta de Mercado Libre conectada. Por eso presento un prototipo académico y no una herramienta comercial validada.”

## Metodología e historias un minuto

“Trabajo de forma individual con Kanban y un límite de una tarea en proceso. Las columnas son Backlog, Pendiente, En proceso y Finalizado. Cada tarea tiene historia, criterio de aceptación y evidencia. Cierro código después de revisar y probar los cambios.”

“Definí ocho historias: registro, acceso, tendencias, alertas, estimación con IA, disponibilidad de la predicción, incorporación de datos y permisos. Registro, acceso, tendencias y alertas son funciones convencionales. La estimación semanal ejecuta el modelo de IA.”

## Diseño un minuto

“El frontend usa Next.js, el backend FastAPI y la base local SQLite. El usuario elige un producto histórico; la API verifica sesión y plan, construye las variables con datos pasados y ejecuta el modelo guardado. Devuelve unidades estimadas, período y referencia, y la pantalla lo muestra.”

“Entrenar y predecir son procesos separados. Entreno con un script reproducible. Cuando pulso Calcular predicción, se ejecuta inferencia: no se vuelve a entrenar y tampoco se muestra una respuesta fija.”

## Demostración en vivo tres minutos

### Ingreso a la aplicación

Abrir una terminal y ejecutar desde la carpeta del proyecto:

```bash
cd /Users/josemanuel/Documents/Workspace/02_Desarrollo/proyectos/trendml
bash scripts/start_academic.sh
```

Esperar a que aparezcan `Uvicorn running on http://127.0.0.1:8000` y `Ready` del frontend. Luego abrir http://localhost:3000/login y pulsar **Entrar como demo**. Si el modelo falta, ejecutar antes `bash scripts/train_academic.sh`. Si un puerto está ocupado, detener la instancia anterior antes de volver a iniciar.

**Notas de arranque:** si aparece `urllib3 ... LibreSSL`, es una advertencia de la librería y no impide la inferencia. El `404` de `/favicon.ico` es inocuo. Si `/` devuelve `404` al inicio, esperar a que Next compile y abrir `/login`. Para detener el sistema, `Ctrl+C` en la terminal.

| Paso | Qué mostrar y decir |
| --- | --- |
| 1 Acceso | Abrir /login y pulsar Entrar como demo. La cuenta Pro local no necesita un pago. |
| 2 Dashboard | Mostrar alertas de precio y etiquetas de datos sintéticos. Si no hay tendencias, explicar el estado vacío; no inventar resultados. |
| 3 Predecir | Abrir /forecast. Elegir PACK OF 12 LONDON TISSUES y pulsar Calcular predicción. |
| 4 Resultado | Mostrar unidades, referencia, versión, período histórico y fecha del cálculo actual. Abrir “Ficha técnica y límites del modelo” para mostrar el corte de entrenamiento, los pares y el MAE de desarrollo. Cambiar de producto y volver a calcular. |
| 5 Evaluación | Abrir /training. Explicar MAE y mostrar que hay errores y productos donde la referencia gana. |
| 6 Gestión | Abrir Notion y mostrar tareas, estados y evidencia del trabajo real. |

“Este resultado de aproximadamente 496,6 unidades corresponde a los siete días posteriores al 8 de diciembre de 2011. La referencia simple estima 674,5. Que los números difieran no demuestra cuál acertó: para saberlo necesitaría comparar con las ventas posteriores observadas.”

## Pruebas y calidad un minuto

“Ejecuté 37 pruebas que verifican registro, acceso, permisos, cálculos, datos, horizonte temporal y fallos. También comprobé la inferencia desde el navegador y la compilación del frontend. Un producto inexistente devuelve 404 y un modelo no disponible devuelve 503; el sistema informa el problema. El plan completo, los diez casos de calidad de IA y los adversarios están en el documento de pruebas.”

“En la evaluación temporal el MAE fue 374,26 unidades frente a 380,00 del promedio de cuatro semanas. La mejora es pequeña, y hay casos peores. Los períodos ya fueron examinados durante el desarrollo, así que no los presento como un test independiente.”

## Uso de IA y cierre un minuto

“Usé Codex para explorar el alcance, redactar historias, diseñar diagramas, revisar código, generar pruebas y organizar la entrega. Corregí propuestas que confundían datos sintéticos con evidencia real y una pantalla de métricas con inferencia integrada. La herramienta ayuda, pero tuve que contrastar los resultados con pruebas.”

“El prototipo cumple un recorrido funcional con IA real sobre datos históricos. El siguiente paso para utilizarlo comercialmente es obtener ventas autorizadas, validar en períodos nuevos, incorporar stock y aislar los datos de cada vendedor.”

## Preguntas que puede hacer el profesor

### Dónde está la IA

En el modelo scikit-learn cargado por forecast_service.py. La ruta POST /api/lab/forecast ejecuta predict y devuelve un resultado que se ve en /forecast.

### Por qué esto no es una fórmula fija

El modelo ajusta una corrección a partir de ejemplos históricos. El promedio de cuatro semanas sí es una referencia convencional; ambos se comparan explícitamente.

### Qué datos son reales

Las transacciones de UCI Online Retail son históricas reales de un comercio británico. Los productos DEMO del dashboard son sintéticos y están identificados.

### Cómo evitas usar el futuro

Las variables miran hacia atrás y el conjunto de entrenamiento solo incluye etiquetas cuyo período de siete días ya terminó al corte.

### Qué significa MAE

Es el promedio del error absoluto expresado en unidades por producto y semana. No es un porcentaje de precisión.

### Por qué puede fallar el modelo

Cambios de demanda, promociones, stock faltante o patrones no representados en el entrenamiento. La referencia puede superar al modelo y por eso no la oculto.

### Qué sucede si el modelo no está disponible

La API devuelve 503 y la pantalla muestra el error. No reemplaza silenciosamente la salida con un número aleatorio.

### Qué falta para uso real

Datos propios, validación independiente, aislamiento multiusuario, monitoreo, despliegue y revisión de seguridad. No afirmo que esas etapas estén terminadas.

### Cómo se aplicó Kanban

Se identificaron tareas con historias y evidencia. El WIP es uno y se actualiza manualmente. Las capturas tienen fechas reales; no reconstruyen un historial anterior.

### Quién es responsable del trabajo

Yo soy responsable de revisar, comprender y defender el proyecto. Codex es una herramienta, no un integrante del grupo.

## Preparación antes de entrar a clase

Ejecutar desde la carpeta trendml:

bash scripts/start_academic.sh

Dejar esa terminal abierta. Abrir http://localhost:3000/login y pulsar Entrar como demo. Si el modelo falta, detenerse y ejecutar antes bash scripts/train_academic.sh. No entrenar por primera vez durante la exposición.

Verificado el 06/11/2026: login, catálogo de diez productos, inferencia real (496,6 unidades para UCI-22616), restricción Starter (403) y frontend respondieron correctamente en local.

Acceso manual Pro: demo@example.com / DemoTrendML123!
Starter para demostrar restricciones: starter@example.com / DemoTrendML123!
Las cuentas nuevas quedan en Starter. No utilizar cuentas o contraseñas personales en la presentación.

## Lista de comprobación

• Probar Login demo y Calcular predicción antes de clase.

• Abrir el informe, este guion y el tablero Notion.

• Mostrar las tres capturas del tablero (`tablero-01`, `02` y `03`) y explicar que documentan estados reales del 31/10 y 01/11; no reconstruyen movimientos históricos. Tener a mano el enlace del repositorio actualizado.

• Hacer una pasada personal con cronómetro y anotar el tiempo en [ensayo-cronometrado.md](ensayo-cronometrado.md); explicar con palabras propias.

• Confirmar turno de exposición con el docente.

• Evitar mostrar archivos .env, tokens o información privada.

## Si aparece un problema durante la demo

Si el puerto está ocupado, detener la instancia anterior desde su terminal. Si la sesión vence, volver a Login. Si aparece un error del modelo, mostrar el mensaje y explicar el manejo del fallo; no sustituirlo por una captura afirmando que hubo una inferencia nueva.

Las capturas y resultados guardados sirven como evidencia complementaria. La consigna pide demostración en vivo: si falla el entorno, corresponde informar el problema y coordinar su repetición.

## Idea central para recordar

“TrendML demuestra cómo integrar y evaluar una predicción real en una aplicación. El trabajo no termina al obtener un número: hay que mostrar de dónde salen los datos, qué período se estima, cuánto se equivoca el modelo y cuándo conviene revisar su resultado.”
