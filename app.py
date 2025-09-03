import streamlit as st
import pandas as pd
import requests
import io
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 🌐 GitHub CSV URL
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Rogersome/esp32-dht22-data/main/data.csv"

# 🔁 Auto-refresh every 10 seconds
st_autorefresh(interval=10_000, key="auto_refresh")

st.set_page_config(page_title="ESP32 DHT22 Monitor", layout="wide")
st.title("🌡️ ESP32 DHT22 Live Monitor")
st.caption("Live data from GitHub CSV (updates every 10 seconds)")

# 📥 Load Data
@st.cache_data(ttl=5)
def load_data():
    response = requests.get(GITHUB_RAW_URL)
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = ["Time", "Temperature", "Humidity"]
        df["Time"] = pd.to_datetime(df["Time"])
        return df
    else:
        st.error("❌ Failed to fetch data from GitHub")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data available.")
    st.stop()

# 📅 Date Filter
with st.sidebar:
    st.header("📅 Filter")
    start = st.date_input("Start", df["Time"].min().date())
    end = st.date_input("End", df["Time"].max().date())
    filtered = df[(df["Time"].dt.date >= start) & (df["Time"].dt.date <= end)]

# 📈 Plotly Chart (Temp + Humid)
fig = go.Figure()
fig.add_trace(go.Scatter(x=filtered["Time"], y=filtered["Temperature"], name="🌡️ Temperature (°C)", line=dict(color="red")))
fig.add_trace(go.Scatter(x=filtered["Time"], y=filtered["Humidity"], name="💧 Humidity (%)", line=dict(color="blue")))
fig.update_layout(title="Live Temperature and Humidity", xaxis_title="Time", yaxis_title="Value")

st.plotly_chart(fig, use_container_width=True)

# 📊 Table & Download
st.subheader("📄 Data Preview")
st.dataframe(filtered.tail(20), use_container_width=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download CSV", csv, "filtered_data.csv", "text/csv")
