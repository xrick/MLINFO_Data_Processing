#!/bin/bash

# SalesRAG 整合系統啟動腳本
echo "🚀 啟動 SalesRAG 整合系統..."

# 檢查是否在正確的目錄
if [ ! -f "backend/app/main.py" ]; then
    echo "❌ 錯誤: 請在 MLINFO_Data_Processing 根目錄執行此腳本"
    exit 1
fi

# 檢查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤: 未找到 Python 3"
    exit 1
fi

python_version=$(python3 --version 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+' | head -1)
if [ -z "$python_version" ]; then
    echo "❌ 錯誤: 無法獲取 Python 版本"
    exit 1
fi

echo "✅ 檢測到 Python $python_version"

# 檢查並安裝依賴
echo "📦 檢查 Python 依賴..."
cd backend

if [ ! -f "requirements.txt" ]; then
    echo "❌ 錯誤: 未找到 requirements.txt"
    exit 1
fi

# 檢查 uvicorn 是否已安裝
if ! command -v uvicorn &> /dev/null; then
    echo "📦 安裝 uvicorn..."
    pip3 install uvicorn
fi

# 安裝依賴
echo "📦 安裝依賴套件..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 依賴安裝失敗"
    exit 1
fi

echo "🖥️  啟動後端服務器..."
# 在背景啟動 FastAPI 服務器
uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

echo "✅ 後端服務器已啟動 (PID: $BACKEND_PID)"

# 等待後端啟動
echo "⏳ 等待後端服務器啟動..."
sleep 5

# 檢查後端是否成功啟動
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "❌ 後端啟動失敗，請檢查 backend.log"
    cat ../backend.log
    exit 1
fi

# 測試後端連接
echo "🔍 測試後端連接..."
for i in {1..10}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ 後端服務器連接成功"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ 後端服務器連接失敗"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# 啟動前端服務器
cd ../frontend
echo "🌐 啟動前端服務器..."
python3 -m http.server 8080 > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo "✅ 前端服務器已啟動 (PID: $FRONTEND_PID)"

# 等待前端啟動
echo "⏳ 等待前端服務器啟動..."
sleep 3

# 檢查前端是否成功啟動
if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo "❌ 前端啟動失敗，請檢查 frontend.log"
    kill $BACKEND_PID 2>/dev/null
    cat ../frontend.log
    exit 1
fi

# 測試前端連接
echo "🔍 測試前端連接..."
for i in {1..5}; do
    if curl -s http://localhost:8080/ > /dev/null 2>&1; then
        echo "✅ 前端服務器連接成功"
        break
    fi
    if [ $i -eq 5 ]; then
        echo "❌ 前端服務器連接失敗"
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# 建立 PID 檔案以便後續關閉
cd ..
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "🎉 SalesRAG 整合系統啟動完成！"
echo ""
echo "📍 訪問地址:"
echo "   主頁面: http://localhost:8080/unified_index.html"
echo "   API 文檔: http://localhost:8000/docs"
echo "   系統狀態: http://localhost:8000/api/system/health"
echo ""
echo "📝 日誌檔案:"
echo "   後端日誌: backend.log"
echo "   前端日誌: frontend.log"
echo ""
echo "🛑 停止系統: ./stop_integrated_system.sh"
echo ""
echo "💡 提示: 請確保 Milvus 服務正在運行以獲得完整功能"
echo ""

# 檢查是否在背景運行
if [ "$1" != "--daemon" ]; then
    echo "按 Ctrl+C 停止系統或在新終端運行停止腳本..."
    # 設置信號處理
    trap 'echo ""; echo "🛑 正在停止系統..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo "✅ 系統已停止"; exit 0' INT TERM
    
    # 保持腳本運行
    while true; do
        # 檢查進程是否還在運行
        if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo "❌ 後端服務器意外停止"
            kill $FRONTEND_PID 2>/dev/null
            rm -f .backend.pid .frontend.pid
            exit 1
        fi
        if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo "❌ 前端服務器意外停止"
            kill $BACKEND_PID 2>/dev/null
            rm -f .backend.pid .frontend.pid
            exit 1
        fi
        sleep 5
    done
else
    echo "🔄 系統以背景模式運行"
    echo "進程 ID: 後端=$BACKEND_PID, 前端=$FRONTEND_PID"
fi