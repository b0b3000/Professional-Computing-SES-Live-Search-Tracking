"""
Python program that runs on the RaspberryPi, connected to a base station.
See RaspberryPi setup documentation in this directory's README.md.
See requirements.txt

TODO 1: Upload additional data like AirUtilTx, under the "telemetry" in dictionary.
TODO 2: Print meaningful error messages and data to a log file.
TODO 3: Upload data to server - need to have database up to do this. 

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
import time
from datetime import datetime
import traceback
import json

BASE_STATION_ID = '!7c5cb2a0'
BASE_STATION_LONG_NAME = 'base_3200_a'
TRACKER_ID = '!33679a4c'
TRACKER_LONG_NAME = 'fredtastic'


def run_base_station():
    """Performs startup operations."""

    print("Booting up base station...")
    log = []      # List of the trackers historical locations, and helpful log data in event of a crash.
    json_upload = []
    json_key = 0

    interface = meshtastic.serial_interface.SerialInterface()   # Establishes an interface with the base station.
    new_data = get_nodes_verbose(interface)     # Gets data for base station and tracker.
    latest_data = new_data                                # Saves latest data to compare updated GPS locations.
    json_upload.append({"point" + str(json_key): new_data})
    f = open(BASE_STATION_LONG_NAME, "w")                 # Saves data to a simple text file.
    f.write(json.dumps(json_upload))    
    f.close()
    json_key += 1

    # Retrieves device information every 5 seconds, checks if it is new info.
    try:
        while True:
            new_data = get_nodes(interface, latest_data)
            if new_data == 0:       # Data was the same as the latest.
                pass
            else:       # Data was unique to the latest.
                print("writing: " + str(new_data))
                json_upload.append({"point" + str(json_key): new_data})     # Names the datapoint uniquely.
                f = open(BASE_STATION_LONG_NAME, "w")
                f.write(json.dumps(json_upload))        # Uploads the file in JSON format.
                f.close()
                json_key += 1
                latest_data = new_data      # Update the latest data for future changes reference.
            time.sleep(5)

    except Exception:
        # Catches any error in running the main code block.
        # TODO: Make the log work, saves it to directory before exiting.
        log.append(traceback)
        print("Encountered an error, shutting down...")
        interface.close()
        traceback.print_exc()

    # ---------------------------------------------------------------------------------


def get_nodes(interface, latest_data):
    """Gets information about the tracker from the serial interface, if this finds a new GPS ping:
        - It saves it to historical data
    
    Keyword arguments:
    interface -- The Meshtastic serial interface that interacts with devices.
    latest_data -- The most recently received ping from the tracker.
    Return: 0 if data is the same as most recent ping, or the new data if it is different.
    """
    try:    
        nodes = interface.nodes     # Creates a list of all nodes the base station has been connected to.
    except AttributeError as e:
        print("AttributeError:", e)
        print("No LoRa devices were found to be serially connected, check USB connection cable and device.")
    
    # ---------- Iterates through all nodes to find the tracker ----------

    print("Retrieving tracker data...")
    foundTracker = False
    tracker = {}
    for value in nodes.values():
        if value['user']['id'] == TRACKER_ID:
            foundTracker = True
            tracker = value
    if foundTracker == False:
        print("\n ----- Failed to find GPS tracker -----")

    # ---------- Checks the tracker data received, if the GPS ping is new, creates a new line. ----------

    battLevel = tracker['deviceMetrics']['batteryLevel']
    try:
        coords = [tracker['position']['longitude'], tracker['position']['latitude']]
        times = datetime.fromtimestamp(tracker['position']['time']).strftime("%Y-%m-%dT%H:%M:%S")   # Converts UNIX time to UTC.
        altitude = tracker['position']['altitude']
        print("GPS data from tracker: " + str(coords))
        if coords == latest_data['coords']:
            print("New GPS data matches old GPS data, not saving.")
            return 0
        else:
            new_data = {"name": TRACKER_ID, "time": times, "lat": coords[0], "long": coords[1], 
                        "telemetry": {"battery": battLevel}}
            # TODO: upload_to_server()
            return new_data
        
    except KeyError as e:
        print("No GPS data found for tracker. Please check GPS lock.")
        coords = [0.000000, 0.000000]
        times = '2024:01:01T00:00:00'
        altitude = 0.000000
        new_data = {"name": TRACKER_ID, "time": times, "lat": coords[0], "long": coords[1], 
                    "telemetry": {"battery": battLevel}}   
        return 0       # TODO: Change this and the other one to 0 after testing.

    # ---------------------------------------------------------------------------------


def get_nodes_verbose(interface):
    """The same as the above function, except runs basic setup and prints results verbosely"""
    try:    
        nodes = interface.nodes     # Creates a list of all nodes the base station has been connected to.
    except AttributeError as e:
        print("AttributeError:", e)
        print("No LoRa devices were found to be serially connected, check USB connection cable and device.")

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

    battLevel = tracker['deviceMetrics']['batteryLevel']
    try:
        coords = [tracker['position']['latitude'], tracker['position']['longitude']]
        times = datetime.fromtimestamp(tracker['position']['time']).strftime("%Y-%m-%dT%H:%M:%S")   # Converts UNIX time to UTC.
        altitude = tracker['position']['altitude']
        new_data = {"name": TRACKER_ID, "time": times, "lat": coords[0], "long": coords[1], 
                    "telemetry": {"battery": battLevel}}
        return new_data

    except KeyError as e:
        print("No GPS data found for tracker. Please check GPS lock.")
        coords = [0.000000, 0.000000]
        times = '2024:01:01T00:00:00'
        altitude = 0.000000
        new_data = {"name": TRACKER_ID, "time": times, "lat": coords[0], "long": coords[1], 
                    "telemetry": {"battery": battLevel}}
        return 0   # Change this to 0 after testing.

    # ---------------------------------------------------------------------------------


if __name__ == "__main__":
    run_base_station()
