import folium
import numpy as np
import os


def initialise_map():
    """
    Initialises a map with various arguments
    :return: map object
    """
    # For a more monochrome map: tiles="cartodb positron"
    m = folium.Map((-31.9714, 116.2562), control_scale=True, zoom_start=15)
    return m


def create_trail(m):
    """
    Creates a trail
    """
    trail_coords = [
        (-31.969518, 116.259844),
        (-31.969388, 116.259662),
        (-31.969133, 116.259061),
        (-31.968996, 116.258408),
        (-31.968852, 116.255267),
        (-31.965284, 116.249019),
        (-31.970103, 116.249647),
    ]
    # Ensure smooth factor is at 0 so you can see the points
    folium.PolyLine(trail_coords, tooltip="trail", color="red", smoothfactor=0).add_to(m)


def create_markers(m):
    """
    Creates a group of markers
    """
    group_1 = folium.FeatureGroup(name="Group 1").add_to(m)

    folium.Marker(
        location=(-31.973088, 116.257886),
        tooltip="Marker 1",
        icon=folium.Icon("orange")
    ).add_to(group_1)

    folium.Marker(
        location=(-31.973489, 116.254536),
        tooltip="Marker 2",
        icon=folium.Icon("orange")
    ).add_to(group_1)

    group_2 = folium.FeatureGroup(name="Group 2").add_to(m)

    folium.Marker(
        location=[-31.971145, 116.256362],
        tooltip="Marker 3",
        icon=folium.Icon(color="red")
    ).add_to(group_2)

    folium.Marker(
        location=[-31.971851, 116.257929],
        tooltip="Marker 4",
        icon=folium.Icon(color="red")
    ).add_to(group_2)


def create_grid(m):
    """
    Creates a grid overlaying the map
    """
    grid = []
    # Change these values for different grid sizes
    lat_interval, lon_interval = 0.01, 0.01

    for lat in np.arange(-33, -30, lat_interval):
        grid.append([[lat, -180], [lat, 180]])

    for lon in np.arange(114, 118, lon_interval):
        grid.append([[-90, lon], [90, lon]])

    for g in grid:
        folium.PolyLine(g, color="black", weight=0.5, opacity=0.5).add_to(m)


m = initialise_map()
create_trail(m)
create_markers(m)
create_grid(m)

# Adds layer control to enable viewing groups of markers
folium.LayerControl().add_to(m)

# Saves the map to HTML file in this directory (open using browser)
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "footprint.html")
print("Done, saving map...")
m.save(file_path)
