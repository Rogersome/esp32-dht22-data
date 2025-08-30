import streamlit as st
import pandas as pd
import requests
import io
import time
import altair as alt

# ---- CONFIG ----
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Rogersome/esp32-dht22-data/main/data.csv"
st.set_page_config(page_title="ESP32 Live DHT22 Monitor", layout="wide")

# ---- LOAD FUNCTION ----
def load_data():
    response = requests.get(GITHUB_RAW_URL)
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = ["Time", "Temperature", "Humidity"]
        df["Time"] = pd.to_datetime(df["Time"])
        return df
    else:
        return pd.DataFrame()

# ---- TITLE ----
st.title("🌡️ ESP32 DHT22 Real-Time Monitor")
st.caption("📡 即時資料由 GitHub 提供，每 10 秒自動更新")

# ---- PLACEHOLDERS ----
chart_placeholder = st.empty()
table_placeholder = st.empty()
metric_placeholder = st.empty()

# ---- REAL-TIME LOOP ----
while True:
    df = load_data()

    if not df.empty:
        latest = df.iloc[-1]
        metrics = {
            "🌡️ 溫度": f"{latest['Temperature']:.1f} °C",
            "💧 濕度": f"{latest['Humidity']:.1f} %",
            "🕒 時間": latest["Time"].strftime("%Y-%m-%d %H:%M:%S"),
        }

        with metric_placeholder.container():
            st.metric("🌡️ 溫度", metrics["🌡️ 溫度"])
            st.metric("💧 濕度", metrics["💧 濕度"])
            st.write(f"🕒 最後更新時間: {metrics['🕒 時間']}")

        df_long = pd.melt(df, id_vars=["Time"], value_vars=["Temperature", "Humidity"], var_name="Type", value_name="Value")

        chart = alt.Chart(df_long).mark_line().encode(
            x=alt.X("Time:T", title="即時時間"),
            y=alt.Y("Value:Q", title="數值"),
            color="Type:N"
        ).properties(height=400)

        chart_placeholder.altair_chart(chart, use_container_width=True)
        table_placeholder.dataframe(df.tail(20), use_container_width=True)
    else:
        st.warning("⚠️ 無法載入資料")

    time.sleep(10)  # 🔁 Refresh every 10 seconds
