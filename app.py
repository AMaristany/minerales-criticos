"""
app.py — Minerales Críticos y Transición Energética
Visualización de datos · UNED Máster Data Science
"""

import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

alt.data_transformers.disable_max_rows()

st.set_page_config(
    page_title="Minerales Críticos",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .stMetric { background: #f8f9fa; padding: 1rem; border-radius: 8px; }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.3rem !important; color: #333; border-bottom: 1px solid #eee; padding-bottom: .4rem; margin-top: 1.5rem; }
    .insight-box {
        background: #f0f4f8;
        border-left: 4px solid #2c7bb6;
        padding: 0.8rem 1rem;
        border-radius: 0 6px 6px 0;
        margin: 0.8rem 0 1.2rem 0;
        font-size: 0.92rem;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

def insight(texto):
    st.markdown(f'<div class="insight-box">💡 {texto}</div>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    df_imf   = pd.read_csv('data_processed/IMF_monthly_prices_clean.csv',
                           parse_dates=['date'], index_col='date')
    df_acled = pd.read_csv('data_processed/political_events.csv',
                           parse_dates=['date'], index_col='date')
    df_usgs  = pd.read_csv('data_processed/usgs_2005_2015_2025.csv')
    df_final = pd.read_csv('data_processed/df_combinado_final.csv',
                           parse_dates=['index'], index_col='index')
    df_final.index.name = 'date'
    return df_imf, df_acled, df_usgs, df_final

df_imf, df_acled, df_usgs, df_final = load_data()

METALES       = ['copper', 'nickel', 'platinum', 'cobalt', 'lithium']
METALES_LABEL = {'copper': 'Cobre', 'nickel': 'Níquel', 'platinum': 'Platino',
                 'cobalt': 'Cobalto', 'lithium': 'Litio'}
PAISES        = ['Democratic Republic of Congo', 'South Africa', 'Chile', 'Peru', 'Indonesia']

with st.sidebar:
    st.title("⛏️ Minerales Críticos")
    st.caption("Análisis de precios, geopolítica y concentración minera global")
    st.divider()
    seccion = st.radio(
        "Sección",
        ["Introducción", "Precios", "Volatilidad", "Geopolítica", "Macroeconomía", "Riesgo Estratégico"],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("UNED · Máster Data Science · Visualización de Datos")

# ═══════════════════════════════════════════════════════════════
# INTRODUCCIÓN
# ═══════════════════════════════════════════════════════════════
if seccion == "Introducción":
    st.title("Minerales Críticos y Transición Energética")
    st.markdown("""
    La transición energética global depende de un puñado de minerales cuya producción está
    altamente concentrada en pocos países. Esta aplicación analiza la **gramática de precios**
    de cinco minerales críticos — cobre, níquel, cobalto, litio y platino — cruzando tres
    dimensiones de análisis:

    - 📈 **Precios y volatilidad** — evolución histórica desde 2000, shocks compartidos y comportamiento diferencial entre minerales
    - 🌍 **Geopolítica** — correlación entre inestabilidad política y precios, y concentración de la producción (HHI)
    - 📊 **Macroeconomía** — relación con el ciclo económico global (CFNAI) y el índice del dólar (DXY)

    La hipótesis de partida es que **a mayor concentración geopolítica de la producción, mayor
    volatilidad histórica del precio**. Los datos la validan con una correlación de r = 0.81
    para los cuatro metales industriales de la transición energética.
    """)

    st.subheader("Último precio disponible")
    df_last = df_imf[METALES].dropna().iloc[-1]
    cols = st.columns(5)
    for i, m in enumerate(METALES):
        prev = df_imf[m].dropna().iloc[-2]
        delta_pct = (df_last[m] - prev) / prev * 100
        cols[i].metric(METALES_LABEL[m], f"${df_last[m]:,.0f}", f"{delta_pct:+.1f}%")
    st.caption(f"Fuente: IMF Primary Commodity Prices · Último dato disponible: {df_imf[METALES].dropna().index[-1].strftime('%b %Y')}")

# ═══════════════════════════════════════════════════════════════
# PRECIOS
# ═══════════════════════════════════════════════════════════════
elif seccion == "Precios":
    st.title("Evolución de Precios")
    st.markdown("""
    Para comparar minerales con unidades heterogéneas ($/t, $/lb, $/troy oz), se normalizan
    todas las series a un **índice base 100 = enero 2000**. Esto permite ver la apreciación
    relativa de cada mineral independientemente de su escala de precio absoluto.
    """)

    insight("A simple vista emergen tendencias compartidas: hundimiento generalizado en 2008–2009 (crisis financiera global), recuperación posterior y un crecimiento post-covid. El platino, sin embargo, muestra un comportamiento discordante desde 2015, anticipando su clasificación como activo de refugio más que como metal industrial.")

    df_2000 = df_imf[df_imf.index >= '2000-01-01'][METALES].copy()
    df_idx  = (df_2000 / df_2000.ffill().bfill().iloc[0]) * 100
    df_long = (
        df_idx.reset_index()
        .melt(id_vars='date', value_vars=METALES, var_name='mineral', value_name='index_100')
        .dropna()
    )
    df_long['mineral'] = df_long['mineral'].map(METALES_LABEL)

    eventos = pd.DataFrame([
        {'date': pd.Timestamp('2008-09-15'), 'label': 'Crisis 2008'},
        {'date': pd.Timestamp('2020-03-01'), 'label': 'COVID-19'},
        {'date': pd.Timestamp('2022-02-24'), 'label': 'Ucrania'},
    ])

    sel = alt.selection_point(fields=['mineral'], bind='legend')
    lineas = (
        alt.Chart(df_long).mark_line(strokeWidth=2)
        .encode(
            x=alt.X('date:T', title='Fecha'),
            y=alt.Y('index_100:Q', title='Índice (Base 100 = Ene 2000)'),
            color=alt.Color('mineral:N', title='Mineral'),
            opacity=alt.condition(sel, alt.value(1), alt.value(0.12)),
            tooltip=[
                alt.Tooltip('date:T', title='Fecha', format='%b %Y'),
                alt.Tooltip('mineral:N', title='Mineral'),
                alt.Tooltip('index_100:Q', title='Índice', format='.1f'),
            ]
        ).add_params(sel)
    )
    reglas = (
        alt.Chart(eventos)
        .mark_rule(strokeDash=[5, 3], color='#999', strokeWidth=1.5)
        .encode(x='date:T', tooltip=alt.Tooltip('label:N', title='Evento'))
    )
    etiq = (
        alt.Chart(eventos)
        .mark_text(angle=270, align='left', dx=5, dy=-8, fontSize=10, color='#999')
        .encode(x='date:T', text='label:N')
    )
    st.altair_chart((lineas + reglas + etiq).properties(height=420).interactive(), use_container_width=True)
    st.caption("Haz clic en la leyenda para aislar un mineral · Scroll para hacer zoom")

    st.subheader("Nota metodológica")
    st.markdown("""
    Las series del FMI y del Banco Mundial (Pink Sheet) se validaron cruzándolas para los
    metales comunes (cobre, níquel, platino): el solapamiento es prácticamente perfecto, por
    lo que se usa la serie del FMI como fuente única por ser más completa. El cobalto requirió
    una conversión de unidades de $/libra a $/tonelada métrica (factor 2.204,62).
    """)

# ═══════════════════════════════════════════════════════════════
# VOLATILIDAD
# ═══════════════════════════════════════════════════════════════
elif seccion == "Volatilidad":
    st.title("Volatilidad Histórica")
    st.markdown("""
    La volatilidad se calcula como la desviación estándar del **retorno mensual** sobre una
    ventana deslizante de 12 meses, anualizada con el factor estándar √12. Trabajar con
    retornos en lugar de precios absolutos elimina el sesgo que introduce el nivel de precio:
    un mineral caro no es necesariamente más volátil.

    σ_anual = σ_mensual × √12
    """)

    insight("El cobalto y el litio muestran picos de volatilidad extremos y concentrados en el tiempo — shocks de oferta específicos de la transición energética. El cobre y el níquel, como metales industriales maduros, tienen una volatilidad más estructural y menos puntual. El platino mantiene una volatilidad amortiguada consistente con su rol de activo de reserva.")

    df_2000 = df_imf[df_imf.index >= '2000-01-01'][METALES].copy()
    df_vol  = df_2000.pct_change().rolling(12).std().dropna() * 100
    df_vol_long = (
        df_vol.reset_index()
        .melt(id_vars='date', value_vars=METALES, var_name='mineral', value_name='vol')
        .dropna()
    )
    df_vol_long['mineral'] = df_vol_long['mineral'].map(METALES_LABEL)

    sel2 = alt.selection_point(fields=['mineral'], bind='legend')
    chart_vol = (
        alt.Chart(df_vol_long).mark_area(opacity=0.45, strokeWidth=2)
        .encode(
            x=alt.X('date:T', title='Fecha'),
            y=alt.Y('vol:Q', title='Volatilidad mensual (%)'),
            color=alt.Color('mineral:N', title='Mineral'),
            opacity=alt.condition(sel2, alt.value(0.5), alt.value(0.05)),
            tooltip=[
                alt.Tooltip('date:T', title='Fecha', format='%b %Y'),
                alt.Tooltip('mineral:N', title='Mineral'),
                alt.Tooltip('vol:Q', title='Volatilidad (%)', format='.2f'),
            ]
        ).add_params(sel2).properties(height=400).interactive()
    )
    st.altair_chart(chart_vol, use_container_width=True)
    st.caption("Desviación estándar del retorno mensual, ventana 12 meses · Haz clic en la leyenda para aislar un mineral")

# ═══════════════════════════════════════════════════════════════
# GEOPOLÍTICA
# ═══════════════════════════════════════════════════════════════
elif seccion == "Geopolítica":
    st.title("El Factor Geopolítico")
    st.markdown("""
    La producción de minerales críticos está geográficamente concentrada en pocos países,
    muchos de ellos con alta inestabilidad política. Esta sección cuantifica esa concentración
    y su correlación con los precios usando datos de violencia política de ACLED.
    """)

    tab1, tab2, tab3 = st.tabs(["Concentración HHI", "Conflicto vs Precio", "RDC vs Cobalto"])

    with tab1:
        st.markdown("""
        El **índice Herfindahl-Hirschman (HHI)** mide la concentración de la producción:
        HHI = Σ(cuota_i)². Un HHI > 2.500 indica estructura de monopolio o duopolio geopolítico;
        entre 1.000 y 2.500, concentración moderada.
        """)
        insight("El cobalto (dominado por la RDC) y el litio (dominado por el triángulo Chile-Argentina-Australia) tienen HHI superiores a 2.500, situándolos en zona de riesgo estructural. El cobre, históricamente concentrado en Chile y Perú, muestra una tendencia a la baja gracias a la diversificación productiva.")

        df_p = df_usgs[~df_usgs['country'].isin(['World total', 'Other countries'])].copy()
        prod_total = df_p.groupby(['mineral', 'year'])['mine_production'].transform('sum')
        df_p['share_pct'] = (df_p['mine_production'] / prod_total) * 100
        df_p['hhi_comp']  = df_p['share_pct'] ** 2
        df_hhi = (
            df_p.groupby(['mineral', 'year'])['hhi_comp']
            .sum().reset_index().rename(columns={'hhi_comp': 'HHI'})
        )
        df_hhi['mineral'] = df_hhi['mineral'].str.capitalize()

        sel_hhi = alt.selection_point(fields=['mineral'], bind='legend')
        umbral_alto = alt.Chart(pd.DataFrame({'y': [2500]})).mark_rule(color='red', strokeDash=[6,3], strokeWidth=2).encode(y='y:Q')
        umbral_mod  = alt.Chart(pd.DataFrame({'y': [1000]})).mark_rule(color='orange', strokeDash=[4,2], strokeWidth=1.5).encode(y='y:Q')
        lineas_hhi = (
            alt.Chart(df_hhi).mark_line(point=True, strokeWidth=2.5)
            .encode(
                x=alt.X('year:O', title='Año'),
                y=alt.Y('HHI:Q', title='HHI'),
                color=alt.Color('mineral:N', title='Mineral'),
                opacity=alt.condition(sel_hhi, alt.value(1), alt.value(0.1)),
                tooltip=[
                    alt.Tooltip('mineral:N', title='Mineral'),
                    alt.Tooltip('year:O', title='Año'),
                    alt.Tooltip('HHI:Q', title='HHI', format='.0f'),
                ]
            ).add_params(sel_hhi)
        )
        st.altair_chart((umbral_alto + umbral_mod + lineas_hhi).properties(height=380), use_container_width=True)
        st.caption("Línea roja: umbral alta concentración (HHI > 2.500) · Línea naranja: concentración moderada (> 1.000)")

    with tab2:
        st.markdown("""
        Se calcula la correlación de Pearson entre los eventos de violencia política (ACLED)
        de cada país productor y el precio de cada mineral, probando delays de 0 a 12 meses
        y quedándose con el máximo.
        """)
        insight("Cuando las correlaciones son fuertes, el delay óptimo se sitúa en la ventana de 8 a 12 meses: la propagación de disrupciones en la cadena de suministro no es inmediata. La mayor correlación directa es entre el cobre y los eventos en Indonesia (r = 0,69). Cobre y níquel — metales con demanda similar — responden de forma muy distinta ante los mismos eventos, lo que subraya la utilidad de los controles geográficos.")

        df_acled_piv = df_acled.pivot(columns='country', values='violence_events')
        df_2000      = df_imf[df_imf.index >= '2000-01-01'][METALES]
        df_comb      = df_acled_piv.join(df_2000, how='inner')

        resultados = []
        for metal in METALES:
            for pais in PAISES:
                mejor_corr, mejor_delay = 0, 0
                for lag in range(0, 13):
                    c = df_comb[pais].shift(lag).corr(df_comb[metal])
                    if abs(c) > abs(mejor_corr):
                        mejor_corr, mejor_delay = c, lag
                resultados.append({'mineral': METALES_LABEL[metal], 'pais': pais,
                                   'corr': round(mejor_corr, 3), 'delay': mejor_delay})

        df_heat = pd.DataFrame(resultados)
        fondo = (
            alt.Chart(df_heat).mark_rect()
            .encode(
                x=alt.X('mineral:N', title='Mineral', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('pais:N', title='País'),
                color=alt.Color('corr:Q', scale=alt.Scale(scheme='redblue', domain=[-1,1]), title='r'),
                tooltip=[
                    alt.Tooltip('mineral:N', title='Mineral'),
                    alt.Tooltip('pais:N', title='País'),
                    alt.Tooltip('corr:Q', title='r', format='.3f'),
                    alt.Tooltip('delay:Q', title='Delay óptimo (meses)'),
                ]
            )
        )
        texto = (
            alt.Chart(df_heat).mark_text(fontSize=11)
            .encode(
                x='mineral:N', y='pais:N',
                text=alt.Text('corr:Q', format='.2f'),
                color=alt.condition(alt.datum.corr > 0.35, alt.value('white'), alt.value('black'))
            )
        )
        st.altair_chart((fondo + texto).properties(height=300), use_container_width=True)
        st.caption("Correlación máxima con delay óptimo 0–12 meses · Tooltip muestra el delay en meses")

    with tab3:
        st.markdown("""
        El cobalto se extrae mayoritariamente en la República Democrática del Congo (RDC),
        un país con conflicto armado crónico. Las dos series se normalizan a escala 0–1
        para permitir la comparación visual directa.
        """)
        insight("La inspección visual sugiere un desajuste temporal entre los picos de violencia y los picos de precio: la señal geopolítica tarda meses en propagarse a los mercados de materias primas a través de disrupciones logísticas y contractuales.")

        df_acled_piv = df_acled.pivot(columns='country', values='violence_events')
        df_geo = df_acled_piv[['Democratic Republic of Congo']].join(df_imf[['cobalt']], how='inner').dropna()
        df_geo.columns = ['violencia_rdc', 'cobalt']
        df_geo = df_geo.reset_index()
        for col in ['violencia_rdc', 'cobalt']:
            df_geo[f'{col}_norm'] = (df_geo[col] - df_geo[col].min()) / (df_geo[col].max() - df_geo[col].min())

        df_geo_long = df_geo.melt(id_vars='date', value_vars=['violencia_rdc_norm', 'cobalt_norm'],
                                  var_name='serie', value_name='valor')
        df_geo_long['serie'] = df_geo_long['serie'].map({'violencia_rdc_norm': 'Violencia RDC', 'cobalt_norm': 'Precio Cobalto'})

        chart_geo = (
            alt.Chart(df_geo_long).mark_line(strokeWidth=2)
            .encode(
                x=alt.X('date:T', title='Fecha'),
                y=alt.Y('valor:Q', title='Valor normalizado (0–1)'),
                color=alt.Color('serie:N',
                    scale=alt.Scale(domain=['Violencia RDC', 'Precio Cobalto'], range=['#D62728', '#1F77B4']),
                    title='Serie'),
                strokeDash=alt.condition(alt.datum.serie == 'Precio Cobalto', alt.value([6,3]), alt.value([1,0])),
                tooltip=[
                    alt.Tooltip('date:T', title='Fecha', format='%b %Y'),
                    alt.Tooltip('serie:N', title='Serie'),
                    alt.Tooltip('valor:Q', title='Valor norm.', format='.3f'),
                ]
            ).properties(height=360).interactive()
        )
        st.altair_chart(chart_geo, use_container_width=True)
        st.caption("Series normalizadas 0–1 · Línea punteada = precio cobalto")

# ═══════════════════════════════════════════════════════════════
# MACROECONOMÍA
# ═══════════════════════════════════════════════════════════════
elif seccion == "Macroeconomía":
    st.title("Relación con el Ciclo Económico")
    st.markdown("""
    Se usa el **CFNAI** (Chicago Fed National Activity Index) como proxy de actividad económica
    global: es un índice compuesto por 85 indicadores de la economía estadounidense donde
    el valor 0 representa crecimiento en la tendencia histórica. Se valida primero su correlación
    con el PMI manufacturero (r = 0,68), aceptable dado el nivel de ruido de ambas series.

    El análisis principal es la **correlación móvil de Pearson** con una ventana de 36 meses,
    que permite capturar cómo evoluciona la relación entre macroeconomía y precio a lo largo
    del tiempo — en lugar de una correlación estática que promediaría épocas muy distintas.
    """)

    insight("El análisis por subperiodos revela tres regímenes históricos bien diferenciados: los años 90 muestran desconexión total (r = 0,13, p = 0,24); el superciclo impulsado por China 2002–2019 activa la relación (r = 0,49, p < 0,001); y el periodo post-covid la estabiliza en un nuevo equilibrio (r = 0,33, p = 0,004). El litio, ausente del ciclo industrial tradicional, se sincroniza por primera vez con el resto de metales a partir de 2020: el mercado ha dejado de moverse por el cemento y el acero, y ahora lo hace por la electroquímica.")

    metales_macro = ['copper', 'lithium', 'nickel', 'cobalt', 'platinum']
    ventana = 36

    for m in metales_macro:
        col = f'{m}_retorno_mensual'
        if col not in df_final.columns:
            df_final[col] = df_final[m].pct_change()
    if 'CFNAI_suavizado' not in df_final.columns:
        df_final['CFNAI_suavizado'] = df_final['CFNAI'].rolling(3).mean()

    corr_dict = {}
    for m in metales_macro:
        corr_dict[m] = (
            df_final['CFNAI_suavizado']
            .rolling(window=ventana)
            .corr(df_final[f'{m}_retorno_mensual'])
        )

    df_corr = pd.DataFrame(corr_dict)
    df_corr_long = (
        df_corr.reset_index()
        .melt(id_vars='date', value_vars=metales_macro, var_name='mineral', value_name='corr')
        .dropna(subset=['corr'])
    )
    df_corr_long['mineral'] = df_corr_long['mineral'].map(METALES_LABEL)

    sel3 = alt.selection_point(fields=['mineral'], bind='legend')
    era_ev = pd.DataFrame([{'start': pd.Timestamp('2015-01-01'), 'end': df_corr.index.max()}])

    banda  = alt.Chart(era_ev).mark_rect(color='#DDDDDD', opacity=0.35).encode(x='start:T', x2='end:T')
    cero   = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(strokeDash=[6,3], color='black', strokeWidth=1.5).encode(y='y:Q')
    lineas_corr = (
        alt.Chart(df_corr_long).mark_line(strokeWidth=2.5)
        .encode(
            x=alt.X('date:T', title='Año'),
            y=alt.Y('corr:Q', title='Correlación (r)', scale=alt.Scale(domain=[-1,1])),
            color=alt.Color('mineral:N', title='Mineral'),
            opacity=alt.condition(sel3, alt.value(1), alt.value(0.08)),
            tooltip=[
                alt.Tooltip('date:T', title='Fecha', format='%b %Y'),
                alt.Tooltip('mineral:N', title='Mineral'),
                alt.Tooltip('corr:Q', title='r', format='.3f'),
            ]
        ).add_params(sel3)
    )
    etiq_ev = (
        alt.Chart(pd.DataFrame([{'x': pd.Timestamp('2015-06-01'), 'y': 0.88, 'text': 'Era EV'}]))
        .mark_text(fontSize=10, color='gray', align='left')
        .encode(x='x:T', y='y:Q', text='text:N')
    )
    st.altair_chart((banda + cero + lineas_corr + etiq_ev).properties(height=420).interactive(), use_container_width=True)
    st.caption("Ventana móvil 36 meses · Zona gris = Era de la Transición Energética (desde 2015) · Clic en leyenda para aislar")

    st.subheader("Regresión de control OLS")
    st.markdown("""
    Para confirmar la robustez del CFNAI, se realiza una regresión multivariable OLS con tres
    predictores macroeconómicos sobre el retorno mensual del cobre. El único predictor
    estadísticamente significativo en frecuencia mensual es el índice del dólar **DXY**
    (β = −1,32, p < 0,001), confirmando la relación inversa clásica entre dólar fuerte y precio
    del cobre. El CFNAI y los tipos de interés no son significativos en frecuencia mensual
    (p = 0,21 y p = 0,13), lo que no contradice el análisis dinámico anterior: su influencia
    es estructural y de largo plazo, no un shock mensual inmediato.
    """)

# ═══════════════════════════════════════════════════════════════
# RIESGO ESTRATÉGICO
# ═══════════════════════════════════════════════════════════════
elif seccion == "Riesgo Estratégico":
    st.title("Matriz de Riesgo Estratégico")
    st.markdown("""
    La hipótesis central del trabajo es que **la concentración geopolítica de la producción
    se traduce en mayor volatilidad de precios**. Esta sección la valida cruzando el HHI de
    2025 de cada mineral con su volatilidad histórica anualizada.
    """)

    insight("El cobalto y el níquel ocupan el cuadrante de mayor riesgo combinado (alta concentración + alta volatilidad). La inclusión del platino en el análisis global penaliza la correlación (r = 0,46) porque opera como activo de reserva y su volatilidad se disocia de los choques de oferta de la transición energética. Aislándolo metodológicamente, la correlación entre HHI y volatilidad para los cuatro metales industriales sube a r = 0,81 — validando la hipótesis de partida.")

    df_p = df_usgs[~df_usgs['country'].isin(['World total', 'Other countries'])].copy()
    prod_total = df_p.groupby(['mineral', 'year'])['mine_production'].transform('sum')
    df_p['share_pct'] = (df_p['mine_production'] / prod_total) * 100
    df_p['hhi_comp']  = df_p['share_pct'] ** 2
    df_hhi_all = (
        df_p.groupby(['mineral', 'year'])['hhi_comp']
        .sum().reset_index().rename(columns={'hhi_comp': 'HHI'})
    )
    df_hhi_2025 = df_hhi_all[df_hhi_all['year'] == 2025].set_index('mineral')[['HHI']]
    df_hhi_2025.index = df_hhi_2025.index.str.lower()

    metales_riesgo = ['copper', 'lithium', 'nickel', 'cobalt']
    vols = {}
    for m in metales_riesgo:
        col = f'{m}_retorno_mensual'
        if col not in df_final.columns:
            df_final[col] = df_final[m].pct_change()
        vols[m] = df_final[col].std() * (12 ** 0.5) * 100

    df_vol_an = pd.DataFrame.from_dict(vols, orient='index', columns=['vol'])
    df_riesgo = df_hhi_2025.join(df_vol_an).dropna().reset_index()
    df_riesgo.columns = ['mineral', 'HHI', 'vol']
    df_riesgo['mineral'] = df_riesgo['mineral'].str.capitalize()

    media_vol = df_riesgo['vol'].mean()

    puntos = (
        alt.Chart(df_riesgo).mark_circle(size=450)
        .encode(
            x=alt.X('HHI:Q', title='HHI — Concentración Geopolítica', scale=alt.Scale(zero=False)),
            y=alt.Y('vol:Q', title='Volatilidad Histórica Anualizada (%)', scale=alt.Scale(zero=False)),
            color=alt.Color('mineral:N', title='Mineral', legend=None),
            tooltip=[
                alt.Tooltip('mineral:N', title='Mineral'),
                alt.Tooltip('HHI:Q', title='HHI', format='.0f'),
                alt.Tooltip('vol:Q', title='Volatilidad (%)', format='.1f'),
            ]
        )
    )
    etiq_puntos = (
        alt.Chart(df_riesgo).mark_text(align='left', dx=14, fontSize=13, fontWeight='bold')
        .encode(x='HHI:Q', y='vol:Q', text='mineral:N', color=alt.Color('mineral:N', legend=None))
    )
    linea_mono = alt.Chart(pd.DataFrame({'x': [2500]})).mark_rule(color='red', strokeDash=[6,3], strokeWidth=2).encode(x='x:Q')
    linea_vol  = alt.Chart(pd.DataFrame({'y': [media_vol]})).mark_rule(color='gray', strokeDash=[4,2], strokeWidth=1.5).encode(y='y:Q')

    st.altair_chart((linea_mono + linea_vol + puntos + etiq_puntos).properties(height=420), use_container_width=True)
    st.caption("Línea roja: umbral monopolio geopolítico (HHI > 2.500) · Línea gris: volatilidad media del grupo")

    st.subheader("Tabla resumen")
    df_show = df_riesgo.copy()
    df_show['HHI'] = df_show['HHI'].round(0).astype(int)
    df_show['vol'] = df_show['vol'].round(1)
    df_show.columns = ['Mineral', 'HHI (2025)', 'Volatilidad anual (%)']
    st.dataframe(df_show.set_index('Mineral'), use_container_width=True)
