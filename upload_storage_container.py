"""
Python program that the base station will use to upload GPS data to the cloud server.

Requirements:
azure-storage-blob==12.22.0
folium==0.17.0

Written by Bob Beashel, Fred Leman.
"""
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

def startup():
    # Sets connection string, where AccountName is the name of the Storage Account, and AccountKey is a valid Access Key to that account.
    STORAGE_CONNECTION_STRING = get_key()
    BASE_STATION_ID = 0
    CONTAINER_ID = "base-station-" + str(BASE_STATION_ID)
    SEARCH_ID = 0

    # Initialises client to interact with the Storage Account.
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=STORAGE_CONNECTION_STRING)
    
    try:
        # Attempt to create a new container. This will fail if the container already exists.
        blob_service_client.create_container(name=CONTAINER_ID)
        print(f"Container '{CONTAINER_ID}' created successfully.")
    except ResourceExistsError:
        print(f"Container '{CONTAINER_ID}' already exists. Skipping creation.")

    # Initialises client to interact with the container.
    container_client = blob_service_client.get_container_client(container=CONTAINER_ID)

    # Example TimestampedGeoJson lines data (assuming the base station has been tracking all this).
    lines = [
        {
            "coordinates": [
                [116.07911971292083, -31.86478329243488], 
                [116.07975560446562, -31.865369779903773]
            ],
            "dates": ["2024-08-18T00:00:00", "2024-08-18T00:10:00"],
            "color": "red",
            "data": "additional data"  # Things like telemetry data can go here.
            
        },
        {
            "coordinates": [
                [116.07911971292083, -31.86478329243488], 
                [116.07975560446562, -31.865369779903773]
            ],
            "dates": ["2024-08-18T00:10:00", "2024-08-18T00:20:00"],
            "color": "red",
            "data": "additional data"
        },
        {
            "coordinates": [
                [116.07975560446562, -31.865369779903773], 
                [116.08041136907269, -31.864828128884]

            ],
            "dates": ["2024-08-18T00:20:00", "2024-08-18T00:30:00"],
            "color": "red",
            "data": "additional data"
        },
        {
            "coordinates": [
                [116.08041136907269, -31.864828128884], 
                [116.0804396265383, -31.866904109870646]
            ],
            "dates": ["2024-08-18T00:30:00", "2024-08-18T00:40:00"],
            "color": "red",
            "data": "additional data"
            
        },
    ]

    # Uploads the data.
    # Assuming this is for single use.
    container_client.upload_blob(name="search_" + str(SEARCH_ID), data=str(lines), overwrite=True)

def get_key():
    # Retrieves key1 from the text file in this directory.
    # Sets connection string, where AccountName is the name of the Storage Account, and AccountKey is a valid Access Key to that account.
    conn_string = "DefaultEndpointsProtocol=https;AccountName=cits3200testv1;AccountKey=;EndpointSuffix=core.windows.net"
    with open("keys.txt") as file:
        for line in file:
            if line.rstrip().startswith("key1:"):
                # Splits the key from after the first occurence of "key1:".
                key = line.rstrip().split("key1:", 1)[1]
                # Places the key in the correct position in the middle of connection string.
                return conn_string[:69] + key + conn_string[69:]

if __name__ == "__main__":
    startup()
