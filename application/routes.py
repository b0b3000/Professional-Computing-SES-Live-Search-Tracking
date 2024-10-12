"""
Routes:
    - index(): Renders the index.html template and passes device data to it.
    - update_map(): Updates the map with new data and returns a success message.
    - push_data_to_server(): Pushes data to Azure storage container and returns a success message. (Testing Purposes).
"""

import traceback
import json
import os
from flask import render_template, request, url_for, current_app as app, jsonify, send_file, session
import folium
from retrieve_from_containers import retrieve_from_containers, historical_data_to_map
import get_key
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import historical_database
from to_gpx import convert_json_to_gpx_string

STORAGE_CONNECTION_STRING = get_key.get_blob_storage_key()


@app.route("/")
def index():
    """Default view for home page of web inteface. 

        Performs several "start-up" functions; rendering a default Folium map, connecting to
        the Azure storage container and retrieving container names, and retrieving historical
        search data.

        Returns:
        render_template: Renders the "index.html" template with:
            - active_map_html (html): Representation of the active map.
            - historical_map_hhtml (html): Representation of the historical map.
            - container_names (list): Active container names from Azure.
            - base_stations (list): Unique base stations for historical searches.
            - historical_searches (list): Historical search data.
    """
    # Initialises the active map and the historical map.
    active_map = folium.Map(location=(-31.9775, 115.8163), control_scale=True, zoom_start=17)
    historical_map = folium.Map(location=(-31.9775, 115.8163), control_scale=True, zoom_start=17)
    
    # Fetches names of available base stations from Azure (for live searches).
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    container_names = [container.name for container in blob_service_client.list_containers()]

    # Fetches unique base stations (for historical searches).
    try:
        base_stations = historical_database.get_unique_base_stations()
    except Exception as e:
        print(f"Error fetching base stations: {e}")
        base_stations = []

    try:    # Fetches historical searches for the scrollable list.
        historical_searches = get_presentable_historical_data(base_stations)

    except Exception as e:
        print(f"Error fetching historical searches: {e}")
        historical_searches = []

    # Saves both maps.
    active_map_save_path = os.path.join(os.path.dirname(__file__), "static/footprint.html")
    active_map.save(active_map_save_path)
    historical_map_save_path = os.path.join(os.path.dirname(__file__), "static/historical_map.html")
    historical_map.save(historical_map_save_path)
    
    # Renders the "index.html" template with both maps and all data collected.
    return render_template(
        "index.html",
        active_map_html=active_map._repr_html_(),
        historical_map_html=historical_map._repr_html_(),
        container_names=container_names,
        base_stations=base_stations,
        historical_searches=historical_searches)


@app.route("/api/update-map", methods=["POST"])
def update_map():
    """Fetches new data and updates the active map based on user selection.

    Called when the user clicks the "fetch_data" button, retrieves data from the specified containers. 
    The newly obtained data is stored in a global dictionary for later use, overwriting any old data.
    Uploads the newly retrieved data to the historical database.

    Returns:
        jsonify: A JSON response containing:
            - map_path (str): URL of the updated map file.
            - telemetry_data (list): The telemetry data retrieved from the containers.

    Raises:
        400: If no containers are selected by the user.
    """
    data = request.get_json()
    container_names = data.get("containers")
    if not container_names:
        return jsonify({"error": "No containers selected"}), 400

    active_map = folium.Map(location=(-31.9775, 115.8163), control_scale=True, zoom_start=17)
    active_map_save_path = os.path.join(os.path.dirname(__file__), "static/footprint.html")
    
    telemetry_data, all_blobs = retrieve_from_containers(active_map, STORAGE_CONNECTION_STRING, container_names, active_map_save_path)

    session["base_stations"] = list(all_blobs.keys())    # Updates session-specific GPS data
    # Replaces existing row in the database.
    update_dict = dict(
        start_time=session["start_time"], 
        session_id=session["session_id"], 
        gps_data=all_blobs
        )

    # Upload the latest retrieved data to the historical database.
    historical_database.upload_search_data(update_dict, True)

    # Returns a response indicating where the updated map is saved, and telemetry data from selected containers.
    return jsonify({
        "map_path": url_for("static", filename="footprint.html"),
        "telemetry_data": telemetry_data
    })


@app.route("/api/start-search", methods=["POST"])
def start_search():
    """Starts a new search session for the user.

    Allocates a unique session ID for the search based on the current timestamp,
    both of which are stored in the Flask session.

    Returns:
        jsonify: A JSON response containing:
            - message (str): Confirmation that the search has started.
            - session_id (str): The unique ID assigned to the current search session.
    """
    session_id = datetime.now().strftime("%Y%m%d%H%M%S")
    session["session_id"] = session_id
    session["start_time"] = datetime.now().strftime("%H:%M:%S")
    
    return jsonify({"message": "Search started", "session_id": session_id})


@app.route("/api/end-search", methods=["POST"])
def end_search():
    """Ends the current search session for the user.

    Allows the user to indicate a search has concluded. Stops data collection, prepares 
    the collected GPS data into GPX strings, and stores the GPX data in a dictionary 
    for further processing. The session data is cleared after the search ends.

    Returns:
        jsonify: A JSON response containing:
            - message (str): Confirmation that the search has ended.
            - gpx_download_routes (list): Filenames for the saved GPX files.

    Raises:
        400: If there is no active search session or no GPS data to convert.
    """
    # Gets session ID variables.
    session_id = session.get("session_id")
    if not session_id:
        return jsonify({"error": "No active search session"}), 400
    
    end_time_dt = datetime.now().strftime("%H:%M:%S")
    search_date_dt = datetime.now().strftime("%Y-%m-%d")
    json_gps_data = historical_database.get_live_searches(session["session_id"], session["base_stations"])

    if not json_gps_data:
        return jsonify({"error": "No GPS data to convert"}), 400

    # Translates all blobs into GPX strings and stores them in a dictionary.
    gpx_data_dict = {}
    for blob_name, blob_content in json_gps_data.items():

        # TODO: Comment this back in to delete containers after a search is ended.
        # blob_service_client.delete_container(blob_name)

        try:
            if isinstance(blob_content, bytes):
                decoded_content = blob_content.decode("utf-8")
            else:
                decoded_content = blob_content
            json_data = json.loads(decoded_content.replace(""", """))
             
            gpx_string = convert_json_to_gpx_string(json_data)
            gpx_data_dict[blob_name] = gpx_string

        except Exception as e:
            print(f"Error converting blob '{blob_name}' to GPX: {e}")
            traceback.print_exc()
    
    # Uploads the search data to the historical database.
    update_db_dict = dict(
        session_id = session["session_id"],
        start_time = session["start_time"],
        end_time = end_time_dt,
        search_date = search_date_dt,
        gpx_data = gpx_data_dict,
        gps_data = json_gps_data

    )
    historical_database.upload_search_data(update_db_dict)

    # Creates download links for the GPX files.
    gpx_filenames = []
    for gpx in gpx_data_dict:
        filename = f"{gpx}.gpx"
        gpx_filenames.append(filename)
        with open(filename, "w") as outfile:
            outfile.write(gpx_data_dict[gpx])

    # Clears global dict, ready for the next search.
    session.pop("session_id", None)
    session.pop("start_time", None)
    session.pop("base_stations", None)
    print("SEARCH ENDED, ", gpx_filenames)

    return jsonify({"message": "Search ended", "gpx_download_routes" : gpx_filenames})


@app.route("/render-map")
def render_map():
    """Renders a map with historical GPS data for a specific session and base station.

    Retrieves live GPS data based on the provided session ID and base station from the historical database. 
    If GPS data is available, it initializes a Folium map, plots the GPS points, and saves the map as an HTML file.

    Args:
        session_id (str): The ID of the current session.
        base_station (str): The base station from which to retrieve GPS data.

    Returns:
        jsonify: A JSON response containing:
            - map_path (str): The URL of the rendered historical map.
        
    Raises:
        400: If no GPS data is available for the provided session ID and base station.
    """
    session_id = request.args.get("session_id")
    base_station = request.args.get("base_station")
    
    gps_data = historical_database.get_live_searches(session_id, [base_station])
    if not gps_data:
        return jsonify({"error": "No GPS data to convert"}), 400
    
    # Ensures the GPS data is in the correct formats
    gps_points = json.loads(gps_data[base_station])

    # Initialises map and plots the GPS points onto it.
    m = folium.Map(location=(-31.9775, 115.8163), control_scale=True, zoom_start=17)
    map_save_path = os.path.join(os.path.dirname(__file__), "static/historical_map.html")
    historical_data_to_map(m, gps_points, map_save_path)
    m.save(map_save_path)

    return jsonify({
        "map_path": url_for("static", filename="/historical_map.html"),
    })


@app.route("/download/<filename>")
def download_gpx(filename):
    """Serves a GPX file for download.

    Checks if the specified GPX file exists in the current working directory. 
    If the file is found, it is sent to the client as an attachment for download.
    If the file does not exist, a 404 error message is returned.

    Args:
        filename (str): The name of the GPX file to be downloaded.

    Returns:
        send_file (.txt): The GPX file sent as an attachment if found.
        jsonify (JSON): A JSON response containing an error message if the file is not found.

    Raises:
        404: If the specified file does not exist in the current working directory.
    """
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404


@app.route("/filter-search", methods=["POST"])
def submit_date():
    """Filters historical search data based on date range and selected base stations.

    Retrieves the start and end dates, along with the selected base stations from the web app's form input. 
    Fetches the relevant historical search data based on these inputs and returns the results in a JSON format.

    Args:
        start_date (str): The starting date for filtering historical searches.
        end_date (str): The ending date for filtering historical searches.
        selected_base_stations (list): A list of base stations selected by the user.

    Returns:
        jsonify (JSON): A JSON response containing the filtered historical search data.

    Raises:
        400: If the input dates are invalid or if no data is found for the specified filters.
    """
    start_date = request.form.get("start-date")
    end_date = request.form.get("end-date")
    selected_base_stations = request.form.getlist("base-station")
    serializable_results = get_presentable_historical_data(selected_base_stations, start_date, end_date)

    return jsonify(serializable_results)


@app.route('/filter-pings', methods=['POST'])
def filter_pings():
    """
    Filter pings stored in the database before a given time. (this is the time user clicks on filter button)
    This will create a foloium map with only the pings that occur after the specified time.
    """
    filter_time_str = request.form.get('filter_time') # time given will be the time that filter button is clicked
    if not filter_time_str:
        return jsonify({'error': 'No filter time provided'}), 400

    try:
        filter_time = datetime.strptime(filter_time_str, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format. Expected format: %Y-%m-%dT%H:%M:%S'}), 400
    base_stations = session.get('base_stations', [])
    session_id = session.get('session_id')
    if not base_stations or not session_id:
        return jsonify({'error': 'No active session or base stations available'}), 400

    # Query the database to retrieve only the pings after the filter time
    filtered_pings = {}
    for base_station in base_stations:
        pings = historical_database.get_pings_after_time(session_id, base_station, filter_time)
        if pings:
            filtered_pings[base_station] = pings

    # Create new map with the filtered pings and return its path for rendering
    active_map = folium.Map(location=(-31.9775, 115.8163), control_scale=True, zoom_start=17)
    for base_station, pings in filtered_pings.items():
        for ping in pings:
            folium.Marker(
                location=(ping['lat'], ping['lon']),
                popup=f"Time: {ping['time']}<br>Base: {base_station}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(active_map)
    active_map_save_path = os.path.join(os.path.dirname(__file__), 'static/footprint_filtered.html')
    active_map.save(active_map_save_path)
    return jsonify({
        "map_path": url_for('static', filename='footprint_filtered.html'),
        "message": "Pings filtered successfully."
    })


def get_presentable_historical_data(selected_base_stations, start_date="2024-01-01", end_date="9999-01-01"):
    """Retrieves and formats historical search data for presentation.

    Fetches historical search data from database based on selected base stations and specified date range. 
    Then converts the results into a format suitable for serialisation and includes download links for GPX files.

    Args:
        selected_base_stations (list): A list of base stations to filter the search data.
        start_date (str, optional): The starting date for filtering results. Defaults to "2024-01-01".
        end_date (str, optional): The ending date for filtering results. Defaults to "9999-01-01".

    Returns:
        list: A list of tuples containing formatted historical search data, including:
            - ID (str): The search ID.
            - Base station (str): The name of the base station.
            - Start time (str): The formatted start time of the search.
            - End time (str): The formatted end time of the search.
            - Search date (str): The formatted date of the search.
            - Download link (str): An HTML link to download the GPX data file.
            - Display button (str): An HTML button for displaying historical data.
            - GPS data (any): The raw GPS data associated with the search.

    Raises:
        IOError: If there is an error writing the GPX data to a file.
    """
    results = historical_database.get_historical_searches(start_date, end_date, selected_base_stations)
    
    # Converts results to serialisable format.
    serializable_results = []
    for row in results:

        filename = f"{row[0]}.gpx"    # Contains search ID for file name.
        with open(filename, "w") as outfile:
            if type(row[6]) == str:
                outfile.write(row[6])    # 'row[6]' is GPX data.

        serializable_row = (
            row[0],  # Assuming ID is already a string.
            row[1],  # Base station.
            row[2].strftime("%H:%M:%S"),  # Converts time to string.
            row[3].strftime("%H:%M:%S"),  # Converts time to string.
            row[4].strftime("%Y-%m-%d"),  # Converts date to string.
            f"<a href='/download/{filename}' download='{filename}'>Download Data</a>"    # Download link.
            f"<button id='display-historical-button'>Display</button>",    # Button.
            row[5]    # GPS data.
        )
        serializable_results.append(serializable_row)
    
    return serializable_results