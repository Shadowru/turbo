<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";
import MermaidViewer from "./MermaidViewer.vue";

type ApiResponse = {
  bft_id: string;
  structured_output: Record<string, unknown>;
  artifacts: Record<string, unknown>;
};

type Props = {
  loading: boolean;
  error: string | null;
  result: ApiResponse | null;
};

type SolutionDetail = {
  label: string;
  items: string[];
};

type EnhancedSolutionOption = {
  id: string;
  description: string;
  details: SolutionDetail[];
};

const props = defineProps<Props>();

const activeTab = ref("architecture");
const exporting = ref(false);
const resultContainer = ref<HTMLElement | null>(null);

const architectureAnalysis = computed(() => {
  const data = props.result?.structured_output?.architecture_analysis;
  return (data ?? null) as Record<string, any> | null;
});

const involvedSystems = computed(() => {
  const systems = props.result?.structured_output?.involved_systems;
  return Array.isArray(systems) ? (systems as Array<Record<string, any>>) : [];
});

const integrationTopics = computed(() => {
  const topics = props.result?.structured_output?.integration_topics;
  return Array.isArray(topics) ? (topics as Array<Record<string, any>>) : [];
});

const functionalBlocks = computed(
  () => architectureAnalysis.value?.functional_blocks ?? [],
);

const riskList = computed(() => {
  const risks = architectureAnalysis.value?.risks;
  if (Array.isArray(risks)) return risks;
  if (typeof risks === "string") return [risks];
  return [];
});

const dependencies = computed(() => {
  const deps = architectureAnalysis.value?.dependencies;
  if (Array.isArray(deps)) return deps;
  if (typeof deps === "string") return [deps];
  return [];
});

const NON_FUNCTIONAL_LABELS: Record<
  string,
  { label: string; icon: string }
> = {
  performance: { label: "Производительность", icon: "⚡" },
  scalability: { label: "Масштабируемость", icon: "📈" },
  security: { label: "Безопасность", icon: "🔒" },
  availability: { label: "Доступность", icon: "🟢" },
  reliability: { label: "Надёжность", icon: "🛡️" },
  maintainability: { label: "Сопровождаемость", icon: "🛠️" },
};

const nonFunctionalCards = computed(() => {
  const entries =
    (architectureAnalysis.value?.non_functional as Record<string, string>) ?? {};
  return Object.entries(entries).map(([key, value]) => ({
    key,
    icon: NON_FUNCTIONAL_LABELS[key]?.icon ?? "✨",
    label: NON_FUNCTIONAL_LABELS[key]?.label ?? key,
    value,
  }));
});

const umlDiagrams = computed(() => {
  const artifactsUml = props.result?.artifacts?.uml;
  if (Array.isArray(artifactsUml)) {
    return artifactsUml as Array<{ type: string; mermaid: string; description?: string }>;
  }
  const structured = props.result?.structured_output?.uml_diagrams;
  if (Array.isArray(structured)) {
    return structured.map((diagram: any) => ({
      type: diagram.type ?? "sequence",
      mermaid: diagram.mermaid ?? "",
      description: diagram.description,
    }));
  }
  return [];
});

const rawJson = computed(() => {
  const structured = props.result?.structured_output ?? null;
  if (!structured) return "";
  return JSON.stringify(structured, null, 2);
});

const summaryStats = computed(() => [
  {
    id: "blocks",
    icon: "🧩",
    label: "Функциональные блоки",
    value: functionalBlocks.value.length,
  },
  {
    id: "systems",
    icon: "🛰️",
    label: "Задействованные системы",
    value: involvedSystems.value.length,
  },
  {
    id: "topics",
    icon: "🔁",
    label: "Интеграционные топики",
    value: integrationTopics.value.length,
  },
]);

const solutionOptions = computed(() => {
  const options = architectureAnalysis.value?.solution_options;
  return Array.isArray(options) ? options : [];
});

const enhancedSolutionOptions = computed<EnhancedSolutionOption[]>(() => {
  return solutionOptions.value.map((option: any, idx: number) => {
    const id = typeof option?.id === "string" ? option.id : `option-${idx + 1}`;

    const description =
      typeof option?.description === "string"
        ? option.description
        : Array.isArray(option?.description)
        ? option.description.join(", ")
        : option?.description
        ? JSON.stringify(option.description, null, 2)
        : "Описание отсутствует.";

    const detailEntries = Object.entries(option ?? {}).filter(
      ([key]) => !["id", "description"].includes(key),
    );

    const details: SolutionDetail[] = detailEntries.map(([rawKey, value]) => ({
      label: formatLabel(rawKey),
      items: normalizeValue(value),
    }));

    return { id, description, details };
  });
});

const selectedOptionId = computed(
  () => architectureAnalysis.value?.selected_option || null,
);

const selectedOption = computed(() => {
  if (!selectedOptionId.value) return null;
  return enhancedSolutionOptions.value.find(
    (option) => option.id === selectedOptionId.value,
  );
});

function formatLabel(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/\b\w/g, (s) => s.toUpperCase());
}

function normalizeValue(value: unknown): string[] {
  if (value === null || value === undefined) return ["—"];
  if (typeof value === "string") return [value];
  if (typeof value === "number" || typeof value === "boolean") return [String(value)];
  if (Array.isArray(value)) {
    return value.flatMap((item) => normalizeValue(item));
  }
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>).map(
      ([k, v]) => `${formatLabel(k)}: ${normalizeValue(v).join(", ")}`,
    );
  }
  return [JSON.stringify(value, null, 2)];
}

const tabs = computed(() => [
  { id: "architecture", label: "Архитектурный анализ" },
  { id: "systems", label: "Задействованные системы" },
  { id: "topics", label: "Интеграционные топики" },
  { id: "uml", label: "Диаграммы" },
  { id: "raw", label: "Raw JSON" },
]);

const switchTab = (tabId: string) => {
  activeTab.value = tabId;
  nextTick(() => {
    document.querySelector(".sticky-tabs")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  });
};

const exportToPdf = async () => {
  if (!props.result || !resultContainer.value) return;

  exporting.value = true;
  try {
    const canvas = await html2canvas(resultContainer.value, {
      scale: 2,
      backgroundColor: "#ffffff",
    });
    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "mm", "a4");

    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    const imgWidth = pdfWidth;
    const imgHeight = (canvas.height * pdfWidth) / canvas.width;

    let position = 0;
    let heightLeft = imgHeight;

    pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
    heightLeft -= pdfHeight;

    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
      heightLeft -= pdfHeight;
    }

    const fileName = `${props.result.bft_id || "bft-analysis"}.pdf`;
    pdf.save(fileName);
  } catch (err) {
    console.error("PDF export error:", err);
    alert("Не удалось сформировать PDF. Подробности в консоли.");
  } finally {
    exporting.value = false;
  }
};

watch(
  () => props.result,
  async (value) => {
    if (value) {
      activeTab.value = "architecture";
      await nextTick();
      resultContainer.value?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  },
  { immediate: false },
);
</script>

<template>
  <div class="panel results-panel">
    <div class="panel-header">
      <h2>Результаты</h2>
      <button
        v-if="result"
        class="ghost-button"
        :disabled="exporting"
        @click="exportToPdf"
      >
        {{ exporting ? "Формирование PDF..." : "Скачать PDF" }}
      </button>
    </div>

    <p v-if="loading" class="muted">Запрос выполняется...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="!result" class="muted">Нет данных — выполните анализ.</p>

    <div v-else class="result-body" ref="resultContainer">
      <section class="hero-card">
        <div class="hero-meta">
          <span class="hero-badge">BFT ID — {{ result?.bft_id || "—" }}</span>
          <h3>Архитектурный обзор</h3>
          <p>
            {{ architectureAnalysis?.business_context || "Описание недоступно." }}
          </p>
        </div>
        <div class="summary-grid">
          <article
            v-for="stat in summaryStats"
            :key="stat.id"
            class="summary-card"
          >
            <span class="icon-bubble">{{ stat.icon }}</span>
            <div>
              <span class="summary-value">{{ stat.value }}</span>
              <p>{{ stat.label }}</p>
            </div>
          </article>
        </div>
      </section>

      <div class="sticky-tabs">
        <div class="tab-bar" role="tablist">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="tab-button"
            :class="{ active: tab.id === activeTab }"
            role="tab"
            :aria-selected="tab.id === activeTab"
            @click="switchTab(tab.id)"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <div class="tab-content">
        <!-- ARCHITECTURE -->
        <section v-if="activeTab === 'architecture'" class="architecture-layout">
          <article v-if="functionalBlocks.length" class="card">
            <header class="card-header">
              <span class="icon-circle">🧩</span>
              <div>
                <h4>Функциональные блоки</h4>
                <p>Состав решения</p>
              </div>
            </header>
            <ul class="chip-grid">
              <li
                v-for="block in functionalBlocks"
                :key="block"
                class="chip chip-primary"
              >
                {{ block }}
              </li>
            </ul>
          </article>

          <article v-if="nonFunctionalCards.length" class="card">
            <header class="card-header">
              <span class="icon-circle">🎯</span>
              <div>
                <h4>Нефункциональные требования</h4>
                <p>Ключевые ограничения</p>
              </div>
            </header>
            <div class="card-grid">
              <div v-for="item in nonFunctionalCards" :key="item.key" class="metric-card">
                <span class="metric-icon">{{ item.icon }}</span>
                <div>
                  <strong>{{ item.label }}</strong>
                  <p>{{ item.value }}</p>
                </div>
              </div>
            </div>
          </article>

          <article v-if="enhancedSolutionOptions.length" class="card">
            <header class="card-header">
              <span class="icon-circle">🛠️</span>
              <div>
                <h4>Варианты решения</h4>
                <p>Оценённые альтернативы</p>
              </div>
            </header>
            <div class="options-grid">
              <div
                v-for="option in enhancedSolutionOptions"
                :key="option.id"
                class="option-card"
                :class="{ selected: option.id === selectedOptionId }"
              >
                <span class="option-id">{{ option.id }}</span>
                <p>{{ option.description }}</p>

                <dl v-if="option.details.length" class="detail-list">
                  <div v-for="detail in option.details" :key="detail.label" class="detail-item">
                    <dt>{{ detail.label }}</dt>
                    <dd>
                      <ul>
                        <li v-for="item in detail.items" :key="item">{{ item }}</li>
                      </ul>
                    </dd>
                  </div>
                </dl>

                <span
                  v-if="option.id === selectedOptionId"
                  class="option-badge"
                >
                  Выбранный вариант
                </span>
              </div>
            </div>
          </article>

          <article
            v-if="selectedOption"
            class="card highlight-card"
          >
            <header class="card-header">
              <span class="icon-circle accent">✅</span>
              <div>
                <h4>Итоговое решение</h4>
                <p>{{ selectedOption.description }}</p>
              </div>
            </header>
            <div v-if="selectedOption.details.length" class="detail-grid">
              <article
                v-for="detail in selectedOption.details"
                :key="detail.label"
                class="detail-card"
              >
                <h5>{{ detail.label }}</h5>
                <ul>
                  <li v-for="item in detail.items" :key="item">{{ item }}</li>
                </ul>
              </article>
            </div>
          </article>

          <article v-if="riskList.length" class="card">
            <header class="card-header">
              <span class="icon-circle warning">⚠️</span>
              <div>
                <h4>Риски</h4>
                <p>На что обратить внимание</p>
              </div>
            </header>
            <ul class="ordered-list">
              <li v-for="(risk, idx) in riskList" :key="idx">{{ risk }}</li>
            </ul>
          </article>

          <article v-if="dependencies.length" class="card">
            <header class="card-header">
              <span class="icon-circle neutral">🔗</span>
              <div>
                <h4>Зависимости</h4>
                <p>Критичные внешние зависимости</p>
              </div>
            </header>
            <ul class="chip-grid">
              <li
                v-for="dep in dependencies"
                :key="dep"
                class="chip chip-neutral"
              >
                {{ dep }}
              </li>
            </ul>
          </article>

          <p v-if="!architectureAnalysis" class="muted centered">
            Структура архитектурного анализа отсутствует.
          </p>
        </section>

        <!-- SYSTEMS -->
        <section v-else-if="activeTab === 'systems'">
          <div v-if="involvedSystems.length" class="glass-table">
            <table>
              <thead>
                <tr>
                  <th>System ID</th>
                  <th>Роль</th>
                  <th>Статус</th>
                  <th>Confidence</th>
                  <th>Примечания</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="system in involvedSystems"
                  :key="system.system_id ?? system.role"
                >
                  <td>
                    <span class="tag">{{ system.system_id || "—" }}</span>
                  </td>
                  <td>{{ system.role || "—" }}</td>
                  <td>
                    <span
                      class="status-pill"
                      :class="{ success: system.existing, warning: !system.existing }"
                    >
                      {{ system.existing ? "Существующая" : "Новая" }}
                    </span>
                  </td>
                  <td>
                    {{
                      system.confidence !== undefined
                        ? (Number(system.confidence) * 100).toFixed(0) + "%"
                        : "—"
                    }}
                  </td>
                  <td>{{ system.notes || "—" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="muted centered">Системы не найдены.</p>
        </section>

        <!-- TOPICS -->
        <section v-else-if="activeTab === 'topics'">
          <div v-if="integrationTopics.length" class="glass-table">
            <table>
              <thead>
                <tr>
                  <th>Topic</th>
                  <th>Статус</th>
                  <th>Publisher</th>
                  <th>Subscriber</th>
                  <th>Schema</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="topic in integrationTopics"
                  :key="topic.topic ?? topic.publisher"
                >
                  <td>
                    <span class="tag tag-topic">{{ topic.topic || "—" }}</span>
                  </td>
                  <td>
                    <span
                      class="status-pill"
                      :class="{
                        success: topic.status === 'existing',
                        info: topic.status !== 'existing',
                      }"
                    >
                      {{ topic.status || "—" }}
                    </span>
                  </td>
                  <td>{{ topic.publisher || "—" }}</td>
                  <td>
                    <ul class="compact-list">
                      <li
                        v-for="subscriber in topic.subscriber ?? []"
                        :key="subscriber"
                      >
                        {{ subscriber }}
                      </li>
                    </ul>
                  </td>
                  <td>{{ topic.payload_schema_ref || "—" }}</td>
                  <td>
                    <ul class="compact-list">
                      <li v-for="action in topic.actions ?? []" :key="action">
                        {{ action }}
                      </li>
                    </ul>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="muted centered">Топики не найдены.</p>
        </section>

        <!-- UML -->
        <section v-else-if="activeTab === 'uml'">
          <div v-if="umlDiagrams.length" class="uml-grid">
            <article v-for="(diagram, idx) in umlDiagrams" :key="idx" class="uml-block">
              <header class="uml-header">
                <span class="tag tag-uml">{{ diagram.type.toUpperCase() }}</span>
                <p v-if="diagram.description" class="muted">
                  {{ diagram.description }}
                </p>
              </header>
              <MermaidViewer :chart="diagram.mermaid" />
            </article>
          </div>
          <p v-else class="muted centered">Диаграммы отсутствуют.</p>
        </section>

        <!-- RAW JSON -->
        <section v-else>
          <pre>{{ rawJson }}</pre>
        </section>
      </div>
    </div>
  </div>
</template>