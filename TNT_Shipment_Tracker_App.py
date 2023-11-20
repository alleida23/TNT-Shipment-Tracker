import streamlit as st
import pandas as pd

def main():
    st.title("Excel File Uploader")

    uploaded_file = st.file_uploader("Upload your Excel File", type=["xlsx", "xls"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write("Preview of the uploaded Excel file:")
        st.write(df)

        if st.button("Get Last TNT Shipment Track Report"):
            # Replace this with the actual code to generate the TNT Shipment Track Report
            st.write("Generating TNT Shipment Track Report...")

if __name__ == "__main__":
    main()
