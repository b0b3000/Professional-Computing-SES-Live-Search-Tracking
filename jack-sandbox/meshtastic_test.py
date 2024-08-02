import meshtastic
import meshtastic.serial_interface
import logging

# Enable debugging logs
logging.basicConfig(level=logging.DEBUG)

# Connect to the Meshtastic device
interface = meshtastic.serial_interface.SerialInterface()

def on_receive(packet):
    # Process received data
    if 'telemetry' in packet['decoded']['payload']:
        telemetry = packet['decoded']['payload']['telemetry']
        print(f"Received telemetry: {telemetry}")
    else:
        print("Received a packet, but no telemetry payload found.")

# Set the callback for received messages
interface.onReceive = on_receive

try:
    # Request telemetry data
    interface.sendText("Requesting telemetry data")
except Exception as e:
    print(f"An error occurred: {e}")
