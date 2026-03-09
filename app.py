import streamlit as st
import pandas as pd
from koboextractor import KoboExtractor

st.title("ASHA Form Submission Dashboard")

my_token = "23801d339dd6d16509a79250731f126401d5f7a3"
form_id = "afWux6DQFqmZrEpK54BobD"
kobo_base_url = "https://kobo.humanitarianresponse.info/api/v2"


# Refresh Data
if st.button("🔄 Refresh Data"):

    kobo = KoboExtractor(my_token, kobo_base_url)

    data = kobo.get_data(form_id)

    df = pd.json_normalize(data['results'])

    # Clean column names
    df.columns = df.columns.str.split('/').str[-1]

    st.session_state["df"] = df


# If data loaded
if "df" in st.session_state:

    df = st.session_state["df"]

    # -------- TABLE 1 --------
    st.subheader("Total Forms by ASHA")

    total_forms = (
        df.groupby("asha")
        .size()
        .reset_index(name="Forms Filled")
    )

    st.dataframe(total_forms, use_container_width=True)


    # -------- FILTER --------
    st.sidebar.header("Filter")

    selected_asha = st.sidebar.selectbox(
        "Select ASHA",
        sorted(df["asha"].dropna().unique())
    )

    df_asha = df[df["asha"] == selected_asha]


    # -------- DUPLICATES --------
    dup = df_asha[df_asha["Paticipant"].duplicated(keep=False)]

    dup_list = (
        dup.groupby("Paticipant")
        .size()
        .reset_index(name="Duplicate Count")
    )


    # -------- SUMMARY --------
    st.subheader("Duplicate Summary")

    summary = pd.DataFrame({
        "ASHA":[selected_asha],
        "Duplicate Participants":[dup["Paticipant"].nunique()]
    })

    st.dataframe(summary, use_container_width=True)


    # -------- DUPLICATE LIST --------
    st.subheader("Actual Duplicate Participant List")

    st.dataframe(dup_list, use_container_width=True)


else:
    st.info("Click 🔄 Refresh Data to load KoBo data")

