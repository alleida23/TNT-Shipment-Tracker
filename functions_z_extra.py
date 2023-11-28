"""

Functions:
- display_url_list
- display_exception_shipments
- plot_tnt_status_bar
- check_inconsistencies
- plot_counts_avg_shipment

"""



def display_url_list(url_list):
    """
    Display chunked URLs.

    Args:
    - url_list (list): Input list containing chunked URLs.

    Returns:
    - None
    """
    for i, url in enumerate(url_list, 1):
        display(f"{i}. {url}")




def display_exception_shipments(dataframe):
    """
    Display information about exception shipments and their URLs.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame containing shipment data.

    Returns:
    - None
    """
    from IPython.display import display, Markdown, HTML
    
    # Extract exception shipments
    exception_shipments = dataframe[dataframe['TNT Exception Notification'] != " "]

    # Display a markdown message
    display(Markdown(f"**{len(exception_shipments)} Exception Notification detected!**"))

    # Define a function to create the URL for each exception shipment
    def build_url(shipment_number):
        return f'https://www.tnt.com/express/es_es/site/herramientas-envio/seguimiento.html?searchType=con&cons={shipment_number}'

    # Apply the build_url function to create the 'URL' column in exception_shipments
    exception_shipments = exception_shipments.copy()  # Create a copy to avoid SettingWithCopyWarning
    exception_shipments.loc[:, 'URL'] = exception_shipments['Shipment Number'].apply(build_url)

    # Display the DataFrame with clickable "Link" text
    display(HTML(exception_shipments[['Shipment Number', 'TNT Exception Notification', 'URL']].to_html(escape=False, formatters={'URL': lambda x: f"<a href='{x}' target='_blank'>Link</a>"})))
    
    return exception_shipments

# Example usage:
# display_exception_shipments(processed_df)




def plot_tnt_status_bar(processed_df):
    """
    Create a horizontal bar plot of the number of shipments by TNT Status.

    Args:
    - processed_df (pd.DataFrame): Input DataFrame containing shipment data.

    Returns:
    - None
    """
    
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Set Seaborn dark theme
    sns.set_theme(style="darkgrid")
    
    # Define a color palette with different colors for each TNT Status
    colors = sns.color_palette("husl", len(processed_df['TNT Status'].unique()))

    # Create a bar plot
    plt.figure(figsize=(8, 4))
    status_counts = processed_df['TNT Status'].value_counts().sort_values(ascending=True)
    status_counts.plot(kind='barh', color=colors)

    # Add labels with the number of shipments on each bar
    for i, count in enumerate(status_counts):
        plt.text(count + 1, i, str(count), ha='left', va='center')

    plt.title('Number of Shipments by "TNT Status"')
    plt.xlabel('Number of Shipments')
    plt.ylabel('TNT Status')
    plt.show()

# Example usage:
# plot_horizontal_bar(processed_df)



def check_inconsistencies(excel_tests_file_path, df):
    """
    Check inconsistencies between the original Excel file and the extracted DataFrame.

    Parameters:
    - excel_tests_file_path (str): Path to the original Excel file.
    - df (pd.DataFrame): Extracted DataFrame.

    Returns:
    - pd.DataFrame: DataFrame containing rows with missing references.
    """
    
    import pandas as pd
    
    # Read the original Excel file
    original_excel = pd.read_excel(excel_tests_file_path)

    # Filter data in original_excel
    original_excel = original_excel[(original_excel["Carrier"] == "TNT") & (original_excel["Status"] != "DELIVERED")][["LOGIS ID", "Carrier", "T&T reference", "Status"]]

    # Extract missing references
    missing_references = original_excel[~original_excel['T&T reference'].isin(df['Shipment Number'])]['T&T reference']

    # Create an empty DataFrame to store rows from original_excel
    df_missing_references = pd.DataFrame(columns=original_excel.columns)

    # Iterate over each missing reference
    for row_value in missing_references:
        condition = original_excel['T&T reference'] == row_value
        original_row = original_excel.loc[condition]

        # Check if the row exists
        if not original_row.empty:
            df_missing_references = pd.concat([df_missing_references, original_row], ignore_index=True)
            
    # Print the comparison information
    print(f"Original Length: {len(original_excel)}")
    print(f"Extracted DataFrame Length: {len(df)}")
    print(f"Difference in Length: {len(original_excel) - len(df)}")

    # Display the DataFrame with missing references
    if not df_missing_references.empty:
        print("\nShipment numbers to check:")
        #print(df_missing_references)
    else:
        print("\nNo Missing Shipment numbers Found")

    return df_missing_references

# Example usage
#excel_tests_file_path = "path/to/your/excel/file.xlsx"
#df = pd.DataFrame(...)  # Replace ... with your actual DataFrame
#check_inconsistencies(excel_tests_file_path, df)




def plot_counts_avg_shipment(df, plot_type='TNT Status'):
    """
    Plot shipment-related data based on different categories.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing shipment data.
    - plot_type (str): Type of plot to generate ('TNT Status', 'Destination Country', 'Status and Country', 'Month').

    Returns:
    - None
    """

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Create a copy of the dataframe for plotting
    plotting_df = df.copy()

    # Convert 'Processing Days' to numeric
    plotting_df['Processing Days'] = pd.to_numeric(plotting_df['Processing Days'].str.extract('(\d+)')[0], errors='coerce')

    # Combine 'TNT Status' and 'TNT Exception Notification' to create a new category
    plotting_df['TNT Status Category'] = plotting_df.apply(lambda row: 'Exception Notification' if row['TNT Exception Notification'] == 'EXCEPTION ALERT' else row['TNT Status'], axis=1)

    # Assuming 'Shipment Destination' is a string column with values like "City, Country"
    plotting_df[['Destination City', 'Destination Country']] = plotting_df['Shipment Destination'].str.split(',', 1, expand=True)

    # Strip leading and trailing whitespaces from the columns
    plotting_df['Destination City'] = plotting_df['Destination City'].str.strip()
    plotting_df['Destination Country'] = plotting_df['Destination Country'].str.strip()

    # Convert 'Shipment Origin Date' to datetime
    plotting_df['Shipment Origin Date'] = pd.to_datetime(plotting_df['Shipment Origin Date'], errors='coerce')

    # Extract month
    plotting_df['Shipment Origin Month'] = plotting_df['Shipment Origin Date'].dt.month

    plotting_df = plotting_df[['TNT Status Category', 'Destination City', 'Destination Country', 'Shipment Origin Month', 'Processing Days']]

    if plot_type == 'TNT Status':
        # Plotting for TNT Status
        status_stats = plotting_df.groupby(['TNT Status Category'])['Processing Days'].agg(['count', 'mean']).round(2)
        status_stats = status_stats.sort_values(by='mean', ascending=False)
        status_stats = status_stats.rename(columns={'mean': 'Avg Processing Days', 'count': 'Shipment Count'})

        # Set Seaborn dark theme
        sns.set_theme(style="darkgrid")

        # Define a color palette with different colors for each TNT Status Category
        colors = sns.color_palette("bright", len(status_stats))

        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Plot the count of shipments on the left subplot
        sns.barplot(x='Shipment Count', y=status_stats.index, data=status_stats, palette=colors, alpha=0.7, ax=ax1)

        # Add labels with the number of shipments on each bar
        for i, p in enumerate(ax1.patches):
            ax1.annotate(str(int(p.get_width())), (p.get_width(), p.get_y() + p.get_height() / 2.), va='center', xytext=(5, 0), textcoords='offset points')

        # Plot average processing days on the right subplot
        sns.barplot(x=status_stats.index, y=status_stats['Avg Processing Days'], palette=colors, alpha=0.7, ax=ax2)

        # Add labels with the average processing days on each bar
        for i, p in enumerate(ax2.patches):
            ax2.annotate(f"{p.get_height():.2f} days", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 5), textcoords='offset points')

        # Adjust layout and labels
        fig.suptitle('TNT Status', y=1.05, fontsize=16)
        ax1.set_title('Number of Shipments by Status Category')
        ax1.set_xlabel('Count of Shipments')
        ax2.set_title('Average Processing Days by Status Category')
        ax2.set_ylabel('Average Processing Days')

        plt.tight_layout()
        plt.show()

    elif plot_type == 'Destination Country':
        # Assuming you have already calculated country_stats
        country_stats = plotting_df.groupby(['Destination Country'])['Processing Days'].agg(['count', 'mean']).round(2)
        country_stats = country_stats.sort_values(by='mean', ascending=False)
        country_stats = country_stats.rename(columns={'mean': 'Avg Processing Days', 'count': 'Shipment Count'})

        # Set Seaborn dark theme
        sns.set_theme(style="darkgrid")
        
        # Extract colors used for the donut chart
        donut_colors = sns.color_palette("Set2", n_colors=len(country_stats))

        if len(country_stats) > 1:  # Check if there is more than one country to plot
            # Create a figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

            # Plot the count of shipments as a donut chart on the left subplot with custom colors
            wedgeprops = {'edgecolor': 'black'}
            ax1.pie(country_stats['Shipment Count'], labels=country_stats.index, autopct='%1.1f%%', startangle=90, counterclock=False, wedgeprops=wedgeprops, pctdistance=0.85, colors=donut_colors)

            # Draw a white circle in the center to create the donut
            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            ax1.add_patch(centre_circle)

            # Define a custom color palette for the bar plot on the right subplot
            bar_colors = sns.color_palette("Set2", n_colors=len(country_stats))

            # Plot average processing days on the right subplot with different colors
            sns.barplot(x=country_stats.index, y=country_stats['Avg Processing Days'], palette=donut_colors, alpha=0.7, ax=ax2)

            # Add labels with the average processing days on each bar
            for i, p in enumerate(ax2.patches):
                ax2.annotate(f"{p.get_height():.2f} days", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 5), textcoords='offset points')

            plt.tight_layout()
            plt.show()

        else:
            # If there is only one country, display a single bar for the average processing days
            plt.figure(figsize=(8, 6))
            sns.barplot(x=country_stats.index, y=country_stats['Avg Processing Days'], palette=sns.color_palette("Set2", n_colors=len(country_stats)), alpha=0.7)
            plt.title('Average Processing Days by Country')
            plt.xlabel('Destination Country')
            plt.ylabel('Average Processing Days')

            plt.tight_layout()
            plt.show()

    elif plot_type == 'Status and Country':
        # Assuming you have already calculated status_country_stats
        status_country_stats = plotting_df.groupby(['TNT Status Category', 'Destination Country'])['Processing Days'].agg(['count', 'mean']).round(2)
        status_country_stats = status_country_stats.sort_values(by='mean', ascending=False)
        status_country_stats = status_country_stats.rename(columns={'mean': 'Avg Processing Days', 'count': 'Shipment Count'})

        # Display status_country_stats
        display(status_country_stats)

    elif plot_type == 'Month':
        # Assuming you have already calculated month_stats
        month_stats = plotting_df.groupby(['Shipment Origin Month'])['Processing Days'].agg(['count', 'mean']).round(2)
        month_stats = month_stats.rename(columns={'mean': 'Avg Processing Days', 'count': 'Shipment Count'})
        # Sort by month and then by mean
        month_stats = month_stats.sort_values(by=['Shipment Origin Month', 'Avg Processing Days'], ascending=[True, False])
        display(month_stats)

        # Example usage:
        # plot_counts_avg_shipment(processed_df, plot_type='TNT Status')
        # plot_counts_avg_shipment(processed_df, plot_type='Destination Country')
        # plot_counts_avg_shipment(processed_df, plot_type='Status and Country')
        # plot_counts_avg_shipment(processed_df, plot_type='Month')

