# pip install azure-storage-blob, folium
"""
Python program for retrieving data from Azure blob storage.

Naming convention for Containers: "base-station-[id]", and for Blobs: "search_[id]".
Data storage format: TimestampedGeoJSON

Written by Bob Beashel, Fred Leman
Implemented/ Further developed by Susheel Utagi, Lilee Hammond
"""
import os
import folium
from folium.plugins import TimestampedGeoJson
from azure.storage.blob import BlobServiceClient
import traceback
import get_key
import json
import random
from enum import Enum

"""Simple enum to assign colours to trails"""
class TrailColour(Enum):
    RED = "#FF5733"
    ORANGE = "#FF8D33"
    YELLOW = "#FFC300"
    GREEN = "#33FF57"
    CYAN = "#33FFF3"
    BLUE = "#3375FF"
    PURPLE = "#B833FF"
    PINK = "#FF33F3"
    MAGENTA = "#FF33B8"
    LIME = "#A8FF33"

def get_random_colour():
    """Chooses a random colour from the given enum.
    
       Returns: Hex string represnting the chosen colour"""
    return random.choice(list(TrailColour)).value


def retrieve_from_containers(m, STORAGE_CONNECTION_STRING, active_containers):
    """
    Retrieve data from Azure blob storage and add the points and lines to the map.

    Parameters:
        - m (folium.Map): The folium map object to add the GeoJSON data to.
        - STORAGE_CONNECTION_STRING (str): The connection string for the Azure storage account.
        - active_containers: a list of strings, of the names of the storage containers.

    """
    # Initialize the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

    telemetry_data = []
    all_blob_content = {}
    for container_name in active_containers:
        
        try:
            container_client = blob_service_client.get_container_client(container_name)
            if not container_client.exists():
                print(f"Container '{container_name}' does not exist. Skipping...")
                continue

            blobs_list = list(container_client.list_blobs())
            if len(blobs_list) != 1:
                print(f"Unexpected blob count in '{container_name}'. Expected 1, found {len(blobs_list)}.")
                continue
            
            # Download and process blob content
            blob = blobs_list[0]
            blob_content = container_client.download_blob(blob).readall()
            all_blob_content[blob.name] = blob_content

            # Call mapify to process and get points and coordinates
            features, coordinates, extracted_telemetry = mapify(blob_content)

            # taken from folium docs, stackoverflow, and integrated with the help of ChatGPT
            # Add points to map using folium.Marker
            for feature in features:
                point_location = feature["geometry"]["coordinates"][::-1]  # Reversing [long, lat] to [lat, long]
                folium.Marker(
                    location=point_location,
                    popup=feature["properties"]["tooltip"],
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)

            # Choose a colour for this trail
            #TODO: pass in the last chosen colour and make it impossible to choose that again.
            trail_colour = get_random_colour()

            # Draw a line connecting coordinates
            if coordinates:
                folium.PolyLine(
                    locations=coordinates,
                    color=trail_colour,  # Assign a random color to each trail
                    weight=5,
                    opacity=0.7  
                ).add_to(m)

            telemetry_data.extend(extracted_telemetry)

        except Exception as e:
            print(f"Error processing container '{container_name}': {e}")
            traceback.print_exc()

    # Save updated map
    map_save_path = os.path.join(os.path.dirname(__file__), 'application/static/footprint.html')
    m.save(map_save_path)

    #print("tel data", telemetry_data)
    #print("map save path", map_save_path)
    return telemetry_data, map_save_path, all_blob_content
        


def mapify(geojson_data):
    """
    Process and display GPS data with telemetry on the map.
    
    Returns:
    - features (list): A list of GeoJSON features to add to the map.
    - coordinates (list): A list of coordinate tuples for drawing a PolyLine.
    - telemetry_list (list): A list of telemetry data points to be sent to the frontend.
    """
    #print("Testing geojson data in mapify", geojson_data)
    
    try:
        decoded_data = geojson_data.decode('utf-8').replace("'", '"')
        points = json.loads(decoded_data)
        #print("decoded data:", points)
    except Exception as e:
        print(f"Error decoding JSON data: {e}")
        return None, [], []

    features = []
    coordinates = []
    telemetry_list = []

    for point in points:
        for _, point_data in point.items():
            lat = point_data.get('lat', 0.0)
            long = point_data.get('long', 0.0)
            name = point_data.get('name', 'Unnamed Point')
            time = point_data.get('time', '00:00:00T00:00:00')
            telemetry = point_data.get('telemetry', {})
            coordinates.append([lat, long])

            # Add the point as a GeoJSON `feature` (this will display points as an icon on map)
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [long, lat],
                },
                "properties": {
                    "time": time,
                    "name": name,
                    "tooltip": f"Name: {name}\nTime: {time}\nBattery: {telemetry.get('battery', 'N/A')}%",
                    "telemetry": telemetry,
                },
            })

            # Collect telemetry data for returning
            telemetry_list.append({
                "name": name,
                "time": time,
                "telemetry": telemetry
            })

    return features, coordinates, telemetry_list 

#Testing purposes (Uncomment if needed to test)
# if __name__ == "__main__":
    
#     active_containers = ['base-3200-b']  # Replace with the containers you want to test
#     STORAGE_CONNECTION_STRING = get_key.get_key()
    
    
#     # Create a new map object to test the updates
#     m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)
    
#     # Call the function with test parameters
#     try:
#         retrieve_from_containers(m, STORAGE_CONNECTION_STRING, active_containers)
#         print()
#         print("Test completed successfully. The map should be updated with data from the active containers.")
#     except Exception as e:
#         print("An error occurred during testing:", e)
    