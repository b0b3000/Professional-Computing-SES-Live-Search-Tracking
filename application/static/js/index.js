// Tab handling logic
function openTab(evt, tabName) {
  var i, tabcontent, tablinks;

  // Hide all elements with class="tabcontent"
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Remove the "active" class from all tablinks
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

// Automatically click on the first tab to show it by default
document.addEventListener("DOMContentLoaded", function () {
  document.getElementsByClassName("tablinks")[0].click();
});

// Handle form submission with AJAX
$(document).ready(function () {
  $(".filter-box form").on("submit", function (e) {
    e.preventDefault(); // Prevent the default form submission

    $.ajax({
      type: "POST",
      url: "/filter-search",
      data: $(this).serialize(), // Serialize form data
      success: function (data) {
        const tbody = $(".scrollable-table tbody");
        tbody.empty(); // Clear existing rows

        // Populate table with returned data
        data.forEach((row) => {
          const newRow = `<tr class="search-row" data-gps='${row[5]}'> 
                      <td>${row[0]}</td>
                      <td>${row[1]}</td>
                      <td>${row[4]}</td>
                      <td>${row[2]}</td>
                      <td>${row[3]}</td>
                  </tr>`;
          tbody.append(newRow);
          console.log("GPS Data 'new row': ", newRow);
        });

        // Bind double-click event to new rows
        bindRowDoubleClick();

      },
      error: function (error) {
        console.error("Error fetching data:", error);
      },
    });
  });

  // Automatically click the first tab
  document.getElementsByClassName("tablinks")[0].click();
});

function bindRowDoubleClick() {
  // Double-click event handler for search-row
  document.querySelectorAll(".search-row").forEach(function (row) {
    row.addEventListener("dblclick", function () {
      const gpsData = this.getAttribute("data-gps");
      console.log("GPS Data from getAttribute, before AJAX request: ", gpsData);

      if (gpsData) {
        // AJAX request to render the map
        $.ajax({
          type: "GET",
          url: "/render-map",
          data: { gps: gpsData },
          success: function (response) {
            document.getElementById("historical-map-iframe").src =
              response.map_path;
          },
          error: function (error) {
            console.error("Error loading map:", error);
          },
        });
      } else {
        console.error("No GPS data found for this row.");
      }
    });
  });
}
// Call the bindRowDoubleClick function on page load to bind existing rows
bindRowDoubleClick();

// Event listener for the button to fetch the latest GPS data
document
  .getElementById("fetch-data-button")
  .addEventListener("click", function () {
    // Collect selected containers
    const selectedContainers = Array.from(
      document.querySelectorAll(".container-checkbox:checked"),
    ).map((checkbox) => checkbox.value);

    // Ensure at least one container is selected
    if (selectedContainers.length === 0) {
      alert("Please select at least one container.");
      return;
    }

    // Send a request to the server to update the map based on the selected containers
    fetch(`/api/update-map`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ containers: selectedContainers }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Fetched Data:", data); // Log the data to the console for inspection

        // Display the telemetry data in a nicer format
        displayTelemetryData(data.telemetry_data);

        // Refresh the iframe to show the updated map
        document.getElementById("map-iframe").src = data.map_path;
      })
      .catch((error) => console.error("Error updating map:", error));
  });

// Displays latest ping from each base in a sidebar, with telemetry data.
function displayTelemetryData(telemetryData) {
  const telemetryContent = document.getElementById("telemetry-content");
  telemetryContent.innerHTML = ""; // Clear previous content

  const latestPingsByBase = {}; // Stores only most recent ping for each base.
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

// Handle the start search button click
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
    })
    .catch((error) => console.error("Error starting search:", error));
});

// Handle the end search button click
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

      // Remove the animated border class
      mapContainer.classList.remove("search-running-animation");

      // Check if the download URL is present in the response
      if (!data.gpx_download_routes) {
        console.error("GPX download URL is missing in the response.");
        alert("GPX download URL is missing. Please try again later.");
        return;
      }

      // Get the selected containers
      const selectedContainers = Array.from(
        document.querySelectorAll(".container-checkbox:checked"),
      ).map((checkbox) => checkbox.value);

      // Log selected containers for debugging
      console.log("Selected Containers:", selectedContainers);

      // Check if the table exists
      let downloadTable = document.getElementById("download-table");

      if (!downloadTable) {
        const tableContainer = document.getElementById("table-container");
        const linkToRemove = tableContainer.querySelector("a");
        // Check if the link contains the specific text
        if (
          linkToRemove &&
          linkToRemove.textContent.includes(
            "Complete a search to create GPX files",
          )
        ) {
          linkToRemove.remove();
        }

        // Create the table if it doesn't exist
        downloadTable = document.createElement("table");
        downloadTable.className = "gpx-table";
        downloadTable.id = "download-table";

        // Append the table to the container
        document.getElementById("table-container").appendChild(downloadTable);
      } else {
        // Clear existing rows if the table exists
        downloadTable.innerHTML = "";
      }

      // Add rows for each selected container
      data.gpx_download_routes.forEach((route) => {
        const row = downloadTable.insertRow();

        const cell1 = row.insertCell(0);
        cell1.textContent = route;

        const cell2 = row.insertCell(1);
        const downloadButton = document.createElement("a");
        downloadButton.textContent = "Download GPX";
        downloadButton.href = `/download/${route}`;
        downloadButton.download = `${route}_search_data.gpx`; // Suggest a filename for the GPX file
        cell2.appendChild(downloadButton);
      });
    })
    .catch((error) => console.error("Error ending search:", error));
});
