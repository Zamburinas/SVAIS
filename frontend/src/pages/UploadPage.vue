<template>
  <div>
    <input type="file" @change="handleFileUpload">
    <button @click="submitForm" :disabled="!file">Enviar</button>
    <div v-if="json">
      <h2>Contenido del JSON</h2>
      <pre>{{ json }}</pre>
      <a :href="jsonDownloadLink" download="data.json">Descargar JSON</a>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import { inject } from 'vue';

let json=false;



</script>
