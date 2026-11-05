from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st


REQUIRED_COLUMNS = {
    "idoperacion",
    "RutCliente",
    "ID_unidad_cubit",
    "PRECIO_VENTA",
    "FECHA_RESERVA",
    "Proyecto",
    "RAZON_COMPRA",
    "Comuna_proyecto",
    "Estadocivil",
    "Genero",
    "INGRESO_RENTA",
    "Ocupacion",
    "FORMA_PAGO",
    "ORIGEN_VENTA",
}


@st.cache_data(show_spinner=False)
def parse_sales_csv(content: bytes) -> pd.DataFrame:
    data = pd.read_csv(
        BytesIO(content),
        na_values=["NULL", "null", ""],
        dtype={"RutCliente": "string", "ID_unidad_cubit": "string"},
    )
    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"El CSV no contiene las columnas requeridas: {missing}")

    data = data.drop_duplicates(subset="idoperacion", keep="first").copy()
    data["PRECIO_VENTA"] = pd.to_numeric(data["PRECIO_VENTA"], errors="coerce")
    data["FECHA_RESERVA"] = pd.to_datetime(data["FECHA_RESERVA"], errors="coerce")
    return data


@st.cache_data(show_spinner="Analizando archivo...")
def load_default_sales_data() -> pd.DataFrame:
    csv_path = Path(__file__).resolve().parents[2] / "data" / "ventas_prediccion.csv"
    return parse_sales_csv(csv_path.read_bytes())


def get_clients(data: pd.DataFrame) -> pd.DataFrame:
    clients = data.drop_duplicates(subset="RutCliente", keep="first").copy()
    clients["Genero"] = clients["Genero"].replace({"M": "Hombre", "F": "Mujer", "0": "No informado"})
    clients["Estadocivil"] = clients["Estadocivil"].fillna("No informado").astype(str).str.strip().str.upper()
    return clients


def clean_category(series: pd.Series) -> pd.Series:
    labels = series.astype("string").str.strip()
    return labels.mask(labels.isna() | labels.eq("") | labels.str.upper().isin(["NULL", "0"]), "No informado")