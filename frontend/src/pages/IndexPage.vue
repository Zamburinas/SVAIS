<template>
  <q-page>
   <div id="map"></div>
  </q-page>
</template>

<script setup>
  import {ref,onMounted} from 'vue'
  import L from 'leaflet'
  import 'leaflet/dist/leaflet.css'

  function initializeMapAndLocator(){
    
    var coordinate = [42.242306, -8.730914]
    const boatIcon = L.icon({
      iconUrl: 'src/assets/cruise_colored-icon.png',
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    });

    var map = L.map('map')
              .setView(coordinate, 14);

    L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
      maxZoom: 19,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      id: "streets-v12",
      accessToken:"pk.eyJ1IjoiYm9id2F0Y2hlcngiLCJhIjoiY2xiMGwwZThrMWg3aTNwcW1mOGRucHh6bSJ9.kNHlmRqkRSxYNeipcKkJhw",
    }).addTo(map);
 
    L.marker(coordinate, 
    { 
      icon: boatIcon 
    })
    .addTo(map)
    .bindPopup("Latitude: " + coordinate[0] + "Longitude: " + coordinate[0]);
 
  }
 
  onMounted(()=>{
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