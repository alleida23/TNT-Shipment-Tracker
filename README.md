# TNT Shipment Tracker - Multiple Search
Created by Albert Lleida, November 2023

This project aims to track multiple shipments from TNT using web scraping techniques. It was born out of the need of an actual company whose workers were manually tracking hundreds of shipments on the TNT tracker page every day. The process involved searching for each shipment number to determine if the client reference belonged to their company. This project is an effort to automate and streamline that process, utilizing Selenium to retrieve data in chunks of 30 to make it less time-consuming.

The project includes a Jupyter Notebook (`TNT Shipment Tracker - Multiple Search (30).ipynb`) and several Python files (`functions_extract.py`, `functions_process_df.py`, `functions_web_scraping.py`, `functions_z_extra.py`) that contain various functions used in the project.

## Project Overview

The main steps of the project are as follows:

1. **Data Extraction from Original Excel File:**
   - Extract shipments from the original Excel file where Carrier is TNT and Status is not "DELIVERED."
   - Set a list of unique shipment numbers.
   - Group shipment numbers into chunks of 30 for batch processing.

2. **Web Scraping:**
   - Use Selenium and BeautifulSoup to scrape data for multiple shipments from the TNT web tracking page.
   - Check if the client reference starts with the pattern "DSD/" before retrieving data.

3. **Data Processing:**
   - Apply customized functions to change data types, create columns, calculate processing days, format days, etc.

4. **Data Analysis:**
   - Display the processed DataFrame.
   - Generate a bar plot of unique "Status" counts present in the DataFrame.

5. **Exception Handling:**
   - Display rows where an EXCEPTION ALERT is detected from the TNT web.
   - Build a single URL for one of these exceptional rows.

6. **Inconsistency Check:**
   - Check for inconsistencies between the length of the original DataFrame and the extracted information DataFrame.
   - Display rows that are present in the original but not in the extracted information.

## Files

- **TNT Shipment Tracker - Multiple Search (30).ipynb:** Main Jupyter Notebook containing the project code.
- **functions_extract.py:** Functions related to data extraction from the original Excel file.
- **functions_process_df.py:** Functions for processing and cleaning the extracted data.
- **functions_web_scraping.py:** Functions related to web scraping using Selenium and BeautifulSoup.
- **functions_z_extra.py:** Additional custom functions.

## Required Columns in Original Excel File

Ensure that your original Excel file contains the following columns:

- **Carrier:** Specifies the carrier (e.g., "TNT").
- **Status:** Represents the shipment status.
- **T&T reference:** Stands for "Track and Trace" reference, representing the shipment number.

## Requirements

- Python 3.x
- Jupyter Notebook
- Selenium
- BeautifulSoup
- Other required libraries (specified in the notebook)

## Usage

1. Open and run the Jupyter Notebook (`TNT Shipment Tracker - Multiple Search (30).ipynb`).
2. Ensure that the required Python packages are installed.
3. Follow the instructions in the notebook for batch processing and web scraping.

## License

This project is licensed under the [MIT License](LICENSE).
