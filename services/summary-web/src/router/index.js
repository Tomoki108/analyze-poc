import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DailyOrderSummariesView from '../views/DailyOrderSummariesView.vue'
import UserSegmentsView from '../views/UserSegmentsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/daily_order_summaries',
      name: 'daily_order_summaries',
      component: DailyOrderSummariesView
    },
    {
      path: '/user_segments',
      name: 'user_segments',
      component: UserSegmentsView
    }
  ]
})

export default router
