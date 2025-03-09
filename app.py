import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Crypto Dashboard", layout="wide")

# Título
st.title("📈 Dashboard de Criptomonedas")

# CSS para personalizar el tamaño de la fuente y mejorar la estética
st.markdown("""
    <style>
        /* Cambiar tamaño de fuente para toda la página */
        body {
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
        })

        # Convertir el símbolo a mayúsculas
        df["Símbolo"] = df["Símbolo"].str.upper()

        return df
    else:
        st.error("Error al obtener datos de la API")
        return pd.DataFrame()

# Función para obtener el historial de precios para los gráficos
def get_crypto_data(crypto_id="bitcoin"):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    params = {"vs_currency": "usd", "days": "30", "interval": "daily"}
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

# Función para el gráfico de precio a lo largo del tiempo
def price_time_graph(crypto_id):
    historical_data = get_crypto_data(crypto_id)
    
    if historical_data is not None:
        prices = historical_data.get('prices', [])
        
        # Verificar que 'prices' contenga datos
        if prices:
            try:
                # Convertir los datos a un DataFrame
                df_prices = pd.DataFrame(prices, columns=["Fecha", "Precio"])
                df_prices['Fecha'] = pd.to_datetime(df_prices['Fecha'], unit='ms')

                # Graficar
                fig = px.line(df_prices, x='Fecha', y='Precio', title=f"Precio de {crypto_id} a lo largo del tiempo")
                st.plotly_chart(fig)
            except Exception as e:
                st.error(f"Error al procesar los datos para el gráfico de líneas: {e}")
        else:
            st.error("No se encontraron datos de precios disponibles.")
    else:
        st.error("No se pudo cargar el gráfico de precios.")

# Función para el gráfico de velas (candlestick)
def candlestick_graph(crypto_id):
    historical_data = get_crypto_data(crypto_id)
    
    if historical_data is not None:
        prices = historical_data.get('prices', [])
        
        # Verificar que 'prices' contenga datos
        if prices:
            try:
                # Convertir los datos a un DataFrame
                df_prices = pd.DataFrame(prices, columns=["Fecha", "Precio"])
                df_prices['Fecha'] = pd.to_datetime(df_prices['Fecha'], unit='ms')

                # Crear columnas para el gráfico de velas (usando el mismo valor para open, high, low, close)
                df_prices['Open'] = df_prices['Precio']
                df_prices['High'] = df_prices['Precio']
                df_prices['Low'] = df_prices['Precio']
                df_prices['Close'] = df_prices['Precio']

                # Graficar el gráfico de velas
                fig = go.Figure(data=[go.Candlestick(x=df_prices['Fecha'],
                                                     open=df_prices['Open'], high=df_prices['High'],
                                                     low=df_prices['Low'], close=df_prices['Close'])])

                fig.update_layout(title=f"Gráfico de Velas de {crypto_id}", xaxis_title='Fecha', yaxis_title='Precio (USD)')
                st.plotly_chart(fig)
            except Exception as e:
                st.error(f"Error al procesar los datos para el gráfico de velas: {e}")
        else:
            st.error("No se encontraron datos de precios disponibles para el gráfico de velas.")
    else:
        st.error("No se pudo cargar el gráfico de velas.")

# Menú de navegación en la barra lateral
nav_option = st.sidebar.radio(
    "Selecciona una opción",
    ("Datos en Tiempo Real", "Comparación de Precios", "Capitalización de Mercado", "Gráfico de Precio", "Gráfico de Velas"),
    index=0  # La opción por defecto es "Datos en Tiempo Real"
)

# Obtener los datos
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
        title="Distribución de Capitalización (Top 10)",
        labels={"Nombre": "Criptomoneda", "Capitalización de Mercado": "Capitalización (USD)"}
    )
    st.plotly_chart(fig2)

# Sección: Gráfico de Precio (Basado en selección)
elif nav_option == "Gráfico de Precio":
    st.subheader("📉 Gráfico de Precio")
    st.markdown("Proximamente...")
    # Mostrar el top 10 para seleccionar una criptomoneda
    # crypto_options = df.head(10)["Nombre"].tolist()
    # selected_crypto = st.selectbox("Selecciona una criptomoneda", crypto_options)
    # price_time_graph(selected_crypto)

# Sección: Gráfico de Velas (Basado en selección)
elif nav_option == "Gráfico de Velas":
    st.subheader("📊 Gráfico de Velas")
    st.markdown("Proximamente...")
    # Mostrar el top 10 para seleccionar una criptomoneda
    # crypto_options = df.head(10)["Nombre"].tolist()
    # selected_crypto = st.selectbox("Selecciona una criptomoneda", crypto_options)
    # candlestick_graph(selected_crypto)
