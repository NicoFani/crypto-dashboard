import streamlit as st
import pandas as pd
import plotly.express as px
from data_fetcher import get_data, get_crypto_data
from news_fetcher import get_crypto_news, display_news
from utils import format_timestamp

# Configuración de la página
st.set_page_config(page_title="Crypto Data", page_icon="assets/logo.png", layout="wide")

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
        
        /* Estilo para las tarjetas de noticias */
        .news-card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 15px;
            background-color: transparent;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .news-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #1E88E5;
        }
        
        .news-source {
            font-size: 14px;
            color: #cacaca;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .news-date {
            font-size: 14px;
            color: #cacaca;
            margin-bottom: 10px;
            font-weight: bold;
        }
        
        .news-body {
            font-size: 14px;
            margin-bottom: 10px;
            color: #ddd;
        }
        
        .news-link {
            font-size: 14px;
            color: #1E88E5;
        }
    </style>
""", unsafe_allow_html=True)

def price_time_graph(crypto_id):
    # Opciones de periodo de tiempo (eliminada la opción de 3 años)
    time_options = {
        "7 días": "7",
        "14 días": "14",
        "1 mes": "30",
        "1 año": "365",
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
        button_cols = st.columns(4)  # 4 botones en una fila
        
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
                    elif st.session_state.selected_period == "30":
                        date_format = '%d %b'  # Formato día mes para 1 mes
                    elif st.session_state.selected_period == "365":
                        date_format = '%b %Y'  # Formato mes año para 1 año
                    
                    # Configurar la densidad de las marcas en el eje X según el periodo
                    if st.session_state.selected_period in ["7", "14", "30"]:
                        n_ticks = 7  # Más ticks para periodos cortos
                    elif st.session_state.selected_period == "365":
                        n_ticks = 12  # Un tick por mes aproximadamente

                    # Obtener el color de fondo de Streamlit para usarlo en el gráfico
                    # Streamlit usa un fondo gris muy claro, casi blanco
                    streamlit_bg_color = "rgba(250, 250, 250, 0)"
                    
                    upper_crypto_id = crypto_id.upper()

                    # Graficar con título actualizado que incluye el periodo
                    fig = px.line(
                        df_prices, 
                        x='Fecha', 
                        y='Precio', 
                        title=f"Precio Historico de {upper_crypto_id}"
                    )
                    
                    # Configuración adicional del gráfico
                    fig.update_layout(
                        xaxis_title='Fecha',
                        yaxis_title='Precio (USD)',
                        hovermode='x unified',
                        plot_bgcolor=streamlit_bg_color,  # Cambiado para coincidir con el fondo de Streamlit
                        paper_bgcolor=streamlit_bg_color,  # También cambiado el fondo del papel
                        title_font_size=20,    # Tamaño del título
                        yaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(230, 230, 230, 0)'  # Grid más sutil
                        ),
                        xaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(230, 230, 230, 0)',  # Grid más sutil
                            nticks=n_ticks  # Número de marcas en el eje X
                        )
                    )
                    
                    # Formatear etiquetas del eje x según el periodo
                    fig.update_xaxes(
                        tickformat=date_format,
                        tickangle=-45 if st.session_state.selected_period in ["7", "14", "30"] else 0
                    )
                    
                    # Mejorar estética de la línea
                    fig.update_traces(
                        line=dict(width=2, color='#4682B4'),  # Línea más gruesa y azul
                        mode='lines'  # Solo líneas, sin marcadores
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error al procesar los datos para el gráfico de líneas: {e}")
            else:
                st.error("No se encontraron datos de precios disponibles.")
        else:
            st.error("No se pudo cargar el gráfico de precios.")

st.sidebar.markdown(
    """
    <div style="display: flex; flex-direction: column; align-items: center;">
        <h1 style="margin-left: 10px; font-size: 36px; font-weight: bold;">CRYPTO DATA</h1>
        <hr style="margin: 10px 0px; border: 0; height: 1px; background-color: #ddd; width: 100%;">
    </div>
    """,
    unsafe_allow_html=True
)

nav_option = st.sidebar.radio(
    "",
    ("Datos en Tiempo Real", "Comparación de Precios", "Capitalización de Mercado", "Gráfico de Precio", "Destacadas de Hoy", "Noticias"),
    index=0  # La opción por defecto es "Datos en Tiempo Real"
)

# Obtener los datos
with st.spinner("Cargando datos..."):
    df = get_data()

# Sección: Datos en Tiempo Real
if nav_option == "Datos en Tiempo Real":
    st.header("📋 Datos en Tiempo Real")
    st.divider()
    st.dataframe(df[["Nombre", "Símbolo", "Precio Actual", "Capitalización de Mercado", "Volumen Total", "Máximo 24h", "Mínimo 24h"]])
    st.markdown("Todos los valores estan expresados en Dolares Estadounidenses (USD)")

# Sección: Comparación de Precios (Top 10)
elif nav_option == "Comparación de Precios":
    st.header("💰 Comparación de Precios")
    st.divider()
    df_top10 = df.head(10)
    fig = px.bar(
        df_top10, x="Nombre", y="Precio Actual", text="Precio Actual", color="Nombre",
        labels={"Nombre": "Criptomoneda", "Precio Actual": "Precio en USD"}
    )
    # Actualizar el fondo del gráfico para que coincida con Streamlit
    fig.update_layout(
        plot_bgcolor="rgba(250, 250, 250, 0)",
        paper_bgcolor="rgba(250, 250, 250, 0)"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("Todos los valores estan expresados en Dolares Estadounidenses (USD)")

# Sección: Capitalización de Mercado (Top 10)
elif nav_option == "Capitalización de Mercado":
    st.header("🌎 Capitalización de Mercado")
    st.divider()
    df_top10 = df.head(10)
    fig2 = px.pie(
        df_top10, names="Nombre", values="Capitalización de Mercado", 
        labels={"Nombre": "Criptomoneda", "Capitalización de Mercado": "Capitalización (USD)"}
    )
    fig2.update_layout(
        width=500,
        height=500,
    )

    st.plotly_chart(fig2)
    st.markdown("Todos los valores estan expresados en Dolares Estadounidenses (USD)")

# Sección: Gráfico de Precio (Basado en selección)
elif nav_option == "Gráfico de Precio":
    st.header("📉 Gráfico de Precio historico")
    st.divider()
    # Create a mapping of display names to IDs
    crypto_map = dict(zip(df["Nombre"], df["id"]))
    # Display options using names
    crypto_options = df.head(10)["Nombre"].tolist()
    selected_crypto_name = st.selectbox("Selecciona una criptomoneda", crypto_options)
    # Get the corresponding ID
    selected_crypto_id = crypto_map.get(selected_crypto_name)
    # Use the ID for API calls
    price_time_graph(selected_crypto_id)

elif nav_option == "Destacadas de Hoy":
    st.header("⚡ Criptomonedas Destacadas del Día")
    st.divider()

    # Asegurarse de que el DataFrame no esté vacío
    if not df.empty:
        # Verificar si las columnas relevantes tienen datos
        if 'price_change_percentage_24h' in df.columns and not df['price_change_percentage_24h'].isna().all():
            max_price = df.loc[df["price_change_percentage_24h"].idxmax()]
            min_price = df.loc[df["price_change_percentage_24h"].idxmin()]
        else:
            max_price = min_price = None

        if 'market_cap_change_percentage_24h' in df.columns and not df['market_cap_change_percentage_24h'].isna().all():
            max_market_cap = df.loc[df["market_cap_change_percentage_24h"].idxmax()]
        else:
            max_market_cap = None

        if 'Volumen Total' in df.columns and not df['Volumen Total'].isna().all():
            max_volume = df.loc[df["Volumen Total"].idxmax()]
        else:
            max_volume = None

        # Criptomoneda más cercana a su ATH utilizando 'ath_change_percentage'
        if 'ath_change_percentage' in df.columns and not df['ath_change_percentage'].isna().all():
            closest_to_ath = df.loc[df["ath_change_percentage"].abs().idxmin()]  # Cripto con el menor porcentaje de cambio respecto al ATH
        else:
            closest_to_ath = None
        
        # Mejor ROI: Filtrar las criptomonedas con ROI no nulo
        if 'roi' in df.columns:
            df_valid_roi = df[df['roi'].notna()]  # Filtrar criptos con ROI no nulo
            if not df_valid_roi.empty:
                df_valid_roi['roi_percentage'] = df_valid_roi['roi'].apply(lambda x: x['percentage'] if isinstance(x, dict) else None)
                best_roi = df_valid_roi.loc[df_valid_roi["roi_percentage"].idxmax()]  # Cripto con el mejor ROI
            else:
                best_roi = None
        else:
            best_roi = None

        # Mostrar resultados en tarjetas informativas
        col1, col2, col3 = st.columns(3)

        with col1:
            if max_price is not None:
                st.metric(label="📈 Mayor subida de precio", value=max_price["Nombre"], delta=f"{max_price['price_change_percentage_24h']:.2f}%")
            if max_market_cap is not None:
                st.metric(label="🏆 Mayor crecimiento Market Cap", value=max_market_cap["Nombre"], delta=f"{max_market_cap['market_cap_change_percentage_24h']:.2f}%")
        
        with col2:
            if min_price is not None:
                st.metric(label="📉 Mayor caída de precio", value=min_price["Nombre"], delta=f"{min_price['price_change_percentage_24h']:.2f}%")
            if max_volume is not None:
                st.metric(label="🔥 Mayor volumen total", value=max_volume["Nombre"], delta=f"{max_volume['Volumen Total']:.2f} USD")
        
        with col3:
            if closest_to_ath is not None:
                st.metric(label="💎 Más cercana a ATH", value=closest_to_ath["Nombre"], delta=f"{closest_to_ath['ath_change_percentage']:.2f}%")
            if best_roi is not None:
                st.metric(label="💰 Mejor ROI", value=best_roi["Nombre"], delta=f"{best_roi['roi_percentage']:.2f}%")
        
        st.markdown("_Datos actualizados diariamente._")
    else:
        st.warning("No se encontraron datos disponibles.")

# Nueva sección: Noticias de Criptomonedas
elif nav_option == "Noticias":
    st.header("📰 Últimas Noticias de Criptomonedas")
    st.divider()
    # Opciones para filtrar noticias
    col1, col2 = st.columns([3, 1])
    
    with col2:
        news_count = st.slider("Número de noticias a mostrar", min_value=5, max_value=30, value=10, step=5)
    
    with col1:
        # Botón para actualizar noticias
        if st.button("🔄 Actualizar noticias"):
            # Forzar actualización del caché
            st.cache_data.clear()
    
    # Mostrar spinner mientras se cargan las noticias
    with st.spinner("Cargando las últimas noticias..."):
        news_items = get_crypto_news(limit=news_count)
        display_news(news_items)