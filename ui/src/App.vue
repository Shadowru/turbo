<script setup lang="ts">
import { computed } from "vue";
import { useRoute, RouterLink, RouterView } from "vue-router";

const route = useRoute();
const title = computed(() =>
  route.name === "rag" ? "RAG Knowledge Base" : "BFT Semantic Analyzer"
);
</script>

<template>
  <div class="global-container">
    <header class="app-header">
      <div>
        <h1>{{ title }}</h1>
        <p>
          {{ route.name === "rag"
            ? "Управление корпоративными знаниями для RAG"
            : "MVP для архитектурного анализа БФТ (RAG + LLM)" }}
        </p>
      </div>

      <nav class="app-nav">
        <RouterLink :to="{ name: 'analyzer' }" class="nav-link" :class="{ active: route.name === 'analyzer' }">
          Анализ БФТ
        </RouterLink>
        <RouterLink :to="{ name: 'rag' }" class="nav-link" :class="{ active: route.name === 'rag' }">
          Управление RAG
        </RouterLink>
      </nav>
    </header>

    <main class="page-container">
      <RouterView />
    </main>
  </div>
</template>