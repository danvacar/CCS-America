# Import Python Libraries
import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image

st.set_page_config(page_title="CCS America", page_icon="sources/icons/logo.png", layout="wide")
logo = "sources/icons/logo.png"

st.markdown(
    """
    <h1 style='text-align: center;'>🌎 CCS América </h1>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

st.markdown(
    """
    <style>
    h1 {text-align: center;
    }
    
    .stApp {background-color: #DCE3D5;
            width: 1400px;
            margin: 15px auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# CSS codes to improve the design of the web app
st.markdown(
    """
<style>
h1 {text-align: center;
}
body {background-color: #DCE3D5;
      width: 1400px;
      margin: 15px auto;
}
</style>""",
    unsafe_allow_html=True,
)

st.sidebar.title("📑 Menú de Navegación")
section = st.sidebar.radio(
    "Ir a:",
    ["📊 Volumen de emisiones de CO₂",
     "🏭 Capacidad de almacenamiento geológico",
     "🟢 Balance de carbono y remoción de emisiones",
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

    df_emisiones["Emissions"] = df_emisiones["Emissions"] / 1e6
    df_emisiones = df_emisiones.rename(columns={"Emissions": "Emissions (Mt)"})

    # Filtros
    modo = st.radio("Ver emisiones por:", ["País", "Región"])
    fuentes = list(df_emisiones["Source"].unique()) + ["All"]
    fuente = st.selectbox("Seleccionar fuente emisora:", fuentes)

    año_min = int(df_emisiones["Year"].min())
    año_max = int(df_emisiones["Year"].max())
    años = st.slider("Seleccionar rango de años:", año_min, año_max, (año_min, año_max))

    if modo == "País":
        st.markdown("### 🌎 Emisiones por país")
        pais = st.selectbox("Seleccionar país:", df_emisiones["Entity"].unique())

        df_filtrado = df_emisiones[
            (df_emisiones["Entity"] == pais) &
            (df_emisiones["Year"] >= años[0]) &
            (df_emisiones["Year"] <= años[1])]

        if fuente == "All":
            df_filtrado = df_filtrado.groupby(["Entity", "Year"], as_index=False)["Emissions (Mt)"].sum()
            df_filtrado["Source"] = "All"
            df_filtrado = df_filtrado[["Entity", "Year", "Source", "Emissions (Mt)"]]
        else:
            df_filtrado = df_filtrado[df_filtrado["Source"] == fuente]
            df_filtrado = df_filtrado[["Entity", "Year", "Source", "Emissions (Mt)"]]

        df_filtrado["Year"] = df_filtrado["Year"].astype(int)
        total_pais = df_filtrado["Emissions (Mt)"].sum()
        st.subheader(f"Emisiones de {pais} ({fuente}) entre {años[0]} y {años[1]}")

        st.dataframe(
            df_filtrado.style.set_properties(**{'text-align': 'center'}), use_container_width=True)

        st.metric(
            label=f"Total emisiones de {pais} ({fuente})", value=f"{round(total_pais, 2)} Mt CO₂")

    elif modo == "Región":
        st.markdown("### 🌎 Emisiones por región")
        regiones = {
            "Norteamérica": ["United States", "Canada", "Mexico"],
            "Sudamérica": ["Argentina", "Brazil", "Colombia", "Venezuela", "Ecuador"]
        }
        region = st.selectbox("Seleccionar región:", list(regiones.keys()))
        df_region = df_emisiones[
            (df_emisiones["Entity"].isin(regiones[region])) &
            (df_emisiones["Year"] >= años[0]) &
            (df_emisiones["Year"] <= años[1])
            ]

        if fuente == "All":
            df_region = df_region.groupby(["Year"], as_index=False)["Emissions (Mt)"].sum()
            df_region["Source"] = "All"
        else:
            df_region = df_region[df_region["Source"] == fuente]
            df_region = df_region.groupby(["Year"], as_index=False)["Emissions (Mt)"].sum()
            df_region["Source"] = fuente

        df_region = df_region[["Source", "Year", "Emissions (Mt)"]]
        df_region["Year"] = df_region["Year"].astype(int)

        total_region = df_region["Emissions (Mt)"].sum()

        st.subheader(f"Emisiones de {region} ({fuente}) entre {años[0]} y {años[1]}")
        st.dataframe(df_region.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
        st.metric(label=f"Total emisiones de {region} ({fuente})", value=f"{round(total_region, 2)} Mt CO₂")

elif section == "🏭 Capacidad de almacenamiento geológico":
    st.subheader("🏭 Capacidad de almacenamiento geológico")
    st.markdown("""
    Esta sección muestra la **cantidad en millones de toneladas (Mt) de CO₂ que pueden ser almacenadas** en los reservorios seleccionados,
    siguiendo la metodología de **Bachu**. 
    Use los filtros para seleccionar países y observar la capacidad de almacenamiento de sus reservorios.
    """)

    df_reservorios = pd.DataFrame({
        "Región": [
            "Norteamérica", "Norteamérica", "Norteamérica", "Norteamérica", "Norteamérica", "Norteamérica",
            "Norteamérica", "Norteamérica",
            "Norteamérica", "Norteamérica", "Norteamérica", "Norteamérica", "Norteamérica", "Norteamérica",
            "Norteamérica",
            "Norteamérica", "Norteamérica",
            "Sudamérica", "Sudamérica", "Sudamérica",
            "Sudamérica", "Sudamérica", "Sudamérica",
            "Sudamérica", "Sudamérica", "Sudamérica", "Sudamérica", "Sudamérica"
        ],
        "País": [
            "Canadá", "Canadá", "Canadá", "Canadá", "Canadá", "Canadá", "Canadá", "Canadá",
            "EE.UU.", "EE.UU.", "EE.UU.", "EE.UU.", "EE.UU.", "EE.UU.", "EE.UU.",
            "México", "México",
            "Brasil", "Brasil", "Brasil",
            "Colombia", "Colombia", "Colombia",
            "Ecuador", "Ecuador", "Ecuador", "Ecuador", "Ecuador"
        ],
        "Reservorio": [
            "Leduc Formation (Clive Field)", "Midale Formation (Weyburn Field)", "Viking Formation (Chigwell Field)", "Leduc Formation (Redwater Field)", "Viking Formation (Joffre Field)", "Cardium Formation (Pembina Field)",
            "Basal Cambrian Sand (Quest)", "Deadwood Formation (Aquistore)",
            "Frio Formation (West Ranch Field)", "Weber Sandstone (Rangely Field)", "Muddy Formation (Bell Creek Field)", "Morrow Formation (Farnsworth Field)", "Mt. Simon Sandstone (Illinois Basin)", "Tuscaloosa Formation (Cranfield Field)",
            "Paluxy Formation (Citronelle Field)",
            "Cahuasas Formation (Tampico Misantla Basin)", "Tamaulipas Formation (Tampico Misantla Basin)",
            "Itapema Formation (Buzios Field)", "Barra Velha Formation (Buzios Field)", "Itapema Formation (Tupi Field)",
            "Siamana Formation (Guajira Basin)", "Jimol Formation (Guajira Basin)", "Jimol Formation (Sinu Basin)",
            "Hollín Superior (Sacha Field)", "Hollín Superior (Lago Agrio Field)", "U Inferior (Parahuacu Field)", "Napo T (Sacha Field)", "T Principal (Yanaquincha Este Field)"
        ],
        "Capacidad (Mt)": [
            18.38, 125.13, 9.33, 79.33, 35.35, 861.54, 65.05, 67.06,
            47.79, 95.45, 13.0, 28.1, 393.15, 109.52, 753.19,
            823.39, 275.49,
            814.48, 892.36, 940.03,
            682.73, 359.42, 136.45,
            58.73, 3.63, 2.56, 17.35, 5.41
        ],
        "Profundidad (m)": [
            1832, 1450, 1385.6, 984, 1400, 1447, 2330, 3200,
            1752.6, 1980, 1360, 2330, 3060, 1690, 2865,
            3600, 2900,
            5000, 5000, 5000,
            1701, 1800, 3287,
            2735.58, 3040.38, 2649, 2671.58, 3048
        ],
        "Espesor (m)": [
            180, 20, 30, 250, 20, 32, 47, 38.6,
            27, 58, 8, 25, 28, 156, 143,
            400, 154,
            121.92, 151, 121.92,
            12, 37, 11,
            15.24, 5.48, 12.92, 10.21, 27.74
        ],
        "Porosidad (%)": [
            8, 26, 13, 12, 13, 16.4, 17, 15,
            30, 58, 25, 23, 25.5, 21, 25,
            14, 9,
            13, 11.5, 13,
            17.5, 21, 24,
            14, 13, 11.9, 16, 15
        ],
        "Permeabilidad (mD)": [
            95.02, 300, 72.89, 100, 349, 21.4, 1000, 20,
            900, 8, 900, 300, 100, 28, 300,
            100, 100,
            88.7, 122.6, 88.7,
            200, 250, 200,
            70, 70.64, 384, 200, 356
        ]})

    region = st.selectbox("🌎 Seleccionar región:", df_reservorios["Región"].unique())
    df_region = df_reservorios[df_reservorios["Región"] == region]

    pais = st.selectbox("🏳️ Seleccionar país:", df_region["País"].unique())
    df_pais = df_region[df_region["País"] == pais]

    reservorio = st.selectbox("🛢️ Seleccionar reservorio:", df_pais["Reservorio"].unique())
    df_seleccionado = df_pais[df_pais["Reservorio"] == reservorio]

    st.subheader(f"🛢️ Reservorio: {reservorio} ({pais})")
    st.dataframe(
        df_seleccionado.style.format({
            "Capacidad (Mt)": "{:.2f}",
            "Profundidad (m)": "{:.2f}",
            "Espesor (m)": "{:.2f}",
            "Porosidad (%)": "{:.2f}",
            "Permeabilidad (mD)": "{:.2f}"
        }).set_properties(**{'text-align': 'center'}),
        use_container_width=True
    )

    st.metric(label="Capacidad del reservorio seleccionado",
              value=f"{df_seleccionado['Capacidad (Mt)'].values[0]:.2f} Mt CO₂")

    st.metric(label=f"Capacidad total en {pais}",
              value=f"{df_pais['Capacidad (Mt)'].sum():.2f} Mt CO₂")

    st.metric(label=f"Capacidad total en {region}",
              value=f"{df_region['Capacidad (Mt)'].sum():.2f} Mt CO₂")

    fig = px.bar(df_pais, x="Reservorio", y="Capacidad (Mt)",
                 color="Capacidad (Mt)", text="Capacidad (Mt)",
                 title=f"📊 Capacidad por reservorio en {pais}")
    st.plotly_chart(fig, use_container_width=True)

elif section == "🟢 Balance de carbono y remoción de emisiones":
    st.subheader("🟢 Balance de carbono y remoción de emisiones")
    st.markdown("""
        Visualice el *balance de carbono* y el *% de remoción de emisiones* por diferentes niveles:
        - América
        - Norteamérica
        - Sudamérica
        - País
    """)

    df_balance = pd.DataFrame({
        "Región": ["Norteamérica", "Norteamérica", "Norteamérica", "Sudamérica", "Sudamérica", "Sudamérica"],
        "País": ["Canadá", "EE.UU.", "México", "Brasil", "Colombia", "Ecuador"],
        "Emisiones (Mt)": [18354.93, 186820.53, 14502.65, 13050.66, 2477.66, 1038.67],
        "CO₂ almacenado (Mt)": [1261.17, 1440.20, 1098.88, 2646.87, 1178.60, 87.68]
    })

    # Agregar columna de emisiones no almacenadas y % remoción
    df_balance["CO₂ no almacenado (Mt)"] = df_balance["Emisiones (Mt)"] - df_balance["CO₂ almacenado (Mt)"]
    df_balance["% Remoción"] = (df_balance["CO₂ almacenado (Mt)"] / df_balance["Emisiones (Mt)"] * 100).round(2)

    # --- Balance total América ---
    with st.expander("🌎 Balance total América"):
        df_america = df_balance.groupby("Región")[["Emisiones (Mt)", "CO₂ almacenado (Mt)", "CO₂ no almacenado (Mt)"]].sum().reset_index()
        df_america["% Remoción"] = (df_america["CO₂ almacenado (Mt)"] / df_america["Emisiones (Mt)"] * 100).round(2)

        st.dataframe(
            df_america[["Región", "Emisiones (Mt)", "CO₂ almacenado (Mt)", "CO₂ no almacenado (Mt)", "% Remoción"]]
            .style.format({
                "Emisiones (Mt)": "{:.2f}",
                "CO₂ almacenado (Mt)": "{:.2f}",
                "CO₂ no almacenado (Mt)": "{:.2f}",
                "% Remoción": "{:.2f}%"
            }).set_properties(**{'text-align': 'center'}))

        fig = px.bar(df_america, x="Región", y=["CO₂ almacenado (Mt)", "CO₂ no almacenado (Mt)"],
                     text_auto=True, labels={"value": "Emisiones totales (Mt)", "variable": ""})
        fig.update_layout(title_text="Balance de emisiones por región", title_x=0.5,
                          barmode='stack',
                          yaxis_title="Emisiones totales (Mt)",
                          legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

    # --- Balance Norteamérica ---
    with st.expander("🟢 Balance por Norteamérica"):
        df_na = df_balance[df_balance["Región"]=="Norteamérica"].copy()
        df_na_total = df_na[["Emisiones (Mt)", "CO₂ almacenado (Mt)", "CO₂ no almacenado (Mt)"]].sum()
        st.dataframe(df_na[["País", "Emisiones (Mt)", "CO₂ almacenado (Mt)", "CO₂ no almacenado (Mt)", "% Remoción"]]
                     .style.format({"Emisiones (Mt)":"{:.2f}", "CO₂ almacenado (Mt)":"{:.2f}", "CO₂ no almacenado (Mt)":"{:.2f}", "% Remoción":"{:.2f}%"}).set_properties(**{'text-align':'center'}))

        st.metric("Total % remoción Norteamérica", f"{(df_na['CO₂ almacenado (Mt)'].sum()/df_na['Emisiones (Mt)'].sum()*100):.2f}%")
        st.metric("CO₂ total almacenado", f"{df_na['CO₂ almacenado (Mt)'].sum():.2f} Mt CO₂")

        fig = px.bar(df_na, x="País", y=["CO₂ almacenado (Mt)", "CO₂ no almacenado (Mt)"],
                     text_auto=True, labels={"value": "Emisiones totales (Mt)", "variable": ""})
        fig.update_layout(title_text="Balance de emisiones por país en Norteamérica", title_x=0.5,
                          yaxis_title="Emisiones totales (Mt)",
                          barmode='stack',
                          legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

    # --- Balance Sudamérica ---
    with st.expander("🟢 Balance por Sudamérica"):
        df_sa = df_balance[df_balance["Región"]=="Sudamérica"].copy()
        st.dataframe(df_sa[["País", "Emisiones (Mt)", "CO₂ almacenado (Mt)", "CO₂ no almacenado (Mt)", "% Remoción"]]
                     .style.format({"Emisiones (Mt)":"{:.2f}", "CO₂ almacenado (Mt)":"{:.2f}", "CO₂ no almacenado (Mt)":"{:.2f}", "% Remoción":"{:.2f}%"}).set_properties(**{'text-align':'center'}))

        st.metric("Total % remoción Sudamérica", f"{(df_sa['CO₂ almacenado (Mt)'].sum()/df_sa['Emisiones (Mt)'].sum()*100):.2f}%")
        st.metric("CO₂ total almacenado", f"{df_sa['CO₂ almacenado (Mt)'].sum():.2f} Mt CO₂")

        fig = px.bar(df_sa, x="País", y=["CO₂ almacenado (Mt)", "CO₂ no almacenado (Mt)"],
                     text_auto=True, labels={"value": "Emisiones totales (Mt)", "variable": "Tipo"})
        fig.update_layout(title_text="Balance de emisiones por país en Sudamérica", title_x=0.5,
                          yaxis_title="Emisiones totales (Mt)",
                          barmode='stack',
                          legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))
        st.plotly_chart(fig, use_container_width=True)

    # --- Balance por país ---
    with st.expander("🌍 Balance por país"):
        selected_paises = st.multiselect("Seleccionar países:", df_balance["País"].unique(),
                                         default=df_balance["País"].unique())
        df_selected = df_balance[df_balance["País"].isin(selected_paises)].copy()
        df_selected["% Remoción"] = (df_selected["CO₂ almacenado (Mt)"] / df_selected["Emisiones (Mt)"] * 100).round(2)

        st.dataframe(
            df_selected[["País", "Emisiones (Mt)", "CO₂ almacenado (Mt)", "% Remoción"]]
            .style.format({"Emisiones (Mt)": "{:.2f}", "CO₂ almacenado (Mt)": "{:.2f}", "% Remoción": "{:.2f}%"})
            .set_properties(**{'text-align': 'center'}),
            use_container_width=True
        )

        fig_pais = px.bar(
            df_selected,
            x="País",
            y=["Emisiones (Mt)", "CO₂ almacenado (Mt)"],
            text_auto=True,
            labels={"value": "Emisiones totales (Mt)", "variable": ""},
            title="Balance de emisiones por país"
        )
        fig_pais.update_layout(
            title_x=0.5,
            barmode='stack',
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
        )
        fig_pais.update_yaxes(title_text="Emisiones totales (Mt)", tickformat=".0f")
        st.plotly_chart(fig_pais, use_container_width=True)
