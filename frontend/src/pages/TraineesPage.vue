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
          <h4 class="title">{{ box.title }}</h4>
          <img :src="box.image" alt="Image" style="width: 250px; height: 230px; margin-bottom:2%">
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
  width: 45%;
  height: 50%;
  background-color: #f0f0f0; /* Color gris muy claro */
  border: 1px solid #ccc;
  transition: all 0.3s ease;
  cursor: pointer;
  display: inline-block;
  margin: 10px;
}

.box:hover {
  background-color: #d0d0d0; /* Un poco más oscuro al pasar el ratón */
  transform: scale(1.05);
}

.box.hovered {
  background-color: #c0c0c0; /* Más oscuro cuando está siendo "hovered" */
}

.content {
  text-align: center;
}
.q-gutter-md {
  margin-top: 2%;
  margin-left: 2%;
  align-items: center;
}
</style>
