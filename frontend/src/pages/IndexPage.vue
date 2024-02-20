<template>
  <q-page>
    <div id="map"></div>
  </q-page>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import L from 'leaflet'
  import 'leaflet/dist/leaflet.css'

  let currentMarker = null;
  let currentEllipse = null;
  let currentLines = [];

  function initializeMapAndLocator() {
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

    const coorGoniometros=[
      {coordinates:[43.6728903,-7.8391903]},
      {coordinates: [56.130366,-106.346771]},
      {	coordinates: [-34.61315,-58.37723]}];

    const boats = [
      { coordinates: [42.242306, -8.730914] },
      { coordinates: [42.245, -8.735] } // Agrega más coordenadas si es necesario
    ];

    coorGoniometros.forEach(Goni => {
      const marker = L.marker(Goni.coordinates, { icon: antennaIcon }).addTo(map);
      marker.bindPopup(`Latitude: ${Goni.coordinates[0]}, Longitude: ${Goni.coordinates[1]}`);
    });


    boats.forEach(boat => {
      const marker = L.marker(boat.coordinates, { icon: boatIcon }).addTo(map);
      marker.bindPopup(`Latitude: ${boat.coordinates[0]}, Longitude: ${boat.coordinates[1]}`);
      marker.on('click', () => {
        if (currentEllipse) {
          currentEllipse.remove();
        }

        if (currentLines.length > 0) {
          linesGroup.clearLayers();
          currentLines.forEach(line => {
            line.remove();
          });
          currentLines = [];
        }

        drawEllipse(map, boat.coordinates);
        drawLinesWithAnimation(map, boat.coordinates, coorGoniometros.map(antenna => antenna.coordinates));
      });
    });

    map.on('click', () => {
      if (currentEllipse) {
        currentEllipse.remove();
        currentEllipse = null;
      }
      linesGroup.clearLayers(); 
      if (currentLines.length > 0) {
        currentLines.forEach(line => {
          line.remove();
        });
        currentLines = [];
      }
   });

    function drawEllipse(map, center) {
      const radius=Math.random() * (0.5 - 0.01) + 0.01; // Ajusta el radio de la elipse (en kilómetros)
      const numberOfSegments = 36; // Define la cantidad de segmentos para la elipse
      currentEllipse = L.circle([center[0], center[1]], {
        color: 'dark',
        fillColor: '#7FFF00', // Color gris muy suave
        fillOpacity: 0.4, // Opacidad de relleno
        radius: radius * 1000, // Convierte el radio de kilómetros a metros
        interactive: false // Evita que la elipse sea interactiva
      }).addTo(map);
    }

// Antes de tu función drawLinesWithAnimation, declara una variable global para almacenar las líneas
let linesGroup = L.layerGroup().addTo(map);

function drawLinesWithAnimation(map, boatCoordinates, antennaCoordinates) {
  antennaCoordinates.forEach(antennaCoord => {
    const latlngs = [antennaCoord, boatCoordinates];
    const line = L.polyline([], { color: '#444', dashArray: '10, 10', weight: 1 }).addTo(map);
    
    let currentLatlng = [antennaCoord[0], antennaCoord[1]];
    let steps = 50; // Número de pasos para la animación
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
      }
    }, 50); // Ajusta el intervalo de animación según tu preferencia
  });
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
