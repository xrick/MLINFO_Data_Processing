# SalesRAG 整合系統使用指南

## 🎯 系統概覽

SalesRAG 是一個整合了資料處理與智能問答功能的筆記型電腦銷售系統，結合了原本的 MLINFO_Data_Processing 和 SalesRAG 兩個系統的優點。

### 主要功能
- **儀表板**: 系統狀態監控與快速操作
- **資料管理**: CSV 檔案上傳、解析與資料庫匯入
- **智能助手**: AI 驅動的規格查詢與比較
- **分析報告**: 使用統計與資料分析

## 🚀 快速啟動

### 1. 後端啟動

```bash
# 進入後端目錄
cd backend

# 啟動 FastAPI 服務器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端啟動

```bash
# 進入前端目錄
cd frontend

# 使用 Python 啟動靜態檔案服務器
python -m http.server 8080

# 或使用 Node.js serve
npx serve . -p 8080
```

### 3. 訪問系統

開啟瀏覽器訪問: `http://localhost:8080/unified_index.html`

## 📁 整合後的檔案結構

```
MLINFO_Data_Processing/
├── backend/
│   ├── app/
│   │   ├── main.py              # 統一的 FastAPI 應用程式
│   │   ├── models.py            # 擴展的資料模型
│   │   ├── rag_service.py       # RAG 查詢服務
│   │   ├── system_service.py    # 系統狀態服務
│   │   ├── db_ingestor.py       # 資料庫匯入服務
│   │   ├── csv_processor2.py    # CSV 處理服務
│   │   └── libs/                # 解析模組庫
│   └── requirements.txt
├── frontend/
│   ├── unified_index.html       # 統一主頁面
│   ├── unified_styles.css       # 統一樣式檔案
│   ├── unified_app.js           # 統一應用程式邏輯
│   ├── mainpage.html           # 原 SalesRAG 頁面 (保留)
│   └── index.html              # 原資料處理頁面 (保留)
├── config/
├── tools/
└── INTEGRATED_SYSTEM_GUIDE.md  # 本檔案
```

## 🔧 API 端點說明

### 資料處理相關
- `POST /api/process` - 處理 CSV 內容
- `POST /api/ingest-to-db` - 匯入資料到資料庫
- `GET /api/data-status` - 獲取資料庫狀態

### RAG 查詢相關
- `POST /api/chat/query` - 智能問答查詢
- `GET /api/chat/suggestions` - 獲取建議問題
- `POST /api/chat/compare` - 比較型號規格

### 系統管理相關
- `GET /api/system/health` - 系統健康檢查
- `GET /api/system/stats` - 系統使用統計
- `POST /api/system/clean` - 清理系統資料

## 💻 使用流程

### 資料管理員工作流程
1. **登入系統** → 查看儀表板狀態
2. **切換到資料管理頁面** → 上傳 CSV 檔案
3. **預覽解析結果** → 編輯或確認資料
4. **匯入資料庫** → 更新知識庫
5. **確認匯入成功** → 檢查儀表板統計

### 銷售人員查詢流程
1. **切換到智能助手** → 開始對話
2. **輸入客戶需求** → 或選擇預設問題
3. **獲得專業建議** → 基於知識庫回答
4. **進行規格比較** → 多款產品對比
5. **查看分析報告** → 了解查詢趨勢

## 🔍 功能測試

### 1. 系統健康檢查
- 點擊頂部「系統狀態」按鈕
- 確認 DuckDB 和 Milvus 狀態為 healthy
- 查看總記錄數和最後更新時間

### 2. 資料處理測試
- 使用 `testdata/` 目錄中的 CSV 檔案進行測試
- 確認檔案上傳、解析和匯入功能正常
- 檢查儀表板統計數據更新

### 3. 智能問答測試
- 嘗試預設問題
- 測試自定義查詢
- 驗證回答準確性和相關性

### 4. 比較功能測試
- 輸入多個型號名稱進行比較
- 確認比較結果的完整性
- 測試不同比較欄位的選擇

## 🛠️ 故障排除

### 常見問題

#### 1. 後端啟動失敗
```bash
# 檢查依賴套件
pip install -r requirements.txt

# 檢查 Python 版本 (需要 3.8+)
python --version

# 檢查埠口是否被占用
lsof -i :8000
```

#### 2. 前端無法載入
```bash
# 確認前端服務器正在運行
curl http://localhost:8080

# 檢查檔案路徑
ls -la frontend/unified_index.html
```

#### 3. 資料庫連接問題
```bash
# 檢查 DuckDB 檔案
ls -la backend/sales_specs.db

# 檢查 Milvus 服務狀態
docker ps | grep milvus
```

#### 4. API 請求失敗
- 檢查 CORS 設定
- 確認 API 端點 URL 正確
- 查看瀏覽器開發者工具的網路標籤

### 日誌查看
```bash
# 後端日誌
uvicorn app.main:app --reload --log-level debug

# 前端日誌
# 開啟瀏覽器開發者工具 (F12) 查看 Console
```

## 🔒 安全性注意事項

1. **CORS 設定**: 僅允許 localhost:8080 和 127.0.0.1:8080
2. **輸入驗證**: 所有用戶輸入都經過驗證
3. **資源管理**: 使用 context manager 管理資料庫連接
4. **錯誤處理**: 避免敏感資訊洩露

## 📊 效能監控

- **回應時間**: 監控 API 回應速度
- **資源使用**: 檢查記憶體和 CPU 使用率
- **資料庫效能**: 監控查詢執行時間
- **用戶體驗**: 追蹤頁面載入速度

## 🚧 已知限制

1. **查詢統計**: 目前使用記憶體存儲，重啟後會清空
2. **檔案大小**: 建議 CSV 檔案不超過 10MB
3. **並發處理**: 目前為單執行緒處理
4. **快取機制**: 尚未實施查詢結果快取

## 🔄 未來改進計劃

1. **效能優化**
   - 實施 Redis 快取
   - 添加批次處理功能
   - 優化資料庫查詢

2. **功能擴展**
   - 用戶管理系統
   - 權限控制
   - 資料匯出功能
   - 高級分析圖表

3. **使用體驗**
   - 響應式設計改進
   - 離線功能支援
   - 多語言支援

## 📞 技術支援

如遇到問題，請：
1. 檢查本指南的故障排除章節
2. 查看系統日誌檔案
3. 確認所有依賴服務正常運行
4. 聯繫技術團隊

---

**版本**: 3.0.0  
**最後更新**: 2025-01-15  
**維護團隊**: SalesRAG 開發組