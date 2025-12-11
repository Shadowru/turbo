<script setup lang="ts">
import { computed, ref } from "vue";

type UploadDoc = {
  doc_id: string;
  filename: string;
  size_bytes: number;
  status?: "processed" | "pending" | "error";
  uploaded_at?: string;
  chunks?: number;
};

const props = defineProps<{
  endpoint?: string;
}>();

const emit = defineEmits<{
  (event: "uploaded", payload: { documents: UploadDoc[] }): void;
  (event: "error", message: string): void;
}>();

const API_ENDPOINT = props.endpoint ?? "http://localhost:8000/api/v1/rag/documents";

const fileInput = ref<HTMLInputElement | null>(null);
const files = ref<File[]>([]);
const isDragOver = ref(false);
const textMode = ref(false);
const textContent = ref("");
const autoProcess = ref(true);
const uploading = ref(false);
const errorMessage = ref<string | null>(null);

const hasSelection = computed(() => files.value.length > 0 || Boolean(textContent.value.trim()));

const formatSize = (bytes: number) => {
  const units = ["Б", "КБ", "МБ", "ГБ"];
  let size = bytes;
  let unit = 0;
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024;
    unit++;
  }
  return `${size.toFixed(unit === 0 ? 0 : 1)} ${units[unit]}`;
};

const openFileDialog = () => fileInput.value?.click();

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target.files?.length) return;
  files.value = [...files.value, ...Array.from(target.files)];
  target.value = "";
};

const handleDrop = (event: DragEvent) => {
  const droppedFiles = event.dataTransfer?.files;
  if (!droppedFiles?.length) return;
  files.value = [...files.value, ...Array.from(droppedFiles)];
  isDragOver.value = false;
};

const removeFile = (index: number) => {
  files.value = files.value.filter((_, idx) => idx !== index);
};

const clearAll = () => {
  files.value = [];
  textContent.value = "";
  errorMessage.value = null;
};

const toggleTextMode = () => {
  textMode.value = !textMode.value;
};

const upload = async () => {
  if (!hasSelection.value || uploading.value) return;

  uploading.value = true;
  errorMessage.value = null;

  try {
    const formData = new FormData();
    files.value.forEach((file) => formData.append("files", file));

    if (textContent.value.trim()) {
      formData.append("text", textContent.value.trim());
    }

    formData.append("auto_process", String(autoProcess.value));

    const response = await fetch(API_ENDPOINT, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || "Ошибка загрузки RAG");
    }

    const payload = await response.json();

    let documents: UploadDoc[] = [];
    if (Array.isArray(payload?.documents)) {
      documents = payload.documents;
    } else if (Array.isArray(payload)) {
      documents = payload;
    } else {
      const now = new Date().toISOString();
      documents = files.value.map((file) => ({
        doc_id: payload?.doc_id ?? `doc-${Date.now()}-${file.name}`,
        filename: file.name,
        size_bytes: file.size,
        status: "processed",
        uploaded_at: now,
      }));
    }

    emit("uploaded", { documents });
    clearAll();
  } catch (err) {
    const message = err instanceof Error ? err.message : "Неизвестная ошибка";
    errorMessage.value = message;
    emit("error", message);
    console.error("RAG upload error:", err);
  } finally {
    uploading.value = false;
  }
};
</script>

<template>
  <div class="rag-uploader">
    <div
      class="drop-zone"
      :class="{
        'is-dragover': isDragOver,
        'has-files': files.length > 0,
      }"
      @click="openFileDialog"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop($event)"
    >
      <div class="cloud-icon">☁️</div>
      <p class="drop-title">Перетащите документы сюда</p>
      <p class="drop-subtitle">или воспользуйтесь кнопками ниже</p>

      <input
        ref="fileInput"
        class="hidden-input"
        type="file"
        multiple
        @change="handleFileChange"
      />
    </div>

    <div class="upload-buttons">
      <button type="button" @click.stop="openFileDialog">Выбрать файл(ы)</button>
      <button type="button" @click.stop="toggleTextMode">
        {{ textMode ? "Скрыть текстовое поле" : "Вставить текст вручную" }}
      </button>
    </div>

    <label class="auto-process">
      <input v-model="autoProcess" type="checkbox" />
      Автообработка после загрузки
    </label>

    <transition name="fade">
      <div v-if="textMode" class="manual-text">
        <textarea
          v-model="textContent"
          rows="6"
          placeholder="Вставьте текстовую инструкцию или регламент. Он также попадёт в RAG."
        />
      </div>
    </transition>

    <div v-if="files.length" class="file-list">
      <h4>Выбранные файлы</h4>
      <ul>
        <li v-for="(file, index) in files" :key="`${file.name}-${index}`">
          <div class="file-info">
            <strong>{{ file.name }}</strong>
            <span>{{ formatSize(file.size) }}</span>
          </div>
          <button type="button" title="Убрать файл" @click.stop="removeFile(index)">✕</button>
        </li>
      </ul>
    </div>

    <footer class="uploader-footer">
      <button
        type="button"
        class="primary"
        :disabled="uploading || !hasSelection"
        @click="upload"
      >
        {{ uploading ? "Загружаем..." : "Загрузить" }}
      </button>
      <button type="button" class="secondary" :disabled="uploading" @click="clearAll">
        Очистить
      </button>

      <span v-if="errorMessage" class="status error">
        {{ errorMessage }}
      </span>
      <span v-else-if="uploading" class="status muted">
        Обработка документов...
      </span>
    </footer>
  </div>
</template>

<style scoped>
.rag-uploader {
  display: grid;
  gap: 18px;
}

.drop-zone {
  border: 2px dashed rgba(60, 93, 227, 0.4);
  border-radius: 26px;
  padding: 40px 20px;
  background: rgba(255, 255, 255, 0.78);
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease, background 0.2s ease,
    box-shadow 0.2s ease;
  position: relative;
}

.drop-zone:hover {
  border-color: rgba(60, 93, 227, 0.65);
  transform: translateY(-3px);
  background: rgba(255, 255, 255, 0.9);
}

.drop-zone.is-dragover {
  border-color: rgba(60, 93, 227, 0.9);
  background: rgba(60, 93, 227, 0.18);
  box-shadow: 0 20px 46px rgba(60, 93, 227, 0.25);
}

.drop-zone .cloud-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.drop-title {
  margin: 0;
  font-weight: 700;
  font-size: 1.1rem;
  color: rgba(21, 31, 66, 0.85);
}

.drop-subtitle {
  margin: 6px 0 0;
  color: rgba(21, 31, 66, 0.6);
}

.hidden-input {
  display: none;
}

.upload-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.upload-buttons button {
  border: 1px solid rgba(33, 52, 118, 0.22);
  border-radius: 12px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.94);
  color: rgba(33, 52, 118, 0.82);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.1s ease;
}

.upload-buttons button:hover {
  background: rgba(62, 116, 229, 0.16);
  transform: translateY(-1px);
}

.auto-process {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 0.9rem;
  color: rgba(21, 31, 66, 0.72);
}

.auto-process input {
  width: 18px;
  height: 18px;
}

.manual-text textarea {
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(33, 52, 118, 0.2);
  background: rgba(255, 255, 255, 0.96);
  padding: 12px 14px;
  font-family: inherit;
  resize: vertical;
  min-height: 140px;
}

.file-list {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(33, 52, 118, 0.14);
  border-radius: 16px;
  padding: 16px;
  display: grid;
  gap: 12px;
}

.file-list h4 {
  margin: 0;
  font-size: 1rem;
}

.file-list ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 10px;
}

.file-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.file-info {
  display: grid;
  gap: 4px;
}

.file-info strong {
  color: rgba(21, 31, 66, 0.9);
}

.file-info span {
  color: rgba(21, 31, 66, 0.6);
  font-size: 0.85rem;
}

.file-list button {
  border: none;
  background: rgba(255, 107, 107, 0.22);
  color: #b21f1f;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.file-list button:hover {
  background: rgba(255, 107, 107, 0.3);
}

.uploader-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-end;
  align-items: center;
}

.uploader-footer .primary {
  border: none;
  border-radius: 12px;
  padding: 12px 22px;
  font-weight: 600;
  background: linear-gradient(135deg, #3c5de3, #7b5cf0);
  color: #fff;
  cursor: pointer;
  transition: transform 0.1s ease, box-shadow 0.2s ease;
}

.uploader-footer .primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.uploader-footer .primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 18px 44px rgba(60, 93, 227, 0.26);
}

.uploader-footer .secondary {
  border: 1px solid rgba(33, 52, 118, 0.22);
  border-radius: 12px;
  padding: 11px 18px;
  background: rgba(255, 255, 255, 0.94);
  font-weight: 600;
  color: rgba(33, 52, 118, 0.82);
  cursor: pointer;
}

.uploader-footer .secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.uploader-footer .secondary:hover:not(:disabled) {
  background: rgba(62, 116, 229, 0.14);
}

.status {
  font-size: 0.9rem;
}

.status.error {
  color: rgba(192, 57, 43, 0.92);
}

.status.muted {
  color: rgba(21, 31, 66, 0.6);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>