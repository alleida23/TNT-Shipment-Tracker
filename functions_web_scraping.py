"""

Functions:
- scrape_structure_from_urls
- scrape_shipment_data
- review_structure_scraped

"""


def scrape_structure_from_urls(url_list, chromedriver_path):
    """
    Scrapes data from a list of URLs using Selenium and BeautifulSoup.

    Args:
    - url_list (list): List of URLs to scrape.
    - chromedriver_path (str): Path to the ChromeDriver executable.

    Returns:
    - list: List of BeautifulSoup objects representing scraped data.
    """
    
    from selenium import webdriver
    from bs4 import BeautifulSoup
    from IPython.display import Markdown, display
    import time
    
    # Empty list to store the divs retrieved
    all_shipment_divs = []
    
    # Start the timer
    start_time = time.time()

    for url in url_list:
        # Set up ChromeOptions for headless mode
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')

        # Set up ChromeDriver
        chrome_service = webdriver.ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        # Set up ChromeDriver - Bernat
        #driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)

        
        # Load the webpage
        driver.get(url)
        driver.implicitly_wait(8)

        # Extract page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Select shipment divs based on the HTML structure of the webpage
        shipment_divs = soup.select('body > div.contentPageFullWidth.newBase.page.basicpage > div:nth-child(1) > div > pb-root > div > div > div > pb-track-trace > pb-search-results > div.__u-mb--xl')

        # Extend the list of all shipment divs
        all_shipment_divs.extend(shipment_divs)

        # Close the browser window
        driver.quit()
    
    # Stop the timer
    end_time = time.time()

    # Calculate and display the elapsed time
    elapsed_time = end_time - start_time
    display(Markdown(f"--> Elapsed time scraping data: **{elapsed_time:.2f} seconds**"))
    
    return all_shipment_divs

# Example usage:
# result_shipment_divs = scrape_data_from_urls(url_list, chromedriver_path)
# print(result_shipment_divs)





def scrape_shipment_data(all_shipment_divs):
    """
    Scrapes shipment data from the provided shipment divs and returns a DataFrame.

    Args:
    - all_shipment_divs (list): List of BeautifulSoup elements containing shipment details.

    Returns:
    - pd.DataFrame: DataFrame with scraped shipment data.
    """
    
    import pandas as pd
    
    all_results = []
    
    # From all url structure stored in all_shipment_divs, consult each one
    for shipment_divs in all_shipment_divs:
        # From each url structure, consult each "container" (each shipment) present
        for div in shipment_divs:
            # Extract client reference for each shipment
            client_reference_element = div.select_one('pb-shipment-reference div dl dd:nth-child(4)')
            client_reference = client_reference_element.get_text(strip=True) if client_reference_element else None

            if client_reference.startswith("DSD/"):
                # Extract shipment number for each shipment
                shipment_number_element = div.select_one('pb-shipment-reference div dl dd:nth-child(2)')
                shipment_number = shipment_number_element.get_text(strip=True) if shipment_number_element else None

                # TNT Status - Original
                #tnt_status_element = div.select_one('pb-shipment div div.__c-shipment__details sham-shipment-status-tnt > div > div.__c-shipment-status-tnt__summary > sham-step-label > span')
                #tnt_status = tnt_status_element.get_text(strip=True) if tnt_status_element else None

                # TNT Status
                tnt_status_element = div.select_one('pb-shipment div div.__c-shipment__details sham-shipment-status-tnt > div > div.__c-shipment-status-tnt__summary > sham-step-label')
                tnt_status = tnt_status_element.get_text(strip=True) if tnt_status_element else None

                # Extract Shipment Origin Date
                shipment_origin_date_element = div.select_one('pb-shipment div div.__c-shipment__details sham-shipment-addresses > div > div.__c-shipment-address.__c-shipment-address--from > div.__c-shipment-address__text > div:nth-child(3) > sham-shipment-origin-date')
                shipment_origin_date = shipment_origin_date_element.get_text(strip=True) if shipment_origin_date_element else None

                # Extract Shipment Destination
                shipment_destination_element = div.select_one('pb-shipment div div.__c-shipment__details sham-shipment-addresses > div > div.__c-shipment-address.__c-shipment-address--to > div:nth-child(2) > div.__c-heading.__c-heading--h4.__c-heading--bold.__u-mb--none')
                shipment_destination = shipment_destination_element.get_text(strip=True) if shipment_destination_element else None

                # Extract Last Update
                last_update_element = div.select_one('pb-shipment div div.__c-shipment__history.__u-print-only sham-shipment-history > table > tbody > tr:nth-child(1) > td.__c-shipment-history__date')
                last_update = last_update_element.get_text(strip=True) if last_update_element else None

                # Extract Last Location
                last_location_element = div.select_one('pb-shipment div div.__c-shipment__history.__u-print-only sham-shipment-history > table > tbody > tr:nth-child(1) > td.__u-hide--small-medium')
                last_location = last_location_element.get_text(strip=True) if last_location_element else None

                # Extract Last Action
                last_action_element = div.select_one('pb-shipment div div.__c-shipment__history sham-shipment-history > table > tbody > tr:nth-child(1) > td:nth-child(3)')
                last_action_text = last_action_element.get_text(strip=True) if last_action_element else None

                # Extract Action Message
                if "-" in last_action_text:
                    _, last_action = last_action_text.split("-", 1)
                else:
                    last_action = last_action_text

                # Check for warning badge and determine if it's a warning
                warning_badge_element = div.select_one('.__c-badge.__c-badge--warning')
                warning_badge = "EXCEPTION ALERT" if warning_badge_element else " "

                # Append extracted data
                all_results.append({
                    "Client Reference": client_reference,
                    "Shipment Number": shipment_number,
                    "TNT Status": tnt_status,
                    "Shipment Origin Date": shipment_origin_date,
                    "Shipment Destination": shipment_destination,
                    "Last Update": last_update,
                    "Last Location": last_location,
                    "Last Action": last_action,
                    "TNT Exception Notification": warning_badge
                })
            else:
                pass

    # Return the DataFrame
    df = pd.DataFrame(all_results)
    return df

# Example usage:
# df = scrape_shipment_data(all_shipment_divs)
# df.head()







def review_structure_scraped(unique_references, all_shipment_divs, url_list, chromedriver_path):
    """
    Review the structure of scraped data.

    Args:
    - unique_references (list): List of unique references to check.
    - all_shipment_divs (list): List of BeautifulSoup objects representing scraped data.
    - url_list (list): List of URLs to scrape.
    - chromedriver_path (str): Path to the ChromeDriver executable.

    Returns:
    None
    """
    
    from IPython.display import Markdown, display
    import time
    
    # Start the timer
    start_time = time.time()

    # Count the expected shipment numbers
    len_unique_ref = len(unique_references)

    # Print the expected number of shipments
    display(Markdown(f"--> Expected number of shipments: **{len_unique_ref}**"))

    # Display a message indicating that the extracted data is being reviewed or scraped
    display(Markdown("--> Reviewing extracted data..."))

    # Set the maximum number of attempts for scraping
    max_attempts = 5
    # Initialize the current attempt counter
    current_attempt = 1

    # Initialize found_shipments outside the loop
    found_shipments = 0

    # Continue scraping until all unique references are found in the shipment data or max attempts are reached
    while current_attempt <= max_attempts:
        # Count the number of found shipment numbers
        found_shipments = sum(any(str(ship_num) in str(div) for div in all_shipment_divs) for ship_num in unique_references)

        # Print a message indicating the attempt status
        if found_shipments == len_unique_ref:
            display(Markdown(f"--> Attempt {current_attempt} Succeeded: Found {found_shipments} out of {len_unique_ref} shipments."))
            break  # Exit the loop if all unique references are found
        else:
            display(Markdown(f"--> Attempt {current_attempt} Unsucceeded: Found {found_shipments} out of {len_unique_ref} shipments.\n**Scraping TNT web again...**"))

        # Scraping data again
        all_shipment_divs = scrape_structure_from_urls(url_list, chromedriver_path)

        # Increment the attempt counter
        current_attempt += 1
    
    
    
    # Check if all unique references are present in the scraped data
    if found_shipments == len_unique_ref:
        display(Markdown("**All shipment numbers in your Excel file are present in the scraped data.**"))
        # Continue with the next stage of your code
    else:
        display(Markdown("**Unsuccessful scrap. Review code, possible errors on the dataframe, or run it again.**"))
    
    # Stop the timer
    end_time = time.time()

    # Calculate and display the elapsed time
    elapsed_time = end_time - start_time
    display(Markdown(f"--> Elapsed time reviewing scraped data: **{elapsed_time:.2f} seconds**"))
    
    # Return the updated all_shipment_divs
    return all_shipment_divs


# Example usage:
# all_shipment_divs = review_structure_scraped(unique_references, all_shipment_divs, url_list, chromedriver_path)

