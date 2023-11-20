import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from io import BytesIO

# Function to get shipment info from TNT website
def get_shipment_info(ship_num):
    url = f'https://www.tnt.com/express/es_es/site/herramientas-envio/seguimiento.html?searchType=con&cons={ship_num}'
    chrome_service = ChromeService(executable_path='/path/to/chromedriver')
    driver = webdriver.Chrome(service=chrome_service)

    driver.get(url)
    driver.implicitly_wait(5)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    shipment_number = soup.select_one('dl:-soup-contains("Número de envío") dd').get_text(strip=True)
    client_reference = soup.select_one('div.__c-shipment__reference dl dd:nth-child(4)').get_text(strip=True)

    if not client_reference.startswith("DSD/"):
        driver.quit()
        return None

    tnt_status_element = soup.select_one('span.sham-shipment-status-tnt__label')
    tnt_status = tnt_status_element.get_text(strip=True) if tnt_status_element else None

    shipment_origin_date_element = soup.select_one('div.sham-shipment-origin-date')
    shipment_origin_date = shipment_origin_date_element.get_text(strip=True) if shipment_origin_date_element else None

    last_update = soup.select_one('td.__c-shipment-history__date').get_text(strip=True)
    action_element = soup.select_one('td.__c-shipment-history__status')
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

# Function to process uploaded Excel file
def process_excel_file(uploaded_file):
    shipment_data = pd.read_excel(uploaded_file)

    shipment_to_query = shipment_data[(shipment_data["Carrier"] == "TNT") & (shipment_data["Status"] != "DELIVERED")][["LOGIS ID", "Carrier", "T&T reference", "Status"]]

    shipment_in_transit = len(shipment_to_query[shipment_to_query["Status"] == "IN TRANSIT"])
    shipment_exception = len(shipment_to_query[shipment_to_query["Status"] == "EXCEPTION"])
    print(f"Previous report: \n- {shipment_in_transit} IN TRANSIT \n- {shipment_exception} EXCEPTION.")

    shipment_to_query = shipment_to_query.head(5)
    unique_references = set(shipment_to_query['T&T reference'])

    results = []

    for reference in unique_references:
        result = get_shipment_info(reference)
        
        if result is not None:
            results.append(result)

    df = pd.DataFrame(results)

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

    df['Shipment Origin Date'] = df['Shipment Origin Date'].replace(month_mapping, regex=True).apply(
        lambda x: datetime.strptime(x, "%d de %B de %Y").strftime("%d/%m/%Y")
    )

    df['Shipment Origin Date'] = pd.to_datetime(df['Shipment Origin Date'], format="%d/%m/%Y")
    df['Last Update'] = pd.to_datetime(df['Last Update'], format="%d/%m/%y %H:%M", errors='coerce')

    df['Processing Days'] = None

    for index, row in df.iterrows():
        if row['TNT Status'] != "Entregado" or row['TNT Status'] != "Delivered":
            current_date = datetime.now().replace(microsecond=0)
            processing_time = current_date - row['Shipment Origin Date']
        else:
            processing_time = row['Last Update'] - row['Shipment Origin Date']

        days, seconds = processing_time.days, processing_time.seconds
        formatted_processing_time = timedelta(days=days, seconds=seconds)

        df.at[index, 'Processing Days'] = formatted_processing_time

    df['Last Update'] = df['Last Update'].dt.strftime('%d/%m/%y %H:%M')
    df['Processing Days'] = df['Processing Days'].astype(str).str.extract(r'(\d+ days)').squeeze()

    df['Shipment Origin Date'] = df['Shipment Origin Date'].dt.strftime('%d/%m/%y')

    df = df[['Shipment Number', 'Client Reference', 'TNT Status', 'Shipment Origin Date', 'Processing Days', 'Last Update', 'Last Location', 'Last Action']]

    st.write("Processed Data:")
    st.write(df)

    excel_file = BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl')
    excel_file.seek(0)

    st.download_button(
        label="Download Processed Data",
        data=excel_file,
        file_name="Processed_Data.xlsx",
        key="download_button"
    )

# Define a main function
def main():
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file is not None:
        process_excel_file(uploaded_file)

# Check if the script is being run as the main module
if __name__ == "__main__":
    main()
