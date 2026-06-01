# ⛰️ ⛏️ Minerales Críticos y Transición Energética 🪙✨

Aplicación de visualización de datos para el análisis de los cinco minerales críticos de la transición energética global: **cobre, níquel, cobalto, litio y platino**.

Desarrollada como Caso Práctico del Máster en Ciencia e Ingeniería de Datos - Facultad de Ingeniería Informática UNED.

🔗 **[Ver aplicación Streamlit en vivo](https://minerales-criticos-2026.streamlit.app)**

(en esta aplicación solo se muestran un parte de las visualizaciones de datos del trabajo).

---

## Objetivo e hipótesis principal

Queremos entender los factores y variables macroeconómicas que influyen en el precio y volatilidad de:
**cobre, níquel, cobalto, litio y platino**

> La hipótesis principal es que hay algo así como una "gramática" o una ecuación que pueda explicar por qué el precio de un material a nivel global fluctúa como las series históricas describen que fluctúa.

En este trabajo, exploramos si esto es posible. 

---

## Estructura del análisis (también en la aplicación)

El análisis aborda tres dimensiones cruzadas:

**1. Introducción + comportamiento de precios 📈**
   → Base 100, choques "compartidos", platino como outlier

**2. El lado de la demanda: ciclo macroeconómico 📊**
   → Datos de CFNAI, los 3 régimenes clave, el "despertar" del litio

**3. El lado de la oferta: concentración geopolítica e impacto de conflictos 🌍**
   → Índice HHI, violencia política, delay clave de 8-12 meses

**4. Síntesis: matriuz de riesgo estratégico 🪙**
   → Relación entre HHI × volatilitat, validación de hipòtesi con r=0.81




---

## Stack del trabajo

| Capa | Tecnología |
|---|---|
| Análisis | Python · Pandas · NumPy · Statsmodels |
| Visualización | Altair · Seaborn · Matplotlib|
| Aplicación | Streamlit |
| Fuentes de datos | IMF Primary Commodity Prices · World Bank Pink Sheet · Chicago Fed (CFNAI) · PMI · ACLED · USGS · FRED (DXY, FEDFUNDS) |

---

## Estructura del repositorio

```
minerales-criticos/
├── app.py                        # Aplicación Streamlit
├── requirements.txt              # Dependencias
├── data_processed/               # Datos limpios listos para análisis
│   ├── IMF_monthly_prices_clean.csv
│   ├── df_combinado_final.csv
│   ├── political_events.csv
│   ├── usgs_2005_2015_2025.csv
│   └── ...
└── README.md
```

---

## Instalación local

```bash
git clone https://github.com/AMaristany/minerales-criticos.git
cd minerales-criticos
pip install -r requirements.txt
streamlit run app.py
```

---

## Hallazgos principales

- **Tres regímenes históricos** en la relación macro–mineral: desconexión en los 90 (r = 0,13, p = 0,24), sincronización durante el superciclo chino 2002–2019 (r = 0,49, p < 0,001), y nuevo equilibrio post-covid (r = 0,33, p = 0,004).
- **El litio se sincroniza por primera vez** con el ciclo industrial a partir de 2020: el mercado ha dejado de moverse por el cemento y el acero para hacerlo por la electroquímica (baterías y EVs).
- **El delay geopolítico es de 8–12 meses**: las disrupciones en zonas de conflicto tardan casi un año en propagarse a los precios de mercado.
- **El dólar (DXY) es el principal driver financiero** del precio del cobre en frecuencia mensual (β = −1,32, p < 0,001).
- **Cobalto y níquel** ocupan el cuadrante de mayor riesgo estratégico: alta concentración geopolítica y alta volatilidad histórica simultáneamente.

---

*Albert Maristany Utrera · 2025*
