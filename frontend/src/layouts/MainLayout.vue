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
        <q-card>
          <q-card-section v-if="capturedImage">
            <q-img :src="capturedImage" alt="Captured Image" style="max-width: 100%;" />
          </q-card-section>
          <q-card-section> 
            <q-btn label="Capture" color="primary" @click="captureImage" />
            <q-btn v-if="capturedImage" label="Confirm" color="green" @click="confirmPhoto" class="confirm-button" />
            <q-btn label="Cancel" color="negative" @click="cancelCapture" />
          </q-card-section>
        </q-card>
      </q-dialog>
    </div>

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
        logic
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
      }
    };

    const captureImage = async () => {
      try {
        // Access the user's camera
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });

        // Create a video element to display the camera stream
        const videoElement = document.createElement('video');
        videoElement.srcObject = stream;
        videoElement.autoplay = true;

        // Wait for the video to load
        await new Promise(resolve => videoElement.onloadedmetadata = resolve);

        // Create a canvas element to capture the image
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;

        // Draw the video frame on the canvas
        const context = canvas.getContext('2d');
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

        // Stop the camera stream
        stream.getVideoTracks().forEach(track => track.stop());

        // Convert the canvas image to a data URL
        const dataUrl = canvas.toDataURL('image/png');


        // Set the captured image
        capturedImage.value = dataUrl;

      } catch (error) {
        console.error('Error capturing image:', error);
      }
    }

    const cancelCapture = () => {
      // Close the dialog without capturing an image
      showDialog.value = false;
    }

    const confirmPhoto = () => {
      // You can implement further actions here, such as saving the image or processing it
      userData.value.two_factor_auth = helpers.sendImageToBackend(capturedImage.value);
    }

    return {
      essentialLinks,
      leftDrawerOpen,
      isAuthenticated,
      userData,
      showDialog,
      capturedImage,
      toggleLeftDrawer,
      navigate,
      toggleChanged,
      captureImage,
      cancelCapture,
      confirmPhoto
    };
  }

})
</script>
