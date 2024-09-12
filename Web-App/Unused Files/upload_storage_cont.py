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
    BASE_STATION_ID = 1
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

    lines = [
        {
            "coordinates": [
                [115.819374, -31.978527],  # UWA Hackett Drive Entrance
                [115.819978, -31.978068]   # UWA Recreation and Fitness Centre
            ],
            "dates": ["2024-08-18T08:00:00", "2024-08-18T08:10:00"],
            "color": "orange",
            "data": "Device A to Device B"
        },
        {
            "coordinates": [
                [115.819978, -31.978068],  # UWA Recreation and Fitness Centre
                [115.820828, -31.977492]   # UWA Guild Village
            ],
            "dates": ["2024-08-18T08:10:00", "2024-08-18T08:20:00"],
            "color": "orange",
            "data": "Device B to Device C"
        },
        {
            "coordinates": [
                [115.820828, -31.977492],  # UWA Guild Village
                [115.821492, -31.976972]   # UWA Winthrop Hall
            ],
            "dates": ["2024-08-18T08:20:00", "2024-08-18T08:30:00"],
            "color": "orange",
            "data": "Device C to Device D"
        },
        {
            "coordinates": [
                [115.821492, -31.976972],  # UWA Winthrop Hall
                [115.822045, -31.976449]   # UWA Lawrence Wilson Art Gallery
            ],
            "dates": ["2024-08-18T08:30:00", "2024-08-18T08:40:00"],
            "color": "orange",
            "data": "Device D to Device E"
        },
        {
            "coordinates": [
                [115.822045, -31.976449],  # UWA Lawrence Wilson Art Gallery
                [115.822732, -31.975925]   # UWA Reid Library
            ],
            "dates": ["2024-08-18T08:40:00", "2024-08-18T08:50:00"],
            "color": "orange",
            "data": "Device E to Device F"
        },
        {
            "coordinates": [
                [115.822732, -31.975925],  # UWA Reid Library
                [115.823324, -31.975425]   # UWA Matilda Bay Foreshore
            ],
            "dates": ["2024-08-18T08:50:00", "2024-08-18T09:00:00"],
            "color": "orange",
            "data": "Device F to Device G"
        },
        {
            "coordinates": [
                [115.823324, -31.975425],  # UWA Matilda Bay Foreshore
                [115.824019, -31.975025]   # UWA Business School
            ],
            "dates": ["2024-08-18T09:00:00", "2024-08-18T09:10:00"],
            "color": "orange",
            "data": "Device G to Device H"
        },
        {
            "coordinates": [
                [115.824019, -31.975025],  # UWA Business School
                [115.824702, -31.974529]   # UWA Prescott Court
            ],
            "dates": ["2024-08-18T09:10:00", "2024-08-18T09:20:00"],
            "color": "orange",
            "data": "Device H to Device I"
        },
        {
            "coordinates": [
                [115.824702, -31.974529],  # UWA Prescott Court
                [115.825387, -31.974020]   # UWA School of Engineering
            ],
            "dates": ["2024-08-18T09:20:00", "2024-08-18T09:30:00"],
            "color": "orange",
            "data": "Device I to Device J"
        },
        {
            "coordinates": [
                [115.825387, -31.974020],  # UWA School of Engineering
                [115.826078, -31.973517]   # UWA Tennis Courts
            ],
            "dates": ["2024-08-18T09:30:00", "2024-08-18T09:40:00"],
            "color": "orange",
            "data": "Device J to Device K"
        },
        {
            "coordinates": [
                [115.826078, -31.973517],  # UWA Tennis Courts
                [115.826746, -31.973026]   # UWA Irwin Street Building
            ],
            "dates": ["2024-08-18T09:40:00", "2024-08-18T09:50:00"],
            "color": "orange",
            "data": "Device K to Device L"
        },
        {
            "coordinates": [
                [115.826746, -31.973026],  # UWA Irwin Street Building
                [115.827382, -31.972548]   # UWA Chemistry Building
            ],
            "dates": ["2024-08-18T09:50:00", "2024-08-18T10:00:00"],
            "color": "orange",
            "data": "Device L to Device M"
        },
        {
            "coordinates": [
                [115.827382, -31.972548],  # UWA Chemistry Building
                [115.828078, -31.972028]   # UWA Medical and Dental Library
            ],
            "dates": ["2024-08-18T10:00:00", "2024-08-18T10:10:00"],
            "color": "orange",
            "data": "Device M to Device N"
        },
        {
            "coordinates": [
                [115.828078, -31.972028],  # UWA Medical and Dental Library
                [115.828724, -31.971547]   # UWA Physics Building
            ],
            "dates": ["2024-08-18T10:10:00", "2024-08-18T10:20:00"],
            "color": "orange",
            "data": "Device N to Device O"
        },
        {
            "coordinates": [
                [115.828724, -31.971547],  # UWA Physics Building
                [115.829426, -31.971067]   # UWA Social Sciences Building
            ],
            "dates": ["2024-08-18T10:20:00", "2024-08-18T10:30:00"],
            "color": "orange",
            "data": "Device O to Device P"
        },
        {
            "coordinates": [
                [115.829426, -31.971067],  # UWA Social Sciences Building
                [115.830053, -31.970596]   # UWA Tropical Grove
            ],
            "dates": ["2024-08-18T10:30:00", "2024-08-18T10:40:00"],
            "color": "orange",
            "data": "Device P to Device Q"
        },
        {
            "coordinates": [
                [115.830053, -31.970596],  # UWA Tropical Grove
                [115.830747, -31.970090]   # UWA Mathematics Building
            ],
            "dates": ["2024-08-18T10:40:00", "2024-08-18T10:50:00"],
            "color": "orange",
            "data": "Device Q to Device R"
        },
        {
            "coordinates": [
                [115.830747, -31.970090],  # UWA Mathematics Building
                [115.831457, -31.969607]   # UWA Geology and Geography Building
            ],
            "dates": ["2024-08-18T10:50:00", "2024-08-18T11:00:00"],
            "color": "orange",
            "data": "Device R to Device S"
        },
        {
            "coordinates": [
                [115.831457, -31.969607],  # UWA Geology and Geography Building
                [115.832162, -31.969128]   # UWA Computer Science Building
            ],
            "dates": ["2024-08-18T11:00:00", "2024-08-18T11:10:00"],
            "color": "orange",
            "data": "Device S to Device T"
        },
        {
            "coordinates": [
                [115.832162, -31.969128],  # UWA Computer Science Building
                [115.832850, -31.968652]   # UWA Electrical Engineering Building
            ],
            "dates": ["2024-08-18T11:10:00", "2024-08-18T11:20:00"],
            "color": "orange",
            "data": "Device T to Device U"
        },
        {
            "coordinates": [
                [115.832850, -31.968652],  # UWA Electrical Engineering Building
                [115.833541, -31.968167]   # UWA Electrical and Electronic Engineering Annex
            ],
            "dates": ["2024-08-18T11:20:00", "2024-08-18T11:30:00"],
            "color": "orange",
            "data": "Device U to Device V"
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
