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

# Example usage:
# display_exception_shipments(processed_df)




def plot_horizontal_bar(processed_df):
    """
    Create a horizontal bar plot of the number of shipments by TNT Status.

    Args:
    - processed_df (pd.DataFrame): Input DataFrame containing shipment data.

    Returns:
    - None
    """
    
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Define a color palette with different colors for each TNT Status
    colors = sns.color_palette("husl", len(processed_df['TNT Status'].unique()))

    # Create a bar plot
    plt.figure(figsize=(10, 6))
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
