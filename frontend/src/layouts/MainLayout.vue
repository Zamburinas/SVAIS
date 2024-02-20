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
              <q-icon :name="link.icon" />
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

const linksList = [
  {
    title: 'Login',
    icon: 'login',
    page: '/login'
  },
  {
    title: 'Map',
    icon: 'map',
    page: '/'
  },
  {
    title: 'Historical',
    icon: 'list',
    page: '/historical'
  },
]

export default defineComponent({
  name: 'MainLayout',

  setup () {
    const router = useRouter()
    const leftDrawerOpen = ref(false)

    const navigate = (page) => {
      router.push(page)
      // No se cierra el cajón al cambiar de página
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
