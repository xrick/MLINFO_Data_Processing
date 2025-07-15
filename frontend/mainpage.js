// 全域變數
let currentSection = 'chat';
let chatHistory = [];
let importedData = [];
let uploadedFiles = [];

// DOM 載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化應用程式
function initializeApp() {
    setupNavigation();
    setupChatInterface();
    setupDataImport();
    setupFileManagement();
    setupModals();
    loadInitialData();
}

// 設置導航功能
function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    
    navButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            switchSection(section);
            
            // 更新按鈕狀態
            navButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// 切換頁面區塊
function switchSection(sectionName) {
    // 隱藏所有區塊
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // 顯示目標區塊
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionName;
    }
}

// 設置聊天介面
function setupChatInterface() {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const questionBtns = document.querySelectorAll('.question-btn');
    
    // 發送按鈕事件
    sendBtn.addEventListener('click', sendMessage);
    
    // 輸入框回車事件
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // 預設問題按鈕事件
    questionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const question = this.textContent;
            chatInput.value = question;
            sendMessage();
        });
    });
}

// 發送訊息
async function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // 添加用戶訊息到聊天記錄
    addChatMessage(message, 'user');
    chatInput.value = '';
    
    // 顯示載入狀態
    const loadingMessage = addChatMessage('正在思考中...', 'bot', true);
    
    try {
        // 調用 SalesRAG API
        const response = await fetch('/api/chat-stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: message,
                service_name: 'sales_assistant'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // 處理流式回應
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedData = '';
        
        // 移除載入訊息
        loadingMessage.remove();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            accumulatedData += decoder.decode(value, { stream: true });
            const lines = accumulatedData.split('\n');
            accumulatedData = lines.pop(); // 保留不完整的行
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        displayChatResponse(data);
                    } catch (e) {
                        console.error('解析回應資料失敗:', e);
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('發送訊息失敗:', error);
        loadingMessage.remove();
        addChatMessage('抱歉，處理您的問題時發生錯誤。請稍後再試。', 'bot');
    }
}

// 添加聊天訊息
function addChatMessage(content, sender, isLoading = false) {
    const chatContainer = document.querySelector('.chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    if (isLoading) {
        messageContent.innerHTML = `<div class="loading"></div> ${content}`;
    } else {
        messageContent.textContent = content;
    }
    
    messageDiv.appendChild(messageContent);
    
    // 插入到預設問題之前
    const defaultQuestions = document.querySelector('.default-questions');
    chatContainer.insertBefore(messageDiv, defaultQuestions);
    
    // 滾動到底部
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

// 顯示聊天回應
function displayChatResponse(data) {
    const { answer_summary, comparison_table } = data;
    
    // 顯示文字回應
    if (answer_summary) {
        addChatMessage(answer_summary, 'bot');
    }
    
    // 顯示比較表格
    if (comparison_table && comparison_table.length > 0) {
        const tableHtml = generateComparisonTable(comparison_table);
        const tableDiv = document.createElement('div');
        tableDiv.className = 'chat-message bot-message';
        tableDiv.innerHTML = `
            <div class="message-content">
                <div class="comparison-table">
                    ${tableHtml}
                </div>
            </div>
        `;
        
        const chatContainer = document.querySelector('.chat-container');
        const defaultQuestions = document.querySelector('.default-questions');
        chatContainer.insertBefore(tableDiv, defaultQuestions);
    }
}

// 生成比較表格
function generateComparisonTable(tableData) {
    if (!tableData || tableData.length === 0) return '';
    
    const headers = Object.keys(tableData[0]);
    let tableHtml = '<table class="comparison-table">';
    
    // 表頭
    tableHtml += '<thead><tr>';
    headers.forEach(header => {
        tableHtml += `<th>${header}</th>`;
    });
    tableHtml += '</tr></thead>';
    
    // 表格內容
    tableHtml += '<tbody>';
    tableData.forEach(row => {
        tableHtml += '<tr>';
        headers.forEach(header => {
            tableHtml += `<td>${row[header] || ''}</td>`;
        });
        tableHtml += '</tr>';
    });
    tableHtml += '</tbody></table>';
    
    return tableHtml;
}

// 設置資料匯入功能
function setupDataImport() {
    const importBtn = document.getElementById('import-csv-btn');
    const exportBtn = document.getElementById('export-csv-btn');
    const clearBtn = document.getElementById('clear-data-btn');
    const importDbBtn = document.getElementById('import-db-btn');
    
    importBtn.addEventListener('click', showUploadModal);
    exportBtn.addEventListener('click', exportData);
    clearBtn.addEventListener('click', clearData);
    importDbBtn.addEventListener('click', importToDatabase);
}

// 顯示上傳模態框
function showUploadModal() {
    const modal = document.getElementById('upload-modal');
    modal.style.display = 'block';
}

// 設置模態框功能
function setupModals() {
    const modal = document.getElementById('upload-modal');
    const closeBtn = modal.querySelector('.close');
    const cancelBtn = document.getElementById('cancel-upload');
    const confirmBtn = document.getElementById('confirm-upload');
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    
    // 關閉模態框
    closeBtn.addEventListener('click', () => modal.style.display = 'none');
    cancelBtn.addEventListener('click', () => modal.style.display = 'none');
    
    // 點擊模態框外部關閉
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // 檔案上傳區域點擊
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // 拖拽上傳
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#667eea';
        uploadArea.style.backgroundColor = '#f0f4ff';
    });
    
    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#dee2e6';
        uploadArea.style.backgroundColor = 'white';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#dee2e6';
        uploadArea.style.backgroundColor = 'white';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
    
    // 檔案選擇
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
    
    // 確認上傳
    confirmBtn.addEventListener('click', processUploadedFile);
}

// 處理檔案上傳
function handleFileUpload(file) {
    if (!file.name.toLowerCase().endsWith('.csv')) {
        showAlert('請選擇 CSV 檔案', 'error');
        return;
    }
    
    // 顯示檔案資訊
    const uploadArea = document.getElementById('upload-area');
    uploadArea.innerHTML = `
        <i class="fas fa-file-csv"></i>
        <p>已選擇檔案: ${file.name}</p>
        <p>檔案大小: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
    `;
    
    // 儲存檔案參考
    window.uploadedFile = file;
}

// 處理上傳的檔案
async function processUploadedFile() {
    if (!window.uploadedFile) {
        showAlert('請先選擇檔案', 'error');
        return;
    }
    
    const modal = document.getElementById('upload-modal');
    const autoParse = document.getElementById('auto-parse').checked;
    const validateData = document.getElementById('validate-data').checked;
    
    try {
        // 顯示載入狀態
        showAlert('正在處理檔案...', 'info');
        
        // 讀取檔案內容
        const content = await readFileAsText(window.uploadedFile);
        
        // 調用後端 API 處理
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text_content: content,
                file_name: window.uploadedFile.name,
                custom_rules: null,
                temp_regex: null,
                user_modeltype: null
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.data) {
            importedData = result.data;
            displayImportedData(result.data);
            updateFileList(window.uploadedFile.name);
            showAlert('檔案處理成功！', 'success');
            modal.style.display = 'none';
        } else {
            throw new Error('處理結果為空');
        }
        
    } catch (error) {
        console.error('檔案處理失敗:', error);
        showAlert('檔案處理失敗: ' + error.message, 'error');
    }
}

// 讀取檔案為文字
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsText(file);
    });
}

// 顯示匯入的資料
function displayImportedData(data) {
    const emptyState = document.getElementById('empty-state');
    const dataTable = document.getElementById('data-table');
    const tableBody = document.getElementById('table-body');
    
    if (data.length === 0) {
        showAlert('沒有找到有效的資料', 'warning');
        return;
    }
    
    // 隱藏空狀態，顯示表格
    emptyState.style.display = 'none';
    dataTable.style.display = 'block';
    
    // 清空表格
    tableBody.innerHTML = '';
    
    // 添加資料行
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.modeltype || ''}</td>
            <td>${row.version || ''}</td>
            <td>${row.modelname || ''}</td>
            <td>${row.cpu || ''}</td>
            <td>${row.gpu || ''}</td>
            <td>${row.memory || ''}</td>
        `;
        tableBody.appendChild(tr);
    });
}

// 匯出資料
function exportData() {
    if (importedData.length === 0) {
        showAlert('沒有資料可以匯出', 'warning');
        return;
    }
    
    // 轉換為 CSV 格式
    const headers = Object.keys(importedData[0]);
    const csvContent = [
        headers.join(','),
        ...importedData.map(row => 
            headers.map(header => `"${row[header] || ''}"`).join(',')
        )
    ].join('\n');
    
    // 下載檔案
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'exported_data.csv';
    link.click();
    
    showAlert('資料匯出成功！', 'success');
}

// 清除資料
function clearData() {
    if (confirm('確定要清除所有資料嗎？')) {
        importedData = [];
        const emptyState = document.getElementById('empty-state');
        const dataTable = document.getElementById('data-table');
        
        emptyState.style.display = 'block';
        dataTable.style.display = 'none';
        
        showAlert('資料已清除', 'info');
    }
}

// 匯入資料庫
async function importToDatabase() {
    if (importedData.length === 0) {
        showAlert('沒有資料可以匯入資料庫', 'warning');
        return;
    }
    
    try {
        showAlert('正在匯入資料庫...', 'info');
        
        const response = await fetch('/api/ingest-to-db', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: importedData
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(`資料匯入成功！DuckDB: ${result.duckdb_rows_added} 行, Milvus: ${result.milvus_entities_added} 實體`, 'success');
        } else {
            throw new Error(result.message || '匯入失敗');
        }
        
    } catch (error) {
        console.error('資料庫匯入失敗:', error);
        showAlert('資料庫匯入失敗: ' + error.message, 'error');
    }
}

// 設置檔案管理功能
function setupFileManagement() {
    // 檔案操作按鈕事件
    document.querySelectorAll('.file-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.querySelector('i').className;
            const fileName = this.closest('.file-card').querySelector('h4').textContent;
            
            if (action.includes('eye')) {
                viewFile(fileName);
            } else if (action.includes('download')) {
                downloadFile(fileName);
            } else if (action.includes('trash')) {
                deleteFile(fileName);
            }
        });
    });
}

// 查看檔案
function viewFile(fileName) {
    showAlert(`查看檔案: ${fileName}`, 'info');
    // 這裡可以實現檔案預覽功能
}

// 下載檔案
function downloadFile(fileName) {
    showAlert(`下載檔案: ${fileName}`, 'info');
    // 這裡可以實現檔案下載功能
}

// 刪除檔案
function deleteFile(fileName) {
    if (confirm(`確定要刪除檔案 ${fileName} 嗎？`)) {
        showAlert(`檔案 ${fileName} 已刪除`, 'success');
        // 這裡可以實現檔案刪除功能
    }
}

// 更新檔案列表
function updateFileList(fileName) {
    const fileList = document.getElementById('imported-files');
    const li = document.createElement('li');
    li.innerHTML = `<i class="fas fa-file-csv"></i> ${fileName}`;
    fileList.appendChild(li);
    
    uploadedFiles.push(fileName);
}

// 載入初始資料
function loadInitialData() {
    // 這裡可以載入初始資料，例如已匯入的檔案列表
    console.log('應用程式初始化完成');
}

// 顯示提示訊息
function showAlert(message, type = 'info') {
    // 移除現有的提示
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // 創建新的提示
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-circle' : 
                 type === 'warning' ? 'exclamation-triangle' : 'info-circle';
    
    alert.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;
    
    // 插入到頁面頂部
    const mainContent = document.querySelector('.main-content');
    mainContent.insertBefore(alert, mainContent.firstChild);
    
    // 自動移除提示
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// 工具函數：格式化檔案大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 工具函數：格式化日期
function formatDate(date) {
    return new Date(date).toLocaleDateString('zh-TW');
}

// 全域錯誤處理
window.addEventListener('error', function(e) {
    console.error('全域錯誤:', e.error);
    showAlert('發生未預期的錯誤，請重新整理頁面', 'error');
});

// 未處理的 Promise 拒絕
window.addEventListener('unhandledrejection', function(e) {
    console.error('未處理的 Promise 拒絕:', e.reason);
    showAlert('網路請求失敗，請檢查連線狀態', 'error');
}); 