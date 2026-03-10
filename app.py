import streamlit as st
import pandas as pd
from koboextractor import KoboExtractor

st.title("ASHA Form Submission Dashboard")


my_token = "23801d339dd6d16509a79250731f126401d5f7a3"
form_id = "afWux6DQFqmZrEpK54BobD"
kobo_base_url = "https://kobo.humanitarianresponse.info/api/v2"


# ---------------- REFRESH DATA ----------------
if st.button("🔄 Refresh Data"):

    kobo = KoboExtractor(my_token, kobo_base_url)
    data = kobo.get_data(form_id)

    df = pd.json_normalize(data['results'])

    # Clean column names
    df.columns = df.columns.str.split('/').str[-1]

    # Convert submission time
    df['_submission_time'] = pd.to_datetime(df['_submission_time'])

    # Extract month
    df['month'] = df['_submission_time'].dt.month_name()

    st.session_state["df"] = df


# ---------------- IF DATA LOADED ----------------
if "df" in st.session_state:

    df = st.session_state["df"]

    # ---------------- MONTH FILTER ----------------
    st.sidebar.header("Month Filter")

    month_order = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]

    months = ["Overall"] + [m for m in month_order if m in df["month"].unique()]

    selected_month = st.sidebar.selectbox(
        "Select Month",
        months
    )

    if selected_month == "Overall":
        df_month = df
    else:
        df_month = df[df["month"] == selected_month]


    # ---------------- TABLE 1 ----------------
    st.subheader("Total Forms by ASHA")

    total_forms = (
        df_month.groupby("asha")
        .size()
        .reset_index(name="Forms Filled")
        .sort_values("Forms Filled", ascending=False)
    )

    st.dataframe(total_forms, use_container_width=True)


    # ---------------- TABLE 2 ----------------
    st.subheader("ASHA Wise Duplicate Participants")

    dup_all = df_month[df_month.duplicated(subset=["asha","Paticipant"], keep=False)]

    dup_summary = (
        dup_all.groupby("asha")["Paticipant"]
        .nunique()
        .reset_index(name="Duplicate Participants")
        .sort_values("Duplicate Participants", ascending=False)
    )

    st.dataframe(dup_summary, use_container_width=True)


    # ---------------- ASHA FILTER ----------------
    st.sidebar.header("ASHA Filter")

    selected_asha = st.sidebar.selectbox(
        "Select ASHA",
        sorted(df_month["asha"].dropna().unique())
    )

    df_asha = df_month[df_month["asha"] == selected_asha]


    # ---------------- DUPLICATE LIST ----------------
    dup = df_asha[df_asha["Paticipant"].duplicated(keep=False)]

    dup_list = (
        dup.groupby("Paticipant")
        .size()
        .reset_index(name="Duplicate Count")
        .sort_values("Duplicate Count", ascending=False)
    )


    # ---------------- TABLE 3 ----------------
    st.subheader("Actual Duplicate Participant List")

    st.dataframe(dup_list, use_container_width=True)


else:
    st.info("Click 🔄 Refresh Data to load KoBo data")

