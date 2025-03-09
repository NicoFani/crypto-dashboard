import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time

# Configuración de la página
st.set_page_config(page_title="Crypto Dashboard", layout="wide")

# Título
st.title("📈 Crypto Dashboard")
st.divider()

# CSS para personalizar el tamaño de la fuente y mejorar la estética
st.markdown("""
    <style>
        /* Cambiar tamaño de fuente para toda la página */
        html, body {
            font-size: 18px;
        }
        
        /* Cambiar tamaño de la fuente en los encabezados de la página */
        .css-1v0mbdj h1, .css-1v0mbdj h2, .css-1v0mbdj h3, .css-1v0mbdj h4 {
            font-size: 30px;
        }

        /* Cambiar tamaño de la fuente en la barra lateral (sidebar) */
        .css-1d391kg {
            font-size: 20px;
        }

        /* Cambiar el tamaño de la fuente de los títulos de las gráficas */
        .plotly-graph-div .xtitle, .plotly-graph-div .ytitle {
            font-size: 18px !important;
        }

        /* Cambiar el tamaño de las leyendas en los gráficos */
        .plotly-graph-div .legendtext {
            font-size: 18px !important;
        }

        /* Cambiar el tamaño de la fuente en el texto de la tabla */
        .css-1v0mbdj .stDataFrame {
            font-size: 18px;
        }

        /* Cambiar tamaño de la fuente en los botones (si hay) */
        .css-1d391kg button {
            font-size: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# API de CoinGecko
API_URL = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,  # Mostrar el top 50 de criptos
    "page": 1,
    "sparkline": False
}

# Función para obtener datos de criptomonedas
@st.cache_data
def get_data():
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        # Renombrar columnas
        df = df.rename(columns={
            "name": "Nombre",
            "symbol": "Símbolo",
            "current_price": "Precio Actual (USD)",
            "market_cap": "Capitalización de Mercado",
            "total_volume": "Volumen Total",
            "high_24h": "Máximo 24h",
            "low_24h": "Mínimo 24h"
            # Don't rename "id" column so we can use it later
        })

        # Convertir el símbolo a mayúsculas
        df["Símbolo"] = df["Símbolo"].str.upper()

        return df
    else:
        st.error("Error al obtener datos de la API")
        return pd.DataFrame()



# Función modificada para obtener datos históricos con periodo personalizable
@st.cache_data(ttl=3600, show_spinner=False)
def get_crypto_data(crypto_id="bitcoin", days="30"):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    
    response = requests.get(url, params=params)
    
    # Verificar si la respuesta es válida y contiene 'prices'
    if response.status_code == 200:
        data = response.json()
        
        # Verificar si 'prices' está presente en la respuesta
        if 'prices' in data:
            return data
        else:
            st.error(f"No se encontraron datos de precios para la criptomoneda {crypto_id}.")
            return None
    else:
        st.error("Error al obtener datos de la API. Código de respuesta: {}".format(response.status_code))
        return None

# Función mejorada para el gráfico de precio con selector de periodo (sin opción de 1 día)
def price_time_graph(crypto_id):
    # Opciones de periodo de tiempo (eliminada la opción de 1 día)
    time_options = {
        "7 días": "7",
        "14 días": "14",
        "1 mes": "30",
        "1 año": "365"
    }
    
    # Crear contenedor para el gráfico
    chart_container = st.container()

        # CSS personalizado para mejorar la estética de los botones
    st.markdown("""
    <style>
    div.stButton > button {
        padding: 5px 10px;
        font-size: 14px;
        width: 100%;
        border-radius: 5px;
        margin: 0 2px;
    }
    
    /* Estilo para el botón activo */
    div.stButton > button:focus {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # Crear un contenedor centrado para los botones usando columns
    _, col_buttons, _ = st.columns([0.2, 0.6, 0.2])  # Centra los botones usando espacios a los lados
    
    with col_buttons:
        # Crear una fila horizontal de botones más cercanos entre sí
        button_cols = st.columns(4)  # 5 botones en una fila
        
        with button_cols[0]:
            days_7 = st.button("7 días")
        with button_cols[1]:
            days_14 = st.button("14 días")
        with button_cols[2]:
            month_1 = st.button("1 mes")
        with button_cols[3]:
            year_1 = st.button("1 año")
    
    # Determinar el periodo seleccionado basado en los botones
    if 'selected_period' not in st.session_state:
        st.session_state.selected_period = "30"  # Valor por defecto: 1 mes
    
    if days_7:
        st.session_state.selected_period = "7"
    elif days_14:
        st.session_state.selected_period = "14"
    elif month_1:
        st.session_state.selected_period = "30"
    elif year_1:
        st.session_state.selected_period = "365"
    
    # Obtener datos para el periodo seleccionado
    with st.spinner("Cargando datos de precios..."):
        historical_data = get_crypto_data(crypto_id, st.session_state.selected_period)
    
    # Encontrar el nombre legible del periodo
    period_name = [name for name, value in time_options.items() if value == st.session_state.selected_period][0]
    
    # Mostrar gráfico en el contenedor
    with chart_container:
        if historical_data is not None:
            prices = historical_data.get('prices', [])
            
            # Verificar que 'prices' contenga datos
            if prices:
                try:
                    # Convertir los datos a un DataFrame
                    df_prices = pd.DataFrame(prices, columns=["Fecha", "Precio"])
                    df_prices['Fecha'] = pd.to_datetime(df_prices['Fecha'], unit='ms')

                    # Determinar el formato de fecha basado en el periodo
                    if st.session_state.selected_period in ["7", "14"]:
                        date_format = '%d %b'  # Formato día mes para periodos cortos
                    else:
                        date_format = '%d %b %Y'  # Formato día mes año para periodos largos

                    # Graficar con título actualizado que incluye el periodo
                    
                    upper_crypto_id = crypto_id.upper()
                    
                    fig = px.line(
                        df_prices, 
                        x='Fecha', 
                        y='Precio', 
                    )
                    
                    # Configuración adicional del gráfico
                    fig.update_layout(
                        xaxis_title='Fecha',
                        yaxis_title='Precio (USD)',
                        hovermode='x unified'
                    )
                    
                    # Formatear etiquetas del eje x según el periodo
                    fig.update_xaxes(
                        tickformat=date_format,
                        tickangle=-45 if st.session_state.selected_period in ["7", "14"] else 0
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error al procesar los datos para el gráfico de líneas: {e}")
            else:
                st.error("No se encontraron datos de precios disponibles.")
        else:
            st.error("No se pudo cargar el gráfico de precios.")

# Menú de navegación en la barra lateral
nav_option = st.sidebar.radio(
    "Selecciona una opción",
    ("Datos en Tiempo Real", "Comparación de Precios", "Capitalización de Mercado", "Gráfico de Precio"),
    index=0  # La opción por defecto es "Datos en Tiempo Real"
)

# Obtener los datos
with st.spinner("Cargando datos..."):
    df = get_data()

# Sección: Datos en Tiempo Real
if nav_option == "Datos en Tiempo Real":
    st.subheader("📋 Datos en Tiempo Real")
    st.dataframe(df[["Nombre", "Símbolo", "Precio Actual (USD)", "Capitalización de Mercado", "Volumen Total", "Máximo 24h", "Mínimo 24h"]])

# Sección: Comparación de Precios (Top 10)
elif nav_option == "Comparación de Precios":
    st.subheader("💰 Comparación de Precios")
    df_top10 = df.head(10)
    fig = px.bar(
        df_top10, x="Nombre", y="Precio Actual (USD)", text="Precio Actual (USD)", color="Nombre",
        labels={"Nombre": "Criptomoneda", "Precio Actual (USD)": "Precio en USD"}
    )
    st.plotly_chart(fig, use_container_width=True)

# Sección: Capitalización de Mercado (Top 10)
elif nav_option == "Capitalización de Mercado":
    st.subheader("🌎 Capitalización de Mercado")
    df_top10 = df.head(10)
    fig2 = px.pie(
        df_top10, names="Nombre", values="Capitalización de Mercado", 
        labels={"Nombre": "Criptomoneda", "Capitalización de Mercado": "Capitalización (USD)"}
    )
    st.plotly_chart(fig2)

# Sección: Gráfico de Precio (Basado en selección)
elif nav_option == "Gráfico de Precio":
    st.subheader("📉 Gráfico de Precio historico")
    # Create a mapping of display names to IDs
    crypto_map = dict(zip(df["Nombre"], df["id"]))
    # Display options using names
    crypto_options = df.head(10)["Nombre"].tolist()
    selected_crypto_name = st.selectbox("Selecciona una criptomoneda", crypto_options)
    # Get the corresponding ID
    selected_crypto_id = crypto_map.get(selected_crypto_name)
    # Use the ID for API calls
    price_time_graph(selected_crypto_id)
