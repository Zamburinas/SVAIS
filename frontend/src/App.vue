<template>
  <router-view />
</template>

<script>
import { defineComponent } from 'vue'
import * as helpers from './helpers/helpers.js';

export default defineComponent({
  name: 'App',
  provide: {
    // Provide the helpers to be accessed by child components
    helpers
  }
})
</script>
