#!/usr/bin/env python3
"""
快速測試腳本：基本功能驗證
使用 testdata/960.csv 進行快速測試
"""

import os
import sys
import requests
from pathlib import Path

# 添加後端目錄到 Python 路徑
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def quick_test():
    """快速測試基本功能"""
    print("🚀 快速測試開始...")
    
    # 檢查測試檔案
    test_file = "../testdata/960.csv"
    if not os.path.exists(test_file):
        print(f"❌ 測試檔案不存在: {test_file}")
        return False
    
    # 讀取測試檔案
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        print(f"✅ 成功讀取測試檔案: {len(csv_content)} 字元")
    except Exception as e:
        print(f"❌ 讀取檔案失敗: {e}")
        return False
    
    # 測試 API 端點
    api_url = "http://localhost:8000"
    
    # 測試 1: /api/process
    print("\n🔄 測試 /api/process 端點...")
    try:
        payload = {
            "text_content": csv_content,
            "file_name": "960.csv",
            "user_modeltype": "960"
        }
        
        response = requests.post(
            f"{api_url}/api/process",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            data_count = len(result.get('data', []))
            print(f"✅ /api/process 成功: {data_count} 筆記錄")
            
            # 測試 2: /api/ingest-to-db
            print("\n🔄 測試 /api/ingest-to-db 端點...")
            ingest_payload = {"data": result.get('data', [])}
            
            ingest_response = requests.post(
                f"{api_url}/api/ingest-to-db",
                json=ingest_payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if ingest_response.status_code == 200:
                ingest_result = ingest_response.json()
                print(f"✅ /api/ingest-to-db 成功")
                print(f"📊 DuckDB: {ingest_result.get('duckdb_rows_added', 0)} 筆")
                print(f"📊 Milvus: {ingest_result.get('milvus_entities_added', 0)} 筆")
                print("🎉 所有測試通過！")
                return True
            else:
                print(f"❌ /api/ingest-to-db 失敗: {ingest_response.status_code}")
                print(f"錯誤: {ingest_response.text}")
                return False
        else:
            print(f"❌ /api/process 失敗: {response.status_code}")
            print(f"錯誤: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到 API 伺服器")
        print("請確認後端服務是否正在運行: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1) 