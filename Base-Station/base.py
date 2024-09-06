"""
Python program that runs on the RaspberryPi, connected to a base station.
See RaspberryPi setup documentation in this directory's README.md.
See requirements.txt

Fred's TODO:
TODO 1: Upload data to storage account container, coordinate with front-end people for method of upload:
    - Each search gets its own container, so base station must know the name of container.
    - Base station uploads the single self-titled .json file every time it gets a GPS update from it's tracker.
TODO 2: Code that checks for types of telemetry received and dynamically builds the returning dictionary/Json.
TODO 3: Print meaningful error messages and data to a log file in the event of a crash.

Meshtastic Serial Interface Node Values
'num':
'user':
    'id':
    'longName':
    'shortName':
    'macaddr':
    'hwModel':
'position':
    'latitudeI':
    'longitudeI':
    'altitude':
    'time':
    'latitude':
    'longitude':
'snr':
'deviceMetrics':
    'batteryLevel':
    'voltage':
    'airUtilTx':
"""

import meshtastic.serial_interface
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import sys
import time
import traceback
import json

BASE_STATION_ID = '!7c5cb2a0'
BASE_STATION_LONG_NAME = 'base_3200_a'
TRACKER_ID = '!33679a4c'
TRACKER_LONG_NAME = 'fredtastic'
SEARCH_ID = ''


def run_base_station():
    """Performs startup operations."""

    # ---------- Establishes connection with Azure Storage, creates blob file for uploading. ----------

    print("Please enter the search ID: ")
    # SEARCH_ID = str(input())
    SEARCH_ID = "0"

    storage_key = get_key()
    # Initialises client to interact with the Storage Account.
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=storage_key)
    print("search" + SEARCH_ID)
    # Initialises client to interact with the existing search container.
    container_client = blob_service_client.get_container_client(container="search" + SEARCH_ID)

    # ---------- Initialises variables and gets first GPS point from tracker. ----------

    print("Beginning base station setup process with base station ID and name = " + BASE_STATION_ID + " , " + BASE_STATION_LONG_NAME
          + ". and tracker ID and name = " + TRACKER_ID + " , " + TRACKER_LONG_NAME)

    json_upload = []        # Holds all current GPS data from the tracker.
    json_key = 0            # Control variable to give each GPS point a unique identifier.

    interface = meshtastic.serial_interface.SerialInterface()   # Establishes an interface with the base station.
    new_data = get_nodes_verbose(interface)                     # Gets data for base station and tracker.
    latest_data = new_data                                      # Holds the latest GPS ping from the tracker.
    json_upload.append({"point" + str(json_key): new_data})
    json_key += 1

    with open(BASE_STATION_LONG_NAME, "w") as f:                # Writes all current GPS data to file (this will be uploaded to server eventually).
        f.write(json.dumps(json_upload))

    # Test upload to container.
    container_client.upload_blob(name=BASE_STATION_LONG_NAME, data=str(json_upload), overwrite=True)

    # ---------- Every 60 seconds, checks for new GPS data from the tracker. ----------

    try:
        while True:
            new_data = get_nodes(interface, latest_data)

            # If the GPS data has not changed since the latest new data, do nothing.
            if new_data == 0:
                pass

            # If the GPS data is new, save it to file.
            else: 
                print("writing: " + str(new_data))
                json_upload.append({"point" + str(json_key): new_data})
                json_key += 1
                with open(BASE_STATION_LONG_NAME, "w") as f:
                    f.write(json.dumps(json_upload))
                latest_data = new_data      # Updates latest_data for future changes reference.

            time.sleep(10)

    except Exception as e:
        # Catches any unexpected error in running the entire code while looping.
        # TODO: Create a log file that stores crash data and current variables.
        print("Encountered an unexpected error, shutting down...")
        interface.close()
        traceback.print_exc()

    # ---------------------------------------------------------------------------------


def get_nodes(interface, latest_data):
    """Gets data from tracker via the base station, returns the data if it is new.
    
    Keyword arguments:
    interface -- The Meshtastic serial interface that interacts with devices.
    latest_data -- The most recently received data from the tracker.
    Return: 0 if the data is the same as most recent data, or returns the new data if it is different.
    """

    # ---------- Checks serial connection has been maintained ---------- 

    try:    
        nodes = interface.nodes
    except AttributeError as e:
        print("AttributeError:", e)
        print("No LoRa devices were found to be serially connected, check USB connection cable and device.")
        # Print to the log file that the serial connection was disrupted.
        sys.exit(1)

    # ---------- Iterates through all nodes to find the tracker ----------

    print("Retrieving tracker data...")
    foundTracker = False
    tracker = {}
    for value in nodes.values():
        if value['user']['id'] == TRACKER_ID:
            foundTracker = True
            tracker = value
    if foundTracker == False:
        print("\n # ----------  Failed to find GPS tracker. ---------- \n")

    # ---------- Checks the tracker data received, if the GPS data is new returns it. ----------

    battLevel = tracker['deviceMetrics']['batteryLevel']
    try:
        coords = [tracker['position']['longitude'], tracker['position']['latitude']]
        times = datetime.fromtimestamp(tracker['position']['time']).strftime("%Y-%m-%dT%H:%M:%S")   # Converts UNIX time to UTC.
        altitude = tracker['position']['altitude']
        print("Received GPS data from tracker: " + str(coords))
        if coords == latest_data['coords']:
            print("Received GPS data matches old GPS data, not saving.")
            return 0
        else:
            print("Received GPS data is new, saving.")
            new_data = {"name": TRACKER_ID, "time": times, "lat": coords[0], "long": coords[1], 
                        "telemetry": {"battery": battLevel, "altitude": altitude}}
            # TODO: upload_to_server()
            return new_data
        
    except KeyError as e:
        print("No GPS data found for tracker. Please check GPS lock.")
        return 0

    # ---------------------------------------------------------------------------------


def get_nodes_verbose(interface):
    """The same as the above function, except runs basic setup and prints results verbosely"""

    # ---------- Checks serial connection has been maintained ---------- 

    try:    
        nodes = interface.nodes
    except AttributeError as e:
        print("AttributeError:", e)
        print("No LoRa devices were found to be serially connected, check USB connection cable and device.")
        # Print to the log file that the serial connection was disrupted.
        sys.exit(1)

    # ---------- Iterates through all nodes and prints their data verbosely. ----------

    baseStation = {}
    tracker = {}
    otherDevices = []
    print("Getting all nodes information...")
    for value in nodes.values(): 
        if value['user']['id'] == BASE_STATION_ID:
            baseStation = value
            print("\nBase Station Details:")
            print(baseStation)
        if value['user']['id'] == TRACKER_ID:
            tracker = value
            print("\nTracker Details:")
            print(tracker)
        else:
            otherDevices.append(value['user']['longName'])
    print("\nOther previously connected devices found:")
    for device in otherDevices:
        print(device)

    # ---------- Adds retrieved tracker data to saved data. ----------

    print("Getting full tracker data...")
    battLevel = tracker['deviceMetrics']['batteryLevel']
    try:
        coords = [tracker['position']['latitude'], tracker['position']['longitude']]
        times = datetime.fromtimestamp(tracker['position']['time']).strftime("%Y-%m-%dT%H:%M:%S")   # Converts UNIX time to UTC.
        altitude = tracker['position']['altitude']
        new_data = {"name": TRACKER_ID, "time": times, "lat": coords[0], "long": coords[1], 
                    "telemetry": {"battery": battLevel, "altitude": altitude}}
        return new_data

    except KeyError as e:
        print("No GPS data found for tracker. Please check GPS lock.")
        return 0

    # ---------------------------------------------------------------------------------


def get_key():
    """Retrieves an Azure Storage key from a text file in this directory."""
    # Sets connection string, where AccountName is the name of the Storage Account, and AccountKey is a valid Access Key to that account.
    conn_string = "DefaultEndpointsProtocol=https;AccountName=cits3200testv1;AccountKey=;EndpointSuffix=core.windows.net"
    with open("keys.txt") as file:
        for line in file:
            if line.rstrip().startswith("key1:"):
                key = line.rstrip().split("key1:", 1)[1]    # Splits the key from after the first occurence of "key1:".
                return conn_string[:69] + key + conn_string[69:]    # Places the key in the correct position in the middle of connection string.


if __name__ == "__main__":
    run_base_station()
