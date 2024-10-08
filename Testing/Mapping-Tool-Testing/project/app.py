from flask import Flask, render_template, request, url_for, flash, redirect
import folium
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        """Loads the map and embeds it on the main page"""
        m = folium.Map((-31.870650, 116.095986), control_scale=True, zoom_start=16) 

        # Sets the iframes width and height.
        m.get_root().width = '800px'
        m.get_root().height = '600px'

        # Creates the grid overlay.
        grid = []
        lat_interval, lon_interval = 0.01, 0.01     # Change for different grid sizes.
        for lat in np.arange(-33, -30, lat_interval):
            grid.append([[lat, -180], [lat, 180]])
        for lon in np.arange(114, 118, lon_interval):
            grid.append([[-90, lon], [90, lon]])
        for g in grid:
            folium.PolyLine(g, color='black', weight=0.5, opacity=0.5).add_to(m)

        group_0 = folium.FeatureGroup(name='Group 0').add_to(m)
        folium.Marker(
            location=(-31.872236, 116.093924),
            tooltip='Marker 1',
            icon=folium.Icon('orange')
        ).add_to(group_0)
        folium.Marker(
            location=(-31.871953, 116.094601),
            tooltip='Marker 1',
            icon=folium.Icon('orange')
        ).add_to(group_0)
        folium.Marker(
            location=(-31.872500, 116.095320),
            tooltip='Marker 1',
            icon=folium.Icon('orange')
        ).add_to(group_0)
        folium.Marker(
            location=(-31.871297, 116.095813),
            tooltip='Marker 1',
            icon=folium.Icon('orange')
        ).add_to(group_0)
        folium.Marker(
            location=(-31.872136, 116.096747),
            tooltip='Marker 1',
            icon=folium.Icon('orange')
        ).add_to(group_0)
        folium.Marker(
            location=(-31.872391, 116.097917),
            tooltip='Marker 1',
            icon=folium.Icon('orange')
        ).add_to(group_0)

        trail_coordinates = [
            (-31.872236,116.093924),
            (-31.871953,116.094601),
            (-31.872500,116.095320),
            (-31.871297,116.095813),
            (-31.872136,116.096747),
            (-31.872391,116.097917)
        ]
        folium.PolyLine(trail_coordinates, tooltip='Group 0').add_to(m)
        iframe = m.get_root()._repr_html_()

        return render_template('map_webpage.html', iframe=iframe)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)