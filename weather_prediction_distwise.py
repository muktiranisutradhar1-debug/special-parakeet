import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 🔑 API KEY
API_KEY = "f8c2a69b6af499e2ae8bbd110d092b13"

st.set_page_config(
    page_title="Bangladesh District Weather",
    page_icon="🌦️",
    layout="wide"
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
<h1 style='text-align: center; color: #4CAF50;'>🌦 Bangladesh District Weather Dashboard</h1>
""", unsafe_allow_html=True)

# ---------------- DISTRICTS ----------------
districts = {
    # Dhaka Division
    "Dhaka": {"lat": 23.8103, "lon": 90.4125},
    "Gazipur": {"lat": 23.9996, "lon": 90.4203},
    "Tangail": {"lat": 24.2500, "lon": 89.9167},
    "Narsingdi": {"lat": 23.9333, "lon": 90.7167},
    "Madaripur": {"lat": 23.1753, "lon": 90.2044},
    # Chittagong Division
    "Chittagong": {"lat": 22.3569, "lon": 91.7832},
    "Cox's Bazar": {"lat": 21.4272, "lon": 92.0058},
    "Comilla": {"lat": 23.4550, "lon": 91.1800},
    "Feni": {"lat": 23.0150, "lon": 91.4000},
    # Khulna Division
    "Khulna": {"lat": 22.8456, "lon": 89.5403},
    "Jessore": {"lat": 23.1700, "lon": 89.2030},
    "Satkhira": {"lat": 22.7167, "lon": 89.0833},
    "Bagerhat": {"lat": 22.6500, "lon": 89.7917},
    # Sylhet Division
    "Sylhet": {"lat": 24.8949, "lon": 91.8687},
    "Moulvibazar": {"lat": 24.4822, "lon": 91.7778},
    "Habiganj": {"lat": 24.3833, "lon": 91.4167},
    "Sunamganj": {"lat": 24.8833, "lon": 91.3833},
}

# ---------------- FETCH WEATHER ----------------
all_weather_list = []

with st.spinner("Fetching weather data..."):
    for district_name, coord in districts.items():
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={district_name},BD&appid={API_KEY}&units=metric"
        data = requests.get(url).json()

        if data.get("cod") == "200":
            for item in data['list']:
                all_weather_list.append({
                    "district": district_name,
                    "date": item['dt_txt'],
                    "temperature": item['main']['temp'],
                    "humidity": item['main']['humidity'],
                    "rainfall": item.get('rain', {}).get('3h', 0),
                    "lat": coord['lat'],
                    "lon": coord['lon']
                })

df = pd.DataFrame(all_weather_list)
df['date'] = pd.to_datetime(df['date'])

# ---------------- METRICS ----------------
st.markdown("### 📊 Overall Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("🌡 Max Temp", f"{df['temperature'].max():.1f} °C")
col2.metric("💧 Avg Humidity", f"{df['humidity'].mean():.1f} %")
col3.metric("🌧 Total Rain", f"{df['rainfall'].sum():.1f} mm")

# ---------------- CHARTS ----------------
st.markdown("### 📈 Temperature Trend")
fig1 = px.line(df, x="date", y="temperature", color="district")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("### 🌧 Rainfall Chart")
fig2 = px.bar(df, x="date", y="rainfall", color="district")
st.plotly_chart(fig2, use_container_width=True)

# ---------------- 5-DAY FORECAST CARDS ----------------
st.markdown("### 📅 5-Day Forecast per District")

df['day'] = df['date'].dt.date
daily_df = df.groupby(['district','day']).agg({
    'temperature': 'mean',
    'humidity': 'mean',
    'rainfall': 'sum'
}).reset_index()
daily_df = daily_df.groupby('district').head(5).reset_index(drop=True)

for district in districts.keys():
    st.markdown(f"#### {district}")
    district_df = daily_df[daily_df['district'] == district]
    cols = st.columns(len(district_df))
    for i, row in district_df.iterrows():
        icon = "☀️"
        if row['rainfall'] > 5:
            icon = "🌧️"
        elif row['humidity'] > 80:
            icon = "☁️"
        cols[i].markdown(f"""
            <div style='background:#ffffff;padding:15px;border-radius:15px;text-align:center;
            box-shadow:0 4px 10px rgba(0,0,0,0.1);'>
                <h4>{row['day']}</h4>
                <h2>{icon} {row['temperature']:.1f}°C</h2>
                <p>💧 {row['humidity']:.0f}%</p>
                <p>🌧 {row['rainfall']:.1f} mm</p>
            </div>
        """, unsafe_allow_html=True)

# ---------------- MAP ----------------
st.markdown("### 🗺 Districts Map")
fig_map = px.scatter_mapbox(
    df[['district','lat','lon']].drop_duplicates(),
    lat="lat",
    lon="lon",
    hover_name="district",
    zoom=6,
    height=600
)
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)

# ---------------- ALERTS ----------------
st.markdown("### 🚨 Alerts")
if df['temperature'].max() > 35:
    st.warning("🔥 Heat Alert!")
if df['rainfall'].sum() > 50:
    st.info("🌧 Heavy Rain expected!")