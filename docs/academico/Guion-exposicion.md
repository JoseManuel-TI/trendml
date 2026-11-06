> **Documento histórico del 14 de octubre de 2026.** El guion vigente para la entrega final está en `docs/entrega/Exposicion-clases.md`.

# Guion de exposición de TrendML

Jose Manuel Castro Reina · Grupo 14 · Matias Arellano
Duración sugerida: 7 a 9 minutos, ajustable al tiempo que indique el profesor.

## Antes de comenzar

El correo del 14 de octubre cita otros grupos para el punto 5 y no asigna un horario al grupo 14. Pedir turno en clase o por el aula virtual. No se envió ningún mensaje en tu nombre.

Frase de apertura:

> Profesor, soy José Manuel Castro Reina, del grupo 14 individual. Quisiera presentar el avance de los puntos 1 al 5 de TrendML para ponerme al día. Tengo preparado el alcance, la metodología, las historias y el diseño; también identifiqué los pendientes de gestión.

## Punto 1 Dominio y funcionalidad de IA

Tiempo: un minuto. Mostrar página 1 del documento.

> TrendML es una aplicación de análisis para vendedores de comercio electrónico. Busca reunir tendencias, alertas de precio y una estimación de las unidades que un producto podría vender durante los próximos siete días. Reutilizo un proyecto que ya tenía, pero estoy corrigiendo y documentando su funcionamiento.
>
> La IA está en la estimación de ventas. Uso modelos de scikit-learn y comparo sus resultados con métodos sencillos. Además, utilicé Codex para asistir el análisis, el diseño, el código, las pruebas y la documentación. Son los dos ejes de la consigna.
>
> Como todavía no tengo ventas propias ni una cuenta vendedora conectada, preparé un laboratorio con transacciones reales históricas de UCI. Es una prueba del sistema, no una validación del mercado actual de Mercado Libre.

## Punto 2 Metodología

Tiempo: 45 segundos. Mostrar página 2.

> Elegí Kanban porque trabajo individualmente. Soy responsable de priorizar, desarrollar, probar y documentar. El flujo es Backlog, Pendiente, En proceso y Finalizado, con un límite de una tarea en proceso.
>
> Una tarea se cierra cuando cumple su aceptación, tiene evidencia y está revisada. En cambios de código también debo asociar el commit. Para IA agrego controles de fuente, fechas, salida y comparación con una referencia.

## Punto 3 Gestión del trabajo

Tiempo: 45 segundos. Mostrar página 3 y el tablero de Notion: https://app.notion.com/p/28314a0e971e47468ef7160884411574

> Tengo un tablero privado de Notion, creado hoy, con 14 tareas desglosadas por historia, etiquetas de IA y dependencias. Registra el estado actual. La tarea documental de definir las ocho historias está finalizada; el cierre de los cambios de código todavía requiere revisión y commits. Faltan las capturas de tres momentos distintos.
>
> El siguiente paso de gestión es iniciar sesión en Notion para tomar la primera captura y registrar los movimientos reales desde este momento. El límite de una tarjeta en proceso se controla manualmente.

El tablero es privado. Si el docente necesita acceso, acordar cómo compartirlo; no se modificaron sus permisos ni se publicó automáticamente.

## Punto 4 Historias de usuario

Tiempo: un minuto. Mostrar páginas 4 y 5.

> Definí ocho historias: registro, acceso, tendencias, alertas, estimación con IA, disponibilidad de la estimación, incorporación de datos y permisos.
>
> La principal de IA dice: como vendedor quiero ver una estimación de unidades para los próximos siete días para orientar mi planificación de stock. Para aceptarla, la salida debe tener horizonte, fecha y limitaciones, y debe evaluarse con datos posteriores al entrenamiento.
>
> Si los datos no son suficientes o no tienen procedencia verificada, la aplicación debe explicarlo y no inventar una cifra. Ese comportamiento corresponde a otra historia y también tiene pruebas.

## Punto 5 Diseño del sistema

Tiempo: dos minutos y medio. Mostrar páginas 6, 7 y 8.

> La interfaz usa Next.js; la API, FastAPI; y la persistencia, SQLAlchemy. En local uso SQLite. Los productos tienen observaciones de precio y ventas. Las tendencias y las predicciones se guardan por separado.
>
> En el ER, un producto puede tener muchas observaciones y muchas predicciones. WeeklyPrediction guarda el resultado o un valor vacío, el estado, la versión y la fecha. El historial tiene un campo que identifica su fuente. No presento un número de prueba como predicción válida.
>
> Hay dos circuitos. En el operativo, el worker obtiene datos autorizados, los valida, procesa el modelo y guarda resultados que después consulta la API. Falta validar ese circuito con una cuenta propia. En el laboratorio, un script prepara datos históricos, entrena, evalúa y guarda resultados que lee la pantalla de entrenamiento.
>
> Abrir la pantalla no ejecuta IA: muestra los resultados calculados por el script. Puedo volver a ejecutar el script para demostrar el cálculo. La versión 3 aprende a corregir el promedio de cuatro semanas usando el comportamiento reciente y un historial de 56 días.
>
> Los wireframes están relacionados con las historias: acceso, dashboard, predicción y laboratorio. No existe una pantalla de importación: por ahora esa tarea se realiza mediante scripts.

## Demostración breve opcional

Tiempo: un minuto. Abrir http://localhost:3000/training .

1. Mostrar el encabezado de datos históricos.
2. Mostrar la tabla de métodos: menor MAE es mejor, no es un porcentaje de aciertos.
3. Señalar el promedio de validación de la v3: 374,3 frente a 380,0 de la referencia.
4. Elegir POPCORN HOLDER y abrir los cinco mayores errores. Explicar que el promedio global no garantiza buen resultado para todos los productos.
5. Concluir que falta una evaluación con datos nuevos antes de usar la estimación comercialmente.

Si hay tiempo, desde la raíz del proyecto ejecutar:

```sh
backend/.venv/bin/python scripts/train_uci_v3.py
```

Después recargar la pantalla. El comando reutiliza datos locales reales históricos, reentrena el experimento y reemplaza sus resultados y artefacto local. No envía correos ni ejecuta pagos. Evitar abrir archivos de configuración con credenciales.

## Cierre

> Hasta aquí presento los puntos 1 al 5 como avance. Tengo código, pruebas técnicas y una evaluación reproducible, pero aún debo completar las capturas del tablero, publicar los cambios locales, verificar el recorrido convencional y validar con datos nuevos. Quisiera confirmar si este alcance y la separación entre laboratorio y operación son adecuados para continuar con la entrega final.

## Respuestas breves para preguntas del profesor

**¿Dónde está la IA?** En los modelos entrenados por los scripts y en el servicio de predicción. Las tendencias y porcentajes de precio son cálculos convencionales.

**¿Qué aprende la v3?** Una corrección sobre la media de cuatro semanas; esa corrección se transforma nuevamente a unidades de venta.

**¿Por qué comparar con un promedio?** Porque un modelo más complejo debe demostrar que aporta algo frente a una solución sencilla.

**¿Los datos son reales?** Sí, las transacciones UCI son reales e históricas de 2010–2011. Los datos DEMO de la base operativa son sintéticos y se mantienen separados.

**¿Ya funciona con Mercado Libre?** Hay código de integración, pero no lo validé con una cuenta vendedora propia. No afirmo disponibilidad real de ventas de ese servicio.

**¿Está integrado o es solo un notebook?** Los scripts generan resultados que consume la aplicación en /training. El entrenamiento es por lotes; no se dispara desde esa pantalla. El cumplimiento final del flujo de IA operativo requiere completar la integración con el alcance que acuerde el docente.

**¿Usaste IA para hacerlo?** Sí. Codex asistió análisis, diseño, implementación y pruebas. Hay ejemplos de propuestas corregidas: el objetivo inicial no representaba siete días y una alternativa mostraba ventas observadas como predicción. Puedo explicar las correcciones y sus pruebas.

**¿Está todo en GitHub?** El proyecto base sí. Las modificaciones recientes están locales y falta revisarlas y publicarlas.

**¿Ya terminaste?** No. Esta es una presentación de avance de los puntos 1 al 5. La entrega final de la consigna figura para el 30 de noviembre de 2026 a las 23:59; el docente define las exposiciones por etapas.
