import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv
import plotly.express as px

# Load API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("dummy_feedback.csv")
    df.columns = df.columns.str.strip()  # Bersihkan nama kolom
    return df

df = load_data()

# Judul
st.title("📊 Pelindo AI – Analisis Kinerja Pekerja Berbasis GPT-4o")

# Pilih NIPP
nipp_list = df["NIPP_Pekerja"].unique()
selected_nipp = st.selectbox("Pilih NIPP Pekerja:", nipp_list)

# Ambil baris data pekerja
row = df[df["NIPP_Pekerja"] == selected_nipp].iloc[0]
nama_posisi = row["Nama_Posisi"]

# Helper untuk ambil nilai kolom
def get_value(col_name):
    matches = [col for col in df.columns if col_name.lower() in col.lower()]
    if matches:
        return str(row[matches[0]])
    return "0"

# Komputasi Skor Tiap Aspek
def compute_scores():
    try:
        delivery_score = (
            int(get_value("Pekerjaan yang diberikan selesai")) * 0.4 +
            int(get_value("Pekerjaan diselesaikan tepat waktu")) * 0.3 +
            int(get_value("Kualitas Pekerjaan")) * 0.3
        ) / 100

        leadership_score = sum([
            int(get_value("Membimbing rekan tim").replace('x', '').replace('≥','').split()[0]),
            int(get_value("Membangun semangat tim").replace('x', '').replace('≥','').split()[0]),
            int(get_value("Mengambil peran aktif").replace('x', '').replace('≥','').split()[0])
        ])

        comm_score = (
            5 if get_value("Memotong pembicaraan") == "0" else 2
        ) + (
            5 if "2" in get_value("Waktu respon komunikasi penting") else 3
        ) + (
            int(get_value("Memberikan masukan").replace('x', '').replace('≥','').split()[0])
        )

        team_score = sum([
            int(get_value("Membagikan informasi").replace('x', '').replace('≥','').split()[0]),
            int(get_value("Menawarkan bantuan").replace('x', '').replace('≥','').split()[0]),
            int(get_value("Proaktif menawarkan bantuan").replace('x', '').replace('≥','').split()[0]),
            6 if "≥" in get_value("Berpartisipasi aktif") else 3
        ])

        return pd.DataFrame({
            "Aspek": ["Delivery", "Leadership", "Communication", "Teamwork"],
            "Skor": [delivery_score, leadership_score, comm_score, team_score]
        })

    except Exception as e:
        st.error(f"Gagal menghitung skor: {e}")
        return pd.DataFrame(columns=["Aspek", "Skor"])

# Tampilkan Skor
score_df = compute_scores()
st.subheader("📋 Ringkasan Skor Per Aspek")
st.dataframe(score_df)

# Chart
st.subheader("📈 Visualisasi Skor Kinerja")
fig = px.bar(score_df, x="Aspek", y="Skor", color="Aspek", text_auto=True, title="Skor Kinerja Berdasarkan Aspek")
st.plotly_chart(fig)

# Prompt ke GPT
prompt = f"""
Anda adalah Pelindo AI, asisten analisis kinerja profesional.

Tulislah narasi penilaian menyeluruh berdasarkan hasil formulir feedback berikut:

Posisi: {nama_posisi}

DELIVERY:
1. Penyelesaian tugas: {get_value('Pekerjaan yang diberikan selesai')}%
2. Ketepatan waktu: {get_value('Pekerjaan diselesaikan tepat waktu')}%
3. Kualitas pekerjaan (jumlah koreksi): {get_value('Kualitas Pekerjaan')}

LEADERSHIP:
- Membimbing rekan tim: {get_value('Membimbing rekan tim')}
- Menunjukkan sikap kerja positif: {get_value('Menunjukkan sikap kerja positif')}
- Membangun semangat tim: {get_value('Membangun semangat tim')}
- Mengambil peran aktif menyelesaikan tantangan: {get_value('Mengambil peran aktif')}

COMMUNICATION:
- Memotong pembicaraan: {get_value('Memotong pembicaraan')}
- Waktu respon komunikasi penting: {get_value('Waktu respon komunikasi penting')}
- Memberikan masukan/ide: {get_value('Memberikan masukan')}

TEAMWORK:
- Membagikan informasi: {get_value('Membagikan informasi')}
- Menawarkan bantuan dalam pekerjaan tim: {get_value('Menawarkan bantuan')}
- Proaktif membantu saat rekan kesulitan: {get_value('Proaktif menawarkan bantuan')}
- Berpartisipasi dalam diskusi tim: {get_value('Berpartisipasi aktif')}

Selalu berikan dan tampilkan juga nilai kuantitatif (bila ada) untuk setiap parameter dalam format tabel.
Tulislah narasi profesional dan sopan, gunakan gaya naratif, bukan bullet point. 
Berikan pujian pada skor tinggi, dan saran pada skor rendah.
"""

# Generate Narasi
st.subheader("🧠 Analisis Naratif oleh GPT-4o")
if st.button("🎯 Generate Analisis"):
    with st.spinner("Sedang menganalisis dengan GPT-4o..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Anda adalah Pelindo AI, asisten analisis kinerja berbasis AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            narasi = response.choices[0].message.content
            st.markdown("### ✍️ Narasi Kinerja:")
            st.write(narasi)
        except Exception as e:
            st.error(f"Gagal memanggil GPT API: {e}")





