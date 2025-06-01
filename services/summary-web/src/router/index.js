import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AboutView from '../views/AboutView.vue'
import DailyOrderSummariesView from '../views/DailyOrderSummariesView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView
    },
    {
      path: '/daily_order_summaries',
      name: 'daily_order_summaries',
      component: DailyOrderSummariesView
    }
  ]
})

export default router
