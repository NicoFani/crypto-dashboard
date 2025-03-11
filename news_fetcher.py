import requests
import streamlit as st
from utils import format_timestamp

@st.cache_data(ttl=3600)
def get_crypto_news(limit=10):
    news_url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
    
    response = requests.get(news_url)
    if response.status_code == 200 and "Data" in response.json():
        return response.json()['Data'][:limit]
    else:
        st.error("Error al obtener noticias")
        return []

def display_news(news_items):
    if not news_items:
        st.info("No hay noticias disponibles en este momento.")
        return
        
    for item in news_items:
        st.markdown(f"""
        <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: transparent;">
            <div style="font-size: 18px; font-weight: bold; color: #1E88E5;">{item.get('title', 'Sin título')}</div>
            <div style="font-size: 14px; color: #ddd;">Fuente: {item.get('source', 'Desconocido')}</div>
            <div style="font-size: 14px; color: #ddd;">Publicado: {format_timestamp(item.get('published_on', 0))}</div>
            <p>{item.get('body', '')[:200]}...</p>
            <a href="{item.get('url', '#')}" target="_blank" style="color: #1E88E5;">Leer más</a>
        </div>
        """, unsafe_allow_html=True)
