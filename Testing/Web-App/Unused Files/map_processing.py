from azure.storage.blob import BlobServiceClient

def save_map_to_storage(map_html, CONTAINER_ID, blob_name, connection_string):
    """
    Saves a generated HTML map to Azure Blob Storage.

    This function uploads an HTML file representing a map to a specified container in Azure Blob Storage.
    The map is stored as a blob within the container, allowing it to be accessed or retrieved later.

    Parameters:
    - map_html (str): The HTML content of the map to be saved.
    - CONTAINER_ID (str): The ID of the container where the map will be stored.
    - blob_name (str): The name of the blob (file) within the container.
    - connection_string (str): The connection string to authenticate with Azure Blob Storage.

    The function attempts to upload the map to the specified container and blob. 
    If the upload is successful, a confirmation message is printed. 
    If the upload fails, an error message is printed with the reason for failure.
    """

    # Communicating with storage account
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container=CONTAINER_ID)
    blob_client = container_client.get_blob_client(blob_name)
 
    # Try uploading map to container 'map-storage'
    try:
        blob_client.upload_blob(map_html, overwrite=True)
        print(f"Map uploaded to {CONTAINER_ID}/{blob_name} successfully.")
    except Exception as e:
        print(f"Failed to upload map to {CONTAINER_ID}/{blob_name}: {e}")

    
def load_map_from_storage(container_name, blob_name, connection_string):
    """
    Loads a saved HTML map from Azure Blob Storage.

    This function retrieves an HTML file representing a map from a specified container in Azure Blob Storage.
    The map is downloaded from the storage container and returned as a string, which can then be used to display the map or further processing.

    Parameters:
    - container_name (str): The name of the container where the map is stored.
    - blob_name (str): The name of the blob (file) within the container.
    - connection_string (str): The connection string to authenticate with Azure Blob Storage.

    The function downloads the HTML content of the map from the specified container and blob, 
    decodes it from bytes to a string, and returns the decoded HTML content.
    """

    # Communicating with storage account
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    
    # Downloading saved map from container
    map_html = blob_client.download_blob().readall().decode('utf-8')
    
    return map_html
