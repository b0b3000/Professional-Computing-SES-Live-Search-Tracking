import meshtastic.serial_interface

def request_telemetry(node_id, channel):
  interface = meshtastic.serial_interface.SerialInterface()
  interface.sendTelemetry(node_id, True, channel)
  interface.close()


def get_base_station_id():
  interface = meshtastic.serial_interface.SerialInterface()
  base_station_info = interface.getMyNodeInfo()
  base_station_id = base_station_info['user']['id']
  interface.close()

  return base_station_id


def get_node_ids():
  interface = meshtastic.serial_interface.SerialInterface()
  nodes = interface.nodes
  ids = [node['user']['id'] for node in nodes.values()]
  interface.close()

  return ids


def get_available_nodes(base_station_id, node_ids):
  return


def telemetry_test():
  base_station_id = get_base_station_id()
  connected_nodes = [node_id for node_id in get_node_ids() if node_id != base_station_id]
  return connected_nodes


# interface.nodes seemingly retrieves all of the information we are looking for:
# telemetry and position data (where available) from a single request.
# likely simplifies this process a lot, and may result in a much simpler 'scheduler' 
def get_node_information():
  interface = meshtastic.serial_interface.SerialInterface()
  nodes = interface.nodes
  interface.close()

  result = {}
  for value in nodes.values():
    user_id = value['user']['id']
    telemetry = value.get('deviceMetrics', {})
    position = value.get('position', {})
    result[user_id] = {'telemetry': telemetry, 'position': position}
  print(result)



get_node_information()