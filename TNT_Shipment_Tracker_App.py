import streamlit as st
import pandas as pd

def main():
    st.title("Excel File Uploader")

    uploaded_file = st.file_uploader("Upload your Excel File", type=["xlsx", "xls"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        if st.button("Get Last TNT Shipment Track Report"):
            # Filter data: subset where Carrier = "TNT" & Status != DELIVERED
            shipment_to_query = df[(df["Carrier"] == "TNT") & (df["Status"] != "DELIVERED")]

            # DELETE ONCE IT WORKS, NOW SUBSET OF 5
            shipment_to_query = shipment_to_query.head(5)

            # Ensure each unique shipment is queried once by using set()
            unique_references = set(shipment_to_query['T&T reference'])

            # Count total shipments
            total_shipments = len(shipment_to_query)

            # Count shipments with "IN TRANSIT" and "EXCEPTION" statuses
            shipment_in_transit = len(shipment_to_query[shipment_to_query["Status"] == "IN TRANSIT"])
            shipment_exception = len(shipment_to_query[shipment_to_query["Status"] == "EXCEPTION"])

            # Display the report
            st.write("Total Shipments:", total_shipments)
            st.write("IN TRANSIT:", shipment_in_transit)
            st.write("EXCEPTION:", shipment_exception)
            st.write("Unique References:", unique_references)

if __name__ == "__main__":
    main()
