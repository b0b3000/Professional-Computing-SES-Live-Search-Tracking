import meshtastic
import meshtastic.serial_interface
import subprocess
import sys

def get_nodes(interface):
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
    
    return node_details

# example usage:
interface = meshtastic.serial_interface.SerialInterface()
node_details = get_nodes(interface)
for node_id, details in node_details.items():
    print(f"ID: {node_id}, User Name: {details['user_name']}, Long Name: {details['long_name']}")

"""
Wrapper for Meshtastic CLI `meshtastic --nodes`
Takes the table of known nodes, and uses string manipulation to format these nodes into a list
of tuples - (name, id)
"""
def get_node_ids():
    try:
        # run the `meshtastic --nodes` command
        result = subprocess.run(['meshtastic', '--nodes'], capture_output=True, text=True, check=True)
        output = result.stdout

        lines = output.splitlines()

        start_idx = None
        for idx, line in enumerate(lines):
            if line.startswith("╒═════╤"):
                start_idx = idx + 2  # the data starts two lines after the header
                break
        
        if start_idx is None:
            raise ValueError("Table header not found in the output.")
        
        # extract node names and IDs into a dict
        nodes = {}
        for line in lines[start_idx:]:
            if line.startswith("╘═════╧"):  # End of table
                break
            parts = line.split("│")
            if len(parts) > 3:
                name = parts[2].strip()
                node_id = parts[3].strip()
                nodes[name] = node_id
        
        return nodes

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return None

# example usage:
#node_dict = get_node_ids()
#print(node_dict)

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
