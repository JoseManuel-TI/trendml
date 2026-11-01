# Material de entrega — TrendML

Jose Manuel Castro Reina · Grupo 14 individual · Docente Matias Arellano

## Orden recomendado

1. `Informe-final.docx`: metodología, ocho historias, diagramas, wireframes, integración de IA, pruebas y análisis crítico. `Informe-final.md` es su fuente editable.
2. `Plan-de-pruebas.md`: plan, resultados, diez casos de calidad de IA, adversarios y recorrido HTTP.
3. `Checklist-entrega.md`: evidencia por requisito y pasos pendientes antes de subir.
4. `Tablero-actualizaciones.md`: estado actual de Notion, sin inventar fechas.
5. `Exposicion-clases.docx`: guion oral; `Exposicion-clases.md` es su fuente editable.
6. Diagramas: `er.png`, `flujo-ia.png`, `wireframes-actuales.png`.
7. Evidencias: `demo-inferencia.png`, `inferencias.json`, `pruebas.txt`, `tablero-01.png` y `tablero-02.png`. La tercera captura se tomó el 01/11/2026 y está identificada en el checklist como pendiente de exportar al archivo `tablero-03.png`.
8. `ensayo-cronometrado.md`: tiempos estimados y registro vacío para la práctica oral real.

## Demostración

```bash
bash scripts/train_academic.sh   # solo si falta el modelo
bash scripts/start_academic.sh
```

Abrir http://localhost:3000/login, pulsar **Entrar como demo**, ir a **Predecir**, calcular y abrir la ficha técnica. Luego revisar **Entrenamiento**. La inferencia usa el modelo entrenado con UCI Online Retail, ventas históricas reales de 2010–2011; no representa ventas actuales propias ni de Mercado Libre.

## Límites que deben mencionarse

- Datos operativos sintéticos identificados; no son ventas propias.
- Modelo histórico británico 2010–2011, sin validación comercial actual.
- Mejora pequeña y desigual frente a referencias simples; los períodos mostrados ya se inspeccionaron.
- Faltan datos propios, período independiente y aislamiento multiusuario para uso comercial.
- La captura tres se realizó en Notion, pero falta guardar su PNG en esta carpeta.
- El ensayo oral personal, la confirmación del turno y la publicación de la versión final siguen pendientes.
