<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          SVAIS
        </q-toolbar-title>

      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
      <q-list>
        <q-item-label header>
          
        </q-item-label>

        <q-item
          v-for="link in essentialLinks"
          :key="link.title"
          clickable
          @click="navigate(link.page)"
        >
          <q-item-section avatar>
            <q-item-label>
              <q-icon 
                :name="link.icon" 
                :size="link.size"/>
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

const linksList = [
  {
    title: 'Login',
    icon: 'login',
    page: '/login',
    size: 'sm'
  },
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
    title: 'logOut',
    icon: 'logout',
    page: 'logout',
    size: 'sm'
  },
]

export default defineComponent({
  name: 'MainLayout',

  setup () {
    const router = useRouter()
    const leftDrawerOpen = ref(false)
    const helpers = inject('helpers')
    const navigate = (page) => {
      if (page === 'logout') {
        helpers.logout(router.push);
      } else {
        router.push(page)
      }
    }

    const toggleLeftDrawer = () => {
      leftDrawerOpen.value = !leftDrawerOpen.value
    }

    return {
      essentialLinks: linksList,
      leftDrawerOpen,
      toggleLeftDrawer,
      navigate
    }
  }
})
</script>
