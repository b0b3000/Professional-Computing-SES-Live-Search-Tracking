from time import sleep
from collections import deque
import meshtastic
import meshtastic.serial_interface
import subprocess
import sys
import json
from datetime import datetime, timezone, timedelta

"""
Performs the following tasks:
  - retrieving node list
  - requesting telemetry
  - requesting position
  - performing health check to determine status
Utilises a deque containing node IDs, and then runs a schedule which performs tasks.
"""
class Scheduler:
  def __init__(self):
    self.node_queue = deque()

  # DUMMY FUNCTION - REPLACE WITH REAL ONE
  def get_node_list(self):
    sleep(1)
    nodes = ['!33677de8', '!7c5b51e0']
    print(f"retrieved nodes: {nodes}")
    return nodes

  def request_telemetry(self, node_id):
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
      return telemetry_data, True
    
    except subprocess.CalledProcessError as e:
      print(f"An error occurred: {e}", file=sys.stderr)
      return None, False

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
          return json.dumps(geojson, indent=2), True
        else:
          print("could not extract GPS coordinates.", file=sys.stderr)
          return None, False
    
    except subprocess.CalledProcessError as e:
      print(f"error occurred: {e}", file=sys.stderr)
      return None, False


  def check_health(self, node_id):
    try:
      # construct command
      command = [
        'meshtastic',
        '--sendtext', "test",
        '--dest', node_id,
        '--ack'
      ]
        
      # run the command
      result = subprocess.run(command, check=True, text=True, capture_output=True)
      print(result.stdout)
      return True
    
    except subprocess.CalledProcessError as e:
      print(f"An error occurred: {e}", file=sys.stderr)
      return False

  def process_node(self, node_id):
    telemetry_data, telemetry_result = self.request_telemetry(node_id)
    position_data, position_result = True, True
    print(telemetry_data)

    if not (telemetry_result and position_result):
      print(f"\t[x] failed to make contact with node {node_id}")
      self.node_queue.append(('health_check', node_id))
    else:
      print(f"\tsuccessfully processed node {node_id}")
      self.node_queue.append(('process_node', node_id))


  def run_scheduler(self):
    for node_id in self.get_node_list():
      self.node_queue.append(('process_node', node_id))

    while True:
        if self.node_queue:
          task, node_id = self.node_queue.popleft()

          if task == 'process_node':
            print(f"processing node {node_id}...")
            self.process_node(node_id)
          elif task == 'health_check':
            print(f"checking health of node {node_id}...")
              
            if self.check_health(node_id):
              print(f"node {node_id} is back online, reprocessing...")
              self.node_queue.appendleft(('process_node', node_id))
            else:
              # still offline, add the health check to the end of the queue
              self.node_queue.append(('health_check', node_id))
          sleep(1)
        else:
          # if queue is empty, repopulate it and continue
          for node_id in self.get_node_list():
            self.node_queue.append(('process_node', node_id))

if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.run_scheduler()
