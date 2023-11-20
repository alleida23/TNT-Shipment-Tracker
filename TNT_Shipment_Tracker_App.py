import streamlit as st
import pandas as pd

# Add a title to the app
st.title("Excel File Uploader App")

# Add a button to upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

# Check if a file is uploaded
if uploaded_file is not None:
    # Read the Excel file into a DataFrame
    df = pd.read_excel(uploaded_file)

    # Display the DataFrame
    st.write("Uploaded DataFrame:", df)
