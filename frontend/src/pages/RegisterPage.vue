<template>
  <q-page class="flex flex-center bg-grey-2">
    <q-card 
      class="q-pa-md shadow-2 my_card" 
      bordered
      @keyup.enter="register()">
      <q-card-section class="text-center">
        <div class="text-blue-9 text-h5 text-weight-bold">Registrarse</div>
        <div class="text-grey-8">Crea una cuenta más abajo.</div>
      </q-card-section>
      <q-card-section>
        <q-input 
          dense 
          outlined 
          required
          color = "primary"
          v-model = "email" 
          label = "Correo electrónico">
        </q-input>
        <q-input 
          dense 
          outlined 
          class = "q-mt-md" 
          v-model = "password" 
          type = "password" 
          label = "Contraseña">
        </q-input>
        <q-input 
          dense 
          outlined 
          class = "q-mt-md" 
          v-model = "repeatPassword" 
          type = "password" 
          label = "Repite Contraseña">
        </q-input>
        <q-input 
          dense 
          outlined 
          class = "q-mt-md" 
          color = "primary"
          v-model = "name" 
          label = "Nombre">
        </q-input>
        <q-input 
          dense 
          outlined 
          class = "q-mt-md" 
          color = "primary"
          v-model = "lastName" 
          label = "Apellidos">
        </q-input>
        <q-input 
          dense 
          outlined 
          class = "q-mt-md" 
          color = "primary"
          v-model = "organization" 
          label = "Organización">
        </q-input>
      </q-card-section>
      <q-card-section>
        <q-btn style="
          border-radius: 8px;" 
          color = "blue" 
          rounded size="md" 
          label = "Sign in" 
          no-caps 
          class = "full-width"
          @click="register()">
      </q-btn>
      </q-card-section>
      <q-card-section class="text-center q-pt-none">
        <div class="text-blue-8">¿Ya tienes una cuenta?
          <a 
            class="text-blue text-weight-bold" 
            style="text-decoration: none; cursor: pointer;"
            @click="this.$router.push({ name: 'login' })"
            >
            Iniciar Sesión.
          </a>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script>
import { inject } from 'vue';

export default {
  data: () => {
    return {
      email: "",
      password: "",
      name: "",
      lastName: "",
      repeatPassword: "",
      organization: "",
      helpers: inject('helpers')
    };
  },
  methods: {
    async register() {
      if (this.password !== this.repeatPassword) {
        this.helpers.pushNotification('negative', 'Passwords do not match');
        return;
      }
      if (!this.validateEmail()) {
        return;
      } 
      let registerRedirect = await this.helpers.register({
        email: this.email,
        password: this.password,
        name: this.name,
        lastName: this.lastName,
        repeatPassword: this.repeatPassword,
        organization: this.organization
      });
      if (registerRedirect) {
        this.$router.push({ name: 'login' });
      }
    },
    validateEmail() {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(this.email)) {
        this.helpers.pushNotification('negative', 'Invalid email address');
        return false;
      }
      return true;
    }
  }
};
</script>

<style>
.my_card {
  width: 25rem;
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
}
</style>
