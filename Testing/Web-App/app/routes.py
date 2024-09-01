"""
Routes:
    - index(): Renders the index.html template and passes device data to it.
    - update_map(): Updates the map with new data and returns a success message.
    - push_data_to_server(): Pushes data to Azure storage container and returns a success message. (Testing Purposes).
    
Written by Susheel Utagi, Lilee Hammond
"""

from flask import render_template, jsonify, current_app as app, request
import os
import folium
from retrieve_from_container import retrieve_from_containers
import map_processing
from azure.core.exceptions import ResourceNotFoundError
import get_key
from create_containers import create_containers
from azure.storage.blob import BlobServiceClient

# Storage connection string used throughout instead of calling get_key() everywhere
STORAGE_CONNECTION_STRING = get_key.get_key()

def get_device_info_list():
    """
    Iterates through each Azure container, retrieves device data, and returns a list of device info.
    """
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    device_info_list = []

    for container in blob_service_client.list_containers():
        container_client = blob_service_client.get_container_client(container)
        
        for blob in container_client.list_blobs():
            blob_content = container_client.download_blob(blob).readall()
            lines = eval(blob_content)  # Convert the blob content to a Python object
            
            for line in lines:
                device_info_list.append({
                    'container_name': container.name,
                    'data': line.get('data', 'No additional data')
                })

    return device_info_list

# Index route
@app.route('/')
def index():
    
    # Creates additional storage containers upon startup
    container_names = ["map-storage", "processed-blobs"]
    create_containers(container_names, STORAGE_CONNECTION_STRING)
    
    # Initialize the map centered on Perth CBD
    m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)

    # Load the map path from storage
    map_path = map_processing.load_map_from_storage("base-station-0", "search_0", STORAGE_CONNECTION_STRING)
    
    # Retrieve device data from containers
    device_info_list = get_device_info_list()
    retrieve_from_containers(m, map_path, STORAGE_CONNECTION_STRING)

    # Pass device data and container names to the template
    return render_template('index.html', device_data=device_info_list, container_names=[c.name for c in BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING).list_containers()])

@app.route('/api/update-map', methods=['POST'])
def update_map():
    container_name = request.args.get('container')  # Get the selected container name from the request

    # Re-initialize the Folium map centered on Perth CBD
    m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)
    
    # Load the map path from the selected container
    map_path = map_processing.load_map_from_storage(container_name, "search_0", STORAGE_CONNECTION_STRING)

    # Retrieve data and update the map
    # device_info_list = retrieve_from_containers(m, map_path, STORAGE_CONNECTION_STRING)
    
    # Save the updated map to a new HTML file
    output_map_path = os.path.join('static', f'{container_name}_map.html')
    m.save(output_map_path)
    
    # Return the path to the updated map
    return jsonify({"status": "success", "map_path": output_map_path})

