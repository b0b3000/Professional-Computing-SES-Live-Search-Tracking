"""
Python program that runs on the RaspberryPi, connected to a base station.
See RaspberryPi setup documentation in this directory's README.md.
See requirements.txt
"""

import meshtastic.serial_interface

def get_node_information():
  interface = meshtastic.serial_interface.SerialInterface()
  nodes = interface.nodes
  interface.close()

  result = {}
  for value in nodes.values():
    user_id = value['user']['longName']
    telemetry = value.get('deviceMetrics', {})
    position = value.get('position', {})
    result[user_id] = {'telemetry': telemetry, 'position': position}
  print(result)

get_node_information()
