"""
Routes:
    - index(): Renders the index.html template and passes device data to it.
    - update_map(): Updates the map with new data and returns a success message.
    - push_data_to_server(): Pushes data to Azure storage container and returns a success message. (Testing Purposes).
    
Written by Susheel Utagi, Lilee Hammond
"""

from flask import render_template, request, url_for, current_app as app, request
import os
import folium
from retrieve_from_containers import retrieve_from_containers
from azure.core.exceptions import ResourceNotFoundError
import get_key
from azure.storage.blob import BlobServiceClient

# Storage connection string used throughout instead of calling get_key() everywhere
STORAGE_CONNECTION_STRING = get_key.get_key()

# Index route to render the form and map
@app.route('/')
def index():
    # Initialize the map centered on Perth CBD (for now)
    m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)
    
    # Retrieve container names from Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    container_names = [container.name for container in blob_service_client.list_containers()]

    # Save the initial map (empty) to be displayed on the page
    map_save_path = os.path.join(os.path.dirname(__file__), 'static/footprint.html')
    m.save(map_save_path)

    # Render the template with container names and the initial map
    return render_template('index.html', map_html=m._repr_html_(), container_names=container_names)

@app.route('/api/update-map', methods=['POST'])
def update_map():
    # Get the container name from the request
    container_name = request.args.get('container')
    
    # Initialize the map centered on Perth CBD
    m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)

    # Call retrieve_from_containers with the selected container
    retrieve_from_containers(m, STORAGE_CONNECTION_STRING, [container_name])

    # Save the updated map to a file
    map_save_path = os.path.join(os.path.dirname(__file__), 'static/footprint.html')
    m.save(map_save_path)

    # Return a response indicating where the updated map is saved
    return {"map_path": url_for('static', filename='footprint.html')}
