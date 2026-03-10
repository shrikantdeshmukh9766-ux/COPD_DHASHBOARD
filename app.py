import streamlit as st
import pandas as pd
from koboextractor import KoboExtractor

st.title("ASHA Form Submission Dashboard")

my_token = "23801d339dd6d16509a79250731f126401d5f7a3"
form_id = "afWux6DQFqmZrEpK54BobD"
kobo_base_url = "https://kobo.humanitarianresponse.info/api/v2"


# -------- Refresh Data --------
if st.button("🔄 Refresh Data"):

    kobo = KoboExtractor(my_token, kobo_base_url)
    data = kobo.get_data(form_id)

    df = pd.json_normalize(data['results'])

    # keep only needed columns
    df = df[["asha","Paticipant","_submission_time"]]

    # convert time
    df["_submission_time"] = pd.to_datetime(df["_submission_time"])

    # create month column
    df["month"] = df["_submission_time"].dt.month_name()

    st.session_state["df"] = df


# -------- If Data Loaded --------
if "df" in st.session_state:

    df = st.session_state["df"]

    # -------- Month Filter --------
    st.sidebar.header("Month Filter")

    months = ["Overall"] + sorted(df["month"].dropna().unique())

    selected_month = st.sidebar.selectbox("Select Month", months)

    if selected_month == "Overall":
        df_month = df
    else:
        df_month = df[df["month"] == selected_month]


    # -------- Table 1 : Forms by ASHA --------
    st.subheader("Total Forms by ASHA")

    total_forms = (
        df_month.groupby("asha")
        .size()
        .reset_index(name="Forms Filled")
    )

    st.dataframe(total_forms, use_container_width=True)


    # -------- Table 2 : Duplicate Summary --------
    st.subheader("ASHA Wise Duplicate Participants")

    dup_all = df_month[df_month.duplicated(subset=["asha","Paticipant"], keep=False)]

    dup_summary = (
        dup_all.groupby("asha")["Paticipant"]
        .nunique()
        .reset_index(name="Duplicate Participants")
    )

    st.dataframe(dup_summary, use_container_width=True)


    # -------- ASHA Filter --------
    st.sidebar.header("ASHA Filter")

    selected_asha = st.sidebar.selectbox(
        "Select ASHA",
        sorted(df_month["asha"].dropna().unique())
    )

    df_asha = df_month[df_month["asha"] == selected_asha]


    # -------- Table 3 : Actual Duplicate List --------
    st.subheader("Actual Duplicate Participant List")

    dup = df_asha[df_asha["Paticipant"].duplicated(keep=False)]

    dup_list = (
        dup.groupby("Paticipant")
        .size()
        .reset_index(name="Duplicate Count")
    )

    st.dataframe(dup_list, use_container_width=True)


else:
    st.info("Click 🔄 Refresh Data to load KoBo data")

