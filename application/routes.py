"""
Routes:
    - index(): Renders the index.html template and passes device data to it.
    - update_map(): Updates the map with new data and returns a success message.
    - push_data_to_server(): Pushes data to Azure storage container and returns a success message. (Testing Purposes).
    
Written by Susheel Utagi, Lilee Hammond
"""

from flask import render_template, request, url_for, current_app as app, request, jsonify, send_file, session
import os
import folium
from retrieve_from_containers import retrieve_from_containers
import get_key
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import shutil
import historical_database


#TODO: TO BE UPDATED to Azure Vault Solution
STORAGE_CONNECTION_STRING = get_key.get_blob_storage_key()

# Global variable to store search session ID and data path, called when a user starts a search
search_session = {
    'session_id': None,
    'data_path': None,
    'start_time': None,
    'end_time': None,
    'gps_data': {},
    'gpx_data': None
}

# Index route to render the form and map
@app.route('/')
def index():
    
    # TODO: Parameters passed for initialising a map, currently map centered on Perth CBD
    m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)
    
    # Retrieve container names from Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    container_names = [container.name for container in blob_service_client.list_containers()]
    
    # Save the initial map (empty) to be displayed on the page
    map_save_path = os.path.join(os.path.dirname(__file__), 'static/footprint.html')
    m.save(map_save_path)

    # Render the template with container names and map
    return render_template(
        'index.html',
        map_html=m._repr_html_(),
        container_names=container_names,
    )

# Updates the map with new data when it is called 
@app.route('/api/update-map', methods=['POST'])
def update_map():
    
    # Get the container names from the request body
    data = request.get_json()
    container_names = data.get('containers')

    if not container_names:
        return jsonify({'error': 'No containers selected'}), 400

    # Initialize a map
    m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)
    telemetry_data, _, all_blobs = retrieve_from_containers(m, STORAGE_CONNECTION_STRING, container_names)

    # Update the global search session with new GPS data
    search_session['gps_data'] = all_blobs

    #m.save(os.path.join(os.path.dirname(__file__), 'static/footprint.html'))
    # Return a response indicating where the updated map is saved and include telemetry data
    return jsonify({
        "map_path": url_for('static', filename='footprint.html'),
        "telemetry_data": telemetry_data
    })


@app.route('/api/start-search', methods=['POST'])
def start_search():
    
    """ 
    start_search:
    Function that allows a user to start a search. Once a search is started a session is started
    and allocated a session_id. All data from that search are saved into the data path.
    """
    session_id = datetime.now().strftime('%Y%m%d%H%M%S')
    search_session['session_id'] = session_id
    search_session['data_path'] = f'search_data/{session_id}' # unsure if this is needed
    search_session['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Record start time

    return jsonify({'message': 'Search started', 'session_id': session_id})

@app.route('/api/end-search', methods=['POST'])
def end_search():
    
    """ 
    end_search:
    Function that allows a user to indicate when a search is over, data will stop being collected and will be prepared into 
    a .gpx file. Provides a donwload link for the .gpx file.
    
    """
    search_session['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    session_id = search_session.get('session_id')
    data_path = search_session.get('data_path')

    if not session_id or not data_path:
        return jsonify({'error': 'No active search session'}), 400

    # Save collected data into a .gpx file (use parsing function here)
    # use jacks code to convert json to gpx.
    """
    gpx_file_path = os.path.join(data_path, 'search_data.gpx')
    with open(gpx_file_path, 'w') as gpx_file:
        # TODO: Use parsing function to save data in GPX format
        gpx_file.write('''<?xml version="1.0" encoding="UTF-8"?>
        <gpx version="1.1" creator="GPS Data">
        <!-- GPX Data goes here -->
        </gpx>''')

    # Optionally move or compress the data for storage
    shutil.make_archive(data_path, 'zip', data_path) #Dont know if this is necessary or what its even doing?

    # Provide a download link for the user
    download_url = f'/download/{session_id}.zip'
    """
    #Generates and executes SQL query to add a row to the database for each base station in query. See historical_database.py
    historical_database.upload_search_data(search_session)

    # Reset the search session
    search_session.clear()
    return jsonify({'message': 'Search ended', 'gpx_download_url': 'download_url'})

# Route to serve the GPX file for download
@app.route('/download/<session_id>.zip')
def download_gpx(session_id):
    data_path = f'search_data/{session_id}.zip'
    if os.path.exists(data_path):
        return send_file(data_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404


