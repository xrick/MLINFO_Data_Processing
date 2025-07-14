// ===== PROTOTYPE APPLICATION LOGIC =====

document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    let state = {
        currentStep: 1,
        uploadedFiles: [],
        processedData: [],
        selectedFormat: null,
        isProcessing: false,
        dataQuality: {
            completeness: 93,
            accuracy: 84,
            performance: 'excellent'
        }
    };

    // --- DOM ELEMENTS ---
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const selectFilesBtn = document.getElementById('select-files');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingMessage = document.getElementById('loading-message');
    const successToast = document.getElementById('success-toast');
    const prototypeTable = document.getElementById('prototype-table');

    // --- NAVIGATION ---
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Simulate navigation (in real app would change views)
            showToast('功能切換成功！這是 prototype 展示。');
        });
    });

    // --- UPLOAD FUNCTIONALITY ---
    
    // File selection button
    selectFilesBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // Upload area click
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop functionality
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        handleFileUpload(files);
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFileUpload(files);
    });

    // --- FILE HANDLING ---
    function handleFileUpload(files) {
        if (files.length === 0) return;

        showLoading('正在上傳檔案...');
        
        // Simulate file upload process
        setTimeout(() => {
            state.uploadedFiles = files;
            processFiles(files);
        }, 1500);
    }

    function processFiles(files) {
        showLoading('正在解析檔案...');
        
        // Simulate file processing
        setTimeout(() => {
            // Mock processed data based on file type
            const mockData = generateMockData(files);
            state.processedData = mockData;
            
            // Update table with processed data
            updateTable(mockData);
            
            hideLoading();
            showToast(`成功處理 ${files.length} 個檔案，解析出 ${mockData.length} 筆記錄！`);
            
            // Update quality metrics
            updateQualityMetrics();
            
        }, 2000);
    }

    function generateMockData(files) {
        const models = ['APX938', 'ARB938', 'AHP938U', 'AKK938', 'AMD958', 'BCX720'];
        const cpus = ['AMD Ryzen 5', 'AMD Ryzen 7', 'Intel Core i5', 'Intel Core i7', 'Intel Core i9'];
        const gpus = ['Radeon Graphics', 'NVIDIA RTX 3060', 'NVIDIA RTX 4070', 'Intel Iris'];
        const memories = ['8GB DDR4', '16GB DDR4', '32GB DDR4', '16GB DDR5', '32GB DDR5'];
        const storages = ['256GB SSD', '512GB SSD', '1TB SSD', '2TB SSD'];

        const mockData = [];
        const recordCount = Math.floor(Math.random() * 50) + 10; // 10-60 records

        for (let i = 0; i < recordCount; i++) {
            mockData.push({
                modeltype: '938',
                version: `${['MP', 'PVT', 'EVT'][Math.floor(Math.random() * 3)]}_v${Math.floor(Math.random() * 5) + 1}.${Math.floor(Math.random() * 10)}`,
                modelname: models[Math.floor(Math.random() * models.length)],
                cpu: cpus[Math.floor(Math.random() * cpus.length)],
                gpu: gpus[Math.floor(Math.random() * gpus.length)],
                memory: memories[Math.floor(Math.random() * memories.length)],
                storage: storages[Math.floor(Math.random() * storages.length)]
            });
        }

        return mockData;
    }

    // --- TABLE FUNCTIONALITY ---
    function updateTable(data) {
        const tbody = prototypeTable.querySelector('tbody');
        tbody.innerHTML = '';

        data.forEach((row, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><input type="checkbox" data-index="${index}"></td>
                <td><span class="badge badge-primary">${row.modeltype}</span></td>
                <td>${row.version}</td>
                <td>${row.modelname}</td>
                <td>${row.cpu}</td>
                <td>${row.gpu}</td>
                <td>${row.memory}</td>
                <td>${row.storage}</td>
                <td>
                    <button class="btn-icon" title="編輯" onclick="editRecord(${index})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" title="刪除" onclick="deleteRecord(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Update record count
        const recordCountElement = document.querySelector('.record-count');
        if (recordCountElement) {
            recordCountElement.innerHTML = `總計 <strong>${data.length}</strong> 筆記錄`;
        }

        // Update pagination info
        const paginationInfo = document.querySelector('.pagination-info');
        if (paginationInfo) {
            paginationInfo.textContent = `顯示 1-${Math.min(data.length, 3)} 筆，共 ${data.length} 筆記錄`;
        }
    }

    // --- TABLE ACTIONS ---
    window.editRecord = function(index) {
        showToast(`編輯記錄 #${index + 1} (Prototype 功能)`);
    };

    window.deleteRecord = function(index) {
        if (confirm('確定要刪除這筆記錄嗎？')) {
            state.processedData.splice(index, 1);
            updateTable(state.processedData);
            showToast('記錄已刪除');
            updateQualityMetrics();
        }
    };

    // --- TABLE CONTROLS ---
    document.getElementById('filter-btn')?.addEventListener('click', () => {
        showToast('篩選功能 (Prototype)');
    });

    document.getElementById('sort-btn')?.addEventListener('click', () => {
        showToast('排序功能 (Prototype)');
    });

    document.getElementById('search-btn')?.addEventListener('click', () => {
        showToast('搜尋功能 (Prototype)');
    });

    // Select all checkbox
    document.getElementById('select-all')?.addEventListener('change', (e) => {
        const checkboxes = document.querySelectorAll('tbody input[type=\"checkbox\"]');
        checkboxes.forEach(cb => cb.checked = e.target.checked);
        
        const selectedCount = e.target.checked ? checkboxes.length : 0;
        showToast(`${selectedCount} 筆記錄已${e.target.checked ? '選取' : '取消選取'}`);
    });

    // --- EXPORT FUNCTIONALITY ---
    document.getElementById('import-database')?.addEventListener('click', () => {
        if (state.processedData.length === 0) {
            showToast('沒有資料可以匯入');
            return;
        }

        showLoading('正在匯入資料庫...');
        
        // Simulate database import
        setTimeout(() => {
            hideLoading();
            showToast(`成功匯入 ${state.processedData.length} 筆記錄到資料庫！`);
            updateQualityMetrics();
        }, 3000);
    });

    document.getElementById('export-csv')?.addEventListener('click', () => {
        if (state.processedData.length === 0) {
            showToast('沒有資料可以匯出');
            return;
        }

        // Simulate CSV export
        const csv = convertToCSV(state.processedData);
        downloadFile('exported_data.csv', csv, 'text/csv');
        showToast('CSV 檔案下載完成！');
    });

    document.getElementById('refresh-data')?.addEventListener('click', () => {
        showLoading('正在重新整理資料...');
        
        setTimeout(() => {
            hideLoading();
            showToast('資料已重新整理');
            updateQualityMetrics();
        }, 1500);
    });

    // --- HERO ACTIONS ---
    document.getElementById('start-processing')?.addEventListener('click', () => {
        // Scroll to upload section
        document.querySelector('.workflow-section').scrollIntoView({ 
            behavior: 'smooth' 
        });
        showToast('開始使用！請上傳您的檔案。');
    });

    document.getElementById('learn-more')?.addEventListener('click', () => {
        showToast('了解更多功能 (Prototype)');
    });

    // --- UTILITY FUNCTIONS ---
    function showLoading(message = '處理中...') {
        loadingMessage.textContent = message;
        loadingOverlay.classList.remove('hidden');
    }

    function hideLoading() {
        loadingOverlay.classList.add('hidden');
    }

    function showToast(message, type = 'success') {
        const toast = successToast;
        const span = toast.querySelector('span');
        span.textContent = message;
        
        toast.classList.remove('hidden');
        
        // Auto hide after 3 seconds
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    function convertToCSV(data) {
        if (data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
        ].join('\\n');
        
        return csvContent;
    }

    function downloadFile(filename, content, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    function updateQualityMetrics() {
        // Update progress circles based on data
        const dataCount = state.processedData.length;
        const completeness = Math.max(85, Math.min(98, 90 + Math.floor(dataCount / 10)));
        const accuracy = Math.max(80, Math.min(95, 85 + Math.floor(dataCount / 20)));
        
        state.dataQuality.completeness = completeness;
        state.dataQuality.accuracy = accuracy;

        // Update DOM elements
        const progressCircles = document.querySelectorAll('.progress-circle');
        progressCircles.forEach((circle, index) => {
            const value = index === 0 ? completeness : accuracy;
            circle.style.setProperty('--progress', value);
            const textElement = circle.querySelector('.progress-text');
            if (textElement) {
                textElement.textContent = `${value}%`;
            }
        });

        // Update metrics
        updateMetricValues();
    }

    function updateMetricValues() {
        const dataCount = state.processedData.length;
        const completeRecords = Math.floor(dataCount * state.dataQuality.completeness / 100);
        const validRecords = Math.floor(dataCount * state.dataQuality.accuracy / 100);
        
        // Update completeness metrics
        const completenessCard = document.querySelectorAll('.dashboard-card')[0];
        if (completenessCard) {
            const metrics = completenessCard.querySelectorAll('.metric-value');
            if (metrics[0]) metrics[0].textContent = `${completeRecords} 筆`;
            if (metrics[1]) metrics[1].textContent = `${dataCount - completeRecords} 筆`;
        }

        // Update accuracy metrics
        const accuracyCard = document.querySelectorAll('.dashboard-card')[1];
        if (accuracyCard) {
            const metrics = accuracyCard.querySelectorAll('.metric-value');
            if (metrics[0]) metrics[0].textContent = `${validRecords} 筆`;
            if (metrics[1]) metrics[1].textContent = `${dataCount - validRecords} 筆`;
        }

        // Update performance metrics
        const performanceCard = document.querySelectorAll('.dashboard-card')[2];
        if (performanceCard) {
            const metrics = performanceCard.querySelectorAll('.metric-value');
            const avgTime = (2.3 + Math.random() * 0.8).toFixed(1);
            const throughput = Math.floor(600 + Math.random() * 200);
            if (metrics[0]) metrics[0].textContent = `${avgTime} 秒`;
            if (metrics[1]) metrics[1].textContent = `${throughput} 記錄/分鐘`;
        }
    }

    // --- PAGINATION ---
    const paginationButtons = document.querySelectorAll('.btn-page');
    paginationButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            paginationButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            showToast(`切換到第 ${btn.textContent} 頁`);
        });
    });

    // --- CHART CONTROLS ---
    const chartButtons = document.querySelectorAll('.btn-chart');
    chartButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            chartButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            showToast(`切換到 ${btn.textContent} 視圖`);
        });
    });

    // --- TOAST CLOSE ---
    document.querySelector('.toast-close')?.addEventListener('click', () => {
        successToast.classList.add('hidden');
    });

    // --- LOGOUT ---
    document.getElementById('logout-btn')?.addEventListener('click', () => {
        showToast('登出功能 (Prototype)');
    });

    // --- INITIALIZATION ---
    function init() {
        // Set initial progress values
        updateQualityMetrics();
        
        // Show welcome message
        setTimeout(() => {
            showToast('歡迎使用 MLINFO 資料處理系統 Prototype！');
        }, 1000);
    }

    // Initialize application
    init();
});

// ===== ADDITIONAL INTERACTIVE FEATURES =====

// Smooth scrolling for internal links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Auto-update dashboard metrics every 10 seconds
setInterval(() => {
    const progressCircles = document.querySelectorAll('.progress-circle');
    progressCircles.forEach(circle => {
        const currentProgress = parseInt(circle.style.getPropertyValue('--progress') || '90');
        const newProgress = Math.max(80, Math.min(98, currentProgress + (Math.random() - 0.5) * 4));
        circle.style.setProperty('--progress', Math.floor(newProgress));
        const textElement = circle.querySelector('.progress-text');
        if (textElement) {
            textElement.textContent = `${Math.floor(newProgress)}%`;
        }
    });
}, 10000);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + U for upload
    if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
        e.preventDefault();
        document.getElementById('file-input')?.click();
    }
    
    // Ctrl/Cmd + E for export
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        document.getElementById('export-csv')?.click();
    }
    
    // Escape to close toast
    if (e.key === 'Escape') {
        document.getElementById('success-toast')?.classList.add('hidden');
    }
});