#!/usr/bin/env python3
"""
測試程式：完整的資料匯入流程測試
測試範圍：CSV 解析 → 資料庫匯入 (DuckDB + Milvus)
測試資料：testdata/960.csv
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# 添加後端目錄到 Python 路徑
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.csv_processor2 import CSVProcessor2
from app.db_ingestor import DBIngestor

class TestIngestFlow:
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
        self.test_csv_path = "../testdata/960.csv"
        self.processor = CSVProcessor2()
        self.ingestor = DBIngestor()
        
    def test_1_csv_parsing(self):
        """測試 1: CSV 解析功能"""
        print("=" * 60)
        print("測試 1: CSV 解析功能")
        print("=" * 60)
        
        try:
            # 讀取測試 CSV 檔案
            with open(self.test_csv_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            print(f"✅ 成功讀取測試檔案: {self.test_csv_path}")
            print(f"📄 檔案大小: {len(csv_content)} 字元")
            
            # 使用 CSVProcessor2 解析
            result = self.processor.process_csv_content(
                csv_content=csv_content,
                custom_rules=None
            )
            
            print(f"✅ CSV 解析成功")
            print(f"📊 解析結果: {len(result)} 筆記錄")
            
            # 顯示前 3 筆記錄的結構
            if result:
                print("\n📋 前 3 筆記錄結構:")
                for i, record in enumerate(result[:3]):
                    print(f"記錄 {i+1}: {len(record)} 個欄位")
                    for key, value in list(record.items())[:5]:  # 只顯示前 5 個欄位
                        print(f"  {key}: {value[:50]}{'...' if len(str(value)) > 50 else ''}")
                    print()
            
            return result
            
        except Exception as e:
            print(f"❌ CSV 解析失敗: {e}")
            return None
    
    def test_2_api_process_endpoint(self):
        """測試 2: API /api/process 端點"""
        print("=" * 60)
        print("測試 2: API /api/process 端點")
        print("=" * 60)
        
        try:
            # 讀取測試 CSV 檔案
            with open(self.test_csv_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            # 呼叫 API
            payload = {
                "text_content": csv_content,
                "custom_rules": None,
                "temp_regex": None,
                "file_name": "960.csv",
                "user_modeltype": "960"  # 明確指定 modeltype
            }
            
            print("🔄 呼叫 /api/process API...")
            response = requests.post(
                f"{self.api_base_url}/api/process",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API 呼叫成功")
                print(f"📊 解析結果: {len(result.get('data', []))} 筆記錄")
                
                # 檢查是否需要 modeltype 輸入
                if result.get('require_modeltype_input'):
                    print("⚠️  需要用戶輸入 modeltype")
                else:
                    print("✅ modeltype 自動判斷成功")
                
                return result.get('data', [])
            else:
                print(f"❌ API 呼叫失敗: HTTP {response.status_code}")
                print(f"錯誤訊息: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ 無法連接到 API 伺服器，請確認後端服務是否正在運行")
            return None
        except Exception as e:
            print(f"❌ API 測試失敗: {e}")
            return None
    
    def test_3_database_ingestion(self, data):
        """測試 3: 資料庫匯入功能"""
        print("=" * 60)
        print("測試 3: 資料庫匯入功能")
        print("=" * 60)
        
        if not data:
            print("❌ 沒有資料可以匯入")
            return False
        
        try:
            print(f"🔄 開始匯入 {len(data)} 筆記錄到資料庫...")
            
            # 使用 DBIngestor 匯入資料
            duckdb_count, milvus_count = self.ingestor.ingest(data)
            
            print("✅ 資料庫匯入成功")
            print(f"📊 DuckDB: {duckdb_count} 筆記錄")
            print(f"📊 Milvus: {milvus_count} 筆記錄")
            
            return True
            
        except Exception as e:
            print(f"❌ 資料庫匯入失敗: {e}")
            return False
    
    def test_4_api_ingest_endpoint(self, data):
        """測試 4: API /api/ingest-to-db 端點"""
        print("=" * 60)
        print("測試 4: API /api/ingest-to-db 端點")
        print("=" * 60)
        
        if not data:
            print("❌ 沒有資料可以匯入")
            return False
        
        try:
            payload = {"data": data}
            
            print("🔄 呼叫 /api/ingest-to-db API...")
            response = requests.post(
                f"{self.api_base_url}/api/ingest-to-db",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # 增加超時時間，因為向量嵌入需要時間
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API 呼叫成功")
                print(f"📊 DuckDB 新增: {result.get('duckdb_rows_added', 0)} 筆")
                print(f"📊 Milvus 新增: {result.get('milvus_entities_added', 0)} 筆")
                print(f"💬 訊息: {result.get('message', '')}")
                return True
            else:
                print(f"❌ API 呼叫失敗: HTTP {response.status_code}")
                print(f"錯誤訊息: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ 無法連接到 API 伺服器，請確認後端服務是否正在運行")
            return False
        except Exception as e:
            print(f"❌ API 測試失敗: {e}")
            return False
    
    def test_5_full_workflow(self):
        """測試 5: 完整工作流程測試"""
        print("=" * 60)
        print("測試 5: 完整工作流程測試")
        print("=" * 60)
        
        print("🔄 開始完整工作流程測試...")
        start_time = time.time()
        
        # 步驟 1: CSV 解析
        parsed_data = self.test_1_csv_parsing()
        if not parsed_data:
            print("❌ CSV 解析失敗，停止測試")
            return False
        
        # 步驟 2: API 處理
        api_data = self.test_2_api_process_endpoint()
        if not api_data:
            print("❌ API 處理失敗，停止測試")
            return False
        
        # 步驟 3: 直接資料庫匯入
        db_success = self.test_3_database_ingestion(api_data)
        
        # 步驟 4: API 資料庫匯入
        api_db_success = self.test_4_api_ingest_endpoint(api_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 完整工作流程測試結果")
        print("=" * 60)
        print(f"⏱️  總執行時間: {duration:.2f} 秒")
        print(f"✅ CSV 解析: {'成功' if parsed_data else '失敗'}")
        print(f"✅ API 處理: {'成功' if api_data else '失敗'}")
        print(f"✅ 直接資料庫匯入: {'成功' if db_success else '失敗'}")
        print(f"✅ API 資料庫匯入: {'成功' if api_db_success else '失敗'}")
        
        if all([parsed_data, api_data, db_success, api_db_success]):
            print("\n🎉 所有測試通過！完整工作流程正常運作")
            return True
        else:
            print("\n⚠️  部分測試失敗，請檢查錯誤訊息")
            return False
    
    def run_all_tests(self):
        """執行所有測試"""
        print("🚀 開始執行資料匯入流程測試")
        print(f"📁 測試檔案: {self.test_csv_path}")
        print(f"🌐 API 端點: {self.api_base_url}")
        print()
        
        # 檢查測試檔案是否存在
        if not os.path.exists(self.test_csv_path):
            print(f"❌ 測試檔案不存在: {self.test_csv_path}")
            return False
        
        # 執行完整工作流程測試
        success = self.test_5_full_workflow()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 測試完成：所有功能正常運作")
        else:
            print("❌ 測試完成：發現問題，請檢查上述錯誤訊息")
        print("=" * 60)
        
        return success

def main():
    """主函數"""
    tester = TestIngestFlow()
    success = tester.run_all_tests()
    
    # 返回適當的退出碼
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 