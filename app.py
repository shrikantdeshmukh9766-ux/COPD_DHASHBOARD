import streamlit as st
import pandas as pd
from koboextractor import KoboExtractor

st.title("ASHA Form Submission Dashboard")

# Kobo credentials
my_token = "23801d339dd6d16509a79250731f126401d5f7a3"
form_id = "afWux6DQFqmZrEpK54BobD"
kobo_base_url = "https://kobo.humanitarianresponse.info/api/v2"

@st.cache_data
def load_data():
    kobo = KoboExtractor(my_token, kobo_base_url)
    data = kobo.get_data(form_id)
    df = pd.json_normalize(data)
    return df

df = load_data()

print(df)

