import streamlit as st
import pandas as pd
import io
import requests
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# ---- CONFIG ----
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Rogersome/esp32-dht22-data/main/data.csv"
st.set_page_config(page_title="ESP32 DHT22 Monitor", layout="wide")

# ---- AUTO REFRESH EVERY 10 SECONDS ----
st_autorefresh(interval=10_000, key="auto_refresh")

# ---- LOAD DATA ----
@st.cache_data(ttl=5)
def load_data():
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=5)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            df.columns = ["Time", "Temperature", "Humidity"]
            df["Time"] = pd.to_datetime(df["Time"])
            return df, True
        else:
            return pd.DataFrame(), False
    except:
        return pd.DataFrame(), False

df, is_online = load_data()

# ---- OFFLINE INDICATOR ----
st.sidebar.markdown("### Connection Status")
if is_online:
    st.sidebar.success("🟢 Online - Data fetched from GitHub")
else:
    st.sidebar.error("🔴 Offline - Unable to fetch data")

# ---- HISTORICAL MODE ----
mode = st.sidebar.radio("Mode", ["Live Update", "Historical Mode"])

if not df.empty:
    st.title("🌡️ ESP32 DHT22 Sensor Dashboard")
    st.caption("Live sensor feed via GitHub | Auto-refresh every 10s")

    if mode == "Live Update":
        st.subheader("📊 Real-Time Temperature & Humidity")

        fig = px.line(df, x="Time", y=["Temperature", "Humidity"],
                      labels={"value": "Reading", "variable": "Sensor"},
                      title="Temperature & Humidity Over Time")

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📄 Latest 20 Records")
        st.dataframe(df.tail(20), use_container_width=True)

        # ---- DOWNLOAD ----
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "latest_data.csv", "text/csv")

    else:
        st.subheader("📁 Historical Mode")
        df["Date"] = df["Time"].dt.date
        selected_date = st.selectbox("Select Date", sorted(df["Date"].unique(), reverse=True))

        df_selected = df[df["Date"] == selected_date]

        st.markdown(f"### Data for **{selected_date}**")

        fig2 = px.line(df_selected, x="Time", y=["Temperature", "Humidity"],
                       labels={"value": "Reading", "variable": "Sensor"},
                       title=f"Temperature & Humidity on {selected_date}")

        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(df_selected, use_container_width=True)

        csv_hist = df_selected.to_csv(index=False).encode("utf-8")
        st.download_button(f"⬇️ Download {selected_date}.csv", csv_hist, f"data_{selected_date}.csv", "text/csv")

else:
    st.warning("⚠️ No data available to display.")
