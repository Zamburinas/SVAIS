<template>
  <q-page>
    <div id="map"></div>

    <!-- Botón para abrir el menú desplegable -->
    <q-btn @click="toggleMenu" class="absolute-top-right">Menú</q-btn>

    <!-- Menú desplegable -->
    <q-drawer v-model="showMenu" side="right" content-class="small-drawer" class="menu-list">
      <div class="search-bar">
        <input type="text" v-model="searchQuery" @input="search" placeholder="Boat name...">
      </div>
      <q-list>
        <!-- Contenido del menú -->
        <q-item v-ripple v-for="(boat, index) in filteredBoats" :key="index" class="boat-item" :class="{ 'selected': boat.checked }" @click="toggleBoat(boat)">
          <q-item-section>
            <!-- Contenedor del barco (simulando un checkbox) -->
            <label :for="'boat_checkbox_' + index" class="boat-checkbox">
              <!-- Foto y nombre del barco -->
              <img :src="boat.photo" style="width: 32px; height: 32px; border-radius: 50%;">
              <span>{{ boat.name }}</span>
            </label>
          </q-item-section>
          <!-- Checkbox oculto -->
          <input type="checkbox" :id="'boat_checkbox_' + index" v-model="boat.checked" @change="handleBoatSelection(boat)" style="display: none;">
        </q-item>
      </q-list>
    </q-drawer>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { inject } from 'vue';
let searchQuery="";
let markers = new Map(); // Usamos un Map para almacenar los marcadores de barcos
let routes = new Map(); // Mapa para almacenar las rutas de los barcos
let helpers = inject('helpers');
let usedColors = new Set();

let showMenu = ref(false); // Variable para controlar la visibilidad del menú
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
  filteredBoats.value=boats.value;
}

// Función para el evento click del botón de menú
function toggleMenu() {
  showMenu.value = !showMenu.value;
  const pageContainer = document.querySelector('.q-page-container');
  if (showMenu.value) {
    pageContainer.style.paddingRight = '0 !important';
  } 
}

async function handleBoatSelection(boat) {
  if (boat.checked) {
    let coords = await helpers.getBoatRoute({"MMSI": boat.MMSI});
    console.log(coords.route);
    boat.route =  Array.from(coords.route);
      const boatIcon = L.icon({
        iconUrl: 'src/assets/cruise_colored-icon.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      });

      const boatMarker = L.marker(boat.route[boat.route.length - 1], { icon: boatIcon }).addTo(map);
      markers.set(boat, boatMarker); // Asocia el marcador con el barco en el mapa

      const boatRoute = L.polyline(boat.route, { color: randomColor(usedColors), weight: 5 }).addTo(map); // Asigna un color aleatorio no utilizado a la ruta
      routes.set(boat, boatRoute); // Asocia la ruta con el barco en el mapa

      // Agregar evento de clic a la polylinea para mostrar un popup
      boatRoute.on('click', function(e) {
        L.popup()
          .setLatLng(e.latlng)
          .setContent('Aquí podemos poner por ahora información sobre la velocidad media y máxima')
          .openOn(map);
      });

  } else {
    // Removemos el marcador y la ruta correspondientes al barco deseleccionado
    const boatMarker = markers.get(boat);
    if (boatMarker) {
      map.removeLayer(boatMarker);
      markers.delete(boat);
    }

    const boatRoute = routes.get(boat);
    if (boatRoute) {
      map.removeLayer(boatRoute);
      routes.delete(boat);
    }
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
    color = '#' + Math.floor(Math.random()*16777215).toString(16);
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
}

.absolute-top-right {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100;
}

.q-btn {
  background-color: #2196f3; /* Cambia el color de fondo del botón */
  color: white; /* Cambia el color del texto del botón a blanco */
}

.small-drawer {
  width: 200px; /* Define el ancho deseado para el menú desplegable */
}

.menu-list {
  background-color: #f0f0f0; /* Fondo más oscuro para el menú */
}


.search-bar {
  display: flex;
  align-items: center;
}

input[type="text"] {
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
  flex: 1;
}


.boat-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.boat-info {
  margin-left: 10px;
}

.boat-item {
  margin-bottom: 5px; /* Espacio entre elementos */
  border-radius: 8px; /* Bordes redondeados */
  margin-left: 5px;
  margin-right: 5px;
  cursor: pointer; /* Agrega un cursor de puntero al pasar sobre el elemento */
}

.boat-item:hover {
  background-color: #e0e0e0; /* Color de fondo más claro al pasar el ratón */
}

.selected {
  background-color: #1976D2 !important;
}
</style>


