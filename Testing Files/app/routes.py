from flask import render_template, jsonify, current_app as app
import os
import folium
import retrieve_container, upload_storage_container

# Index route
@app.route('/')
def index():
    current_dir = os.path.dirname(__file__)
    map_path = os.path.join(current_dir, 'static', 'test_footprint.html')
    m = folium.Map((-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)
    retrieve_container.update_map_with_data(m, map_path)
    return render_template('index.html')

# API route for GPS data
@app.route('/api/gps-data')
def get_gps_data():
    data = retrieve_container.retrieve_from_containers() # Adjust this as needed
    return jsonify(data)

@app.route('/api/push-data', methods=['POST'])
def push_data_to_server():
    try:
        upload_storage_container.startup()
        return jsonify({"status": "success", "message": "Data pushed to Azure successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

