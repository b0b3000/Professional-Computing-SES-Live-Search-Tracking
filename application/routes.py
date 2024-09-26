"""
Routes:
    - index(): Renders the index.html template and passes device data to it.
    - update_map(): Updates the map with new data and returns a success message.
    - push_data_to_server(): Pushes data to Azure storage container and returns a success message. (Testing Purposes).

Written by Susheel Utagi, Lilee Hammond
"""

import traceback
import json
import os
import shutil
import tempfile
from flask import render_template, request, url_for, current_app as app, jsonify, send_file, Response
import folium
from retrieve_from_containers import retrieve_from_containers
import get_key
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import historical_database
from to_gpx import convert_json_to_gpx_string

# TODO: TO BE UPDATED to Azure Vault Solution
STORAGE_CONNECTION_STRING = get_key.get_blob_storage_key()

# Global variable to store search session ID and data path, called when a user starts a search
search_session = {
    'session_id': None,
    'data_path': None,
    'search_date': None,
    'start_time': None,
    'end_time': None,
    'gps_data': {},
    'gpx_data': None
}

@app.route('/')
def index():
    '''Default view for landing page of web inteface. This is where the user first gets taken on the app.
       Renders a blank folium map centered on UWA campus. 
       Establishes connection to Azure Server with secure connection string, and fetches active container names.
    '''

    m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    container_names = [container.name for container in blob_service_client.list_containers()]

    # Retrieve unique base stations from the database
    try:
        base_stations = historical_database.get_unique_base_stations()
    except Exception as e:
        print(f"Error fetching base stations: {e}")
        base_stations = []

    # Save the initial map (empty) to be displayed on the page
    map_save_path = os.path.join(os.path.dirname(__file__), 'static/footprint.html')
    m.save(map_save_path)

    # Render the template with container names and map
    return render_template(
        'index.html',
        map_html=m._repr_html_(),
        container_names=container_names,
        base_stations=base_stations,  # Pass base stations to the template
    )

# Updates the map with new data when it is called
@app.route('/api/update-map', methods=['POST'])
def update_map():
    '''
    When user elects to fetch new data through fetch_data button, this function does so by calling external function.
    updates the nely obtained data in global dictionary for later use.
    Old data is overwritten each update with newly fetched data.
    '''
    data = request.get_json()
    container_names = data.get('containers')
    if not container_names:
        return jsonify({'error': 'No containers selected'}), 400

    m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)
    telemetry_data, _, all_blobs = retrieve_from_containers(m, STORAGE_CONNECTION_STRING, container_names)

    # Update global dict with newly obtained data
    search_session['gps_data'] = all_blobs

    # Return a response indicating where the updated map is saved and include telemetry data
    return jsonify({
        "map_path": url_for('static', filename='footprint.html'),
        "telemetry_data": telemetry_data
    })


@app.route('/api/start-search', methods=['POST'])
def start_search():
    """
    start_search:
    Function that allows a user to start a search. Once a search is started, a session is allocated a session_id.
    All data from that search are saved into the data path.
    """
    session_id = datetime.now().strftime('%Y%m%d%H%M%S')
    search_session['session_id'] = session_id
    search_session['search_date'] = datetime.now().strftime('%Y-%m-%d')
    search_session['start_time'] = datetime.now().strftime('%H:%M:%S')
    return jsonify({'message': 'Search started', 'session_id': session_id})

@app.route('/api/end-search', methods=['POST'])
def end_search():
    """
    end_search:
    Function that allows a user to indicate when a search is over. Data will stop being collected and will be prepared into
    GPX strings. Stores the GPX data in a dictionary for further processing.
    """
    session_id = search_session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No active search session'}), 400

    search_session['end_time'] = datetime.now().strftime('%H:%M:%S')
    gps_data = search_session.get('gps_data')
    if not gps_data:
        return jsonify({'error': 'No GPS data to convert'}), 400

    # Translate all blobs into GPX string and store in a dictionary
    gpx_data = {}
    for blob_name, blob_content in gps_data.items():
        try:
            if isinstance(blob_content, bytes):
                decoded_content = blob_content.decode('utf-8')
            else:
                decoded_content = blob_content
            json_data = json.loads(decoded_content.replace("'", '"'))
            gpx_string = convert_json_to_gpx_string(json_data)
            gpx_data[blob_name] = gpx_string
        except Exception as e:
            print(f"Error converting blob '{blob_name}' to GPX: {e}")
            traceback.print_exc()

    # Now we got a dict 'gpx_data' containing GPX strings for each blob
    # TODO: ship these gpx strings off to azure database.
    # TODO: make them into a file and allow the user to download the files (zip all gpx files for a single search)
    search_session['gpx_data'] = gpx_data
    for gpx in gpx_data:
        print(gpx_data[gpx])

        # Save= GPX data to a file
        with open(f'{gpx}.gpx', 'w') as outfile:
            outfile.write(gpx_data[gpx])

         

    # Save search data to the database (pass gpx_data if needed)
    historical_database.upload_search_data(search_session)

    # Clear global dict ready for the next search
    search_session['gps_data'] = {}
    search_session['gpx_data'] = {}
    search_session['session_id'] = None
    search_session['start_time'] = None
    search_session['end_time'] = None
    search_session['search_date'] = None
    return jsonify({'message': 'Search ended'})

# Route to serve the GPX ZIP file for download
@app.route('/download/<filename>')
def download_gpx(filename):
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/submit-date', methods=['POST'])
def submit_date():
    # These two values are from the inputs from the web app, index
    start_date = request.form.get('start-date')
    end_date = request.form.get('end-date')

    # This needs to correlate with the base containers that have shown up in history, index.html controls this
    selected_base_stations = request.form.getlist('base-station')

    results = historical_database.get_historical_searches(start_date, end_date, selected_base_stations)
    print("Testing: Retrieved search data", results, flush=True)

    return "Check the terminal for the input values!"
