# TNT Shipment Tracker - Multiple Search
Created by Albert Lleida, November 2023

This project aims to address the challenge of manually tracking hundreds of shipments from TNT faced by a company's workforce. Prior to automation, employees had to navigate the TNT tracker page daily, searching for each shipment number to identify if the client reference belonged to their company. This labor-intensive process prompted the creation of an automated solution.

## Project Objective

The primary goal of this project is to streamline the shipment tracking process through web scraping techniques. By leveraging Selenium, the project automates the retrieval of shipment data in chunks of 30 —the maximum allowed by the TNT tracker-, significantly reducing the time and effort required for tracking.

<p align="center">
  <img height="800" src="https://github.com/alleida23/TNT-Shipment-Tracker/assets/124719215/c1bc22e7-71c8-4e09-837d-010e64fe53b2" alt="TNT Shipment Tracker">
</p>

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
   - Display the processed DataFrame.
   - Generate a bar plot of unique "Status" counts present in the DataFrame.

4. **Exception Handling:**
   - Display rows where an EXCEPTION ALERT is detected from the TNT web.
   - Build a single URL for one of these exceptional rows.

5. **Inconsistency Check:**
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
3. Adjust the paths to: excel_tests_file_path, chromedriver_path and folder_save_to_excel_path.
4. Follow the instructions in the notebook for batch processing and web scraping.

## License

This project is licensed under the [MIT License](LICENSE).
