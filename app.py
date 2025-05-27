import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("dummy_feedback.csv")

df = load_data()

# Title
st.title("Pelindo AI: Analisis Kinerja Individu")

# Select NIPP
nipp_list = df["NIPP_Pekerja"].unique()
selected_nipp = st.selectbox("Pilih NIPP Pekerja:", nipp_list)

# Ambil data pekerja
row = df[df["NIPP_Pekerja"] == selected_nipp].iloc[0]
nama_posisi = row["Nama_Posisi"]

# Compose prompt
prompt = f"""
Anda adalah Pelindo AI, sang asisten analisis kinerja berbasis GPT-4o.

Tulislah narasi penilaian menyeluruh berdasarkan hasil formulir feedback berikut:

Posisi: {nama_posisi}

DELIVERY:
1. Penyelesaian tugas: {row['Pekerjaan yang diberikan selesai']}%
2. Ketepatan waktu: {row['Pekerjaan diselesaikan tepat waktu']}%
3. Kualitas pekerjaan (jumlah koreksi): {row['Kualitas Pekerjaan']}

LEADERSHIP:
- Membimbing rekan tim: {row['Membimbing rekan tim']}
- Menunjukkan sikap kerja positif: {row['Menunjukkan sikap kerja positif dan inspiratif']}
- Membangun semangat tim: {row['Membangun semangat tim']}
- Mengambil peran aktif menyelesaikan tantangan: {row['Mengambil peran aktif menyelesaikan tantangan']}

COMMUNICATION:
- Memotong pembicaraan: {row['Memotong pembicaraan tanpa alasan']}
- Waktu respon komunikasi penting: {row['Waktu respon komunikasi penting']}
- Memberikan masukan/ide: {row['Memberikan masukan']}

TEAMWORK:
- Membagikan informasi: {row['Membagikan informasi']}
- Menawarkan bantuan dalam pekerjaan tim: {row['Menawarkan bantuan dalam pekerjaan tim']}
- Proaktif membantu saat rekan kesulitan: {row['Proaktif menawarkan bantuan saat rekan kesulitan']}
- Berpartisipasi dalam diskusi tim: {row['Berpartisipasi aktif dalam diskusi atau koordinasi tim']}

Tulislah narasi profesional dan sopan, berikan pujian untuk skor tinggi, dan berikan saran untuk skor rendah. Gunakan gaya naratif, bukan bullet point.
"""

# Generate narrative
if st.button("Generate Analisis Naratif"):
    with st.spinner("Sedang menganalisa..."):
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Anda adalah Pelindo AI, asisten penilai kinerja profesional."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        narasi = response.choices[0].message.content
        st.markdown("### Hasil Analisis Naratif:")
        st.write(narasi)
