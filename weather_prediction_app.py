import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_KEY = "f8c2a69b6af499e2ae8bbd110d092b13"

st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌦️",
    layout="centered"
)

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

st.markdown("""
<h1 style='text-align: center; color: #4CAF50;'>
🌦 Bangladesh Weather Dashboard
</h1>
""", unsafe_allow_html=True)

city = st.selectbox("📍 Select City",
    ["Dhaka", "Chittagong", "Khulna", "Rajshahi", "Sylhet"]
)

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

    # ✅ DAILY FORECAST (FIXED POSITION)
    df['day'] = df['date'].dt.date

    daily_df = df.groupby('day').agg({
        'temperature': 'mean',
        'humidity': 'mean',
        'rainfall': 'sum'
    }).reset_index()

    daily_df = daily_df.head(5)

    # ✅ METRICS
    st.markdown("### 📊 Overview")
    col1, col2, col3 = st.columns(3)

    col1.metric("🌡 Max Temp", f"{df['temperature'].max():.1f} °C")
    col2.metric("💧 Avg Humidity", f"{df['humidity'].mean():.1f} %")
    col3.metric("🌧 Total Rain", f"{df['rainfall'].sum():.1f} mm")

    # ✅ CHARTS
    st.markdown("### 📈 Temperature Trend")
    fig1 = px.line(df, x="date", y="temperature")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### 🌧 Rainfall Chart")
    fig2 = px.bar(df, x="date", y="rainfall")
    st.plotly_chart(fig2, use_container_width=True)

    # ✅ FORECAST CARDS (FULL FIX)
    st.markdown("### 📅 5-Day Forecast")

    cols = st.columns(len(daily_df))

    for i, row in daily_df.iterrows():

        icon = "☀️"
        if row['rainfall'] > 5:
            icon = "🌧️"
        elif row['humidity'] > 80:
            icon = "☁️"

        cols[i].markdown(f"""
            <div style='
                background:#ffffff;
                padding:15px;
                border-radius:15px;
                text-align:center;
                box-shadow:0 4px 10px rgba(0,0,0,0.1);
            '>
                <h4>{row['day']}</h4>
                <h2>{icon} {row['temperature']:.1f}°C</h2>
                <p>💧 {row['humidity']:.0f}%</p>
                <p>🌧 {row['rainfall']:.1f} mm</p>
            </div>
        """, unsafe_allow_html=True)

    # ✅ MAP
    st.markdown("### 🗺 Location")
    st.map(df[['lat', 'lon']].drop_duplicates())

    # ✅ TABLE
    with st.expander("📊 View Raw Data"):
        st.dataframe(df)

    # ✅ ALERTS
    st.markdown("### 🚨 Alerts")

    if df['temperature'].max() > 35:
        st.warning("🔥 Heat Alert!")

    if df['rainfall'].sum() > 20:
        st.info("🌧 Rain expected!")
