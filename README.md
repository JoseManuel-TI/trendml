# TrendML

Proyecto integrador de Desarrollo de Software con Inteligencia Artificial. Jose Manuel Castro Reina, grupo 14 individual; docente Matias Arellano.

TrendML ofrece registro, acceso, tendencias, alertas de precio e inferencia semanal con un modelo propio. La entrega académica usa un catálogo sintético claramente identificado y un laboratorio UCI con ventas históricas reales británicas de 2010–2011. **No es una predicción comercial validada para Mercado Libre.**

## Arranque local

Requisitos: Python 3.9 o posterior compatible con las dependencias fijadas; Node.js 18.17 o posterior y npm. Validado en macOS con SQLite. Ejecutar desde la raíz del repositorio.

```bash
bash scripts/setup_local.sh       # primera instalación; no sobrescribe .env existente
bash scripts/train_academic.sh    # descarga pública, preparación y entrenamiento v3
bash scripts/start_academic.sh    # API 8000 e interfaz 3000
```

Si el archivo UCI ya existe, no se vuelve a descargar. La preparación del XLSX puede tardar. Esperar a que termine antes de iniciar la demo. No se requiere clave de IA ni cuenta Mercado Libre.

Abrir http://localhost:3000/login y pulsar **Entrar como demo**.

| Cuenta local | Contraseña de demostración | Permisos |
|---|---|---|
| demo@example.com | DemoTrendML123! | Pro |
| starter@example.com | DemoTrendML123! | Starter |

Son cuentas públicas de prueba, solo para la demo local. La base de demostración es `work/academic.db`, separada de la base anterior. El seed es idempotente. El arranque escucha solo en loopback y se detiene con Ctrl+C. Si un puerto está ocupado, detener la instancia anterior; el script no elimina procesos ajenos.

## Recorrido

1. `/register`: crear cuenta Starter; validación de correo y contraseña en API.
2. `/login`: acceso JWT; `/dashboard`: tendencias, alertas y estado de predicciones. El catálogo DEMO no genera predicciones falsamente válidas.
3. `/forecast`: seleccionar un producto histórico y calcular. La API carga el modelo local y ejecuta `predict` en cada solicitud. Muestra unidades, horizonte histórico, fecha del cálculo y referencia de cuatro semanas.
4. `/training`: consultar evaluaciones ya calculadas. Esta pantalla por sí sola no entrena ni ejecuta inferencia.
5. `/pricing`: explicación de permisos, sin pagos. La API impide checkout y cambios de plan en modo académico.

## IA reproducible

Fuente: [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail), Daqing Chen (2015), DOI 10.24432/C5BW33, CC BY 4.0. La preparación conserva hash de archivo, reglas de filtrado, productos y fechas. El objetivo son unidades positivas brutas; devoluciones y cancelaciones excluidas. Los precios son GBP.

Entradas: 56 días completos de ventas y precios; características de 7, 14, 28 y 56 días. Salida: estimación no negativa para los siete días siguientes al corte. Modelo v3: boosting que corrige el promedio de cuatro semanas. División temporal con etiquetas conocidas al corte; referencias: semana anterior y promedio de cuatro semanas.

Archivos generados (ignorados por Git): `work/uci/prepared-v2.json`, `work/uci/weekly-model-v3.joblib` y `work/uci/evaluation-v3.json`. El script también publica métricas en `frontend/public/training-results-v3.json`. Cargar únicamente artefactos joblib entrenados localmente y confiables.

Resultados reproducidos el 31/10/2026: MAE de validación 374,26 frente a 380,00 de la referencia; noviembre 479,06 frente a 492,77. Los períodos ya fueron examinados: son resultados de desarrollo, no un test independiente ni una garantía comercial. Hay productos y períodos donde la referencia gana.

## Pruebas

```bash
bash scripts/check_academic.sh
```

Ejecuta unittest con base aislada y compilación de Next.js. La prueba del artefacto real requiere el entrenamiento previo; sin él se marca omitida expresamente. Evidencia: `docs/entrega/pruebas.txt`, `inferencias.json` y documentos de entrega.

## Arquitectura y trazabilidad

- FastAPI, SQLAlchemy, JWT: HU01, HU02, HU08.
- Analytics y dashboard: HU03, HU04.
- `backend/api/forecast.py`, `backend/services/forecast_service.py`, `/forecast`: HU05, HU06.
- `scripts/prepare_uci.py`, `train_uci_v3.py`: HU07 y HU05.
- Diseño, historias, pruebas y uso crítico de IA: `docs/entrega/Informe-final.md`.
- Guion independiente: `docs/entrega/Exposicion-clases.docx`.
- [Tablero Kanban](https://app.notion.com/p/28314a0e971e47468ef7160884411574).

## Configuración y límites

`ACADEMIC_MODE=true` por defecto: checkout bloqueado y registro sin correos externos. `start_academic.sh` fuerza este modo, proveedor de email local y DB aislada. `APP_SECRET` debe ser privado fuera de una demo. `FRONTEND_URL` controla CORS. `ADMIN_EMAILS` es una lista explícita de administradores; tener plan Premium no permite consultar datos administrativos.

El catálogo académico es compartido y no admite carga de ventas privadas de vendedores. El aislamiento multiempresa, cuenta Mercado Libre real, despliegue público, pagos, mensajería y PostgreSQL en producción quedan fuera de la entrega validada. El código heredado de estas integraciones se conserva, pero no implica que esté aprobado para producción. Los scripts antiguos de inicio/seed comercial no son necesarios para esta demo.

Los archivos `docs/academico/` describen el avance del 14/10. La versión de entrega actual está en `docs/entrega/`.
