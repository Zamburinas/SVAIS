<template>
  <q-page>
    <div id="map"></div>
  </q-page>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { inject } from 'vue';
let Areas;
let intervalId;
let currentEllipse = null;
let currentLines = [];
let linesGroup = L.layerGroup();
let helpers= inject('helpers');
let map=null;
async function initializeMapAndLocator() {
  if (!map) {
  let coorGoniometros=null;
  let boats =null;
  let coords = await helpers.getAllCoords();
  if(coords){
    coorGoniometros=coords.radiogonos;
    boats =JSON.parse(coords.boats);
  }
  Areas = await helpers.getProtectedAreas();
  
      
  map= L.map('map').setView([37.0902, -95.7129], 5);

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

  drawAreas();

  boats.forEach(boat => {
    const marker = L.marker([boat.data.LAT,boat.data.LON], { icon: boatIcon }).addTo(map);
    marker.bindPopup(`Latitude: ${boat.data.LAT}, Longitude: ${boat.data.LON}`);
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
      
      drawLinesWithAnimation(map, [boat.data.LAT,boat.data.LON], coorGoniometros.map(antenna => antenna));
    });
  });

  map.on('click', () => {
    if (currentEllipse) {
      currentEllipse.remove();
      currentEllipse = null;
      linesGroup.clearLayers();
    }
  });


  function drawEllipse(map, boat,center, semiMajorAxis, semiMinorAxis, angle) {
    var angle = angle * Math.PI / 180;
    var numSegments = 400;
    var points = [];
    var angleOffset = 2 * Math.PI / numSegments;

    for (var i = 0; i < numSegments; i++) {
        var angleRad = i * angleOffset;
        var x = center[0] + (0.0001)*semiMajorAxis * Math.cos(angleRad) * Math.cos(angle) - (0.0001)*semiMinorAxis * Math.sin(angleRad) * Math.sin(angle);
        var y = center[1] + (0.0001)*semiMajorAxis * Math.cos(angleRad) * Math.sin(angle) + (0.0001)*semiMinorAxis * Math.sin(angleRad) * Math.cos(angle);
        points.push([x, y]);
    }
    const q = isInsideEllipse(boat, center, semiMajorAxis, semiMinorAxis, angle);
    const fillColor = q ? '#00FF00' : '#FF0000';

    currentEllipse =L.polygon(points, {
        color: 'dark',
        fillColor: fillColor,
        fillOpacity: 0.4,
        interactive: false
    }).addTo(map);
  }
  }else{
    map.eachLayer(layer => {
      map.removeLayer(layer);
    });
  }


    function isInsideEllipse(point, center, semiMajorAxis, semiMinorAxis, angle) {
      const dx = point[0] - center[0];
      const dy = point[1] - center[1];
      const angleRad = angle * Math.PI / 180;
      const cosAngle = Math.cos(angleRad);
      const sinAngle = Math.sin(angleRad);
      const rotatedDx = cosAngle * dx - sinAngle * dy;
      const rotatedDy = sinAngle * dx + cosAngle * dy;

      return (rotatedDx * rotatedDx) / (semiMajorAxis*(0.0001) * semiMajorAxis*(0.0001)) + (rotatedDy * rotatedDy) / (semiMinorAxis *(0.0001)* semiMinorAxis*(0.0001)) <= 1;
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
          }                                                       //Por ahora el centro de la elipse es el propio barco
          drawEllipse(map,[boatCoordinates[0],boatCoordinates[1]] ,[boatCoordinates[0],boatCoordinates[1]],113.5624900059602,127.04089357908843,-135.35846661098765);
        }
      }, 50);
      
      line.addTo(linesGroup);
      
    });
    
    linesGroup.addTo(map);
  }
}

function drawAreas() {
  console.log("asdasd");
    Areas.forEach(area => {
        const coordinates = area.coordinates[0].map(coord => [coord[0], coord[1]]);
        L.polygon(coordinates, { color: 'red' }).addTo(map);
    });
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
