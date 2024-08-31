# Context

### Changes made
- get_key.py as its own file, and acts as global variable in Flask app
- 

### In Progress Tasks / Future Tasks
- functions for processing seen blob data and only reading in new blob data from storage container need writing
- improve telemetry data dispaly
- when data is uploaded to storage container, search ID is updated along with it, this will allow us to track and display data from the particular LoRa device
- containers names are set and hardcoded for now, for testing purposes



# GPS Data Visualization Flask App

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

