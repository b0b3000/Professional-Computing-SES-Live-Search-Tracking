# pip install azure-storage-blob, folium
"""
Python program for retrieving data from Azure blob storage.

Naming convention for Containers: "base-station-[id]", and for Blobs: "search_[id]".
Data storage format: TimestampedGeoJSON

Written by Bob Beashel, Fred Leman
"""
import os
import folium
from folium.plugins import TimestampedGeoJson
from azure.storage.blob import BlobServiceClient
import map_processing
import traceback

def retrieve_from_containers(m, geojson_data, STORAGE_CONNECTION_STRING):
    
    # Initialize the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

    # To store device-specific data
    device_data = []

    # Iterate through each container in the Storage Account
    print("\n----- Containers -----\n")
    for container in blob_service_client.list_containers():
        print(container.name)
        container_client = blob_service_client.get_container_client(container)

        # Iterate through each blob in the container
        for blob in container_client.list_blobs():
            try:
                blob_content = container_client.download_blob(blob).readall()
                
                # Append parsed data to device_data
                lines = eval(blob_content)
                for line in lines:
                    device_data.append({
                        'data': line.get('data', 'No additional data')
                    })  
                
                print(f"\n\tContent of the blob '{blob.name}': \n\t\t{str(blob_content)}")
                
                # Add the GeoJSON data to the map
                mapify(blob_content).add_to(m)
            
            except Exception as e:
                print(f"Error downloading blob: {e}")
                traceback.print_exc()

    print("\n")
    
    # Save the map to an HTML file
    map_save_path = os.path.join(os.path.dirname(__file__), 'app/static/footprint.html')
    m.save(map_save_path)
    
    return device_data

def mapify(geojson_data):
    
    # Parse the GeoJSON data
    lines = eval(geojson_data)
    
    # Create features from the GeoJSON data
    features = [    
        {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": line["coordinates"],
            },
            "properties": {
                "times": line["dates"],
                "tooltip": line["data"] + str(line["dates"]),
                "style": {
                    "color": line["color"],
                    "weight": 5,
                },
            },
        }
        for line in lines
    ]
    
    # Create a TimestampedGeoJson object to add to the map
    trail = TimestampedGeoJson(
        {
            "type": "FeatureCollection",
            "features": features,
        },
        transition_time=100,
        period="PT1M",
        loop=False,
        add_last_point=True,
    )
    
    return trail

# if __name__ == "__main__":
#     # Set up the map and path for saving the HTML file
#     current_dir = os.path.dirname(__file__)
#     map_save_path = os.path.join(current_dir, 'footprint.html')
#     m = folium.Map(location=(-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)
    
#     # Retrieve GeoJSON data and add it to the map
#     geojson_data = "Your GeoJSON data string here"
#     retrieve_from_containers(m, geojson_data, "Your_Storage_Connection_String")
    
#     # Save the final map
#     m.save(map_save_path)
