from azure.storage.blob import BlobServiceClient

def save_map_to_storage(map_html, CONTAINER_ID, blob_name, connection_string):
    
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
    
    # Communicating with storage account
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    
    # Downloading saved map from container
    map_html = blob_client.download_blob().readall().decode('utf-8')
    
    return map_html
