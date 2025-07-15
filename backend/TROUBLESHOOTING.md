# 故障排除指南

## 常見問題和解決方案

### 1. huggingface_hub 版本衝突錯誤

**錯誤訊息：**
```
Failed to ingest: cannot import name 'cached_download' from 'huggingface_hub'
```

**原因：**
`sentence-transformers` 套件與 `huggingface_hub` 版本不兼容。

**解決方案：**

#### 方法 1: 使用修復腳本 (推薦)
```bash
cd backend
chmod +x fix_dependencies.sh
./fix_dependencies.sh
```

#### 方法 2: 手動修復
```bash
cd backend

# 1. 卸載衝突的套件
pip uninstall -y huggingface-hub sentence-transformers transformers torch numpy

# 2. 清理快取
pip cache purge

# 3. 重新安裝正確版本
pip install huggingface-hub==0.19.4
pip install transformers==4.35.2
pip install torch>=1.13.0
pip install numpy>=1.21.0
pip install sentence-transformers==2.2.2

# 4. 安裝其他依賴
pip install -r requirements.txt
```

#### 方法 3: 使用 conda 環境
```bash
# 如果使用 conda 環境
conda install pytorch torchvision torchaudio -c pytorch
pip install huggingface-hub==0.19.4
pip install transformers==4.35.2
pip install sentence-transformers==2.2.2
```

### 2. Milvus 連線錯誤

**錯誤訊息：**
```
Connection refused to Milvus server
```

**解決方案：**
```bash
# 檢查 Milvus 服務狀態
docker ps | grep milvus

# 啟動 Milvus 服務 (如果使用 Docker)
docker-compose up -d

# 檢查環境變數
echo $MILVUS_HOST
echo $MILVUS_PORT
```

### 3. DuckDB 檔案權限錯誤

**錯誤訊息：**
```
Permission denied: sales_specs.db
```

**解決方案：**
```bash
# 檢查檔案權限
ls -la sales_specs.db

# 修改權限
chmod 644 sales_specs.db

# 或重新建立資料庫
rm sales_specs.db
```

### 4. 記憶體不足錯誤

**錯誤訊息：**
```
Out of memory error
```

**解決方案：**
```bash
# 增加系統交換空間
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 或減少批次處理大小
# 在 db_ingestor.py 中修改批次大小
```

### 5. 模型下載失敗

**錯誤訊息：**
```
Failed to download model from HuggingFace
```

**解決方案：**
```bash
# 設定代理 (如果需要)
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

# 或使用鏡像
export HF_ENDPOINT=https://hf-mirror.com

# 手動下載模型
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./models')
"
```

### 6. 埠號被佔用

**錯誤訊息：**
```
Address already in use
```

**解決方案：**
```bash
# 檢查埠號使用情況
lsof -i :8000

# 終止佔用程序
kill -9 <PID>

# 或使用不同埠號
uvicorn app.main:app --port 8001 --reload
```

### 7. 模組找不到錯誤

**錯誤訊息：**
```
ModuleNotFoundError: No module named 'app'
```

**解決方案：**
```bash
# 確保在正確目錄
cd backend

# 設定 PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 或使用模組方式執行
python -m uvicorn app.main:app --reload
```

## 預防措施

### 1. 使用虛擬環境
```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 2. 定期更新依賴
```bash
# 檢查過期套件
pip list --outdated

# 更新套件
pip install --upgrade package_name
```

### 3. 備份重要資料
```bash
# 備份資料庫
cp sales_specs.db sales_specs_backup.db

# 備份設定檔
cp .env .env.backup
```

## 診斷工具

### 1. 環境檢查腳本
```bash
cd backend
python -c "
import sys
print(f'Python 版本: {sys.version}')

packages = ['fastapi', 'uvicorn', 'pandas', 'duckdb', 'pymilvus', 'sentence_transformers']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg} 已安裝')
    except ImportError:
        print(f'❌ {pkg} 未安裝')
"
```

### 2. 連線測試腳本
```bash
cd backend
python -c "
import os
print(f'MILVUS_HOST: {os.getenv(\"MILVUS_HOST\", \"未設定\")}')
print(f'MILVUS_PORT: {os.getenv(\"MILVUS_PORT\", \"未設定\")}')

try:
    from pymilvus import connections
    connections.connect('default', host='localhost', port='19530')
    print('✅ Milvus 連線成功')
except Exception as e:
    print(f'❌ Milvus 連線失敗: {e}')
"
```

## 聯絡支援

如果以上解決方案都無法解決問題，請提供以下資訊：

1. 錯誤訊息完整內容
2. 作業系統版本
3. Python 版本
4. 套件版本列表 (`pip list`)
5. 環境變數設定
6. 執行步驟

## 更新日誌

- 2024-12-19: 新增 huggingface_hub 版本衝突解決方案
- 2024-12-19: 新增常見錯誤處理指南 