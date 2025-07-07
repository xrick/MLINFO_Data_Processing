document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    let state = {
        customRules: null,
        tableData: [],
    };

    // --- DOM ELEMENTS ---
    // Views and Tabs
    const loadFileTabBtn = document.getElementById('load-file-tab-btn');
    const pasteTextTabBtn = document.getElementById('paste-text-tab-btn');
    const fileUploadView = document.getElementById('file-upload-view');
    const pasteTextView = document.getElementById('paste-text-view');
    const fileDropZone = document.getElementById('file-drop-zone');
    
    // Inputs
    const textFileInput = document.getElementById('text-file-input');
    const textInput = document.getElementById('text-input'); // The main textarea
    const tempRegexInput = document.getElementById('temp-regex');
    const ruleUploader = document.getElementById('rule-uploader');
    const csvUploader = document.getElementById('csv-uploader');
    
    // Others
    const tableContainer = document.getElementById('table-container');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingMessage = document.getElementById('loading-message');

    // --- BUTTONS ---
    const loadRuleBtn = document.getElementById('load-rule-btn');
    const processBtn = document.getElementById('process-btn');
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
            tableContainer.innerHTML = '<p>No data to display. Process text on the left.</p>';
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
    
    const handleTextFile = (file) => {
        if (!file || !file.type.match('text.*')) {
            alert("Please select a valid text file (.txt).");
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
            textInput.value = e.target.result; // Put content into the textarea
            fileDropZone.querySelector('span').textContent = `Loaded: ${file.name}`;
            fileDropZone.classList.add('file-loaded');
        };
        reader.readAsText(file);
    };

    // --- EVENT LISTENERS ---
    
    // Tab switching logic
    loadFileTabBtn.addEventListener('click', () => {
        loadFileTabBtn.classList.add('active');
        pasteTextTabBtn.classList.remove('active');
        fileUploadView.classList.add('active');
        pasteTextView.classList.remove('active');
    });

    pasteTextTabBtn.addEventListener('click', () => {
        pasteTextTabBtn.classList.add('active');
        loadFileTabBtn.classList.remove('active');
        pasteTextView.classList.add('active');
        fileUploadView.classList.remove('active');
    });
    
    // File Drop Zone Logic
    fileDropZone.addEventListener('click', () => textFileInput.click());
    fileDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileDropZone.classList.add('dragover');
    });
    fileDropZone.addEventListener('dragleave', () => {
        fileDropZone.classList.remove('dragover');
    });
    fileDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        fileDropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleTextFile(e.dataTransfer.files[0]);
        }
    });
    textFileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleTextFile(e.target.files[0]);
        }
    });

    // Load Rules Button
    loadRuleBtn.addEventListener('click', () => ruleUploader.click());
    ruleUploader.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                state.customRules = JSON.parse(e.target.result);
                alert('Rules loaded successfully!');
            } catch (error) {
                alert('Failed to parse JSON rules.');
                state.customRules = null;
            }
        };
        reader.readAsText(file);
        event.target.value = '';
    });

    // Process Button
    processBtn.addEventListener('click', async () => {
        const textContent = textInput.value;
        const tempRegex = tempRegexInput.value.split('\n').filter(r => r.trim() !== '');
        if (!textContent.trim()) {
            alert('Text content is empty. Please paste text or upload a file.');
            return;
        }
        showLoading('Processing data...');
        try {
            const response = await fetch(`${API_BASE_URL}/api/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text_content: textContent,
                    custom_rules: state.customRules,
                    temp_regex: tempRegex,
                }),
            });
            if (!response.ok) throw new Error((await response.json()).detail);
            const result = await response.json();
            if (result.error) {
                alert(`Error: ${result.error}`);
                state.tableData = [];
            } else {
                state.tableData = result.data;
            }
            renderTable();
        } catch (error) {
            alert(`Failed to process: ${error.message}`);
        } finally {
            hideLoading();
        }
    });

    // CSV Import Button
    importCsvBtn.addEventListener('click', () => csvUploader.click());
    csvUploader.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (!file) return;
        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
                state.tableData = results.data;
                renderTable();
                alert('CSV imported successfully!');
            },
            error: () => alert('Failed to import CSV.'),
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