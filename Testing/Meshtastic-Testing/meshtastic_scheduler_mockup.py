from time import sleep
from collections import deque
import random

"""
Simulates the following tasks:
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
        nodes = ['0', '1', '2', '3']
        print(f"retrieved nodes: {nodes}")
        return nodes

    # DUMMY FUNCTION - REPLACE WITH REAL ONE
    def request_telemetry(self, node_id):
        sleep(1)
        print(f"\ttelemetry data received for node {node_id}")
        return True

    # DUMMY FUNCTION - REPLACE WITH REAL ONE
    def request_position(self, node_id):
        sleep(1)
        print(f"\tposition data received for node {node_id}")
        return True

    # DUMMY FUNCTION - REPLACE WITH REAL ONE
    def check_health(self, node_id):
        sleep(1)
        print(f"\thealth check for node {node_id}")
        if random.random() < 0.5:  # 50% chance that health check passes
            print(f"\t\tnode {node_id} is healthy")
            return True
        print(f"\t\t[x] node {node_id} is still offline")
        return False

    def process_node(self, node_id):
        if random.random() < 0.2:  # 20% chance to simulate failure
            print(f"\t[x] both telemetry and position requests failed for node {node_id}")
            self.node_queue.append(('health_check', node_id))
        else:
            self.request_telemetry(node_id)
            self.request_position(node_id)
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
