<template>
  <q-page>
    <q-btn class="absolute-top-right" @click="toggleMenu">Menu</q-btn>
    <div id="menu" class="menu-right" v-show="showMenu">Hola</div>
    <div id="map" @click="hideMapPopup"></div>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { inject } from 'vue';

let currentMarker = null;
let showMenu = ref(false); // Controla la visibilidad del menú

let helpers = inject('helpers');
let boats = ref([]);

async function initializeMapAndLocator() {
    const map = L.map('map').setView([42.242306, -8.730914], 14)

    L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
      maxZoom: 19,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      id: "streets-v12",
      accessToken: "pk.eyJ1IjoiYm9id2F0Y2hlcngiLCJhIjoiY2xiMGwwZThrMWg3aTNwcW1mOGRucHh6bSJ9.kNHlmRqkRSxYNeipcKkJhw",
    }).addTo(map);

}

function toggleMenu() {
  showMenu.value = !showMenu.value; // Cambia el estado de la visibilidad del menú
}

function showBoatOnMap(boat) {
  const map = L.map('map');
  const boatIcon = L.icon({
    iconUrl: 'src/assets/cruise_colored-icon.png',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });

  if (currentMarker) {
    map.removeLayer(currentMarker);
  }

  currentMarker = L.marker(boat, { icon: boatIcon }).addTo(map);
  currentMarker.bindPopup(`Latitude: ${boat[0]}, Longitude: ${boat[1]}`).openPopup();
}


onMounted(() => {
  initializeMapAndLocator();
})
</script>

<style>
#map {
  width: 100%;
  height: 92vh;
  position: relative;
}

.absolute-top-right {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100;
}

.menu-right {
  width: 80%; /* Ajusta el ancho del menú */
  max-height: 100vh; /* Establece una altura máxima para el menú */
  position: fixed; /* Usa posición fija para bloquear el menú en la pantalla */
  top: 0;
  right: 0;
  background-color: white; /* Añade un color de fondo para el menú */
  border-left: 1px solid #ccc; /* Añade un borde para separar el menú del mapa */
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  padding: 20px;
  box-sizing: border-box;
  overflow-y: auto; /* Añade un scroll si el contenido del menú es más grande que la pantalla */
}

body {
  overflow: hidden; /* Bloquea el scroll en el cuerpo de la página */
}

.q-btn {
  background-color: #2196f3; /* Cambia el color de fondo del botón */
  color: white; /* Cambia el color del texto del botón a blanco */
}
</style>
