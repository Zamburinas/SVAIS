<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          SVAIS
        </q-toolbar-title>
        <div v-if=isAuthenticated>
          <q-btn flat color="primary">
            <q-avatar style="background-color: #eee;">
              <q-icon name="person" color="primary" size="sm" />
            </q-avatar>
            <q-menu>
              <div class="row no-wrap q-pa-md">
                <div class="column">
                  <div class="text-h6 q-mb-md">Settings</div>
                  <q-toggle v-model="userData.two_factor_auth" label="Two Factor Authentication"
                    @update:model-value="toggleChanged" />
                </div>

                <q-separator vertical inset class="q-mx-lg" />

                <div class="column items-center">
                  <div class="text-subtitle1 q-mt-md q-mb-xs">{{ userData.name }}</div>
                  <div class="text-caption">{{ userData.email }}</div> <!-- Email -->
                  <div class="text-caption">{{ userData.organization }}</div> <!-- Organization -->
                  <q-btn color="primary" label="Logout" push size="sm" v-close-popup @click="navigate('logout')" />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>

      </q-toolbar>
    </q-header>

    <div>
      <q-dialog v-model="showDialog">
        <q-card @keyup.enter="confirmPhoto()">
          <q-card-section v-if="capturedImage">
            <q-img :src="capturedImage" alt="Captured Image" style="width: 20vw; height: 100%;
          box-shadow: rgba(0, 0, 0, 0.25) 0px 14px 28px, rgba(0, 0, 0, 0.22) 0px 10px 10px; border-radius: 5px" />
            <!-- <q-input v-model="password" label="Password" type="password" /> -->
            <q-input dense outlined class="q-mt-md" v-model="password" type="password" label="Password">
            </q-input>
          </q-card-section>
          <q-card-actions align="center">
            <!-- Capture and confirm buttons -->
            <q-btn label="Capture" color="primary" @click="captureImage" />
            <q-btn v-if="capturedImage" label="Confirm" color="green" @click="confirmPhoto" class="confirm-button" />
            <q-btn label="Cancel" color="negative" @click="closePopup" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>

    <q-dialog v-model="showAlert">
      <q-card>
        <q-card-section class="text-center">
          <div class="q-pa-md">
            <div class="text-h6">Are you sure you want to disable two-factor authentication?</div>
          </div>
          <q-input dense outlined class="q-mt-md" v-model="password" type="password" label="Password">
          </q-input>
        </q-card-section>
        <q-card-actions align="center">
          <q-btn label="Cancel" color="primary" @click="closePopup" />
          <q-btn label="Disable" color="negative" @click="disableTwoFactorAuth()" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-drawer v-model="leftDrawerOpen" side="left" show-if-above bordered>
      <q-list>
        <q-item-label header>

        </q-item-label>

        <q-item v-for="link in essentialLinks" :key="link.title" clickable @click="navigate(link.page)">
          <q-item-section avatar>
            <q-item-label>
              <q-icon :name="link.icon" :size="link.size" />
            </q-item-label>
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ link.title }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { inject } from 'vue';
import { SessionStorage } from 'quasar';

const notLoginList = [
  {
    title: 'Login',
    icon: 'login',
    page: '/login',
    size: 'sm'
  },
  {
    title: 'Signup',
    icon: 'how_to_reg',
    page: '/register',
    size: 'sm'
  },
]

const loginList = [

  {
    title: 'Map',
    icon: 'map',
    page: '/',
    size: 'sm'
  },
  {
    title: 'Historical',
    icon: 'list',
    page: '/historical',
    size: 'sm'
  },
  {
    title: 'Trainees',
    icon: 'example',
    page: '/trainees',
    size: 'sm'
  }
]

export default defineComponent({
  name: 'MainLayout',

  setup() {
    const router = useRouter()
    const leftDrawerOpen = ref(false)
    const helpers = inject('helpers')
    var isAuthenticated = ref()
    var essentialLinks = ref([]);
    var userData = ref({});
    var showDialog = ref();
    var capturedImage = ref();
    var password = ref('');
    var showAlert = ref(false);

    // Check if token exists
    if (helpers && helpers.checkToken && helpers.checkToken()) {
      essentialLinks.value = loginList;
      isAuthenticated.value = true;
    } else {
      essentialLinks.value = notLoginList;
      isAuthenticated.value = false;
    }

    const navigate = (page) => {
      if (page === 'logout') {
        helpers.logout(router.push, isAuthenticated);
      } else {
        router.push(page);
      }
    }

    const toggleLeftDrawer = () => {
      leftDrawerOpen.value = !leftDrawerOpen.value;
    }

    window.addEventListener('Auth', (event) => {
      isAuthenticated.value = true;
      essentialLinks.value = loginList;
      userData.value = SessionStorage.getItem('user');
    });

    window.addEventListener('notAuth', (event) => {
      isAuthenticated.value = false;
      essentialLinks.value = notLoginList;
      userData.value = {};
    });

    const toggleChanged = () => {
      if (userData.value.two_factor_auth) {
        // If toggle value is true, show the popup
        showDialog.value = true;
        userData.value.two_factor_auth = false;
      } else {
        showAlert.value = true;
        userData.value.two_factor_auth = true;
      }
    };

    const captureImage = async () => {
      capturedImage.value = await helpers.takePhoto();
    }

    const closePopup = () => {
      // Close the dialog without capturing an image
      showDialog.value = false;
      password.value = '';
      capturedImage.value = '';
      showAlert.value = false;
    }

    const confirmPhoto = async () => {
      userData.value.two_factor_auth = await helpers.sendImageToBackend(capturedImage.value, password.value);
      if (userData.value.two_factor_auth) {
        closePopup();
      }
    }
    
    const disableTwoFactorAuth = async () => {
      userData.value.two_factor_auth = !(await helpers.disableTwoFactor(password.value));
      if (!userData.value.two_factor_auth) {
        showAlert.value = false;
      }
    }
    return {
      essentialLinks,
      leftDrawerOpen,
      isAuthenticated,
      userData,
      showDialog,
      capturedImage,
      password,
      showAlert,
      disableTwoFactorAuth,
      toggleLeftDrawer,
      navigate,
      toggleChanged,
      captureImage,
      closePopup,
      confirmPhoto
    };
  }

})
</script>
