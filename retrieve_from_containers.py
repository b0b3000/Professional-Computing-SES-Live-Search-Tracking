"""This module contains functions for retrieveing data from the Azure storage containers."""

import traceback
import json
import folium
from azure.storage.blob import BlobServiceClient

all_coordinates = []    # Global list to store all coordinates.

default_coord_avg = -31.9775, 115.8163    # Changes the default map centring location.


def assign_colour(initial_coord):
    """Assigns a colour in hex format based on the last three digits of the fractional part
    of the given coordinate.

    Arg: initial_coord(str): The latitude value of a base station's first ping.
    Returns: string (str): The associated hex colour.
    """
    # Gets the last three digits of the coordinate.
    last_three_digits = [int(digit) for digit in str(initial_coord).split(".")[1][-3:]]
    min_value = 0
    max_value = 9

    # Normalises each value to the range 0-255.
    normalised_values = [
        int((value - min_value) / (max_value - min_value) * 255)
        for value in last_three_digits
    ]
    
    # Converts to hexadecimal format and return as hex colour code.
    hex_colour = '#{:02x}{:02x}{:02x}'.format(*normalised_values)
    
    return hex_colour


def convert_to_geojson(data):
    """Converts raw data taken from the Azure containers into GeoJSON data.
    
    Args:
        data (dict): A base station's full data.

    Returns:
        features (list): A list of GeoJSON features to add to the map.
        coordinates (list): A list of coordinate tuples for drawing a PolyLine.
        telemetry_list (list): A list of telemetry data points to be sent to the frontend.
    """
    # Decodes the data from UTF-8 to JSON if necessary.
    if isinstance(data, bytes):
        try:
            decoded_data = data.decode('utf-8').replace("'", '"')
            points = json.loads(decoded_data)
            
        except Exception as e:
            print(f"Error decoding JSON data: {e}")
            return None, [], []
    else:
        points = data

    features = []
    coordinates = []
    telemetry_list = []

    for point in points:
        for _, point_data in point.items():
            lat = point_data.get('lat', 0.0)
            lon = point_data.get('long', 0.0)
            name = point_data.get('name', 'Unnamed Point')
            time = point_data.get('time', '00:00:00T00:00:00')
            telemetry = point_data.get('telemetry', {})
            longname = point_data.get('longname')
            coordinates.append([lat, lon])

            # From each point, creates a GeoJSON `feature` (these will display points as icons on the Folium map).
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat],
                },
                "properties": {
                    "time": time,
                    "name": name,
                    "tooltip": f"Name: {longname}\nID: {name}\nTime: {time}\nCoords: {[lon, lat]}\nBattery: {telemetry.get('battery', 'N/A')}%",
                    "telemetry": telemetry,
                },
            })
            telemetry_list.append({
                "name": name,
                "time": time,
                "telemetry": telemetry,
                "lon": lon,
                "lat": lat,
                "longname": longname
            })

    return features, coordinates, telemetry_list 


def process_data_to_map(data, map, telemetry_data=[] ):
    """For a given dataset, draws its GPS points and connecting lines on a Folium map.

    Args:
        data (dict): A base stations GPS data.
        map (_type_): The folium map that is being used.
        telemetry_data (list, optional): _description_. The telemetry data of the base station.
    """
    features, coordinates, extracted_telemetry = convert_to_geojson(data)
    initial_coord = 0

    # Draws points on the Folium map.
    for feature in features:
        point_location = feature["geometry"]["coordinates"][::-1]  # Reverses [long, lat] to [lat, long].
        folium.Marker(
            location=point_location,
            popup=feature["properties"]["tooltip"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(map)

    initial_coord = features[0]["geometry"]["coordinates"][0]
    trail_colour = assign_colour(initial_coord)     # Assigns the custom hex colour.

    # Draws lines that connect coordinates on the Folium map.
    if coordinates:
        folium.PolyLine(
            locations=coordinates,
            color=trail_colour,
            weight=5,
            opacity=0.7  
        ).add_to(map)
        all_coordinates.extend(coordinates)

    telemetry_data.extend(extracted_telemetry)
    

def historical_data_to_map(m, gps_points, map_save_path):
    """Displays historical data on the historical Folium map, then saves the map.

    Args:
        m (folium.Map): The historical Folium map.
        gps_points: Historical GPS data.
        map_save_path (str): Path to save the updated historical map.
    """
    process_data_to_map(gps_points, m, telemetry_data=[])
    m.save(map_save_path)
    
    
def retrieve_from_containers(m, STORAGE_CONNECTION_STRING, active_containers, map_save_path):
    """Fetches Azure storage container data and adds it to the live map.

    Args:
        m (folium.Map): The folium map object to add the GeoJSON data to.
        STORAGE_CONNECTION_STRING (str): The connection string for the Azure storage account.
        active_containers (list): A list of strings, of the names of the storage containers.

    Returns:
        telemetry_data (list): A list of all selected blob's telemetry data, in dictionaries.
        all_blob_content (list): A list of all selected blob's data, in dictionaries.
    """
    global all_coordinates
    all_coordinates.clear()    # Clears 'all_coordinates' to ensure fresh updates.

    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

    # For each container in the storage account, fetch its blobs data.
    telemetry_data = []
    all_blob_content = {}
    for container_name in active_containers:
        try:
            container_client = blob_service_client.get_container_client(container_name)
            if not container_client.exists():
                print(f"Container '{container_name}' does not exist. Skipping...")
                continue

            blobs_list = list(container_client.list_blobs())
            if len(blobs_list) != 1:
                print(f"Unexpected blob count in '{container_name}'. Expected 1, found {len(blobs_list)}.")
                continue
            
            blob = blobs_list[0]
            blob_content = container_client.download_blob(blob).readall()
            all_blob_content[blob.name] = blob_content
            process_data_to_map(blob_content, m, telemetry_data)

        except Exception as e:
            print(f"Error processing container '{container_name}': {e}")
            traceback.print_exc()
    
    # Calculates average lat and lon in order to centre the map.
    if len(all_coordinates) != 0:
        avg_lat = sum(lat for lat, _ in all_coordinates) / len(all_coordinates)
        avg_long = sum(long for _, long in all_coordinates) / len(all_coordinates)
    else:
        avg_lat, avg_long = default_coord_avg    # (See global variable)
    m.location = [avg_lat, avg_long]
    m.fit_bounds([(lat, long) for lat, long in all_coordinates])    # Adjusts the map zoom to fit all coordinates.

    m.save(map_save_path)
    return telemetry_data, all_blob_content


# Testing purposes (Uncomment if needed to test)
# if __name__ == "__main__":
#     active_containers = ['base-3200-b']  # Replace with the containers you want to test
#     STORAGE_CONNECTION_STRING = get_key.get_key()
#     # Create a new map object to test the updates
#     m = folium.Map(location=(-31.9505, 115.8605), control_scale=True, zoom_start=17)
#     # Call the function with test parameters
#     try:
#         retrieve_from_containers(m, STORAGE_CONNECTION_STRING, active_containers)
#         print()
#         print("Test completed successfully. The map should be updated with data from the active containers.")
#     except Exception as e:
#         print("An error occurred during testing:", e)
    