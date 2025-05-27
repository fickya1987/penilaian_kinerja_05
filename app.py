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
    df = pd.read_csv("dummy_feedback.csv")
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
    return df

df = load_data()

# Title
st.title("Pelindo AI: Analisis Kinerja Individu")

# Select NIPP
nipp_list = df["NIPP_Pekerja"].unique()
selected_nipp = st.selectbox("Pilih NIPP Pekerja:", nipp_list)

# Ambil data pekerja
row = df[df["NIPP_Pekerja"] == selected_nipp].iloc[0]
nama_posisi = row["Nama_Posisi"]

# Ambil nama-nama kolom yang kita perlukan
def get_value(col_name):
    # Pastikan pencocokan kolom yang toleran terhadap whitespace
    matched_cols = [col for col in df.columns if col_name.lower() in col.lower()]
    if matched_cols:
        return row[matched_cols[0]]
    return "[Data Tidak Ditemukan]"

# Compose prompt
prompt = f"""
Anda adalah Pelindo AI, sang asisten analisis kinerja berbasis GPT-4o.

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

Berikan dan tampilkan juga nilai kuantitatif (bila ada) untuk setiap parameter. Kemudian, sajikan juga chart atau grafik yang merujuk pada parameter yang kuantitatif.
Tulislah narasi profesional dan sopan, berikan pujian untuk skor tinggi, dan berikan saran untuk skor rendah. Gunakan gaya naratif, bukan bullet point.
"""

# Generate narrative
if st.button("Generate Analisis Naratif"):
    with st.spinner("Sedang menganalisa..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Anda adalah Pelindo AI, asisten penilai kinerja profesional."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            narasi = response.choices[0].message.content
            st.markdown("### Hasil Analisis Naratif:")
            st.write(narasi)
        except Exception as e:
            st.error(f"Gagal mengakses GPT API: {e}")
