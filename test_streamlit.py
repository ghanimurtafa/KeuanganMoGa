import streamlit as st
import gspread
from datetime import date

st.set_page_config(page_title="Input Pengeluaran", page_icon="💸", layout="centered")
st.title("💸 Input Pengeluaran")

# 1. VLOOKUP Database Mapping
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
    "Hutang": {"urgensi": "Investasi", "kantong": "Hutang", "kategori": "Hutang"}
}

# 2. Session state to clear fields after submit (since we removed st.form)
if "reset_key" not in st.session_state:
    st.session_state.reset_key = 0
k = st.session_state.reset_key

# 3. Build the Live UI
tanggal = st.date_input("Tanggal", value=date.today(), key=f"tgl_{k}")

col1, col2 = st.columns(2)
with col1:
    tipe = st.selectbox("Tipe", options=["RT", "Mo"], key=f"tipe_{k}")
    mata_uang = st.selectbox("Mata Uang", options=["EUR", "IDR"], key=f"mu_{k}")
with col2:
    oleh = st.selectbox("Oleh", options=["Gan", "Mof"], key=f"oleh_{k}")
    penyimpanan_list = [ "ABN Mo-Ga",
        "Permata Gan", "Jago Mo-Ga", "Mandiri Gan", "Gopay Gan", "Cash Gan", 
        "Emoney Gan", "Jenius Gan", "Revolut Gan", "ABN Gan", 
        "Wise Gan", "Kas Gan", "Kas Mo", "Mandiri Mo"
    ]
    penyimpanan = st.selectbox("Penyimpanan", options=penyimpanan_list, index=9, key=f"peny_{k}")

# --- NEW VLOOKUP LOGIC ---
subkategori = st.selectbox("Subkategori", options=list(SUBKATEGORI_DATA.keys()), key=f"subkat_{k}")

# Fetch matching data based on selection
urgensi = SUBKATEGORI_DATA[subkategori]["urgensi"]
kantong = SUBKATEGORI_DATA[subkategori]["kantong"]
kategori = SUBKATEGORI_DATA[subkategori]["kategori"]

# Display them as disabled (read-only) text inputs
col_u, col_ka, col_kat = st.columns(3)
with col_u:
    st.text_input("Urgensi", value=urgensi, disabled=True, key=f"u_{k}")
with col_ka:
    st.text_input("Kantong", value=kantong, disabled=True, key=f"ka_{k}")
with col_kat:
    st.text_input("Kategori", value=kategori, disabled=True, key=f"kat_{k}")
# -------------------------

nominal = st.number_input("Nominal", min_value=0.0, format="%.2f", key=f"nom_{k}")
deskripsi = st.text_area("Deskripsi", key=f"desk_{k}")

# 4. Handle Submission
if st.button("Submit Data", use_container_width=True):
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
                    
                    # Writing the VLOOKUP data to Columns E, F, G 
                    {'range': f'E{lastrow}', 'values': [[urgensi]]},
                    {'range': f'F{lastrow}', 'values': [[kantong]]},
                    {'range': f'G{lastrow}', 'values': [[kategori]]},
                    
                    {'range': f'H{lastrow}', 'values': [[subkategori]]},                         
                    {'range': f'I{lastrow}', 'values': [[oleh]]},                         
                    {'range': f'J{lastrow}', 'values': [[mata_uang]]},                    
                    {'range': f'K{lastrow}', 'values': [[nominal]]},                      
                    {'range': f'L{lastrow}', 'values': [[deskripsi]]},                     
                    {'range': f'M{lastrow}', 'values': [[penyimpanan]]}                  
                ]
                
                pengeluaran.batch_update(updates)
                st.success(f"✅ Berhasil menambahkan {mata_uang} {nominal} ke baris {lastrow}!")
                
                # Increment the key to force all widgets to clear instantly
                st.session_state.reset_key += 1
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {e}")