// Event listener for the button to fetch the latest GPS data
document.getElementById('fetch-data-button').addEventListener('click', function () {
  // Collect selected containers
  const selectedContainers = Array.from(document.querySelectorAll('.container-checkbox:checked'))
      .map(checkbox => checkbox.value);

  // Ensure at least one container is selected
  if (selectedContainers.length === 0) {
      alert('Please select at least one container.');
      return;
  }

  // Send a request to the server to update the map based on the selected containers
  fetch(`/api/update-map`, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ containers: selectedContainers })
  })
      .then(response => response.json())
      .then(data => {
          console.log('Fetched Data:', data);  // Log the data to the console for inspection

          // Display the telemetry data in a nicer format
          displayTelemetryData(data.telemetry_data);

          // Refresh the iframe to show the updated map
          document.getElementById('map-iframe').src = data.map_path;
      })
      .catch(error => console.error('Error updating map:', error));
});

// Function to display telemetry data in a nicer format
function displayTelemetryData(telemetryData) {
  const telemetryContent = document.getElementById('telemetry-content');
  telemetryContent.innerHTML = '';  // Clear previous content

  telemetryData.forEach((entry, index) => {
      const card = document.createElement('div');
      card.className = 'telemetry-card';

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
document.getElementById('start-search-button').addEventListener('click', function () {
  fetch('/api/start-search', {
      method: 'POST',
  })
      .then(response => response.json())
      .then(data => {
          alert('Search started!');
          console.log('Start Search Response:', data);
      })
      .catch(error => console.error('Error starting search:', error));
});

// Handle the end search button click
document.getElementById('end-search-button').addEventListener('click', function () {
  fetch('/api/end-search', {
      method: 'POST',
  })
      .then(response => response.json())
      .then(data => {
          alert('Search ended! Click below to download the GPX file.');
          console.log('End Search Response:', data);

          // Create a link to download the GPX file
          const downloadLink = document.createElement('a');
          downloadLink.href = data.gpx_download_url; // URL returned from the server to download the GPX file
          downloadLink.textContent = 'Download GPX File';
          downloadLink.download = 'search_data.gpx'; // Suggest a filename for the GPX file
          document.body.appendChild(downloadLink);
      })
      .catch(error => console.error('Error ending search:', error));
});