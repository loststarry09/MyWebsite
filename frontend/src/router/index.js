import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Programs from '../views/Programs.vue'
import ProgramDetail from '../views/ProgramDetail.vue'
import Fun from '../views/Fun.vue'
import ComingSoon from '../views/ComingSoon.vue'
import BlogList from '../views/BlogList.vue'
import BlogDetail from '../views/BlogDetail.vue'
import BlogEditor from '../views/BlogEditor.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/programs', name: 'programs', component: Programs },
  { path: '/program/:id', name: 'program-detail', component: ProgramDetail },
  { path: '/fun', name: 'fun', component: Fun },
  { path: '/blog', name: 'blog', component: BlogList },
  { path: '/blog/new', name: 'blog-new', component: BlogEditor },
  { path: '/blog/edit/:id', name: 'blog-edit', component: BlogEditor },
  { path: '/blog/:id', name: 'blog-detail', component: BlogDetail },
  { path: '/coming-soon', name: 'coming-soon', component: ComingSoon },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
