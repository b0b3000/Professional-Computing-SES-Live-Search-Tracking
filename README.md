# SES Live Search


This project was allocated by Jim Catelli from the Communications Support Unit of the State Emergency Services of WA, to UWA students completing the unit CITS3200 Professional Computing.

This project has two main goals:
1. To create a physical system between two LoRa devices running the Meshtastic protocol, in which one device constantly transmits GPS locations (amongst other data) to the other device, which is connected via a headless computer to a cloud that can upload these GPS locations.
2. To provide a web-based interface for visualizing GPS data collected from these base stations. Users from the CSU should be able to view and filter searches, visualise historical GPS data on an interactive map, and download GPX files for further analysis.


## Installation


Because of the complex nature of this project, the entire setup process cannot be described here.

Instead, please refer to the `Documentation` folder located in this repository for instructions on how to setup the devices, the web application, and the Microsoft Azure peripheral infrastructure.

Contained in this folder is:
- *Hardware Documentation* - For setting up the physical devices.

- *Technical Documentation* - For setting up the software elements of the project, and understanding the codebase.

- *Selenium Testing Documentation* - For setting up the testing environment to test the codebase.

- *User Interface Documentation* - A guide on how to operate the web application as a user.

- *Project Management Documentation* - A history of the management of this project, for referencing.


## Code Structure

```
/project-root
├── application
│   ├── static
│   │   ├── css                     # Stylesheets
│   │   │   └── style.css           # Main page's style
│   │   ├── images                  # Images (logos, etc)
│   │   ├── js                      # JavaScript files
│   │   │   └── index.js            # Main page JavaScript
│   │   ├── footprint.html          # Live Folium map
│   │   ├── historical_map.html     # Historical Folium map
│   │   └── templates               # HTML templates
│   │       └── index.html          # Main web interface
│   ├── __init__.py                 # Initialises Flask app
│   └── routes.py                   # Routes and functions for Flask
├── Base-Station                    # Base station files
│   ├── base.log                    # Base station's log
│   ├── base.py                     # Base station running code
│   └── requirements.txt            # Requirements for base station
├── Documentation                   # All 5 documentation files
├── search_data                     # Save path for GPX
├── Testing                         # Various testing files
├── app.py                          # Main Flask application
├── config.py                       # Flask configuration variables
├── get_key.py                      # Retrieves Azure keys
├── historical_database.py          # Manages historical data
├── README.md
├── requirements.txt                # Flask dependencies.
├── retrieve_from_containers.py     # Retrieves GPS data from Azure blobs
└── to_gpx.py                       # Converts GeoJSON to GPX
```


## License

This project is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt the material for any purpose, even commercially, as long as you give appropriate credit to the original author(s).

![CC BY 4.0](https://i.creativecommons.org/l/by/4.0/88x31.png)
