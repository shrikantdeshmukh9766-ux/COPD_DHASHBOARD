import streamlit as st
import pandas as pd
from koboextractor import KoboExtractor

st.title("ASHA Form Submission Dashboard")

# Kobo credentials

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

