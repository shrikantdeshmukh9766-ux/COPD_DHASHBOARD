import streamlit as st
import pandas as pd

st.title("ASHA Monitoring Dashboard from Excel")

# 1️⃣ Upload Excel
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    sheet = st.selectbox("Select sheet to process", sheet_names)
    
    df = pd.read_excel(uploaded_file, sheet_name=sheet)
    
    st.write("**Preview of uploaded data:**")
    st.dataframe(df.head())  # Show first few rows for debugging
    
    # 2️⃣ Identify correct columns
    col_mapping = {
        'Name of ASHA': None,
        'Participant Unique Code': None,
        '_submission_time': None
    }
    
    for col in df.columns:
        if 'asha' in col.lower():
            col_mapping['Name of ASHA'] = col
        elif 'participant' in col.lower():
            col_mapping['Participant Unique Code'] = col
        elif 'submission' in col.lower() and 'time' in col.lower():
            col_mapping['_submission_time'] = col
    
    missing_cols = [k for k,v in col_mapping.items() if v is None]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
    else:
        df = df[[col_mapping['Name of ASHA'], col_mapping['Participant Unique Code'], col_mapping['_submission_time']]].copy()
        df.columns = ['Name of ASHA', 'Participant Unique Code', '_submission_time']
        
        # Ensure datetime
        df['_submission_time'] = pd.to_datetime(df['_submission_time'], errors='coerce')
        
        # ---------------- TABLE 1 ----------------
        st.subheader("Table 1: Overall Forms Submitted")
        df['Month'] = df['_submission_time'].dt.to_period('M')
        month_options = ["All"] + sorted(df['Month'].dropna().astype(str).unique())
        selected_month = st.selectbox("Select Month (or All)", month_options)
        
        table1_df = df.copy()
        if selected_month != "All":
            table1_df = table1_df[df['Month'].astype(str) == selected_month]
        
        table1 = table1_df.groupby('Name of ASHA').size().reset_index(name='Forms Submitted')
        st.dataframe(table1)
        
        # ---------------- TABLE 2 ----------------
        st.subheader("Table 2: Duplicate Participant Count per ASHA")
        table2 = (
            df.groupby('Name of ASHA')['Participant Unique Code']
              .apply(lambda x: x.duplicated().sum())
              .reset_index(name='Duplicate Participants')
        )
        st.dataframe(table2)
        
        # ---------------- TABLE 3 ----------------
        st.subheader("Table 3: Actual Duplicates per ASHA")
        asha_list = df['Name of ASHA'].dropna().unique()
        selected_asha = st.selectbox("Select ASHA for duplicate list", asha_list)
        
        asha_df = df[df['Name of ASHA'] == selected_asha]
        duplicates = asha_df[asha_df.duplicated(subset=['Participant Unique Code'], keep=False)]
        
        if duplicates.empty:
            st.info("No duplicates found for this ASHA.")
        else:
            st.dataframe(duplicates)
            st.download_button(
                "Download Duplicate List",
                duplicates.to_csv(index=False).encode('utf-8'),
                file_name=f"{selected_asha}_duplicates.csv",
                mime="text/csv"
            )
