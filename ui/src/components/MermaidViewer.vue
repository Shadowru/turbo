<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import mermaid from "mermaid";

const props = defineProps<{
  chart: string;
}>();

const html = ref<string>("");

const renderMermaid = async () => {
  try {
    const chartId = `mermaid-${crypto.randomUUID?.() ?? Math.random().toString(36).slice(2)}`;
    const { svg } = await mermaid.render(chartId, props.chart);
    html.value = svg;
  } catch (err) {
    html.value = `<pre class="error">Ошибка рендеринга Mermaid:\\n${String(err)}</pre>`;
  }
};

mermaid.initialize({
  startOnLoad: false,
  theme: "default",
  securityLevel: "loose",
});

watch(
  () => props.chart,
  () => {
    renderMermaid();
  },
  { immediate: true }
);

onMounted(() => {
  renderMermaid();
});
</script>

<template>
  <div class="mermaid-container" v-html="html" />
</template>