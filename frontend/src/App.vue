<template>
  <div class="app-container">
    <div class="loading-overlay" v-if="isLoading || isIngesting">
      <p>{{ loadingMessage }}</p>
    </div>
    <div class="panels-container">
      <LeftPanel @process="handleProcess" @update:rawText="updateText" />
      <RightPanel :table-data="tableData" @ingest="handleIngest" @update:tableData="updateTableData" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import LeftPanel from './components/LeftPanel.vue';
import RightPanel from './components/RightPanel.vue';
import { processText, ingestToDB } from './services/api.js';

const isLoading = ref(false);
const isIngesting = ref(false);
const loadingMessage = ref('');
const tableData = ref([]);
const rawText = ref('');

const updateText = (text) => {
  rawText.value = text;
}

const updateTableData = (data) => {
    tableData.value = data;
}

const handleProcess = async ({ customRules, tempRegex }) => {
  isLoading.value = true;
  loadingMessage.value = 'Processing data...';
  try {
    const response = await processText(rawText.value, customRules, tempRegex);
    if (response.error) {
      alert(`Error: ${response.error}`);
      tableData.value = [];
    } else {
      tableData.value = response.data;
    }
  } catch (error) {
    alert(`Failed to process: ${error.message}`);
  } finally {
    isLoading.value = false;
  }
};

const handleIngest = async (dataToIngest) => {
    isIngesting.value = true;
    loadingMessage.value = 'Ingesting data into database...';
    try {
        const response = await ingestToDB(dataToIngest);
        alert(`${response.message}\nDuckDB rows added: ${response.duckdb_rows_added}\nMilvus entities added: ${response.milvus_entities_added}`);
    } catch (error) {
        alert(`Failed to ingest: ${error.message}`);
    } finally {
        isIngesting.value = false;
    }
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
}
.panels-container {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
}
</style>