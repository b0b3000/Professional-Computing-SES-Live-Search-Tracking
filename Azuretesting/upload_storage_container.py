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

storage_connection_string = 'DefaultEndpointsProtocol=https;AccountName=3200data;AccountKey=o1n3cEFaFRhSH+ag2sB+82xRWOQwge3641FCMKEBqpEmaS5uMYwWaCGqp6YIFD6Ikcn+zibojnRo+AStQdyo0g==;EndpointSuffix=core.windows.net'

# using blobserviceclient class, to authenticate the account, we pass the connection string
blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)

#create container reference/entity
container_id = 'datacontainer'
container_client = blob_service_client.get_container_client(container_id)

# Prepare the data
data_string = "device123, -31.9505, 115.8605"
blob_name = "gps_data.txt"  # Name of the blob (file) in the container

# Upload the data
blob_client = container_client.get_blob_client(blob_name)
blob_client.upload_blob(data_string, overwrite=True)