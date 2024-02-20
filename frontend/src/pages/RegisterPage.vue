<template>
  <q-page class="flex flex-center bg-grey-2">
    <q-card 
      class="q-pa-md shadow-2 my_card" 
      bordered
      @keyup.enter="register()">
      <q-card-section class="text-center">
        <div class="text-blue-9 text-h5 text-weight-bold">Sign up</div>
        <div class="text-grey-8">Create an account below</div>
      </q-card-section>
      <q-card-section>
        <q-input 
          dense 
          outlined 
          required
          color = "primary"
          v-model = "email" 
          @blur="validateEmail"
          label = "Email Address">
        </q-input>
        <q-input 
          dense 
          outlined 
          class = "q-mt-md" 
          v-model = "password" 
          type = "password" 
          label = "Password">
        </q-input>
        <q-input 
          dense 
          outlined 
          class = "q-mt-md" 
          v-model = "repeatPassword" 
          type = "password" 
          label = "Repeat Password">
        </q-input>
        <q-input 
          dense 
          outlined 
          class = "q-mt-md" 
          color = "primary"
          v-model = "name" 
          label = "Name">
        </q-input>
        <q-input 
          dense 
          outlined 
          class = "q-mt-md" 
          color = "primary"
          v-model = "lastName" 
          label = "Last Name">
        </q-input>
        <q-input 
          dense 
          outlined 
          class = "q-mt-md" 
          color = "primary"
          v-model = "organization" 
          label = "Organization">
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
        <div class="text-blue-8">Already have an account?
          <a 
            class="text-blue text-weight-bold" 
            style="text-decoration: none; cursor: pointer;"
            @click="this.$router.push({ name: 'login' })"
            >
            Sign in.
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
