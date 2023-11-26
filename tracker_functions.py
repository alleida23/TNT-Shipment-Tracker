import pandas as pd
from datetime import datetime, timedelta

def convert_shipment_origin_date(dataframe):
    """
    Convert 'Shipment Origin Date' to the desired format.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame containing shipment data.

    Returns:
    - pd.DataFrame: DataFrame with 'Shipment Origin Date' in the desired format.
    """
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

    # Check if 'Shipment Origin Date' is already in the desired format
    if pd.api.types.is_datetime64_ns_dtype(dataframe['Shipment Origin Date']):
        return dataframe
    else:
        # Apply the conversion to the 'Shipment Origin Date' column
        dataframe['Shipment Origin Date'] = dataframe['Shipment Origin Date'].replace(month_mapping, regex=True).apply(
            lambda x: datetime.strptime(x, "%d de %B de %Y").strftime("%d/%m/%y")
        )
        dataframe['Shipment Origin Date'] = pd.to_datetime(dataframe['Shipment Origin Date'], format="%d/%m/%y", errors='coerce')

    return dataframe



def convert_last_update(dataframe):
    """
    Convert 'Last Update' to the desired format.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame containing shipment data.

    Returns:
    - pd.DataFrame: DataFrame with 'Last Update' in the desired format.
    """
    dataframe['Last Update'] = pd.to_datetime(dataframe['Last Update'], format="%d/%m/%y %H:%M", errors='coerce')
    dataframe['Last Update'] = dataframe['Last Update'].dt.strftime('%Y-%m-%d')

    return dataframe



def calculate_processing_days(dataframe):
    current_date = datetime.now().replace(microsecond=0)

    # Create a new column 'Processing Days'
    dataframe['Processing Days'] = None

    # Iterate through each row
    for index, row in dataframe.iterrows():
        if pd.notna(row['Last Update']) and pd.notna(row['Shipment Origin Date']):
            try:
                last_update = pd.to_datetime(row['Last Update'], errors='coerce')
                shipment_origin_date = pd.to_datetime(row['Shipment Origin Date'], errors='coerce')
            except Exception as e:
                print(f"Error converting dates at index {index}: {e}")
                continue

            if row['TNT Status'] != "Entregado" and row['TNT Exception Notification'] != "EXCEPTION ALERT":
                # Calculate processing time for non-delivered shipments
                processing_time = current_date - shipment_origin_date
            else:
                # For delivered shipments, use 'Last Update'
                processing_time = last_update - shipment_origin_date

            # Access the 'days' attribute
            processing_days = processing_time.days

            # Assign the numerical processing days to the 'Processing Days' column
            dataframe.at[index, 'Processing Days'] = processing_days
        else:
            # Handle missing values or invalid dates
            dataframe.at[index, 'Processing Days'] = None

    return dataframe



import pandas as pd

def format_rearrange_columns(dataframe):
    """
    Format 'Last Update', 'Processing Days', and 'Shipment Origin Date' columns
    to the desired format and rearrange DataFrame columns.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame containing shipment data.

    Returns:
    - pd.DataFrame: DataFrame with formatted and rearranged columns.
    """
    # Format 'Last Update' and 'Processing Days' columns
    dataframe['Last Update'] = pd.to_datetime(dataframe['Last Update']).dt.strftime('%d/%m/%y %H:%M')
    dataframe['Processing Days'] = dataframe['Processing Days'].astype(str).str.extract(r'(\d+)').astype(float)

    # Format 'Shipment Origin Date' column
    dataframe['Shipment Origin Date'] = pd.to_datetime(dataframe['Shipment Origin Date']).dt.strftime('%d/%m/%y')

    # Rearrange DataFrame columns in the desired order
    dataframe = dataframe[['Client Reference', 'Shipment Number', 'TNT Status',
                           'Shipment Origin Date', 'Shipment Destination',
                           'Processing Days', 'Last Update', 'Last Location',
                           'Last Action', 'TNT Exception Notification']]

    return dataframe





def save_to_excel(dataframe, folder_path="./TNT Track Reports"):
    """
    Save DataFrame to an Excel file with a formatted file name.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame containing shipment data.
    - folder_path (str): Folder path for saving the file. Default is "./TNT Track Reports".

    Returns:
    - str: Full path of the saved Excel file.
    """
    import os
    from datetime import datetime

    current_datetime = datetime.now().strftime("%d-%m-%Y %H_%M_%S")
    excel_filename = f"TNT Track Report {current_datetime}.xlsx"

    # Create the full path for saving the file
    full_path = os.path.join(folder_path, excel_filename)

    # Save the DataFrame to Excel
    dataframe.to_excel(full_path, index=False)

    return full_path



def process_shipment_data(dataframe):
    """
    Process shipment data using a sequence of functions.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame containing shipment data.

    Returns:
    - pd.DataFrame: Processed DataFrame with all transformations applied.
    """
    # Step 1: Convert 'Shipment Origin Date'
    dataframe = convert_shipment_origin_date(dataframe)

    # Step 2: Convert 'Last Update'
    dataframe = convert_last_update(dataframe)

    # Step 3: Calculate processing days
    dataframe = calculate_processing_days(dataframe)

    # Step 4: Format date columns and rearrange them
    dataframe = format_rearrange_columns(dataframe)

    # Step 6: Save DataFrame into an Excel file
    dataframe = save_to_excel(dataframe)

    return dataframe

# Example usage:
# df = process_shipment_data(df)
# file_path = save_to_excel(df)
