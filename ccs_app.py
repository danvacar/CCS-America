# Import Python Libraries
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import plotly.express as px
from pathlib import Path
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
#from PIL import Image

st.set_page_config(page_title="CCS America", page_icon="sources/icons/logo.png", layout="wide")
logo = "sources/icons/logo.png"

st.markdown(
    """
    <h1 style='text-align: center;'>🌎 CO₂ Removal Americas </h1>
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

# Add sections of the app
with st.sidebar:
     section = option_menu(menu_title="Section Menu", options=["Home",
                                                               "CO₂ Emissions Volume",
                                                               "Geological Storage Capacity",
                                                               "Carbon balance and emission removal",
                                                               "Reservoirs Location"],
                           icons=["house", "graph-up", "database", "tree", "pin-map"])

#st.sidebar.title("📑 Section Menu")
#section = st.sidebar.radio(
#    "Ir a:",
#    ["📊 CO₂ Emissions Volume",
#     "🛢️ Geological Storage Capacity",
#     "🟢 Carbon balance and emission removal",
#     "🗺️ Reservoirs Location"])

APP_DIR = Path(__file__).resolve().parent
data = APP_DIR / "Data" /"co2-by-source.csv"

if section == "CO₂ Emissions Volume":
    st.subheader("📊 CO₂ Emissions Volume")
    st.markdown("""
    Here you can explore the **total emissions volume** by country or region 
    for a defined year range. Use the filters below to select country, emission source, 
    and year range.
    """)

    # --- Load and prepare data ---
    df_emisiones = pd.read_csv(data)
    df_emisiones = df_emisiones.melt(
        id_vars=["Entity", "Year"],
        value_vars=["Coal", "Oil", "Gas", "Flaring", "Cement"],
        var_name="Source",
        value_name="Emissions"
    )
    # Convert to millions and renombrar columnas
    df_emisiones["Emissions"] = df_emisiones["Emissions"] / 1e6
    df_emisiones = df_emisiones.rename(columns={"Entity": "Country", "Emissions": "Emissions (Mt)"})

    # Eliminar filas sin año
    df_emisiones = df_emisiones.dropna(subset=["Year"])
    df_emisiones["Year"] = df_emisiones["Year"].astype(int)

    regions = {
        "America": ["United States", "Canada", "Mexico", "Argentina", "Brazil", "Colombia", "Venezuela", "Ecuador"],
        "North America": ["United States", "Canada", "Mexico"],
        "South America": ["Argentina", "Brazil", "Colombia", "Venezuela", "Ecuador"]
    }

    # --- Table View ---
    st.markdown("### Table View")
    mode_table = st.radio("View table by:", ["Country", "Region"])
    sources_table = list(df_emisiones["Source"].unique()) + ["All"]
    source_table = st.selectbox("Select emission source:", sources_table, key="table_source")

    year_min_table = int(df_emisiones["Year"].min())
    year_max_table = int(df_emisiones["Year"].max())
    years_table = st.slider("Select year range:", year_min_table, year_max_table, (year_min_table, year_max_table), key="table_years")

    if mode_table == "Country":
        countries_table = df_emisiones["Country"].dropna().unique()
        country_table = st.selectbox("Select country:", sorted(countries_table), key="table_country")
        df_filtered = df_emisiones[
            (df_emisiones["Country"] == country_table) &
            (df_emisiones["Year"] >= years_table[0]) &
            (df_emisiones["Year"] <= years_table[1])
        ]
        if source_table == "All":
            df_filtered = df_filtered.groupby(["Country", "Year"], as_index=False)["Emissions (Mt)"].sum()
            df_filtered["Source"] = "All"
        else:
            df_filtered = df_filtered[df_filtered["Source"] == source_table]

        total_country = df_filtered["Emissions (Mt)"].sum()
        st.dataframe(df_filtered.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
        st.metric(label=f"Total emissions of {country_table} ({source_table})", value=f"{round(total_country, 2)} Mt CO₂")

    elif mode_table == "Region":
        region_table = st.selectbox("Select region:", list(regions.keys()), key="table_region")
        df_filtered = df_emisiones[
            (df_emisiones["Country"].isin(regions[region_table])) &
            (df_emisiones["Year"] >= years_table[0]) &
            (df_emisiones["Year"] <= years_table[1])
        ]
        if source_table == "All":
            df_filtered = df_filtered.groupby(["Year"], as_index=False)["Emissions (Mt)"].sum()
            df_filtered["Source"] = "All"
        else:
            df_filtered = df_filtered[df_filtered["Source"] == source_table]
            df_filtered = df_filtered.groupby(["Year", "Source"], as_index=False)["Emissions (Mt)"].sum()

        total_region = df_filtered["Emissions (Mt)"].sum()
        st.dataframe(df_filtered.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
        st.metric(label=f"Total emissions of {region_table} ({source_table})", value=f"{round(total_region, 2)} Mt CO₂")

    # --- Chart View ---
    st.markdown("### 📈 Visualize Emissions")
    chart_type = st.selectbox("Select chart type:", ["Line Chart", "Bar Chart"], key="chart_type")
    mode_chart = st.radio("View chart by:", ["Country", "Region"], key="chart_mode")
    sources_chart = st.multiselect(
        "Select emission sources to display:",
        options=list(df_emisiones["Source"].unique()),
        default=list(df_emisiones["Source"].unique()),
        key="chart_sources"
    )
    year_min_chart = int(df_emisiones["Year"].min())
    year_max_chart = int(df_emisiones["Year"].max())
    years_chart = st.slider("Select year range for chart:", year_min_chart, year_max_chart, (year_min_chart, year_max_chart), key="chart_years")

    # X-axis selection
    x_axis_options = ["Year"]
    if mode_chart in ["Country", "Region"]:
        x_axis_options.append("Country")
    x_axis = st.selectbox("Select X-axis:", x_axis_options, key="chart_x_axis")

    # Filter data for chart
    df_chart = df_emisiones[df_emisiones["Source"].isin(sources_chart)]
    df_chart = df_chart[(df_chart["Year"] >= years_chart[0]) & (df_emisiones["Year"] <= years_chart[1])]

    # Apply mode filters
    if mode_chart == "Country":
        if x_axis == "Year":
            countries_chart = df_emisiones["Country"].dropna().unique()
            country_chart = st.selectbox("Select country for chart:", sorted(countries_chart), key="chart_country")
            df_chart = df_chart[df_chart["Country"] == country_chart]
        else:  # X-axis = Country
            region_chart = st.selectbox("Select region for country comparison:", list(regions.keys()), key="chart_region")
            df_chart = df_chart[df_chart["Country"].isin(regions[region_chart])]
    elif mode_chart == "Region":
        region_chart = st.selectbox("Select region for chart:", list(regions.keys()), key="chart_region")
        df_chart = df_chart[df_chart["Country"].isin(regions[region_chart])]

    # Group data for chart
    if x_axis == "Year":
        df_chart_grouped = df_chart.groupby(["Year", "Source"], as_index=False)["Emissions (Mt)"].sum()
    else:
        df_chart_grouped = df_chart.groupby(["Country", "Source"], as_index=False)["Emissions (Mt)"].sum()
        x_axis = "Country"

    # Color map
    color_map = {
        "Coal": "crimson",
        "Oil": "green",
        "Gas": "gray",
        "Cement": "skyblue",
        "Flaring": "darkorange"
    }

    # Plot chart
    if chart_type == "Line Chart":
        fig = px.line(
            df_chart_grouped,
            x=x_axis,
            y="Emissions (Mt)",
            color="Source",
            markers=True,
            title=f"{chart_type} of Emissions ({', '.join(sources_chart)})",
            color_discrete_map=color_map
        )
    else:
        fig = px.bar(
            df_chart_grouped,
            x=x_axis,
            y="Emissions (Mt)",
            color="Source",
            barmode="group",
            title=f"{chart_type} of Emissions ({', '.join(sources_chart)})",
            color_discrete_map=color_map
        )

    st.plotly_chart(fig, use_container_width=True)

elif section == "Geological Storage Capacity":
    st.subheader("🛢️ Geological Storage Capacity")
    st.markdown("""
    Here you can explore the **CO₂ geological storage capacity**.  
    First, select a **Region**, then one or more **countries** from that region.  
    If you select **America**, you will only see the total storage capacity per country.  
    """)

    df_reservoirs = pd.DataFrame({
        "Region": [
            "North America", "North America", "North America", "North America", "North America", "North America",
            "North America", "North America",
            "North America", "North America", "North America", "North America", "North America", "North America",
            "North America",
            "North America", "North America",
            "South America", "South America", "South America",
            "South America", "South America", "South America",
            "South America", "South America", "South America", "South America", "South America"
        ],
        "Country": [
            "Canada", "Canada", "Canada", "Canada", "Canada", "Canada", "Canada", "Canada",
            "USA", "USA", "USA", "USA", "USA", "USA", "USA",
            "Mexico", "Mexico",
            "Brazil", "Brazil", "Brazil",
            "Colombia", "Colombia", "Colombia",
            "Ecuador", "Ecuador", "Ecuador", "Ecuador", "Ecuador"
        ],
        "Reservoir": [
            "Leduc Formation (Clive Field)", "Midale Formation (Weyburn Field)", "Viking Formation (Chigwell Field)",
            "Leduc Formation (Redwater Field)", "Viking Formation (Joffre Field)", "Cardium Formation (Pembina Field)",
            "Basal Cambrian Sand (Quest)", "Deadwood Formation (Aquistore)",
            "Frio Formation (West Ranch Field)", "Weber Sandstone (Rangely Field)",
            "Muddy Formation (Bell Creek Field)", "Morrow Formation (Farnsworth Field)",
            "Mt. Simon Sandstone (Illinois Basin)", "Tuscaloosa Formation (Cranfield Field)",
            "Paluxy Formation (Citronelle Field)",
            "Cahuasas Formation (Tampico Misantla Basin)", "Tamaulipas Formation (Tampico Misantla Basin)",
            "Itapema Formation (Buzios Field)", "Barra Velha Formation (Buzios Field)",
            "Itapema Formation (Tupi Field)",
            "Siamana Formation (Guajira Basin)", "Jimol Formation (Guajira Basin)", "Jimol Formation (Sinu Basin)",
            "Hollín Superior (Sacha Field)", "Hollín Superior (Lago Agrio Field)", "U Inferior (Parahuacu Field)",
            "Napo T (Sacha Field)", "T Principal (Yanaquincha Este Field)"
        ],
        "Capacity (Mt)": [
            18.38, 125.13, 9.33, 79.33, 35.35, 861.54, 65.05, 67.06,
            47.79, 95.45, 13.0, 28.1, 393.15, 109.52, 753.19,
            823.39, 275.49,
            814.48, 892.36, 940.03,
            682.73, 359.42, 136.45,
            58.73, 3.63, 2.56, 17.35, 5.41
        ],
        "Depth (m)": [
            1832, 1450, 1385.6, 984, 1400, 1447, 2330, 3200,
            1752.6, 1980, 1360, 2330, 3060, 1690, 2865,
            3600, 2900,
            5000, 5000, 5000,
            1701, 1800, 3287,
            2735.58, 3040.38, 2649, 2671.58, 3048
        ],
        "Thickness (m)": [
            180, 20, 30, 250, 20, 32, 47, 38.6,
            27, 58, 8, 25, 28, 156, 143,
            400, 154,
            121.92, 151, 121.92,
            12, 37, 11,
            15.24, 5.48, 12.92, 10.21, 27.74
        ],
        "Porosity (%)": [
            8, 26, 13, 12, 13, 16.4, 17, 15,
            30, 58, 25, 23, 25.5, 21, 25,
            14, 9,
            13, 11.5, 13,
            17.5, 21, 24,
            14, 13, 11.9, 16, 15
        ],
        "Permeability (mD)": [
            95.02, 300, 72.89, 100, 349, 21.4, 1000, 20,
            900, 8, 900, 300, 100, 28, 300,
            100, 100,
            88.7, 122.6, 88.7,
            200, 250, 200,
            70, 70.64, 384, 200, 356
        ]
    })

    region_options = list(df_reservoirs["Region"].unique()) + ["America"]
    region = st.selectbox("🌎 Select region:", region_options)

    if region == "America":
        df_region = df_reservoirs.copy()
    else:
        df_region = df_reservoirs[df_reservoirs["Region"] == region]

    countries = st.multiselect("🏳️ Select country/countries:", df_region["Country"].unique())

    if countries:
        df_countries = df_region[df_region["Country"].isin(countries)]

        if region == "America":
            df_country_total = df_countries.groupby("Country", as_index=False)["Capacity (Mt)"].sum().round(2)

            st.subheader("🏳️ Total Capacity by Country")
            st.dataframe(df_country_total.style.format({"Capacity (Mt)": "{:.2f}"}), use_container_width=True)

            fig_country = px.bar(df_country_total, x="Country", y="Capacity (Mt)",
                                 color="Country", text="Capacity (Mt)",
                                 title="📊 Total Capacity per Country in America")
            st.plotly_chart(fig_country, use_container_width=True)

            st.metric(label="Total capacity (selected countries)",
                      value=f"{df_country_total['Capacity (Mt)'].sum():.2f} Mt CO₂")

        else:
            df_countries["Reservoir_Display"] = df_countries["Country"] + " - " + df_countries["Reservoir"]
            selected_display_reservoirs = st.multiselect(
                "🛢️ Select reservoir(s):",
                df_countries["Reservoir_Display"].unique()
            )

            if selected_display_reservoirs:
                df_selected = df_countries[df_countries["Reservoir_Display"].isin(selected_display_reservoirs)]
                st.subheader("🛢️ Selected Reservoir Data")
                st.dataframe(
                    df_selected[
                        ["Region", "Country", "Reservoir", "Capacity (Mt)", "Depth (m)", "Thickness (m)", "Porosity (%)",
                         "Permeability (mD)"]]
                    .style.format({
                        "Capacity (Mt)": "{:.2f}",
                        "Depth (m)": "{:.2f}",
                        "Thickness (m)": "{:.2f}",
                        "Porosity (%)": "{:.2f}",
                        "Permeability (mD)": "{:.2f}"
                    }).set_properties(**{'text-align': 'center'}),
                    use_container_width=True
                )

                if len(selected_display_reservoirs) == 1:
                    st.metric(label="Selected reservoir capacity",
                              value=f"{df_selected['Capacity (Mt)'].values[0]:.2f} Mt CO₂")

                st.metric(label="Total capacity of selected reservoir(s)",
                          value=f"{df_selected['Capacity (Mt)'].sum():.2f} Mt CO₂")
                st.metric(label=f"Total capacity in {region}",
                          value=f"{df_region['Capacity (Mt)'].sum():.2f} Mt CO₂")

                fig = px.bar(df_selected, x="Reservoir", y="Capacity (Mt)",
                             color="Country", text="Capacity (Mt)",
                             title=f"📊 Capacity per selected reservoir(s)")
                st.plotly_chart(fig, use_container_width=True)

elif section == "Carbon balance and emission removal":
    st.subheader("🟢 Carbon balance and emission removal")
    st.markdown("""
        Visualize the *carbon balance* and the *% of CO₂ emission removal* at different levels:
    """)

    df_balance = pd.DataFrame({
        "Region": ["North America", "North America", "North America", "South America", "South America",
                   "South America"],
        "Country": ["Canada", "USA", "Mexico", "Brazil", "Colombia", "Ecuador"],
        "CO₂ emissions (Mt)": [18354.93, 186820.53, 14502.65, 13050.66, 2477.66, 1038.67],
        "CO₂ stored (Mt)": [1261.17, 1440.20, 1098.88, 2646.87, 1178.60, 87.68]
    })

    df_balance["CO₂ not stored (Mt)"] = df_balance["CO₂ emissions (Mt)"] - df_balance["CO₂ stored (Mt)"]
    df_balance["% Removal"] = (df_balance["CO₂ stored (Mt)"] / df_balance["CO₂ emissions (Mt)"] * 100).round(2)

    with st.expander("🌎 Total balance - America"):
        df_balance_ext = df_balance.copy()

        df_emissions = pd.read_csv(data)
        df_emissions = df_emissions.melt(
            id_vars=["Entity", "Year"],
            value_vars=["Coal", "Oil", "Gas", "Flaring", "Cement"],
            var_name="Source",
            value_name="Emissions"
        )
        df_emissions["Emissions"] = df_emissions["Emissions"] / 1e6  # Mt
        df_emissions = df_emissions.rename(columns={"Emissions": "Emissions (Mt)"})

        extras = df_emissions[df_emissions["Entity"].isin(["Argentina", "Venezuela"])][
            ["Entity", "Emissions (Mt)"]
        ].copy()

        if not extras.empty:
            extras = extras.rename(columns={
                "Entity": "Country",
                "Emissions (Mt)": "CO₂ emissions (Mt)"
            })
            extras["Region"] = "South America"
            extras["CO₂ stored (Mt)"] = 0.0
            extras["CO₂ not stored (Mt)"] = extras["CO₂ emissions (Mt)"]
            extras["% Removal"] = 0.0

            cols = ["Region", "Country", "CO₂ emissions (Mt)", "CO₂ stored (Mt)",
                    "CO₂ not stored (Mt)", "% Removal"]
            df_balance_ext = pd.concat([df_balance_ext, extras[cols]], ignore_index=True)

        df_america = df_balance_ext.groupby("Region")[
            ["CO₂ emissions (Mt)", "CO₂ stored (Mt)", "CO₂ not stored (Mt)"]].sum().reset_index()
        df_america["% Removal"] = (df_america["CO₂ stored (Mt)"] / df_america["CO₂ emissions (Mt)"] * 100).round(2)

        total_emissions = df_america["CO₂ emissions (Mt)"].sum()
        total_stored = df_america["CO₂ stored (Mt)"].sum()
        total_not_stored = df_america["CO₂ not stored (Mt)"].sum()
        total_removal = (total_stored / total_emissions * 100).round(2)

        america_total = pd.DataFrame({
            "Region": ["America"],
            "CO₂ emissions (Mt)": [total_emissions],
            "CO₂ stored (Mt)": [total_stored],
            "CO₂ not stored (Mt)": [total_not_stored],
            "% Removal": [total_removal]
        })

        df_america = pd.concat([df_america, america_total], ignore_index=True)

        st.dataframe(
            df_america[["Region", "CO₂ emissions (Mt)", "CO₂ stored (Mt)", "CO₂ not stored (Mt)", "% Removal"]]
            .style.format({
                "CO₂ emissions (Mt)": "{:.2f}",
                "CO₂ stored (Mt)": "{:.2f}",
                "CO₂ not stored (Mt)": "{:.2f}",
                "% Removal": "{:.2f}%"
            }).set_properties(**{'text-align': 'center'})
        )

        fig = go.Figure()

        fig.add_bar(
            x=df_america["Region"],
            y=df_america["CO₂ not stored (Mt)"],
            name="CO₂ not removed",
            marker_color="silver",
            hovertemplate="Not removed: %{y:.2f} Mt"
        )

        fig.add_bar(
            x=df_america["Region"],
            y=df_america["CO₂ stored (Mt)"],
            name="CO₂ removed",
            marker_color="#6AA84F",
            hovertemplate="Removed: %{y:.2f} Mt<br>% Removal: %{customdata:.2f}%",
            customdata=df_america["% Removal"]
        )

        for i, row in df_america.iterrows():
            fig.add_annotation(
                x=row["Region"],
                y=row["CO₂ emissions (Mt)"],
                text=f"{row['% Removal']:.1f}%",
                showarrow=False,
                yshift=10
            )

        fig.update_layout(
            title="Emission balance in America",
            barmode="stack",
            yaxis_title="Total emissions (Mt CO₂)",
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
            title_x=0.5
        )

        st.plotly_chart(fig, use_container_width=True)

    with st.expander("🟢 Balance - North America"):
        df_na = df_balance[df_balance["Region"] == "North America"].copy()

        st.dataframe(
            df_na[["Country", "CO₂ emissions (Mt)", "CO₂ stored (Mt)", "CO₂ not stored (Mt)", "% Removal"]]
            .style.format({
                "CO₂ emissions (Mt)": "{:.2f}",
                "CO₂ stored (Mt)": "{:.2f}",
                "CO₂ not stored (Mt)": "{:.2f}",
                "% Removal": "{:.2f}%"
            }).set_properties(**{'text-align': 'center'})
        )

        st.metric("Total % removal North America",
                  f"{(df_na['CO₂ stored (Mt)'].sum() / df_na['CO₂ emissions (Mt)'].sum() * 100):.2f}%")
        st.metric("Total CO₂ stored", f"{df_na['CO₂ stored (Mt)'].sum():.2f} Mt CO₂")

        fig = go.Figure()

        fig.add_bar(
            x=df_na["Country"],
            y=df_na["CO₂ not stored (Mt)"],
            name="CO₂ not removed",
            marker_color="silver",
            hovertemplate="Not removed: %{y:.2f} Mt"
        )

        fig.add_bar(
            x=df_na["Country"],
            y=df_na["CO₂ stored (Mt)"],
            name="CO₂ removed",
            marker_color="#6AA84F",
            hovertemplate="Removed: %{y:.2f} Mt<br>% Removal: %{customdata:.2f}%",
            customdata=df_na["% Removal"]
        )

        for i, row in df_na.iterrows():
            fig.add_annotation(
                x=row["Country"],
                y=row["CO₂ emissions (Mt)"],
                text=f"{row['% Removal']:.1f}%",
                showarrow=False,
                yshift=10
            )

        fig.update_layout(
            title="Emission balance by country in North America",
            barmode="stack",
            yaxis_title="Total emissions (Mt CO₂)",
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
            title_x=0.5
        )

        st.plotly_chart(fig, use_container_width=True)

    with st.expander("🟢 Balance - South America"):
        df_sa = df_balance[df_balance["Region"] == "South America"].copy()

        df_emissions = pd.read_csv(data)
        df_emissions = df_emissions.melt(
            id_vars=["Entity", "Year"],
            value_vars=["Coal", "Oil", "Gas", "Flaring", "Cement"],
            var_name="Source",
            value_name="Emissions"
        )
        df_emissions["Emissions"] = df_emissions["Emissions"] / 1e6
        df_emissions = df_emissions.rename(columns={"Emissions": "Emissions (Mt)"})

        extras = df_emissions[df_emissions["Entity"].isin(["Argentina", "Venezuela"])]
        extras = extras.groupby("Entity", as_index=False)["Emissions (Mt)"].sum()
        extras.rename(columns={"Entity": "Country", "Emissions (Mt)": "CO₂ emissions (Mt)"}, inplace=True)

        extras["Region"] = "South America"
        extras["CO₂ stored (Mt)"] = pd.NA
        extras["CO₂ not stored (Mt)"] = pd.NA
        extras["% Removal"] = pd.NA

        cols = ["Region", "Country", "CO₂ emissions (Mt)", "CO₂ stored (Mt)", "CO₂ not stored (Mt)", "% Removal"]
        extras = extras.reindex(columns=cols)

        df_sa = pd.concat([df_sa, extras], ignore_index=True)

        df_sa["CO₂ not stored (Mt)"] = df_sa["CO₂ emissions (Mt)"] - df_sa["CO₂ stored (Mt)"]
        df_sa["% Removal"] = (df_sa["CO₂ stored (Mt)"] / df_sa["CO₂ emissions (Mt)"]) * 100

        st.dataframe(
            df_sa[["Country", "CO₂ emissions (Mt)", "CO₂ stored (Mt)", "CO₂ not stored (Mt)", "% Removal"]]
            .style.format({
                "CO₂ emissions (Mt)": "{:.2f}",
                "CO₂ stored (Mt)": "{:.2f}",
                "CO₂ not stored (Mt)": "{:.2f}",
                "% Removal": "{:.2f}%"
            }, na_rep="—").set_properties(**{'text-align': 'center'})
        )

        st.metric("Total % removal South America",
                  f"{(df_sa['CO₂ stored (Mt)'].fillna(0).sum() / df_sa['CO₂ emissions (Mt)'].sum() * 100):.2f}%")
        st.metric("Total CO₂ stored", f"{df_sa['CO₂ stored (Mt)'].fillna(0).sum():.2f} Mt CO₂")

        df_sa_plot = df_sa[~df_sa["Country"].isin(["Argentina", "Venezuela"])]

        fig = go.Figure()

        fig.add_bar(
            x=df_sa_plot["Country"],
            y=df_sa_plot["CO₂ not stored (Mt)"],
            name="CO₂ not removed",
            marker_color="silver",
            hovertemplate="Not removed: %{y:.2f} Mt"
        )

        fig.add_bar(
            x=df_sa_plot["Country"],
            y=df_sa_plot["CO₂ stored (Mt)"],
            name="CO₂ removed",
            marker_color="#6AA84F",
            hovertemplate="Removed: %{y:.2f} Mt<br>% Removal: %{customdata:.2f}%",
            customdata=df_sa_plot["% Removal"]
        )

        for i, row in df_sa_plot.iterrows():
            fig.add_annotation(
                x=row["Country"],
                y=row["CO₂ emissions (Mt)"],
                text=f"{row['% Removal']:.1f}%",
                showarrow=False,
                yshift=10
            )

        fig.update_layout(
            title="Emission balance by country in South America",
            barmode="stack",
            yaxis_title="Total emissions (Mt CO₂)",
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
            title_x=0.5
        )

        st.plotly_chart(fig, use_container_width=True)

    with st.expander("🌍 Balance - Country"):
        selected_countries = st.multiselect(
            "Select countries:",
            df_balance["Country"].unique()
        )

        df_selected = df_balance[df_balance["Country"].isin(selected_countries)].copy()
        df_selected = df_selected[~df_selected["Country"].str.contains("Total", case=False, na=False)]

        df_selected["% Removal"] = (
                (df_selected["CO₂ stored (Mt)"] / df_selected["CO₂ emissions (Mt)"]) * 100
        ).round(2)

        df_selected = df_selected.rename(columns={"CO₂ stored (Mt)": "CO₂ Removed (Mt)"})

        st.dataframe(
            df_selected[["Country", "CO₂ emissions (Mt)", "CO₂ Removed (Mt)", "% Removal"]]
            .style.format(
                {
                    "CO₂ emissions (Mt)": "{:.2f}",
                    "CO₂ Removed (Mt)": "{:.2f}",
                    "% Removal": "{:.2f}%"
                }
            ).set_properties(**{'text-align': 'center'}),
            use_container_width=True
        )

        fig = go.Figure()

        fig.add_bar(
            x=df_selected["Country"],
            y=df_selected["CO₂ emissions (Mt)"] - df_selected["CO₂ Removed (Mt)"],
            name="CO₂ not removed",
            marker_color="silver",
            hovertemplate="Not removed: %{y:.2f} Mt"
        )

        fig.add_bar(
            x=df_selected["Country"],
            y=df_selected["CO₂ Removed (Mt)"],
            name="CO₂ removed",
            marker_color="#6AA84F",
            hovertemplate="Removed: %{y:.2f} Mt<br>% Removal: %{customdata:.2f}%",
            customdata=df_selected["% Removal"]
        )

        for i, row in df_selected.iterrows():
            fig.add_annotation(
                x=row["Country"],
                y=row["CO₂ emissions (Mt)"],
                text=f"{row['% Removal']:.1f}%",
                showarrow=False,
                yshift=10
            )

        fig.update_layout(
            title="Emission balance by selected countries",
            barmode="stack",
            yaxis_title="Total emissions (Mt CO₂)",
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
            title_x=0.5
        )

        st.plotly_chart(fig, use_container_width=True)

elif section == "Reservoirs Location":
    # Load the coordinates of the countries where the EOR projects of this dataset are
    coordinates = {
        "Clive": ([52.42931464961698, -113.41669788869072], 5),
        "Weyburn": ([49.66753769, -103.85824585], 38),
        "Chigwell": ([52.632, -113.581], 140),
        "Redwater": ([53.953056, -113.110794], 8),
        "Joffre": ([52.336111, -113.537222], 1),
        "Pembina": ([53.062, -114.891], 1),
        "Quest": ([53.797248, -113.092769], 10),
        "Aquistore": ([49.096207, -103.033997], 1)
    }
    # Load the world map
    m = folium.Map(zoom_start=14)
    # Load the markers and popups
    for reservoir, point in coordinates.items():
        folium.Marker(
            point[0], popup="<b>{}: </b> {} EOR Projects".format(reservoir, point[1])
        ).add_to(m)
    folium_static(m)
