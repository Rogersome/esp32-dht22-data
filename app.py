import streamlit as st
import pandas as pd
import io
import requests
import plotly.express as px
from datetime import datetime, timezone
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

# ---- DEVICE STATUS CHECK ----
def get_device_status(df):
    if df.empty:
        return "Unknown ❔", "gray"

    last_time = df["Time"].max()
    
    # Make sure the datetime is timezone-aware
    if last_time.tzinfo is None:
        last_time = last_time.tz_localize("UTC")

    now_utc = datetime.now(timezone.utc)
    diff = (now_utc - last_time).total_seconds()

    if diff < 30:  # ESP32 uploads every 10s, give buffer
        return "🟢 Device Online", "green"
    else:
        return "🔴 Device Offline", "red"

# ---- SIDEBAR ----
st.sidebar.markdown("### GitHub Sync Status")
if is_online:
    st.sidebar.success("🟢 Connected to GitHub")
else:
    st.sidebar.error("🔴 GitHub Not Reachable")

# ---- MAIN ----
if not df.empty:
    status_text, status_color = get_device_status(df)
    st.title("🌡️ ESP32 DHT22 Sensor Dashboard")
    st.markdown(f"#### **Status:** <span style='color:{status_color}'>{status_text}</span>", unsafe_allow_html=True)
    st.caption("Real-time IoT monitoring | Auto-refresh every 10s")
    st.markdown(f"**Last Data Received:** `{last_time}`")

    # ---- MODE SWITCH ----
    mode = st.radio("Mode", ["Live Update", "Historical Mode"], horizontal=True)

    if mode == "Live Update":
        st.subheader("📊 Temperature & Humidity")

        fig = px.line(df, x="Time", y=["Temperature", "Humidity"],
                      labels={"value": "Reading", "variable": "Sensor"},
                      title="Temperature & Humidity Over Time")

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📄 Latest Records")
        st.dataframe(df.tail(20), use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Full CSV", csv, "data.csv", "text/csv")

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


