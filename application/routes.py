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
from flask import render_template, request, url_for, current_app as app, jsonify, send_file, Response, session
import folium
from retrieve_from_containers import retrieve_from_containers, retrieve_historical_data
import get_key
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import historical_database
from to_gpx import convert_json_to_gpx_string

STORAGE_CONNECTION_STRING = get_key.get_blob_storage_key()

def get_presentable_historical_data(selected_base_stations, start_date="2024-01-01", end_date="9999-01-01"):
    results = historical_database.get_historical_searches(start_date, end_date, selected_base_stations)
    
    # Convert results to serializable format
    serializable_results = []
    for row in results:

        filename = f'{row[0]}.gpx' # Contains search ID for file name  
        with open(filename, 'w') as outfile:

            if type(row[6]) == str:
                outfile.write(row[6]) # row[6] is GPX data

        serializable_row = (
            row[0],  # Assuming ID is already a string
            row[1],  # Base station
            row[2].strftime('%H:%M:%S'),  # Convert time to string
            row[3].strftime('%H:%M:%S'),  # Convert time to string
            row[4].strftime('%Y-%m-%d'),  # Convert date to string
            f"<a href='/download/{filename}' download='{filename}'>Download Data</a>", #Download Link
            f'<button id="display-historical-button">Display</button>', # Button"
            row[5] #GPS data
        )
        serializable_results.append(serializable_row)
    
    return serializable_results

@app.route('/')
def index():
    '''Default view for landing page of web inteface. This is where the user first gets taken on the app.
       Renders a blank folium map centered on UWA campus. 
       Establishes connection to Azure Server with secure connection string, and fetches active container names.
    '''

    # Initialize both maps: active and historical
    active_map = folium.Map(location=(-31.9775, 115.8163), control_scale=True, zoom_start=17)
    historical_map = folium.Map(location=(-31.9775, 115.8163), control_scale=True, zoom_start=17)
    
    # Getting available base stations from azure container, for live search
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    container_names = [container.name for container in blob_service_client.list_containers()]

    # Get base stations for historical searches
    try:
        base_stations = historical_database.get_unique_base_stations()
    except Exception as e:
        print(f"Error fetching base stations: {e}")
        base_stations = []

    # Save the initial map (empty) to be displayed on the page
    map_save_path = os.path.join(os.path.dirname(__file__), 'static/footprint.html')
    active_map.save(map_save_path)

    # Fetch historical searches for the scrollable list
    try:
        #historical_searches = historical_database.get_all_searches()
        historical_searches = get_presentable_historical_data(base_stations)

    except Exception as e:
        print(f"Error fetching historical searches: {e}")
        historical_searches = []

    # Save the maps to be displayed on the page
    active_map_save_path = os.path.join(os.path.dirname(__file__), 'static/active_map.html')
    active_map.save(active_map_save_path)

    historical_map_save_path = os.path.join(os.path.dirname(__file__), 'static/historical_map.html')
    historical_map.save(historical_map_save_path)
    
    # Render the template with maps and historical search data
    return render_template(
        'index.html',
        active_map_html=active_map._repr_html_(),
        historical_map_html=historical_map._repr_html_(),
        container_names=container_names,
        base_stations=base_stations,
        historical_searches=historical_searches)  # Pass the historical search data to the template


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

    active_map = folium.Map(location=(-31.9775, 115.8163), control_scale=True, zoom_start=17)
    active_map_save_path = os.path.join(os.path.dirname(__file__), 'static/footprint.html')
    
    telemetry_data, _, all_blobs = retrieve_from_containers(active_map, STORAGE_CONNECTION_STRING, container_names, active_map_save_path)

    # Update session-specific GPS data
    session['base_stations'] = list(all_blobs.keys())
    #replace existing row in DB
    update_dict = dict(
        start_time=session["start_time"], 
        session_id=session["session_id"], 
        gps_data=all_blobs
        )

    historical_database.upload_search_data(update_dict, True)


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

    # Store session data in Flask session
    session['session_id'] = session_id
    session['start_time'] = datetime.now().strftime('%H:%M:%S')
    
    return jsonify({'message': 'Search started', 'session_id': session_id})

@app.route('/api/end-search', methods=['POST'])
def end_search():
    """
    end_search:
    Function that allows a user to indicate when a search is over. Data will stop being collected and will be prepared into
    GPX strings. Stores the GPX data in a dictionary for further processing.
    """
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No active search session'}), 400

    end_time_dt = datetime.now().strftime('%H:%M:%S')
    search_date_dt = datetime.now().strftime('%Y-%m-%d')

    json_gps_data = historical_database.get_live_searches(session["session_id"], session["base_stations"])

    if not json_gps_data:
        return jsonify({'error': 'No GPS data to convert'}), 400

    # Translate all blobs into GPX string and store in a dictionary
    gpx_data_dict = {}
    for blob_name, blob_content in json_gps_data.items():
        try:
            if isinstance(blob_content, bytes):
                decoded_content = blob_content.decode('utf-8')
            else:
                decoded_content = blob_content
            json_data = json.loads(decoded_content.replace("'", '"'))
             
            gpx_string = convert_json_to_gpx_string(json_data) #replace back to
            gpx_data_dict[blob_name] = gpx_string

        except Exception as e:
            print(f"Error converting blob '{blob_name}' to GPX: {e}")
            traceback.print_exc()

    # Now we got a dict 'gpx_data_dict' containing GPX strings for each blob
    
    update_db_dict = dict(
        session_id = session["session_id"],
        start_time = session["start_time"],
        end_time = end_time_dt,
        search_date = search_date_dt,
        gpx_data = gpx_data_dict,
        gps_data = json_gps_data

    )
        
    historical_database.upload_search_data(update_db_dict)

    gpx_filenames = []
    for gpx in gpx_data_dict:
        # Save= GPX data to a file
        filename = f'{gpx}.gpx'
        gpx_filenames.append(filename)

        with open(filename, 'w') as outfile:
            outfile.write(gpx_data_dict[gpx])

    # Clear global dict ready for the next search
    session.pop('session_id', None)
    session.pop('start_time', None)
    session.pop('base_stations', None)
    print("SEARCH ENDED, ", gpx_filenames)
    return jsonify({'message': 'Search ended', 'gpx_download_routes' : gpx_filenames})


@app.route('/render-map')
def render_map():
    
    gps_data = request.args.get('gps')
    
    # Ensures the GPS data is in the correct format
    gps_points = json.loads(gps_data)  

    # Initialize map
    m = folium.Map(location=(-31.9775, 115.8163), control_scale=True, zoom_start=17)
    
    # Render GPS points
    map_save_path = os.path.join(os.path.dirname(__file__), 'static/historical_map.html')
    retrieve_historical_data(m, gps_points, map_save_path)

    # Save the map and render the template
    m.save(map_save_path)

    return jsonify({
        "map_path": url_for('static', filename='/historical_map.html'),
    })

# Route to serve the GPX ZIP file for download
@app.route('/download/<filename>')
def download_gpx(filename):
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/filter-search', methods=['POST'])
def submit_date():
    # These two values are from the inputs from the web app, index
    start_date = request.form.get('start-date')

    end_date = request.form.get('end-date')
    selected_base_stations = request.form.getlist('base-station')
    
    serializable_results = get_presentable_historical_data(selected_base_stations, start_date, end_date)

    return jsonify(serializable_results)