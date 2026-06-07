# Panel de Costos Ocultos — Demo

Prototipo navegable de un **sistema autónomo de control para gastronomía**, construido
como respuesta directa a la publicación de Felix Viana (Grupo Viana) sobre los 10 puntos
críticos de "costos ocultos" en restaurantes.

La idea: en vez de comentar "totalmente de acuerdo 👏", mostrar — con un panel funcionando —
cómo se vería cada uno de esos 10 puntos resuelto en un sistema único, navegable, con datos
en tiempo real.

## Estructura del proyecto

```
panel-costos-ocultos/
├── app.py                      ← App Streamlit (panel completo, 6 secciones)
├── data/
│   ├── financiero.json         ← 30 días de ingresos vs. costos (simulado)
│   ├── inventario.json         ← Stock con fechas de vencimiento (FIFO)
│   ├── decomisos.json          ← Registro de mermas, declaradas y no declaradas
│   ├── energia.json            ← Zonas con consumo energético fuera de horario
│   ├── fichas_tecnicas.json    ← Costo teórico vs. real por plato
│   └── equipo.json             ← Conocimiento de menú y rotación de mozos
├── .streamlit/config.toml
├── requirements.txt
├── pitch/
│   └── comentario_linkedin.md  ← Borrador del comentario para la publicación de Felix
└── README.md
```

## Cómo correr la demo

```bash
cd "/Users/martinhulais/Trabajo Claude/proyectos/panel-costos-ocultos"
pip install -r requirements.txt
streamlit run app.py
```

Abrir en el navegador: **http://localhost:8501**

## Qué resuelve cada sección (mapeo a los 10 puntos del post de Felix)

| Pestaña | Puntos del post que ataca |
|---|---|
| 📊 Resumen financiero | 1. Administración financiera ineficiente · 2. Multiplicidad de desvíos |
| 📦 Inventario & FIFO | 5. Falta de aplicación del método FIFO · 8. Desconocimiento del inventario |
| 🗑️ Decomisos | 3. Decomisos no declarados |
| ⚡ Energía | 4. Consumo energético innecesario |
| 📋 Fichas técnicas | 6. Falta de estandarización · 10. Ausencia de fichas técnicas |
| 👥 Equipo & capacitación | 7. Fallas en la selección de personal · 9. Falta de conocimiento en los camareros |

## Notas importantes

- **Todos los datos son simulados.** El panel está diseñado para conectarse a información
  real: POS/caja, planillas de stock, sensores de temperatura y movimiento.
- **No se mencionan ni se inventan datos de ningún restaurante real.** El "local demo"
  es genérico a propósito — sirve como vidriera conceptual, no como acusación a nadie.
- Pensado como **pieza de apertura de conversación**, no como producto terminado: el
  objetivo es que Felix (o cualquiera que vea el comentario) entienda en 2 minutos de
  qué se trata el sistema y quiera saber más — sin regalar toda la arquitectura ni el
  modelo de precios en el primer contacto.

## Próximo paso

Publicar el comentario de `pitch/comentario_linkedin.md` en la publicación de Felix Viana
con el link a esta demo (cuando esté deployada — ver sección "Deploy" más abajo).

## Deploy rápido (para compartir el link)

Streamlit Community Cloud es gratis y alcanza para esto:
1. Subir el repo a GitHub (público o privado con acceso).
2. https://share.streamlit.io → "New app" → seleccionar el repo y `app.py`.
3. Copiar el link público (`https://<usuario>-panel-costos-ocultos.streamlit.app`) y
   pegarlo en el comentario de LinkedIn.
