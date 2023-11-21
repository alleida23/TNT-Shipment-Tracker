# Import necessary libraries
import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

# Function to retrieve shipment information from TNT website
def get_shipment_info(ship_num):
    # Construct the URL with a single shipment number
    url = f'https://www.tnt.com/express/es_es/site/herramientas-envio/seguimiento.html?searchType=con&cons={ship_num}'

    # Set up the ChromeDriver (replace '/Users/albertlleidaestival/Downloads/chromedriver-mac-arm64/chromedriver' with the actual path)
    chrome_service = ChromeService(executable_path='/Users/albertlleidaestival/Downloads/chromedriver-mac-arm64/chromedriver')
    driver = webdriver.Chrome(options=chrome_service)

    # Load the page
    driver.get(url)

    # Wait for a few seconds to allow dynamic content to load (you may need to adjust the wait time)
    driver.implicitly_wait(5)

    # Get the page source using Selenium
    page_source = driver.page_source

    # Use BeautifulSoup to parse the page source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract information as before
    shipment_number = soup.select_one('dl:-soup-contains("Número de envío") dd').get_text(strip=True)
    client_reference = soup.select_one('div.__c-shipment__reference dl dd:nth-child(4)').get_text(strip=True)

    # Return None if the client reference doesn't start with "DSD/"
    if not client_reference.startswith("DSD/"):
        driver.quit()
        return None

    tnt_status_element = soup.select_one('body > div.contentPageFullWidth.newBase.page.basicpage > div:nth-child(1) > div > pb-root > div > div > div > pb-track-trace > pb-search-results > div:nth-child(3) > pb-shipment > div > div.__c-shipment__details > sham-shipment-status > sham-shipment-status-tnt > div > div.__c-shipment-status-tnt__summary > sham-step-label > span')
    tnt_status = tnt_status_element.get_text(strip=True) if tnt_status_element else None

    shipment_origin_date_element = soup.select_one('div.__c-shipment-address--from div.__c-shipment-address__text div:nth-child(3) sham-shipment-origin-date')
    shipment_origin_date = shipment_origin_date_element.get_text(strip=True) if shipment_origin_date_element else None

    last_update = soup.select_one('div.__c-shipment__history sham-shipment-history table tbody tr:nth-child(1) td.__c-shipment-history__date').get_text(strip=True)
    action_element = soup.select_one('div.__c-shipment__history sham-shipment-history table tbody tr:nth-child(1) td:nth-child(3)')
    action_element = action_element.get_text(strip=True) if action_element else None

    if "-" in action_element:
        last_location, last_action = action_element.split("-", 1)
    else:
        last_location = last_action = None

    driver.quit()

    return {
        "Shipment Number": shipment_number,
        "Client Reference": client_reference,
        "TNT Status": tnt_status,
        "Shipment Origin Date": shipment_origin_date,
        "Last Update": last_update,
        "Last Location": last_location,
        "Last Action": last_action
    }

# Main Streamlit app
def main():
    st.title("Excel File Uploader")

    # Upload Excel file
    uploaded_file = st.file_uploader("Upload your Excel File", type=["xlsx", "xls"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        # Button to trigger report generation
        if st.button("Get Last TNT Shipment Track Report"):
            # Filter data: subset where Carrier = "TNT" & Status != DELIVERED
            shipment_to_query = df[(df["Carrier"] == "TNT") & (df["Status"] != "DELIVERED")]
            # DELETE ONCE IT WORKS, NOW SUBSET OF 5
            shipment_to_query = shipment_to_query.head(5)

            # Ensure each unique shipment is queried once by using set()
            unique_references = set(shipment_to_query['T&T reference'])

            # Create an empty list to store the results
            results = []

            # Iterate through each unique reference
            for reference in unique_references:
                # Call the function with the individual reference
                result = get_shipment_info(reference)

                # Check if the result is not None before appending to the list
                if result is not None:
                    # Append the result to the list
                    results.append(result)

            # Create a DataFrame from the results
            df_results = pd.DataFrame(results)

            # Format text date to numerical date for Shipment Origin Date
            month_mapping = {
                'enero': 'January',
                'febrero': 'February',
                'marzo': 'March',
                'abril': 'April',
                'mayo': 'May',
                'junio': 'June',
                'julio': 'July',
                'agosto': 'August',
                'septiembre': 'September',
                'octubre': 'October',
                'noviembre': 'November',
                'diciembre': 'December'
            }
            df_results['Shipment Origin Date'] = df_results['Shipment Origin Date'].replace(month_mapping, regex=True).apply(
                lambda x: datetime.strptime(x, "%d de %B de %Y").strftime("%d/%m/%Y")
            )

            # Calculate the days the shipment is being processed by TNT
            df_results['Shipment Origin Date'] = pd.to_datetime(df_results['Shipment Origin Date'], format="%d/%m/%Y")
            df_results['Last Update'] = pd.to_datetime(df_results['Last Update'], format="%d/%m/%y %H:%M", errors='coerce')

            df_results['Processing Days'] = None

            for index, row in df_results.iterrows():
                if row['TNT Status'] not in ["Entregado", "Delivered"]:
                    current_date = datetime.now().replace(microsecond=0)
                    processing_time = current_date - row['Shipment Origin Date']
                else:
                    processing_time = row['Last Update'] - row['Shipment Origin Date']

                days, seconds = processing_time.days, processing_time.seconds
                formatted_processing_time = timedelta(days=days, seconds=seconds)

                df_results.at[index, 'Processing Days'] = formatted_processing_time

            df_results['Last Update'] = df_results['Last Update'].dt.strftime('%d/%m/%y %H:%M')
            df_results['Processing Days'] = df_results['Processing Days'].astype(str).str.extract(r'(\d+ days)').squeeze()
            df_results['Shipment Origin Date'] = df_results['Shipment Origin Date'].dt.strftime('%d/%m/%y')

            df_results = df_results[['Shipment Number', 'Client Reference', 'TNT Status', 'Shipment Origin Date', 'Processing Days', 'Last Update', 'Last Location', 'Last Action']]

            # Display the updated DataFrame with the desired date format and column name
            st.write("Shipment Track Report:")
            st.write(df_results)

            # Download Last Report button
            if st.button("Download Last Report"):
                # Format file name as "TNT Track Report + datetime"
                current_datetime = datetime.now().strftime("%d-%m-%Y %H_%M_%S")
                excel_filename = f"TNT Track Report {current_datetime}.xlsx"
                df_results.to_excel(excel_filename, index=False)
                st.success(f"Report downloaded as {excel_filename}")

if __name__ == "__main__":
    main()
