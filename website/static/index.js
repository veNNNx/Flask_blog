function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

document.addEventListener("DOMContentLoaded", function () {
  window.addEventListener("scroll", function () {
    if (window.scrollY > 0) {
      document.getElementById("navbar_top").classList.add("fixed-top");
      // add padding top to show content behind navbar
      navbar_height = document.querySelector(".navbar").offsetHeight;
      document.body.style.paddingTop = navbar_height + "px";
    } else {
      document.getElementById("navbar_top").classList.remove("fixed-top");
      // remove padding top from body
      document.body.style.paddingTop = "0";
    }
  });
});

function send_lat_lon(lat, lon) {
  fetch("/send_lat_lon", {
    method: "POST",
    body: JSON.stringify({ lat: lat, lon: lon }),
  });
}

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.watchPosition(showPosition);
  } else {
    document.getElementById("findMe").innerHTML =
      "Geolocation is not supported by this browser.";
  }
}
function showPosition(position) {
  send_lat_lon(position.coords.latitude, position.coords.longitude);
  location.reload();
}
