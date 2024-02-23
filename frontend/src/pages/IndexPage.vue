<template>
  <q-page>
    <div id="map"></div>
  </q-page>
</template>

<script setup>
import { onMounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { inject } from 'vue';


let currentMarker = null;
let currentEllipse = null;
let currentLines = [];
let linesGroup = L.layerGroup();
let helpers= inject('helpers');

async function initializeMapAndLocator() {
  let coorGoniometros=null;
  let boats =null;
  let coords = await helpers.getAllCoords();
  if(coords){
    coorGoniometros=coords.radiogonos;
    boats =coords.boats;
    console.log(boats);
  }
  
      
  const map = L.map('map').setView([42.242306, -8.730914], 14)

  L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    id: "streets-v12",
    accessToken: "pk.eyJ1IjoiYm9id2F0Y2hlcngiLCJhIjoiY2xiMGwwZThrMWg3aTNwcW1mOGRucHh6bSJ9.kNHlmRqkRSxYNeipcKkJhw",
  }).addTo(map);

  const boatIcon = L.icon({
    iconUrl: 'src/assets/cruise_colored-icon.png',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
  const antennaIcon = L.icon({
    iconUrl: 'src/assets/antena.png',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });

  coorGoniometros.forEach(Goni => {
    const marker = L.marker(Goni, { icon: antennaIcon }).addTo(map);
    marker.bindPopup(`Latitude: ${Goni[0]}, Longitude: ${Goni[1]}`);
  });

  boats.forEach(boat => {
    const marker = L.marker(boat.slice(0, 2), { icon: boatIcon }).addTo(map);
    marker.bindPopup(`Latitude: ${boat[0]}, Longitude: ${boat[1]}`);
    marker.on('click', () => {
      if (currentEllipse) {
        currentEllipse.remove();
        linesGroup.clearLayers();
      }

      if (currentLines.length > 0) {
        currentLines.forEach(line => {
          line.remove();
        });
        currentLines = [];
      }

      
      drawLinesWithAnimation(map, boat, coorGoniometros.map(antenna => antenna));
    });
  });

  map.on('click', () => {
    if (currentEllipse) {
      currentEllipse.remove();
      currentEllipse = null;
      linesGroup.clearLayers();
    }
  });


  function drawEllipse(map, center, semiMajorAxis, semiMinorAxis, angle) {
    var angle = angle * Math.PI / 180;
    var numSegments = 400;
    var points = [];
    var angleOffset = 2 * Math.PI / numSegments;

    for (var i = 0; i < numSegments; i++) {
        var angleRad = i * angleOffset;
        var x = center[0] + (0.001)*semiMajorAxis * Math.cos(angleRad) * Math.cos(angle) - (0.001)*semiMinorAxis * Math.sin(angleRad) * Math.sin(angle);
        var y = center[1] + (0.001)*semiMajorAxis * Math.cos(angleRad) * Math.sin(angle) + (0.001)*semiMinorAxis * Math.sin(angleRad) * Math.cos(angle);
        points.push([x, y]);
    }

    currentEllipse =L.polygon(points, {
        color: 'dark',
        fillColor: '#7FFF00',
        fillOpacity: 0.4,
        interactive: false
    }).addTo(map);
}

  function drawLinesWithAnimation(map, boatCoordinates, antennaCoordinates) {
    antennaCoordinates.forEach(antennaCoord => {
      const latlngs = [antennaCoord, boatCoordinates];
      const line = L.polyline([], { color: '#444', dashArray: '10, 10', weight: 1 });
      
      let currentLatlng = [antennaCoord[0], antennaCoord[1]];
      let steps = 100;
      let step = 0;

      const deltaLat = (boatCoordinates[0] - antennaCoord[0]) / steps;
      const deltaLng = (boatCoordinates[1] - antennaCoord[1]) / steps;

      const lineDrawingInterval = setInterval(() => {
        if (step < steps) {
          currentLatlng[0] += deltaLat;
          currentLatlng[1] += deltaLng;
          line.setLatLngs([antennaCoord, currentLatlng]);
          step++;
        } else {
          clearInterval(lineDrawingInterval);
          if(currentEllipse){
            currentEllipse.remove();
          }
          drawEllipse(map, boatCoordinates.slice(0,2),boatCoordinates[4],boatCoordinates[5],boatCoordinates[6]);
        }
      }, 50);
      
      line.addTo(linesGroup);
      
    });
    
    linesGroup.addTo(map);
  }
}

onMounted(() => {
  initializeMapAndLocator();
})
</script>

<style>
#map {
  width: 100%;
  height: 92vh;
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
