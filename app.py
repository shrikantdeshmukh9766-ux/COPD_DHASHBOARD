import streamlit as st
import pandas as pd

st.title("ASHA Monitoring Dashboard")

# Upload Excel/CSV file
file = st.file_uploader("Upload Excel file", type=["xlsx","csv"])

if file is not None:

    # Read file
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    # Convert submission time
    df['_submission_time'] = pd.to_datetime(df['_submission_time'])

    # Month name and month number
    df['Month'] = df['_submission_time'].dt.strftime('%b')
    df['Month_num'] = df['_submission_time'].dt.month

    # =========================
    # TABLE 1 : ASHA × MONTH
    # =========================
    st.subheader("Table 1: ASHA Month-wise Form Count")

    table1 = pd.pivot_table(
        df,
        index='Select the Name of Asha',
        columns='Month',
        values='Select the Participant Unique Code',
        aggfunc='count',
        fill_value=0
    )

    # Sort months correctly
    month_order = df[['Month','Month_num']].drop_duplicates().sort_values('Month_num')['Month']
    table1 = table1.reindex(columns=month_order)

    st.dataframe(table1)

    # =========================
    # TABLE 2 : DUPLICATE COUNT
    # =========================
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

    # =========================
    # TABLE 3 : DUPLICATE LIST
    # =========================
    st.subheader("Table 3: Actual Duplicate Participant List")

    asha_list = dup['Select the Name of Asha'].unique()

    selected_asha = st.selectbox("Select ASHA", asha_list)

    table3 = dup[dup['Select the Name of Asha'] == selected_asha][
        ['Select the Name of Asha',
         'Select the Participant Unique Code',
         '_submission_time']
    ]

    st.dataframe(table3)
