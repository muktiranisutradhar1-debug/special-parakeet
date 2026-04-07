import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 🔑 API KEY
API_KEY = "f8c2a69b6af499e2ae8bbd110d092b13"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌦️",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 50px;
        border-radius: 12px;
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>
        🌦 Bangladesh Weather Dashboard
    </h1>
""", unsafe_allow_html=True)

st.write("")

# ---------------- CITY SELECT ----------------
city = st.selectbox(
    "📍 Select City",
    ["Dhaka", "Chittagong", "Khulna", "Rajshahi", "Sylhet"]
)

# ---------------- API ----------------
url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},BD&appid={API_KEY}&units=metric"
data = requests.get(url).json()

if data.get("cod") != "200":
    st.error("❌ API Error")
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

    # ---------------- BEAUTIFUL METRIC CARDS ----------------
    st.markdown("### 📊 Overview")

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
        <div style='background:#ff7675;padding:15px;border-radius:15px;text-align:center;color:white;'>
            <h4>🌡 Max Temp</h4>
            <h2>{df['temperature'].max():.1f} °C</h2>
        </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
        <div style='background:#74b9ff;padding:15px;border-radius:15px;text-align:center;color:white;'>
            <h4>💧 Avg Humidity</h4>
            <h2>{df['humidity'].mean():.1f} %</h2>
        </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
        <div style='background:#55efc4;padding:15px;border-radius:15px;text-align:center;color:black;'>
            <h4>🌧 Total Rain</h4>
            <h2>{df['rainfall'].sum():.1f} mm</h2>
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    # ---------------- TEMPERATURE CHART ----------------
    st.markdown("### 📈 Temperature Trend")
    fig1 = px.line(df, x="date", y="temperature")
    st.plotly_chart(fig1, use_container_width=True)

    # ---------------- RAIN CHART ----------------
    st.markdown("### 🌧 Rainfall Chart")
    fig2 = px.bar(df, x="date", y="rainfall")
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------- MAP ----------------
    st.markdown("### 🗺 Location")
    st.map(df[['lat', 'lon']].drop_duplicates())

    # ---------------- DATA TABLE ----------------
    with st.expander("📊 View Raw Data"):
        st.dataframe(df)

    # ---------------- ALERTS ----------------
    st.markdown("### 🚨 Alerts")

    if df['temperature'].max() > 35:
        st.warning("🔥 Heat Alert!")

    if df['rainfall'].sum() > 20:
        st.info("🌧 Rain expected!")