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
    path: '/trainees',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { 
        path: '', 
        component: () => import('pages/TraineesPage.vue'),
        name: 'trainees'
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
    path: '/trainees/CorrectBoatPage',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { 
        path: '', 
        component: () => import('pages/CorrectBoatPage.vue'),
        name: 'CorrectBoatPage'
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
    path: '/trainees/IncorrectBoatPage',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { 
        path: '', 
        component: () => import('pages/IncorrectBoatPage.vue'),
        name: 'IncorrectBoatPage'
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
    path: '/trainees/IncorrectRoutePage',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { 
        path: '', 
        component: () => import('pages/IncorrectRoutePage.vue'),
        name: 'IncorrectRoutePage'
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
    path: '/trainees/CorrectRoutePage',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { 
        path: '', 
        component: () => import('pages/CorrectRoutePage.vue'),
        name: 'CorrectRoutePage'
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
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
