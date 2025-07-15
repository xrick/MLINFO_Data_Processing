# Tools 工具目錄

本目錄包含用於管理和操作資料庫的各種工具程式。

## 工具列表

### 1. duckdbviewer.py
DuckDB 資料庫檢視器，用於查看和匯出 sales_specs.db 中的資料。

**功能：**
- 檢視資料庫摘要和表格結構
- 顯示記錄內容（支援限制數量）
- 根據 modeltype 查詢特定記錄
- 匯出資料到 CSV 檔案
- 互動模式操作

**使用方法：**
```bash
# 互動模式
python duckdbviewer.py

# 命令列模式
python duckdbviewer.py summary                    # 顯示摘要
python duckdbviewer.py list [limit]              # 顯示記錄（可限制數量）
python duckdbviewer.py search <modeltype>        # 搜尋特定型號
python duckdbviewer.py export [filename]         # 匯出到 CSV
```

### 2. milvusviewer.py
Milvus 向量資料庫檢視器（若存在）。

### 3. db_cleaner.py ⭐ 新增
資料庫清理工具，用於清理 DuckDB 和 Milvus 資料庫中的所有資料，但保留資料庫結構。

**功能：**
- 檢查 DuckDB 和 Milvus 資料庫狀態
- 清理 DuckDB 表格中的所有記錄
- 清理 Milvus collection 中的所有實體
- 同時清理所有資料庫
- 安全確認機制防止誤操作
- 支援命令列和互動模式

**使用方法：**
```bash
# 互動模式
python db_cleaner.py

# 命令列模式
python db_cleaner.py status                      # 檢查資料庫狀態
python db_cleaner.py clear-duckdb               # 清理 DuckDB 資料
python db_cleaner.py clear-milvus               # 清理 Milvus 資料
python db_cleaner.py clear-all                  # 清理所有資料庫資料

# 強制模式（跳過確認，小心使用）
python db_cleaner.py clear-all --force
```

**安全特性：**
- ⚠️ 所有清理操作都需要輸入 'YES' 確認
- ✅ 操作前會顯示將被刪除的記錄/實體數量
- ✅ 操作後會驗證清理結果
- ✅ 只清理資料，保留資料庫和表格結構
- ✅ 支援 --force 參數用於自動化腳本

### 4. quick_view.sh
快速檢視腳本（若存在）。

## 環境需求

### Python 套件
- `duckdb`: DuckDB 資料庫操作
- `pandas`: 資料處理
- `pymilvus`: Milvus 向量資料庫操作（可選）

### 環境變數
- `MILVUS_HOST`: Milvus 主機位址（預設: localhost）
- `MILVUS_PORT`: Milvus 連接埠（預設: 19530）

## 資料庫位置

- **DuckDB**: `../backend/sales_specs.db`
- **Milvus**: `localhost:19530` (collection: `sales_notebook_specs`)

## 使用注意事項

1. **權限設定**: 確保工具有執行權限
   ```bash
   chmod +x *.py
   ```

2. **路徑依賴**: 工具設計為從 tools 目錄執行
   ```bash
   cd tools
   python db_cleaner.py
   ```

3. **資料備份**: 清理操作無法復原，重要資料請先備份

4. **Milvus 連線**: 如果 Milvus 服務未啟動，相關功能會自動跳過

## 開發者說明

### 添加新工具
1. 在 tools 目錄下創建新的 Python 檔案
2. 遵循現有工具的結構和命名慣例
3. 更新此 README.md 文檔
4. 設定適當的執行權限

### 工具設計原則
- 支援命令列和互動兩種模式
- 提供清楚的錯誤訊息和狀態回饋
- 危險操作需要確認機制
- 相對路徑設計，便於移植