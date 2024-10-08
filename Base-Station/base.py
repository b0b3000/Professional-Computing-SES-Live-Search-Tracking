"""
Python program that runs on the RaspberryPi, connected to a base station.
See RaspberryPi setup documentation in this directory's README.md.
See requirements.txt

Fred's TODO:
TODO 1: Comment out all print statements when finished.

Known Issues:
ISSUE 1: 

Written by Fred Leman
"""

import meshtastic.serial_interface
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import sys
import time
import traceback
import json
import logging

logger = logging.getLogger(__name__)

# Change these variables for different base stations.
BASE_STATION_ID = '!7c5cb2a0'
BASE_STATION_LONG_NAME = 'base-3200-c'
TRACKER_ID = '!33679a4c'
TRACKER_LONG_NAME = 'fredtastic'
CONN_STRING = "DefaultEndpointsProtocol=https;AccountName=cits3200testv1;AccountKey=;EndpointSuffix=core.windows.net"
POLL_RATE_SECONDS = 30


def run_base_station():
    """Performs startup operations."""
    logging.basicConfig(filename='base.log', level=logging.INFO)
    logger.info('Started')

    # ---------- Establishes connection with Azure Storage, creates blob file for uploading. ----------

    # Retrieves the Azure Storage key.
    storage_key = get_azure_key()

    # Initialises client to interact with the Storage Account.
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=storage_key)

    # Checks to see if container already exists.
    found = False
    for container in blob_service_client.list_containers():
        if container['name'] == BASE_STATION_LONG_NAME:
            found = True

    if not found:
        # Creates a new container named after this blob if it does not already exist.
        blob_service_client.create_container(name=BASE_STATION_LONG_NAME)

    # Creates a new container client to interact with this base station's private container.
    container_client = blob_service_client.get_container_client(container=BASE_STATION_LONG_NAME)

    # ---------- Initialises variables and gets first GPS point from tracker. ----------

    logging.info(f"Beginning base station setup process with base station ID and name = {BASE_STATION_ID}, {BASE_STATION_LONG_NAME}, and tracker ID and name = {TRACKER_ID} + {TRACKER_LONG_NAME}")
    print(f"Beginning base station setup process with base station ID and name = {BASE_STATION_ID}, {BASE_STATION_LONG_NAME}, and tracker ID and name = {TRACKER_ID} + {TRACKER_LONG_NAME}")

    json_upload = []        # Holds all current GPS data from the tracker.
    json_key = 0            # Control variable to give each GPS point a unique identifier.

    interface = meshtastic.serial_interface.SerialInterface()   # Establishes an interface with the base station.

    new_data = get_nodes_verbose(interface)                     # Gets data for base station and tracker.
    if new_data == 0:
        logging.error("Tracker has no GPS lock, achieve lock then run program again.")
        print("Tracker has no GPS lock, achieve lock then run program again.")
        interface.close()
        return 0
    
    latest_data = new_data                                      # Holds the latest GPS ping from the tracker.
    json_upload.append({"point" + str(json_key): new_data})
    json_key += 1

    logging.info(f"Writing new GPS point {str(new_data)}")
    print("\nWriting new GPS point: " + str(new_data))
    with open(BASE_STATION_LONG_NAME, "w") as f:        # Writes all current GPS data to file (this will be uploaded to server eventually).
        f.write(json.dumps(json_upload))

    # Initial upload to container.
    container_client.upload_blob(name=BASE_STATION_LONG_NAME, data=str(json_upload), overwrite=True)
    logging.info(f"Uploaded total: {str(json_upload)}")
    print("\n Uploaded total: " + str(json_upload) + "\n")

    # ---------- Checks for new GPS data from the tracker, based on poll rate (default 30 seconds) ----------

    time.sleep(POLL_RATE_SECONDS)
    try:
        while True:
            print("\n--------------- LOOP ---------------\n")
            new_data = get_nodes(interface, latest_data)

            # If the GPS data has not changed since the latest new data, do nothing.
            if new_data == 0:
                pass

            # If the GPS data is new, save it to file.
            else: 
                logging.info(f"Writing new GPS point {str(new_data)}")
                print("\nWriting new GPS point: " + str(new_data))
                json_upload.append({"point" + str(json_key): new_data})
                json_key += 1
                with open(BASE_STATION_LONG_NAME, "w") as f:
                    f.write(json.dumps(json_upload))
                container_client.upload_blob(name=BASE_STATION_LONG_NAME, data=str(json_upload), overwrite=True)
                logging.info(f"Uploaded total: {str(json_upload)}")
                print("\nUploaded total: " + str(json_upload) + "\n")
                latest_data = new_data      # Updates latest_data for future changes reference.

            time.sleep(POLL_RATE_SECONDS)

    except Exception as e:
        # Catches any unexpected error in running the entire code while looping.
        # TODO: Create a log file that stores crash data and current variables.
        print("Encountered an unexpected error, shutting down...")
        interface.close()
        logging.fatal(traceback.format_exc)
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
        logging.error("AttributeError: ", e)
        logging.error("No LoRa devices were found to be serially connected, check USB connection cable and device.")
        print("AttributeError:", e)
        print("No LoRa devices were found to be serially connected, check USB connection cable and device.")
        sys.exit(1)

    # ---------- Iterates through all nodes to find the tracker ----------

    logging.info("Retrieving tracker data...")
    print("\nRetrieving tracker data...")
    foundTracker = False
    tracker = {}
    for tracker_data in nodes.values():
        if tracker_data['user']['id'] == TRACKER_ID:
            foundTracker = True
            tracker = tracker_data
    if foundTracker == False:
        logging.fatal("Failed to find GPS tracker amongst nodes. Restart program and ensure tracker is on.")
        print("\n ----------  Failed to find GPS tracker. ---------- \n")

    # ---------- Checks the tracker data received, if the GPS data is new returns it. ----------
    
    # Check that GPS data was included in the tracker data.
    try:
        coords = [tracker['position']['latitude'], tracker['position']['longitude']]
    except KeyError as e:
        logging.warning("No GPS data found for tracker. Please check GPS lock.")
        print("\nNo GPS data found for tracker. Please check GPS lock.")
        return 0
    
    # Check that the GPS data is new.
    if coords == [latest_data['lat'], latest_data['long']]:
        logging.info("Received GPS data matches old GPS data, not saving.")
        logging.info(f"OLD DATA: {tracker}")
        print("Received GPS data matches old GPS data, not saving.")
        print("Old data: " + tracker + "\n")
        return 0
    
    # If it is new, save it, along with other data from the tracker.
    logging.info("Received GPS data is new, saving")
    print("\nReceived GPS data is new, saving.")
    battLevel = tracker['deviceMetrics']['batteryLevel']
    times = datetime.fromtimestamp(tracker['position']['time']).strftime("%Y-%m-%dT%H:%M:%S")
    new_data = {"name": TRACKER_ID, "time": times, "lat": coords[0], "long": coords[1], 
                "telemetry": {"battery": battLevel, "altitude": " "}, "longname": BASE_STATION_LONG_NAME}

    try:        # Method to fix altitude bug.
        new_data["telemetry"]["altitude"] = tracker['position']['altitude']
    except KeyError:
        pass

    return new_data
    
    # ---------------------------------------------------------------------------------


def get_nodes_verbose(interface):
    """The same as get_nodes(), except runs basic setup and prints results verbosely"""

    # ---------- Checks serial connection has been maintained ---------- 

    try:    
        nodes = interface.nodes
    except AttributeError as e:
        logging.error("AttributeError: ", e)
        logging.error("No LoRa devices were found to be serially connected, check USB connection cable and device.")
        print("AttributeError:", e)
        print("No LoRa devices were found to be serially connected, check USB connection cable and device.")

    # ---------- Iterates through all nodes and prints their data verbosely. ----------

    baseStation = {}
    tracker = {}
    otherDevices = []
    logging.info("Getting all nodes information...")
    print("Getting all nodes information...")
    for value in nodes.values(): 
        if value['user']['id'] == BASE_STATION_ID:
            baseStation = value
            logging.info(f"Base station details: {baseStation}")
            print("\nBase Station Details:")
            print(baseStation)
        if value['user']['id'] == TRACKER_ID:
            tracker = value
            logging.info(f"Tracker details: {tracker}")
            print("\nTracker Details:")
            print(tracker)
        else:
            otherDevices.append(value['user']['longName'])
    logging.info("Other previously connected devices found:")
    print("\nOther previously connected devices found:")
    for device in otherDevices:
        logging.info(device)
        print(device)

    # ---------- Adds retrieved tracker data to saved data. ----------
    
    logging.info("Processing tracker data...")
    print("\nProcessing tracker data...")

    # Check that GPS data was included in the tracker data.
    try:
        coords = [tracker['position']['latitude'], tracker['position']['longitude']]
    except KeyError as e:
        logging.warning("No GPS data found for tracker. Please check GPS lock.")
        print("\nNo GPS data found for tracker. Please check GPS lock.")
        return 0
    
    # Save the GPS data, along with other data from the tracker.
    logging.info("Received GPS data is new, saving.")
    print("\nReceived GPS data is new, saving.")
    battLevel = tracker['deviceMetrics']['batteryLevel']
    times = datetime.fromtimestamp(tracker['position']['time']).strftime("%Y-%m-%dT%H:%M:%S")
    new_data = {"name": TRACKER_ID, "time": times, "lat": coords[0], "long": coords[1], 
                "telemetry": {"battery": battLevel, "altitude": " "}, "longname": BASE_STATION_LONG_NAME}

    try:        # Ensures that the telemetry exists, to avoid KeyErrors.
        new_data["telemetry"]["altitude"] = tracker['position']['altitude']
    except KeyError:
        pass

    return new_data

    # ---------------------------------------------------------------------------------


def get_azure_key():
    """Retrieves an Azure Storage key from a text file in this directory."""
    # Sets connection string, where AccountName is the name of the Storage Account, 
    # and AccountKey is a valid Access Key to that account.

    # Find the position where "AccountKey=" appears.
    key_pos = CONN_STRING.find("AccountKey=") + len("AccountKey=")

    with open("keys.txt") as file:
        for line in file:
            if line.rstrip().startswith("key1:"):
                key = line.rstrip().split("key1:", 1)[1]  # Extracts the key after "key1:".
                # Insert the key after "AccountKey=" in the connection string.
                return CONN_STRING[:key_pos] + key + CONN_STRING[key_pos:]

if __name__ == "__main__":
    run_base_station()
