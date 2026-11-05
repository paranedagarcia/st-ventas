from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from millify import millify

from st_ventas.data import clean_category, get_clients, load_default_sales_data, parse_sales_csv


COLORS = ["#126e68", "#e17c55", "#d8a52a", "#496b9a", "#7b8f5a", "#b85c71"]

style_metric_cards()

def _style() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f5f7f5; }
        [data-testid="stSidebar"] { background: #172f32; }
        [data-testid="stSidebar"] * { color: #f4f6f0; }
        [data-testid="stMetric"] { background: #ffffff; border: 1px solid #dfe7e2; padding: 14px 16px; border-radius: 6px; }
        [data-testid="stMetricLabel"] { color: #586b69; }
        [data-testid="stMetricValue"] { color: #172f32; }
        h1, h2, h3 { color: #172f32; }
        div[data-testid="stForm"] { border: 1px solid #dfe7e2; border-radius: 6px; background: #ffffff; padding: 20px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _currency(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _chart(data: pd.DataFrame, x: str, y: str, title: str, *, horizontal: bool = False) -> None:
    if data.empty:
        st.info("No hay datos suficientes para mostrar este gráfico.")
        return
    if horizontal:
        figure = px.bar(data, x=y, y=x, orientation="h", title=title, color_discrete_sequence=COLORS)
    else:
        figure = px.bar(data, x=x, y=y, title=title, color_discrete_sequence=COLORS)
    figure.update_layout(
        title_font_size=16,
        title_font_color="#172f32",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin={"l": 12, "r": 12, "t": 52, "b": 12},
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None,
    )
    st.plotly_chart(figure, use_container_width=True)


def _metric_row(metrics: list[tuple[str, str]]) -> None:
    columns = st.columns(len(metrics))
    for column, (label, value) in zip(columns, metrics, strict=True):
        column.metric(label, value)


def _page_inicio() -> None:
    data = st.session_state.sales_data
    clients = get_clients(data)
    married = clients["Estadocivil"].eq("CASADO").sum()
    single = clients["Estadocivil"].eq("SOLTERO").sum()
    gender = clients["Genero"].value_counts()
    total_sales = data["PRECIO_VENTA"].sum()

    st.title("Ventas inmobiliarias")
    st.caption(f"{len(data):,} operaciones unicas · {len(clients):,} clientes unicos".replace(",", "."))
    _metric_row(
        [
            ("Clientes", f"{len(clients):,}".replace(",", ".")),
            ("Hombres", f"{gender.get('Hombre', 0):,}".replace(",", ".")),
            ("Mujeres", f"{gender.get('Mujer', 0):,}".replace(",", ".")),
            ("Casados", f"{married:,}".replace(",", ".")),
        ]
    )
    _metric_row(
        [
            ("Solteros", f"{single:,}".replace(",", ".")),
            ("Total ventas · PRECIO_VENTA", f"$ {millify(total_sales, precision=2)}"),
            ("Departamentos vendidos", f"{data['ID_unidad_cubit'].nunique():,}".replace(",", ".")),
        ]
    )
    st.caption("Total calculado con PRECIO_VENTA. El archivo no especifica moneda ni permite convertir a otra.")

    monthly = (
        data.dropna(subset=["FECHA_RESERVA"])
        .assign(Mes=lambda frame: frame["FECHA_RESERVA"].dt.to_period("M").dt.to_timestamp())
        .groupby("Mes", as_index=False)["PRECIO_VENTA"]
        .sum()
    )
    if not monthly.empty:
        figure = px.area(monthly, x="Mes", y="PRECIO_VENTA", title="Ventas de departamentos por mes", color_discrete_sequence=COLORS)
        figure.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", title_font_size=16, margin={"l": 12, "r": 12, "t": 52, "b": 12}, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(figure, use_container_width=True)

    first, second = st.columns(2)
    with first:
        _chart(data.assign(Tipo=clean_category(data["RAZON_COMPRA"])).groupby("Tipo").size().reset_index(name="Ventas").sort_values("Ventas", ascending=False), "Tipo", "Ventas", "Tipos de venta", horizontal=True)
    with second:
        _chart(data.assign(Proyecto=clean_category(data["Proyecto"])).groupby("Proyecto").size().reset_index(name="Departamentos").sort_values("Departamentos", ascending=False).head(12), "Proyecto", "Departamentos", "Departamentos por proyecto", horizontal=True)

    comunas = data.assign(Comuna=clean_category(data["Comuna_proyecto"])).groupby("Comuna").size().reset_index(name="Departamentos").sort_values("Departamentos", ascending=False).head(12)
    _chart(comunas, "Comuna", "Departamentos", "Departamentos vendidos por comuna", horizontal=True)


def _page_clientes() -> None:
    clients = get_clients(st.session_state.sales_data)
    gender = clients["Genero"].value_counts()
    st.title("Clientes")
    _metric_row(
        [
            ("Total de clientes", f"{len(clients):,}".replace(",", ".")),
            ("Casados", f"{clients['Estadocivil'].eq('CASADO').sum():,}".replace(",", ".")),
            ("Solteros", f"{clients['Estadocivil'].eq('SOLTERO').sum():,}".replace(",", ".")),
            ("Hombres", f"{gender.get('Hombre', 0):,}".replace(",", ".")),
            ("Mujeres", f"{gender.get('Mujer', 0):,}".replace(",", ".")),
        ]
    )
    civil = clients.assign(Estado=clean_category(clients["Estadocivil"])).groupby("Estado").size().reset_index(name="Clientes").sort_values("Clientes", ascending=False)
    genders = clients.assign(Genero=clean_category(clients["Genero"])).groupby("Genero").size().reset_index(name="Clientes").sort_values("Clientes", ascending=False)
    rent = clients.assign(Renta=clean_category(clients["INGRESO_RENTA"])).groupby("Renta").size().reset_index(name="Clientes").sort_values("Clientes", ascending=False)
    occupations = clients.assign(Ocupacion=clean_category(clients["Ocupacion"])).groupby("Ocupacion").size().reset_index(name="Clientes").sort_values("Clientes", ascending=False).head(15)
    left, right = st.columns(2)
    with left:
        _chart(civil, "Estado", "Clientes", "Estado civil", horizontal=True)
        _chart(rent, "Renta", "Clientes", "Tramo de renta", horizontal=True)
    with right:
        _chart(genders, "Genero", "Clientes", "Genero de los clientes", horizontal=True)
        _chart(occupations, "Ocupacion", "Clientes", "Ocupaciones mas frecuentes", horizontal=True)


def _page_prediccion() -> None:
    data = st.session_state.sales_data
    st.title("Prediccion de ventas")
    st.caption("Registra los antecedentes del cliente, departamento y venta.")
    with st.form("sale_prediction_form", clear_on_submit=False):
        st.subheader("Datos del cliente")
        client_1, client_2, client_3 = st.columns(3)
        client_1.text_input("RUT del cliente")
        client_2.selectbox("Estado civil", ["No informado", "Soltero", "Casado", "Divorciado", "Viudo", "Union civil"])
        client_3.selectbox("Genero", ["No informado", "Hombre", "Mujer"])
        client_1.number_input("Edad", min_value=18, max_value=120, value=30)
        client_2.selectbox("Tramo de renta", sorted(clean_category(data["INGRESO_RENTA"]).unique().tolist()))
        client_3.text_input("Ocupacion")
        client_1.text_input("Comuna de residencia")
        client_2.number_input("Cantidad de hijos", min_value=0, max_value=30, value=0)

        st.subheader("Datos del departamento")
        department_1, department_2, department_3 = st.columns(3)
        department_1.selectbox("Proyecto", sorted(clean_category(data["Proyecto"]).unique().tolist()))
        department_2.text_input("Etapa")
        department_3.text_input("Unidad")
        department_1.selectbox(
            "Comuna del proyecto",
            sorted(clean_category(data["Comuna_proyecto"]).unique().tolist()),
        )

        st.subheader("Datos de la venta")
        sale_1, sale_2, sale_3 = st.columns(3)
        sale_1.selectbox("Tipo de compra", sorted(clean_category(data["RAZON_COMPRA"]).unique().tolist()))
        sale_2.selectbox("Forma de pago", sorted(clean_category(data["FORMA_PAGO"]).unique().tolist()))
        sale_3.date_input("Fecha de reserva")
        sale_1.number_input("Precio de venta", min_value=0.0, step=100.0)
        sale_2.number_input("Descuento", min_value=0.0, step=10.0)
        sale_3.selectbox("Origen de venta", sorted(clean_category(data["ORIGEN_VENTA"]).unique().tolist()))
        submitted = st.form_submit_button("Enviar datos", type="primary")
    if submitted:
        st.success("datos ingresados")


def main() -> None:
    st.set_page_config(page_title="Analisis de ventas", page_icon="V", layout="wide")
    _style()
    if "sales_data" not in st.session_state:
        st.session_state.sales_data = load_default_sales_data()

    with st.sidebar:
        st.title("ST Ventas")
        page = st.radio("Menu", ["Inicio", "Clientes", "Prediccion de ventas"], label_visibility="collapsed")
        st.divider()
        st.subheader("Archivo de analisis")
        uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"], help="El CSV debe incluir los campos de ventas y clientes del archivo original.")
        if uploaded_file is not None:
            try:
                st.session_state.sales_data = parse_sales_csv(uploaded_file.getvalue())
                st.success(f"{len(st.session_state.sales_data):,} operaciones cargadas".replace(",", "."))
            except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as error:
                st.error(str(error))

    if page == "Inicio":
        _page_inicio()
    elif page == "Clientes":
        _page_clientes()
    else:
        _page_prediccion()


if __name__ == "__main__":
    main()