import streamlit as st
import pandas as pd
import json
from google.cloud import firestore
from google.oauth2 import service_account
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib as mpl
import plotly.express as px

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Crowd Monitoring FT UI",
    page_icon=":bus:",
    layout="wide"
    
)

st.title(
    'Crowd Monitoring dan Kedatangan Bikun di Halte FT UI')



# Fungsi untuk mendapatkan semua data Firestore

def get_all_firestore_data():
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="deteksiorangdanbikun")
    docs_snapshot = db.collection("data").stream()
    
    all_data = []

    for doc in docs_snapshot:
        data = doc.to_dict()

        if 'timestamp' in data:
            timestamp_firestore = data['timestamp']
            timestamp_str = timestamp_firestore.strftime('%Y-%m-%d %H:%M:%S')
            data['timestamp'] = [timestamp_str]

            all_data.append(data)

    return all_data

# Fungsi untuk menampilkan grafik jumlah orang di halte
def show_people_graph(all_data):
    timestamps = []
    jumlah_orang = []

    # Sort data berdasarkan timestamp
    all_data_sorted = sorted(all_data, key=lambda x: x["timestamp"][0])
    last_30_data = all_data_sorted[-30:]

    for data in last_30_data:
        if "timestamp" in data and "Orang" in data:
            timestamp_str = data["timestamp"][0]
            timestamp_obj = pd.to_datetime(timestamp_str) + pd.Timedelta(hours=7)
            waktu = timestamp_obj.strftime('%H:%M')
            timestamps.append(waktu)
            jumlah_orang.append(data["Orang"])

    fig = px.line(x=timestamps, y=jumlah_orang, labels={'x': 'Waktu', 'y': 'Jumlah Orang'})
    fig.update_layout(title='Grafik Jumlah Orang di Halte')

    # Ganti st.pyplot(fig) dengan st.plotly_chart(fig)
    st.plotly_chart(fig)

# Fungsi untuk menampilkan jumlah orang dan skala parameter
def show_latest_people_count_and_scale(all_data):
    latest_data = max(all_data, key=lambda x: x.get('timestamp', ''))

    if "Orang" in latest_data:
        jumlah_orang = latest_data["Orang"]

        st.write(f"Jumlah Orang di Halte: {jumlah_orang if jumlah_orang else 0}")

        if jumlah_orang and jumlah_orang <= 3:
            skala = "Sangat Sepi"
        elif jumlah_orang and 3 < jumlah_orang <= 6:
            skala = "Sepi"
        elif jumlah_orang and 6 < jumlah_orang <= 10:
            skala = "Normal"
        elif jumlah_orang and 10 < jumlah_orang <= 15:
            skala = "Ramai"
        elif jumlah_orang:
            skala = "Sangat Ramai"
        else:
            skala = "Tidak Ada Orang"
        
        st.write(f"Skala Parameter: {skala}")

# Fungsi untuk menampilkan status kedatangan Bis Kuning
def show_bikun_status(all_data):
    latest_data = max(all_data, key=lambda x: x.get('timestamp', ''))

    if "Bikun" in latest_data:
        bikun_status = latest_data["Bikun"]
        if bikun_status:
            st.write("Bis Kuning ada di halte.")
            st.image("bikun.jpg", caption="Bis Kuning di halte", width=400)
        else:
            st.write("Bis Kuning tidak ada di halte.")


# Fungsi untuk menampilkan grafik status kehadiran bikun
def show_bikun_presence_graph(all_data):
    timestamps = []
    bikun_status = []

    all_data_sorted = sorted(all_data, key=lambda x: x["timestamp"][0])

    last_30_data = all_data_sorted[-30:]

    for data in last_30_data:
        if "timestamp" in data and "Bikun" in data:
            timestamp_str = data["timestamp"][0]
            timestamp_obj = pd.to_datetime(timestamp_str) + pd.Timedelta(hours=7)
            waktu = timestamp_obj.strftime('%H:%M')
            timestamps.append(waktu)
            bikun_status.append(1 if data["Bikun"] else 0.5)

    fig = px.bar(x=timestamps, y=bikun_status, color=bikun_status, labels={'x': 'Waktu', 'y': 'Status Kehadiran Bikun'},
                 color_discrete_map={0: 'red', 1: 'green'})
    fig.update_layout(title='Grafik Status Kehadiran Bikun')
    fig.update_yaxes(ticks="inside", tickvals=[0, 0.5, 1], ticktext=['', 'Tidak Ada', 'Ada'])

    
    st.plotly_chart(fig)



all_data_firestore = get_all_firestore_data()



if all_data_firestore:
    st.text("")  
    

    # Sidebar
    st.sidebar.header('Navigation')
    selected_page = st.sidebar.radio('Go to', ['Home', 'Grafik Keramaian', 'Grafik Status Bikun', 'Jumlah & Status Orang'])

    if selected_page == 'Home':

        # Menambahkan tombol untuk memuat ulang data
        if st.button("Perbarui Data"):
            all_data_firestore = get_all_firestore_data()
            
        # Menampilkan grafik jumlah orang di halte
        st.header('Grafik Jumlah Orang di Halte')
        previous_chart = st.empty()
        show_people_graph(all_data_firestore)
        previous_chart.text("") 

        # Menampilkan jumlah orang dan skala parameter
        st.header('Informasi Jumlah Orang dan Skala Parameter')
        previous_info = st.empty()
        show_latest_people_count_and_scale(all_data_firestore)
        previous_info.text("") 

        # Menampilkan status kedatangan Bis Kuning
        st.header('Status Kedatangan Bis Kuning')
        previous_status = st.empty()
        show_bikun_status(all_data_firestore)
        previous_status.text("") 

        # Menampilkan grafik status kehadiran Bis Kuning
        st.header('Grafik Status Kehadiran Bis Kuning')
        previous_bikun_graph = st.empty()
        show_bikun_presence_graph(all_data_firestore)
        previous_bikun_graph.text("")

    elif selected_page == 'Grafik Keramaian':
        # Menampilkan grafik jumlah orang di halte
        st.header('Grafik Jumlah Orang di Halte')
        previous_chart = st.empty()
        show_people_graph(all_data_firestore)
        previous_chart.text("") 


    elif selected_page == 'Grafik Status Bikun':
        # Menampilkan grafik status kehadiran Bis Kuning
        st.header('Grafik Status Kehadiran Bis Kuning')
        previous_bikun_graph = st.empty()
        show_bikun_presence_graph(all_data_firestore)
        previous_bikun_graph.text("")

        # Menampilkan status kedatangan Bis Kuning
        st.header('Status Kedatangan Bis Kuning')
        previous_status = st.empty()
        show_bikun_status(all_data_firestore)
        previous_status.text("") 

    elif selected_page == 'Jumlah & Status Orang':
        # Menampilkan jumlah orang dan skala parameter
        st.header('Informasi Jumlah Orang dan Skala Parameter')
        show_latest_people_count_and_scale(all_data_firestore)

   

    st.text("")  
    # Footer
    st.markdown(
        """
        <div style="background-color: #343a40; padding: 10px; text-align: center; color: white">
            <p>© 2023 Project Monitoring Crowd Control Halte FTUI</p>
            <p>Group 1.5</p>
        </div>
        """,
        unsafe_allow_html=True
    )
