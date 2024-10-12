// Function to open a specific tab and hide the others.
function openTab(evt, tabName) {
  // Hides all tab content elements.
  const tabcontent = document.getElementsByClassName("tabcontent");
  for (let i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Removes the active class from all buttons
  const tablinks = document.getElementsByClassName("tablinks");
  for (let i = 0; i < tablinks.length; i++) {
    tablinks[i].classList.remove("active");
  }

  // Shows the clicked tab content and add the active class to the clicked button
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.classList.add("active");
}

// Default: Show the first tab when the DOM is fully loaded.
document.addEventListener('DOMContentLoaded', function() {
  document.getElementsByClassName("tablinks")[0].click();
});

// Handles form submission with AJAX
$(document).ready(function () {
  $(".filter-box form").on("submit", function (e) {
    e.preventDefault();    // Prevents the default form submission

    $.ajax({
      type: "POST",
      url: "/filter-search",
      data: $(this).serialize(),    // Serializes form data
      success: function (data) {
        const tbody = $(".scrollable-table tbody");
        tbody.empty();    // Clears existing rows

        // Populates table with returned data
        data.forEach((row) => {

          const newRow = `<tr class='search-row' session_id='${row[0]}' base_station ='${row[1]}'>
                      <td>${row[0]}</td> <!-- ID -->
                      <td>${row[1]}</td> <!-- Base Station -->
                      <td>${row[4]}</td> <!-- Date -->
                      <td>${row[2]}</td> <!-- Start Time -->
                      <td>${row[3]}</td> <!-- End Time -->
                      <td>${row[5]}</td> <!-- GPS Data -->
                      <td>${row[6]}</td> <!-- Download Link -->
                  </tr>`;
          tbody.append(newRow);
          console.log("GPS Data 'new row': ", newRow);
        });

        attachButtonListeners();
      },
      error: function (error) {
        console.error("Error fetching data:", error);
      },
    });
  });

  // Automatically clicks the first tab on page load.
  document.getElementsByClassName("tablinks")[0].click();
});

// Attaches event listeners for display buttons in each search result row.
function attachButtonListeners(){
  document.querySelectorAll(".search-row").forEach(function (row) {
    const displayButton = row.querySelector("#display-historical-button");
    displayButton.addEventListener("click", function () {
      session_id = row.getAttribute("session_id");
      base_station = row.getAttribute("base_station");

      // AJAX request to render the map based on the session and base station.
      $.ajax({
        type: "GET",
        url: "/render-map",
        data: {session_id: session_id, base_station: base_station},
        success: function (response) {
          document.getElementById("historical-map-iframe").src =
            response.map_path;
        },
        error: function (error) {
          console.error("Error loading map:", error);
        },
      });
    });
  });
}
attachButtonListeners();

// Event listener for container label clicks to toggle selection.
document.querySelectorAll(".container-label").forEach((label) => {
  label.addEventListener("click", function () {
    // Toggles the active class on click
    label.classList.toggle("active");
  });
});

// Event listener for the button to fetch the latest GPS data.
document
  .getElementById("fetch-data-button")
  .addEventListener("click", function () {
    // Collect selected containers based on active class.
    const selectedContainers = Array.from(
      document.querySelectorAll(".container-label.active"),
    ).map((label) => label.getAttribute("data-container"));

    // Ensures at least one container is selected.
    if (selectedContainers.length === 0) {
      alert("Please select at least one container.");
      return;
    }

    // Sends a request to the server to update the map based on the selected containers.
    fetch(`/api/update-map`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ containers: selectedContainers }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Fetched Data:", data);    // Logs the data to the console for inspection.

        // Displays the telemetry data in a nicer format.
        displayTelemetryData(data.telemetry_data);

        // Refreshes the iframe to show the updated map.
        document.getElementById("map-iframe").src = data.map_path;
      })
      .catch((error) => console.error("Error updating map:", error));
  });


// Select2 Library for selecting multiple base stations in the historical data filter.
  $(document).ready(function() {
    $('#base-station').select2({
        placeholder: "Select Base Stations",
        allowClear: true,
        width: '100%'    // Ensures the Select2 input takes up the full width of its parent container.
    });
});

// Function to display the latest telemetry data from each base station in the sidebar.
function displayTelemetryData(telemetryData) {
  const telemetryContent = document.getElementById("telemetry-content");
  telemetryContent.innerHTML = "";    // Clears previous content

  const latestPingsByBase = {};    // Stores only most recent ping for each base.
  telemetryData.forEach((entry) => {
    const baseName = entry.name;
    if (
      !latestPingsByBase[baseName] ||
      entry.time > latestPingsByBase[baseName].time
    ) {
      latestPingsByBase[baseName] = entry;
    }
  });
  const latestPings = Object.values(latestPingsByBase);

  latestPings.forEach((entry, index) => {
    const card = document.createElement("div");
    card.className = "telemetry-card";

    // Outlines the box in red if the latest ping for a base was >5 minutes ago.
    const timeDiff = (new Date() - new Date(entry.time)) / 60000;
    if (timeDiff > 5) {
      card.style.border = "2px solid red";
    } else {
      card.style.border = "1px solid green";
    }

    card.innerHTML = `
      <p class="title">${entry.longname}</p>
      <p><strong>Device ID:</strong> ${entry.name}</p>
      <p><strong>Time:</strong> ${entry.time}</p>
      <hr>
      <p><strong>Coordinates:</strong> ${entry.lat}, ${entry.lon}</p>
      <hr>
      <p><strong>Battery Level:</strong> ${entry.telemetry.battery}%</p>
      <p><strong>Altitude:</strong> ${entry.telemetry.altitude}</p>
    `;

    telemetryContent.appendChild(card);
  });
}

// Handles the click event for the start search button.
document.getElementById("start-search").addEventListener("click", function () {
  fetch("/api/start-search", {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      alert("Search started!");
      console.log("Start Search Response:", data);
      document
        .getElementById("map-container")
        .classList.add("search-running-animation");
      document.getElementById("end-search").disabled = false;
      document.getElementById("end-search").classList.remove("disabled");
      document.getElementById("end-search").classList.add("ready");

      document.getElementById("start-search").disabled = true;
      document.getElementById("start-search").classList.remove("ready");
      document.getElementById("start-search").classList.add("disabled");

      filterButton = document.getElementById("filter-pings-button");
      filterButton.disabled = false;

    })
    .catch((error) => console.error("Error starting search:", error));
});


// FILTER PINGS BUTTON
document
  .getElementById("filter-pings-button")
  .addEventListener("click", function () {
    const filterButton = this;
    const isFiltering = filterButton.getAttribute("data-filtering") === "true";

    if (!isFiltering) {
      const filterTime = new Date().toISOString().split(".")[0]; // milliseconds omitted
      console.log("Current time captured for filtering:", filterTime);

      // Send the filter time to the /filter-pings route
      $.ajax({
        type: "POST",
        url: "/filter-pings",
        data: { filter_time: filterTime },
        success: function (response) {
          console.log("Pings filtered successfully:", response.message);

          // Update the map iframe new filtered map
          const iframe = document.getElementById("map-iframe");
          if (iframe) {
            iframe.src = response.map_path;
          }

          filterButton.innerHTML = "Revert Pings";
          filterButton.setAttribute("data-filtering", "true");
        },
        error: function (error) {
          console.error("Error filtering pings:", error);
        },
      });
    } else {
      console.log("Reverting to original pings...");
      const iframe = document.getElementById("map-iframe");
      if (iframe) {
        iframe.src = "/static/footprint.html";
      }
      filterButton.innerHTML = "Filter Pings";
      filterButton.setAttribute("data-filtering", "false");
    }
  });


// Handles the click event for the end search button.
document.getElementById("end-search").addEventListener("click", function () {
  const mapContainer = document.getElementById("map-container");

  if (!mapContainer.classList.contains("search-running-animation")) {
    alert("Search is not currently running.");
    return;
  }

  fetch("/api/end-search", {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      alert("Search ended! Click below to download the GPX file.");
      console.log("End Search Response:", data);

      // Removes the animated border class.
      mapContainer.classList.remove("search-running-animation");
      document.getElementById("end-search").disabled = true;
      document.getElementById("end-search").classList.remove("ready");
      document.getElementById("end-search").classList.add("disabled");

      document.getElementById("start-search").disabled = false;
      document.getElementById("start-search").classList.remove("disabled");
      document.getElementById("start-search").classList.add("ready");

      // Checks if the download URL is present in the response.
      if (!data.gpx_download_routes) {
        console.error("GPX download URL is missing in the response.");
        alert("GPX download URL is missing. Please try again later.");
        return;
      }

      // Gets the selected containers based on the active class.
      const selectedContainers = Array.from(
        document.querySelectorAll(".container-label.active"),    // Updated selector.
      ).map((label) => label.getAttribute("data-container"));

      // Logs selected containers for debugging.
      console.log("Selected Containers:", selectedContainers);

      // Checks if the table exists.
      let downloadTable = document.getElementById("download-table");

      if (!downloadTable) {
        const tableContainer = document.getElementById("table-container");
        const linkToRemove = tableContainer.querySelector("a");
        // Checks if the link contains the specific text.
        if (
          linkToRemove &&
          linkToRemove.textContent.includes(
            "Complete a search to create GPX files",
          )
        ) {
          linkToRemove.remove();
        }

        // Creates the table if it doesn't exist.
        downloadTable = document.createElement("table");
        downloadTable.className = "gpx-table";
        downloadTable.id = "download-table";

        // Appends the table to the container.
        document.getElementById("table-container").appendChild(downloadTable);
      } else {
        // Clears existing rows if the table exists.
        downloadTable.innerHTML = "";
      }

      // Adds rows for each selected container.
      data.gpx_download_routes.forEach((route) => {
        const row = downloadTable.insertRow();

        const cell1 = row.insertCell(0);
        cell1.textContent = route;

        const cell2 = row.insertCell(1);
        const downloadButton = document.createElement("a");
        downloadButton.textContent = "Download Data";
        downloadButton.href = `/download/${route}`;
        downloadButton.download = `${route}_search_data.gpx`; // Suggests a filename for the GPX file.
        cell2.appendChild(downloadButton);
      });
    })
    .catch((error) => console.error("Error ending search:", error));
});
// Js for tutorial Boxes Historical Data
// Show the tutorial boxes
function showTutorial() {
  document.getElementById('tutorial-box-1').style.display = 'block';
  document.getElementById('tutorial-box-2').style.display = 'block';
}

// Hide the individual tutorial boxes when the user clicks "Got it!"
function hideBox(boxNumber) {
  document.getElementById('tutorial-box-' + boxNumber).style.display = 'none';
}
