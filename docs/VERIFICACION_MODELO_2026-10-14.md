# Verificación de datos y corrección del modelo — 14 de octubre de 2026

Alumno: Jose Manuel Castro Reina. Grupo 14, individual. Profesor: Matias Arellano.
Modalidad individual confirmada como autorizada por el docente, según mensaje del alumno.
Objetivo personal: reutilizar y evolucionar TrendML para uso real futuro.

## Datos disponibles

La auditoría de solo lectura de `backend/trendml.db` encontró 100 productos,
3.000 observaciones y 100 snapshots antiguos. Todas las observaciones usan IDs
`DEMO-`; no hay procedencia de datos reales acreditada. Fechas: 25 de mayo a 23 de
junio de 2026. El código de `seed_demo.py` genera ventas, precios y predicciones
aleatoriamente. El alumno confirmó que aún no tiene registros propios ni cuenta
vendedora para este flujo.

Se hicieron dos GET sin credenciales desde este equipo: búsqueda de auriculares
con límite 1 y metadatos del sitio MLA. Ambos respondieron HTTP 403. Esto demuestra
que no obtuvimos datos por ese camino, no que toda la API sea inaccesible para una
cuenta autorizada. No se generaron ni descargaron ventas ficticias como alternativa.

La documentación oficial describe consultas autenticadas y restringe la información
privada del vendedor: [Ítems y búsquedas](https://developers.mercadolibre.com.ar/es_ar/publica-productos/items-y-busquedas).
El recolector ahora requiere token y vendedor propios, verifica titularidad, consulta
sus publicaciones y rechaza cantidades ausentes en lugar de inventar ceros.
El recolector autenticado fue probado con fixtures y SQLite; no con una cuenta real.

Existe otra fuente **real histórica** para una evaluación académica:
[UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail), de Daqing Chen
(2015), DOI 10.24432/C5BW33, licencia CC BY 4.0. Contiene transacciones de un comercio
británico de 2010–2011, con fechas, productos, unidades y precios. Se verificó su ficha;
no se descargó ni se integró en esta tarea. Es una opción para el próximo paso,
con atribución y tratamiento explícito de devoluciones, cancelaciones, monedas y
agregación diaria. No representa Mercado Libre Argentina ni demanda actual.

## Cambios implementados

1. Objetivo: incremento del acumulado de ventas en siete días, con tolerancia de una hora.
2. Datos para inferencia separados de los pares con objetivo conocido: se usa la última
   fila válida, y no se etiqueta una predicción antigua como actual si la última fila es inválida.
3. Entrenamiento sin objetivos posteriores a la fecha de la observación predicha.
4. Rechazo de datos no finitos, negativos, fechas duplicadas e historial sin procedencia;
   recorte del historial después del último reinicio del contador.
5. Una sola implementación del modelo y persistencia para backend y worker.
6. Tabla nueva de resultados con valor nullable y estado; las cifras legacy o aleatorias
   dejan de alimentar `/api/predictions`.
7. Procesamiento idempotente y manejo de excepción del modelo conservando análisis convencional.
8. Pantalla diferencia datos no verificados, insuficiencia, error y estimación disponible.
9. Migración aditiva y recolector compatible con SQLite mediante ORM.

El campo histórico `predicted_sales_next_week` se conserva en snapshots para compatibilidad
con la base, pero la API usa exclusivamente `weekly_predictions`. La API cambió: valor nullable,
metadatos y ausencia de `current_sales`; otros consumidores deberán adaptarse.

## Verificación ejecutada

- 17 pruebas automatizadas aprobadas con `unittest`, en SQLite temporal.
- Comprobación TypeScript: `tsc --noEmit`, sin errores.
- Worker sobre copia de la base local: 100 productos procesados.
- Consulta del servicio y validación Pydantic: 100 resultados `unverified_data`,
  cero cifras mostradas como predicciones reales.
- La base original se leyó y copió para validar; no se modificó ni se ejecutó el seed.
- Sin envíos de email, pagos, publicación de cambios o uso de credenciales reales.

Los fixtures prueban contratos y regresiones; no validan precisión comercial. Un
fixture etiquetado `verified_import` dentro de una prueba no se presenta como dato real.
La migración y el recolector tienen pruebas SQLite; Docker/PostgreSQL y la pantalla en
navegador no se verificaron en esta sesión. Los cambios están locales, sin commit ni push.

## Pendientes para uso real

- Reunir historial real propio o integrar el conjunto UCI con procedencia y licencia.
- Mantener historial diario durante semanas, o disponer de exportaciones fechadas.
- Separar entrenamiento y evaluación por tiempo con purga de los siete días de horizonte.
- Medir MAE frente a referencia de ventas de la semana anterior, por producto y período.
- Comprobar permisos y exactitud del contador de ventas; una cifra redondeada no es un objetivo exacto.
- Definir antigüedad máxima del resultado y evitar recomendar stock con datos vencidos.
- Medir latencia y carga: el prototipo reentrena para cada observación final de producto.
- Gestionar tokens vencidos/renovación y comprobar PostgreSQL antes de despliegue real.

## Registro de asistencia de IA

| Herramienta | Etapa | Uso | Resultado | Revisión |
|---|---|---|---|---|
| Codex | Análisis | Auditoría de base y código; verificación pública | Datos demo y acceso 403 identificados | Evidencia de consulta; sin atribuir precisión |
| Codex | Diseño | Separar resultado semanal del snapshot legacy | Tabla y contrato con estados explícitos | Aplicados y comprobados con pruebas |
| Codex | Desarrollo | Corregir modelo, worker, API, ingesta y pantalla | Código local | Validación funcional parcial, sin producción |
| Codex | Pruebas | Casos temporales, límites, persistencia y origen | 17 pruebas aprobadas | Fixtures; evaluación real pendiente |
| Codex | Gestión | Actualizar grupo y estado del integrador | Documento actualizado | Modalidad confirmada por alumno |
