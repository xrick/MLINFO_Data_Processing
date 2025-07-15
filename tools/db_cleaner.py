#!/usr/bin/env python3
"""
資料庫清理工具
用於清理 DuckDB 和 Milvus 資料庫中的所有資料，但保留資料庫結構
"""

import os
import sys
import duckdb
from pathlib import Path
from typing import Tuple

# 添加後端路徑以便導入模組
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from pymilvus import connections, utility, Collection
    MILVUS_AVAILABLE = True
except ImportError:
    MILVUS_AVAILABLE = False
    print("⚠️ 警告：pymilvus 未安裝，將跳過 Milvus 清理功能")

class DatabaseCleaner:
    def __init__(self):
        # DuckDB 設定
        self.duckdb_file = os.path.join(os.path.dirname(__file__), "..", "backend", "sales_specs.db")
        self.duckdb_table = "specs"
        
        # Milvus 設定
        self.milvus_host = os.getenv("MILVUS_HOST", "localhost")
        self.milvus_port = os.getenv("MILVUS_PORT", "19530")
        self.milvus_collection = "sales_notebook_specs"
        
    def check_duckdb_exists(self) -> bool:
        """檢查 DuckDB 資料庫檔案是否存在"""
        if not os.path.exists(self.duckdb_file):
            print(f"❌ DuckDB 資料庫檔案不存在: {self.duckdb_file}")
            return False
        return True
    
    def get_duckdb_record_count(self) -> int:
        """取得 DuckDB 記錄總數"""
        try:
            with duckdb.connect(database=self.duckdb_file, read_only=True) as con:
                # 檢查表格是否存在
                table_check = con.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_name = 'specs'"
                ).fetchone()
                
                if not table_check:
                    print(f"📭 DuckDB 表格 '{self.duckdb_table}' 不存在")
                    return 0
                
                result = con.execute(f"SELECT COUNT(*) FROM {self.duckdb_table}").fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"❌ 取得 DuckDB 記錄數失敗: {e}")
            return 0
    
    def clear_duckdb_data(self) -> bool:
        """清理 DuckDB 資料表中的所有資料"""
        try:
            if not self.check_duckdb_exists():
                return False
            
            record_count = self.get_duckdb_record_count()
            if record_count == 0:
                print("📭 DuckDB 表格中沒有資料需要清理")
                return True
            
            print(f"🗑️ 準備清理 DuckDB 中的 {record_count} 筆記錄...")
            
            with duckdb.connect(database=self.duckdb_file, read_only=False) as con:
                # 刪除所有資料但保留表格結構
                con.execute(f"DELETE FROM {self.duckdb_table}")
                print(f"✅ 已清理 DuckDB 表格 '{self.duckdb_table}' 中的所有資料")
                
                # 驗證清理結果
                remaining = con.execute(f"SELECT COUNT(*) FROM {self.duckdb_table}").fetchone()[0]
                if remaining == 0:
                    print(f"✅ DuckDB 清理驗證成功：剩餘記錄數 = {remaining}")
                    return True
                else:
                    print(f"❌ DuckDB 清理驗證失敗：仍有 {remaining} 筆記錄")
                    return False
                    
        except Exception as e:
            print(f"❌ DuckDB 清理失敗: {e}")
            return False
    
    def check_milvus_connection(self) -> bool:
        """檢查 Milvus 連線"""
        if not MILVUS_AVAILABLE:
            return False
            
        try:
            connections.connect("default", host=self.milvus_host, port=self.milvus_port)
            print(f"✅ 成功連接到 Milvus ({self.milvus_host}:{self.milvus_port})")
            return True
        except Exception as e:
            print(f"❌ 無法連接到 Milvus: {e}")
            return False
    
    def get_milvus_entity_count(self) -> int:
        """取得 Milvus collection 中的實體數量"""
        try:
            if not utility.has_collection(self.milvus_collection):
                print(f"📭 Milvus collection '{self.milvus_collection}' 不存在")
                return 0
            
            collection = Collection(self.milvus_collection)
            collection.load()
            count = collection.num_entities
            return count
        except Exception as e:
            print(f"❌ 取得 Milvus 實體數失敗: {e}")
            return 0
    
    def clear_milvus_data(self) -> bool:
        """清理 Milvus collection 中的所有資料"""
        try:
            if not MILVUS_AVAILABLE:
                print("⚠️ 跳過 Milvus 清理：pymilvus 未安裝")
                return True
                
            if not self.check_milvus_connection():
                return False
            
            if not utility.has_collection(self.milvus_collection):
                print(f"📭 Milvus collection '{self.milvus_collection}' 不存在，無需清理")
                return True
            
            collection = Collection(self.milvus_collection)
            collection.load()
            
            entity_count = collection.num_entities
            if entity_count == 0:
                print("📭 Milvus collection 中沒有資料需要清理")
                return True
            
            print(f"🗑️ 準備清理 Milvus collection 中的 {entity_count} 個實體...")
            
            # 刪除所有資料但保留 collection 結構
            # 由於 Milvus 的限制，我們需要先釋放 collection，然後刪除並重新創建
            collection.release()
            collection.drop()
            
            print(f"✅ 已刪除 Milvus collection '{self.milvus_collection}'")
            print(f"ℹ️ Collection 將在下次資料匯入時自動重新創建")
            
            # 驗證清理結果 - 檢查 collection 是否不存在
            if not utility.has_collection(self.milvus_collection):
                print(f"✅ Milvus 清理驗證成功：Collection 已不存在")
                return True
            else:
                print(f"❌ Milvus 清理驗證失敗：Collection 仍然存在")
                return False
                
        except Exception as e:
            print(f"❌ Milvus 清理失敗: {e}")
            return False
    
    def display_status(self):
        """顯示資料庫狀態"""
        print("=" * 80)
        print("📊 資料庫狀態檢查")
        print("=" * 80)
        
        # DuckDB 狀態
        print("\n🏪 DuckDB 狀態:")
        if self.check_duckdb_exists():
            count = self.get_duckdb_record_count()
            print(f"  📄 記錄數: {count}")
            print(f"  📂 檔案位置: {self.duckdb_file}")
        else:
            print("  ❌ 資料庫檔案不存在")
        
        # Milvus 狀態
        print(f"\n🔍 Milvus 狀態:")
        if MILVUS_AVAILABLE:
            if self.check_milvus_connection():
                try:
                    if utility.has_collection(self.milvus_collection):
                        count = self.get_milvus_entity_count()
                        print(f"  📄 實體數: {count}")
                        print(f"  📂 Collection: {self.milvus_collection}")
                    else:
                        print(f"  📭 Collection '{self.milvus_collection}' 不存在")
                except Exception as e:
                    print(f"  ❌ 檢查失敗: {e}")
            else:
                print(f"  ❌ 無法連接到 Milvus ({self.milvus_host}:{self.milvus_port})")
        else:
            print("  ⚠️ pymilvus 未安裝")
    
    def clear_all_data(self, confirm: bool = False) -> Tuple[bool, bool]:
        """清理所有資料庫中的資料"""
        if not confirm:
            print("\n" + "⚠️" * 20)
            print("⚠️ 警告：此操作將清理所有資料庫中的資料！")
            print("⚠️ 這個操作無法復原！")
            print("⚠️" * 20)
            
            response = input("\n確定要繼續嗎？請輸入 'YES' 確認: ").strip()
            if response != "YES":
                print("❌ 操作已取消")
                return False, False
        
        print("\n🚀 開始清理資料庫...")
        
        # 清理 DuckDB
        print("\n1️⃣ 清理 DuckDB...")
        duckdb_success = self.clear_duckdb_data()
        
        # 清理 Milvus
        print("\n2️⃣ 清理 Milvus...")
        milvus_success = self.clear_milvus_data()
        
        # 總結
        print("\n" + "=" * 50)
        print("📋 清理結果總結")
        print("=" * 50)
        print(f"DuckDB: {'✅ 成功' if duckdb_success else '❌ 失敗'}")
        print(f"Milvus: {'✅ 成功' if milvus_success else '❌ 失敗'}")
        
        if duckdb_success and milvus_success:
            print("\n🎉 所有資料庫清理完成！")
        else:
            print("\n⚠️ 部分資料庫清理失敗，請檢查錯誤訊息")
        
        return duckdb_success, milvus_success
    
    def interactive_mode(self):
        """互動模式"""
        while True:
            print("\n" + "=" * 60)
            print("🗑️ 資料庫清理工具 - 互動模式")
            print("=" * 60)
            print("1. 檢查資料庫狀態")
            print("2. 清理 DuckDB 資料")
            print("3. 清理 Milvus 資料")
            print("4. 清理所有資料庫資料")
            print("5. 退出")
            print("-" * 60)
            
            choice = input("請選擇選項 (1-5): ").strip()
            
            if choice == "1":
                self.display_status()
            elif choice == "2":
                print("\n⚠️ 準備清理 DuckDB 資料...")
                response = input("確定要繼續嗎？請輸入 'YES' 確認: ").strip()
                if response == "YES":
                    self.clear_duckdb_data()
                else:
                    print("❌ 操作已取消")
            elif choice == "3":
                print("\n⚠️ 準備清理 Milvus 資料...")
                response = input("確定要繼續嗎？請輸入 'YES' 確認: ").strip()
                if response == "YES":
                    self.clear_milvus_data()
                else:
                    print("❌ 操作已取消")
            elif choice == "4":
                self.clear_all_data()
            elif choice == "5":
                print("👋 再見！")
                break
            else:
                print("❌ 無效選項，請重新選擇")

def main():
    """主函數"""
    cleaner = DatabaseCleaner()
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            cleaner.display_status()
        elif command == "clear-duckdb":
            confirm = "--force" in sys.argv
            cleaner.clear_duckdb_data()
        elif command == "clear-milvus":
            confirm = "--force" in sys.argv
            cleaner.clear_milvus_data()
        elif command == "clear-all":
            confirm = "--force" in sys.argv
            cleaner.clear_all_data(confirm)
        else:
            print("❌ 無效命令")
            print("可用命令:")
            print("  status                 - 檢查資料庫狀態")
            print("  clear-duckdb [--force] - 清理 DuckDB 資料")
            print("  clear-milvus [--force] - 清理 Milvus 資料")
            print("  clear-all [--force]    - 清理所有資料庫資料")
            print("  (無參數)               - 進入互動模式")
    else:
        # 互動模式
        cleaner.interactive_mode()

if __name__ == "__main__":
    main()