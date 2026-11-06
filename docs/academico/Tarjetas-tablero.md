> **Documento histórico del 14 de octubre de 2026.** Las actualizaciones propuestas para el estado final están en `docs/entrega/Tablero-actualizaciones.md`.

# Tarjetas para el tablero de TrendML

Responsable de todas las tarjetas: Jose Manuel Castro Reina, grupo 14.
Este registro fue preparado el 14 de octubre de 2026; no es un historial retrospectivo de un tablero externo.
Tablero creado en Notion: https://app.notion.com/p/28314a0e971e47468ef7160884411574 . Las tarjetas siguientes son su referencia local; el estado vigente se consulta en Notion.
Columnas: Backlog, Pendiente, En proceso, Finalizado. WIP: una tarjeta.

## Referencia de tarjetas cargadas

- T01 · HU01 y HU02 · Pruebas de registro y acceso · Pendiente · convencional, pruebas.
  Subtareas: registro válido, duplicado, login válido e inválido, sesión vencida. Aceptación: resultados registrados sin exponer credenciales. Evidencia a obtener: prueba funcional de API y pantalla.
- T02 · HU03 y HU04 · Validar tendencias y alertas · Pendiente · convencional, pruebas.
  Subtareas: crecimiento, precio 100 a 80, precio anterior cero y lista vacía. Aceptación: cálculo y estados correctos. Dependencia: entorno local disponible.
- T03 · HU05 y HU06 · IA Corregir contrato semanal y estados · Pendiente de cierre · IA, revisión.
  Trabajo implementado y probado localmente: horizonte, última observación, fuentes, errores y persistencia. Subtareas restantes: revisar diff y asociar commit. Evidencia: backend/services/ml_service.py, tests/test_weekly_model.py y docs/VERIFICACION_MODELO_2026-10-14.md.
- T04 · HU07 · IA Revisar preparación UCI y cerrar integración · Pendiente · IA, datos.
  Preparación ejecutada. Revisar reglas de cancelaciones, duplicados, días sin ventas y selección por fecha; asociar commit. Evidencia: scripts/prepare_uci.py y docs/ENTRENAMIENTO_UCI.md. Dependencia: T03 para coherencia de objetivo.
- T05 · HU05 · IA Revisar experimentos y publicar resultados · Pendiente · IA, pruebas.
  v1, v2 y v3 ejecutadas. Subtareas: revisión personal de métricas, limitaciones y cambios; commit. Evidencia: docs/ENTRENAMIENTO_UCI_V2.md, docs/ENTRENAMIENTO_UCI_V3.md, scripts/train_uci_v3.py. No marcar precisión comercial aprobada.
- T06 · HU05 y HU06 · IA Cerrar revisión de pantalla de entrenamiento · Pendiente · IA, interfaz.
  Filtros, resultados y mayores errores verificados. Subtareas restantes: revisión personal, commit. Aceptación: cada sección identifica versión, fuente y estado; v3 no muestra datos v2.
- T07 · HU08 · Verificar permisos por plan · Pendiente · convencional, pruebas.
  Subtareas: cuenta Starter, cuenta Pro de prueba y llamadas directas a API. Aceptación: permisos aplicados por servidor. No activar pagos.
- T08 · Todas · Revisar material de exposición · Pendiente · documentación.
  Documento, diagramas y guion preparados. Subtareas: leer, ensayar 7–9 minutos, confirmar horario con docente. Aceptación: poder explicar los cinco puntos y sus pendientes.
- T09 · Todas · Crear tablero real y registrar primera captura · En proceso · gestión.
  Tablero y etiquetas creados. Pendiente: iniciar sesión y tomar primera captura con fecha real. WIP1 manual. Aceptación: captura auténtica; no movimientos históricos reconstruidos.
- T10 · Todas · Revisar y publicar cambios en GitHub · Pendiente · integración.
  Subtareas: revisar diff, excluir datos crudos/modelos/secretos, organizar commits, ejecutar controles pertinentes y publicar. Aceptación: enlace y commits revisables. No afirmar que ya fue publicado.
- T11 · HU05 y HU07 · IA Evaluar una fuente o período nuevo · Backlog · IA, datos.
  Subtareas: obtener datos autorizados, fijar evaluación antes de revisar resultados, medir error por producto. Aceptación: comparación independiente. Dependencia: disponibilidad de datos nuevos.
- T12 · HU07 y HU08 · Validar cuenta de Mercado Libre y aislamiento de datos · Backlog · integración.
  Subtareas: cuenta autorizada, campos disponibles, asociación de datos a vendedor y permisos. Aceptación: circuito completo verificado con procedencia. Dependencia: cuenta y datos propios.
- T13 · Todas · Registrar segunda y tercera captura del tablero · Backlog · gestión.
  Tomarlas en sesiones posteriores con cambios reales. Aceptación: tres momentos distintos acreditados, sin recrear el pasado.

Los experimentos ya ejecutados se describen en las tarjetas, pero su cierre de código está pendiente de revisión y commit. Mover a En proceso solo la tarjeta en la que se trabaje realmente.

- T14 · Todas · Definir ocho historias y criterios de aceptación · Finalizado · documentación. Evidencia: documento de puntos 1–5, páginas 4–5. Este cierre no significa que todas las funcionalidades estén implementadas.
