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
    
    # Empty list to store the divs retrieved
    all_shipment_divs = []

    for url in url_list:
        # Set up ChromeOptions for headless mode
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')

        # Set up ChromeDriver
        chrome_service = webdriver.ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

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

                # TNT Status
                tnt_status_element = div.select_one('pb-shipment div div.__c-shipment__details sham-shipment-status-tnt > div > div.__c-shipment-status-tnt__summary > sham-step-label > span')
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
