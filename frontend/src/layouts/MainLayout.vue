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
                  <q-toggle v-model="mobileData" label="Use Mobile Data" />
                  <q-toggle v-model="bluetooth" label="Bluetooth" />
                </div>

                <q-separator vertical inset class="q-mx-lg" />

                <div class="column items-center">
                  <div class="text-subtitle1 q-mt-md q-mb-xs">John Doe</div>
                  <q-btn color="primary" label="Logout" push size="sm" v-close-popup @click="navigate('logout')" />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>

      </q-toolbar>
    </q-header>

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
    });

    window.addEventListener('notAuth', (event) => {
      isAuthenticated.value = false;
      essentialLinks.value = notLoginList;
    });

    return {
      essentialLinks,
      leftDrawerOpen,
      isAuthenticated,
      toggleLeftDrawer,
      navigate
    };
  }

})
</script>
