<template>
    <q-page>
      <q-btn :label="buttonLabel" @click="marcarDesmarcar" class="marcar">
    </q-btn>
      <div id="alertBox" class="alert-box"></div>
      <div id="map"></div>

      
    </q-page>
  </template>
  
  <script setup>
  import { onMounted, ref } from 'vue';
  import L from 'leaflet';
  import 'leaflet/dist/leaflet.css';
  import { inject } from 'vue';
  // let selectedOption = ref('Nombre');
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
  let marcado= true;
let buttonLabel = ref('Ocultar Marcadores');
  const puntosIntermedios = [
  [42.236324, -8.737408],
  [42.239348999999995, -8.751727100000001],
  [42.242374, -8.7660462],
  [42.245399, -8.7803653],
  [42.248424, -8.7946844],
  [42.251448999999996, -8.809003500000001],
  [42.254473999999996, -8.8233226],
  [42.257499, -8.8376417],
  [42.260524, -8.8519608],
  [42.263548999999996, -8.8662799]
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
    map = L.map('map').setView([37.0902, -95.7129], 4);
  
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
      name: coord.VesselName,
      photo: "src/assets/cruise_colored-icon.png",
      checked: false
    }));
    filteredBoats.value = boats.value;
    handleBoatSelection(coords.filter(coord => coord.MMSI === 246506000)[0]);
  }
  
  function marcarDesmarcar(){
  buttonLabel.value = !marcado ? 'Ocultar Marcadores' : 'Mostrar Marcadores';
  if(marcado){
    
    pointMarkers.forEach(markers => {
      markers.forEach(marker => {
        map.removeLayer(marker); // Quitar el marcador del mapa
      });
    });
  }else{
    
    pointMarkers.forEach(markers => {
      markers.forEach(marker => {
        marker.addTo(map); // Añadir el marcador al mapa
      });
    });
  }
  marcado= !marcado

}
  
  
  async function handleBoatSelection(boat) {
      try {
        const response = await helpers.getBoatRoute({ "MMSI": boat.MMSI});
        
        let alertCount = 0; // Contador de alertas
  
        const routeSegments = []; // Almacenar segmentos de la ruta con problemas
  
        let lastCoords; // Últimas coordenadas de la última ruta
        let pointMarkersArray = [];
        let routesArray=[];
        response.forEach((routeData,index) => {
          let routeColor = randomColor(usedColors);
          for (let i = 1; i < routeData.route.length; i++) {
            const [lat1, lon1, time1, sog1] = routeData.route[i - 1];
            const [lat2, lon2, time2, sog2] = routeData.route[i];
            
            const speedKnots=calcularDistancia(lat1, lon1, lat2, lon2,time1,time2);
  
  
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
          const boatRoute = L.polyline(primerosDosElementos, { color: routeColor, weight: 3 }).addTo(map);
          routesArray.push(boatRoute);
          
  
          // Agregar evento de clic a la ruta del barco para mostrar un popup
          boatRoute.on('click', function (e) {
            L.popup()
              .setLatLng(e.latlng)
              .setContent('Aquí podemos poner información sobre la velocidad promedio y máxima por ahora')
              .openOn(map);
          });
  
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
  
  
          let indexPoint=0;
          if(index==response.lenth){
            indexPoint=routeData.route.length -1
          }else{
            indexPoint=routeData.route.length
          }
  
          
          for (let i = 0; i <indexPoint ; i++) {
            const coord = routeData.route[i];
            const marker = L.marker([coord[0], coord[1]], { icon: PointIcon }).addTo(map);
            pointMarkersArray.push(marker);
          }
          
        });
        routes.set(boat,routesArray);
        pointMarkers.set(boat, pointMarkersArray);
  
        if (alertCount !== 0) {
        helpers.pushNotification('negative', 'Este barco no está en la posición que reporta');
        
      } else {
        helpers.pushNotification('positive', 'Este barco está en la posición que reporta');
      }
  
  
        // Colocar el icono del barco en el último punto de la última ruta
        if (lastCoords) {
          map.setView([lastCoords[0], lastCoords[1]], 8)
          const boatMarker = L.marker([lastCoords[0], lastCoords[1]], { icon: boatIcon }).addTo(map);
          markers.set(boat, boatMarker); // Asociar el marcador con el barco en el mapa
        }
  
      } catch (error) {
        console.error('Error fetching boat route:', error);
      }
}
  
  
  function calcularDistancia(lat1, lon1, lat2, lon2,time1,time2){
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
    // if (selectedOption.value=='Name'){
    //   const option= "VesselName";
    // }else{
    //   const option= selectedOption.value.value
    // }
    
  
    // // Filtrar los barcos que coincidan con la consulta de búsqueda
    // let prueba= await helpers.getBoats({option:searchQuery.toLowerCase()});
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
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    z-index: 9999;
  }
  
  .marcar{
  position:absolute;
  z-index:999;
  top: 1vh;
  margin-left: 50px;
  background-color: #1976D2;
  color: white;
}
  
  </style>
