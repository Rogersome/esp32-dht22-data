
# 🌡️ ESP32 DHT22 Sensor Logger & Streamlit Dashboard

This project is an end-to-end IoT solution using **ESP32**, **DHT22**, **GitHub**, and **Streamlit**.  
It collects real-time temperature and humidity data from a DHT22 sensor, logs it into a CSV file in this repository, and displays it live through an interactive Streamlit web app.

🔗 **Live Dashboard:**  
[📊 https://esp32-dht22-data-j2zpeed9xdter8jgaayjox.streamlit.app/](https://esp32-dht22-data-j2zpeed9xdter8jgaayjox.streamlit.app/)

---

## 🛠️ Features

- 🔁 **Real-time updates** (every 10 seconds)
- 🌡️📈 Dual-axis chart for **Temperature** and **Humidity**
- 📅 **Date filter sidebar**
- 🧠 **Historical Mode**:
  - Click on past records from the list to visualize them
  - Switch back to live updates anytime
- 💾 **Download filtered data as CSV**
- ☁️ **Serverless & cloud-based**:
  - ESP32 sends data directly to GitHub via REST API
  - Streamlit pulls from GitHub and updates the charts

---

## 🔧 Hardware Setup

| Component | Description |
|----------|-------------|
| ESP32    | Microcontroller with WiFi |
| DHT22    | Digital Temp & Humidity Sensor |
| Others   | Jumper wires, USB cable, breadboard, 10k resistor |

---

## 📂 Repository Contents

```
esp32-dht22-data/
├── app.py               # Main Streamlit application
├── data.csv             # CSV file updated by the ESP32
├── requirements.txt     # Python dependencies
└── README.md            # This documentation file
```

---

## 🚀 How It Works

### ESP32 Firmware
- Reads DHT22 values every 10 seconds.
- Gets real-time clock using NTP.
- Sends HTTP PUT request to GitHub API to append new row to `data.csv`.

### Streamlit App (`app.py`)
- Pulls `data.csv` from GitHub every 10 seconds.
- Displays:
  - A **dual line chart** of temperature and humidity.
  - A **filtered table** of latest 20 records.
  - A **download button** for exporting filtered data.
- Allows **switching to historical mode**, where:
  - You can click a record to display only that point on the chart.
  - Return to live data view anytime.

---

## 🧪 Python Dependencies

Make sure to install the following packages (already listed in `requirements.txt`):

```txt
streamlit
pandas
requests
matplotlib
```

To run locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📈 Screenshots

**Live Updating Mode:**

![Live Chart](https://github.com/Rogersome/esp32-dht22-data/blob/main/assets/live-chart-preview.png)

**Historical View Mode:**

![Historical View](https://github.com/Rogersome/esp32-dht22-data/blob/main/assets/historical-mode-preview.png)

---

## 🔐 Security Note

If you're pushing to GitHub via ESP32:
- Never expose your personal **GitHub access token** publicly.
- Ideally, store it in a secrets file or use environment variables.
- Use a separate GitHub account or token with minimal repo permissions.

---

## 📌 To-Do / Roadmap

- [ ] Auto-backup old data to `history/YYYYMMDD.csv`
- [ ] Add temperature/humidity alerts
- [ ] Add min/max/avg summaries
- [ ] Add mobile-optimized UI for Streamlit

---

## 👨‍💻 Author

Made with ❤️ by [Rogersome](https://github.com/Rogersome)

MIT License © 2025
