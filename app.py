import streamlit as st
import pandas as pd
from koboextractor import KoboExtractor

st.title("ASHA Form Submission Dashboard")


my_token = "23801d339dd6d16509a79250731f126401d5f7a3"
form_id = "afWux6DQFqmZrEpK54BobD"
kobo_base_url = "https://kobo.humanitarianresponse.info/api/v2"

# connect
kobo = KoboExtractor(my_token, kobo_base_url)

# download data
data = kobo.get_data(form_id)

# dataframe
df = pd.json_normalize(data['results'])

# clean column names
df.columns = df.columns.str.split('/').str[-1]

# remove label columns if present
df = df.loc[:, ~df.columns.str.contains('_label')]

# total forms submitted per ASHA
total_forms = df.groupby('asha').size().reset_index(name='total_forms')

# duplicate participant count per ASHA
dup_count = (
    df.groupby('asha')['Paticipant']
      .apply(lambda x: x.duplicated().sum())
      .reset_index(name='duplicate_participants')
)

# merge both results
result = pd.merge(total_forms, dup_count, on='asha')

print(result)
form_id = "afWux6DQFqmZrEpK54BobD"
kobo_base_url = "https://kobo.humanitarianresponse.info/api/v2"

# Connect Kobo
kobo = KoboExtractor(my_token, kobo_base_url)

# Load data
data = kobo.get_data(form_id)

df = pd.json_normalize(data['results'])

# Clean column names
df.columns = df.columns.str.split('/').str[-1]

# Convert submission time
df['_submission_time'] = pd.to_datetime(df['_submission_time'])

# Extract month
df['month'] = df['_submission_time'].dt.month_name()

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

# ASHA wise form count
asha_summary = (
    filtered_df.groupby('asha')
    .size()
    .reset_index(name='Forms Filled')
)

st.subheader("ASHA Wise Forms Filled")

st.dataframe(asha_summary, use_container_width=True)

# Chart
st.subheader("Forms Filled by ASHA")


st.bar_chart(asha_summary.set_index("asha"))

