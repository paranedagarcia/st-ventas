import streamlit as st
import pandas as pd
import altair as alt

# 1. Configuración y Carga de Datos
st.set_page_config(layout="wide")
st.title("Análisis de Titanic con Altair")

@st.cache_data
def load_titanic():
    """Carga y limpieza del dataset del Titanic.

    Retorna:
        pd.DataFrame: DataFrame limpio con columnas 'age', 'pclass', 'survived', 'survived_str' y 'pclass_str'.
    """
    # El archivo titanic3.csv contiene columnas como pclass, survived y age [1]
    df = pd.read_csv('data/titanic3.csv')
    # Limpieza: eliminar nulos en edad para los gráficos de distribución [1]
    df = df.dropna(subset=['age', 'pclass', 'survived'])
    # Mapeo para mejorar la legibilidad de las leyendas [1]
    df['survived_str'] = df['survived'].map({1: 'Sobrevivió', 0: 'Falleció'})
    df['pclass_str'] = df['pclass'].astype(str) + "° Clase"
    return df

df = load_titanic()

# 2. Personalización en el Sidebar
st.sidebar.header("Opciones de Personalización")
# Permitir al usuario elegir un color corporativo mediante el color_picker

color_base = st.sidebar.color_picker("Elige color para la clase", "#4b9ed9")

# 3. Visualización 1: Densidad de Edad y Supervivencia
st.subheader("Distribución de Edad por Supervivencia")

# Aplicamos leyenda superior y orientación horizontal [Turn 22]
chart_age = alt.Chart(df).transform_density(
    'age',
    as_=['age', 'density'],
    groupby=['survived_str']
).mark_area(opacity=0.6).encode(
    alt.X('age:Q', title='Edad del Pasajero'),
    alt.Y('density:Q', title='Densidad'),
    alt.Color('survived_str:N', 
              title=None,
              scale=alt.Scale(range=["#e7b51f", "#0d9ab6"]), # Rojo para fallecidos, verde para sobrevivientes
              legend=alt.Legend(orient='top', direction='horizontal')),
    tooltip=[
        alt.Tooltip('survived_str:N', title='Estado'),
        alt.Tooltip('age:Q', title='Edad'),
        alt.Tooltip('density:Q', title='Densidad')
    ] # Tooltips interactivos [4]
).properties(
    height=400
).interactive() # Zoom y desplazamiento habilitados [5, 6]

st.altair_chart(chart_age, use_container_width=True)

# 4. Visualización 2: Relación entre Clase (Pclass) y Supervivencia
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.write("**Probabilidad de Supervivencia por Clase**")
    # Gráfico de barras apiladas al 100% para ver proporciones
    chart_pclass = alt.Chart(df).mark_bar().encode(
        alt.X('pclass_str:N', title='Clase'),
        alt.Y('count():Q', stack="normalize", title='Proporción'),
        alt.Color('survived_str:N', scale=alt.Scale(range=['#e74c3c', '#27ae60'])),
        tooltip=['pclass_str', 'survived_str', 'count()']
    ).properties(height=350)
    st.altair_chart(chart_pclass, use_container_width=True)

with col2:
    st.write("**Promedio de Edad por Clase**")
    # Uso del color personalizado del sidebar [2]
    chart_box = alt.Chart(df).mark_boxplot(color=color_base).encode(
        alt.X('pclass_str:N', title='Clase'),
        alt.Y('age:Q', title='Edad')
    ).properties(height=350)
    st.altair_chart(chart_box, use_container_width=True)


# 2. Creación del gráfico con Altair [3, 5]
# Nota: Altair utiliza transformaciones para representar densidades [Turn 23]
violin_like_chart = alt.Chart(df).transform_density(
    'age',
    as_=['age', 'density'],
    groupby=['pclass', 'survived']
).mark_area(orient='horizontal').encode(
    alt.X('density:Q', stack='center', impute=None, title=None, axis=alt.Axis(labels=False, grid=False)),
    alt.Y('age:Q', title='Edad'),
    alt.Color('survived:N', title='Estado', scale=alt.Scale(range=['red', 'green'])),
    alt.Column('pclass:N', title='Clase del Pasajero', header=alt.Header(labelOrient='bottom'))
).properties(
    width=150,
    title='Densidad de Edad por Clase y Supervivencia'
).configure_view(
    stroke=None
)

# 3. Mostrar el gráfico en Streamlit [6, 9]
st.altair_chart(violin_like_chart, use_container_width=True)

# Alternativa rápida: Boxplot (Soportado nativamente por Altair)
st.subheader("Alternativa: Gráfico de Caja (Boxplot)")
boxplot = alt.Chart(df).mark_boxplot().encode(
    x='survived:N',
    y='age:Q',
    color='survived:N',
    column='pclass:N'
).properties(width=150)

st.altair_chart(boxplot)