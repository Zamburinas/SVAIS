<template>
  <q-page>
    <div id="alertBox" class="alert-box"></div>
    <div id="map"></div>
  </q-page>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { inject } from 'vue';
let Areas;
let currentEllipse = null;
let currentLines = [];
let linesGroup = L.layerGroup();
let helpers = inject('helpers');
let map = null;
const randomOffsets = new Map();

async function initializeMapAndLocator() {
  if (!map) {
    let coorGoniometros = null;
    let boats = null;
    let coords = await helpers.getAllCoords();
    if (coords) {
      coorGoniometros = coords.radiogonos;
      boats = coords.boats;
    }
    Areas = await helpers.getProtectedAreas();

    map = L.map('map').setView([42.156932, -8.880105], 11);

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

    coorGoniometros.forEach((Goni, index) => {
      const marker = L.marker(Goni, { icon: antennaIcon }).addTo(map);
              var popupContent = `<div class="popup-content">
                                <span class="label">Nombre:</span> <span class="boat-name">Radiogoniometro${index + 1}</span><br>
                                <span class="label">Latitud:</span> <span class="latitude">${Goni[0]}</span><br>
                                <span class="label">Longitud:</span> <span class="longitude">${Goni[1]}</span><br>
                                <span class="label">Estado:</span> <span class="longitude">Activo</span><br>
                              </div>`;



        var popup = L.popup().setContent(popupContent);
        marker.bindPopup(popup).openPopup();
    });

    drawAreas();

    boats.forEach(boat => {


      const marker = L.marker([boat.LAT, boat.LON], { icon: boatIcon }).addTo(map);

      marker.on('click', async () => {
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
        let aux = await helpers.getBoatInfo(boat.MMSI);
        var popupContent = `<div class="popup-content">
                                <span class="label">Nombre:</span> <span class="boat-name">${aux.data.SHIPNAME}</span><br>
                                <span class="label">Tipo de Barco:</span> <span class="vessel-type">${aux.data.SHIP_TYPE}</span><br>
                                <span class="label">MMSI:</span> <span class="mmsi">${aux.data.MMSI}</span><br>
                                <span class="label">Fecha:</span> <span class="date">${aux.data.day}</span><br>
                                <span class="label">Hora:</span> <span class="time">${aux.data.hour}</span><br>
                                <span class="label">Estado:</span> <span class="status">${aux.data.STATUS}</span><br>
                                <span class="label">Latitud:</span> <span class="latitude">${aux.data.LAT}</span><br>
                                <span class="label">Longitud:</span> <span class="longitude">${aux.data.LON}</span><br>
                              </div>`;



        var popup = L.popup().setContent(popupContent);
        marker.bindPopup(popup).openPopup();
        if (!randomOffsets.has(boat.MMSI)) {
          // Generar un valor de desplazamiento aleatorio
          const randomLatOffset = (Math.random() * (0.005 - (-0.005)) + (-0.005)).toFixed(6);
          const randomLngOffset = (Math.random() * (0.005 - (-0.005)) + (-0.005)).toFixed(6);
          randomOffsets.set(boat.MMSI, [parseFloat(randomLatOffset), parseFloat(randomLngOffset)]);
        }
        const randomOffset = randomOffsets.get(boat.MMSI);
        const center = [boat.LAT + randomOffset[0], boat.LON + randomOffset[1]];
        await drawLinesWithAnimation(map, center, coorGoniometros.map(antenna => antenna));
        let semiMajorAxis = 113.5624900059602;
        let semiMinorAxis = 127.04089357908843;
        let angle = -135.35846661098765; 
        drawEllipse(map, [boat.LAT, boat.LON], center, semiMajorAxis, semiMinorAxis, angle);
  
      });
    });

    map.on('click', () => {
      if (currentEllipse) {
        currentEllipse.remove();
        currentEllipse = null;
        linesGroup.clearLayers();
      }
    });

  } else {
    map.eachLayer(layer => {
      map.removeLayer(layer);
    });
  }



  function drawEllipse(map, boat, center, semiMajorAxis, semiMinorAxis, angle) {
    var angle = angle * Math.PI / 180;
    var numSegments = 400;
    var points = [];
    var angleOffset = 2 * Math.PI / numSegments;

    for (var i = 0; i < numSegments; i++) {
      var angleRad = i * angleOffset;
      var x = center[0] + (0.0001) * semiMajorAxis * Math.cos(angleRad) * Math.cos(angle) - (0.0001) * semiMinorAxis * Math.sin(angleRad) * Math.sin(angle);
      var y = center[1] + (0.0001) * semiMajorAxis * Math.cos(angleRad) * Math.sin(angle) + (0.0001) * semiMinorAxis * Math.sin(angleRad) * Math.cos(angle);
      points.push([x, y]);
    }
    const q = isInsideEllipse(boat, center, semiMajorAxis, semiMinorAxis, angle);
    const fillColor = q ? '#00FF00' : '#FF0000';
    if (!q) {
      helpers.pushNotification('negative', 'Este barco no está en la posición que reporta');
      
    } else {
      helpers.pushNotification('positive', 'Este barco está en la posición que reporta');
    }

    currentEllipse = L.polygon(points, {
      color: 'dark',
      fillColor: fillColor,
      fillOpacity: 0.4,
      interactive: false
    }).addTo(map);
  }

  function isInsideEllipse(point, center, semiMajorAxis, semiMinorAxis, angle) {
    const dx = point[0] - center[0];
    const dy = point[1] - center[1];
    const angleRad = angle * Math.PI / 180;
    const cosAngle = Math.cos(angleRad);
    const sinAngle = Math.sin(angleRad);
    const rotatedDx = cosAngle * dx - sinAngle * dy;
    const rotatedDy = sinAngle * dx + cosAngle * dy;

    return (rotatedDx * rotatedDx) / (semiMajorAxis * (0.0001) * semiMajorAxis * (0.0001)) + (rotatedDy * rotatedDy) / (semiMinorAxis * (0.0001) * semiMinorAxis * (0.0001)) <= 1;
  }



  function drawLinesWithAnimation(map, boatCoordinates, antennaCoordinates) {
  antennaCoordinates.forEach(antennaCoord => {
    const latlngs = [antennaCoord, boatCoordinates];
    const line = L.polyline(latlngs, { color: '#444', dashArray: '10, 10', weight: 1 });

    const steps = 100;
    const deltaLat = (boatCoordinates[0] - antennaCoord[0]) / steps;
    const deltaLng = (boatCoordinates[1] - antennaCoord[1]) / steps;

    const interpolatedCoords = [];
    let currentLatlng = [antennaCoord[0], antennaCoord[1]];

    for (let step = 0; step <= steps; step++) {
      interpolatedCoords.push([currentLatlng[0], currentLatlng[1]]);
      currentLatlng[0] += deltaLat;
      currentLatlng[1] += deltaLng;
    }

    line.setLatLngs(interpolatedCoords);
    line.addTo(linesGroup);
  });

  linesGroup.addTo(map);
}
}

function drawAreas() {
  Areas.forEach(area => {
    const coordinates = area.coordinates[0].map(coord => [coord[0], coord[1]]);
    const polygon = L.polygon(coordinates, { color: 'red' }).addTo(map);

    polygon.on('click', function (e) {
      L.popup()
        .setLatLng(e.latlng)
        .setContent(area.name)
        .openOn(map);
    });
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

.popup-content {
  max-width: 200px;
  /* Ancho máximo del popup */
  padding: 10px;
  /* Espaciado interior del popup */
  background-color: #ffffff;
  /* Color de fondo del popup */
  border: 1px solid #ccc;
  /* Borde del popup */
  border-radius: 5px;
  /* Radio de borde del popup */
  font-family: Arial, sans-serif;
  /* Fuente del texto del popup */
  font-size: 14px;
  /* Tamaño de fuente del texto del popup */
}

.boat-name {
  font-weight: bold;
  /* Texto en negrita */
  font-size: 16px;
  /* Tamaño de fuente más grande */
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
