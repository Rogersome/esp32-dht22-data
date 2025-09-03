import streamlit as st
import pandas as pd
import requests
import io
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# GitHub-hosted CSV
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Rogersome/esp32-dht22-data/main/data.csv"

st.set_page_config(page_title="ESP32 DHT22 Monitor", layout="wide")
st.title("🌡️ ESP32 DHT22 Monitor")
st.caption("Powered by ESP32 + GitHub + Streamlit")

# Page Selector
page = st.sidebar.radio("Select Mode", ["Live View", "Historical View"])

# Data Loader
@st.cache_data(ttl=5)
def load_data():
    response = requests.get(GITHUB_RAW_URL)
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = ["Time", "Temperature", "Humidity"]
        df["Time"] = pd.to_datetime(df["Time"])
        return df
    else:
        st.error("❌ Failed to load data from GitHub")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("No data available.")
    st.stop()

# 🔁 Live View Mode
if page == "Live View":
    st_autorefresh(interval=5000, key="auto_refresh")
    st.subheader("📡 Real-Time Sensor Data")

    # Optional date filter (still useful here)
    with st.sidebar:
        st.markdown("### 🔎 Filter (Optional)")
        start = st.date_input("Start", df["Time"].min().date())
        end = st.date_input("End", df["Time"].max().date())
        filtered = df[(df["Time"].dt.date >= start) & (df["Time"].dt.date <= end)]

    # Plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered["Time"], y=filtered["Temperature"], name="🌡️ Temp", line=dict(color="red")))
    fig.add_trace(go.Scatter(x=filtered["Time"], y=filtered["Humidity"], name="💧 Humidity", line=dict(color="blue")))
    fig.update_layout(title="Live Data (Auto-refreshes every 10s)", xaxis_title="Time", yaxis_title="Value")
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.subheader("📄 Latest Data")
    st.dataframe(filtered.tail(20), use_container_width=True)

    # Download
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "filtered_data.csv", "text/csv")

# 📜 Historical View Mode
elif page == "Historical View":
    st.subheader("📜 Historical Data Viewer")
    unique_dates = df["Time"].dt.date.unique()

    with st.sidebar:
        selected_day = st.selectbox("Pick a Date", sorted(unique_dates, reverse=True))

    day_data = df[df["Time"].dt.date == selected_day]

    if day_data.empty:
        st.info("No data for the selected date.")
    else:
        st.markdown(f"### 📆 Showing data from: `{selected_day}`")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=day_data["Time"], y=day_data["Temperature"], name="🌡️ Temp", line=dict(color="red")))
        fig.add_trace(go.Scatter(x=day_data["Time"], y=day_data["Humidity"], name="💧 Humidity", line=dict(color="blue")))
        fig.update_layout(title="Temperature & Humidity", xaxis_title="Time", yaxis_title="Value")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(day_data.tail(20), use_container_width=True)

