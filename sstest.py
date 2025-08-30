import streamlit as st
import pandas as pd
import requests
import io
import altair as alt
from streamlit_autorefresh import st_autorefresh

# ---- CONFIG ----
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Rogersome/esp32-dht22-data/main/data.csv"
st.set_page_config(page_title="ESP32 DHT22 Live Dashboard", layout="wide")

# ---- AUTO REFRESH every 10 seconds ----
st_autorefresh(interval=10_000, key="data_refresh")

# ---- LOAD DATA FUNCTION ----
@st.cache_data(ttl=5)
def load_data():
    response = requests.get(GITHUB_RAW_URL)
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = ["Time", "Temperature", "Humidity"]
        df["Time"] = pd.to_datetime(df["Time"])
        return df
    else:
        return pd.DataFrame()

# ---- PAGE TITLE ----
st.title("🌡️ ESP32 DHT22 Live Monitor")
st.caption("📡 Real-time data from GitHub | Auto-refreshes every 10 seconds")

# ---- LOAD DATA ----
df = load_data()

if df.empty:
    st.warning("⚠️ Failed to load data.")
    st.stop()

# ---- LATEST METRICS ----
latest = df.iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("🌡️ Temperature", f"{latest['Temperature']:.1f} °C")
col2.metric("💧 Humidity", f"{latest['Humidity']:.1f} %")
col3.write(f"🕒 Last Updated: {latest['Time'].strftime('%Y-%m-%d %H:%M:%S')}")

# ---- LINE CHART (Temperature & Humidity) ----
df_long = pd.melt(df, id_vars=["Time"], value_vars=["Temperature", "Humidity"],
                  var_name="Type", value_name="Value")

chart = alt.Chart(df_long).mark_line().encode(
    x=alt.X("Time:T", title="Time"),
    y=alt.Y("Value:Q", title="Value"),
    color="Type:N"
).properties(height=400)

st.altair_chart(chart, use_container_width=True)

# ---- TABLE & DOWNLOAD ----
st.subheader("🔢 Latest Data Table")
st.dataframe(df.tail(20), use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download CSV", csv, "data.csv", "text/csv")
