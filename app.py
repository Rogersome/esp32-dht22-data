import streamlit as st
import pandas as pd
import requests
import io
from streamlit_autorefresh import st_autorefresh

GITHUB_RAW_URL = "https://raw.githubusercontent.com/Rogersome/esp32-dht22-data/main/data.csv"

st.set_page_config(page_title="ESP32 DHT22 Dashboard", layout="wide")

st.sidebar.title("⏱️ Auto Refresh")
refresh_seconds = st.sidebar.slider("Refresh every...", min_value=5, max_value=60, value=10, step=5)
st_autorefresh(interval=refresh_seconds * 1000, key="auto_refresh")

@st.cache_data(ttl=refresh_seconds)
def load_data():
    response = requests.get(GITHUB_RAW_URL)
    if response.status_code == 200:
        return pd.read_csv(io.StringIO(response.text))
    else:
        st.error("❌ Failed to load data from GitHub")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    df.columns = ["Time", "Temperature", "Humidity"]
    df["Time"] = pd.to_datetime(df["Time"])

    st.title("🌡️ ESP32 DHT22 Real-Time Dashboard")
    st.caption("Live data from GitHub (Auto refresh every {} sec)".format(refresh_seconds))

    st.line_chart(df.set_index("Time")[["Temperature", "Humidity"]])

    st.dataframe(df.tail(10), use_container_width=True)

else:
    st.warning("No data available.")
