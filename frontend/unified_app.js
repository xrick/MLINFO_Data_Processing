/**
 * SalesRAG 統一應用程式
 * 筆記型電腦智能銷售系統
 */

// 應用程式狀態管理
const AppState = {
    currentSection: 'dashboard',
    systemHealth: null,
    systemStats: null,
    processedData: null,
    chatHistory: [],
    isLoading: false,
    
    // API 基礎 URL
    apiBaseUrl: 'http://localhost:8000',
    
    // 更新狀態
    setState(newState) {
        Object.assign(this, newState);
        this.notifyStateChange();
    },
    
    // 狀態變更通知
    notifyStateChange() {
        // 可以在這裡添加狀態變更的回調
        console.log('App state updated:', this);
    }
};

// 工具函數
const Utils = {
    // 顯示載入指示器
    showLoading(message = '處理中...') {
        const overlay = document.getElementById('loading-overlay');
        const text = overlay.querySelector('p');
        text.textContent = message;
        overlay.classList.add('active');
        AppState.setState({ isLoading: true });
    },
    
    // 隱藏載入指示器
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        overlay.classList.remove('active');
        AppState.setState({ isLoading: false });
    },
    
    // 顯示通知
    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        container.appendChild(notification);
        
        // 自動移除通知
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    },
    
    // 獲取通知圖標
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    },
    
    // 格式化日期
    formatDate(dateString) {
        if (!dateString) return '--';
        const date = new Date(dateString);
        return date.toLocaleString('zh-TW');
    },
    
    // 格式化數字
    formatNumber(num) {
        if (typeof num !== 'number') return num;
        return new Intl.NumberFormat('zh-TW').format(num);
    },
    
    // 防抖函數
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// API 服務
const ApiService = {
    // 發送 HTTP 請求
    async request(endpoint, options = {}) {
        const url = `${AppState.apiBaseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    // 系統健康檢查
    async getSystemHealth() {
        return this.request('/api/system/health');
    },
    
    // 獲取系統統計
    async getSystemStats() {
        return this.request('/api/system/stats');
    },
    
    // 獲取資料狀態
    async getDataStatus() {
        return this.request('/api/data-status');
    },
    
    // 處理 CSV 內容
    async processCSV(data) {
        return this.request('/api/process', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    // 匯入到資料庫
    async ingestToDatabase(data) {
        return this.request('/api/ingest-to-db', {
            method: 'POST',
            body: JSON.stringify({ data })
        });
    },
    
    // 聊天查詢
    async chatQuery(query, chatHistory = []) {
        return this.request('/api/chat/query', {
            method: 'POST',
            body: JSON.stringify({
                query,
                chat_history: chatHistory,
                max_results: 5
            })
        });
    },
    
    // 獲取建議問題
    async getChatSuggestions() {
        return this.request('/api/chat/suggestions');
    },
    
    // 比較型號
    async compareModels(models, compareFields = null) {
        return this.request('/api/chat/compare', {
            method: 'POST',
            body: JSON.stringify({
                models,
                compare_fields: compareFields
            })
        });
    },
    
    // 清理資料
    async cleanData() {
        return this.request('/api/system/clean', {
            method: 'POST'
        });
    }
};

// 導航管理
const NavigationManager = {
    init() {
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.switchSection(section);
            });
        });
    },
    
    switchSection(sectionName) {
        // 更新導航按鈕狀態
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.section === sectionName) {
                btn.classList.add('active');
            }
        });
        
        // 顯示對應的內容區塊
        const sections = document.querySelectorAll('.content-section');
        sections.forEach(section => {
            section.classList.remove('active');
        });
        
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
            AppState.setState({ currentSection: sectionName });
            
            // 根據區塊載入相應的內容
            this.loadSectionContent(sectionName);
        }
    },
    
    async loadSectionContent(sectionName) {
        switch (sectionName) {
            case 'dashboard':
                await DashboardManager.loadDashboard();
                break;
            case 'data-manager':
                DataManager.init();
                break;
            case 'chat':
                await ChatManager.init();
                break;
            case 'analytics':
                await AnalyticsManager.loadAnalytics();
                break;
        }
    }
};

// 儀表板管理
const DashboardManager = {
    async loadDashboard() {
        try {
            // 載入系統健康狀態
            const health = await ApiService.getSystemHealth();
            AppState.setState({ systemHealth: health });
            this.updateHealthIndicators(health);
            
            // 載入系統統計
            const stats = await ApiService.getSystemStats();
            AppState.setState({ systemStats: stats });
            this.updateStatsCards(stats);
            
            // 載入資料狀態
            const dataStatus = await ApiService.getDataStatus();
            this.updateDataStatus(dataStatus);
            
        } catch (error) {
            console.error('載入儀表板失敗:', error);
            Utils.showNotification('載入儀表板失敗', 'error');
        }
    },
    
    updateHealthIndicators(health) {
        // 更新側邊欄指示器
        const duckdbIndicator = document.getElementById('duckdb-indicator');
        const milvusIndicator = document.getElementById('milvus-indicator');
        
        const duckdbDot = duckdbIndicator.querySelector('.status-dot');
        const milvusDot = milvusIndicator.querySelector('.status-dot');
        
        // 清除之前的狀態
        duckdbDot.className = 'status-dot';
        milvusDot.className = 'status-dot';
        
        // 設定新狀態
        if (health.duckdb_status === 'healthy') {
            duckdbDot.classList.add('healthy');
        } else {
            duckdbDot.classList.add('error');
        }
        
        if (health.milvus_status === 'healthy') {
            milvusDot.classList.add('healthy');
        } else {
            milvusDot.classList.add('error');
        }
    },
    
    updateStatsCards(stats) {
        // 更新統計卡片
        document.getElementById('total-records').textContent = Utils.formatNumber(stats.total_records);
        document.getElementById('total-queries').textContent = Utils.formatNumber(stats.total_queries);
        document.getElementById('database-size').textContent = stats.database_size;
    },
    
    updateDataStatus(dataStatus) {
        document.getElementById('last-update').textContent = Utils.formatDate(dataStatus.last_update);
    }
};

// 資料管理
const DataManager = {
    processedData: null,
    
    init() {
        this.setupFileUpload();
        this.setupDragAndDrop();
    },
    
    setupFileUpload() {
        const fileInput = document.getElementById('file-input');
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFileUpload(file);
            }
        });
    },
    
    setupDragAndDrop() {
        const uploadZone = document.getElementById('upload-zone');
        
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });
        
        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });
    },
    
    async handleFileUpload(file) {
        if (!file.name.endsWith('.csv')) {
            Utils.showNotification('請選擇 CSV 檔案', 'error');
            return;
        }
        
        try {
            Utils.showLoading('正在處理檔案...');
            
            const content = await this.readFileContent(file);
            const result = await ApiService.processCSV({
                text_content: content,
                file_name: file.name
            });
            
            if (result.require_modeltype_input) {
                // 需要用戶輸入 modeltype
                const modeltype = prompt('請輸入型號類型:');
                if (modeltype) {
                    const finalResult = await ApiService.processCSV({
                        text_content: content,
                        file_name: file.name,
                        user_modeltype: modeltype
                    });
                    this.displayProcessedData(finalResult.data);
                }
            } else {
                this.displayProcessedData(result.data);
            }
            
        } catch (error) {
            console.error('檔案處理失敗:', error);
            Utils.showNotification('檔案處理失敗: ' + error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = () => reject(new Error('檔案讀取失敗'));
            reader.readAsText(file, 'utf-8');
        });
    },
    
    displayProcessedData(data) {
        this.processedData = data;
        
        const preview = document.getElementById('data-preview');
        const table = document.getElementById('data-table');
        const header = document.getElementById('table-header');
        const body = document.getElementById('table-body');
        
        // 清空現有內容
        header.innerHTML = '';
        body.innerHTML = '';
        
        if (data.length > 0) {
            // 建立表頭
            const headerRow = document.createElement('tr');
            Object.keys(data[0]).forEach(key => {
                const th = document.createElement('th');
                th.textContent = key;
                headerRow.appendChild(th);
            });
            header.appendChild(headerRow);
            
            // 建立表格內容
            data.forEach(row => {
                const tr = document.createElement('tr');
                Object.values(row).forEach(value => {
                    const td = document.createElement('td');
                    td.textContent = value || '';
                    tr.appendChild(td);
                });
                body.appendChild(tr);
            });
            
            preview.style.display = 'block';
            Utils.showNotification('檔案處理完成', 'success');
        }
    },
    
    async ingestData() {
        if (!this.processedData) {
            Utils.showNotification('沒有可匯入的資料', 'error');
            return;
        }
        
        try {
            Utils.showLoading('正在匯入資料庫...');
            
            const result = await ApiService.ingestToDatabase(this.processedData);
            
            if (result.success) {
                Utils.showNotification(
                    `成功匯入 ${result.duckdb_rows_added} 筆記錄到 DuckDB，${result.milvus_entities_added} 筆記錄到 Milvus`,
                    'success'
                );
                
                // 重新載入儀表板資料
                await DashboardManager.loadDashboard();
            }
            
        } catch (error) {
            console.error('資料匯入失敗:', error);
            Utils.showNotification('資料匯入失敗: ' + error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    }
};

// 聊天管理
const ChatManager = {
    chatHistory: [],
    
    async init() {
        this.setupChatInput();
        await this.loadSuggestions();
    },
    
    setupChatInput() {
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        
        const sendMessage = () => {
            const message = chatInput.value.trim();
            if (message) {
                this.sendChatMessage(message);
                chatInput.value = '';
            }
        };
        
        sendBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    },
    
    async loadSuggestions() {
        try {
            const suggestions = await ApiService.getChatSuggestions();
            this.displaySuggestions(suggestions);
        } catch (error) {
            console.error('載入建議問題失敗:', error);
        }
    },
    
    displaySuggestions(suggestions) {
        const container = document.getElementById('suggestion-buttons');
        container.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const button = document.createElement('button');
            button.className = 'suggestion-btn';
            button.textContent = suggestion;
            button.addEventListener('click', () => {
                this.sendChatMessage(suggestion);
            });
            container.appendChild(button);
        });
    },
    
    async sendChatMessage(message) {
        // 顯示用戶訊息
        this.addMessageToChat(message, 'user');
        
        try {
            // 顯示載入狀態
            const loadingMessage = this.addMessageToChat('正在思考中...', 'bot', true);
            
            // 發送查詢
            const response = await ApiService.chatQuery(message, this.chatHistory);
            
            // 移除載入訊息
            loadingMessage.remove();
            
            // 顯示回答
            this.addMessageToChat(response.answer, 'bot');
            
            // 更新聊天歷史
            this.chatHistory.push(
                { role: 'user', content: message },
                { role: 'assistant', content: response.answer }
            );
            
        } catch (error) {
            console.error('聊天查詢失敗:', error);
            this.addMessageToChat('抱歉，查詢過程中發生錯誤。', 'bot');
        }
    },
    
    addMessageToChat(content, sender, isLoading = false) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (isLoading) {
            messageContent.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + content;
        } else {
            messageContent.innerHTML = `<p>${content}</p>`;
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // 滾動到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }
};

// 分析管理
const AnalyticsManager = {
    async loadAnalytics() {
        try {
            const stats = await ApiService.getSystemStats();
            this.displayPopularQueries(stats.popular_queries);
            // 可以在這裡添加更多分析功能
        } catch (error) {
            console.error('載入分析資料失敗:', error);
        }
    },
    
    displayPopularQueries(queries) {
        const container = document.getElementById('popular-queries');
        container.innerHTML = '';
        
        if (queries.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary);">暫無查詢記錄</p>';
            return;
        }
        
        queries.forEach(query => {
            const queryItem = document.createElement('div');
            queryItem.className = 'query-item';
            queryItem.innerHTML = `
                <span class="query-text">${query.query}</span>
                <span class="query-count">${query.count}</span>
            `;
            container.appendChild(queryItem);
        });
    }
};

// 全域函數
window.switchSection = (sectionName) => {
    NavigationManager.switchSection(sectionName);
};

window.exportData = async () => {
    Utils.showNotification('匯出功能開發中...', 'info');
};

window.cleanData = async () => {
    if (confirm('確定要清除所有資料嗎？此操作無法復原。')) {
        try {
            Utils.showLoading('正在清除資料...');
            const result = await ApiService.cleanData();
            
            if (result.success) {
                Utils.showNotification('資料清除成功', 'success');
                await DashboardManager.loadDashboard();
            } else {
                Utils.showNotification('資料清除失敗', 'error');
            }
        } catch (error) {
            console.error('資料清除失敗:', error);
            Utils.showNotification('資料清除失敗: ' + error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    }
};

window.editData = () => {
    Utils.showNotification('編輯功能開發中...', 'info');
};

window.ingestData = () => {
    DataManager.ingestData();
};

window.closeModal = (modalId) => {
    const modal = document.getElementById(modalId);
    modal.classList.remove('active');
};

// 應用程式初始化
document.addEventListener('DOMContentLoaded', async () => {
    console.log('SalesRAG 應用程式正在啟動...');
    
    // 初始化導航
    NavigationManager.init();
    
    // 初始化系統狀態檢查
    document.getElementById('system-status-btn').addEventListener('click', async () => {
        const modal = document.getElementById('system-status-modal');
        modal.classList.add('active');
        
        try {
            const health = await ApiService.getSystemHealth();
            document.getElementById('overall-status').textContent = health.status;
            document.getElementById('duckdb-status').textContent = health.duckdb_status;
            document.getElementById('milvus-status').textContent = health.milvus_status;
            document.getElementById('modal-total-records').textContent = health.total_records;
            document.getElementById('modal-last-update').textContent = Utils.formatDate(health.last_update);
        } catch (error) {
            console.error('獲取系統狀態失敗:', error);
        }
    });
    
    // 載入默認儀表板
    await DashboardManager.loadDashboard();
    
    // 設置定期更新
    setInterval(async () => {
        if (AppState.currentSection === 'dashboard') {
            await DashboardManager.loadDashboard();
        }
    }, 30000); // 每30秒更新一次
    
    console.log('SalesRAG 應用程式啟動完成');
});

// 錯誤處理
window.addEventListener('error', (event) => {
    console.error('全域錯誤:', event.error);
    Utils.showNotification('系統發生錯誤，請重新載入頁面', 'error');
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('未處理的 Promise 拒絕:', event.reason);
    Utils.showNotification('系統發生異步錯誤', 'error');
});