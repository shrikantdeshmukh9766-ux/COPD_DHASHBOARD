import streamlit as st
import pandas as pd

st.title("ASHA Monthly Form Count")

file = st.file_uploader("Upload Excel file", type=["xlsx","csv"])

if file is not None:

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    # Convert submission time
    df['_submission_time'] = pd.to_datetime(df['_submission_time'])

    # Month name instead of number
    df['Month'] = df['_submission_time'].dt.strftime('%b')

    # Pivot table
    table1 = pd.pivot_table(
        df,
        index='Select the Name of Asha',
        columns='Month',
        values='Select the Participant Unique Code',
        aggfunc='count',
        fill_value=0
    )

    st.dataframe(table1)
