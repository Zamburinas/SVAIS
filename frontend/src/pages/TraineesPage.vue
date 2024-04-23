<template>
  <q-page class="q-pa-md">
    <div class="q-gutter-md">
      <div
        v-for="box in boxes"
        :key="box.id"
        class="box"
        :class="{ 'hovered': hover === box.id }"
        @mouseover="hover = box.id"
        @mouseleave="hover = null"
        @click="handleClick(box)"
      >
        <div class="content">
          <h5 class="title">{{ box.title }}</h5>
          <img :src="box.image" alt="Image" class="box-image">
        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
export default {
  data() {
    return {
      hover: null,
      boxes: [
        { id: 1, title: 'Posición y comprobación de posición correcta de un barco', description: 'Description 1', image: 'src/assets/CorrectBoat.png', page: 'CorrectBoatPage' },
        { id: 2, title: 'Posición y comprobación de posición incorrecta de un barco', description: 'Description 2', image: 'src/assets/IncorrectBoat.png', page: 'IncorrectBoatPage' },
        { id: 3, title: 'Ruta de un barco correcta', description: 'Description 3', image: 'src/assets/CorrectRoute.png', page: 'CorrectRoutePage' },
        { id: 4, title: 'Ruta de un barco incorrecta', description: 'Description 4', image: 'src/assets/IncorrectRoute.png', page: 'IncorrectRoutePage' }
      ]
    }
  },
  methods: {
    handleClick(box) {
      this.$router.push({ name: box.page });
    }
  }
}
</script>

<style scoped>
.box {
  width: 47%; /* Dos columnas en ordenador */
  height: auto;
  background-color: #f8f8f8; /* Color gris claro */
  border: 1px solid #ccc;
  border-radius: 8px; /* Borde redondeado */
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1); /* Sombra */
  transition: all 0.3s ease;
  cursor: pointer;
  display: inline-block;
  box-sizing: border-box;
  padding: 10px;
  margin: 10px 1% 20px 2%; /* Añadido margen: arriba-derecha-abajo-izquierda */
}

.box:hover {
  background-color: #e0e0e0; /* Un poco más oscuro al pasar el ratón */
  transform: scale(1.05); /* Escalar un poco al pasar el ratón */
}

.box.hovered {
  background-color: #c0c0c0; /* Más oscuro cuando está siendo "hovered" */
}

.content {
  text-align: center;
}

.box-image {
  max-width: 100%;
  height: 220px;
}
.q-gutter-md {
  margin-top: 2%;
  margin-left: 1%;
}

/* Cuatro filas en móvil */
@media screen and (max-width: 600px) {
  .box {
    width: 96% !important; /* Una columna en móvil */
    margin-bottom: 10px; /* Espacio entre las cajas */
  }
}
</style>
