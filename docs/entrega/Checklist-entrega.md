# Checklist de entrega — TrendML

Jose Manuel Castro Reina · Grupo 14 individual · Docente Matias Arellano  
Revisión: 1 de noviembre de 2026

**Leyenda:** ☑ con evidencia local o verificable · ◐ preparado/implementado pero falta completar la evidencia final · ☐ pendiente

## Documento

- ☑ Metodología ágil explicada: Kanban individual, roles, eventos de trabajo aplicados, WIP 1 y flujo. `Informe-final.md`, sección 2.
- ☑ Ocho historias con criterios de aceptación; HU05 cubre la funcionalidad de IA. `Informe-final.md`, sección 4.
- ☑ Diagrama ER: `er.png`.
- ☑ Wireframes de pantallas principales: `wireframes-actuales.png`.
- ☑ Integración de IA con entradas, API/modelo, respuesta y uso posterior: `flujo-ia.png` y `Informe-final.md`, sección 6.
- ☑ Plan y resultados de pruebas, incluidos casos de calidad/adversarios de IA: `Plan-de-pruebas.md`, `pruebas.txt`, `inferencias.json`.
- ☑ Tabla de uso de IA en análisis, gestión, diseño, desarrollo y pruebas, con revisión crítica: `Informe-final.md`, sección 9.

## Tablero de tareas

- ◐ Capturas en al menos tres momentos: están guardadas `tablero-01.png` y `tablero-02.png` (ambas del 31/10/2026 y con estados diferentes). El 01/11/2026 se tomó una tercera captura real en Notion, visible en la conversación y con T13 ya finalizada, pero falta exportarla/guardarla como `tablero-03.png` dentro de esta carpeta antes de adjuntar la entrega.
- ☑ Las tarjetas se vinculan con HU01–HU08 e identifican las tareas de IA. Tablero Notion: https://app.notion.com/p/28314a0e971e47468ef7160884411574
- ☑ WIP máximo 1; al 01/11/2026, T03 está En proceso. La pasada oral de T08 sigue Pendiente.

## Repositorio

- ☑ Repositorio público: https://github.com/JoseManuel-TI/trendml. Versión académica publicada en la rama [codex/entrega-academica](https://github.com/JoseManuel-TI/trendml/tree/codex/entrega-academica).
- ☑ README con instalación, entrenamiento, ejecución, configuración académica y límites de IA.
- ☑ Hay al menos cuatro funcionalidades trazables (registro/acceso, tendencias, alertas y predicción IA); la inferencia histórica con el modelo guardado fue ejecutada y probada. Código y documentos están publicados en la rama académica indicada.
- ☑ Historial con commits incrementales; el paquete de entrega quedó publicado en el commit `9a82c1b` de la rama académica.

## Exposición oral

- ◐ La aplicación contiene inferencia con datos históricos reales de UCI Online Retail y hay evidencia local de ejecución; el usuario debe realizar la demostración en vivo durante la exposición. UCI son ventas históricas británicas de 2010–2011, no ventas actuales propias ni de Mercado Libre.
- ☑ Guion preparado para explicar Kanban y Notion: `Exposicion-clases.md` / `.docx`.
- ☑ Registro y análisis crítico de herramientas de IA incluidos en el informe.
- ◐ Exposición individual: Jose Manuel Castro Reina es el único integrante y el docente autorizó esta modalidad, según lo informado por el estudiante. Falta realizar la exposición y confirmar el turno.
- ◐ Hoja con tiempos de referencia lista en `ensayo-cronometrado.md`; la práctica oral personal con cronómetro aún no se ha realizado ni registrado.

## Para cerrar antes de subir

1. Guardar la tercera captura real como `tablero-03.png` y revisar que no muestre información privada.
2. Entregar el enlace a la rama `codex/entrega-academica`, donde están el README, el código y los documentos revisados.
3. La rama publicada incluye evidencia de 37 pruebas y compilación frontend correctas; usar esa rama para la revisión académica.
4. Hacer al menos una pasada oral con cronómetro y completar el registro de `ensayo-cronometrado.md`.
5. Llevar el sistema levantado y el modelo entrenado para hacer la inferencia en vivo; explicar que son datos históricos UCI y declarar sus límites.
6. Confirmar con el docente el horario de exposición.

## Límites que deben quedar claros en la entrega

- Los datos de operación del dashboard son sintéticos e identificados; no son ventas propias.
- El modelo usa ventas históricas UCI y aún no está validado para el mercado actual.
- La mejora frente a la referencia simple es pequeña y no uniforme; noviembre ya fue examinado y no es una prueba independiente.
- No se verificó una cuenta vendedora de Mercado Libre ni el aislamiento multiusuario en producción.
