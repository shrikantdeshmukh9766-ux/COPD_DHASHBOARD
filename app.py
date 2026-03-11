import streamlit as st
import pandas as pd

st.title("ASHA Monitoring Dashboard")

file = st.file_uploader("Upload Excel file", type=["xlsx","csv"])

if file is not None:

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    # convert submission time
    df['_submission_time'] = pd.to_datetime(df['_submission_time'])

    # month column
    df['Month'] = df['_submission_time'].dt.strftime('%b')

    # ---------------- TABLE 1 ----------------
    st.subheader("Table 1: ASHA Month-wise Form Count")

    table1 = pd.pivot_table(
        df,
        index='Select the Name of Asha',
        columns='Month',
        values='Select the Participant Unique Code',
        aggfunc='count',
        fill_value=0
    )

    st.dataframe(table1)

    # ---------------- TABLE 2 ----------------
    st.subheader("Table 2: Duplicate Forms Count by ASHA")

    dup = df[df.duplicated(
        subset=['Select the Name of Asha','Select the Participant Unique Code'],
        keep=False
    )]

    table2 = (
        dup.groupby('Select the Name of Asha')
        ['Select the Participant Unique Code']
        .count()
        .reset_index(name='Duplicate Forms')
    )

    st.dataframe(table2)

    # ---------------- TABLE 3 ----------------
    st.subheader("Table 3: Actual Duplicate Participant List")

    asha_list = dup['Select the Name of Asha'].unique()

    selected_asha = st.selectbox("Select ASHA", asha_list)

    table3 = dup[dup['Select the Name of Asha'] == selected_asha][
        ['Select the Name of Asha','Select the Participant Unique Code','_submission_time']
    ]

    st.dataframe(table3)
