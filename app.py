import streamlit as st
import pandas as pd

st.title("ASHA Monitoring Dashboard from Excel")

# 1️⃣ Upload Excel
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    sheet = st.selectbox("Select sheet to process")
    
    df = pd.read_excel(uploaded_file)
    
    # 2️⃣ Select needed columns
    required_cols = ['Name of ASHA', 'Participant Unique Code', '_submission_time']
    available_cols = [col for col in required_cols if col in df.columns]
    
    if len(available_cols) < 3:
        st.warning("Some required columns are missing!")
    else:
        df = df[available_cols].copy()
        df['_submission_time'] = pd.to_datetime(df['_submission_time'])
        
        # ---------------- TABLE 1: Overall forms ----------------
        st.subheader("Table 1: Overall Forms Submitted")
        
        # Month filter
        df['Month'] = df['_submission_time'].dt.to_period('M')
        month_options = sorted(df['Month'].astype(str).unique())
        selected_month = st.selectbox("Select Month (or All)", ["All"] + month_options)
        
        table1_df = df.copy()
        if selected_month != "All":
            table1_df = table1_df[table1_df['Month'].astype(str) == selected_month]
        
        table1 = table1_df.groupby('Name of ASHA').size().reset_index(name='Forms Submitted')
        st.dataframe(table1)
        
        # ---------------- TABLE 2: Duplicate Count ----------------
        st.subheader("Table 2: Duplicate Participant Count per ASHA")
        
        dup_count_df = (
            df.groupby('Name of ASHA')['Participant Unique Code']
              .apply(lambda x: x.duplicated().sum())
              .reset_index(name='Duplicate Participants')
        )
        st.dataframe(dup_count_df)
        
        # ---------------- TABLE 3: Duplicate List ----------------
        st.subheader("Table 3: List of Actual Duplicates for Selected ASHA")
        
        asha_list = df['Name of ASHA'].dropna().unique()
        selected_asha = st.selectbox("Select ASHA to view duplicates", asha_list)
        
        asha_df = df[df['Name of ASHA'] == selected_asha]
        duplicates = asha_df[asha_df.duplicated(subset=['Participant Unique Code'], keep=False)]
        
        if duplicates.empty:
            st.info("No duplicates found for this ASHA.")
        else:
            st.dataframe(duplicates)
            
            # Optional download
            st.download_button(
                "Download Duplicate List",
                duplicates.to_csv(index=False).encode('utf-8'),
                file_name=f"{selected_asha}_duplicates.csv",
                mime="text/csv"
            )

