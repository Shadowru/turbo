<script setup lang="ts">
import { computed, ref } from "vue";
import RagUploader from "../components/RagUploader.vue";

type HistoryStatus = "processed" | "pending" | "error";

type HistoryRow = {
  id: number;
  docId: string;
  filename: string;
  type: string;
  sizeBytes: number;
  uploadedAt: string;
  status: HistoryStatus;
};

const activeTab = ref<"upload" | "collections" | "settings">("upload");

const uploadHistory = ref<HistoryRow[]>([
  {
    id: 1,
    docId: "doc-req",
    filename: "requirements.pdf",
    type: "PDF",
    sizeBytes: 1.2 * 1024 * 1024,
    uploadedAt: "2023-04-12T10:30:00Z",
    status: "processed",
  },
  {
    id: 2,
    docId: "doc-api",
    filename: "api_spec.md",
    type: "MD",
    sizeBytes: 0.4 * 1024 * 1024,
    uploadedAt: "2023-04-12T09:45:00Z",
    status: "processed",
  },
  {
    id: 3,
    docId: "doc-arch",
    filename: "architecture.pptx",
    type: "PPTX",
    sizeBytes: 3.1 * 1024 * 1024,
    uploadedAt: "2023-04-12T09:10:00Z",
    status: "pending",
  },
  {
    id: 4,
    docId: "doc-error",
    filename: "ошибка_log.txt",
    type: "TXT",
    sizeBytes: 0.1 * 1024 * 1024,
    uploadedAt: "2023-04-12T08:55:00Z",
    status: "error",
  },
]);

const statusConfig: Record<
  HistoryStatus,
  { label: string; className: string; icon: string }
> = {
  processed: {
    label: "Готово",
    className: "success",
    icon: "✅",
  },
  pending: {
    label: "В обработке",
    className: "pending",
    icon: "⏳",
  },
  error: {
    label: "Ошибка",
    className: "error",
    icon: "⚠️",
  },
};

const historyCount = computed(() => uploadHistory.value.length);

const formatSize = (bytes: number) => {
  if (!bytes) return "—";
  const units = ["Б", "КБ", "МБ", "ГБ"];
  let size = bytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  return `${size.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
};

const formatDate = (iso: string) => {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const extensionFromName = (name: string) => {
  const parts = name.split(".");
  return parts.length > 1 ? parts.pop()?.toUpperCase() ?? "—" : "—";
};

const handleUploaded = (payload: { documents?: any[] } | null) => {
  const docs = Array.isArray(payload?.documents) ? payload!.documents : [];
  const now = new Date().toISOString();

  // fallback, если API вернул одиночный объект
  if (!docs.length && payload && "docId" in payload) {
    docs.push(payload);
  }

  docs.forEach((doc) => {
    const filename = doc.filename ?? doc.name ?? doc.doc_id ?? "Документ";
    uploadHistory.value.unshift({
      id: Date.now() + Math.floor(Math.random() * 1000),
      docId: doc.doc_id ?? doc.docId ?? filename,
      filename,
      type: extensionFromName(filename),
      sizeBytes: doc.size_bytes ?? doc.size ?? 0,
      uploadedAt: doc.uploaded_at ?? now,
      status: (doc.status ?? "processed") as HistoryStatus,
    });
  });

  // ограничим список последними 50 записями
  uploadHistory.value = uploadHistory.value.slice(0, 50);
};

const removeEntry = (row: HistoryRow) => {
  uploadHistory.value = uploadHistory.value.filter((item) => item.id !== row.id);
};

const retryEntry = (row: HistoryRow) => {
  const entry = uploadHistory.value.find((item) => item.id === row.id);
  if (entry) {
    entry.status = "pending";
    entry.uploadedAt = new Date().toISOString();
  }
};

const switchTab = (tab: "upload" | "collections" | "settings") => {
  activeTab.value = tab;
};
</script>

<template>
  <div class="rag-wrapper">
    <header class="rag-header">
      <div>
        <h1>🔷 RAG KNOWLEDGE BASE</h1>
        <p>Управление корпоративной базой знаний для Retrieval-Augmented Generation.</p>
      </div>

      <div class="rag-actions">
        <span class="status-chip">
          <span class="dot"></span>
          Готово к загрузке
        </span>
        <button type="button" class="user-avatar" title="Профиль">
          👤
        </button>
      </div>
    </header>

    <nav class="rag-quick-tabs">
      <button
        class="tab-pill"
        :class="{ active: activeTab === 'upload' }"
        @click="switchTab('upload')"
      >
        📥 Загрузка
      </button>
      <button
        class="tab-pill"
        :class="{ active: activeTab === 'collections' }"
        @click="switchTab('collections')"
      >
        📚 Коллекции
      </button>
      <button
        class="tab-pill"
        :class="{ active: activeTab === 'settings' }"
        @click="switchTab('settings')"
      >
        ⚙️ Настройки RAG
      </button>
    </nav>

    <section v-if="activeTab === 'upload'" class="rag-grid">
      <article class="rag-upload-card">
        <header>
          <div>
            <h2>Перетащите документы или выберите файлы</h2>
            <p>
              Поддерживаются PDF, DOCX, PPTX, Markdown и plain-text. При включённой автообработке
              документы автоматически разрезаются на чанки и индексируются в гибридном RAG.
            </p>
          </div>
        </header>

        <RagUploader @uploaded="handleUploaded" />
      </article>

      <article class="rag-table-card">
        <header>
          <div>
            <h3>📋 Последние загрузки</h3>
            <p class="muted">
              Отслеживайте статус обработки и переиндексации документов ({{ historyCount }}).
            </p>
          </div>
        </header>

        <div class="table-scroll">
          <table class="rag-table">
            <thead>
              <tr>
                <th>Название</th>
                <th>Тип</th>
                <th>Размер</th>
                <th>Дата</th>
                <th>Статус</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in uploadHistory" :key="row.id">
                <td>
                  <div class="doc-name">
                    <strong>{{ row.filename }}</strong>
                    <span class="muted">{{ row.docId }}</span>
                  </div>
                </td>
                <td>{{ row.type }}</td>
                <td>{{ formatSize(row.sizeBytes) }}</td>
                <td>{{ formatDate(row.uploadedAt) }}</td>
                <td>
                  <span
                    class="history-status"
                    :class="statusConfig[row.status].className"
                  >
                    {{ statusConfig[row.status].icon }}
                    {{ statusConfig[row.status].label }}
                  </span>
                </td>
                <td>
                  <div class="table-actions">
                    <button type="button" title="Удалить" @click="removeEntry(row)">
                      🗑️
                    </button>
                    <button type="button" title="Переиндексировать" @click="retryEntry(row)">
                      🔄
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
            <tfoot v-if="!uploadHistory.length">
              <tr>
                <td colspan="6">Загрузок пока нет.</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </article>
    </section>

    <section v-else class="rag-placeholder">
      <h3>
        {{
          activeTab === "collections"
            ? "Сводка коллекций и метрик — скоро здесь."
            : "Расширенные настройки RAG — в разработке."
        }}
      </h3>
      <p>
        Вы сможете управлять несколькими наборами знаний, обновлять веса BM25 / векторного индекса
        и запускать переиндексацию из этой вкладки.
      </p>
    </section>
  </div>
</template>