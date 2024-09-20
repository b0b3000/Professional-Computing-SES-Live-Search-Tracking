# STT Hardware Documentation

The purpose of this document is to provide a concise and readable guide on how to configure the hardware required for the Search Team Trackers project. Included in this document is the following:
- LoRa/Meshtastic Device Configuration

- Base Station Configuration

- Tracker Device User Guide

<br><br>

# LoRa/Meshtastic Device Configuration

### Introduction

Official documentation for the Meshtastic project can be found [here](https://meshtastic.org/docs/introduction/).

The intention of this document is not to replace any official documentation, but rather to provide a guideline for getting Meshtastic devices configured specifically for use in this project.

## Software Installation

### Meshtastic Mobile App

Meshtastic's mobile app contains all the features necessary to configure the LoRa devices for the purposes of this project.

The app is available on both iOS and Android devices.

### Python CLI

Meshtastic's Python Command Line Interface (CLI) can be used to configure devices, and it is also a requirement for the code which processes the tracking data.

A basic installation guide for the CLI is as follows:

- Ensure Python 3 is installed on the system.

- Utilise `pip` to install the package:

	`pip install meshtastic`

- Verify the installation:

	`meshtastic --version`

See the [official documentation](https://meshtastic.org/docs/software/python/cli/installation/?install-python-cli=windows) for more information.

## Basic Device Configuration:

Configuration assumes that the Meshtastic device has followed the "[Getting Started](https://meshtastic.org/docs/getting-started/)" section of the official documentation, which outlines the installation of serial drivers onto a computer, as well as the flashing of firmware onto the Meshtastic device.

#### Python CLI

- For ease of use, we recommend using the Meshtastic App for configuration.

#### Meshtastic App

- Open the Meshtastic app and connect a LoRa device (either via USB or Bluetooth).

- If using USB, select the option which begins with `/dev/bus/usb/...`.

- If using Bluetooth, select the '+' button, then select the target device, and enter the Bluetooth code which appears on the screen of the LoRa device.

- Once connected, set the region to `ANZ`, and name the device appropriately. The device will reboot itself after each change.

- The device is now connected to the mobile device. The other tabs of the app will now be populated with relevant information.

### Channel Configuration:

In order for Meshtastic devices to be able to communicate with each other, they need to be configured to share a mutual channel. A Meshtastic device can be connected to multiple channels, with some channels being reserved for specific purposes.

A channel primarily consists of a `Channel Name`, and a Pre-Shared Key (`PSK`). By default, Meshtastic devices are connected to a public channel named "LongFast", which utilises the PSK '`AQ==`'.

The scope of this project does not require any communication with devices that we do not control, and so we opt to remove this public "LongFast" channel from each device.

In configuring these devices, our aim is to create two channels:

- An admin channel utilising the reserved named `admin`, which allows for remote access control over nodes within the mesh.

- A primary channel which is used to capture position and telemetry broadcasts.

#### Meshtastic App

- With a Meshtastic device connected, navigate to `Radio configuration` using `⋮` in the top right.

- Select the `Channels` section.

- From here, we can assign a `Channel Name` and `PSK`.

- The `⟳` symbol can be used to generate a new `PSK`. This key needs to be consistent across any devices which are intended to communicate with each other.

-  `Uplink enabled` and `Downlink enabled` can remain set to their default value of `disabled`.

- Once configured, we can select `save`, and then select `send`.

This process will need to be repeated for each device.

  ### Device Position Configuration:

Devices on a shared network will periodically broadcast their position and telemetry information to other nodes. 

In order to generate more granular tracking data, it is recommended that the `GPS update interval` and `position broadcast interval` are changed from their default setting. 

#### Meshtastic App

- With a Meshtastic device connected, navigate to `Radio configuration` using `⋮` in the top right.

- Select `position`

- From this menu, change the values of `GPS update interval` and `position broadcast interval`

- From testing, setting each to a value of `30` seconds provides very detailed tracking information across small areas, however this can be configured to best suit the requirements of the search area.

- Setting these values too low may negatively impact channel utilisation, which can be monitored in the device's telemetry data.

## Factory Resetting a Meshtastic Device:

#### Meshtastic App

- With a Meshtastic device connected, navigate to `Radio configuration` using `⋮` in the top right.

- At the bottom of the options, select `Factory reset`, and confirm this choice with `send`.

- The connected Meshtastic device will then reboot - completing this process.

<br><br>

# Base Station Configuration

### Introduction

The specifications of the base station computer include WiFi connectivity, a USB-A serial port, capacity to run headless Python3 code.

Given these specifications, we opted to use a Raspberry Pi 3A+ for the role of base station. Official documentation for the Raspberry Pi can be found [here](https://www.raspberrypi.com/documentation/). The intention of this document is not to replace any official documentation, but rather to provide a guideline for connecting a Raspberry Pi and tracker device together for the purposes of the project.

## Hardware Setup

Connect the following to your base station:

- *Power Supply*: For the 3A+ model you will need a 5V/2.5A power supply connected to the 12.5W micro USB power cable.

- *Boot Media*: If an OS is not installed, you will need to install it via a MicroSD card, find the OS on the RaspberryPi website. Alternatively you can use the imager found on the website

- *Peripherals*:
	- Connect a preconfigured client tracker device (see above section)
	- *Optionally* connect a mouse, keyboard, and monitor if not using SSH.

- *Networking*:
	- The 3A+ model does not have an Ethernet port, but comes with wireless connectivity and Bluetooth out of the box.

- For basic setup, follow the official instructions found [here](https://www.raspberrypi.com/documentation/computers/getting-started.html).

## Software Setup

- **Establish SSH Connection**
	- On the RaspPi run `ifconfig` and find the IP address of the device, and `whoami` to get the username.

	- If necessary, go to the Settings and change the password so you know it.

	- On your external PC run `ssh username@ipaddr` using the username and IP of the RaspPi, entering the password for the Raspberry Pi when prompted.


- **Setup Virtual Environment**
	- Create a virtual environment so we can install certain python packages that are not packaged for the Debian OS:

	```
	> mkdir Trackers
	> python3 -m venv /home/[username]/Trackers/venv
	> source /venv/bin/activate
	```

	- Get the requirements.txt file from Github, move it into the `Trackers` and run `pip install -r requirements.txt` to install required packages.

	- Get the `base_py` file from Github, move it into the `Trackers` directory.

## Base/Tracker Pair Configuration

- **LoRa/Meshtastic Device Physical Connection**
	- Connect a preconfigured LoRa/Meshtastic device (setup in `CLIENT` mode) to RaspberryPi via the USB-A port, this will act as the **base station**. Ensure that this device boots up and stays on with no power issues.

	- Connect a second preconfigured LoRa device (setup in `TRACKER` mode and equipped with a GPS module) into an adequate power supply (5V), this will be the **tracker**. Ensure that this device boots up and stays on with no power issues, and that it has established a GPS lock. 
	
	- You may have to take the tracker outdoors to establish the GPS lock, after which, you can take it back inside to continue the setup.


- **Run Code**

	- Run the Python code using `python3 base.py`

	- Note the global variables in the Python file `TRACKER_ID`, `TRACKER_LONG_NAME`, `BASE_ID`, `BASE_LONG_NAME`.

	- When the code runs for the first time you will be able to find these details in the nodes summary printout, enter them into the code and run it again.

	- This documentation is continued in `technical_documentation.md`
