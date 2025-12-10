<script setup lang="ts">
import type { Ref } from "vue";
import MermaidViewer from "./MermaidViewer.vue";

type ApiResponse = {
  bft_id: string;
  structured_output: Record<string, unknown>;
  artifacts: {
    uml?: Array<{ type: string; mermaid: string }>;
    [key: string]: unknown;
  };
};

const props = defineProps<{
  loading: boolean;
  error: string | null;
  result: ApiResponse | null;
}>();
</script>

<template>
  <div class="panel results-wrapper">
    <h2>Результаты</h2>

    <p v-if="loading" class="muted">Запрос выполняется...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="!result" class="muted">Нет данных — выполните анализ.</p>

    <div v-else class="results">
      <section>
        <h3>Структурированный ответ</h3>
        <pre>{{ JSON.stringify(result.structured_output, null, 2) }}</pre>
      </section>

      <section>
        <h3>Mermaid диаграммы</h3>
        <template v-if="result.artifacts.uml?.length">
          <div
            v-for="(diagram, idx) in result.artifacts.uml"
            :key="idx"
            class="diagram-block"
          >
            <p class="diagram-label">
              Тип:
              <strong>{{ diagram.type }}</strong>
            </p>
            <MermaidViewer :chart="diagram.mermaid" />
          </div>
        </template>
        <p v-else class="muted">Диаграммы отсутствуют.</p>
      </section>
    </div>
  </div>
</template>