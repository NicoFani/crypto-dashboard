import requests
import pandas as pd
import streamlit as st

API_URL = "https://api.coingecko.com/api/v3/coins/markets"

params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "page": 1,
    "sparkline": False
}

@st.cache_data
def get_data():
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        df = df.rename(columns={
            "name": "Nombre",
            "symbol": "Símbolo",
            "current_price": "Precio Actual",
            "market_cap": "Capitalización de Mercado",
            "total_volume": "Volumen Total",
            "high_24h": "Máximo 24h",
            "low_24h": "Mínimo 24h"
        })
        df["Símbolo"] = df["Símbolo"].str.upper()
        return df
    else:
        st.error("Error al obtener datos de la API")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_crypto_data(crypto_id="bitcoin", days="30"):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    
    response = requests.get(url, params=params)
    if response.status_code == 200 and "prices" in response.json():
        return response.json()
    else:
        st.error("Error al obtener datos históricos")
        return None
