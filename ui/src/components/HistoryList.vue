<script setup lang="ts">
import { computed } from "vue";

type HistoryItem = {
  id: number;
  bft_id: string;
  created_at: string;
  preview: string;
};

const props = defineProps<{
  items: HistoryItem[];
  activeId: number | null;
  loading: boolean;
}>();

const emit = defineEmits<{
  (event: "select", id: number): void;
}>();

const formattedItems = computed(() =>
  props.items.map((item) => ({
    ...item,
    created_at_formatted: new Date(item.created_at).toLocaleString(),
  })),
);
</script>

<template>
  <aside class="history-panel panel">
    <header>
      <h3>История запросов</h3>
      <p class="muted">Последние BFT анализы</p>
    </header>

    <div v-if="loading" class="history-placeholder">
      Загрузка истории...
    </div>

    <div v-else-if="!items.length" class="history-placeholder">
      История пока пуста.
    </div>

    <ul v-else class="history-list">
      <li
        v-for="item in formattedItems"
        :key="item.id"
        class="history-item"
        :class="{ active: activeId === item.id }"
        @click="emit('select', item.id)"
      >
        <div class="history-meta">
          <span class="history-badge">{{ item.bft_id }}</span>
          <time>{{ item.created_at_formatted }}</time>
        </div>
        <p class="history-preview">{{ item.preview }}</p>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.history-panel {
  display: grid;
  gap: 16px;
  max-height: calc(100vh - 240px);
  overflow-y: auto;
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 12px;
}

.history-item {
  border-radius: 14px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid transparent;
  box-shadow: inset 0 0 0 1px rgba(24, 36, 82, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
  display: grid;
  gap: 8px;
}
.history-item:hover {
  border-color: rgba(62, 116, 229, 0.35);
  box-shadow: 0 16px 32px rgba(62, 116, 229, 0.12);
  transform: translateY(-2px);
}
.history-item.active {
  border-color: rgba(62, 116, 229, 0.6);
  box-shadow: 0 18px 40px rgba(62, 116, 229, 0.18);
  background: rgba(62, 116, 229, 0.12);
}

.history-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  font-size: 0.92rem;
  color: rgba(21, 31, 66, 0.7);
}

.history-badge {
  padding: 4px 10px;
  border-radius: 10px;
  background: rgba(62, 116, 229, 0.16);
  color: #2d4aa1;
  font-weight: 600;
  font-size: 0.85rem;
}

.history-preview {
  margin: 0;
  color: rgba(21, 31, 66, 0.9);
  line-height: 1.4;
}

.history-placeholder {
  padding: 40px 12px;
  text-align: center;
  color: rgba(21, 31, 66, 0.5);
  font-style: italic;
}
</style>