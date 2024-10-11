# Project Technical Documentation

This document includes:
- Code Documentation: (Comments within code files), separate documentation explaining the purpose and functionality of each file, class, function, and critical logic. Including examples, dependencies, and any assumptions or limitations.

- System Architecture Documentation: Diagrams and explanations of the system's architecture. Data flow and key components for high-level understanding.

- Microsoft Azure Peripherals Documentation: Guide on how to setup and integrate the various Microsoft Azure tools that are integral to the running of the project.

**Project Name:** SES Live Search.

**Description:** This project implements real-time GPS tracking for search teams operating in remote areas, using LoRa/Meshtastic devices as a communication medium for upload of GPS data to a cloud server, which is then visualised on a hosted web application for the search team coordinators to use.

**Key Components:** LoRa/Meshtastic tracker and client device, small computer (Raspberry Pi) base station, Microsoft Azure cloud server hosting a database and web application.

# Code Documentation

### Base Station

---

<br>

- **File Name:** `base.py`

- **Description:** The code that runs on the base station, found in this repository in the folder labelled `Base-Station`, is exclusively the file `base.py`. See the hardware documentation for specific steps on how to set up the base station and tracker pair.

- **External Dependencies:** 
    - Use `requirements.txt` in this directory to download requirements.
    - `meshtastic.serial_interface` (The meshtastic library is utterly essential to the operation of the devices).
    - `azure.storage.blob` (Enables data upload to the Microsoft Azure cloud server).
    - Depends on the connected LoRa/Meshtastic client device, communicating with the paired tracker device.
    - Requires internet connection via WiFi or Ethernet, to upload data.

- **Example Usage:** Technical staff connect a client device and Starlink to a Raspberry Pi, then run this file on the Raspberry Pi with the correct global variables. They give this and the connected tracker to a search team, the search team leaves this in their car and takes the tracker on the search. The tracker relays GPS coordinates to the client device which uploads this data to the cloud.

- **Key Classes and Functions:**
    - `run_base_station()` - Firstly establishes a connection with the cloud server, then with the tracker device. Runs a 60 second loop at the end of which it calls the next function.
    - `get_nodes()` - Called every 60 seconds, using LoRa from the client device it checks the location of the tracker device and uploads that, along with all previous locations, to the cloud server.
    - `get_nodes_verbose()` - Called only at the start of the first 60 second loop, performs relatively the same actions as `get_nodes()`, but with more verbose output in the terminal.

- **Assumptions:** The technical team will edit the global variables at the top of this file to correlate with the tracker/base pair's ID and long name.

<br>

---

### Web Application

The web application follows a standard Flask directory structure. For more information see [this link](https://flask.palletsprojects.com/en/2.3.x/tutorial/layout/).

---

<br>

- **File Name:** `requirements.txt`

- **Description:** Used when running the web application locally and when hosted, specifies the required packages for running the web application, along with their specific versions.

<br>

---

<br>

- **File Name:** `.deployment`

- **Description:** Used exclusively by the Azure cloud hosting service, specifies the configuration and application name.

<br>

---

<br>

- **File Name:** `__init__.py`

- **Description:** In initialising the Flask application, loads all routes from `routes.py`.

<br>

---

<br>

- **File Name:** `app.py`

- **Description:** Calls `app.run` function to start the web application.

<br>

---

<br>


- **File Name:** `routes.py`

- **Description:** Standard flask routes file that binds various app routes to HTTP functions and Python code. Further descriptions for each route found below.

- **External Dependencies:** 
    - Libraries: `flask`, `folium`, `azure.storage.blob`.
    - Python Files: `retrieve_from_containers.py`, `get_key.py`.

- **Example Usage:** 

- **Key Routes:**
    - `'/'` - Initialises the Folium map, finds and displays all container names.
    - `'/api/update-map'` - Uses `retrieve_from_containers.py` to update the Folium map.
    - `'/api/start-search'` - Allows user to manually begin a search, all data from this search is saved in the data path.
    - `'/api/end-search'` - Allows user to manually end a search, data stops being collected and is packaged into a GPX file.
    - `'/download/<session_id>.zip'` - Bound to a button on main page, allows user to download the GPX file.

<br>

---

<br>

- **File Name:** `get_key.py`

- **Description:** Retrieves the Azure storage key from the `keys.txt` file in this directory.

<br>

---

<br>

- **File Name:** `db_setup.py`

- **Description:** Specifies the schema/tables for the historical search database.

- **External Dependencies:** 
    - `sqlaclhemy` (Required for all database functions).

- **Example Usage:** 

- **Key Classes and Functions:**
    - `class SearchData()` - 
    - `get_database_url()` - 
    - `setup_database()` - 

- **Assumptions:**

<br>

---

<br>

- **File Name:** `retrieve_from_containers.py`

- **Description:** The web application imports and uses this Python file to download all GPS data from the containers held in the Azure storage blob. The data is then translated onto a Folium map HTML file labelled `footprint.html` that is stored within the `/application/static/` directory, which is embedded directly onto the main page of the web application.

- **External Dependencies:** 
    - `folium` (For creating the Folium map with the data).
    - `azure.storage.blob` (For downloading from Azure storage blob).

- **Example Usage:** The web application runs this file every time the user reloads the page, it pulls all the current GPS data from searches onto the Folium map and returns it.

- **Key Classes and Functions:**
    - `retrieve_from_containers()` - Establishes connection with storage container, iterates through containers retrieving their data and calls `mapify()` on each, then uses the returning data to add the GPS trail onto the Folium map.
    - `mapify()` - Translates GPS data from container into TimestampedGEOJson format.

- **Assumptions:** Data in the containers has been correctly uploaded by the base station and is error free.

<br>

---

<br>

- **File Name:** `index.js`

- **Description:** Handles various button clicks on the web application and calls the `'/api/'` routes accordingly.

- **External Dependencies:** 
    - Dependency

- **Example Usage:** 

- **Key Classes and Functions:**
    - `example_function()`

- **Assumptions:**

<br>

---

# System Architecture Documentation

System architecture documentation here.

# Microsoft Peripherals Documentation

This Flask web application is designed to visualize GPS data on a map. Data is pulled from Azure cloud server. This guide will walk you through the steps to set up and run the application on your local machine. 

### Step 1: (Optional) Create and Activate a Python Virtual Environment

It is recommended to use a Python virtual environment to manage project's dependencies. Follow these steps to create and activate a virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate       # On Windows
source venv/bin/activate    # On macOS/Linux
```

### Step 2: Run

Ensure you're in the Testing Files directory. Proceed to app, via the hyperlink to localhost:5000 in the terminal. You can run the Flask app using one of the following commands:

Option 1: Run the app with Flask's built-in server:

```bash
flask run
```
Option 2: Run the app directly using Python:

```bash
python run.py
```

