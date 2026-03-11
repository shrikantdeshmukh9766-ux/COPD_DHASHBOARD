import streamlit as st
import pandas as pd
from koboextractor import KoboExtractor

st.title("ASHA Form Submission Dashboard")

# ---------------- Kobo Credentials ----------------
my_token = "23801d339dd6d16509a79250731f126401d5f7a3"
form_id = "afWux6DQFqmZrEpK54BobD"
kobo_base_url = "https://kobo.humanitarianresponse.info/api/v2"

# ---------------- Fetch Data ----------------
@st.cache_data
def load_data():
    kobo = KoboExtractor(my_token, kobo_base_url)
    data = kobo.get_data(form_id)
    df = pd.json_normalize(data)

    # keep only required columns
    df = df[['asha', 'Paticipant', '_submission_time']]

    # convert date
    df['_submission_time'] = pd.to_datetime(df['_submission_time'])

    # extract month
    df['month'] = df['_submission_time'].dt.to_period('M').astype(str)

    return df

df = load_data()

# ---------------- Table 1 ----------------
st.subheader("ASHA wise Month wise Form Count")

table1 = (
    df.groupby(['asha', 'month'])
    .size()
    .reset_index(name='forms_filled')
    .sort_values(['asha','month'])
)

st.dataframe(table1)

# ---------------- Pivot Table (Better View) ----------------
st.subheader("ASHA vs Month Summary")

pivot = pd.pivot_table(
    df,
    index="asha",
    columns="month",
    values="Paticipant",
    aggfunc="count",
    fill_value=0
)

st.dataframe(pivot)
