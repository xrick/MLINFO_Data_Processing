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

    // CSV Import Button
    importCsvBtn.addEventListener('click', () => csvUploader.click());
    csvUploader.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        console.log('CSV file selected:', file.name, 'Size:', file.size, 'Type:', file.type);
        
        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            encoding: 'UTF-8',
            complete: (results) => {
                console.log('CSV parse results:', results);
                
                if (results.errors && results.errors.length > 0) {
                    console.error('CSV parsing errors:', results.errors);
                    alert(`CSV parsing errors: ${results.errors.map(e => e.message).join(', ')}`);
                    return;
                }
                
                if (!results.data || results.data.length === 0) {
                    alert('CSV file appears to be empty or has no valid data rows.');
                    return;
                }
                
                // Filter out completely empty rows
                const filteredData = results.data.filter(row => {
                    return Object.values(row).some(value => value && value.trim() !== '');
                });
                
                console.log(`Filtered data: ${filteredData.length} rows from ${results.data.length} total`);
                
                if (filteredData.length === 0) {
                    alert('No valid data found in CSV file.');
                    return;
                }
                
                state.tableData = filteredData;
                renderTable();
                alert(`CSV imported successfully! Loaded ${filteredData.length} rows.`);
            },
            error: (error) => {
                console.error('CSV parsing error:', error);
                alert(`Failed to import CSV: ${error.message || 'Unknown error'}`);
            },
        });
        event.target.value = '';
    });

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