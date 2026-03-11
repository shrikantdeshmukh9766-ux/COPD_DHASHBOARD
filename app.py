import streamlit as st
import pandas as pd

st.title("Excel Variable Viewer")

# Upload file
file = st.file_uploader("Upload Excel file", type=["xlsx", "xls", "csv"])

if file is not None:

    # Read file
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    st.success("File uploaded successfully")

    # Show dataset dimension
    st.write("Dataset shape:", df.shape)

    # Show column names
    st.subheader("Variable Names (Columns)")
    st.write(list(df.columns))

    # Show preview
    st.subheader("Data Preview")
    st.dataframe(df.head())
