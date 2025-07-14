#!/bin/bash

# 測試執行腳本
# 用於執行資料匯入流程測試

echo "🚀 MLINFO 資料匯入流程測試"
echo "================================"

# 檢查是否在正確的目錄
if [ ! -f "app/main.py" ]; then
    echo "❌ 請在 backend 目錄下執行此腳本"
    exit 1
fi

# 檢查測試檔案是否存在
if [ ! -f "../testdata/960.csv" ]; then
    echo "❌ 測試檔案不存在: ../testdata/960.csv"
    exit 1
fi

echo "✅ 測試環境檢查完成"
echo ""

# 選擇測試模式
echo "請選擇測試模式："
echo "1. 快速測試 (推薦)"
echo "2. 完整測試"
echo "3. 僅測試 CSV 解析"
echo ""

read -p "請輸入選項 (1-3): " choice

case $choice in
    1)
        echo "🔄 執行快速測試..."
        python quick_test.py
        ;;
    2)
        echo "🔄 執行完整測試..."
        python test_ingest_flow.py
        ;;
    3)
        echo "🔄 僅測試 CSV 解析..."
        python -c "
import sys
sys.path.insert(0, '.')
from app.csv_processor2 import CSVProcessor2

processor = CSVProcessor2()
with open('../testdata/960.csv', 'r', encoding='utf-8') as f:
    content = f.read()

result = processor.process_csv_content(content, None)
print(f'✅ CSV 解析成功: {len(result)} 筆記錄')
if result:
    print('前 3 筆記錄:')
    for i, record in enumerate(result[:3]):
        print(f'記錄 {i+1}: {len(record)} 個欄位')
"
        ;;
    *)
        echo "❌ 無效選項"
        exit 1
        ;;
esac

echo ""
echo "測試完成！" 