#!/bin/bash

# SalesRAG 整合系統停止腳本
echo "🛑 停止 SalesRAG 整合系統..."

# 檢查是否在正確的目錄
if [ ! -f "backend/app/main.py" ]; then
    echo "❌ 錯誤: 請在 MLINFO_Data_Processing 根目錄執行此腳本"
    exit 1
fi

# 停止後端服務器
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        # 等待進程結束
        for i in {1..5}; do
            if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        # 如果仍在運行，強制終止
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill -9 $BACKEND_PID 2>/dev/null
        fi
        echo "✅ 後端服務器已停止 (PID: $BACKEND_PID)"
    else
        echo "⚠️  後端服務器已經停止"
    fi
    rm -f .backend.pid
else
    echo "⚠️  未找到後端 PID 檔案"
fi

# 停止前端服務器
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        # 等待進程結束
        for i in {1..5}; do
            if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        # 如果仍在運行，強制終止
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill -9 $FRONTEND_PID 2>/dev/null
        fi
        echo "✅ 前端服務器已停止 (PID: $FRONTEND_PID)"
    else
        echo "⚠️  前端服務器已經停止"
    fi
    rm -f .frontend.pid
else
    echo "⚠️  未找到前端 PID 檔案"
fi

# 清理可能殘留的進程
echo "🧹 清理殘留進程..."
KILLED_COUNT=0

# 清理後端進程
BACKEND_PIDS=$(pgrep -f "uvicorn app.main:app")
if [ ! -z "$BACKEND_PIDS" ]; then
    echo "$BACKEND_PIDS" | xargs kill 2>/dev/null
    KILLED_COUNT=$((KILLED_COUNT + $(echo "$BACKEND_PIDS" | wc -l)))
fi

# 清理前端進程
FRONTEND_PIDS=$(pgrep -f "python.*http.server 8080")
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo "$FRONTEND_PIDS" | xargs kill 2>/dev/null
    KILLED_COUNT=$((KILLED_COUNT + $(echo "$FRONTEND_PIDS" | wc -l)))
fi

if [ $KILLED_COUNT -gt 0 ]; then
    echo "🧹 清理了 $KILLED_COUNT 個殘留進程"
fi

# 檢查端口是否被占用
echo "🔍 檢查端口狀態..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  端口 8000 仍被占用"
    PIDS=$(lsof -ti:8000)
    echo "占用進程: $PIDS"
    echo "$PIDS" | xargs kill -9 2>/dev/null
fi

if lsof -ti:8080 > /dev/null 2>&1; then
    echo "⚠️  端口 8080 仍被占用"
    PIDS=$(lsof -ti:8080)
    echo "占用進程: $PIDS"
    echo "$PIDS" | xargs kill -9 2>/dev/null
fi

# 清理日誌檔案（可選）
if [ "$1" == "--clean-logs" ]; then
    echo "🧹 清理日誌檔案..."
    rm -f backend.log frontend.log
    echo "✅ 日誌檔案已清理"
fi

echo "✅ SalesRAG 整合系統已完全停止"

# 顯示系統狀態
echo ""
echo "📊 系統狀態:"
echo "   端口 8000: $(if lsof -ti:8000 > /dev/null 2>&1; then echo "占用"; else echo "空閒"; fi)"
echo "   端口 8080: $(if lsof -ti:8080 > /dev/null 2>&1; then echo "占用"; else echo "空閒"; fi)"
echo "   後端進程: $(pgrep -f "uvicorn app.main:app" | wc -l) 個"
echo "   前端進程: $(pgrep -f "python.*http.server 8080" | wc -l) 個"