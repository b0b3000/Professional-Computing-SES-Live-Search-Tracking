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


def retrieve_from_containers(m, STORAGE_CONNECTION_STRING, active_containers):
    
    """
    Retrieve data from Azure blob storage.
    This function retrieves data from Azure blob storage by iterating through each active 
    container passed in the list 'active_containers'. A single blob will be in the container at a time. 
    It parses the GeoJSON data from a blob and adds it to our map, and saves the map as an HTML file.

    Parameters:
        - m (folium.Map): The folium map object to add the GeoJSON data to.
        - STORAGE_CONNECTION_STRING (str): The connection string for the Azure storage account.
        - active_containers: a list of strings, of the names of the storage containers. eg 'base-station-0'

    """
    # Initialize the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

    # Initialize an empty list to collect telemetry data
    telemetry_data = []

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
            
            # Download and process the blob content
            blob = blobs_list[0]
            blob_content = container_client.download_blob(blob).readall()

            # Call mapify to process and add data to the map
            trail, extracted_telemetry = mapify(blob_content)
            if trail:
                trail.add_to(m)

            # Collect telemetry data
            telemetry_data.extend(extracted_telemetry)

        except Exception as e:
            print(f"Error processing container '{container_name}': {e}")
            traceback.print_exc()

    # Save the updated map
    map_save_path = os.path.join(os.path.dirname(__file__), 'application/static/footprint.html')
    m.save(map_save_path)

    return telemetry_data, map_save_path
        


def mapify(geojson_data):
    """
    Process and display GPS data with telemetry on the map.

    Returns:
    - trail (TimestampedGeoJson): A Folium object to add to the map, or None if parsing fails.
    - telemetry_list (list): A list of telemetry data points to be sent to the frontend.
    """
    
    try:
        decoded_data = geojson_data.decode('utf-8').replace("'", '"')
        points = json.loads(decoded_data)
    except Exception as e:
        print(f"Error decoding JSON data: {e}")
        return None, []

    features = []
    telemetry_list = []

    for point in points:
        for _, point_data in point.items():
            lat = point_data.get('lat', 0.0)
            long = point_data.get('long', 0.0)
            name = point_data.get('name', 'Unnamed Point')
            time = point_data.get('time', '00:00:00T00:00:00')
            telemetry = point_data.get('telemetry', {})

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

    trail = TimestampedGeoJson(
        {
            "type": "FeatureCollection",
            "features": features,
        },
        transition_time=100,
        period="PT1M",
        loop=False,
        add_last_point=True,
    )

    return trail, telemetry_list

# Testing purposes
if __name__ == "__main__":
    
    active_containers = ['base-station-0']  # Replace with the containers you want to test
    STORAGE_CONNECTION_STRING = get_key.get_key()
    
    
    # Create a new map object to test the updates
    m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)
    
    # Call the function with test parameters
    try:
        retrieve_from_containers(m, STORAGE_CONNECTION_STRING, active_containers)
        print()
        print("Test completed successfully. The map should be updated with data from the active containers.")
    except Exception as e:
        print("An error occurred during testing:", e)
    