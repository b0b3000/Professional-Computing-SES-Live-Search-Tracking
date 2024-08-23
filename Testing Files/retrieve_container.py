# pip install azure-storage-blob, folium
"""
Python program for retrieving data from Azure blob storage.

Naming convention for Containers: "base-station-[id]", and for Blobs: "search_[id]".
Data storage format: TimestampedGeoJSON

Written by Bob Beashel, Fred Leman
"""
import json
import os
import folium
from folium.plugins import TimestampedGeoJson
from azure.storage.blob import BlobServiceClient


def retrieve_from_containers():
    combined_data = []
    
    # Sets connection string, where AccountName is the name of the Storage Account, and AccountKey is a valid Access Key to that account.
    STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=cits3200testv1;AccountKey=oVbt8D3gIlcm2zu/ihMeHHIiuJdKXVMtwKJWYdLzmsMFNklyatcEsFoECqe1dcgUqz2NuCyIJDXd+ASt0iGB3A==;EndpointSuffix=core.windows.net"
    # Initialises client.
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)   # The BlobServiceClient interacts with the Storage Account itself.

    # Iterates through each container in the Storage Account, and prints their names.
    for container in blob_service_client.list_containers():
        container_client = blob_service_client.get_container_client(container)   # The ContainerClient interacts with a specific container (directory).

        # Iterates through each blob in the container and prints its data.
        for blob in container_client.list_blobs():
            try:
                blob_content = container_client.download_blob(blob).readall()
                decoded_content = blob_content.decode('utf-8')
                # Replace single quotes with double quotes for valid JSON format
                json_content = decoded_content.replace("'", '"')
                
                # Convert to JSON
                if json_content.strip():
                    try:
                        json_data = json.loads(json_content)
                        combined_data.extend(json_data)
                        
                    except json.JSONDecodeError:
                        print(f"Error parsing JSON for blob '{blob.name}'")
                else:
                    print(f"Blob '{blob.name}' is empty")
                
            except Exception as e:
                print(f"Error downloading blob: {e}")
    
    """
    if combined_data:
        mapify(combined_data).add_to(m)
        m.save(path)
    else:
        print("No data to map")"""

    return combined_data

def update_map_with_data(m, path):
    combined_data = retrieve_from_containers()
    if combined_data:
        mapify(combined_data).add_to(m)
        m.save(path)
    else:
        print("No data to map")
    

def mapify(data):
    
    # Draws out the trail lines as a Folium object.
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
        for line in data
    ]
    
    # Creates the TimestampedGeoJson object to add to the Folium map.
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

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    path = os.path.join(current_dir, 'static', 'test_footprint.html')  # Save map to the static folder
    m = folium.Map((-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)
    
    #m.save(path)
    update_map_with_data(m, path)
