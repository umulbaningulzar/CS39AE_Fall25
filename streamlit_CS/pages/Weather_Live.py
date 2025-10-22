# 5_Weather_Live.py
import time
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="🌦️ Live Weather (Open-Meteo)", page_icon="🌦️", layout="wide")
st.title("🌦️ Live Weather (Open-Meteo)")
st.caption("Caches current weather, appends to a short in-memory time series, and plots temperature over time.")

# Prevent chart blink on rerun
st.markdown("""
<style>
  [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer { transition: none !important; opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)

# --- Config (Denver)
lat, lon = 39.7392, -104.9903
wurl = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}

# --- Cached fetch of *current* reading
@st.cache_data(ttl=600, show_spinner=False)
def get_weather():
    try:
        r = requests.get(wurl, timeout=10, headers=HEADERS)
        r.raise_for_status()
        j = r.json()["current"]
        # use the API-provided timestamp (UTC)
        row = {
            "time": pd.to_datetime(j["time"]),
            "temperature": float(j["temperature_2m"]),
            "wind": float(j["wind_speed_10m"])
        }
        return pd.DataFrame([row]), None
    except requests.RequestException as e:
        return None, f"Network/HTTP error: {e}"

# --- Auto Refresh Controls
st.subheader("🔁 Auto Refresh Settings")
refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)
auto_refresh = st.toggle("Enable auto-refresh", value=False)
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

# --- Session history for weather
if "wx_hist" not in st.session_state:
    st.session_state.wx_hist = pd.DataFrame(columns=["time", "temperature", "wind"])

df, err = get_weather()
if err:
    st.error(err)
    st.stop()

# Append the latest reading, dedupe by time
st.session_state.wx_hist = pd.concat([st.session_state.wx_hist, df], ignore_index=True)
st.session_state.wx_hist.drop_duplicates(subset=["time"], keep="last", inplace=True)

# Keep only last ~50 readings so the chart stays tidy
st.session_state.wx_hist = st.session_state.wx_hist.sort_values("time").tail(50)

# --- Metrics (current, with delta vs previous)
st.subheader("Current Conditions (Denver)")
c1, c2 = st.columns(2)

cur_temp = df["temperature"].iloc[0]
prev_temp_series = st.session_state.wx_hist["temperature"].iloc[:-1].tail(1)
temp_delta = None if prev_temp_series.empty else cur_temp - float(prev_temp_series.values[0])
c1.metric("Temperature (°C)", f"{cur_temp:.1f} °C", None if temp_delta is None else f"{temp_delta:+.1f}")

cur_wind = df["wind"].iloc[0]
prev_wind_series = st.session_state.wx_hist["wind"].iloc[:-1].tail(1)
wind_delta = None if prev_wind_series.empty else cur_wind - float(prev_wind_series.values[0])
c2.metric("Wind (m/s)", f"{cur_wind:.1f}", None if wind_delta is None else f"{wind_delta:+.1f}")

# --- Line chart (temperature over time)  ← not a bar chart
st.subheader("Temperature Over Time (recent)")
fig = px.line(
    st.session_state.wx_hist,
    x="time", y="temperature",
    markers=True,
    labels={"time": "Time (UTC)", "temperature": "°C"},
    title="Open-Meteo current temperature (rolling session history)"
)
st.plotly_chart(fig, use_container_width=True)

# Optional: show wind as a second line in a separate chart
with st.expander("Show wind over time"):
    wind_fig = px.line(
        st.session_state.wx_hist, x="time", y="wind", markers=True,
        labels={"time": "Time (UTC)", "wind": "m/s"},
        title="Wind speed (m/s)"
    )
    st.plotly_chart(wind_fig, use_container_width=True)

# Auto-refresh loop
if auto_refresh:
    time.sleep(refresh_sec)
    get_weather.clear()   # allow a fresh API call even within session
    st.rerun()
