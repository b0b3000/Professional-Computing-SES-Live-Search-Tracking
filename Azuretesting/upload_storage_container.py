# Ensure that you pip install azure-storage-blob
# Details
"""
The storage_connection_string is what enables connection to a storage container.
Currently this is linked to the one I have made through a free account on microsoft Azure.
I tried to look into making it available for sharing but it began to take too long for the time I had.

Worth looking into of course, however this is just what I tested in the time being.
If you want to test this you need to create an Azure storage account, create a container, then get its access key which is the connection string here.

"""

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=bob3200;AccountKey=uoWVK+RRGGf4jaMYZ76U0zffW9Pm2ejc0XnN6ybXs6MuX6HQkNCa7fzVsKuP78Y8H7qjCheH8EZ7+AStwTVQ6g==;EndpointSuffix=core.windows.net"
CONTAINER_ID = '3200testv1'

# using blobserviceclient class, to authenticate the account, we pass the connection string
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

#create container reference/entity

container_client = blob_service_client.get_container_client(CONTAINER_ID)

# Prepare the data
sample_data_string = "device123, -31.9505, 115.8605"
blob_name = "gps_data.txt"  # Name of the blob (file) in the container

# Upload the data
blob_client = container_client.get_blob_client(blob_name)
blob_client.upload_blob(sample_data_string, overwrite=True)