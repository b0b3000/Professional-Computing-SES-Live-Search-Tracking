from flask import render_template, jsonify, current_app as app
import os
import folium
import retrieve_from_container, upload_storage_container

# Index route
@app.route('/')
def index():
    current_dir = os.path.dirname(__file__)
    map_path = os.path.join(current_dir, 'static', 'footprint.html')
    m = folium.Map((-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)
    retrieve_from_container.retrieve_from_containers(m, map_path)
    return render_template('index.html')

@app.route('/api/update-map', methods=['POST'])
def update_map():
    current_dir = os.path.dirname(__file__)  # Get the current directory
    map_path = os.path.join(current_dir, 'static', 'footprint.html')  # Define the path to save the map

    # Re-initialize the Folium map to ensure new data is added
    m = folium.Map(location=(-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)
    
    # Retrieve new data and update the map
    retrieve_from_container.retrieve_from_containers(m, map_path)
    
    # Return a success message after updating the map
    return jsonify({"status": "success", "message": "Map updated with new data"})

@app.route('/api/push-data', methods=['POST'])
def push_data_to_server():
    try:
        upload_storage_container.startup()
        return jsonify({"status": "success", "message": "Data pushed to Azure successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

