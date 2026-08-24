function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition, showError);
  } else {
    alert("Geolocation is not supported by this browser.");
  }
}

function showPosition(position) {
  const latitude = position.coords.latitude;
  const longitude = position.coords.longitude;
  const accuracy = position.coords.accuracy;

  // Display the location information on the page
  document.getElementById("latitude").textContent = latitude;
  document.getElementById("longitude").textContent = longitude;
  document.getElementById("accuracy").textContent = accuracy + " meters";

  // Optionally, use a mapping library like Google Maps to display the location on a map
  // You'll need to include the Google Maps JavaScript API and initialize it
  // with your API key. Then, you can create a map and add a marker to the
  // user's location using the latitude and longitude coordinates.
}

function showError(error) {
  switch (error.code) {
    case error.PERMISSION_DENIED:
      alert("User denied the request for Geolocation.");
      break;
    case error.POSITION_UNAVAILABLE:
      alert("Location information is unavailable.");
      break;
    case error.TIMEOUT:
      alert("The request to get user location timed out.");
      break;
    case error.UNKNOWN_ERROR:
      alert("An unknown error occurred.");
      break;
  }
}

// Call the getLocation function to start the process
getLocation();