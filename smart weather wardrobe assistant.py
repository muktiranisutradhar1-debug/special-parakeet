import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Smart Weather Wardrobe Assistant",
    page_icon="🌦️",
    layout="centered"
)

# ----------------- CUSTOM CSS -----------------
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 50px;
        border-radius: 12px;
        font-size: 18px;
    }
    .metric-card {
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- TITLE -----------------
st.markdown("""
<h1 style='text-align: center; color: #4CAF50;'>
    🌦 Smart Weather Wardrobe Assistant
</h1>
""", unsafe_allow_html=True)

st.write("Get daily outfit suggestions based on weather!")

# ----------------- USER INPUT -----------------
user_type = st.selectbox("👤 Select User Type", ["Male", "Female", "Child"])
city = st.text_input("📍 Enter Your City", "Dhaka")

# ----------------- FETCH WEATHER -----------------
API_KEY = "f8c2a69b6af499e2ae8bbd110d092b13"
url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},BD&appid={API_KEY}&units=metric"

try:
    data = requests.get(url).json()
except:
    st.error("❌ Could not fetch weather data. Check your API key or internet connection.")
    st.stop()

if data.get("cod") != "200":
    st.error("❌ City not found. Try another city.")
    st.stop()

# ----------------- PREPARE DATA -----------------
weather_list = []
for item in data['list']:
    weather_list.append({
        "date": item['dt_txt'],
        "temperature": item['main']['temp'],
        "humidity": item['main']['humidity'],
        "rainfall": item.get('rain', {}).get('3h', 0)
    })

df = pd.DataFrame(weather_list)
df['date'] = pd.to_datetime(df['date'])
df['day'] = df['date'].dt.date

# 5-day forecast
daily_df = df.groupby('day').agg({
    'temperature': 'mean',
    'humidity': 'mean',
    'rainfall': 'sum'
}).reset_index().head(5)

# ----------------- SMART METRIC CARDS -----------------
st.markdown("### 📊 Today’s Weather Overview")
col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class='metric-card' style='background:#ff7675;'>
    🌡 <b>Max Temp</b><br>{df['temperature'].max():.1f} °C
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class='metric-card' style='background:#74b9ff;'>
    💧 <b>Avg Humidity</b><br>{df['humidity'].mean():.1f} %
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class='metric-card' style='background:#55efc4; color:black;'>
    🌧 <b>Total Rain</b><br>{df['rainfall'].sum():.1f} mm
</div>
""", unsafe_allow_html=True)

# ----------------- FORECAST CHARTS -----------------
st.markdown("### 📈 5-Day Temperature Trend")
fig1 = px.line(daily_df, x="day", y="temperature", markers=True, title=f"{city} Temperature Trend")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("### 🌧 5-Day Rainfall Forecast")
fig2 = px.bar(daily_df, x="day", y="rainfall", title=f"{city} Rainfall Forecast")
st.plotly_chart(fig2, use_container_width=True)

# ----------------- OUTFIT RECOMMENDATION LOGIC -----------------
def get_outfit(temp, rain, user_type):
    if rain > 1:
        return "🌧 Wear Raincoat / Take Umbrella"
    if temp > 35:
        return {"Male":"T-shirt & Shorts", "Female":"Light Dress", "Child":"T-shirt & Shorts"}[user_type]
    if temp > 30:
        return {"Male":"Polo & Chinos", "Female":"Top & Skirt", "Child":"T-shirt & Pants"}[user_type]
    if temp > 20:
        return {"Male":"Shirt & Jeans", "Female":"Top & Jeans", "Child":"Long-sleeve & Pants"}[user_type]
    if temp > 10:
        return {"Male":"Sweater & Jacket", "Female":"Sweater & Jacket", "Child":"Sweater & Pants"}[user_type]
    return {"Male":"Heavy Jacket & Scarf", "Female":"Coat & Scarf", "Child":"Jacket & Warm Clothes"}[user_type]

# ----------------- DISPLAY FORECAST CARDS -----------------
st.markdown("### 📅 5-Day Outfit Recommendation")

cols = st.columns(len(daily_df))
for idx, row in daily_df.iterrows():
    temp = row['temperature']
    rain = row['rainfall']
    icon = "☀️"
    if rain > 1:
        icon = "🌧️"
    elif temp > 35:
        icon = "🔥"
    elif temp < 15:
        icon = "❄️"
    cols[idx].markdown(f"""
        <div style='
            background:#ffffff;
            padding:15px;
            border-radius:15px;
            text-align:center;
            box-shadow:0 4px 10px rgba(0,0,0,0.1);'>
            <h4>{row['day']}</h4>
            <h2>{icon} {temp:.1f}°C</h2>
            <p>💧 {row['humidity']:.0f}% Humidity</p>
            <p>🌧 {rain:.1f} mm Rain</p>
            <b>👗 Outfit: {get_outfit(temp, rain, user_type)}</b>
        </div>
    """, unsafe_allow_html=True)

# ----------------- ALERTS -----------------
st.markdown("### 🚨 Alerts")
if df['temperature'].max() > 35:
    st.warning("🔥 Heat Alert!")
if df['rainfall'].sum() > 20:
    st.info("🌧 Rain expected!")