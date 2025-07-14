document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    let state = {
        customRules: null,
        tableData: [],
    };

    // --- DOM ELEMENTS ---
    const csvUploader = document.getElementById('csv-uploader');
    const tableContainer = document.getElementById('table-container');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingMessage = document.getElementById('loading-message');
    const filePathDisplay = document.getElementById('file-path-display');
    const filePathText = document.getElementById('file-path-text');

    // --- BUTTONS ---
    const importCsvBtn = document.getElementById('import-csv-btn');
    const exportCsvBtn = document.getElementById('export-csv-btn');
    const ingestDbBtn = document.getElementById('ingest-db-btn');

    // --- API CONFIG ---
    const API_BASE_URL = 'http://localhost:8000';

    // --- HELPER FUNCTIONS ---
    const showLoading = (message) => {
        loadingMessage.textContent = message;
        loadingOverlay.classList.remove('hidden');
    };
    const hideLoading = () => {
        loadingOverlay.classList.add('hidden');
    };
    
    const showFilePath = (filePath) => {
        filePathText.textContent = filePath;
        filePathDisplay.classList.remove('hidden');
    };
    
    const hideFilePath = () => {
        filePathDisplay.classList.add('hidden');
        filePathText.textContent = '';
    };

    const renderTable = () => {
        if (state.tableData.length === 0) {
            tableContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📊</div>
                    <h3>尚未載入資料</h3>
                    <p>請使用下方的「匯入 CSV」按鈕載入筆電規格資料</p>
                </div>
            `;
            return;
        }

        const headers = Object.keys(state.tableData[0]);
        const table = document.createElement('table');
        const thead = table.createTHead();
        const headerRow = thead.insertRow();
        headers.forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText;
            headerRow.appendChild(th);
        });

        const tbody = table.createTBody();
        state.tableData.forEach((rowData, rowIndex) => {
            const row = tbody.insertRow();
            headers.forEach(header => {
                const cell = row.insertCell();
                const input = document.createElement('input');
                input.type = 'text';
                input.value = rowData[header] || '';
                input.addEventListener('change', (e) => {
                    state.tableData[rowIndex][header] = e.target.value;
                });
                cell.appendChild(input);
            });
        });

        tableContainer.innerHTML = '';
        tableContainer.appendChild(table);
    };
    
    // --- EVENT LISTENERS ---

    // CSV Import and Parse Button
    importCsvBtn.addEventListener('click', () => csvUploader.click());
    csvUploader.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        console.log('CSV file selected:', file.name, 'Size:', file.size, 'Type:', file.type);
        
        // 顯示檔案路徑
        showFilePath(file.name);
        
        try {
            // 顯示載入狀態
            showLoading('正在解析 CSV 檔案...');
            
            // 讀取檔案內容
            const fileContent = await readFileAsText(file);
            
            // 呼叫後端 API 進行解析
            const response = await fetch(`${API_BASE_URL}/api/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text_content: fileContent,
                    custom_rules: state.customRules,
                    temp_regex: null,
                    file_name: file.name
                }),
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            
            if (!result.data || result.data.length === 0) {
                throw new Error('解析結果為空，請檢查 CSV 檔案格式');
            }
            
            // 處理需用戶輸入 modeltype 的情境
            if (result.require_modeltype_input) {
                let userModeltype = prompt('無法自動判斷型號，請輸入 modeltype（如 960、928...）：');
                if (!userModeltype || !userModeltype.trim()) {
                    alert('必須輸入 modeltype！');
                    hideFilePath();
                    hideLoading();
                    return;
                }
                // 再次呼叫 API，補送 user_modeltype
                const retryResponse = await fetch(`${API_BASE_URL}/api/process`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text_content: fileContent,
                        custom_rules: state.customRules,
                        temp_regex: null,
                        file_name: file.name,
                        user_modeltype: userModeltype.trim()
                    }),
                });
                const retryResult = await retryResponse.json();
                if (!retryResult.data || retryResult.data.length === 0) {
                    throw new Error('解析結果為空，請檢查 CSV 檔案格式');
                }
                state.tableData = retryResult.data;
                renderTable();
                alert(`CSV 解析成功！已處理 ${retryResult.data.length} 筆記錄`);
                hideLoading();
                return;
            }
            
            // 更新狀態和顯示
            state.tableData = result.data;
            renderTable();
            
            console.log(`CSV 解析完成：${result.data.length} 筆記錄`);
            alert(`CSV 解析成功！已處理 ${result.data.length} 筆記錄`);
            
        } catch (error) {
            console.error('CSV 處理失敗:', error);
            alert(`CSV 處理失敗: ${error.message}`);
            hideFilePath(); // 隱藏檔案路徑
        } finally {
            hideLoading();
            event.target.value = ''; // 清除檔案選擇
        }
    });
    
    // 讀取檔案內容的 helper function
    const readFileAsText = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('檔案讀取失敗'));
            reader.readAsText(file, 'UTF-8');
        });
    };

    // CSV Export Button
    exportCsvBtn.addEventListener('click', () => {
        if (state.tableData.length === 0) {
            alert('No data to export.');
            return;
        }
        const csv = Papa.unparse(state.tableData);
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.setAttribute('download', 'edited_data.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    // Ingest to DB Button
    ingestDbBtn.addEventListener('click', async () => {
        if (state.tableData.length === 0) {
            alert('No data to ingest.');
            return;
        }
        showLoading('Ingesting data into database...');
        try {
            const response = await fetch(`${API_BASE_URL}/api/ingest-to-db`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data: state.tableData }),
            });
            if (!response.ok) throw new Error((await response.json()).detail);
            const result = await response.json();
            alert(`${result.message}\nDuckDB rows added: ${result.duckdb_rows_added}\nMilvus entities added: ${result.milvus_entities_added}`);
        } catch (error) {
            alert(`Failed to ingest: ${error.message}`);
        } finally {
            hideLoading();
        }
    });
});