import meshtastic
import meshtastic.serial_interface
import subprocess
import sys
import json
from datetime import datetime, timezone, timedelta

def get_nodes():
    interface = meshtastic.serial_interface.SerialInterface()
    nodes = interface.nodes
    
    node_details = {}

    for node_id, node in nodes.items():
        name = node.get('user', {}).get('longName', 'Unnamed')
        node_details[node_id] = {
            'name': name,
        }
    interface.close()
    return node_details

# example usage:
#node_details = get_nodes()
#for node_id, details in node_details.items():
#    print(f"ID: {node_id}, Name: {details['name']}")

def request_telemetry(node_id):
    try:
        # construct command
        command = [
            'meshtastic',
            '--request-telemetry',
            '--dest', node_id
        ]
        
        # run command
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        output = result.stdout
        
        # parse telemetry data
        telemetry_data = {}
        
        lines = output.splitlines()
        telemetry_start = False
        
        for line in lines:
            if 'Telemetry received:' in line:
                telemetry_start = True
                continue
            
            if telemetry_start:
                key_value = line.split(':', 1)
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    value = key_value[1].strip()
                    telemetry_data[key] = value
        
        return telemetry_data
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return None

# example usage:
#print(request_telemetry('!33677de8'))   

def request_position(node_id):
    try:
        # construct command
        command = [
            'meshtastic',
            '--request-position',
            '--dest', node_id
        ]
        
        # run command
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        output = result.stdout
        
        # parse output and extract coords
        latitude = None
        longitude = None
        
        lines = output.splitlines()
        for line in lines:
            if 'Position received' in line:
                # line containing coordinates is like: Position received: (lat, lon) 45949000m full precision
                # extracting lat and lon from the line
                try:
                    lat_long = line.split('received: ')[1].split(')')[0].strip('(')
                    latitude, longitude = [float(coord) for coord in lat_long.split(',')]
                except ValueError:
                    print(f"Error parsing coordinates from line: {line}", file=sys.stderr)
        
        if latitude is not None and longitude is not None:
            # get current timestamp
            gmt_plus_8 = timezone(timedelta(hours=8))
            timestamp = datetime.now(gmt_plus_8).isoformat()

            # format as TimestampedGeoJSON
            geojson = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "properties": {
                    "timestamp": timestamp,
                    "altitude": None
                }
            }
            
            return json.dumps(geojson, indent=2)
        else:
            print("could not extract GPS coordinates.", file=sys.stderr)
            return None
    
    except subprocess.CalledProcessError as e:
        print(f"error occurred: {e}", file=sys.stderr)
        return None

# example usage:
geojson_output = request_position('!33677de8')
print(geojson_output)


"""
Wrapper for Meshtastic CLI `meshtastic --sendtext <message> --dest <dest_id> --ack`
Sends a message to a destination node, and awaits an ACK.
"""
def send_text_ack(message, dest_id):
    try:
        # construct command
        command = [
            'meshtastic',
            '--sendtext', message,
            '--dest', dest_id,
            '--ack'
        ]
        
        # run the command
        result = subprocess.run(command, check=True, text=True, capture_output=True)

        print(result.stdout)
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}", file=sys.stderr)

# example usage:
#send_text_ack('hello!', '!33677de8')
