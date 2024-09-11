"""
Python program that runs on the RaspberryPi, connected to a base station.
See RaspberryPi setup documentation in this directory's README.md.
See requirements.txt

TODO 1: Print meaningful error messages and data to a log file.
TODO 2: Upload data to server.


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
import copy

BASE_STATION_ID = '!7c5b51e0'
BASE_STATION_LONG_NAME = 'client_3200_b_temp'
TRACKER_ID = '!33679a4c'
TRACKER_LONG_NAME = 'fredtastic'


def run_base_station():
    """Performs startup operations."""

    print("Booting up base station...")
    lines = []      # List of the trackers historical locations.

    interface = meshtastic.serial_interface.SerialInterface()   # Establishes an interface with the base station.
    baseStation, tracker, current_line = get_nodes_verbose(interface)      # Gets data for base station and tracker.

    # Retrieves device information every 10 seconds, continues to draw new lines.
    try:
        while True:
            lines, current_line = get_nodes(interface, lines, current_line)
            time.sleep(10)
    except:
        print("Encountered an error, shutting down...")
        interface.close()


def get_nodes(interface, lines, current_line):
    """Gets information about the tracker from the serial interface, if this finds a new GPS ping
        - It adds the new GPS data to the end of the current line.
        - Adds that line to the list of lines to be uploaded to the server (this forms a path).
        - It creates the start of a new current line with the new GPS data, and returns it.
    
    Keyword arguments:
    interface -- The Meshtastic serial interface that interacts with devices.
    lines - a list of the trackers historical lines.
    current_line - the first half the current line.
    Return: A list of the trackers historical lines, and the first half of the current line.
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

    data_line = {'coordinates': [], 'dates': [], 'color': "red", 'data': "additional data here"}
    coords = [tracker['position']['longitude'], tracker['position']['latitude']]
    times = datetime.fromtimestamp(tracker['position']['time']).strftime("%Y-%m-%dT%H:%M:%S")   # Converts UNIX time to GeoJson.
    battLevel = tracker['deviceMetrics']['batteryLevel']
    altitude = tracker['position']['altitude']

    # If the data retrieved in the last node retrieval is NEW, then starts a new line.
    if coords == current_line['coordinates'][0] and times == current_line['dates'][0]:
        print("\nNo tracker update yet.\n")

    else:
        print("\nTRACKER UPDATE.")
        current_line['coordinates'].append(coords)      # Adds latitude and longitude to END of the current line.
        current_line['dates'].append(times)                # Adds time to the END of the current line.
        current_line['data'] = "BatteryLevel: " + str(battLevel) + ", Altitude: " + str(altitude)

        # Adds this line to the list, then starts a NEW CURRENT LINE.
        print("Finished current line: " + str(current_line))
        lines.append(current_line)
        current_line = copy.deepcopy(data_line)

        current_line['coordinates'].append(coords)      # Adds latitude and longitude to START of the current line.
        current_line['dates'].append(times)                # Adds time to the START of the current line.
        current_line['data'] = "BatteryLevel: " + str(battLevel) + ", Altitude: " + str(altitude)

    # TODO: upload_to_server()

    return lines, current_line


def get_nodes_verbose(interface):
    """Gets information from the serial interface and prints it verbosely, returns base station and tracker info.
    
    Keyword arguments:
    interface -- The Meshtastic serial interface that interacts with devices.
    Return: Two dictionaries with information retrieved from the base station and the tracker.
    """
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

    # ---------- Adds retrieved tracker data to the first data line. ----------
    
    data_line = {'coordinates': [], 'dates': [], 'color': "red", 'data': "additional data here"}
    coords = [tracker['position']['longitude'], tracker['position']['latitude']]
    times = datetime.fromtimestamp(tracker['position']['time']).strftime("%Y-%m-%dT%H:%M:%S")   # Converts UNIX time to GeoJson.
    battLevel = tracker['deviceMetrics']['batteryLevel']
    altitude = tracker['position']['altitude']

    data_line['coordinates'].append(coords)      # Adds latitude and longitude to END of the current line.
    data_line['dates'].append(times)                # Adds time to the END of the current line.
    data_line['data'] = "BatteryLevel: " + str(battLevel) + ", Altitude: " + str(altitude)

    print("\nFirst data line: " + str(data_line))

    return baseStation, tracker, data_line


if __name__ == "__main__":
    run_base_station()
