import meshtastic
import meshtastic.serial_interface
import subprocess
import sys

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
        
        # extract node names and IDs
        nodes = []
        for line in lines[start_idx:]:
            if line.startswith("╘═════╧"):  # end of table
                break
            parts = line.split("│")
            if len(parts) > 3:
                name = parts[2].strip()
                node_id = parts[3].strip()
                nodes.append((name, node_id))
        
        return nodes

    except subprocess.CalledProcessError as e:
        print(f"error occurred: {e}")
        return None

# example usage:
node_list = get_node_ids()
for name, node_id in node_list:
    print(f"Name: {name}, ID: {node_id}")


