"""
Functions:
- extract_and_create_urls

"""




def extract_and_create_urls(excel_tests_file_path):
    """
    Read and extract shipment data from the Tests Excel file, create a list of unique shipment numbers,
    and group them in chunks of 30 to create the URL.

    Args:
    - excel_tests_file_path (str): Path to the Tests Excel file.

    Returns:
    - list: List of URLs to be scraped.
    """
    import pandas as pd
    from IPython.display import display, Markdown
    
    # Read and extract shipment data from the Excel file
    shipment_data = pd.read_excel(excel_tests_file_path)

    # Filter data: subset where Carrier = "TNT" & Status != DELIVERED
    shipment_to_query = shipment_data[(shipment_data["Carrier"] == "TNT") & (shipment_data["Status"] != "DELIVERED")][["LOGIS ID", "Carrier", "T&T reference", "Status"]]

    # Convert the "Status" column to uppercase
    shipment_to_query["Status"] = shipment_to_query["Status"].str.upper()

    # Display count of current "In Transit" and "Exception" shipments in the Excel file
    shipment_in_transit = len(shipment_to_query[shipment_to_query["Status"] == "IN TRANSIT"])
    shipment_exception = len(shipment_to_query[shipment_to_query["Status"] == "EXCEPTION"])
    

    # Ensure each unique shipment is queried once by using set()
    unique_references = set(shipment_to_query['T&T reference'])

    # Print
    display(Markdown(f" --> In your Excel file there are **{len(unique_references)} unique shipment numbers** ({shipment_in_transit} 'In Transit' and {shipment_exception} 'Exception'). "))

    # Convert the set to a list
    unique_references_list = list(unique_references)

    # Convert all elements to strings and sort the list in ascending order
    sorted_references = sorted(map(str, unique_references_list))

    # Create chunks of up to 30 unique references
    chunked_references = [sorted_references[i:i + 30] for i in range(0, len(sorted_references), 30)]
    
    # Print
    #display(Markdown(f"Number of **URL** (up-to-30 shipment numbers groups) to be consulted: **{len(chunked_references)}**"))

    # Create an empty list to store the URL
    url_list = []

    # Iterate through the list and construct the URL
    for chunk in chunked_references:
        url = f"https://www.tnt.com/express/es_es/site/herramientas-envio/seguimiento.html?searchType=con&cons={','.join(map(str, chunk))}"
        url_list.append(url)
    
    # Linkable URLs to manually check them if needed
    display(Markdown(f"--> Chunked URLs to be consulted: **{len(chunked_references)}** "))
    
    #for i, url in enumerate(url_list, 1):
    #    display(f"{i}. {url}")
    
    # Return the list of URLs
    return url_list, unique_references

# Example usage:
# excel_tests_file_path = "./Shipment_Data/Testsinmacro.xlsx"
# url_list = extract_and_create_urls(excel_tests_file_path)
# (no need to display each URL separately; it will be printed as part of the function)
