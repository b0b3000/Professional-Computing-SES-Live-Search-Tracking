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


def retrieve_from_containers(m, path, STORAGE_CONNECTION_STRING):
    
    # Initialises client.
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)   # The BlobServiceClient interacts with the Storage Account itself.

    # To store device-specific data
    device_data = []

    # Iterates through each container in the Storage Account, and prints their names.
    print("\n----- Containers -----\n")
    for container in blob_service_client.list_containers():
        print(container.name)
        container_client = blob_service_client.get_container_client(container)   # The ContainerClient interacts with a specific container (directory).

        # Iterates through each blob in the container and prints its data.
        for blob in container_client.list_blobs():
            try:
                blob_content = container_client.download_blob(blob).readall()
                
                # 
                # --------------------------------------------------------------------------
                # Append parsed data to device_data
                lines = eval(blob_content)
                for line in lines:
                    device_data.append({
                        'data': line.get('data', 'No additional data')
                    })  
                # --------------------------------------------------------------------------  
                
                print(f"\n\tContent of the blob '{blob.name}': \n\t\t{str(blob_content)}")    # Prints the content of the blob.
                mapify(blob_content).add_to(m)    # Creates a TimestampedGeoJson object from the blob's lines.
                m.save(path)    # Save map after each edit.
            
            except Exception as e:
                print(f"Error downloading blob: {e}")

    print("\n")
    
    # Saves current map to Azure storage container
    map_processing.save_map_to_storage(path, "map-storage", "latest_map", STORAGE_CONNECTION_STRING)
    
    # This returns tel data
    return device_data

def mapify(blob_content):
    
    # Evaluates the timestamped trail lines from the blob's content file into a list.
    lines = eval(blob_content)
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
        for line in lines
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

"""
if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    path = os.path.join(current_dir, 'footprint.html')      # Finds correct location to store Folium map.
    m = folium.Map((-31.865184419408514, 116.07863524846368), control_scale=True, zoom_start=17)    # Creates a new Folium map at an arbitrary location.
    m.save(path)
    retrieve_from_containers(m, path)
"""