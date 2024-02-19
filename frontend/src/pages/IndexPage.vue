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

    const boats = [
      { coordinates: [42.242306, -8.730914] },
      { coordinates: [42.245, -8.735] } // Agrega más coordenadas si es necesario
    ];

    boats.forEach(boat => {
      const marker = L.marker(boat.coordinates, { icon: boatIcon }).addTo(map);
      marker.bindPopup(`Latitude: ${boat.coordinates[0]}, Longitude: ${boat.coordinates[1]}`);
      marker.on('click', () => {
        if (currentEllipse) {
          currentEllipse.remove();
        }
        
        drawEllipse(map, boat.coordinates);
      });
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
