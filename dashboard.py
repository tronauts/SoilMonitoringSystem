import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Konfigurasi ThingSpeak
CHANNEL_ID = "2572257"
READ_API_KEY = "KHO554NBRCHPVLGB"
BASE_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}"

# Konfigurasi Streamlit
st.set_page_config(page_title="Soil Monitoring System", layout="wide", page_icon=":partly_sunny:")
st_autorefresh(interval=30000, limit=None, key="auto-refresh-handler")

# Custom CSS for Dark Mode Styling and Header Positioning
st.markdown("""
<style>
    .main { background-color: rgba(0,0,0,0); color: #E0E0E0; }
    header, .css-18e3th9, .css-1d391kg { background-color: #383838; color: white; }
    h1, h2, h3, h4, h5, h6 { color: white; }
    .stMetric { text-align: center; background-color: #383838; border-radius: 5px; color: #E0E0E0; }
    .title-header {
        background-color: plotly_dark; /* Latar belakang untuk judul */
        padding: 10px; /* Jarak dalam container */
        border-radius: 5px; /* Sudut membulat */
        text-align: center; /* Pusatkan teks */
    }
    /* CSS untuk memusatkan label di sidebar */
    .stSidebar .stMetric label {
        display: block;
        text-align: center;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper function untuk mengambil data dari ThingSpeak
def fetch_data(results):
    try:
        response = requests.get(BASE_URL, params={"results": results})
        response.raise_for_status()
        data = response.json()
        feeds = data.get("feeds", [])
        if feeds:
            df = pd.DataFrame(feeds)
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_convert("Asia/Jakarta")  # Convert ke WIB
            df["field1"] = pd.to_numeric(df["field1"], errors="coerce")  # Soil Moisture
            df["field2"] = pd.to_numeric(df["field2"], errors="coerce")  # Temperature
            df["field3"] = pd.to_numeric(df["field3"], errors="coerce")  # pH
            df["field4"] = pd.to_numeric(df["field4"], errors="coerce")  # Conductivity
            df["field5"] = pd.to_numeric(df["field5"], errors="coerce")  # Nitrogen
            df["field6"] = pd.to_numeric(df["field6"], errors="coerce")  # Phosphorus
            df["field7"] = pd.to_numeric(df["field7"], errors="coerce")  # Kalium
            
            # Resample data to 10-minute intervals and calculate the mean
            df.set_index("created_at", inplace=True)
            df_resampled = df.resample('10T').mean().reset_index()  # '10T' for 10 minutes
            
            return df_resampled
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Fungsi utama Streamlit
def main():
    # Input untuk jumlah hasil yang diambil
    results = st.sidebar.number_input("Jumlah Data yang ditampilkan:", min_value=1, max_value=100000, value=650)

    data = fetch_data(results)
    if data.empty:
        st.error("No data available!")
        return

    # Tampilkan dashboard
    st.markdown("<div class='title-header'><h1>Soil Monitoring System 🌱</h1></div>", unsafe_allow_html=True)
    st.button("Refresh")

    # Sidebar untuk Current Status
    st.sidebar.header("Current Status")
    st.sidebar.metric(label="Soil Moisture 🌱", value=f"{data['field1'].iloc[-1]:.2f} %")
    st.sidebar.metric(label="Temperature 🌡️", value=f"{data['field2'].iloc[-1]:.2f} °C")
    st.sidebar.metric(label="pH 🧪", value=f"{data['field3'].iloc[- 1]:.2f}")
    st.sidebar.metric(label="Conductivity ⚡", value=f"{data['field4'].iloc[-1]:.2f} µS/cm")
    st.sidebar.metric(label="Nitrogen 🆖", value=f"{data['field5'].iloc[-1]:.2f} mg/L")
    st.sidebar.metric(label="Phosphorus 🅿️", value=f"{data['field6'].iloc[-1]:.2f} mg/L")
    st.sidebar.metric(label="Kalium 🆑", value=f"{data['field7'].iloc[-1]:.2f} mg/L")

    # Menampilkan grafik
    charts_row1 = st.columns(2, gap="small")
    with charts_row1[0]:
        st.subheader("Soil Moisture")
        soil_chart = px.area(
            data,
            x="created_at",
            y="field1"
        )
        soil_chart.update_layout(
            xaxis_title="Time",
            yaxis_title="Soil Moisture (%)",
            template="plotly_dark"
        )
        soil_chart.update_yaxes(range=[60, 80])
        st.plotly_chart(soil_chart, use_container_width=True)

    with charts_row1[1]:
        st.subheader("Temperature")
        temp_chart = px.area(
            data,
            x="created_at",
            y="field2"
        )
        temp_chart.update_layout(
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            template="plotly_dark"
        )
        temp_chart.update_yaxes(range=[22, 26])
        st.plotly_chart(temp_chart, use_container_width=True)

    charts_row2 = st.columns(2, gap="small")
    with charts_row2[0]:
        st.subheader("Conductivity")
        conductivity_chart = px.area(
            data,
            x="created_at",
            y="field4"
        )
        conductivity_chart.update_layout(
            xaxis_title="Time",
            yaxis_title="Conductivity (µS/cm)",
            template="plotly_dark"
        )
        conductivity_chart.update_yaxes(range=[40, 65])
        st.plotly_chart(conductivity_chart, use_container_width=True)

    with charts_row2[1]:
        st.subheader("pH")
        ph_chart = px.area(
            data,
            x="created_at",
            y="field3"
        )
        ph_chart.update_layout(
            xaxis_title="Time",
            yaxis_title="pH Level",
            template="plotly_dark"
        )
        ph_chart.update_yaxes(range=[0, 16])
        st.plotly_chart(ph_chart, use_container_width=True)

    charts_row3 = st.columns(2, gap="small")
    with charts_row3[0]:
        st.subheader("Nitrogen")
        nitrogen_chart = px.line(
            data,
            x="created_at",
            y="field5"
        )
        nitrogen_chart.update_layout(
            xaxis_title="Time",
            yaxis_title="Nitrogen (mg/L)",
            template="plotly_dark"
        )
        st.plotly_chart(nitrogen_chart, use_container_width=True)

    with charts_row3[1]:
        st.subheader("Phosphorus")
        phosphorus_chart = px.area(
            data,
            x="created_at",
            y="field6"
        )
        phosphorus_chart.update_layout(
            xaxis_title="Time",
            yaxis_title="Phosphorus (mg/L)",
            template="plotly_dark"
        )
        phosphorus_chart.update_yaxes(range=[190, 400])
        st.plotly_chart(phosphorus_chart, use_container_width=True)

    charts_row4 = st.columns(2, gap="small")
    with charts_row4[0]:
        st.subheader("Kalium")
        kalium_chart = px.area(
            data,
            x="created_at",
            y="field7"
        )
        kalium_chart.update_layout(
            xaxis_title="Time",
            yaxis_title="Kalium (mg/L)",
            template="plotly_dark"
        )
        kalium_chart.update_yaxes(range=[190, 400])
        st.plotly_chart(kalium_chart, use_container_width=True)

# Jalankan aplikasi
if __name__ == "__main__":
    main()