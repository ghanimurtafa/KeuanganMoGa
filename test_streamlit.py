import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Streamlit automatically finds the credentials in st.secrets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("Data Entry Form")

with st.form(key="data_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120)
    submit = st.form_submit_button("Insert Data")

if submit:
    # 1. Read existing data
    existing_data = conn.read(worksheet="Sheet1")
    
    # 2. Append new row
    new_row = pd.DataFrame([{"Name": name, "Age": age}])
    updated_data = pd.concat([existing_data, new_row], ignore_index=True)
    
    # 3. Update the Google Sheet
    conn.update(worksheet="Sheet1", data=updated_data)
    
    # 4. Clear the cache so the app fetches the newest data next time
    st.cache_data.clear()
    st.success("Data inserted successfully!")