<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import BftForm, { type BftFormPayload } from "../components/BftForm.vue";
import ResultViewer from "../components/ResultViewer.vue";
import HistoryList from "../components/HistoryList.vue";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";


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

type ViewMode = "landing" | "result";
const viewMode = ref<ViewMode>("landing");

const resultCreatedAt = computed(() => {
  if (!result.value?.created_at) return null;
  const date = new Date(result.value.created_at);
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
});

const fetchHistoryList = async () => {
  historyLoading.value = true;
  try {
    const response = await fetch(`${API_BASE}/api/v1/history?limit=20`);
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
    const response = await fetch(`${API_BASE}/api/v1/history/${id}`);
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
    viewMode.value = "result";
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Неизвестная ошибка";
    console.error(err);
  }
};

const handleSubmit = async (payload: BftFormPayload) => {
  loading.value = true;
  error.value = null;

  try {
    const response = await fetch(`${API_BASE}/api/v1/analyze`, {
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

    formBftId.value = payload.bft_id;
    formText.value = payload.text;

    await fetchHistoryList();
    viewMode.value = "result";
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Неизвестная ошибка";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const backToLanding = () => {
  viewMode.value = "landing";
  result.value = null;
  activeHistoryId.value = null;
};

onMounted(async () => {
  await fetchHistoryList();
});
</script>

<template>
  <div class="analyzer-page">
    <section v-if="viewMode === 'landing'" class="landing-view">
      <header class="landing-header">
        <div>
          <h1>Анализ БФТ</h1>
          <p>
            Подготовьте ID и описание бизнес-функционального требования. Система сравнит его
            с корпоративной базой знаний и сформирует интеграционную архитектуру.
          </p>
        </div>
      </header>

      <div class="landing-grid">
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
      </div>
    </section>

    <section v-else class="result-view">
      <div class="result-top-bar">
        <button type="button" class="back-button" @click="backToLanding">
          ← Вернуться к началу
        </button>

        <div v-if="result" class="result-meta">
          <span class="meta-chip">
            BFT ID: <strong>{{ result.bft_id }}</strong>
          </span>
          <span v-if="resultCreatedAt" class="meta-chip">
            Анализ от: <strong>{{ resultCreatedAt }}</strong>
          </span>
        </div>
      </div>

      <ResultViewer
        :loading="loading"
        :error="error"
        :result="result"
      />
    </section>
  </div>
</template>

<style scoped>
.analyzer-page {
  display: grid;
  gap: 24px;
}

.landing-view {
  display: grid;
  gap: 28px;
}

.landing-header h1 {
  margin: 0;
  font-size: 2rem;
  letter-spacing: -0.01em;
}

.landing-header p {
  margin: 10px 0 0;
  color: rgba(21, 31, 66, 0.75);
  max-width: 720px;
  line-height: 1.55;
}

.landing-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: minmax(340px, 1fr) minmax(320px, 0.9fr);
  align-items: start;
}

.form-column,
.history-column {
  display: grid;
}

.result-view {
  display: grid;
  gap: 20px;
}

.result-top-bar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.back-button {
  border: none;
  border-radius: 12px;
  padding: 10px 16px;
  background: rgba(62, 116, 229, 0.14);
  color: #2c3faa;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.1s ease;
}
.back-button:hover {
  background: rgba(62, 116, 229, 0.22);
  transform: translateY(-1px);
}

.result-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.meta-chip {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  padding: 8px 12px;
  border-radius: 10px;
  background: rgba(24, 36, 82, 0.08);
  color: rgba(24, 36, 82, 0.85);
  font-size: 0.9rem;
}
.meta-chip strong {
  font-weight: 700;
}
</style>