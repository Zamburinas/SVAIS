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
          <!-- Agregar el q-select con las opciones desplegables -->
          <q-select v-model="selectedOption" :options="selectOptions">
          </q-select>
        </div>
        <q-virtual-scroll :items="filteredBoats" item-height="50">
          <template v-slot="{ item }">
            <q-item clickable v-ripple :class="{ 'selected': item.checked }" @click="toggleBoat(item)">
              <q-item-section>
                <label :for="'boat_checkbox_' + item.index" class="boat-checkbox">
                  <img :src="item.photo" style="width: 32px; height: 32px; border-radius: 50%;">
                  <span>{{ item.name }} : {{ item.MMSI }}</span>
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
let selectedOption = ref('Name');
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

const selectOptions = [
  { label: 'Nombre', value: 'SHIPNAME' },
  { label: 'MMSI', value: 'MMSI' },
  { label: 'Tipo de Barco', value: 'SHIP_TYPE' },
  { label: 'Estado', value: 'STATUS' }
];

const PointIcon = L.icon({
  iconUrl: 'src/assets/point.png',
  iconSize: [12, 12],
  iconAnchor: [8, 8],
});

const boatIcon = L.icon({
  iconUrl: 'src/assets/cruise_colored-icon.png',
  iconSize: [32, 32],
  iconAnchor: [16, 16],
});



async function initializeMapAndLocator() {
  map = L.map('map').setView([42.156932, -8.880105], 11);

  L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    id: 'streets-v12',
    accessToken: 'pk.eyJ1IjoiYm9id2F0Y2hlcngiLCJhIjoiY2xiMGwwZThrMWg3aTNwcW1mOGRucHh6bSJ9.kNHlmRqkRSxYNeipcKkJhw',
  }).addTo(map);

  let coords = JSON.parse(await helpers.getBoatNames());
  // Asignar los datos de los barcos a la variable boats
  boats.value = coords.map(coord => ({
    MMSI: coord.MMSI,
    name: coord.SHIPNAME,
    photo: "src/assets/cruise_colored-icon.png",
    checked: false
  }));
  filteredBoats.value = boats.value;
}




async function handleBoatSelection(boat) {
  if (boat.checked) {
    try {
      const response = await helpers.getBoatRoute({ "MMSI": boat.MMSI });

      let alertCount = 0; // Contador de alertas

      const routeSegments = []; // Almacenar segmentos de la ruta con problemas

      let lastCoords; // Últimas coordenadas de la última ruta
      let pointMarkersArray = [];
      let routesArray = [];
      response.forEach((routeData, index) => {
        let routeColor = randomColor(usedColors);
        for (let i = 1; i < routeData.route.length; i++) {
          const [lat1, lon1, time1, sog1] = routeData.route[i - 1];
          const [lat2, lon2, time2, sog2] = routeData.route[i];

          const speedKnots = calcularDistancia(lat1, lon1, lat2, lon2, time1, time2);


          if (speedKnots > sog2 * 2) {
            alertCount++;
            routeSegments.push([lat1, lon1, lat2, lon2]); // Almacenar segmento sospechoso
          }
        }

        let primerosDosElementos = [];
        routeData.route.forEach(array => {
          // Obtener los dos primeros elementos y agregarlos al nuevo array
          primerosDosElementos.push(array.slice(0, 2));
        });

        // Crear y agregar ruta del barco al mapa
        const boatRoute = L.polyline(primerosDosElementos, { color: routeColor, weight: 5 }).addTo(map);
        routesArray.push(boatRoute);


        if (index === response.length - 1) {
          // Si es la última ruta, obtener las últimas coordenadas
          lastCoords = routeData.route[routeData.route.length - 1];
        }


        if (routeSegments.length > 0) {
          // Si hay segmentos sospechosos, cambiar su color a rojo y marcarlos en el mapa
          routeSegments.forEach(segment => {
            const [lat1, lon1, lat2, lon2] = segment;
            const redRouteSegment = L.polyline([[lat1, lon1], [lat2, lon2]], { color: '#FF0000', weight: 5 }).addTo(map);
            routesArray.push(redRouteSegment);

          });
        }


        let indexPoint = 0;
        if (index == response.lenth) {
          indexPoint = routeData.route.length - 1
        } else {
          indexPoint = routeData.route.length
        }


        for (let i = 0; i < indexPoint; i++) {
          const coord = routeData.route[i];
          const marker = L.marker([coord[0], coord[1]], { icon: PointIcon }).addTo(map);
          marker.on('click', async () => {
            let aux = await helpers.getBoatInfo(boat.MMSI);
            var popupContent = `<div class="popup-content">
                                <span class="label">MMSI:</span> <span class="mmsi">${boat.MMSI}</span><br>
                                <span class="label">Hora:</span> <span class="time">${coord[2]}</span><br>
                                <span class="label">Latitud:</span> <span class="latitude">${coord[0]}</span><br>
                                <span class="label">Longitud:</span> <span class="longitude">${coord[1]}</span><br>
                              </div>`;

            var popup = L.popup().setContent(popupContent);
            marker.bindPopup(popup).openPopup();
          });
          pointMarkersArray.push(marker);
        }

      });
      routes.set(boat, routesArray);
      pointMarkers.set(boat, pointMarkersArray);
      if (alertCount !== 0) {
        helpers.pushNotification('negative', 'Hay un total de '+alertCount+' tramos sospechosos');
        alertCount=0;
      } else {
        helpers.pushNotification('positive', 'Ruta correcta');
      }

      // Colocar el icono del barco en el último punto de la última ruta
      if (lastCoords) {
        const boatMarker = L.marker([lastCoords[0], lastCoords[1]], { icon: boatIcon }).addTo(map);
        boatMarker.on('click', async () => {
          let aux = await helpers.getBoatInfo(boat.MMSI);
          var popupContent = `<div class="popup-content">
                                <span class="label">Nombre:</span> <span class="boat-name">${aux.data.SHIPNAME}</span><br>
                                <span class="label">Tipo de Barco:</span> <span class="vessel-type">${aux.data.SHIP_TYPE}</span><br>
                                <span class="label">MMSI:</span> <span class="mmsi">${aux.data.MMSI}</span><br>
                                <span class="label">Fecha:</span> <span class="date">${aux.data.day}</span><br>
                                <span class="label">Hora:</span> <span class="time">${aux.data.hour}</span><br>
                                <span class="label">Estado:</span> <span class="status">${aux.data.STATUS}</span><br>
                                <span class="label">Latitud:</span> <span class="latitude">${lastCoords[0]}</span><br>
                                <span class="label">Longitud:</span> <span class="longitude">${lastCoords[1]}</span><br>
                              </div>`;



          var popup = L.popup().setContent(popupContent);
          boatMarker.bindPopup(popup).openPopup();
        });
        markers.set(boat, boatMarker); // Asociar el marcador con el barco en el mapa
      }

    } catch (error) {
      console.error('Error fetching boat route:', error);
    }
  } else {
    removeBoat(boat);
  }
}


function calcularDistancia(lat1, lon1, lat2, lon2, time1, time2) {
  const distance = haversineDistance(lat1, lon1, lat2, lon2);
  const timeDiff = (new Date(time2) - new Date(time1)) / (1000 * 3600);
  const speedKmh = distance / timeDiff;
  const speedKnots = speedKmh * 0.53996;
  return speedKnots;
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
  removeRoutes(boat);

  removePointMarkers(boat);

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

function removePointMarkers(boat) {
  const pointMarkersArray = pointMarkers.get(boat);
  if (pointMarkersArray && pointMarkersArray.length > 0) {
    pointMarkersArray.forEach(marker => {
      map.removeLayer(marker);
    });
    pointMarkers.set(boat, []);
  }

}

function removeRoutes(boat) {
  const routeArray = routes.get(boat);
  if (routeArray && routeArray.length > 0) {
    routeArray.forEach(marker => {
      map.removeLayer(marker);
    });
    routes.set(boat, []);
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
  } while (usedColors.has(color) || color.startsWith('#FF'));
  return color;
}

async function search() {
  let option = 'as';
  if (selectedOption.value == 'Name') {
    option = "SHIPNAME";
  } else {
    option = selectedOption.value.value
  }


  // Filtrar los barcos que coincidan con la consulta de búsqueda
  let prueba = null;
  let filter = { [option]: searchQuery };
  if (searchQuery != '') prueba = await helpers.getBoats(filter);
  else prueba = await helpers.getBoatNames();
  filteredBoats.value = boats.value.filter(boat => {
    return prueba.includes(boat.name);
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
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  z-index: 9999;
}
</style>