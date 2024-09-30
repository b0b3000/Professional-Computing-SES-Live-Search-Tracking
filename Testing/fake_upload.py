"""
Python program that uploads fake GPS data to the cloud server.
Use this for testing the web application.

Written by Fred Leman
"""

from azure.storage.blob import BlobServiceClient
import json
import time
import copy
import datetime

NUM_BASE_STATIONS = 5


def upload():
    # Initialises Azure storage.
    storage_key = get_key()
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=storage_key)

    # Reads in the test data.
    with open("base-3200-a", "r") as file:
        test_data = file.read().replace("'", '"')
    test_points = json.loads(test_data)

    # For each base station, adds the first data point as a list.
    fake_data_sets = []
    for i in range(NUM_BASE_STATIONS):
        print(f"Creating container {i}")
        blob_service_client.create_container(name=f"base-station-{i}")
        time_now = datetime.datetime.now()
        iso_time = time_now.strftime("%Y-%m-%dT%H:%M:%S")

        data_set = {
            'point0': {
                'name': f'!33679a4test{i}', 
                'time': iso_time,
                'lat': round(test_points[0]['point0']['lat'] + (0.0001 * (i * 10)), 7),     # Adds a bit of variance for the coordinates of each base station.
                'long': round(test_points[0]['point0']['long'] + (0.0001 * (i * 10)), 7),   # Modify these to make the searches more or less spaced out.
                'telemetry': {
                    'battery': test_points[0]['point0']['telemetry']['battery'],
                    'altitude': test_points[0]['point0']['telemetry']['altitude'],
                },
                'longname': f'base-station-{i}'
            }
        }
        fake_data_sets.append([data_set])     # Adds the first data point as a list.
        print(fake_data_sets[i])
        print("\n")

    # For the next 23 points in the test data, add the modified point and upload to server, then wait 30 seconds, then repeat.
    for i in range(23):
        print("Uploading.")
        time_now = datetime.datetime.now()
        iso_time = time_now.strftime("%Y-%m-%dT%H:%M:%S")
        for j in range(NUM_BASE_STATIONS):
            container_client = blob_service_client.get_container_client(container=f"base-station-{j}")
            data_set = copy.deepcopy({
                f'point{i+1}': {
                    'name': f'!33679a4test{j}', 
                    'time': iso_time,
                    'lat': round(test_points[i+1][f'point{i+1}']['lat'] + (0.001 * j), 7),  # Modify these to make the searches more or less spaced out.
                    'long': round(test_points[i+1][f'point{i+1}']['long'] + (0.001 * j), 7),
                    'telemetry': {
                        'battery': test_points[i+1][f'point{i+1}']['telemetry']['battery'],
                        'altitude': test_points[i+1][f'point{i+1}']['telemetry']['altitude'],
                    },
                    'longname': f'base-station-{j}'
                }
            })
            fake_data_sets[j].append(data_set)
            print(f"{fake_data_sets[j]}\n")
            container_client.upload_blob(name=f"base-station{j}", data=str(fake_data_sets[j]), overwrite=True)
        print("Sleeping for 30 secs.")
        time.sleep(30)      # Modify this to make it run a bit faster.

    for set in fake_data_sets:
        print(f"{set}\n")

    return 0


def delete_containers():
    # Initialises Azure storage.
    storage_key = get_key()
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=storage_key)

    # Deletes containers equal to NUM_BASE_STATIONS.
    for i in range(NUM_BASE_STATIONS):
        print(f"Deleting container {i}")
        blob_service_client.delete_container(f"base-station-{i}")
    print("All test containers deleted.")


def get_key():
    """Retrieves an Azure Storage key from a text file in this directory."""
    # Sets connection string, where AccountName is the name of the Storage Account, 
    # and AccountKey is a valid Access Key to that account.
    conn_string = "DefaultEndpointsProtocol=https;AccountName=cits3200testv1;AccountKey=;EndpointSuffix=core.windows.net"
    with open("keys.txt") as file:
        for line in file:
            if line.rstrip().startswith("key1:"):
                key = line.rstrip().split("key1:", 1)[1]    # Splits the key from after the first occurence of "key1:".
                return conn_string[:69] + key + conn_string[69:]    # Places the key in the correct position in the middle of connection string.


if __name__ == "__main__":
    upload()                  # Comment this out, then
    # delete_containers()     # uncomment this to delete the test containers.
