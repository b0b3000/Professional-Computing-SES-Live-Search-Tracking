# Following the Google Python style guide, especially for docstrings:
# https://google.github.io/styleguide/pyguide.html

import folium
import numpy as np
import os

def startup():
    """Starts the program, initialises the map, then listens for input from the server.
    
    Because we haven't got the server running yet, the input will just be simulated.
    """
    current_dir = os.path.dirname(__file__)
    path = os.path.join(current_dir, 'footprint.html')              # Find correct location to store map.

    m = folium.Map((-31.870650, 116.095986), control_scale=True, zoom_start=16)     # Arbitrary location in John Forrest National Park.

    # Creates the grid overlay.
    grid = []
    lat_interval, lon_interval = 0.01, 0.01             # Change for different grid sizes.
    for lat in np.arange(-33, -30, lat_interval):
        grid.append([[lat, -180], [lat, 180]])
    for lon in np.arange(114, 118, lon_interval):
        grid.append([[-90, lon], [90, lon]])
    for g in grid:
        folium.PolyLine(g, color='black', weight=0.5, opacity=0.5).add_to(m)

    print('\nMap initialised.\n')
    
    m = create_trail(m, (-31.872236, 116.093924))
    m.save(path)


def create_trail(m, trail_start: tuple):
    """Creates a new trail start and adds it to the map
    
    Returns:
        A tuple of the device number, the trail number, a new group object, 
        and a list of trail coordinates containing just the first point.
    """
    group_0 = folium.FeatureGroup(name='Group 0').add_to(m)
    
    folium.Marker(
        location=(-31.872236, 116.093924),
        tooltip='Marker 1',
        icon=folium.Icon('orange')
    ).add_to(group_0)

    folium.LayerControl().add_to(m)             # Enables viewing controls for different groups of markers.

    return m


# Startup the program.
startup()
