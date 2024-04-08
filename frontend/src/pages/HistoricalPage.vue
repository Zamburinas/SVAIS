<template>
  <q-page>
    <div id="alertBox" class="alert-box"></div>
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
let alertCount = 0;
const showAlerts = ref(false);

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

      for (let i = 1; i < coords.route.length; i++) {
        const [lat1, lon1, time1, sog1] = coords.route[i - 1];
        const [lat2, lon2, time2, sog2] = coords.route[i];

        // Calcular la distancia entre dos puntos consecutivos en kilómetros usando la fórmula de Haversine
        const distance = haversineDistance(lat1, lon1, lat2, lon2);

        // Calcular el tiempo transcurrido entre dos puntos consecutivos en horas
        const timeDiff = (new Date(time2) - new Date(time1)) / (1000 * 3600); // Diferencia de tiempo en horas

        // Calcular la velocidad en kilómetros por hora
        const speedKmh = distance / timeDiff;
        const speedKnots = speedKmh * 0.53996;
        // Comparar la velocidad calculada con el campo SOG
        if (speedKnots > sog1) {
          alertCount++;
        }
       
      }
      if(alertCount!=0){
        showAlert("Hay un total de "+alertCount+" tramos sospechosos");
      }
      

      // Create boat icon
      const boatIcon = L.icon({
        iconUrl: 'src/assets/cruise_colored-icon.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      });

              // Create and add boat marker to map
        const lastCoordsIndex = coords.route.length - 1;
        const lastCoords = coords.route[lastCoordsIndex];
        const boatMarker = L.marker([lastCoords[0], lastCoords[1]], { icon: boatIcon }).addTo(map);
        markers.set(boat, boatMarker); // Asociar el marcador con el barco en el mapa

        // Create and add boat route to map
        const routeCoords = coords.route.map(coord => [coord[0], coord[1]]); // Extraer solo las coordenadas
        const boatRoute = L.polyline(routeCoords, { color: randomColor(usedColors), weight: 5 }).addTo(map);
        routes.set(boat, boatRoute); // Asociar la ruta con el barco en el mapa

        // Add click event to boat route to show popup
        boatRoute.on('click', function (e) {
          L.popup()
            .setLatLng(e.latlng)
            .setContent('Aquí podemos poner información sobre la velocidad promedio y máxima por ahora')
            .openOn(map);
        });

        // Create markers for all points in the route except the last one
        const PointIcon = L.icon({
          iconUrl: 'src/assets/point.png',
          iconSize: [16, 16],
          iconAnchor: [8, 8],
        });
        const pointMarkersArray = [];
        for (let i = 0; i < lastCoordsIndex; i++) {
          const coord = coords.route[i];
          const marker = L.marker([coord[0], coord[1]], { icon: PointIcon }).addTo(map);
          pointMarkersArray.push(marker);
        }
        pointMarkers.set(boat, pointMarkersArray);

    } catch (error) {
      console.error('Error fetching boat route:', error);
    }
  } else {
    removeBoat(boat);
  }
}



function showAlert(message) {
  // Obtener el elemento del div de alerta
  const alertBox = document.getElementById('alertBox');

  // Establecer el mensaje de alerta en el contenido del div
  alertBox.textContent = message;

  // Mostrar el div de alerta
  alertBox.style.display = 'block';

  // Después de un tiempo, ocultar el div de alerta
  setTimeout(() => {
    alertBox.style.display = 'none';
  }, 5000); // Ocultar la alerta después de 5 segundos (5000 milisegundos)

  // Decrementar el contador de alertas y actualizar el botón
  alertCount=0;
}


function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Radio de la Tierra en kilómetros
  const dLat = (lat2 - lat1) * Math.PI / 180;  // Convertir a radianes
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c; // Distancia en kilómetros
  return distance;
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

.alert-box {
  display: none;
  position: fixed;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #f44336;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  z-index: 9999;
}



</style>
cd b