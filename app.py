import streamlit as st
import pandas as pd

st.title("ASHA Monitoring Dashboard from Excel")

# 1️⃣ Upload Excel
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    # Read all sheet names
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    sheet = st.selectbox("Select sheet to process", sheet_names)
    
    # Read selected sheet
    df = pd.read_excel(uploaded_file, sheet_name=sheet)
    
    st.subheader("Preview of Uploaded Data")
    st.dataframe(df.head())
    
    # 2️⃣ Check required columns
    required_cols = ['Participant Unique Code', 'Name of ASHA', '_submission_time']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
    else:
        # Keep only required columns
        df = df[required_cols].copy()
        df['_submission_time'] = pd.to_datetime(df['_submission_time'], errors='coerce')
        
        # ---------------- TABLE 1 ----------------
        st.subheader("Table 1: Forms Submitted per ASHA")
        df['Month'] = df['_submission_time'].dt.to_period('M')
        month_options = ["All"] + sorted(df['Month'].dropna().astype(str).unique())
        selected_month = st.selectbox("Select Month (or All)", month_options, key="month1")
        
        table1_df = df.copy()
        if selected_month != "All":
            table1_df = table1_df[table1_df['Month'].astype(str) == selected_month]
        
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
        st.subheader("Table 3: Actual Duplicate Participants (Filter by ASHA)")
        # Dropdown to select ASHA
        asha_list = df['Name of ASHA'].dropna().unique()
        selected_asha = st.selectbox("Select ASHA for duplicate list", asha_list, key="asha_dup")
        
        # Filter by selected ASHA
        asha_df = df[df['Name of ASHA'] == selected_asha]
        # Find duplicates **within that ASHA**
        duplicates = asha_df[asha_df.duplicated(subset=['Participant Unique Code'], keep=False)]
        
        if duplicates.empty:
            st.info(f"No duplicates found for ASHA: {selected_asha}")
        else:
            st.dataframe(duplicates)
            st.download_button(
                "Download Duplicate List for this ASHA",
                duplicates.to_csv(index=False).encode('utf-8'),
                file_name=f"{selected_asha}_duplicates.csv",
                mime="text/csv"
            )
