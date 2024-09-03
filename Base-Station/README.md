# Documentation for Setting Up RaspberryPi with a LoRa Device

## Get Started

**Required Components**:
- *Power Supply*: For the 3A+ model you will need a 5V/2.5A power supply (standard USB should limit power to 5V, so any basic charger or power supply will do), connected to the 12.5W micro USB power cable
- *Boot Media*: If an OS is not installed, you will need to install it via a MicroSD card, find the OS on the RaspberryPi website. Alternatively you can use the imager found on the website
- *Peripherals*:
	- On a *USB Hub* connect a mouse and keyboard
	- Connect a monitor through the *HDMI port*
- *Networking*:
	- The 3A+ model does not have an Ethernet port, but comes with wireless connectivity and Bluetooth out of the box

**Initial Setup**
- Follow the instructions found here:
	https://www.raspberrypi.com/documentation/computers/getting-started.html
- (I used the setup method using the Imager software)

## RaspberryPi Setup for Project (for Unix)

- **Establish SSH Connection**
	- You can use a HDMI cable, mouse, and keyboard to operate on the RaspPi, but it is actually far easier to SSH into the device and operate on it using a terminal window
	- On the RaspPi run `ifconfig` and find the IP address of the device
	- Next run `whoami` to get the username
	- If necessary, go to the Settings and change the password so you know it
	- Now on your main PC run `ssh username@ipaddr` using the username and IP of the RaspPi
	- Enter the password for the RaspPi when prompted
	- You are now in the terminal of the RaspPi

- **Setup Virtual Environment**
	- We will need to create a virtual environment so we can install certain python packages that are not packaged for the Debian OS (virtualenv is useful anyway)
	- Run `mkdir Trackers` to create a new directory
	- Run `python3 -m venv /home/[username]/Trackers/venv` to create a virtual environment
	- Run `source /venv/bin/activate` to activate the virtual environment
	- Get the requirements file from Github, move it into the Trackers directory and run `pip install -r requirements.txt` to install required packages

- **Create Files** 
	- Run `vi upload_server.py` to create a new Python file
	- Vim may not be setup correctly initially, so in the Vim editor run `:set nocompatible`
	- If backspace is not working then in the Vim editor run `:set backspace=indent,eol,start`
	- I followed this guide for Vim: https://www.freecodecamp.org/news/vimrc-configuration-guide-customize-your-vim-editor/
	- Copy the code from Github into the Python file on the RaspPi

- **LoRa Device Connection**
	- Plug the LoRa device into the RaspberryPi via the USB-A port (this will be the base station)
	- Plug another LoRa device into a power supply and ensure it has a GPS lock (this will be the tracker)
	- If necessary, follow the LoRa device setup documentation written by Jack

- **Run Code**
	- Run the Python code using `python3 upload_server.py`
