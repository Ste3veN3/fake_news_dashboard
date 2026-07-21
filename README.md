# Estilometría de Noticias — Panel Exploratorio

Proyecto Final · Visualización de Datos · USFQ
Autor: Steeven Quezada

## Qué es esto

Panel interactivo que explora diferencias de **estilo de escritura** (no de contenido)
entre noticias falsas y verdaderas, usando únicamente variables ya calculadas en el
preprocesamiento (sin modelos de clasificación).

## Marco de diseño

Además del Nested Model de Munzner (usado en todo el curso), el panel se clasifica según
la taxonomía de visualización de texto revisada en la Semana 4
([IEEE PacificVis 2015, vía textvis.lnu.se](https://ieeexplore.ieee.org/document/7156366)):

| Categoría | Aplicado a este dashboard |
|---|---|
| **Analytic Tasks** | Lexical/Syntactical Analysis (conteos estilométricos: exclamaciones, preguntas, longitud) + Comparison (falsa vs. verdadera) |
| **Visualization Tasks** | Comparison (A, B), Region of Interest / brushing (A→C), Categorization (D) |
| **Domain** | Editorial Media — noticias políticas en inglés, EE.UU., 2015-2017 |
| **Data** | Corpus/Document — 3,000 artículos con atributos categóricos (`subject`, clase) y cuantitativos (features estilométricas) |
| **Visualization** | 2D — jitter + boxplot (A), bar chart horizontal ordenado (B), ficha de texto (C), stacked bar 100% (D) |

## Pipeline de datos (reproducible de principio a fin)

```
Fake.csv + True.csv (Kaggle, 44,898 registros crudos)
        │
        ▼
notebooks/01_exploracion_inicial.ipynb   (EDA: limpieza, deduplicación, features lingüísticas)
        │  → data/processed/dataset_final.csv (38,473 registros)
        ▼
notebooks/02_preprocesamiento.ipynb      (limpieza NLP: stopwords, lematización — usa src/preprocessing.py)
        │  → data/processed/dataset_preprocessed.csv (38,473 registros)
        ▼
notebooks/03_muestreo.ipynb              (muestreo estratificado 1,500/1,500 + verificación Cohen's d)
        │  → data/processed/dataset_muestra.csv (3,000 registros) ← usado por app.py
        ▼
app.py (Streamlit)
```

Cada notebook guarda sus resultados impresos (conteos, tiempos, verificaciones) dentro
del propio archivo — evidencia de que ya se ejecutó, sin necesidad de volver a correrlos
para confirmar que funcionan.

### Reproducibilidad verificada

`03_muestreo.ipynb` usa `random_state=42`. Al re-ejecutarlo, los 5 valores de Cohen's d
salen idénticos:

| Variable | Cohen's d | Mann-Whitney p |
|---|---|---|
| title_length | 1.48 | 4.33e-279 |
| questions | 0.71 | 1.74e-141 |
| avg_word_len | -0.58 | 9.37e-96 |
| exclamations | 0.54 | 1.88e-81 |
| text_length | 0.19 | 4.00e-09 |

## Cómo correr el dashboard

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre automáticamente en `http://localhost:8501`. `data/processed/dataset_muestra.csv` ya está
incluido — no hace falta correr el pipeline completo solo para ver el dashboard.

## Cómo regenerar los datos desde cero (opcional)

1. Descargar `Fake.csv` y `True.csv` desde [Kaggle — Fake and Real News](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset)
   y colocarlos en `data/raw/`.
2. Correr `notebooks/01_exploracion_inicial.ipynb`.
3. Correr `notebooks/02_preprocesamiento.ipynb` (tarda ~31 min la primera vez; si
   `data/processed/dataset_preprocessed.csv` ya existe, lo carga directo en segundos).
4. Correr `notebooks/03_muestreo.ipynb`.

Los archivos intermedios (`dataset_final.csv`, `dataset_preprocessed.csv`, ~38,473 filas
con texto completo) no se incluyen en este repositorio por tamaño — se regeneran con los
pasos de arriba. Solo `data/processed/dataset_muestra.csv` (el que usa el dashboard) sí está incluido.

## Dataset

["Fake and Real News"](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset)
(Kaggle, Ahmed et al.) — noticias en inglés, contexto político de EE.UU., 2015-2017.

**Nota metodológica:** las etiquetas se basan en la fuente de origen (Reuters.com =
verdadera; sitios marcados como no confiables por PolitiFact/Wikipedia = falsa), no en
verificación de hechos artículo por artículo — una limitación reconocida en la literatura
del dataset, no propia de este proyecto.

## Estado del proyecto

- [x] **Componente A** — Distribución por clase (boxplot + jitter), con brushing real:
      selecciona puntos arrastrando (box o lasso) para ver los artículos exactos.
- [x] **Componente B** — Variables más discriminantes (ranking por Cohen's d), sincronizado
      con el selector de A al hacer clic en una barra.
- [x] **Componente C** — Explorador de casos individuales, poblado por la selección de
      la tabla de A: ficha completa del artículo con z-scores frente a su propia clase.
- [x] **Componente D** — Composición del dataset por `subject` (barra 100% apilada,
      normalizada) — expone el leakage de la variable `subject` como límite metodológico.

## Estructura

```
├── app.py                          # aplicación Streamlit
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml                 # tema fijo (evita el modo oscuro automático)
├── notebooks/
│   ├── 01_exploracion_inicial.ipynb
│   ├── 02_preprocesamiento.ipynb
│   └── 03_muestreo.ipynb
├── src/
│   └── preprocessing.py            # usado por 02_preprocesamiento.ipynb
└── data/
    └── processed/
        └── dataset_muestra.csv      # usado por app.py
```