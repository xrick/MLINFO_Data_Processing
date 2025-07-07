<template>
    <div class="panel">
      <h2>手動編輯區</h2>
      <div class="table-container">
        <table v-if="localTableData.length > 0">
          <thead>
            <tr>
              <th v-for="(header, index) in headers" :key="index">{{ header }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in localTableData" :key="rowIndex">
              <td v-for="(header, colIndex) in headers" :key="colIndex">
                <input v-model="row[header]" @change="onCellChange" />
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else>No data to display. Process text on the left.</p>
      </div>
      <div class="actions">
          <button class="secondary" @click="triggerCsvUpload">匯入 CSV</button>
          <input type="file" ref="csvUploader" @change="handleCsvImport" accept=".csv" style="display: none;" />
          <button class="secondary" @click="handleCsvExport">匯出 CSV</button>
          <button class="primary" @click="ingestData">匯入資料庫</button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, watch } from 'vue';
  import { exportCSV, importCSV } from '../services/csvHandler.js';
  
  const props = defineProps({
    tableData: Array,
  });
  const emit = defineEmits(['ingest', 'update:tableData']);
  
  const localTableData = ref([]);
  const csvUploader = ref(null);
  
  watch(() => props.tableData, (newData) => {
      localTableData.value = JSON.parse(JSON.stringify(newData || []));
  }, { deep: true, immediate: true });
  
  const headers = computed(() => {
    if (localTableData.value.length === 0) return [];
    return Object.keys(localTableData.value[0]);
  });
  
  const triggerCsvUpload = () => {
      csvUploader.value.click();
  }
  
  const onCellChange = () => {
      emit('update:tableData', localTableData.value);
  };
  
  const handleCsvImport = async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      try {
          const data = await importCSV(file);
          localTableData.value = data;
          onCellChange(); // Propagate changes to parent
          alert('CSV imported successfully!');
      } catch (error) {
          alert('Failed to import CSV.');
      }
      event.target.value = ''; // Reset file input
  };
  
  const handleCsvExport = () => {
      exportCSV(localTableData.value, 'edited_data.csv');
  };
  
  const ingestData = () => {
      if (localTableData.value.length === 0) {
          alert('No data to ingest.');
          return;
      }
      emit('ingest', localTableData.value);
  };
  
  </script>
  
  <style scoped>
  .panel { display: flex; flex-direction: column; gap: 15px; background: var(--color-surface); padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  .table-container { overflow-x: auto; flex-grow: 1; }
  table { width: 100%; border-collapse: collapse; }
  th, td { border: 1px solid var(--color-border); padding: 8px; text-align: left; white-space: nowrap; }
  th { background-color: #fafafa; position: sticky; top: 0; z-index: 1; }
  input { width: 150px; border: none; background: transparent; padding: 0; }
  .actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 10px; }
  </style>