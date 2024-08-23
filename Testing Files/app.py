from flask import Flask, jsonify, render_template
import os
import folium
import retrieve_container

app = Flask(__name__)

@app.route('/')
def index():
    current_dir = os.path.dirname(__file__)
    map_path = os.path.join(current_dir, 'static', 'test_footprint.html')  # Save map to the static folder
    # Ensure map is updated
    m = folium.Map((-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)  # Create a new Folium map
    retrieve_container.update_map_with_data(m, map_path)
    return render_template('index.html')

@app.route('/api/gps-data')
def get_gps_data():
    data = retrieve_container.retrieve_from_containers() #needs paramters 'm' and 'path'
    return jsonify(data)
"""
@app.route('/api/telemetry')
def get_telemetry():"""
    


if __name__ == '__main__':
    app.run(debug=True)