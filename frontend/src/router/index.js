import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Programs from '../views/Programs.vue'
import ProgramDetail from '../views/ProgramDetail.vue'
import Fun from '../views/Fun.vue'
import ComingSoon from '../views/ComingSoon.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/programs', name: 'programs', component: Programs },
  { path: '/program/:id', name: 'program-detail', component: ProgramDetail },
  { path: '/fun', name: 'fun', component: Fun },
  { path: '/coming-soon', name: 'coming-soon', component: ComingSoon },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
