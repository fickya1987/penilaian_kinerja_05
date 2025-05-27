import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv

# Load OpenAI API Key dari .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("dummy_feedback.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Judul Aplikasi
st.title("📊 Pelindo AI – Analisis Kinerja Pekerja Berbasis GPT-4o")

# Pilihan NIPP
nipp_list = df["NIPP_Pekerja"].unique()
selected_nipp = st.selectbox("Pilih NIPP Pekerja:", nipp_list)
row = df[df["NIPP_Pekerja"] == selected_nipp].iloc[0]
nama_posisi = row["Nama_Posisi"]

# Daftar kolom per aspek
delivery_cols = ['Pekerjaan yang diberikan selesai', 'Pekerjaan diselesaikan tepat waktu', 'Kualitas Pekerjaan']
leadership_cols = ['Membimbing rekan tim', 'Menunjukkan sikap kerja positif dan inspiratif',
                   'Membangun semangat tim', 'Mengambil peran aktif menyelesaikan tantangan']
communication_cols = ['Memotong pembicaraan tanpa alasan', 'Waktu respon komunikasi penting', 'Memberikan masukan']
teamwork_cols = ['Membagikan informasi', 'Menawarkan bantuan dalam pekerjaan tim',
                 'Proaktif menawarkan bantuan saat rekan kesulitan', 'Berpartisipasi aktif dalam diskusi atau koordinasi tim']

# Fungsi ambil nilai parameter sebagai DataFrame
def get_aspek_df(cols):
    return pd.DataFrame({col: [row[col]] for col in cols})

# Tampilkan tabel per aspek
st.subheader("📁 Delivery")
st.dataframe(get_aspek_df(delivery_cols))

st.subheader("📁 Leadership")
st.dataframe(get_aspek_df(leadership_cols))

st.subheader("📁 Communication")
st.dataframe(get_aspek_df(communication_cols))

st.subheader("📁 Teamwork")
st.dataframe(get_aspek_df(teamwork_cols))

# Ambil nilai deskriptif untuk prompt GPT
def get_val(col_name):
    matches = [col for col in df.columns if col_name.lower() in col.lower()]
    return str(row[matches[0]]) if matches else "[Data Tidak Ada]"

# Prompt GPT-4o
prompt = f"""
Anda adalah Pelindo AI, asisten analisis kinerja profesional.

Tulislah narasi penilaian menyeluruh berdasarkan hasil formulir feedback berikut:

Posisi: {nama_posisi}

DELIVERY:
1. Penyelesaian tugas: {get_val('Pekerjaan yang diberikan selesai')}%
2. Ketepatan waktu: {get_val('Pekerjaan diselesaikan tepat waktu')}%
3. Kualitas pekerjaan: {get_val('Kualitas Pekerjaan')}

LEADERSHIP:
- Membimbing rekan tim: {get_val('Membimbing rekan tim')}
- Sikap kerja positif: {get_val('Menunjukkan sikap kerja positif')}
- Membangun semangat tim: {get_val('Membangun semangat tim')}
- Mengambil peran aktif: {get_val('Mengambil peran aktif')}

COMMUNICATION:
- Memotong pembicaraan: {get_val('Memotong pembicaraan')}
- Respon komunikasi: {get_val('Waktu respon komunikasi penting')}
- Memberikan masukan: {get_val('Memberikan masukan')}

TEAMWORK:
- Membagikan informasi: {get_val('Membagikan informasi')}
- Membantu pekerjaan tim: {get_val('Menawarkan bantuan')}
- Bantu rekan kesulitan: {get_val('Proaktif menawarkan bantuan')}
- Diskusi tim: {get_val('Berpartisipasi aktif')}

Tulislah narasi profesional dan sopan, gunakan gaya naratif, bukan bullet point.
Berikan pujian pada skor tinggi, dan saran pada skor rendah.
"""

# GPT-4o Narasi
st.subheader("🧠 Narasi Analisis oleh GPT-4o")
if st.button("🎯 Generate Narasi"):
    with st.spinner("Sedang menganalisis..."):
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
            st.markdown("### ✍️ Narasi Kinerja")
            st.write(narasi)
        except Exception as e:
            st.error(f"Gagal mengakses GPT API: {e}")
