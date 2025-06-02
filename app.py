import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv

# Load API key dari .env
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
st.title("📊 Pelindo AI – Analisis Kinerja & KPI Pekerja")

# Pilih NIPP
nipp_list = df["NIPP_Pekerja"].unique()
selected_nipp = st.selectbox("Pilih NIPP Pekerja:", nipp_list)
row = df[df["NIPP_Pekerja"] == selected_nipp].iloc[0]
nama_posisi = row["Nama_Posisi"]

# Kelompok parameter
delivery_cols = ['Pekerjaan yang diberikan selesai', 'Pekerjaan diselesaikan tepat waktu', 'Kualitas Pekerjaan']
leadership_cols = ['Membimbing rekan tim', 'Menunjukkan sikap kerja positif dan inspiratif',
                   'Membangun semangat tim', 'Mengambil peran aktif menyelesaikan tantangan']
communication_cols = ['Memotong pembicaraan tanpa alasan', 'Waktu respon komunikasi penting', 'Memberikan masukan']
teamwork_cols = ['Membagikan informasi', 'Menawarkan bantuan dalam pekerjaan tim',
                 'Proaktif menawarkan bantuan saat rekan kesulitan', 'Berpartisipasi aktif dalam diskusi atau koordinasi tim']

# Fungsi tampilkan nilai parameter per aspek
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

# ===== KPI Section =====
st.subheader("📌 Deskripsi dan Nilai KPI")

kpi_data = []
for i in range(1, 7):
    deskripsi = f"Deskripsi_KPI_{i}"
    nilai = f"Nilai_KPI_{i}"
    if deskripsi in df.columns and nilai in df.columns:
        kpi_data.append({
            "KPI": f"KPI {i}",
            "Deskripsi": row[deskripsi],
            "Nilai": row[nilai]
        })

kpi_df = pd.DataFrame(kpi_data)
st.dataframe(kpi_df)

# Ambil nilai deskriptif untuk GPT prompt
def get_val(col_name):
    matches = [col for col in df.columns if col_name.lower() in col.lower()]
    return str(row[matches[0]]) if matches else "[Data Tidak Ada]"

# Generate prompt untuk GPT
prompt = f"""
Anda adalah Pelindo AI, asisten analisis kinerja profesional.
Narasi tidak perlu diawali dengan basa-basi dan tidak perlu diakhiri dengan salam hormat.
Tulislah narasi profesional dan sopan berdasarkan hasil berikut:

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

KPI Highlights:
- Kamu adalah yang paling tahu mengenai semua rincian parameter KPI yang terkait bisnis Pelindo
- Jelaskan dan elaborasi tiap deskripsi dan skor KPI dari unit-unit di Pelindo
- ketika membahas deskripsi KPI, coba detailkan dengaan melakukan insight sesuai sektor bisnis pelindo dan kepelabuhan sesuai dengan knowledge kamu


"""

for i in range(1, 7):
    deskripsi = get_val(f"Deskripsi_KPI_{i}")
    nilai = get_val(f"Nilai_KPI_{i}")
    prompt += f"\nKPI {i}: {deskripsi} → Nilai: {nilai}"

prompt += "\n\nTulislah narasi lengkap dan sopan. Berikan apresiasi pada nilai tinggi dan saran pada nilai sedang atau rendah."

# Generate analisis naratif
st.subheader("🧠 Narasi Analisis oleh Pelindo AI")
if st.button("🎯 Generate Narasi"):
    with st.spinner("Sedang menganalisis..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Anda adalah Pelindo AI, asisten penilai kinerja profesional."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1500
            )
            narasi = response.choices[0].message.content
            st.markdown("### ✍️ Narasi Kinerja")
            st.write(narasi)
        except Exception as e:
            st.error(f"Gagal mengakses GPT API: {e}")
