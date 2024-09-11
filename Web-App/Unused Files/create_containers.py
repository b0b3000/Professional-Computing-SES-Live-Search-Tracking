# Creates additional storage containers to store continuous map data and record of blobs processed.

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

def create_containers(container_names, STORAGE_CONNECTION_STRING):
    
    """
    Creates the required containers in Azure Blob Storage if they don't already exist.
    
    :param connection_string: The connection string to your Azure Blob Storage account.
    :param container_names: A list of container names to create.
    """
    # Initialize the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

    for container_name in container_names:
        try:
            # Attempt to create each container
            blob_service_client.create_container(name=container_name)
            print(f"Container '{container_name}' created successfully.")
        except ResourceExistsError:
            print(f"Container '{container_name}' already exists. Skipping creation.")
