<script setup lang="ts">
import { ref } from "vue";
import BftForm, { type BftFormPayload } from "./components/BftForm.vue";
import ResultViewer from "./components/ResultViewer.vue";

type ApiResponse = {
  bft_id: string;
  structured_output: Record<string, unknown>;
  artifacts: Record<string, unknown>;
};

const loading = ref(false);
const error = ref<string | null>(null);
const result = ref<ApiResponse | null>(null);

const handleSubmit = async (payload: BftFormPayload) => {
  loading.value = true;
  error.value = null;
  result.value = null;

  try {
    const response = await fetch("http://localhost:8000/api/v1/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Ошибка API: ${await response.text()}`);
    }

    const data = (await response.json()) as ApiResponse;
    result.value = data;
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Неизвестная ошибка";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="container">
    <header>
      <h1>BFT Semantic Analyzer</h1>
      <p>MVP для архитектурного анализа БФТ (RAG + LLM)</p>
    </header>

    <main>
      <BftForm :loading="loading" @submit="handleSubmit" />

      <ResultViewer
        :loading="loading"
        :error="error"
        :result="result"
      />
    </main>
  </div>
</template>