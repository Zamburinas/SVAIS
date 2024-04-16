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
        @click="handleClick(box.id)"
      >
        <div class="content">
          <h4 class="title">{{ box.title }}</h4>
          <p>{{ box.description }}</p>
          <img :src="box.image" alt="Image">
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
        { id: 1, title: 'Posición y comprobarción de posición correcta de un barco', description: 'Description 1', image: 'https://via.placeholder.com/150' },
        { id: 2, title: 'Posición y comprobarción de posición incorrecta de un barco', description: 'Description 2', image: 'https://via.placeholder.com/150' },
        { id: 3, title: 'Ruta de un barco correcta', description: 'Description 3', image: 'https://via.placeholder.com/150' },
        { id: 4, title: 'Ruta de un barco incorrecta', description: 'Description 4', image: 'https://via.placeholder.com/150' }
      ]
    }
  },
  methods: {
    handleClick(boxId) {
      alert(`Box ${boxId} clicked!`);
    }
  }
}
</script>

<style scoped>
.box {
  width: 45%;
  height: 50%;
  background-color: lightblue;
  border: 1px solid #ccc;
  transition: all 0.3s ease;
  cursor: pointer;
  display: inline-block;
  margin: 10px;
}

.box:hover {
  background-color: blue;
  transform: scale(1.1);
}

.box.hovered {
  background-color: darkblue;
}

.content {
  text-align: center;
}
.q-gutter-md{
  margin-top:2%;
  margin-left:2%;
  align-items: center;
}
</style>
