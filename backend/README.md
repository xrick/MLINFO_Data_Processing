# MLINFO 資料處理後端執行指南

## 概述

後端程式基於 FastAPI 框架，提供 CSV 解析和資料庫匯入的 REST API 服務。

## 系統需求

- Python 3.8+
- 虛擬環境 (推薦)
- 必要的 Python 套件 (見 requirements.txt)

## 安裝步驟

### 1. 建立虛擬環境 (推薦)

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. 安裝依賴套件

```bash
cd backend
pip install -r requirements.txt
```

### 3. 環境變數設定

創建 `.env` 檔案 (如果不存在):

```bash
# Milvus 連線設定
MILVUS_HOST=localhost
MILVUS_PORT=19530

# 其他設定 (可選)
DEBUG=True
LOG_LEVEL=INFO
```

## 執行方式

### 方式 1: 使用 uvicorn (推薦)

```bash
cd backend

# 基本執行
uvicorn app.main:app --reload

# 指定主機和埠號
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 生產環境執行 (不包含 --reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 方式 2: 使用 Python 直接執行

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 方式 3: 使用啟動腳本

```bash
# 使用提供的啟動腳本
./start_server.sh
```

## 服務端點

### 根端點
- **GET** `/` - API 歡迎訊息

### 處理端點
- **POST** `/api/process` - CSV 內容解析
- **POST** `/api/ingest-to-db` - 資料庫匯入

### API 文件
- **GET** `/docs` - Swagger UI 文件
- **GET** `/redoc` - ReDoc 文件

## 執行範例

### 1. 啟動服務

```bash
cd backend
uvicorn app.main:app --reload
```

### 2. 檢查服務狀態

```bash
# 檢查根端點
curl http://localhost:8000/

# 檢查 API 文件
# 在瀏覽器中開啟: http://localhost:8000/docs
```

### 3. 測試 CSV 處理

```bash
# 使用 curl 測試
curl -X POST "http://localhost:8000/api/process" \
     -H "Content-Type: application/json" \
     -d '{
       "text_content": "test,data\n1,2",
       "file_name": "test.csv",
       "user_modeltype": "960"
     }'
```

## 開發模式

### 啟用開發模式

```bash
# 設定環境變數
export DEBUG=True
export LOG_LEVEL=DEBUG

# 啟動服務
uvicorn app.main:app --reload --log-level debug
```

### 熱重載

使用 `--reload` 參數可以啟用熱重載功能，當程式碼變更時會自動重啟服務。

## 生產環境部署

### 1. 使用 Gunicorn (推薦)

```bash
# 安裝 Gunicorn
pip install gunicorn

# 啟動服務
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. 使用 Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 故障排除

### 常見問題

#### 1. 埠號被佔用
```bash
# 檢查埠號使用情況
lsof -i :8000

# 使用不同埠號
uvicorn app.main:app --port 8001 --reload
```

#### 2. 模組找不到
```bash
# 確保在正確的目錄
cd backend

# 檢查 Python 路徑
python -c "import sys; print(sys.path)"
```

#### 3. 依賴套件問題
```bash
# 重新安裝依賴
pip install -r requirements.txt --force-reinstall

# 檢查套件版本
pip list
```

#### 4. Milvus 連線問題
```bash
# 檢查 Milvus 服務狀態
docker ps | grep milvus

# 檢查環境變數
echo $MILVUS_HOST
echo $MILVUS_PORT
```

### 日誌檢查

```bash
# 啟用詳細日誌
uvicorn app.main:app --reload --log-level debug

# 檢查錯誤日誌
tail -f logs/app.log
```

## 效能優化

### 1. 工作程序數

```bash
# 多工作程序
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### 2. 記憶體優化

```bash
# 設定記憶體限制
export PYTHONOPTIMIZE=1
uvicorn app.main:app --reload
```

## 監控和維護

### 健康檢查

```bash
# 健康檢查端點
curl http://localhost:8000/health

# 檢查服務狀態
curl http://localhost:8000/status
```

### 效能監控

```bash
# 使用 htop 監控系統資源
htop

# 監控網路連線
netstat -tulpn | grep 8000
```

## 安全注意事項

1. **生產環境**: 不要使用 `--reload` 參數
2. **防火牆**: 設定適當的防火牆規則
3. **HTTPS**: 在生產環境中使用 HTTPS
4. **認證**: 實作適當的認證機制
5. **日誌**: 記錄所有重要操作

## 支援

如有問題，請檢查：
1. 日誌檔案
2. 環境變數設定
3. 依賴套件版本
4. 網路連線狀態 