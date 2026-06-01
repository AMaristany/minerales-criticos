"""
app.py — POC Minerales Críticos
Visualización de datos · UNED Máster Data Science
"""

import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

alt.data_transformers.disable_max_rows()

# ── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Minerales Críticos",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos mínimos ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .stMetric { background: #f8f9fa; padding: 1rem; border-radius: 8px; }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.2rem !important; color: #444; border-bottom: 1px solid #eee; padding-bottom: .4rem; }
    .caption { font-size: 0.8rem; color: #888; margin-top: -0.5rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Carga de datos (cacheada) ─────────────────────────────────────────────────
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

# ── Sidebar ───────────────────────────────────────────────────────────────────
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

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 0 — INTRODUCCIÓN
# ═════════════════════════════════════════════════════════════════════════════
if seccion == "Introducción":
    st.title("Minerales Críticos y Transición Energética")
    st.markdown("""
    Esta aplicación analiza los **cinco minerales críticos** que vertebran la transición energética global:
    cobre, níquel, cobalto, litio y platino.

    El análisis aborda tres dimensiones:

    - 📈 **Precios y volatilidad** — evolución histórica desde 2000, shocks y comparativa entre minerales
    - 🌍 **Geopolítica** — correlación entre inestabilidad política y precios, concentración de producción (HHI)
    - 📊 **Macroeconomía** — relación con el ciclo económico global (CFNAI) y el dólar (DXY)

    Navega por las secciones usando el panel lateral.
    """)

    # KPIs rápidos
    st.subheader("Estado actual (último dato disponible)")
    df_last = df_imf[METALES].dropna().iloc[-1]
    cols = st.columns(5)
    for i, m in enumerate(METALES):
        prev = df_imf[m].dropna().iloc[-2]
        delta_pct = (df_last[m] - prev) / prev * 100
        cols[i].metric(
            METALES_LABEL[m],
            f"${df_last[m]:,.0f}",
            f"{delta_pct:+.1f}%"
        )
    st.caption(f"Fuente: IMF Primary Commodity Prices · Último dato: {df_imf[METALES].dropna().index[-1].strftime('%b %Y')}")

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — PRECIOS
# ═════════════════════════════════════════════════════════════════════════════
elif seccion == "Precios":
    st.title("Evolución de Precios")
    st.markdown("Índice base 100 = enero 2000. Permite comparar la apreciación relativa entre minerales independientemente de sus unidades.")

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
        {'date': pd.Timestamp('2020-03-01'),  'label': 'COVID-19'},
        {'date': pd.Timestamp('2022-02-24'),  'label': 'Ucrania'},
    ])

    sel = alt.selection_point(fields=['mineral'], bind='legend')

    lineas = (
        alt.Chart(df_long)
        .mark_line(strokeWidth=2)
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
        )
        .add_params(sel)
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

    chart = (lineas + reglas + etiq).properties(height=420).interactive()
    st.altair_chart(chart, use_container_width=True)
    st.caption("Haz clic en la leyenda para aislar un mineral · Scroll para hacer zoom")

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — VOLATILIDAD
# ═════════════════════════════════════════════════════════════════════════════
elif seccion == "Volatilidad":
    st.title("Volatilidad Rolling 12 Meses")
    st.markdown("Desviación estándar del retorno mensual sobre una ventana de 12 meses. Captura la incertidumbre estructural de cada mineral.")

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
        alt.Chart(df_vol_long)
        .mark_area(opacity=0.45, strokeWidth=2)
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
        )
        .add_params(sel2)
        .properties(height=400)
        .interactive()
    )
    st.altair_chart(chart_vol, use_container_width=True)
    st.caption("Haz clic en la leyenda para aislar un mineral")

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — GEOPOLÍTICA
# ═════════════════════════════════════════════════════════════════════════════
elif seccion == "Geopolítica":
    st.title("Concentración Geopolítica y Conflicto")

    tab1, tab2, tab3 = st.tabs(["HHI por Mineral", "Correlación Conflicto–Precio", "RDC vs Cobalto"])

    with tab1:
        st.markdown("El índice Herfindahl-Hirschman (HHI) mide la concentración de la producción minera. Un HHI >2500 indica riesgo de monopolio geopolítico.")

        df_p = df_usgs[~df_usgs['country'].isin(['World total', 'Other countries'])].copy()
        prod_total = df_p.groupby(['mineral', 'year'])['mine_production'].transform('sum')
        df_p['share_pct'] = (df_p['mine_production'] / prod_total) * 100
        df_p['hhi_comp']  = df_p['share_pct'] ** 2
        df_hhi = (
            df_p.groupby(['mineral', 'year'])['hhi_comp']
            .sum().reset_index()
            .rename(columns={'hhi_comp': 'HHI'})
        )
        df_hhi['mineral'] = df_hhi['mineral'].str.capitalize()

        sel_hhi = alt.selection_point(fields=['mineral'], bind='legend')

        umbral_alto = alt.Chart(pd.DataFrame({'y': [2500]})).mark_rule(
            color='red', strokeDash=[6, 3], strokeWidth=2).encode(y='y:Q')
        umbral_mod  = alt.Chart(pd.DataFrame({'y': [1000]})).mark_rule(
            color='orange', strokeDash=[4, 2], strokeWidth=1.5).encode(y='y:Q')

        lineas_hhi = (
            alt.Chart(df_hhi)
            .mark_line(point=True, strokeWidth=2.5)
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
            )
            .add_params(sel_hhi)
        )
        st.altair_chart((umbral_alto + umbral_mod + lineas_hhi).properties(height=380),
                        use_container_width=True)
        st.caption("Rojo: alta concentración (>2500) · Naranja: concentración moderada (>1000)")

    with tab2:
        st.markdown("Correlación de Pearson entre eventos de violencia política (ACLED) y precios, con delay óptimo de 0–12 meses.")

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
                resultados.append({
                    'mineral': METALES_LABEL[metal],
                    'pais': pais,
                    'corr': round(mejor_corr, 3),
                    'delay': mejor_delay,
                })

        df_heat = pd.DataFrame(resultados)

        fondo = (
            alt.Chart(df_heat)
            .mark_rect()
            .encode(
                x=alt.X('mineral:N', title='Mineral', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('pais:N', title='País'),
                color=alt.Color('corr:Q', scale=alt.Scale(scheme='redblue', domain=[-1, 1]), title='r'),
                tooltip=[
                    alt.Tooltip('mineral:N', title='Mineral'),
                    alt.Tooltip('pais:N',    title='País'),
                    alt.Tooltip('corr:Q',    title='r', format='.3f'),
                    alt.Tooltip('delay:Q',   title='Delay (meses)'),
                ]
            )
        )
        texto = (
            alt.Chart(df_heat)
            .mark_text(fontSize=11)
            .encode(
                x='mineral:N', y='pais:N',
                text=alt.Text('corr:Q', format='.2f'),
                color=alt.condition(
                    alt.datum.corr > 0.35, alt.value('white'), alt.value('black'))
            )
        )
        st.altair_chart((fondo + texto).properties(height=300), use_container_width=True)
        st.caption("Correlación con delay óptimo 0–12 meses · Azul = correlación positiva, Rojo = negativa")

    with tab3:
        st.markdown("El cobalto se produce mayoritariamente en la República Democrática del Congo (RDC). Series normalizadas 0–1 para comparación visual.")

        df_acled_piv = df_acled.pivot(columns='country', values='violence_events')
        df_geo = df_acled_piv[['Democratic Republic of Congo']].join(
            df_imf[['cobalt']], how='inner').dropna()
        df_geo.columns = ['violencia_rdc', 'cobalt']
        df_geo = df_geo.reset_index()

        for col in ['violencia_rdc', 'cobalt']:
            df_geo[f'{col}_norm'] = (
                (df_geo[col] - df_geo[col].min()) /
                (df_geo[col].max() - df_geo[col].min())
            )

        df_geo_long = df_geo.melt(
            id_vars='date',
            value_vars=['violencia_rdc_norm', 'cobalt_norm'],
            var_name='serie', value_name='valor'
        )
        df_geo_long['serie'] = df_geo_long['serie'].map({
            'violencia_rdc_norm': 'Violencia RDC',
            'cobalt_norm': 'Precio Cobalto'
        })

        chart_geo = (
            alt.Chart(df_geo_long)
            .mark_line(strokeWidth=2)
            .encode(
                x=alt.X('date:T', title='Fecha'),
                y=alt.Y('valor:Q', title='Valor normalizado (0–1)'),
                color=alt.Color('serie:N',
                    scale=alt.Scale(domain=['Violencia RDC', 'Precio Cobalto'],
                                    range=['#D62728', '#1F77B4']), title='Serie'),
                strokeDash=alt.condition(
                    alt.datum.serie == 'Precio Cobalto',
                    alt.value([6, 3]), alt.value([1, 0])),
                tooltip=[
                    alt.Tooltip('date:T',  title='Fecha', format='%b %Y'),
                    alt.Tooltip('serie:N', title='Serie'),
                    alt.Tooltip('valor:Q', title='Valor norm.', format='.3f'),
                ]
            )
            .properties(height=360)
            .interactive()
        )
        st.altair_chart(chart_geo, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — MACROECONOMÍA
# ═════════════════════════════════════════════════════════════════════════════
elif seccion == "Macroeconomía":
    st.title("Relación con el Ciclo Económico")
    st.markdown("""
    Correlación móvil (ventana 36 meses) entre los retornos de cada mineral y el **CFNAI**
    (Chicago Fed National Activity Index), un indicador de actividad manufacturera global.
    El \"despertar\" post-2020 muestra cómo el litio se sincroniza por primera vez con el ciclo industrial.
    """)

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
        .rename(columns={'date': 'date'})
        .melt(id_vars='date', value_vars=metales_macro, var_name='mineral', value_name='corr')
        .dropna(subset=['corr'])
    )
    df_corr_long['mineral'] = df_corr_long['mineral'].map(METALES_LABEL)

    sel3 = alt.selection_point(fields=['mineral'], bind='legend')

    era_ev = pd.DataFrame([{
        'start': pd.Timestamp('2015-01-01'),
        'end': df_corr.index.max()
    }])

    banda = (
        alt.Chart(era_ev)
        .mark_rect(color='#DDDDDD', opacity=0.35)
        .encode(x='start:T', x2='end:T')
    )
    cero = (
        alt.Chart(pd.DataFrame({'y': [0]}))
        .mark_rule(strokeDash=[6, 3], color='black', strokeWidth=1.5)
        .encode(y='y:Q')
    )
    lineas_corr = (
        alt.Chart(df_corr_long)
        .mark_line(strokeWidth=2.5)
        .encode(
            x=alt.X('date:T', title='Año'),
            y=alt.Y('corr:Q', title='Correlación (r)',
                    scale=alt.Scale(domain=[-1, 1])),
            color=alt.Color('mineral:N', title='Mineral'),
            opacity=alt.condition(sel3, alt.value(1), alt.value(0.08)),
            tooltip=[
                alt.Tooltip('date:T',   title='Fecha', format='%b %Y'),
                alt.Tooltip('mineral:N', title='Mineral'),
                alt.Tooltip('corr:Q',   title='r', format='.3f'),
            ]
        )
        .add_params(sel3)
    )
    etiq_ev = (
        alt.Chart(pd.DataFrame([{'x': pd.Timestamp('2015-06-01'), 'y': 0.88, 'text': 'Era EV'}]))
        .mark_text(fontSize=10, color='gray', align='left')
        .encode(x='x:T', y='y:Q', text='text:N')
    )

    chart_cfnai = (banda + cero + lineas_corr + etiq_ev).properties(height=420).interactive()
    st.altair_chart(chart_cfnai, use_container_width=True)
    st.caption("Ventana móvil 36 meses · Zona gris = Era de la Transición Energética (desde 2015) · Clic en leyenda para aislar")

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5 — RIESGO ESTRATÉGICO
# ═════════════════════════════════════════════════════════════════════════════
elif seccion == "Riesgo Estratégico":
    st.title("Matriz de Riesgo Estratégico")
    st.markdown("""
    Cruza la **concentración geopolítica** (HHI 2025) con la **volatilidad histórica anualizada** de cada mineral.
    El cuadrante superior derecho representa el mayor riesgo combinado para la cadena de suministro.
    """)

    # HHI 2025
    df_p = df_usgs[~df_usgs['country'].isin(['World total', 'Other countries'])].copy()
    prod_total = df_p.groupby(['mineral', 'year'])['mine_production'].transform('sum')
    df_p['share_pct'] = (df_p['mine_production'] / prod_total) * 100
    df_p['hhi_comp']  = df_p['share_pct'] ** 2
    df_hhi_all = (
        df_p.groupby(['mineral', 'year'])['hhi_comp']
        .sum().reset_index().rename(columns={'hhi_comp': 'HHI'})
    )
    df_hhi_2025 = (
        df_hhi_all[df_hhi_all['year'] == 2025]
        .set_index('mineral')[['HHI']]
    )
    df_hhi_2025.index = df_hhi_2025.index.str.lower()

    # Volatilidad anualizada
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

    media_vol   = df_riesgo['vol'].mean()
    umbral_mono = 2500

    puntos = (
        alt.Chart(df_riesgo)
        .mark_circle(size=450)
        .encode(
            x=alt.X('HHI:Q', title='HHI — Concentración Geopolítica',
                    scale=alt.Scale(zero=False)),
            y=alt.Y('vol:Q', title='Volatilidad Histórica Anualizada (%)',
                    scale=alt.Scale(zero=False)),
            color=alt.Color('mineral:N', title='Mineral', legend=None),
            tooltip=[
                alt.Tooltip('mineral:N', title='Mineral'),
                alt.Tooltip('HHI:Q',     title='HHI',  format='.0f'),
                alt.Tooltip('vol:Q',     title='Volatilidad (%)', format='.1f'),
            ]
        )
    )
    etiq_puntos = (
        alt.Chart(df_riesgo)
        .mark_text(align='left', dx=14, fontSize=13, fontWeight='bold')
        .encode(
            x='HHI:Q', y='vol:Q',
            text='mineral:N',
            color=alt.Color('mineral:N', legend=None)
        )
    )
    linea_mono = (
        alt.Chart(pd.DataFrame({'x': [umbral_mono]}))
        .mark_rule(color='red', strokeDash=[6, 3], strokeWidth=2)
        .encode(x='x:Q')
    )
    linea_vol = (
        alt.Chart(pd.DataFrame({'y': [media_vol]}))
        .mark_rule(color='gray', strokeDash=[4, 2], strokeWidth=1.5)
        .encode(y='y:Q')
    )

    chart_riesgo = (
        (linea_mono + linea_vol + puntos + etiq_puntos)
        .properties(height=420)
    )
    st.altair_chart(chart_riesgo, use_container_width=True)
    st.caption("Línea roja: umbral monopolio geopolítico (HHI >2500) · Línea gris: volatilidad media del grupo")

    # Tabla resum
    st.subheader("Tabla resumen")
    df_show = df_riesgo.copy()
    df_show['HHI'] = df_show['HHI'].round(0).astype(int)
    df_show['vol'] = df_show['vol'].round(1)
    df_show.columns = ['Mineral', 'HHI (2025)', 'Volatilidad anual (%)']
    st.dataframe(df_show.set_index('Mineral'), use_container_width=True)
