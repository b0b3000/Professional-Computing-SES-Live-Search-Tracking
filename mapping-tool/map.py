# Following the Google Python style guide, especially for docstrings:
# https://google.github.io/styleguide/pyguide.html

import folium
import numpy as np
import os

def startup():
    """Starts the program, initialises the map, then listens for input from the server.
    
    Because we haven't got the server running yet, the input will just be simulated.
    """
    devices = []
    trails = []

    current_dir = os.path.dirname(__file__)
    path = os.path.join(current_dir, 'footprint.html')      # Find correct location to store map.

    # For a more monochrome map: tiles="cartodb positron".
    map1 = folium.Map((-31.870650, 116.095986), control_scale=True, zoom_start=16)    # Arbitrary location in John Forrest National Park.
    # Enables viewing controls for different groups of markers.
    folium.LayerControl().add_to(map1)

    # Creates the grid overlay.
    grid = []
    lat_interval, lon_interval = 0.01, 0.01     # Change for different grid sizes.
    for lat in np.arange(-33, -30, lat_interval):
        grid.append([[lat, -180], [lat, 180]])
    for lon in np.arange(114, 118, lon_interval):
        grid.append([[-90, lon], [90, lon]])
    for g in grid:
        folium.PolyLine(g, color='black', weight=0.5, opacity=0.5).add_to(map1)

    map1.save(path)
    print('\nMap initialised.\n')
    
    # Simulates the server input:

    print('Connected to a device: Device 0, <more device details>.\n')
    devices.append(("Device 1", "<device_details>"))        # Add a tuple of device details to the list of all devices.
    print('Ping from <device_name>: "-31.872236, 116.093924".\n')
    
    # This part doesn't work right now!
    # map1, new_trail = create_trail(map1, path, 0, 0, (-31.872236, 116.093924))    # Create a new trail for this search.
    # trails.append(new_trail)


def create_trail(map1, path: str, device_num: int, trail_num: int, trail_start: tuple):
    """Creates a new trail start and adds it to the map
    
    Returns:
        A tuple of the device number, the trail number, a new group object, 
        and a list of trail coordinates containing just the first point.
    """
    group_0 = folium.FeatureGroup(name='Group 0').add_to(map1)
    
    folium.Marker(
        location=(-31.872236, 116.093924),
        tooltip='Marker 1',
        icon=folium.Icon('orange')
    ).add_to(group_0)
    
    trail = (device_num, trail_num, group_0, trail_start)
    return map1, trail

def extend_trail(m, trail_extend: tuple) -> list:
    # folium.PolyLine(trail_coords, tooltip='trail', color='red', smoothfactor=0).add_to(m)
    return 0


def create_markers(m):
    """
    Creates a group of markers.
    """
    group_1 = folium.FeatureGroup(name='Group 1').add_to(m)

    folium.Marker(
        location=(-31.973088, 116.257886),
        tooltip='Marker 1',
        icon=folium.Icon('orange')
    ).add_to(group_1)

    folium.Marker(
        location=(-31.973489, 116.254536),
        tooltip='Marker 2',
        icon=folium.Icon('range')
    ).add_to(group_1)


# Startup the program.
startup()
