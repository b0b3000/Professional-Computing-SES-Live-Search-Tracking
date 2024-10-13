# STT User Interface Documentation

This document is a user manual, with step-by-step guides on how to use the interface including: log in steps, navigation through tabs, retrieving and viewing data.

# Introduction
The web application has been designed for volunteer State Emergency Service (SES) search teams to monitor and visualize live GPS locations of search teams, and to maintain a detailed digital record of completed searches. Naming conventions have been applied with this context in mind.

This user guide provides step-by-step instructions on logging in and using the key features of the application.

## User Manual

### 1. Logging In
- **Step 1**: Click on the provided link to access the login page.
- **Step 2**: Enter your username and password in the respective fields.
- **Step 3**: Click the "Login" button to proceed.
- **Step 4**: Upon successful login, you will be directed to the front page.

### 2. Navigating the Interface

**Overview of the Main Interface**:  
Upon logging in, users are taken to the main page, where they can navigate using the tabs at the top: the "Active Search" tab and the "Historical Data" tab. Each tab opens a separate page with distinct functionality.

### 3. Active Search Tab

#### Overview:
When a user is ready to start recording a search, they can navigate to this tab and enter the required details to begin receiving data for map visualization. The search can also be ended on this page, and users can download a separate GPX file containing data for each involved base station.

#### Map:
Before a search begins, the map is zoomed out to display Western Australia and does not show any GPS points. Once the search starts and GPS signals are transmitted, the map will automatically zoom in and center on the location of the transmitted GPS signals, enabling dynamic location tracking.

These changes are applied when the “Fetch Data” button is pressed.  
A user can also control the display of the map by scrolling and dragging on the map interface.  
For every GPS ping that is transmitted, a location icon is presented on the map with a colored trail line in between each point. A user may hover over any location point to view its telemetry data at any time.  
When a search is active, the border around the map glows green; when there is no search, the border glows red.

#### Left and Right Side Panels:

- **Left Panel: “Select Base Station”**:  
  This panel lists each base station configured to receive GPS transmissions. To start a search, users must select the base stations involved, which can be one or multiple. A selected tab will glow orange.

- **Right Panel: “Most Recent Pings”**:  
  This panel displays the telemetry data for each GPS ping transmitted to the server, including time, date, coordinates, battery level, and altitude. Instructions at the top of the panel explain the behavior when a base station has not received a ping for over 5 minutes, which results in the box being outlined in red.

#### Buttons Below the Map:
- **“Start Search”**: Once a user has selected the involved base stations, they must click this button to begin the search.
- **“Fetch Data”**: During an active search, pressing this button refreshes the map with newly received GPS pings.
- **“End Search”**: Pressing this button stops the recording of GPS pings. Before using it, ensure the "Fetch Data" button has been pressed to collect the latest GPS data points. After pressing "End Search," a download link will appear in the GPX Download section.
- **“Filter Pings”**: This button filters GPS points on the map from a specific time. It allows users to display only GPS points from the exact time of the search. To revert the display to all transmitted GPS points, press the “Revert Pings” button.
- **Help Button**: Displayed as a rounded orange question mark, this button provides a brief explanation of each feature on the page and offers a tutorial on how to start a search and use the various buttons.

#### Download GPX Files:
Located under the map, once a search has ended, a GPX file download link can be found for each base station involved in the search.

### 4. Historical Data Tab

#### Overview:
This page provides quick access to the data from completed searches. Users can look up the date and base station of the search they are interested in, display the data on the map, and download the corresponding GPX file for that search and base station.

#### Features:
- **Filter Previous Searches**:  
  Users can filter completed searches by entering a date range and selecting one or multiple base stations.

- **Database Table**:  
  When the tab is opened, it displays a record of all previous searches, with each row representing a single base station. The table includes details such as search ID, date, time, base station, a GPX download link, and a display button to show the data points from that search on the map. Once the table is filtered, only filtered results will be displayed.

- **Historical Map**:  
  Provides instant visualization of the selected historical search.

- **Help Button**: Displayed as a rounded orange question mark, this button provides a brief explanation of the features on the page.

### 5. Step-by-Step User Journey

Follow this step-by-step guide to use the application's features:

1. Log in using your credentials.
2. Navigate to the **Active Search** tab.
3. Select the base stations involved in the search.
4. Click **Start Search** to begin.
5. During the search, press the **Fetch Data** button regularly to retrieve recent GPS locations.
6. (Optional) To filter GPS pings from a specific time, press the **Filter Pings** button. To revert and display all data points again, press **Revert Pings**.
7. When ready to end the search, press **End Search**.
8. Use the download links under **Download GPX Files** to download the GPX data for the selected base stations.

#### Navigating Historical Searches:
1. Refresh the page.
2. Scroll through the table to find the desired base station data, or use the filter feature to narrow down the results.
3. Click the **Display Data** button to show the data points on the Historical Map for verification.
4. Press **Download Data** to download the associated GPX file for the base station.
