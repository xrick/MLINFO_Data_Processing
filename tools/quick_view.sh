#!/bin/bash

# 快速檢視腳本
# 用於快速檢視 DuckDB 和 Milvus 資料庫狀態

echo "🔍 MLINFO 資料庫快速檢視工具"
echo "================================"

# 檢查是否在正確的目錄
if [ ! -f "duckdbviewer.py" ]; then
    echo "❌ 請在 tools 目錄下執行此腳本"
    exit 1
fi

echo "請選擇要檢視的資料庫："
echo "1. DuckDB 檢視器"
echo "2. Milvus 檢視器"
echo "3. 同時檢視兩個資料庫摘要"
echo "4. 退出"
echo ""

read -p "請輸入選項 (1-4): " choice

case $choice in
    1)
        echo "🔄 啟動 DuckDB 檢視器..."
        python duckdbviewer.py
        ;;
    2)
        echo "🔄 啟動 Milvus 檢視器..."
        python milvusviewer.py
        ;;
    3)
        echo "🔄 檢視兩個資料庫摘要..."
        echo ""
        echo "📊 DuckDB 摘要:"
        echo "----------------"
        python duckdbviewer.py summary
        echo ""
        echo "📊 Milvus 摘要:"
        echo "----------------"
        python milvusviewer.py summary
        ;;
    4)
        echo "👋 再見！"
        exit 0
        ;;
    *)
        echo "❌ 無效選項"
        exit 1
        ;;
esac

echo ""
echo "檢視完成！" 