import streamlit as st
import pandas as pd
from datetime import date
import gspread
from streamlit_gsheets import GSheetsConnection

# 1. Mobile-Optimized Page Config
st.set_page_config(
    page_title="Input Pengeluaran", 
    page_icon="💸", 
    layout="centered"
)

st.title("💸 Input Pengeluaran")

# 2. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Build the Mobile UI
with st.form("input_form", clear_on_submit=True):
    # Full-width inputs for primary data
    tanggal = st.date_input("Tanggal", value=date.today())
    
    # 2-column layout for shorter dropdowns to save vertical screen space
    col1, col2 = st.columns(2)
    with col1:
        tipe = st.selectbox("Tipe", options=["RT", "Mo"])
        mata_uang = st.selectbox("Mata Uang", options=["EUR", "IDR"])
    with col2:
        oleh = st.selectbox("Oleh", options=["Gan", "Mof"])
        # Updated Penyimpanan list
        penyimpanan_list = ["ABN Mo-Ga",
            "Permata Gan", "Jago Mo-Ga", "Mandiri Gan", "Gopay Gan", "Cash Gan", 
            "Emoney Gan", "Jenius Gan", "Revolut Gan", "ABN Gan", 
            "Wise Gan", "Kas Gan", "Kas Mo", "Mandiri Mo"
        ]

        penyimpanan = st.selectbox("Penyimpanan", options=penyimpanan_list)    
    subkategori = st.text_input("Subkategori")
    nominal = st.number_input("Nominal", min_value=0.0, format="%.2f")
    deskripsi = st.text_area("Deskripsi")
    
    # Mobile-friendly full-width submit button
    submitted = st.form_submit_button("Submit Data", use_container_width=True)

if submitted:
    if nominal <= 0:
        st.error("⚠️ Nominal tidak boleh kosong atau nol!")
    else:
        try:
            with st.spinner("Menyimpan data..."):
                # 1. Authenticate pure gspread directly using Streamlit secrets
                # Convert the Streamlit secrets object to a standard Python dictionary
                secrets_dict = dict(st.secrets["connections"]["gsheets"])
                client = gspread.service_account_from_dict(secrets_dict)
                
                # 2. Open the spreadsheet using the URL from secrets
                sheet_url = secrets_dict["spreadsheet"]
                sh = client.open_by_url(sheet_url)
                
                pengeluaran = sh.worksheet("Pengeluaran")
                
                # 3. Get last row from A1
                lastrow_val = pengeluaran.acell('A1').value
                
                if not lastrow_val:
                    st.error("Cell A1 is kosong. Tidak dapat menentukan baris terakhir.")
                    st.stop()
                    
                lastrow = str(lastrow_val)
                
                # 4. Map inputs to specific cells 
                updates = [
                    {'range': f'C{lastrow}', 'values': [[tanggal.strftime("%d/%m/%Y")]]},
                    {'range': f'D{lastrow}', 'values': [[tipe]]},                         
                    {'range': f'I{lastrow}', 'values': [[oleh]]},                         
                    {'range': f'M{lastrow}', 'values': [[penyimpanan]]},                  
                    {'range': f'H{lastrow}', 'values': [[subkategori]]},                  
                    {'range': f'J{lastrow}', 'values': [[mata_uang]]},                    
                    {'range': f'K{lastrow}', 'values': [[nominal]]},                      
                    {'range': f'L{lastrow}', 'values': [[deskripsi]]}                     
                ]
                
                # 5. Batch update all cells simultaneously
                pengeluaran.batch_update(updates)
                
                st.success(f"✅ Berhasil menambahkan {mata_uang} {nominal} ke baris {lastrow}!")
                
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {e}")