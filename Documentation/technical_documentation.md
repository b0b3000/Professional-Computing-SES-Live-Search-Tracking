# STT Technical Documentation

This document includes:
- **Code Documentation**: Explains the purpose and functionality of some of the more complex code files, classes, functions, and critical logic. Includes examples, dependencies, and any assumptions or limitations.

- **System Architecture Documentation**: Diagrams and explanations of the system's architecture. Data flow and key components for high-level understanding.

- **Microsoft Azure Peripherals Documentation**: Guide on how to setup and integrate the various Microsoft Azure tools that are integral to the running of the project.

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
    <br>

- **Example Usage:** Technical staff connect a client device and Starlink to a Raspberry Pi, then run this file on the Raspberry Pi with the correct global variables. They give this and the connected tracker to a search team, the search team leaves this in their car and takes the tracker on the search. The tracker relays GPS coordinates to the client device which uploads this data to the cloud.

- **Key Classes and Functions:**
    - `run_base_station()` - Firstly establishes a connection with the cloud server, then with the tracker device. Runs a 30 second loop at the end of which it calls the next function.
    - `get_nodes()` - Called every 30 seconds, using LoRa from the client device it checks the location of the tracker device and uploads that, along with all previous locations, to the cloud server.
    - `get_nodes_verbose()` - Called only at the start of the first 30 second loop, performs relatively the same actions as get_nodes(), but with more verbose output in the terminal.

- **Assumptions:** The technical team will edit the global variables at the top of this file to correlate with the tracker/base pair's ID and long name.

<br>

---

### Web Application

The web application follows a standard Flask directory structure. For more information see [this link](https://flask.palletsprojects.com/en/2.3.x/tutorial/layout/).

---

<br>

- **File Name:** `routes.py`

- **Description:** This Flask application serves as the backend for a web-based GPS tracking system, interacting with Azure Blob Storage and a historical database. The system supports real-time GPS tracking, historical search visualization, data filtering, and data export in GPX format. The primary user interface is an HTML page that displays an active map and a historical map, with data sourced from Azure Blob containers and the historical database.

- **External Dependencies:**

    - Flask (Used for routing and rendering templates).
    - folium (For rendering and saving maps in HTML format).
    - azure.storage.blob (Manages interaction with Azure Blob Storage containers).
    - get_key (Retrieves the Azure storage connection string securely).
    - historical_database (Handles historical search data storage and retrieval).
    - retrieve_from_containers (Used to fetch live GPS data from the Azure Blob containers).
    - to_gpx (Converts JSON GPS data to GPX format for export).
    - datetime (For timestamp management). <br>

- **Example Usage:** A search team runs the application on a web interface where they can view both live and historical GPS data, stored in Azure Blob containers and a database. The team can start a new search session, track live GPS data on the map, end the session, and download GPS data in GPX format for further analysis.

- **Key Classes and Functions:**

    - `index()` - Renders the home page of the web interface, displaying both the active and historical maps. Retrieves active Azure container names, historical search data, and base station data from the database.
    - `update_map()` - Called when the user requests new data. Fetches GPS data from the specified containers, updates the map, and stores the data in the database.
    - `start_search()` - Initializes a new search session by generating a unique session ID and storing session-related metadata in Flask’s session storage.
    - `end_search()` - Ends the current search session, converts GPS data to GPX format, and uploads the data to the database. Cleans up session data after the search concludes.
    - `render_map()` - Retrieves GPS data for a specific session and base station, renders it on a Folium map, and saves the map to an HTML file.
    - `download_gpx()` - Serves GPX files for download based on the user’s selection.
    - `submit_date()` - Filters historical search data by date range and base stations, returning the filtered data in JSON format.
    - `create_filtered_map()` - Creates a map that includes only the GPS pings that occurred after a user-specified filter time.
    - `filter_pings()` - Filters pings based on a timestamp and updates the map with only the relevant data points.
    - `get_presentable_historical_data()` - Retrieves and formats historical search data for display in the user interface. Also generates download links for GPX files.
    - `revert()` - Resets the map to its unfiltered state by reverting to the default "footprint" map.

- **Assumptions:**
    - Flask session management is used to track user sessions and store data between requests.

<br>

---

<br>

- **File Name:** `get_key.py`

- **Description:** Retrieves the Azure storage key and database password from the Azure key vault.
Alternatively, retrieves the key and password from local key/password .txt files, if the app is ran locally.

<br>

---

<br>

- **File Name:** `retrieve_from_containers.py`

- **Description:** This module contains functions for retrieving data from Azure storage containers. It handles the conversion of raw data into GeoJSON format, displays the data on a Folium map, and saves the updated map. The module also includes functionality to assign colors based on coordinates and center the map based on available GPS data.

- **External Dependencies:**
    - azure.storage.blob: Used to connect to and interact with Azure Blob Storage.
    - folium: A library for creating interactive maps.
    - json: For parsing and manipulating JSON data.
    - traceback: To handle and report exceptions.
    - config: Used to access configuration values such as default map coordinates.

- **Example Usage:** This module is primarily used for visualizing GPS data from base stations on a map. Technical staff can call `retrieve_from_containers()` with the required parameters to fetch data from Azure and update the Folium map. The updated map can then be saved for further analysis or visualization.

- **Key Functions:**

    - `assign_colour(initial_coord)`: Assigns a color in hex format based on the last three digits of the fractional part of the given coordinate.
    - `convert_to_geojson(data)`: Converts raw data taken from the Azure containers into GeoJSON format, extracting features, coordinates, and telemetry data.
    - `center_and_zoom(m)`: Centers the Folium map based on the average of available coordinates and adjusts the zoom level.
    - `process_data_to_map(data, map, telemetry_data=[])`: Draws GPS points and connecting lines on a Folium map for the provided dataset.
    - `historical_data_to_map(m, gps_points, map_save_path)`: Displays historical GPS data on a Folium map and saves the updated map.
    - `retrieve_from_containers(m, STORAGE_CONNECTION_STRING, active_containers, map_save_path)`: Fetches data from specified Azure storage containers and adds it to the live Folium map.

- **Assumptions:**
    - Each active container is expected to contain only one blob with the required GPS data.
    - The GPS data is structured in a format that includes latitude, longitude, name, time, and telemetry information.

<br>

---

<br>

- **File Name:** `historical_database.py`

- **Description:** This module is responsible for handling interactions between the web application and the Azure SQL database. It includes functions for establishing database connections, uploading search data, retrieving historical search information, and fetching real-time GPS data from the search records. The SQL database stores search session data, which can be queried for either live or historical operations.

- **External Dependencies:**
    - pyodbc (The essential library for connecting to and querying SQL databases via ODBC).
    - json (Used to serialize and deserialize GPS data in the database).
    - get_key (Used to retrieve sensitive database credentials such as the password).
    - datetime (Used for timestamp conversions when working with search data).

- **Example Usage:** Technical staff use these functions to handle communication between the Flask web app and the Azure SQL database. For example, after a search session is completed, the `upload_search_data()` function is called to store the collected GPS data. During a live search, the `get_live_searches()` function is used to fetch and display current GPS data from the database in real time.

- **Key Classes and Functions:**

    - `get_database_url()` - Retrieves the Azure SQL database connection string using hardcoded values like server, database, and username.
    - `connect_database()` - Establishes a connection to the database and returns a cursor object for executing SQL queries.
    - `upload_search_data()` - Uploads search data (GPS coordinates, session start/end times, etc.) to the database. It either inserts new rows or updates existing records.
    - `get_unique_base_stations()` - Returns a list of all unique base stations currently in the database.
    - `get_live_searches()` - Retrieves live GPS data for a particular session ID and a set of base stations.
    - `get_historical_searches()` - Fetches historical search data between a range of dates for the selected base stations.
    - `get_all_searches()` - Fetches all stored search data in the database.
    - `get_pings_after_time()` - Retrieves GPS pings that occurred after a specific time for a given search session and base station.

- Assumptions:
    - All search data, including GPS coordinates, is stored in JSON format in the database.

<br>

---

<br>

# System Architecture Documentation

## Cloud System Design

The system is a complex one, with a combination of cloud-based software and resources, and hardware devices running headless code. The following diagram explains how all our resources interact.

![Resource Organisation](/application/static/images/Resource_Organisation.drawio.png?raw=true "Resource Organisation")

## Local Web-App Deployment

This guide will walk you through the steps to set up and run the application on your local machine, rather than hosting it through an Azure web application as intended. This may be useful for development or testing purposes.

### Setup: Changes to make to code to enable it to run locally

1. Create a file `keys.txt` in the root directory.

2. In this file, add a line containing the storage container connection key of the form 'key1: {key}'

3. Add another line containing the database connection password of the form 'password: {password}'

4. Comment out the two functions in `get_key.py` which access key/password from the Azure key vault

5. Uncomment the two functions in `get_key.py` which access key/password locally.

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

<br>

# Azure Peripherals

## CSU Tenant Reesource Group: 'CITS3200_4'

These resources should not need to be altered upon delivering of the project to the Communications Support Unit. These are already deployed in a resource group within the tenant, and therefore can be managed/altered if desired by CSU administrators.

### Web Application: 'cits32004Mesh'

- **URL**: cits32004mesh-h5apbbfzdvb5acbf.australiaeast-01.azurewebsites.net
- **Setup**: 
    - Publish: Code
    - Runtime Stack: Python 3.9 (most compatible with our Flask dependencies) 
    - Operating System: Linux
    - Deployment: Set to the desired account, repository and branch if forking existing repository
    <br><br>

- **Authentication**:   Organisation based authentication is a key feature of our web app. It is pre-configured to allow access to only CSU tenant Microsoft identities through leverage of Entra ID. To amend this, in the Web App open `Settings>Authentication`, and edit/remove the entry:

    Identity Provider: `Microsoft(Cits3200-Meshtastic)`.

    To remove this requirement, near `Authentication Settings` select `Edit`, and set `App Service Authentication` to **Disabled**.

- **Deployment**: To modify the deployment source, open `Deployment Center`. Select `Settings`, and `Disconnect`. Following this, add your desired deployment source and build settings (Python 3.9 recommended). 
    - Ensure you set the identity settings in accordance with the managed identity.

### Managed Identity: 'CITS3200_4_UA'

- **Role Assignments**: This identity has the role assignment of 'Website Contributor', a role which allows the web application all required functionality. Modify this in `Azure role assignments` settings if required.

- **Associated Resources**: For now this is just the web application: cits32004Mesh. This is assigned in the Deployment Center of the Web Application.

### Key Vault: 'cits32004keys'

- **Vault URI**: https://cits32004keys.vault.azure.net/

- **Access Control**: The key vault uses **Access Policy** access control rather than the default **Role-Based** system. This can be configured in `Settings>Access Configuration>Permission Model`.

- **Policies**: The aforementioned web application and managed identity are added as Principals for access policies to the vault. These policies should most importantly grant access to view *secrets* and *passwords*. 

- **Secrets**: 
    - The storage connection key should be stored as a secret titled **BlobStorageConnectionString**
    - The database connection password should be stored as a secret titled **historicalDatabasePassword**

- If you decide to make a new Key Vault, set the **VAULT_NAME** constant in `get_key.py` to match its name.

## Resources Requiring Setup (IMPORTANT)

Due to ease of development, subscription constraints and security reasons, some resources were configured outside the CSU tenant during development. As such, these resources will need to be re-created within the CSU tenant by an administrator for proper system functionality.

### Historical Search Database

- **SQL Database Server**: Before a cloud-hosted database can be setup, a server should be set up to host it. 
    - **Setup**: 
        - Set `Authentication Method` to *Use SQL Authentication*.
        - Set up a **username** and **password** for database access.
            - Set the **USERNAME** constant in `historical_database.py` to the set database connection username.
            - Save the **password** in the appropriate secret in the key vault (see above).
        - In `Firewall Rules` set *Allow Azure services and resources to access this server* to **Yes**.
    - **Security**
        - Open `Security>Networking`.
        - Under `Public Network Access`, we opted to select **Selected Networks**, and below in `Firewall Rules` add a rule allowing all IPs from *0.0.0.0* to *255.255.255.255* access to the database, as group members were connecting to the database from a range of IP addresses. However, this can be configured to your preference.
        - Ensure under `Exceptions`, *Allow Azure services and resources access* is selected.
    - In the **Overview** screen, find the *Server Name* and set the **SERVER** constant in `historical_database.py` to match the server name.

<br>

- **SQL Database**
    - **Setup**: 
        - In your SQL Database Server, select `Create Database`.
        - Set the **DATABASE** constant in `historical_database.py` to the set database name
        - In `Networking`, set *Allow Azure services and resources to access this server* to **Yes**.
    -**Table Configuration**:
        - Select `Query Editor`, and login with the credentials created earlier under `SQL Server Authentication`
        - Create the search_history table using the following query:
        `CREATE TABLE search_history(
            session_id VARCHAR(100),
            base_station VARCHAR(100),
            start_time TIME,
            end_time TIME,
            gpx_data TEXT,
            search_date DATE,
            gps_JSON NVARCHAR(MAX)
        );`

### Blob Storage Container

- **Setup**:
    - When logged in to your Azure account, on the main page click `Create a resource`.
    - Select `Storage Account`.
    - Fill in your desired subscription, titles, and settings for the storage account.
    - Once it is created, on the storage account main screen, navigate to `Security + Networking`, then to `Access Keys`.
    - Here you can find key1 and key2, copy either of the hidden keys for them under the `Key` heading, save it in the appropriate secret in the key vault (see above).
    - Additionally, for each base station you run, you should copy this key into the `keys.txt` file in that base stations `Trackers` directory where the `base.py` code is being run.
    - This will enable the base station to upload, and the web app to download from the Blob Storage Container.
