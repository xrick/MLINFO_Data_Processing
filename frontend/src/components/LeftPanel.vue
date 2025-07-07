<template>
    <div class="panel">
      <h2>自動處理區</h2>
      <div class="input-area">
        <textarea placeholder="Paste text here or upload a file..." @input="onTextInput" :value="textValue"></textarea>
      </div>
      <div class="rules-area">
        <h4>規則擴充</h4>
        <button @click="triggerRuleUpload">載入規則 (JSON)</button>
        <input type="file" ref="ruleUploader" @change="handleRuleUpload" accept=".json" style="display: none;" />
        <textarea v-model="tempRegex" placeholder="Enter temporary regex, one per line"></textarea>
      </div>
      <div class="actions">
        <button @click="startProcessing" class="primary">開始處理</button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  const emit = defineEmits(['process', 'update:rawText']);
  
  const textValue = ref('');
  const customRules = ref(null);
  const tempRegex = ref('');
  const ruleUploader = ref(null);
  
  const onTextInput = (event) => {
      textValue.value = event.target.value;
      emit('update:rawText', event.target.value);
  }
  
  const triggerRuleUpload = () => {
      ruleUploader.value.click();
  };
  
  const handleRuleUpload = (event) => {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
          try {
              customRules.value = JSON.parse(e.target.result);
              alert('Rules loaded successfully!');
          } catch (error) {
              alert('Failed to parse JSON rules.');
          }
      };
      reader.readAsText(file);
  };
  
  const startProcessing = () => {
      emit('process', {
          customRules: customRules.value,
          tempRegex: tempRegex.value.split('\n').filter(r => r.trim() !== ''),
      });
  };
  </script>
  
  <style scoped>
  .panel { display: flex; flex-direction: column; gap: 15px; background: var(--color-surface); padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  textarea { width: 100%; box-sizing: border-box; padding: 8px; border-radius: 4px; border: 1px solid var(--color-border); }
  .input-area textarea { min-height: 200px; }
  .rules-area textarea { min-height: 80px; }
  .actions { display: flex; justify-content: flex-end; }
  </style>