<script setup lang="ts">
import { ref } from "vue";

const INITIAL_SAMPLE = `БФТ: Клиент может обновлять контактные данные. Требуется отправлять событие ...`;

export type BftFormPayload = {
  bft_id: string;
  text: string;
};

const props = defineProps<{
  loading: boolean;
}>();

const emit = defineEmits<{
  submit: [payload: BftFormPayload];
}>();

const bftId = ref("BFT-001");
const text = ref(INITIAL_SAMPLE);

const submitForm = () => {
  emit("submit", {
    bft_id: bftId.value.trim(),
    text: text.value.trim(),
  });
};
</script>

<template>
  <form class="panel" @submit.prevent="submitForm">
    <h2>Анализ БФТ</h2>

    <label for="bftId">BFT ID</label>
    <input
      id="bftId"
      v-model="bftId"
      placeholder="BFT-12345"
      :disabled="loading"
      required
    />

    <label for="bftText">Текст требования</label>
    <textarea
      id="bftText"
      v-model="text"
      rows="10"
      placeholder="Опишите требование..."
      :disabled="loading"
      required
    />

    <button type="submit" :disabled="loading">
      {{ loading ? "Обработка..." : "Запустить анализ" }}
    </button>
  </form>
</template>