<template>
    <div>
      <!-- Menú de opciones -->
      <div v-if="showMenu">
        <h2 class="menu-title">Available Boats:</h2>
        <div class="options-container">
          <div class="option" v-for="(option, index) in options" :key="index" @click="selectOption(option)">
            <img src="../assets/cruise_colored-icon.png" alt="Imagen del barco" class="option-image" />
            <div class="option-details">
              <!-- Aquí puedes agregar más datos sobre el barco -->
              <h3>{{ option.name }}</h3>
              <p>{{ option.description }}</p>
              <!-- Puedes agregar más contenido aquí según sea necesario -->
            </div>
          </div>
        </div>
      </div>
  
      <!-- Contenido principal -->
      <div v-else>
        <div>
        <button @click="goBack" class="back-button">Back</button>
      </div>
      <div id="map"></div>
      </div>
    </div>
  </template>
  
  <script>
import { ref, onMounted } from 'vue'

  export default {
    data() {
      return {
        options: [
          { name: 'aaaaaaaaaaaa', description: 'Descripción del Barco 1' },
          { name: 'bbbbbbbbbbbb', description: 'Descripción del Barco 2' },
          { name: 'ccccccccccccc', description: 'Descripción del Barco 3' },
          { name: 'dddddddddddd', description: 'Descripción del Barco 4' }
        ], // Opciones del menú
        content: '', // Contenido que se muestra al hacer clic en una opción
        showMenu: true // Controla si se muestra el menú o el contenido principal
      };
    },
    methods: {
      selectOption(option) {
        this.showMenu = false;

        const map = L.map('map').setView([43.6728903,-7.8391903], 14); // Configura el centro del mapa con las coordenadas del barco seleccionado

        L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        id: "streets-v12",
        accessToken: "pk.eyJ1IjoiYm9id2F0Y2hlcngiLCJhIjoiY2xiMGwwZThrMWg3aTNwcW1mOGRucHh6bSJ9.kNHlmRqkRSxYNeipcKkJhw",
        }).addTo(map);

      },
      goBack() {

      this.showMenu = true;
    }
    }
  };
  </script>
  
  <style>
  /* Estilos para mejorar la apariencia del menú y del contenido */
  
  .menu-title {
    font-size: 2rem; /* Tamaño del título más grande */
    margin-left: 1.5%;
  }
  
  .options-container {
    display: flex;
    flex-wrap: wrap;
  }
  
  .option {
    cursor: pointer;
    background-color: #f0f0f0;
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 20px;
    margin-right: 20px;
    margin-bottom: 20px;
    width: 30%; /* Ancho deseado para cada opción */
    transition: background-color 0.3s ease;
    display: flex;
    align-items: center;
    margin-left: 1.5%; /* Añade margen a la izquierda */
  }
  
  .option:hover {
    background-color: #e0e0e0;
  }
  
  .option-image {
    width: 100px; /* Ancho de la imagen */
    height: auto; /* Altura automática para mantener la proporción */
    margin-right: 20px;
  }
  .back-button {
  margin-bottom: 10px;
  background-color: #1976D2; /* Fondo azul */
  color: #ffffff; /* Letras blancas */
  border: none;
  border-radius: 5px;
  padding: 0.5% 1%;
  font-size: 1.2rem; /* Tamaño de letra más grande */
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 1%;
  margin-left: 1%;
}

.back-button:hover {
  background-color: #0056b3; /* Cambio de color al pasar el ratón */
}
  .option-details {
    
    flex: 1;
  }
  
  </style>
  
