"""
Routes:
    - index(): Renders the index.html template and passes device data to it.
    - update_map(): Updates the map with new data and returns a success message.
    - push_data_to_server(): Pushes data to Azure storage container and returns a success message. (Testing Purposes).
    
Written by Susheel Utagi, Lilee Hammond

"""


from flask import render_template, jsonify, current_app as app
import os
import folium
import retrieve_from_container
# from Azure_Testing import retrieve_from_container - fred's
import map_processing
from azure.core.exceptions import ResourceNotFoundError
import get_key
from create_containers import create_containers


# Storage connection string used throughout instead of calling get_key() everywhere
STORAGE_CONNECTION_STRING = get_key.get_key()

# Index route
@app.route('/')
def index():
    
    # Creates additional storage containers upon startup
    container_names = ["map-storage", "processed-blobs"]
    create_containers(container_names, STORAGE_CONNECTION_STRING)
    
    # try:
    #     # Attempt to load the existing map from Azure Blob Storage
    #     map_path = map_processing.load_map_from_storage("map-storage", "latest_map", STORAGE_CONNECTION_STRING)
    #     m = folium.Map(location=(-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)
    
    # except ResourceNotFoundError:
        
    #     # If the map doesn't exist, create a default map
    #     print("Map not found in Azure Blob Storage. Creating a default map.")
        
    #     # Save default map to Azure Storage
    #     m = folium.Map(location=(-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)
    #     map_path = 'default_map.html'
    #     m.save(map_path)
    #     map_processing.save_map_to_storage(map_path, "map-storage", "latest_map", STORAGE_CONNECTION_STRING)

    m = folium.Map(location=(-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)
    map_path = map_processing.load_map_from_storage("base-station-0", "search_0", STORAGE_CONNECTION_STRING)
    device_data = retrieve_from_container.retrieve_from_containers(m, map_path, STORAGE_CONNECTION_STRING)

    # Pass device data to template
    return render_template('index.html', device_data=device_data)

@app.route('/api/update-map', methods=['POST'])
def update_map():
    
    # Load the existing map from Azure Blob Storage
    map_path = map_processing.load_map_from_storage("map-storage", "latest_map", STORAGE_CONNECTION_STRING)

    # Re-initialize the Folium map to ensure new data is added
    m = folium.Map(location=(-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)
    
    # Retrieve new data and update the map
    retrieve_from_container.retrieve_from_containers(m, map_path, STORAGE_CONNECTION_STRING)
    
    # Return a success message after updating the map
    return jsonify({"status": "success", "message": "Map updated with new data"})


