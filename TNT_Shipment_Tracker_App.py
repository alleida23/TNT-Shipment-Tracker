import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

# Function to get shipment info from TNT website
def get_shipment_info(ship_num):
    # Construct the URL with a single shipment number
    url = f'https://www.tnt.com/express/es_es/site/herramientas-envio/seguimiento.html?searchType=con&cons={ship_num}'

    # Set up the ChromeDriver (replace '/Users/albertlleidaestival/Downloads/chromedriver-mac-arm64/chromedriver' with the actual path)
    chrome_service = ChromeService(executable_path='/Users/albertlleidaestival/Downloads/chromedriver-mac-arm64/chromedriver')
    driver = webdriver.Chrome(service=chrome_service)

    # Load the page
    driver.get(url)

    # Wait for a few seconds to allow dynamic content to load (you may need to adjust the wait time)
    driver.implicitly_wait(5)

    # Get the page source using Selenium
    page_source = driver.page_source

    # Use BeautifulSoup to parse the page source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract information as before
    
    ## Shipment Number
    shipment_number = soup.select_one('dl:-soup-contains("Número de envío") dd').get_text(strip=True)
    
    ## Client Reference
    client_reference = soup.select_one('div.__c-shipment__reference dl dd:nth-child(4)').get_text(strip=True)
    
    # Return None if the client reference doesn't start with "DSD/"
    if not client_reference.startswith("DSD/"):
        driver.quit()
        return None
    
    # TNT Status
    tnt_status_element = soup.select_one('body > div.contentPageFullWidth.newBase.page.basicpage > div:nth-child(1) > div > pb-root > div > div > div > pb-track-trace > pb-search-results > div:nth-child(3) > pb-shipment > div > div.__c-shipment__details > sham-shipment-status > sham-shipment-status-tnt > div > div.__c-shipment-status-tnt__summary > sham-step-label > span')
    tnt_status = tnt_status_element.get_text(strip=True) if tnt_status_element else None

    # From (Location&Time)
   # from_address = soup.select_one('div.__c-shipment-address--from .__c-shipment-address__text .__c-heading.__c-heading--h4.__c-heading--bold.__u-mb--none').get_text(strip=True)
    shipment_origin_date_element = soup.select_one('div.__c-shipment-address--from div.__c-shipment-address__text div:nth-child(3) sham-shipment-origin-date')
    shipment_origin_date = shipment_origin_date_element.get_text(strip=True) if shipment_origin_date_element else None
    
    ## To (Location&Time)
    #to_address_element = soup.select_one('div.__c-shipment-address--to div.__c-shipment-address__text div.__c-heading.__c-heading--h4.__c-heading--bold.__u-mb--none')
    #to_address = to_address_element.get_text(strip=True) if to_address_element else None
    #shipment_destination_date_element = soup.select_one('div.__c-shipment-address--to div.__c-shipment-address__text div:nth-child(3) sham-shipment-destination-date span span.__u-hide--large.__u-screen-only')
    #shipment_destination_date = shipment_destination_date_element.get_text(strip=True) if shipment_destination_date_element else None
    
    ## Last history (Location&Time)
    last_update = soup.select_one('div.__c-shipment__history sham-shipment-history table tbody tr:nth-child(1) td.__c-shipment-history__date').get_text(strip=True)
    action_element = soup.select_one('div.__c-shipment__history sham-shipment-history table tbody tr:nth-child(1) td:nth-child(3)')
    action_element = action_element.get_text(strip=True) if action_element else None

    # Split Location - Action if the dash is present
    if "-" in action_element:
        last_location, last_action = action_element.split("-", 1)
    else:
        last_location = last_action = None

    # Close the browser
    driver.quit()

    # Return a dictionary with the extracted information
    return {
        "Shipment Number": shipment_number,
        "Client Reference": client_reference,
        "TNT Status": tnt_status,
        #"From Address": from_address,
        "Shipment Origin Date": shipment_origin_date,
        #"To Address": to_address,
        #"Shipment Destination Date": shipment_destination_date,
        "Last Update": last_update,
        "Last Location": last_location,
        "Last Action": last_action
    }

# Function to process uploaded Excel file
def process_excel_file(uploaded_file):
    # Read uploaded Excel file
    shipment_data = pd.read_excel(uploaded_file)

    # Filter data: subset where Carrier = "TNT" & Status != DELIVERED
    shipment_to_query = shipment_data[(shipment_data["Carrier"] == "TNT")&(shipment_data["Status"] != "DELIVERED")][["LOGIS ID", "Carrier", "T&T reference", "Status"]]

    # Print count of current "In Transit" and "Exception" shipments in your Excel File
    shipment_in_transit = len(shipment_to_query[shipment_to_query["Status"] == "IN TRANSIT"])
    shipment_exception = len(shipment_to_query[shipment_to_query["Status"] == "EXCEPTION"])
    print(f"Previous report: \n- {shipment_in_transit} IN TRANSIT \n- {shipment_exception} EXCEPTION.")

    # DELETE ONCE IT WORKS, NOW SUBSET OF 5
    shipment_to_query = shipment_to_query[0:5]

    # Ensure each unique shipment is queried once by using set()
    unique_references = set(shipment_to_query['T&T reference'])

    """ Extract data from TNT url. As it is now, it will make requests one shipment number at a time"""

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
    df = pd.DataFrame(results)

    """Format text date to numerical date for Shipment Origin Date"""

    # Mapping of Spanish month names to English month names
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

    # Apply the conversion to the 'Shipment Origin Date' column
    df['Shipment Origin Date'] = df['Shipment Origin Date'].replace(month_mapping, regex=True).apply(
        lambda x: datetime.strptime(x, "%d de %B de %Y").strftime("%d/%m/%Y")
    )

    """ Calculate the days the shipment is being processed by TNT """

    # Change format
    df['Shipment Origin Date'] = pd.to_datetime(df['Shipment Origin Date'], format="%d/%m/%Y")
    df['Last Update'] = pd.to_datetime(df['Last Update'], format="%d/%m/%y %H:%M", errors='coerce')

    # Create a new column 'Processing Days'
    df['Processing Days'] = None

    # Iterate through each row
    for index, row in df.iterrows():
        if row['TNT Status'] != "Entregado" or row['TNT Status'] != "Delivered" :
            # Calculate processing time for non-delivered shipments
            current_date = datetime.now().replace(microsecond=0)
            processing_time = current_date - row['Shipment Origin Date']
        else:
            # For delivered shipments, use 'Last Update'
            processing_time = row['Last Update'] - row['Shipment Origin Date']

        # Format processing time to display only days, months, and years
        days, seconds = processing_time.days, processing_time.seconds
        formatted_processing_time = timedelta(days=days, seconds=seconds)

        # Assign the formatted processing time to the 'Processing Days' column
        df.at[index, 'Processing Days'] = formatted_processing_time

    # Format 'Last Update' and 'Processing Days' to the desired format
    df['Last Update'] = df['Last Update'].dt.strftime('%d/%m/%y %H:%M')
    df['Processing Days'] = df['Processing Days'].astype(str).str.extract(r'(\d+ days)').squeeze()

    # Display the updated DataFrame with the desired date format and column name
    df['Shipment Origin Date'] = df['Shipment Origin Date'].dt.strftime('%d/%m/%y')

    # Rearrange DataFrame in the desired order
    df = df[['Shipment Number', 'Client Reference', 'TNT Status', 'Shipment Origin Date', 'Processing Days', 'Last Update', 'Last Location', 'Last Action']]

    """ Save the DataFrame to an Excel File"""

    # Format file name as "TNT Track Report + datetime"
    current_datetime = datetime.now().strftime("%d-%m-%Y %H_%M_%S")
    excel_filename = f"TNT Track Report {current_datetime}.xlsx"

    # Specify the folder path
    folder_path = "./TNT Track Reports"

    # Create the full path for saving the file
    full_path = os.path.join(folder_path, excel_filename)

    # Save the DataFrame to Excel
    df.to_excel(full_path, index=False)

    """ Display the DataFrame as an Output"""

    # Display the updated DataFrame
    st.write("Processed Data:")
    st.write(df)

    # Download button
    st.download_button(
        label="Download Processed Data",
        data=df.to_excel(index=False, engine='openpyxl'),
        file_name=excel_filename,
        key="download_button"
    )

if __name__ == "__main__":
    main()
