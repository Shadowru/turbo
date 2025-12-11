<script setup lang="ts">
import { onMounted, ref } from "vue";
import BftForm, { type BftFormPayload } from "../components/BftForm.vue";
import ResultViewer from "../components/ResultViewer.vue";
import HistoryList from "../components/HistoryList.vue";

type ApiResponse = {
  bft_id: string;
  structured_output: Record<string, unknown>;
  artifacts: Record<string, unknown>;
  history_id: number;
  created_at: string;
};

type HistoryDetail = {
  id: number;
  bft_id: string;
  request_text: string;
  structured_output: Record<string, unknown>;
  artifacts: Record<string, unknown>;
  raw_llm_output: string | null;
  retrieved_context: string | null;
  created_at: string;
};

type HistoryItem = {
  id: number;
  bft_id: string;
  created_at: string;
  preview: string;
};

const loading = ref(false);
const error = ref<string | null>(null);
const result = ref<ApiResponse | null>(null);

const historyItems = ref<HistoryItem[]>([]);
const historyLoading = ref(false);
const activeHistoryId = ref<number | null>(null);

const formBftId = ref<string | null>(null);
const formText = ref<string | null>(null);

const fetchHistoryList = async () => {
  historyLoading.value = true;
  try {
    const response = await fetch("http://localhost:8000/api/v1/history?limit=20");
    if (!response.ok) {
      throw new Error(`Ошибка загрузки истории: ${await response.text()}`);
    }
    const payload = (await response.json()) as { items: HistoryItem[] };
    historyItems.value = payload.items;
  } catch (err) {
    console.error(err);
  } finally {
    historyLoading.value = false;
  }
};

const loadHistoryDetail = async (id: number) => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/history/${id}`);
    if (!response.ok) {
      throw new Error(`Ошибка загрузки записи: ${await response.text()}`);
    }
    const payload = (await response.json()) as HistoryDetail;
    result.value = {
      bft_id: payload.bft_id,
      structured_output: payload.structured_output,
      artifacts: payload.artifacts,
      history_id: payload.id,
      created_at: payload.created_at,
    };
    activeHistoryId.value = payload.id;
    formBftId.value = payload.bft_id;
    formText.value = payload.request_text;
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Неизвестная ошибка";
    console.error(err);
  }
};

const handleSubmit = async (payload: BftFormPayload) => {
  loading.value = true;
  error.value = null;

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
    activeHistoryId.value = data.history_id;

    // Обновляем форму
    formBftId.value = payload.bft_id;
    formText.value = payload.text;

    await fetchHistoryList();
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Неизвестная ошибка";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const loadLatest = async () => {
  try {
    const response = await fetch("http://localhost:8000/api/v1/history/latest");
    if (!response.ok) {
      throw new Error(`Ошибка загрузки последнего анализа: ${await response.text()}`);
    }
    const payload = (await response.json()) as HistoryDetail | null;
    if (payload) {
      result.value = {
        bft_id: payload.bft_id,
        structured_output: payload.structured_output,
        artifacts: payload.artifacts,
        history_id: payload.id,
        created_at: payload.created_at,
      };
      activeHistoryId.value = payload.id;
      formBftId.value = payload.bft_id;
      formText.value = payload.request_text;
    }
  } catch (err) {
    console.warn("Последний анализ не найден:", err);
  }
};

onMounted(async () => {
  await Promise.all([fetchHistoryList(), loadLatest()]);
});
</script>

<template>
  <div class="analyzer-layout">
    <section class="form-column">
      <BftForm
        :loading="loading"
        :initial-bft-id="formBftId"
        :initial-text="formText"
        @submit="handleSubmit"
      />
    </section>

    <section class="history-column">
      <HistoryList
        :items="historyItems"
        :active-id="activeHistoryId"
        :loading="historyLoading"
        @select="loadHistoryDetail"
      />
    </section>

    <section class="results-column">
      <ResultViewer
        :loading="loading"
        :error="error"
        :result="result"
      />
    </section>
  </div>
</template>

<style scoped>
.analyzer-layout {
  display: grid;
  gap: 24px;
  grid-template-columns: minmax(340px, 1fr) minmax(260px, 0.8fr) minmax(420px, 1.4fr);
  align-items: start;
}

.form-column,
.history-column,
.results-column {
  display: grid;
}
</style>