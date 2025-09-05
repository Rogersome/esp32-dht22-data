import streamlit as st
import pandas as pd
import io
import requests
from datetime import datetime, timezone
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# CONFIG
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Rogersome/esp32-dht22-data/main/data.csv"
st.set_page_config(page_title="ESP32 DHT22 Dashboard", layout="wide")

# REFRESH every 10 seconds
st_autorefresh(interval=10_000, key="auto_refresh")

# Load CSV from GitHub
@st.cache_data(ttl=5)
def load_data():
    response = requests.get(GITHUB_RAW_URL)
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = ["Time", "Temperature", "Humidity"]
        df["Time"] = pd.to_datetime(df["Time"], utc=True, errors='coerce')
        return df
    else:
        return pd.DataFrame()

df = load_data()

# Determine status
def get_device_status(df):
    if df.empty or df["Time"].isnull().all():
        return "❔ Unknown", "gray", "Unknown"

    last_time = df["Time"].max()
    now_utc = datetime.now(timezone.utc)

    try:
        diff = (now_utc - last_time).total_seconds()
        if diff < 30:
            return "🟢 Online", "green", last_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return "🔴 Offline", "red", last_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return "❔ Unknown", "gray", "Invalid timestamp"

# UI
if not df.empty:
    st.title("🌡️ ESP32 DHT22 Sensor Dashboard")

    # Status
    status_text, status_color, last_seen = get_device_status(df)
    st.markdown(f"### **Status:** <span style='color:{status_color}'>{status_text}</span>", unsafe_allow_html=True)
    st.caption(f"🕒 Last data received at: `{last_seen}` (UTC)")

    # Historical mode toggle
    historical_mode = st.toggle("📁 Historical Mode", value=False)

    if not historical_mode:
        # Live data
        recent_df = df[df["Time"] > (df["Time"].max() - pd.Timedelta(minutes=5))]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=recent_df["Time"], y=recent_df["Temperature"],
                                 mode='lines+markers', name='Temperature (°C)', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=recent_df["Time"], y=recent_df["Humidity"],
                                 mode='lines+markers', name='Humidity (%)', line=dict(color='blue')))
        fig.update_layout(title="📊 Real-Time Sensor Readings", xaxis_title="Time (UTC)",
                          yaxis_title="Value", legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(recent_df.tail(10), use_container_width=True)
    else:
        st.subheader("📁 Full Historical Data")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Full CSV", csv, "data.csv", "text/csv")

else:
    st.warning("No data found or failed to fetch.")
