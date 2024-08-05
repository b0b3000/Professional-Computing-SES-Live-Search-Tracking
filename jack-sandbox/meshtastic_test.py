import meshtastic
import meshtastic.serial_interface
import subprocess
import serial
import sys


def get_nodes():
    interface = meshtastic.serial_interface.SerialInterface()
    nodes = interface.nodes
    
# create dict to store the node details
    node_details = {}
    for node_id, node in nodes.items():
        user_name = node.get('user', {}).get('userName', 'Unnamed')
        long_name = node.get('user', {}).get('longName', 'Unnamed')
        node_details[node_id] = {
            'user_name': user_name,
            'long_name': long_name
        }
    interface.close()
    return node_details

# example usage:
#node_details = get_nodes()
#for node_id, details in node_details.items():
#    print(f"ID: {node_id}, User Name: {details['user_name']}, Long Name: {details['long_name']}")

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
