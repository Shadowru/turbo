import { createRouter, createWebHistory } from "vue-router";

const AnalyzerPage = () => import("../pages/AnalyzerPage.vue");
const RagPage = () => import("../pages/RagPage.vue");

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "analyzer", component: AnalyzerPage },
    { path: "/rag", name: "rag", component: RagPage },
  ],
});

export default router;