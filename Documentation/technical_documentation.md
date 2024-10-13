# Project Technical Documentation

This document includes:
- Code Documentation: (Comments within code files), separate documentation explaining the purpose and functionality of some complex files, classes, functions, and critical logic. Including examples, dependencies, and any assumptions or limitations.

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
    <br><br>

- **Example Usage:** Technical staff connect a client device and Starlink to a Raspberry Pi, then run this file on the Raspberry Pi with the correct global variables. They give this and the connected tracker to a search team, the search team leaves this in their car and takes the tracker on the search. The tracker relays GPS coordinates to the client device which uploads this data to the cloud.

- **Key Classes and Functions:**
    - `run_base_station()` - Firstly establishes a connection with the cloud server, then with the tracker device. Runs a 60 second loop at the end of which it calls the next function.
    - `get_nodes()` - Called every 60 seconds, using LoRa from the client device it checks the location of the tracker device and uploads that, along with all previous locations, to the cloud server.
    - `get_nodes_verbose()` - Called only at the start of the first 60 second loop, performs relatively the same actions as `get_nodes()`, but with more verbose output in the terminal.

- **Assumptions:** The technical team will edit the global variables at the top of this file to correlate with the tracker/base pair's ID and long name.

<br>

---

# Web Application

The web application follows a standard Flask directory structure. For more information see [this link](https://flask.palletsprojects.com/en/2.3.x/tutorial/layout/).

---

<br>

- **File Name:** `routes.py`

- **Description:** Standard flask routes file that binds various app routes to HTTP functions and Python code. Has a variety of functions, handles most webapp backend.

- **Key Routes:**
    - `'/'` - Initialises the Folium map, finds and displays all container names.
    - `'/api/update-map'` - Uses `retrieve_from_containers.py` to update the Folium map.
    - `'/api/start-search'` - Allows user to manually begin a search, all data from this search is saved in the data path.
    - `'/api/end-search'` - Allows user to manually end a search, data stops being collected and is packaged into a GPX file.

<br>

---

<br>

- **File Name:** `get_key.py`

- **Description:** Retrieves the Azure storage key and database password from the Azure key vault.
Alternatively, retrieves the key and password from local key/password txt files, if app ran locally.

<br>

---

<br>

- **File Name:** `historical_database.py`

- **Description:** Facilitates upload and download of data to and from cloud database
    - `pyodbc` Provides drivers and connection functions for server hosted database<br><br>
- **Key Functions:**
    - `get_historical_searches()` - 
    - `upload_search_data()` - 
    - `connect_database()` - 

<br>

---

<br>

- **File Name:** `retrieve_from_containers.py`

- **Description:** The web application imports and uses this Python file to download all GPS data from the containers held in the Azure storage blob. The data is then translated onto a Folium map HTML file labelled stored within the `/application/static/` directory, which is embedded directly onto the main page of the web application.

- **Example Usage:** The web application runs this file every time the user reloads the page, it pulls all the current GPS data from searches onto the Folium map and returns it.

- **Key Classes and Functions:**
    - `retrieve_from_containers()` - Establishes connection with storage container, iterates through containers retrieving their data and calls `mapify()` on each, then uses the returning data to add the GPS trail onto the Folium map.
    - `mapify()` - Translates GPS data from container into TimestampedGEOJson format.
    <br><br>

- **Assumptions:** Data in the containers has been correctly uploaded by the base station and is error free.


---

# System Architecture Documentation

## Cloud System Design

The system is a complex one, with a combination of cloud-based software & resources, and hardware devices running headless code. The following diagram explains how all our resources interact

![Resource Organisation](/application/static/images/Resource_Organisation.drawio.png?raw=true "Resource Organisation")

## Local Web-App Deployment

This guide will walk you through the steps to set up and run the application on your local machine, rather than hosting it through an Azure web application as intended. This may be useful for development or testing purposes.

### Setup: Changes to make to code to enable it to run locally

1: Create a file 'keys.txt' in the root directory<br>
2: In this file, add a line containing the storage container connection key of the form 'key1: {key}'<br>
3: Add another line containing the database connection password of the form 'password: {password}'<br>
4: Comment out the two functions in 'get_key.py' which access key/password from the Azure key vault<br>
5: Uncomment the two functions in 'get_key.py' which access key/password locally. (More information can be found in get_key.py)<br>

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

- **Authentication**:   Organisation based authentication is a key feature of our web app. It is pre-configured to allow access to only CSU tenant Microsoft identities through leverage of Entra ID. To amend this, in the Web App open `Settings>Authentication`, and edit/remove the entry: <br>
Identity Provider: ` Microsoft(Cits3200-Meshtastic)`.<br>
To remove this requirement, near `Authentication Settings` select `Edit`, and set `App Service Authentication` to **Disabled**

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

Due to ease of development, subscription constraints and security reasons, some resources were configured outside the CSU tenant during development. As such, these resources will need to be re-created within the CSU tenant by an administrator for proper system functionality

### Historical Search Database

- **SQL Database Server**: Before a cloud-hosted database can be setup, a server should be set up to host it. 
    - **Setup**: 
        - Set `Authentication Method` to *Use SQL Authentication*.
        - Set up a **username** and **password** for database access
            - Set the **USERNAME** constant in `historical_database.py` to the set database connection username
            - Save the **password** in the appropriate secret in the key vault (see above)
        - In `Firewall Rules` set *Allow Azure services and resources to access this server* to **Yes**
    - **Security**
        - Open `Security>Networking`
        - Under `Public Network Access`, we opted to select **Selected Networks**, and below in `Firewall Rules` add a rule allowing all IPs from *0.0.0.0* to *255.255.255.255* access to the database, as group members were connecting to the database from a range of IP addresses. However, this can be configured to your preference.
        - Ensure under `Exceptions`, *Allow Azure services and resources access* is selected.
    - In the **Overview** screen, find the *Server Name* and set the **SERVER** constant in `historical_database.py` to match the server name. <br><br>
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



