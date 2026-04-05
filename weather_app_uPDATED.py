import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 🔑 API KEY
API_KEY = "f8c2a69b6af499e2ae8bbd110d092b13"

st.set_page_config(page_title="Weather Dashboard", layout="wide")

# 🌈 Title
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🌦 Bangladesh Weather Dashboard</h1>", unsafe_allow_html=True)

# 📍 City selection
city = st.selectbox("Select City", ["Dhaka", "Chittagong", "Khulna", "Rajshahi", "Sylhet"])

# 🌐 API
url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},BD&appid={API_KEY}&units=metric"
data = requests.get(url).json()

if data.get("cod") != "200":
    st.error("API Error ❌")
else:
    weather_list = []

    for item in data['list']:
        weather_list.append({
            "date": item['dt_txt'],
            "temperature": item['main']['temp'],
            "humidity": item['main']['humidity'],
            "rainfall": item.get('rain', {}).get('3h', 0),
            "lat": data['city']['coord']['lat'],
            "lon": data['city']['coord']['lon']
        })

    df = pd.DataFrame(weather_list)
    df['date'] = pd.to_datetime(df['date'])

    # 📊 Metrics (Top cards)
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡 Max Temp", f"{df['temperature'].max():.1f} °C")
    col2.metric("💧 Avg Humidity", f"{df['humidity'].mean():.1f} %")
    col3.metric("🌧 Total Rain", f"{df['rainfall'].sum():.1f} mm")

    # 📈 Temperature chart
    fig1 = px.line(df, x="date", y="temperature", title="Temperature Trend")
    st.plotly_chart(fig1, use_container_width=True)

    # 🌧 Rainfall chart
    fig2 = px.bar(df, x="date", y="rainfall", title="Rainfall Chart")
    st.plotly_chart(fig2, use_container_width=True)

    # 🗺 Map
    st.subheader("📍 Location Map")
    st.map(df[['lat', 'lon']].drop_duplicates())

    # 📋 Table
    st.subheader("📊 Raw Data")
    st.dataframe(df)

    # 🚨 Alerts
    if df['temperature'].max() > 35:
        st.warning("🔥 Heat Alert!")

    if df['rainfall'].sum() > 20:
        st.info("🌧 Rain expected!")