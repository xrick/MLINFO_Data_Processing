#!/bin/bash

# 修復依賴套件版本衝突腳本

echo "🔧 修復 MLINFO 後端依賴套件問題"
echo "================================"

# 檢查是否在正確的目錄
if [ ! -f "requirements.txt" ]; then
    echo "❌ 請在 backend 目錄下執行此腳本"
    exit 1
fi

echo "🔍 檢查當前環境..."

# 檢查 Python 環境
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安裝或不在 PATH 中"
    exit 1
fi

echo "✅ Python 版本: $(python --version)"

# 檢查虛擬環境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  未檢測到虛擬環境，建議使用虛擬環境"
    echo "   建立虛擬環境: python -m venv venv"
    echo "   啟動虛擬環境: source venv/bin/activate"
    echo ""
fi

echo ""
echo "🔄 開始修復依賴套件..."

# 步驟 1: 卸載衝突的套件
echo "📦 步驟 1: 卸載衝突的套件..."
pip uninstall -y huggingface-hub sentence-transformers transformers torch numpy

# 步驟 2: 清理快取
echo "🧹 步驟 2: 清理 pip 快取..."
pip cache purge

# 步驟 3: 重新安裝正確版本的套件
echo "📦 步驟 3: 安裝正確版本的套件..."
pip install huggingface-hub==0.19.4
pip install transformers==4.35.2
pip install torch>=1.13.0
pip install numpy>=1.21.0
pip install sentence-transformers==2.2.2

# 步驟 4: 安裝其他依賴
echo "📦 步驟 4: 安裝其他依賴套件..."
pip install -r requirements.txt

# 步驟 5: 驗證安裝
echo "✅ 步驟 5: 驗證安裝..."
python -c "
try:
    import sentence_transformers
    print('✅ sentence-transformers 安裝成功')
    
    from sentence_transformers import SentenceTransformer
    print('✅ SentenceTransformer 導入成功')
    
    # 測試模型載入
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print('✅ 模型載入成功')
    
    # 測試編碼
    embeddings = model.encode(['test text'])
    print(f'✅ 編碼測試成功，維度: {embeddings.shape}')
    
except Exception as e:
    print(f'❌ 驗證失敗: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 依賴套件修復完成！"
    echo "✅ 所有套件已正確安裝"
    echo "✅ 模型載入測試通過"
    echo ""
    echo "現在可以正常使用資料庫匯入功能了！"
else
    echo ""
    echo "❌ 修復失敗，請檢查錯誤訊息"
    exit 1
fi 