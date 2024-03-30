import * as helpers from '../helpers/helpers.js';

const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { 
        path: '', 
        component: () => import('pages/IndexPage.vue'),
        name: 'map'
      }
    ],
    beforeEnter: async (to, from, next) => {
      const token = await helpers.checkToken();
      if (!token) {
        next({ name: 'login' });
      } else {
        next();
      }
    }
  },
  {
    path: '/login',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { 
        path: '', 
        component: () => import('pages/LoginPage.vue'),
        name: 'login'
      }
    ],
    beforeEnter: async (to, from, next) => {
      const token = await helpers.checkToken();
      if (token) {
        next({ name: 'map' });
      } else {
        next();
      }
    }
  },
  {
    path: '/historical',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { 
        path: '', 
        component: () => import('pages/HistoricalPage.vue'),
        name: 'historical'
      }
    ],
    beforeEnter: async (to, from, next) => {
      const token = await helpers.checkToken();
      if (!token) {
        next({ name: 'login' });
      } else {
        next();
      }
    }
  },
  {
    path: '/register',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { 
        path: '', 
        component: () => import('pages/RegisterPage.vue'),
        name: 'register'
      }
    ]
  },
  // {
  //   path: '/profile',
  //   component: () => import('layouts/MainLayout.vue'),
  //   children: [
  //     { 
  //       path: '', 
  //       component: () => import('pages/ProfilePage.vue'),
  //       name: 'profile'
  //     }
  //   ],
  //   beforeEnter: async (to, from, next) => {
  //     const token = await helpers.checkToken();
  //     if (!token) {
  //       next({ name: 'login' });
  //     } else {
  //       next();
  //     }
  //   }
  // },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
