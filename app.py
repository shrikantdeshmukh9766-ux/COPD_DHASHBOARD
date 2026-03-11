import streamlit as st
import pandas as pd

st.title("ASHA Form Monitoring Dashboard")

# Upload Excel
file = st.file_uploader("Upload Excel file", type=["xlsx","csv"])

if file is not None:

    # Read file
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    # Convert submission time to datetime
    df['_submission_time'] = pd.to_datetime(df['_submission_time'])

    # Create month column
    df['Month'] = df['_submission_time'].dt.to_period('M').astype(str)

    # Group data
    table = (
        df.groupby(['Select the Name of Asha','Month'])
        ['Select the Participant Unique Code']
        .count()
        .reset_index(name='Forms Filled')
    )

    st.subheader("ASHA-wise Month-wise Form Count")
    st.dataframe(table)

    # Pivot table (better view)
    st.subheader("ASHA Monthly Summary")

    pivot = pd.pivot_table(
        df,
        index='Select the Name of Asha',
        columns='Month',
        values='Select the Participant Unique Code',
        aggfunc='count',
        fill_value=0
    )

    st.dataframe(pivot)
