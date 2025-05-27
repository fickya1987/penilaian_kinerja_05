import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv
import plotly.express as px
import re

# Load API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("dummy_feedback.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Helper untuk mengekstrak angka dari teks format bebas
def safe_extract_number(val):
    if isinstance(val, (int, float)):
        return int(val)

    val = str(val).lower().replace("–", "-").replace("—", "-").strip()

    if "selalu" in val:
        return 5
    if "tidak pernah" in val or "hanya jika diminta" in val:
        return 0
    if "< 2 jam" in val or "cepat" in val:
        return 5
    if "2-4 jam" in val:
        return 4
    if "5-8 jam" in val:
        return 3
    if ">8 jam" in val:
        return 2

    match = re.match(r"(\d+)[\s\-–—to]*(\d+)", val)
    if match:
        return (int(match.group(1)) + int(match.group(2))) // 2

    match = re.search(r"\d+", val)
    if match:
        return int(match.group())

    return 0

# Hitung skor tiap aspek
def compute_scores(row):
    try:
        delivery = (
            safe_extract_number(row['Pekerjaan yang diberikan selesai']) * 0.4 +
            safe_extract_number(row['Pekerjaan diselesaikan tepat waktu']) * 0.3 +
            safe_extract_number(row['Kualitas Pekerjaan']) * 0.3
        ) / 100

        leadership = sum([
            safe_extract_number(row['Membimbing rekan tim']),
            safe_extract_number(row['Membangun semangat tim']),
            safe_extract_number(row['Mengambil peran aktif menyelesaikan tantangan'])
        ])

        communication = (
            safe_extract_number(row['Memotong pembicaraan tanpa alasan']) +
            safe_extract_number(row['Waktu respon komunikasi penting']) +
            safe_extract_number(row['Memberikan masukan'])
        )

        teamwork = sum([
            safe_extract_number(row['Membagikan informasi']),
            safe_extract_number(row['Menawarkan bantuan dalam pekerjaan tim']),
            safe_extract_number(row['Proaktif menawarkan bantuan saat rekan kesulitan']),
            safe_extract_number(row['Berpartisipasi aktif dalam diskusi atau koordinasi tim'])
        ])

        return pd.DataFrame({
            "Aspek": ["Delivery", "Leadership", "Communication", "Teamwork"],
            "Skor": [round(delivery, 2), leadership, communication, teamwork]
        })
    except Exception as e:
        st.error(f"Gagal menghitung skor: {e}")
        return pd.DataFrame(columns=["Aspek", "Skor"])

# Judul
st.title("📊 Pelindo AI – Analisis Kinerja Pekerja Berbasis GPT-4o")

# Pilih pekerja
nipp_list = df["NIPP_Pekerja"].unique()
selected_nipp = st.selectbox("Pilih NIPP Pekerja:", nipp_list)
row = df[df["NIPP_Pekerja"] == selected_nipp].iloc[0]
nama_posisi = row["Nama_Posisi"]

# Hitung skor per aspek
score_df = compute_scores(row)

# Tampilkan tabel skor
st.subheader("🗂️ Ringkasan Skor Per Aspek")
st.dataframe(score_df)

# Chart
st.subheader("📈 Visualisasi Skor Kinerja")
fig = px.bar(score_df, x="Aspek", y="Skor", color="Aspek", text_auto=True, title="Skor Kinerja Berdasarkan Aspek")
st.plotly_chart(fig)

# Prompt untuk GPT-4o
def get_val(col_name):
    matches = [col for col in df.columns if col_name.lower() in col.lower()]
    return str(row[matches[0]]) if matches else "[Data Tidak Ada]"

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

# Tombol generate analisis
st.subheader("🧠 Analisis Naratif oleh GPT-4o")
if st.button("🎯 Generate Analisis"):
    with st.spinner("Sedang menganalisis dengan GPT-4o..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Anda adalah Pelindo AI, asisten penilai kinerja profesional."},
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





