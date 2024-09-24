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

// Function to display telemetry data in a nicer format
function displayTelemetryData(telemetryData) {
  const telemetryContent = document.getElementById("telemetry-content");
  telemetryContent.innerHTML = ""; // Clear previous content

  telemetryData.forEach((entry, index) => {
    const card = document.createElement("div");
    card.className = "telemetry-card";

    card.innerHTML = `
          <p class="title">Ping ${index + 1}</p>
          <p><strong>Device Name:</strong> ${entry.name}</p>
          <p><strong>Time:</strong> ${entry.time}</p>
          <hr>
          <p><strong>Battery Level:</strong> ${entry.telemetry.battery}%</p>
          <p><strong>Altitude:</strong> ${entry.telemetry.altitude}</p>
      `;

    telemetryContent.appendChild(card);
  });
}

// Handle the start search button click
document
  .getElementById("start-search")
  .addEventListener("click", function () {
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
document
  .getElementById("end-search")
  .addEventListener("click", function () {
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

        // Check if the download URL is present in the response
        if (!data.gpx_download_url) {
          console.error("GPX download URL is missing in the response.");
          alert("GPX download URL is missing. Please try again later.");
          return;
        }

        // Remove the animated border class
        mapContainer.classList.remove("search-running-animation");

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
          if (linkToRemove && linkToRemove.textContent.includes("Complete a search to create GPX files")) {
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
        selectedContainers.forEach((container) => {
          const row = downloadTable.insertRow();

          const cell1 = row.insertCell(0);
          cell1.textContent = container;

          const cell2 = row.insertCell(1);
          const downloadButton = document.createElement("a");
          downloadButton.href = data.gpx_download_url; // URL returned from the server to download the GPX file
          downloadButton.textContent = "Download GPX";
          downloadButton.download = `${container}_search_data.gpx`; // Suggest a filename for the GPX file
          cell2.appendChild(downloadButton);
        });
      })
      .catch((error) => console.error("Error ending search:", error));
  });
