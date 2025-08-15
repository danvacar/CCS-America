# Import Python Libraries
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image

st.set_page_config(page_title="CCS America", page_icon="sources/icons/logo.png", layout="wide")
logo = Image.open('sources/icons/logo.png')

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, width=60)
    st.title("CarbonScope")
st.markdown("---")

st.sidebar.title("📑 Menú de Navegación")
section = st.sidebar.radio(
    "Ir a:",
    ["📊 Volumen de emisiones de CO₂",
     "🏭 Capacidad de almacenamiento geológico",
     "📉 Gráficos comparativos de emisiones",
     "🗺️ Mapa interactivo de reservorios"])

