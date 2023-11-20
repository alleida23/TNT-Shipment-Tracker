import streamlit as st
import pandas as pd

# Add a title to the app
st.title("Excel File Uploader App")

# Add a button to upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

# Check if a file is uploaded
if uploaded_file is not None:
    # Read the Excel file into a DataFrame
    shipment_data = pd.read_excel(uploaded_file)

    # Display the DataFrame
    st.write("Uploaded DataFrame:", shipment_data)

    # Add a button to get the last shipment track report
    if st.button("Get the Last Shipment Track Report"):
        # Filter data: subset where Carrier = "TNT" & Status != DELIVERED
        shipment_to_query = shipment_data[(shipment_data["Carrier"] == "TNT") & (shipment_data["Status"] != "DELIVERED")][["LOGIS ID", "Carrier", "T&T reference", "Status"]]

        # Print count of current "In Transit" and "Exception" shipments in your Excel File
        shipment_in_transit = len(shipment_to_query[shipment_to_query["Status"] == "IN TRANSIT"])
        shipment_exception = len(shipment_to_query[shipment_to_query["Status"] == "EXCEPTION"])
        st.write(f"Previous report: \n- {shipment_in_transit} IN TRANSIT \n- {shipment_exception} EXCEPTION.")

        # Delete once it works, now a subset of 5
        shipment_to_query = shipment_to_query.head(5)

        # Ensure each unique shipment is queried once by using set()
        unique_references = set(shipment_to_query['T&T reference'])
