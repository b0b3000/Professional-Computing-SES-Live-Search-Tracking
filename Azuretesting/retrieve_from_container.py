# Ensure that you pip install azure-storage-blob
# Written by Bob Beashel

"""
Test python program for retrieving data from azure blob storage
"""

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Connection string to your Azure Storage account
STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=bob3200;AccountKey=uoWVK+RRGGf4jaMYZ76U0zffW9Pm2ejc0XnN6ybXs6MuX6HQkNCa7fzVsKuP78Y8H7qjCheH8EZ7+AStwTVQ6g==;EndpointSuffix=core.windows.net"
CONTAINER_ID = '3200testv1'
BLOB_NAME = "gps_data.txt"  # Name of the blob (file) in the container

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

# Get the ContainerClient and BlobClient
container_client = blob_service_client.get_container_client(CONTAINER_ID)
blob_client = container_client.get_blob_client(BLOB_NAME)

# Download the blob's content
try:
    # Download the blob to a local file
    with open(BLOB_NAME, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
    print(f"Blob '{BLOB_NAME}' downloaded successfully.")
    
    # Or print the blob's content directly
    blob_content = blob_client.download_blob().readall().decode("utf-8")
    print(f"Content of the blob '{BLOB_NAME}': {blob_content}") #downloads as a string

except Exception as e:
    print(f"Error downloading blob: {e}")