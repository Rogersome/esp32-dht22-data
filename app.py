import streamlit as st
import pandas as pd
import io
import requests
import plotly.express as px

# --- CONFIG ---
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Rogersome/esp32-dht22-data/main/data.csv"
st.set_page_config(page_title="ESP32 DHT22 Visualizer", layout="centered")

# --- DATA LOADER ---
@st.cache_data(ttl=60)
def load_data():
    r = requests.get(GITHUB_RAW_URL)
    if r.status_code == 200:
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["Time", "Temperature", "Humidity"]
        df["Time"] = pd.to_datetime(df["Time"])
        return df
    else:
        return pd.DataFrame()

df = load_data()

# --- SELECT & DISPLAY ---
st.title("🔍 Explore Individual Sensor Reading")

if not df.empty:
    # Allow selecting one row by timestamp
    time_options = df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
    selected_time = st.selectbox("Select a timestamp", time_options[::-1])  # newest first

    selected_row = df[df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S") == selected_time]

    st.write("### 📋 Selected Record")
    st.dataframe(selected_row, use_container_width=True)

    st.write("### 📈 Point Highlight")
    fig = px.line(df.tail(100), x="Time", y=["Temperature", "Humidity"], markers=True)
    fig.add_scatter(x=selected_row["Time"], y=selected_row["Temperature"], mode='markers+text',
                    name="Selected Temp", text=["🌡️"], textposition="top center")
    fig.add_scatter(x=selected_row["Time"], y=selected_row["Humidity"], mode='markers+text',
                    name="Selected Humid", text=["💧"], textposition="bottom center")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No data available.")
