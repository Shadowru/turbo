<script setup lang="ts">
import { ref, watch, computed } from "vue";

export type BftFormPayload = {
  bft_id: string;
  text: string;
};

const props = defineProps<{
  loading: boolean;
  initialBftId: string | null;
  initialText: string | null;
}>();

const emit = defineEmits<{
  submit: [payload: BftFormPayload];
}>();

const bftId = ref(props.initialBftId ?? "BFT-001");
const text = ref(
  props.initialText ??
    "Клиент должен иметь возможность обновлять контактные данные в личном кабинете...",
);

watch(
  () => props.initialBftId,
  (value) => {
    if (value !== null) {
      bftId.value = value;
    }
  },
);
watch(
  () => props.initialText,
  (value) => {
    if (value !== null) {
      text.value = value;
    }
  },
);

const submitDisabled = computed(() => {
  if (props.loading) return true;
  return !bftId.value.trim() || text.value.trim().length < 20;
});

const handleSubmit = () => {
  emit("submit", {
    bft_id: bftId.value.trim(),
    text: text.value.trim(),
  });
};

const fillDefaults = () => {
  bftId.value = "BFT-ONBOARD-123";
  text.value =
    "Клиент заполняет onboarding-форму, затем система должна синхронизировать данные с CRM и отправить события...";
};
</script>

<template>
  <form class="panel form-card" @submit.prevent="handleSubmit">
    <header class="form-header">
      <h2>Анализ БФТ</h2>
      <button type="button" class="ghost-button" @click="fillDefaults" :disabled="loading">
        Пример
      </button>
    </header>

    <label class="field">
      <span>BFT ID</span>
      <input
        v-model="bftId"
        placeholder="Например, BFT-12345"
        :disabled="loading"
        required
      />
    </label>

    <label class="field">
      <span>Текст требования</span>
      <textarea
        v-model="text"
        rows="12"
        placeholder="Опишите обработку события, взаимодействие систем..."
        :disabled="loading"
        required
      />
    </label>

    <footer class="form-footer">
      <button type="submit" :disabled="submitDisabled">
        {{ loading ? "Обработка..." : "Запустить анализ" }}
      </button>
    </footer>
  </form>
</template>

<style scoped>
.form-card {
  display: grid;
  gap: 18px;
}
.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.field {
  display: grid;
  gap: 8px;
}
.field span {
  font-weight: 600;
  color: rgba(21, 31, 66, 0.75);
}
input,
textarea {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid rgba(40, 62, 100, 0.14);
  background: rgba(255, 255, 255, 0.9);
  font-family: inherit;
}
textarea {
  resize: vertical;
}
.form-footer {
  display: flex;
  justify-content: flex-end;
}
button[type="submit"] {
  border: none;
  border-radius: 12px;
  padding: 14px 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #1f6feb, #6c5ce7);
  color: white;
  cursor: pointer;
  transition: transform 0.1s ease, box-shadow 0.2s ease;
}
button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
button[type="submit"]:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 18px 40px rgba(45, 84, 207, 0.25);
}
.ghost-button {
  border: 1px solid rgba(31, 111, 235, 0.26);
  border-radius: 12px;
  padding: 9px 16px;
  background: transparent;
  color: #1f6feb;
  font-weight: 600;
  cursor: pointer;
}
.ghost-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>