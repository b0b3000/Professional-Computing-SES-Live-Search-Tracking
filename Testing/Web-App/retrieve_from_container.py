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
import map_processing
import traceback


"""
Retrieve data from Azure blob storage.
This function retrieves data from Azure blob storage by iterating through each 
container in the storage account and each blob in the container. 
It parses the GeoJSON data from the blobs and appends the parsed data to device-specific 
data list. It also adds the GeoJSON data to a map and saves the map as an HTML file.

Parameters:
    - m (folium.Map): The folium map object to add the GeoJSON data to.
    - STORAGE_CONNECTION_STRING (str): The connection string for the Azure storage account.

Returns:
    - device_data (list): A list of dictionaries containing the parsed data from the blobs.

    needs to return a dict of all container data. -> {container_name: list_of_blobs}

Raises:
    - Exception: If there is an error downloading a blob.


NEEDS WORK:

- The function is currently not returning correct data. needs to return a dict of all container data.
- function can't take in a map object asa parameter. we may need to create a new folium map object for each base-statino-{id}.
- This will allow us to save the map as an HTML file for each base station.


"""
def retrieve_from_containers(m, STORAGE_CONNECTION_STRING):
    
    # Initialize the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

    # To store device-specific data
    retrieved_data = {}

    # Iterate through each container in the Storage Account
    print("\n----- Containers -----\n")
    base_stn_id = -1
    for container in blob_service_client.list_containers():

        retrieved_data[container.name] = []
        m_container = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)

        if container.name.startswith('base-station-'):
            base_stn_id = container.name.split('-')[-1]

        container_client = blob_service_client.get_container_client(container)

        # Iterate through each blob in the container
        for blob in container_client.list_blobs():
            try:
                blob_content = container_client.download_blob(blob).readall()
                # # Append parsed data to device_data
                # lines = eval(blob_content)
                # for line in lines:
                #     device_data.append({
                #         'data': line.get('data', 'No additional data')
                #     })  
                # print(f"\n\tContent of the blob '{blob.name}': \n\t\t{str(blob_content)}")
                # Add the GeoJSON data to the map

                mapify(blob_content).add_to(m_container)
                retrieved_data[container.name].append(blob_content)
                mapify(blob_content).add_to(m)
            except Exception as e:
                print(f"Error downloading blob: {e}")
                traceback.print_exc()

        # Save the map to an HTML file
        if base_stn_id == -1:
            map_save_path = os.path.join(os.path.dirname(__file__), f'app/static/base-station-{base_stn_id}.html')
            m_container.save(map_save_path)
            
        m.save('app/static/footprint.html')
        
    return retrieved_data



"""
Parse and create a TimestampedGeoJson object from GeoJSON data.
Takes in GeoJSON data as input and parses it to create a list of features.
Each feature represents a line on the map with its corresponding properties
such as coordinates, times, tooltip, and style. The function then creates a
TimestampedGeoJson object using the parsed data.

Parameters:
    - geojson_data (str): The GeoJSON data to be parsed.

Returns:
    - trail (folium.plugins.TimestampedGeoJson): The TimestampedGeoJson object representing the parsed GeoJSON data.
"""
def mapify(geojson_data):
    
    # Parse the GeoJSON data
    lines = eval(geojson_data)
    
    # Create features from the GeoJSON data
    features = [    
        {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": line["coordinates"],
            },
            "properties": {
                "times": line["dates"],
                "tooltip": line["data"] + str(line["dates"]),
                "style": {
                    "color": line["color"],
                    "weight": 5,
                },
            },
        }
        for line in lines
    ]
    
    # Create a TimestampedGeoJson object to add to the map
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
    
    return trail
