"""

Functions:
- tnt_shipment_tracker

"""


def tnt_shipment_tracker(excel_tests_file_path, chromedriver_path, folder_save_to_excel_path):
    """
    Description: This function performs a series of operations, including data extraction, web scraping, DataFrame
    transformation, visualization, and consistency checks.

    Args:
    - excel_tests_file_path (str): Path to the Excel file containing tests data.
    - chromedriver_path (str): Path to the ChromeDriver executable.
    - folder_save_to_excel_path (str): Folder path to save the processed Excel file.

    Returns:
    - processed_df (DataFrame): DataFrame containing processed shipment data.
    """
    import pandas as pd
    import numpy as np
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options
    from bs4 import BeautifulSoup
    from datetime import datetime, timedelta
    import os
    from IPython.display import display, Markdown, HTML
    import matplotlib.pyplot as plt
    import seaborn as sns
    import time

    # Import customized functions from external files
    from functions_extract import extract_and_create_urls
    from functions_web_scraping import (
        scrape_structure_from_urls, scrape_shipment_data, review_structure_scraped
        )
    from functions_process_df import (
        convert_shipment_origin_date, process_last_update_column,
        calculate_processing_days, format_dates_and_processing_days,
        rearrange_columns_and_save_to_excel, global_df_transformation
        )
    
    # Start the timer
    start_time = time.time()
    
    display(Markdown(f"**Stage 1/4: Retrieving Data from Your Excel File...**"))
    
    # Call function extract_and_create_urls
    url_list, unique_references = extract_and_create_urls(excel_tests_file_path)
    
    display(Markdown(f"**Stage 1/4: Completed**"))
    display(Markdown(f"**Stage 2/4: Initiating Data Scraping Process...**"))
    
    # Call function scrape_structure_from_urls
    all_shipment_divs = scrape_structure_from_urls(url_list, chromedriver_path)
    
    display(Markdown(f"**Stage 2/4: Completed**"))
    display(Markdown(f"**Stage 3/4: Ensuring Data Retrieval for All Shipment Numbers....**"))
    
    # Apply function to scrap again if not all shipment numbers are found in all_shipment_divs
    all_shipment_divs = review_structure_scraped(unique_references, all_shipment_divs, url_list, chromedriver_path)
    
    display(Markdown(f"**Stage 3/4: Completed**"))
    display(Markdown(f"**Stage 4/4: Creating TNT Track Report...**"))
    
    # Call function scrape_shipment_data
    df = scrape_shipment_data(all_shipment_divs)

    # Print first output
    #display(df.head(), df.tail())
    #display(df.info())

    # Create a copy of the DataFrame to perform changes
    processed_df = df.copy()

    # Apply the function global_df_transformations
    processed_df, excel_file_path = global_df_transformation(processed_df, folder_save_to_excel_path)

    display(Markdown(f"**Stage 4/4: Completed**"))
    
    #display(processed_df.head(), processed_df.tail())
    
    # Stop the timer
    end_time = time.time()

    # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    display(Markdown(f"**Total elapsed time: {elapsed_time:.2f} seconds**"))
    
    #display(Markdown(f"TNT Track Report available in your local folder: {excel_file_path}"))

    
    return processed_df, url_list

# Example usage:
# result_processed_df = tnt_shipment_tracker('your_excel_file.xlsx', 'your_chromedriver_path', 'your_folder_path')
