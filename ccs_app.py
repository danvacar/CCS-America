# Import Python Libraries
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from PIL import Image

st.set_page_config(page_title="CCS America", page_icon="sources/icons/logo.png", layout="wide")
logo = Image.open('sources/icons/logo.png')

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, width=60)
    st.title("CCS America")
st.markdown("---")

st.sidebar.title("📑 Menú de Navegación")
section = st.sidebar.radio(
    "Ir a:",
    ["📊 Volumen de emisiones de CO₂",
     "🏭 Capacidad de almacenamiento geológico",
     "📉 Gráficos comparativos de emisiones",
     "🗺️ Mapa interactivo de reservorios"])

if section == "📊 Volumen de emisiones de CO₂":
    st.subheader("📊 Volumen de emisiones de CO₂")
    st.markdown("""
    Aquí puede ver el **volumen total de emisiones** por país
    para un rango de años definido. Use los filtros para seleccionar país, fuente emisora y rango de años.
    """)

    df_emisiones = pd.read_csv("data/co2-by-source.csv")
    df_emisiones = df_emisiones.melt(
        id_vars=["Entity", "Year"],
        value_vars=["Coal", "Oil", "Gas", "Flaring", "Cement"],
        var_name="Source",
        value_name="Emissions")

    pais = st.selectbox("Seleccionar país:", df_emisiones["Entity"].unique())
    fuente = st.selectbox("Seleccionar fuente emisora:", df_emisiones["Source"].unique())

    año_min = int(df_emisiones["Year"].min())
    año_max = int(df_emisiones["Year"].max())
    años = st.slider("Seleccionar rango de años:", año_min, año_max, (año_min, año_max))

    df_filtrado = df_emisiones[
        (df_emisiones["Entity"] == pais) &
        (df_emisiones["Source"] == fuente) &
        (df_emisiones["Year"] >= años[0]) &
        (df_emisiones["Year"] <= años[1])]

    st.subheader(f"Emisiones de {pais} ({fuente}) entre {años[0]} y {años[1]}")
    st.dataframe(df_filtrado)

    total_pais = df_filtrado["Emissions"].sum()
    st.markdown(f"**Total emisiones de {pais}:** {round(total_pais, 2)} Mt CO₂")
