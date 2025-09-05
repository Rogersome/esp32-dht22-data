import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh

# ---------- CONFIG ----------
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Rogersome/esp32-dht22-data/main/data.csv"
st.set_page_config(page_title="ESP32 DHT22 Dashboard", layout="wide")
st_autorefresh(interval=10_000, key="auto_refresh")  # Refresh every 10 seconds

# ---------- LOAD CSV FROM GITHUB ----------
@st.cache_data(ttl=10)
def load_data():
    response = requests.get(GITHUB_RAW_URL)
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = ["Time", "Temperature", "Humidity"]
        df["Time"] = pd.to_datetime(df["Time"])
        if df["Time"].dt.tz is None:
            df["Time"] = df["Time"].dt.tz_localize("UTC")
        return df
    else:
        st.error("❌ Failed to load data from GitHub.")
        return pd.DataFrame()

# ---------- DEVICE STATUS CHECK ----------
def get_device_status(df):
    if df.empty:
        return "❔ Unknown", "gray", "N/A", "N/A", "N/A"

    last_time = df["Time"].max()
    if last_time.tzinfo is None:
        last_time = last_time.tz_localize("Asia/Taipei") 
    last_time_utc = last_time.astimezone(timezone.utc)  

    now_utc = datetime.now(timezone.utc)
    diff = (now_utc - last_time_utc).total_seconds()

    if diff < 30:  # consider device online if data within last 30 sec
        return "🟢 Online", "green", last_time_utc.strftime("%Y-%m-%d %H:%M:%S"), now_utc.strftime("%Y-%m-%d %H:%M:%S"), diff
    else:
        return "🔴 Offline", "red", last_time_utc.strftime("%Y-%m-%d %H:%M:%S"), now_utc.strftime("%Y-%m-%d %H:%M:%S"), diff

# ---------- MAIN ----------
df = load_data()

if not df.empty:
    status_text, status_color, last_seen, curtime, time_diff = get_device_status(df)

    st.title("🌡️ ESP32 DHT22 Sensor Dashboard")
    st.markdown(f"#### **Status:** <span style='color:{status_color}'>{status_text}</span>", unsafe_allow_html=True)
    st.caption(f"📡 Last data received at: `{last_seen}` (UTC)")
    st.caption(f"current time: {curtime}")
    st.caption(f"time different: {time_diff}")
    st.caption("🔁 Auto-refresh every 10 seconds")

    # ---------- MODE TOGGLE ----------
    mode = st.radio("📊 Select Mode", ["Live Mode", "Historical Mode"], horizontal=True)

    if mode == "Historical Mode":
        with st.sidebar:
            st.header("📅 Filter Data")
            start = st.date_input("Start date", df["Time"].min().date())
            end = st.date_input("End date", df["Time"].max().date())
            df = df[(df["Time"].dt.date >= start) & (df["Time"].dt.date <= end)]
    else:
        df = df.tail(30)  # Only show last 30 rows for live view

    # ---------- CHART ----------
    st.subheader("📈 Temperature & Humidity Over Time (Interactive)")
    fig = px.line(df, x="Time", y=["Temperature", "Humidity"], markers=True,
              labels={"value": "Reading", "variable": "Sensor"},
              title="Temperature and Humidity")
    fig.update_traces(mode="lines+markers")
    fig.update_layout(legend_title_text="Sensor Type", height=450)
    st.plotly_chart(fig, use_container_width=True)


    # ---------- TABLE + DOWNLOAD ----------
    st.subheader("🔢 Data Table")
    st.dataframe(df.tail(30), use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "esp32_data.csv", "text/csv")
else:
    st.warning("No data to display.")




