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

  print(connected_nodes)
  for node in connected_nodes:
    request_telemetry(node, 1)


def print_node_information():
  interface = meshtastic.serial_interface.SerialInterface()
  data = interface.nodes
  interface.close()

  for key, value in data.items():
      print(f"Key: {key}")
      for sub_key, sub_value in value.items():
          if isinstance(sub_value, dict):
              print(f"  {sub_key}:")
              for sub_sub_key, sub_sub_value in sub_value.items():
                  print(f"    {sub_sub_key}: {sub_sub_value}")
          else:
              print(f"  {sub_key}: {sub_value}")

print_node_information()