"""
Python program that the base station will use to upload GPS data to the cloud server.

TO-DO:
    - Create robustness through try/except blocks for pretty much everything

Requirements:
azure-storage-blob==12.22.0
folium==0.17.0

Written by Bob Beashel, Fred Leman.
"""
import random
import copy
import datetime
from azure.storage.blob import BlobServiceClient

def startup():
    """Boots up the base station and establishes connection to server."""

    STORAGE_CONNECTION_STRING = get_key()
    BASE_STATION_ID = 1
    CONTAINER_ID = "base-station-" + str(BASE_STATION_ID)
    SEARCH_ID = 0

    # Initialises client to interact with the Storage Account.
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=STORAGE_CONNECTION_STRING)

    # Creates a new container (directory) for this base station to upload data to.
    blob_service_client.create_container(name=CONTAINER_ID)

    # Initialises client to interact with the container.
    container_client = blob_service_client.get_container_client(container=CONTAINER_ID)

    # Simulate the running of the base station, periodcally taking GPS input data from a tracker.
    run_base_station(SEARCH_ID, container_client)


def get_key():
    """Retrieves key1 from the text file in this directory."""

    # Sets connection string, where AccountName is the name of the Storage Account, and AccountKey is a valid Access Key to that account.
    conn_string = "DefaultEndpointsProtocol=https;AccountName=cits3200testv1;AccountKey=;EndpointSuffix=core.windows.net"
    with open("keys.txt") as file:
        for line in file:
            if line.rstrip().startswith("key1:"):
                # Splits the key from after the first occurence of "key1:".
                key = line.rstrip().split("key1:", 1)[1]
                # Places the key in the correct position in the middle of connection string.
                return conn_string[:69] + key + conn_string[69:]
            

def run_base_station(search_id, container_client):
    """Simulates the running of the base station, periodcally taking GPS input data from a tracker, and uploading it."""

    data_lines = []     # Stores all the GPS lines.
    data_line = {"coordinates": [], "dates": [], "color": "red", "data": "additional data goes here"}   # Dictionary shell to be copied.

    # Begins the simulation of random GPS inputs.
    current_line = copy.deepcopy(data_line)
    i = 0
    while i < 5:
        dt = datetime.datetime.now()
        gps_data = [float(116) + random.random(), float(-31) - random.random()]     # Simulate some random GPS data.
        # If this is the first data point, create the start of the first line.
        if i == 0:
            current_line["coordinates"].append(gps_data)
            current_line["dates"].append(dt.strftime("%Y-%m-%dT%H:%M:%S"))
            
        # If this is not the first data point, create the first line using this GPS data and the last GPS data,
        # then set this point as the start of the next line.
        else:
            dt += datetime.timedelta(hours=i)    # Simulate the passing of an hour each loop.
            current_line["coordinates"].append(gps_data)
            current_line["dates"].append(dt.strftime("%Y-%m-%dT%H:%M:%S"))
            data_lines.append(current_line)     # Finalises the line.
            current_line = copy.deepcopy(data_line)     # Starts the new line.
            current_line["coordinates"].append(gps_data)
            current_line["dates"].append(dt.strftime("%Y-%m-%dT%H:%M:%S"))
        i += 1

    server_upload(search_id, container_client, data_lines)


def server_upload(search_id, container_client, lines):
    """Uploads TimestampedGeoJson lines data to server."""

    container_client.upload_blob(name="search_" + str(search_id), data=str(lines), overwrite=True)


if __name__ == "__main__":
    startup()
