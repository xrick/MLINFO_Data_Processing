#!/bin/bash

# MLINFO 後端服務啟動腳本

echo "🚀 MLINFO 資料處理後端服務啟動"
echo "================================"

# 檢查是否在正確的目錄
if [ ! -f "app/main.py" ]; then
    echo "❌ 請在 backend 目錄下執行此腳本"
    exit 1
fi

# 檢查 Python 環境
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安裝或不在 PATH 中"
    exit 1
fi

# 檢查虛擬環境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  未檢測到虛擬環境，建議使用虛擬環境"
    echo "   建立虛擬環境: python -m venv venv"
    echo "   啟動虛擬環境: source venv/bin/activate"
    echo ""
fi

# 檢查依賴套件
echo "🔍 檢查依賴套件..."
if ! python -c "import fastapi, uvicorn" &> /dev/null; then
    echo "❌ 缺少必要套件，請執行: pip install -r requirements.txt"
    exit 1
fi

# 檢查環境變數
echo "🔍 檢查環境變數..."
if [ -z "$MILVUS_HOST" ]; then
    export MILVUS_HOST=localhost
    echo "⚠️  MILVUS_HOST 未設定，使用預設值: localhost"
fi

if [ -z "$MILVUS_PORT" ]; then
    export MILVUS_PORT=19530
    echo "⚠️  MILVUS_PORT 未設定，使用預設值: 19530"
fi

# 載入 .env 檔案 (如果存在)
if [ -f ".env" ]; then
    echo "📄 載入 .env 檔案..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# 選擇執行模式
echo ""
echo "請選擇執行模式："
echo "1. 開發模式 (熱重載)"
echo "2. 生產模式"
echo "3. 除錯模式"
echo "4. 自訂設定"
echo ""

read -p "請輸入選項 (1-4): " choice

case $choice in
    1)
        echo "🔄 啟動開發模式..."
        echo "📍 服務地址: http://localhost:8000"
        echo "📚 API 文件: http://localhost:8000/docs"
        echo "🛑 停止服務: Ctrl+C"
        echo ""
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        echo "🔄 啟動生產模式..."
        echo "📍 服務地址: http://localhost:8000"
        echo "📚 API 文件: http://localhost:8000/docs"
        echo "🛑 停止服務: Ctrl+C"
        echo ""
        uvicorn app.main:app --host 0.0.0.0 --port 8000
        ;;
    3)
        echo "🔄 啟動除錯模式..."
        echo "📍 服務地址: http://localhost:8000"
        echo "📚 API 文件: http://localhost:8000/docs"
        echo "🛑 停止服務: Ctrl+C"
        echo ""
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
        ;;
    4)
        echo "🔄 自訂設定模式..."
        read -p "請輸入主機 (預設: 0.0.0.0): " host
        host=${host:-0.0.0.0}
        
        read -p "請輸入埠號 (預設: 8000): " port
        port=${port:-8000}
        
        read -p "是否啟用熱重載? (y/n, 預設: y): " reload
        reload=${reload:-y}
        
        reload_flag=""
        if [ "$reload" = "y" ] || [ "$reload" = "Y" ]; then
            reload_flag="--reload"
        fi
        
        echo "🔄 啟動自訂模式..."
        echo "📍 服務地址: http://$host:$port"
        echo "📚 API 文件: http://$host:$port/docs"
        echo "🛑 停止服務: Ctrl+C"
        echo ""
        uvicorn app.main:app $reload_flag --host $host --port $port
        ;;
    *)
        echo "❌ 無效選項"
        exit 1
        ;;
esac 