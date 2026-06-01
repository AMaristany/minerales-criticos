# ⛏️ Minerales Críticos y Transición Energética

Aplicación de visualización de datos para el análisis de los cinco minerales críticos que vertebran la transición energética global: **cobre, níquel, cobalto, litio y platino**.

Desarrollada como Caso Práctico del Máster en Data Science e Ingeniería de Datos · UNED.

🔗 **[Ver aplicación en vivo](https://minerales-criticos.streamlit.app)**

---

## Hipótesis

> *A mayor concentración geopolítica de la producción minera, mayor volatilidad histórica del precio del mineral.*

Los datos la validan con una correlación de **r = 0,81** para los cuatro metales industriales de la transición energética (excluido el platino, que opera bajo lógicas de metal precioso y activo de reserva).

---

## Estructura del análisis

El análisis aborda tres dimensiones cruzadas:

**📈 Precios y volatilidad**
Evolución histórica desde 2000 en índice base 100, shocks compartidos (crisis 2008, COVID-19, guerra en Ucrania) y volatilidad rolling anualizada por mineral. Se valida la fuente IMF frente al Banco Mundial (Pink Sheet) y se normalizan unidades heterogéneas.

**🌍 Geopolítica**
Correlación entre eventos de violencia política (ACLED) y precios con análisis de delay óptimo (0–12 meses). Concentración de la producción mediante el índice Herfindahl-Hirschman (HHI) para 2005, 2015 y 2025.

**📊 Macroeconomía**
Correlación dinámica (ventana móvil 36 meses) con el CFNAI (Chicago Fed National Activity Index, compuesto por 85 indicadores). Análisis por subperiodos históricos y regresión OLS multivariable con DXY y tipos de interés como controles.

---

## Stack técnico

| Capa | Tecnología |
|---|---|
| Análisis | Python · Pandas · NumPy · SciPy · Statsmodels |
| Visualización | Altair |
| Aplicación | Streamlit |
| Fuentes de datos | IMF Primary Commodity Prices · World Bank Pink Sheet · ACLED · USGS · Chicago Fed (CFNAI) · FRED (DXY, FEDFUNDS) |

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
- **El litio se sincroniza por primera vez** con el ciclo industrial a partir de 2020: el mercado ha dejado de moverse por el cemento y el acero para hacerlo por la electroquímica.
- **El delay geopolítico es de 8–12 meses**: las disrupciones en zonas de conflicto tardan casi un año en propagarse a los precios de mercado.
- **El dólar (DXY) es el principal driver financiero** del precio del cobre en frecuencia mensual (β = −1,32, p < 0,001).
- **Cobalto y níquel** ocupan el cuadrante de mayor riesgo estratégico: alta concentración geopolítica y alta volatilidad histórica simultáneamente.

---

*Albert Maristany Utrera · 2025*
