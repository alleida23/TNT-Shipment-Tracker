def convert_shipment_origin_date(dataframe):
    """
    Convert 'Shipment Origin Date' column to the desired format.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame containing shipment data.

    Returns:
    - pd.DataFrame: DataFrame with 'Shipment Origin Date' in the desired format.
    """
    
    import pandas as pd
    from datetime import datetime
    
    # Define a mapping for Spanish month names to English
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

# Example usage:
# df = convert_shipment_origin_date(df)
# df.head()



def process_last_update_column(dataframe):
    """
    Process 'Last Update' column in the DataFrame.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame containing shipment data.

    Returns:
    - pd.DataFrame: DataFrame with processed 'Last Update' column.
    """
    import pandas as pd
    
    # Convert 'Last Update' to datetime format
    dataframe['Last Update'] = pd.to_datetime(dataframe['Last Update'], format="%d/%m/%y %H:%M", errors='coerce')

    # Format 'Last Update' to YYYY-MM-DD
    dataframe['Last Update'] = dataframe['Last Update'].dt.strftime('%Y-%m-%d')

    return dataframe

# Example usage:
# df = process_last_update_column(df)
# df.head()



def calculate_processing_days(dataframe):
    """
    Calculate the processing days for each shipment and add a 'Processing Days' column.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame containing shipment data.

    Returns:
    - pd.DataFrame: DataFrame with the 'Processing Days' column added.
    """
    
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Create a new column 'Processing Days'
    dataframe['Processing Days'] = None

    # Iterate through each row
    for index, row in dataframe.iterrows():
        if row['TNT Status'] != "Entregado" and row['TNT Exception Notification'] != "EXCEPTION ALERT":
            # Calculate processing time for non-delivered shipments
            current_date = datetime.now().replace(microsecond=0)
            processing_time = current_date - row['Shipment Origin Date']
        else:
            # For delivered shipments, use 'Last Update'
            processing_time = pd.to_datetime(row['Last Update']) - row['Shipment Origin Date']

        # Format processing time to display only days, months, and years
        days, seconds = processing_time.days, processing_time.seconds
        formatted_processing_time = timedelta(days=days, seconds=seconds)

        # Assign the formatted processing time to the 'Processing Days' column
        dataframe.at[index, 'Processing Days'] = formatted_processing_time

    return dataframe

# Example usage:
# processed_df = calculate_processing_days(processed_df)



def format_dates_and_processing_days(dataframe):
    """
    Format 'Shipment Origin Date' and 'Last Update' columns as dd/mm/yy,
    and modify 'Processing Days' to only show the number of days.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame containing shipment data.

    Returns:
    - pd.DataFrame: DataFrame with formatted columns.
    """
    
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Format 'Shipment Origin Date' and 'Last Update' columns
    dataframe['Shipment Origin Date'] = dataframe['Shipment Origin Date'].dt.strftime('%d/%m/%y')
    dataframe['Last Update'] = pd.to_datetime(dataframe['Last Update']).dt.strftime('%d/%m/%y')

    # Modify 'Processing Days' column to only show the number of days
    dataframe['Processing Days'] = dataframe['Processing Days'].apply(lambda x: str(x).split(',')[0])

    return dataframe

# Example usage:
# processed_df = format_dates_and_processing_days(processed_df)



def rearrange_columns_and_save_to_excel(dataframe, folder_save_to_excel_path):
    """
    Rearrange DataFrame columns and save it to an Excel file.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame.
    - folder_save_to_excel_path (str): Folder path to save the Excel file.

    Returns:
    - pd.DataFrame: Rearranged DataFrame.
    - str: Full path of the saved Excel file.
    """
    
    import os
    import pandas as pd
    from datetime import datetime

    # Rearrange DataFrame columns
    dataframe = dataframe[['Client Reference', 'Shipment Number', 'TNT Status',
                           'Shipment Origin Date', 'Shipment Destination',
                           'Processing Days', 'Last Update', 'Last Location',
                           'Last Action', 'TNT Exception Notification']]

    # Get current date and time for creating a unique filename
    current_datetime = datetime.now().strftime("%d-%m-%Y %H_%M_%S")
    excel_filename = f"TNT Track Report {current_datetime}.xlsx"

    # Create the full path for saving the file
    full_path = os.path.join(folder_save_to_excel_path, excel_filename)

    # Save the DataFrame to Excel
    dataframe.to_excel(full_path, index=False)
    
    # Print path
    print(f"Excel file saved at: {full_path}")

    return dataframe, full_path

# Example usage:
# folder_save_to_excel_path = "/path/to/save/excel/files"
# processed_df, excel_file_path = rearrange_columns_and_save_to_excel(processed_df, folder_save_to_excel_path)
# print(f"Excel file saved at: {excel_file_path}")



def global_df_transformation(dataframe, folder_save_to_excel_path):
    """
    Perform the global processing of the input DataFrame.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame containing shipment data.
    - folder_save_to_excel_path (str): Folder path to save the Excel file.

    Returns:
    - pd.DataFrame: Processed and rearranged DataFrame.
    - str: Full path of the saved Excel file.
    """
    # Import libraries
    import pandas as pd
    from datetime import datetime, timedelta
    import os

    # Function 1: Convert 'Shipment Origin Date'
    dataframe = convert_shipment_origin_date(dataframe)

    # Function 2: Process 'Last Update' column
    dataframe = process_last_update_column(dataframe)

    # Function 3: Calculate processing days and add 'Processing Days' column
    dataframe = calculate_processing_days(dataframe)

    # Function 4: Format 'Shipment Origin Date', 'Last Update', and 'Processing Days'
    dataframe = format_dates_and_processing_days(dataframe)

    # Function 5: Rearrange columns and save to Excel
    processed_df, excel_file_path = rearrange_columns_and_save_to_excel(dataframe, folder_save_to_excel_path)

    print(f"Global processing completed. Excel file saved at: {excel_file_path}")

    return processed_df, excel_file_path

# Example usage:
# folder_save_to_excel_path = "/path/to/save/excel/files"
# processed_df, excel_file_path = global_df_transformation(df, folder_save_to_excel_path)

