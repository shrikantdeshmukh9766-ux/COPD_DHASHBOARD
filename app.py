import streamlit as st
import pandas as pd
from koboextractor import KoboExtractor

st.title("ASHA Form Submission Dashboard")

my_token = "23801d339dd6d16509a79250731f126401d5f7a3"
form_id = "afWux6DQFqmZrEpK54BobD"
kobo_base_url = "https://kobo.humanitarianresponse.info/api/v2"

# Refresh Button
if st.button("🔄 Refresh Data"):

    # Connect Kobo
    kobo = KoboExtractor(my_token, kobo_base_url)

    # Download data
    data = kobo.get_data(form_id)

    df = pd.json_normalize(data['results'])

    # Clean column names
    df.columns = df.columns.str.split('/').str[-1]

    # Remove label columns
    df = df.loc[:, ~df.columns.str.contains('_label')]

    # Convert submission time
    df['_submission_time'] = pd.to_datetime(df['_submission_time'])

    # Extract month
    df['month'] = df['_submission_time'].dt.month_name()

    # Save in session
    st.session_state["df"] = df


# If data loaded
if "df" in st.session_state:

    df = st.session_state["df"]

    # Sidebar filter
    st.sidebar.header("Filter")

    months = ["Overall"] + sorted(df['month'].dropna().unique())

    selected_month = st.sidebar.selectbox(
        "Select Month",
        months
    )

    # Apply filter
    if selected_month != "Overall":
        filtered_df = df[df['month'] == selected_month]
    else:
        filtered_df = df

    # ASHA total forms
    total_forms = (
        filtered_df.groupby('asha')
        .size()
        .reset_index(name='Forms Filled')
    )

    # Duplicate participants
    dup_count = (
        filtered_df.groupby('asha')['Paticipant']
        .apply(lambda x: x.duplicated().sum())
        .reset_index(name='Duplicate Participants')
    )

    # Merge results
    result = pd.merge(total_forms, dup_count, on='asha')

    st.subheader("ASHA Summary")

    st.dataframe(result, use_container_width=True)

    st.subheader("Forms Filled by ASHA")

    st.bar_chart(total_forms.set_index("asha"))

else:

    st.info("Click 🔄 Refresh Data to load KoBo data")


st.bar_chart(asha_summary.set_index("asha"))


