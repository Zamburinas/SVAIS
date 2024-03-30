<template>
  <q-page>
    <div id="map"></div>

    <!-- Botón para abrir el menú desplegable -->
    <q-btn class="menu-button" label="Menu">
      <q-menu fit>
        <div class="q-pa-md">
          <q-input outlined v-model="searchQuery" @keyup="search" placeholder="Search boats...">
          </q-input>
        </div>
        <q-virtual-scroll :items="filteredBoats" item-height="50">
          <template v-slot="{ item }">
            <q-item clickable v-ripple :class="{ 'selected': item.checked }" @click="toggleBoat(item)">
              <q-item-section>
                <label :for="'boat_checkbox_' + item.index" class="boat-checkbox">
                  <img :src="item.photo" style="width: 32px; height: 32px; border-radius: 50%;">
                  <span>{{ item.name }}</span>
                </label>
              </q-item-section>
              <!-- <input type="checkbox" :id="'boat_checkbox_' + item.index" v-model="item.checked"
                @change="handleBoatSelection(item)" style="display: none;"> -->
            </q-item>
          </template>
        </q-virtual-scroll>
      </q-menu>
    </q-btn>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { inject } from 'vue';
let searchQuery = "";
let markers = new Map(); // Usamos un Map para almacenar los marcadores de barcos
let routes = new Map(); // Mapa para almacenar las rutas de los barcos
let helpers = inject('helpers');
let usedColors = new Set();
let pointMarkers = new Map();
let map = null; // Variable para almacenar la instancia del mapa
let boats = ref([]); // Variable para almacenar los datos de los barcos
let filteredBoats = ref([]); // Variable para almacenar los barcos filtrados

async function initializeMapAndLocator() {
  map = L.map('map').setView([37.0902, -95.7129], 4);

  L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    id: 'streets-v12',
    accessToken: 'pk.eyJ1IjoiYm9id2F0Y2hlcngiLCJhIjoiY2xiMGwwZThrMWg3aTNwcW1mOGRucHh6bSJ9.kNHlmRqkRSxYNeipcKkJhw',
  }).addTo(map);

  let coords = JSON.parse(await helpers.getBoatInfo());
  // Asignar los datos de los barcos a la variable boats
  boats.value = coords.map(coord => ({
    MMSI: coord.MMSI,
    name: coord.VesselName,
    photo: "src/assets/cruise_colored-icon.png",
    checked: false,
    route: [] // Puedes agregar la ruta si también está disponible en coords
  }));
  filteredBoats.value = boats.value;
}

async function handleBoatSelection(boat) {
  if (boat.checked) {
    try {
      const coords = await helpers.getBoatRoute({ "MMSI": boat.MMSI });

      // Create boat icon
      const boatIcon = L.icon({
        iconUrl: 'src/assets/cruise_colored-icon.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      });

      // Create and add boat marker to map
      const boatMarker = L.marker(coords.route[coords.route.length - 1], { icon: boatIcon }).addTo(map);
      markers.set(boat, boatMarker); // Associate the marker with the boat on the map

      // Create and add boat route to map
      const boatRoute = L.polyline(coords.route, { color: randomColor(usedColors), weight: 5 }).addTo(map);
      routes.set(boat, boatRoute); // Associate the route with the boat on the map

      // Add click event to boat route to show popup
      boatRoute.on('click', function (e) {
        L.popup()
          .setLatLng(e.latlng)
          .setContent('Here we can put information about the average and maximum speed for now')
          .openOn(map);
      });

      // Create markers for all points in the route except the last one
      const PointIcon = L.icon({
        iconUrl: 'src/assets/point.png',
        iconSize: [16, 16],
        iconAnchor: [8, 8],
      });
      const pointMarkersArray = coords.route.slice(0, -1).map(coord => L.marker(coord, { icon: PointIcon }).addTo(map));
      pointMarkers.set(boat, pointMarkersArray);
    } catch (error) {
      console.error('Error fetching boat route:', error);
    }
  } else {
    removeBoat(boat);
  }
}

function removeBoat(boat) {
  // Remove boat marker, route, and point markers associated with the deselected boat
  removeMarker(markers.get(boat));
  removeRoute(routes.get(boat));
  removePointMarkers(pointMarkers.get(boat));

  // Remove boat from maps
  markers.delete(boat);
  routes.delete(boat);
  pointMarkers.delete(boat);
}

function removeMarker(marker) {
  if (marker) {
    map.removeLayer(marker);
  }
}

function removeRoute(route) {
  if (route) {
    map.removeLayer(route);
  }
}

function removePointMarkers(pointMarkersArray) {
  if (pointMarkersArray) {
    pointMarkersArray.forEach(marker => map.removeLayer(marker));
  }
}

// Función para cambiar la selección de un barco cuando se hace clic en toda la fila
function toggleBoat(boat) {
  boat.checked = !boat.checked;
  handleBoatSelection(boat);
}

function randomColor(usedColors) {
  let color;
  do {
    color = '#' + Math.floor(Math.random() * 16777215).toString(16);
  } while (usedColors.has(color));
  return color;
}

function search() {
  // Filtrar los barcos que coincidan con la consulta de búsqueda
  filteredBoats.value = boats.value.filter(boat => {
    return boat.name.toLowerCase().includes(searchQuery.toLowerCase());
  });
}
onMounted(() => {
  initializeMapAndLocator();
});

</script>

<style>
#map {
  width: 100%;
  height: 92vh;
  position: relative;
  z-index: 1;
}

.menu-button {
  z-index: 2;
  background-color: #1976D2;
  position: absolute;
  top: 1vh;
  right: 1vw;
  color: white;
}

.selected {
  background-color: #9ecfff !important;
}
</style>
