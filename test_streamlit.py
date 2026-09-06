import streamlit as st
import gspread
from datetime import date

st.set_page_config(page_title="Input Pengeluaran", page_icon="💸", layout="centered")

# --- 1. PASSWORD AUTHENTICATION GATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Restricted Access")
    st.markdown("Please enter your password to access the expense tracker.")

    with st.form("login_form"):
        entered_password = st.text_input("Password", type="password")
        login_submitted = st.form_submit_button("Login", use_container_width=True)

        if login_submitted:
            correct_password = st.secrets["auth"]["app_password"]
            if entered_password == correct_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password!")

    st.stop()

# --- 2. MAIN APP (Runs only after successful login) ---

with st.sidebar:
    if st.button("🔒 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# Trim default Streamlit top padding so the form starts higher on screen
st.markdown(
    """
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        div[data-testid="stVerticalBlock"] > div { gap: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.write("💸 Input Pengeluaran")

# VLOOKUP Database Mapping
SUBKATEGORI_DATA = {
    "Ziswaf Lain": {"urgensi": "Non-Bulanan", "kantong": "Ziswaf", "kategori": "Ziswaf"},
    "Zakat Fitrah": {"urgensi": "Non-Bulanan", "kantong": "Ziswaf", "kategori": "Zakat Fitrah"},
    "Zakat Mal": {"urgensi": "Non-Bulanan", "kantong": "Ziswaf", "kategori": "Zakat Mal"},
    "Wakaf": {"urgensi": "Non-Bulanan", "kantong": "Ziswaf", "kategori": "Wakaf"},
    "Bela Sungkawa": {"urgensi": "Non-Bulanan", "kantong": "Ziswaf", "kategori": "Bela Sungkawa"},
    "Pernikahan": {"urgensi": "Non-Bulanan", "kantong": "Keluarga", "kategori": "Pernikahan"},
    "Keluarga": {"urgensi": "Non-Bulanan", "kantong": "Keluarga", "kategori": "Keluarga"},
    "Darurat (Keluarga)": {"urgensi": "Non-Bulanan", "kantong": "Keluarga", "kategori": "Keluarga"},
    "Travelio": {"urgensi": "Non-Bulanan", "kantong": "Keluarga", "kategori": "Keluarga"},
    "Darurat": {"urgensi": "Non-Bulanan", "kantong": "Darurat", "kategori": "Darurat"},
    "Haji": {"urgensi": "Non-Bulanan", "kantong": "Haji", "kategori": "Haji"},
    "Liburan": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Liburan"},
    "Pulang Kampung": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Pulang Kampung"},
    "Masa Depan": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Masa Depan"},
    "Kerjaan": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Masa Depan"},
    "Investasi": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Langganan Lain2": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Masa Depan"},
    "Konversi Uang": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Konversi Uang"},
    "Pendidikan": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Pendidikan"},
    "Pajak Tahunan": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Pajak"},
    "Anggaran Disimpan": {"urgensi": "Non-Bulanan", "kantong": "Anggaran Disimpan", "kategori": "Anggaran Disimpan"},
    "Dana Tak Terduga Bulanan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Dana Tak Terduga"},
    "Keperluan Rumah Habis Pakai": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Keperluan Rumah Tidak Habis Pakai": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Listrik": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Air": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Gas": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Internet Rumah": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Sewa": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Laundry": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Bahan Makanan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Makan & Minum Primer"},
    "Buah-Buahan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Makan & Minum Primer"},
    "Makanan Berat Reguler": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Makan & Minum Primer"},
    "Asuransi": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Dokter": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Vitamin & Suplemen": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Obat": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Olahraga": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Kegiatan Kesehatan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Kosmetik": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Buku": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Pendidikan"},
    "Pembelajaran": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Pendidikan"},
    "Peralatan Pendidikan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Pendidikan"},
    "Pulsa & Internet HP": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Komunikasi"},
    "Administrasi": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Komunikasi"},
    "Transportasi Umum": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Transportasi Online": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Bensin": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Parkir": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Tol": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Pajak": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Sepeda": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Keluarga Bulanan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keluarga Bulanan"},
    "Ziswaf Bulanan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Ziswaf Bulanan"},
    "Rekonsiliasi Bulanan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Rekonsiliasi"},
    "Baju": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Aksesoris": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Elektronik": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Sepatu": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Belanja Lain-Lain": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Berkebun": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Olahraga Rekreatif": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Transportasi Rekreasi": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Tiket Hiburan": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Musik": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Fotografi": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Langganan Hiburan": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Rekreasi Lain": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Bersosialisasi": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Sosial"},
    "Hadiah": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Sosial"},
    "Makanan Ringan": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Makan Rekreatif"},
    "Restoran": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Makan Rekreatif"},
    "Kafe": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Makan Rekreatif"},
    "Pesan Antar": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Makan Rekreatif"},
    "Emas": {"urgensi": "Investasi", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Bibit": {"urgensi": "Investasi", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Franchise/Bisnis": {"urgensi": "Investasi", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Saham": {"urgensi": "Investasi", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Investasi Lain": {"urgensi": "Investasi", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Hutang": {"urgensi": "Investasi", "kantong": "Hutang", "kategori": "Hutang"},
}

if "reset_key" not in st.session_state:
    st.session_state.reset_key = 0
k = st.session_state.reset_key

# --- Row 1: Tanggal + Nominal ---
r1c1, r1c2 = st.columns(2)
with r1c1:
    tanggal = st.date_input("Tanggal", value=date.today(), key=f"tgl_{k}")
with r1c2:
    nominal = st.number_input("Nominal", min_value=0.0, format="%.2f", key=f"nom_{k}")

# --- Row 2: Tipe + Mata Uang + Oleh (short values, fit 3-up) ---
r2c1, r2c2, r2c3 = st.columns(3)
with r2c1:
    tipe = st.selectbox("Tipe", options=["RT", "Mo"], key=f"tipe_{k}")
with r2c2:
    mata_uang = st.selectbox("Mata Uang", options=["EUR", "IDR"], key=f"mu_{k}")
with r2c3:
    oleh = st.selectbox("Oleh", options=["Gan", "Mof"], key=f"oleh_{k}")

# --- Row 3: Penyimpanan + Subkategori ---
r3c1, r3c2 = st.columns(2)
with r3c1:
    penyimpanan_list = [
        "ABN Mo-Ga", "Permata Gan", "Jago Mo-Ga", "Mandiri Gan", "Gopay Gan",
        "Cash Gan", "Emoney Gan", "Jenius Gan", "Revolut Gan", "ABN Gan",
        "Wise Gan", "Kas Gan", "Kas Mo", "Mandiri Mo",
    ]
    penyimpanan = st.selectbox("Penyimpanan", options=penyimpanan_list, index=9, key=f"peny_{k}")
with r3c2:
    subkategori = st.selectbox("Subkategori", options=list(SUBKATEGORI_DATA.keys()), key=f"subkat_{k}")

urgensi = SUBKATEGORI_DATA[subkategori]["urgensi"]
kantong = SUBKATEGORI_DATA[subkategori]["kantong"]
kategori = SUBKATEGORI_DATA[subkategori]["kategori"]

# Auto-derived fields shown as one compact read-only line instead of 3 disabled inputs
st.caption(f"📍 {urgensi}  ·  {kantong}  ·  {kategori}")

deskripsi = st.text_area("Deskripsi", key=f"desk_{k}", height=70)

if st.button("Submit Data", use_container_width=True, type="primary"):
    if nominal <= 0:
        st.error("⚠️ Nominal tidak boleh kosong atau nol!")
    else:
        try:
            with st.spinner("Menyimpan data..."):
                secrets_dict = dict(st.secrets["connections"]["gsheets"])
                client = gspread.service_account_from_dict(secrets_dict)

                sheet_url = secrets_dict["spreadsheet"]
                sh = client.open_by_url(sheet_url)
                pengeluaran = sh.worksheet("Pengeluaran")

                lastrow_val = pengeluaran.acell('A1').value
                if not lastrow_val:
                    st.error("Cell A1 is kosong. Tidak dapat menentukan baris terakhir.")
                    st.stop()

                lastrow = str(lastrow_val)

                updates = [
                    {'range': f'C{lastrow}', 'values': [[tanggal.strftime("%d/%m/%Y")]]},
                    {'range': f'D{lastrow}', 'values': [[tipe]]},
                    {'range': f'E{lastrow}', 'values': [[urgensi]]},
                    {'range': f'F{lastrow}', 'values': [[kantong]]},
                    {'range': f'G{lastrow}', 'values': [[kategori]]},
                    {'range': f'H{lastrow}', 'values': [[subkategori]]},
                    {'range': f'I{lastrow}', 'values': [[oleh]]},
                    {'range': f'J{lastrow}', 'values': [[mata_uang]]},
                    {'range': f'K{lastrow}', 'values': [[nominal]]},
                    {'range': f'L{lastrow}', 'values': [[deskripsi]]},
                    {'range': f'M{lastrow}', 'values': [[penyimpanan]]},
                ]

                pengeluaran.batch_update(updates)
                st.success(f"✅ Berhasil menambahkan {mata_uang} {nominal} ke baris {lastrow}!")

                st.session_state.reset_key += 1
                st.rerun()

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {e}")