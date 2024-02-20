import * as helpers from '../helpers/helpers.js';
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { 
        path: '', 
        component: () => import('pages/IndexPage.vue'),
        name: 'index'
      }
    ],
    beforeEnter: (to, from, next) => {
      const token = helpers.checkToken();
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
    ]
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
    beforeEnter: (to, from, next) => {
      const token = helpers.checkToken();
      console.log(token);
      if (!token) {
        next({ name: 'login' });
      } else {
        next();
      }
    }
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
