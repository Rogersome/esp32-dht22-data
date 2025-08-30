import streamlit as st
import pandas as pd
import requests
import io
import time
import matplotlib.pyplot as plt

# ---- CONFIG ----
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Rogersome/esp32-dht22-data/main/data.csv"
REFRESH_INTERVAL = 10  # in seconds

st.set_page_config(page_title="ESP32 DHT22 Live Dashboard", layout="wide")
st.title("🌡️ ESP32 DHT22 Real-Time Dashboard")
st.caption("Data updates every 10 seconds from GitHub")

# ---- LOAD DATA FUNCTION ----
def load_data():
    response = requests.get(GITHUB_RAW_URL)
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = ["Time", "Temperature", "Humidity"]
        df["Time"] = pd.to_datetime(df["Time"])
        return df
    else:
        st.error("Failed to load data from GitHub")
        return pd.DataFrame()

# ---- REAL-TIME LOOP ----
placeholder = st.empty()

while True:
    with placeholder.container():
        df = load_data()

        if not df.empty:
            st.subheader("📊 Real-Time Temperature & Humidity")

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(df["Time"], df["Temperature"], label="Temperature (°C)", color='red')
            ax.plot(df["Time"], df["Humidity"], label="Humidity (%)", color='blue')
            ax.set_xlabel("Time")
            ax.set_ylabel("Value")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

            st.subheader("🔢 Latest Data")
            st.dataframe(df.tail(10), use_container_width=True)

            st.caption(f"🔄 Auto-refreshing every {REFRESH_INTERVAL} seconds")
        else:
            st.warning("No data found.")

    time.sleep(REFRESH_INTERVAL)
    st.rerun()

