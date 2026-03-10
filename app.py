import streamlit as st
import pandas as pd
from koboextractor import KoboExtractor

st.title("ASHA Form Submission Dashboard")

my_token = "23801d339dd6d16509a79250731f126401d5f7a3"
form_id = "afWux6DQFqmZrEpK54BobD"
kobo_base_url = "https://kobo.humanitarianresponse.info/api/v2"


# -------------------- Refresh Data --------------------
if st.button("🔄 Refresh Data"):
    kobo = KoboExtractor(my_token, kobo_base_url)
    # Fetch all data (increase limit)
    data = kobo.get_data(form_id, params={"limit": 20000}) 

    df = pd.json_normalize(data['results'])

    # Clean column names
    df.columns = df.columns.str.split('/').str[-1]

    # Convert submission time (handle "Jan 27, 2026 1:05 PM" format)
    df['_submission_time'] = pd.to_datetime(df['_submission_time'], errors='coerce')

    # Extract month name
    df['month'] = df['_submission_time'].dt.month_name()

    st.session_state["df"] = df

# -------------------- If data loaded --------------------
if "df" in st.session_state:

    df = st.session_state["df"]

    # -------------------- MONTH FILTER (TABLE 1 ONLY) --------------------
    st.sidebar.header("Month Filter")

    months = ["Overall", "January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    selected_month = st.sidebar.selectbox("Select Month", months)

    if selected_month == "Overall":
        df_month = df
    else:
        df_month = df[df["month"] == selected_month]

    # -------------------- TABLE 1 --------------------
    st.subheader("Total Forms by ASHA")

    total_forms = (
        df_month.groupby("asha")
        .size()
        .reset_index(name="Forms Filled")
    )

    st.dataframe(total_forms, use_container_width=True)

    # -------------------- ASHA FILTER (TABLE 2 & 3) --------------------
    st.sidebar.header("ASHA Filter")

    selected_asha = st.sidebar.selectbox(
        "Select ASHA",
        sorted(df["asha"].dropna().unique())
    )

    df_asha = df[df["asha"] == selected_asha]

    # -------------------- DUPLICATES --------------------
    dup = df_asha[df_asha["Paticipant"].duplicated(keep=False)]

    dup_list = (
        dup.groupby("Paticipant")
        .size()
        .reset_index(name="Duplicate Count")
    )

    # -------------------- TABLE 2: Duplicate Summary --------------------
    st.subheader("Duplicate Summary")

    summary = pd.DataFrame({
        "ASHA": [selected_asha],
        "Unique Duplicate Participants": [dup["Paticipant"].nunique()],
        "Total Duplicate Entries": [dup.shape[0]]
    })

    st.dataframe(summary, use_container_width=True)

    # -------------------- TABLE 3: Actual Duplicate List --------------------
    st.subheader("Actual Duplicate Participant List")

    if dup_list.empty:
        st.write("No duplicate participants for this ASHA.")
    else:
        st.dataframe(dup_list, use_container_width=True)

else:
    st.info("Click 🔄 Refresh Data to load KoBo data")






