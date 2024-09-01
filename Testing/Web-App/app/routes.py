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

# Index route
@app.route('/')
def index():
    
    # Creates default storage containers upon startup (for historical data)
    container_names = ["map-storage", "processed-blobs"]
    create_containers(container_names, STORAGE_CONNECTION_STRING)
    
    # Initialize the map centered on Perth CBD
    m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)

    # Load the map path from storage
    # map_path = map_processing.load_map_from_storage("base-station-0", "search_0", STORAGE_CONNECTION_STRING)
    
    # Retrieve device data from containers
    retrieved_data = retrieve_from_containers(m, STORAGE_CONNECTION_STRING)

    # Pass device data and container names to the template
    return render_template('index.html', device_data=retrieved_data, container_names=[c.name for c in BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING).list_containers()])

@app.route('/api/update-map', methods=['POST'])
def update_map():
    container_name = request.args.get('container')  # Get the selected container name from the request

    # Re-initialize the Folium map centered on Perth CBD
    m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)
    
    # Retrieve data and update the map
    retrieved_data = retrieve_from_containers(m, STORAGE_CONNECTION_STRING)
    
    # Save the updated map to a new HTML file
    output_map_path = os.path.join('static', f'{container_name}.html')
    # m.save(output_map_path)
    return jsonify({'message': 'Map updated successfully!', 'map_path': output_map_path})

