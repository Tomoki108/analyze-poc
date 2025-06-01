/// <reference types="vite/client" />

import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";
import HomeView from "../views/HomeView.vue";
import DailyOrderSummariesView from "../views/DailyOrderSummariesView.vue";
import UserSegmentsView from "../views/UserSegmentsView.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/daily_order_summaries",
    name: "daily_order_summaries",
    component: DailyOrderSummariesView,
  },
  {
    path: "/user_segments",
    name: "user_segments",
    component: UserSegmentsView,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
