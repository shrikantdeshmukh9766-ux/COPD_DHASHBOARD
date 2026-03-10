import streamlit as st
import pandas as pd

st.title("Excel Viewer Dashboard")

# 1️⃣ Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    # 2️⃣ Read all sheet names
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    # 3️⃣ Select sheet
    sheet = st.selectbox("Select sheet to view", sheet_names)

    # 4️⃣ Read selected sheet
    df = pd.read_excel(uploaded_file, sheet_name=sheet)

    # 5️⃣ Show dataframe
    st.subheader(f"Data from sheet: {sheet}")
    st.dataframe(df)
