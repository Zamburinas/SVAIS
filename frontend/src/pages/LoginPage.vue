<template>
  <q-page class="flex flex-center bg-grey-2">
    <q-card class="q-pa-md shadow-2 my_card" bordered @keyup.enter="login()">
      <q-card-section class="text-center">
        <div class="text-blue-9 text-h5 text-weight-bold">Iniciar Sesión</div>
        <div class="text-grey-8">Inicia sesión para acceder a tu cuenta</div>
      </q-card-section>
      <q-card-section>
        <q-input dense outlined color="primary" v-model="email" label="Correo Electrónico">
        </q-input>
        <q-input dense outlined class="q-mt-md" v-model="password" type="password" label="Contraseña">
        </q-input>
        <q-img v-if="this.tfa" :src="this.capturedImage" alt="Captured Image"
          style="margin-top: 5%; max-width: 100%; border: 1px solid blue; border-radius: 5px;" />
      </q-card-section>
      <q-card-section style="display: flex; gap: 5%">
        <q-btn v-if="this.tfa" label="Capture" @click="captureImage" style="
          border-radius: 8px;" color="primary" rounded size="md" no-caps class="full-width" />
        <q-btn style="
          border-radius: 8px;" color="blue" rounded size="md" label="Sign in" no-caps class="full-width"
          @click="login()">
        </q-btn>
      </q-card-section>
      <q-card-section class="text-center q-pt-none">
        <div class="text-blue-8">¿Aún no tienes cuenta?
          <a class="text-blue text-weight-bold" style="text-decoration: none; cursor: pointer;"
            @click="this.$router.push({ name: 'register' })">
            Registrar.
          </a>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script>
import { SessionStorage } from 'quasar';
import { inject, ref } from 'vue';

export default {
  data: () => {
    return {
      email: "",
      password: "",
      helpers: inject('helpers'),
      tfa: ref(false),
      capturedImage: ref('')
    };
  },
  created() {
    window.addEventListener('tfa', (event) => {
      let sessionRequired = SessionStorage.getItem('required');
      sessionRequired = sessionRequired.tfa;
      this.tfa = sessionRequired;
    });
  },
  methods: {
    async login() {
      if (!this.validateEmail()) {
        return;
      }
      let loginRedirect = await this.helpers.login(this.email, this.password, this.capturedImage);
      if (loginRedirect) {
        this.$router.push({ name: 'map' });
      }
    },
    validateEmail() {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(this.email)) {
        this.helpers.pushNotification('negative', 'Invalid email address');
        return false;
      }
      return true;
    },
    async captureImage() {
      this.capturedImage = await this.helpers.takePhoto();
    }
  },
};
</script>

<style>
.my_card {
  width: 25rem;
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
}
</style>
