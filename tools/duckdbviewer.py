#!/usr/bin/env python3
"""
DuckDB 檢視器
用於檢視 sales_specs.db 資料庫中的資料
"""

import os
import sys
import duckdb
import pandas as pd
from pathlib import Path

class DuckDBViewer:
    def __init__(self):
        self.db_file = "../backend/sales_specs.db"
        self.table_name = "specs"
        
    def check_database_exists(self):
        """檢查資料庫檔案是否存在"""
        if not os.path.exists(self.db_file):
            print(f"❌ 資料庫檔案不存在: {self.db_file}")
            return False
        return True
    
    def get_record_count(self):
        """取得記錄總數"""
        try:
            with duckdb.connect(database=self.db_file, read_only=True) as con:
                result = con.execute(f"SELECT COUNT(*) as total FROM {self.table_name}").fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"❌ 取得記錄數失敗: {e}")
            return 0
    
    def get_table_schema(self):
        """取得表格結構"""
        try:
            with duckdb.connect(database=self.db_file, read_only=True) as con:
                schema = con.execute(f"DESCRIBE {self.table_name}").fetchall()
                return schema
        except Exception as e:
            print(f"❌ 取得表格結構失敗: {e}")
            return []
    
    def get_all_records(self, limit=None):
        """取得所有記錄"""
        try:
            with duckdb.connect(database=self.db_file, read_only=True) as con:
                if limit:
                    query = f"SELECT * FROM {self.table_name} LIMIT {limit}"
                else:
                    query = f"SELECT * FROM {self.table_name}"
                
                result = con.execute(query).fetchall()
                columns = [desc[0] for desc in con.description]
                return result, columns
        except Exception as e:
            print(f"❌ 取得記錄失敗: {e}")
            return [], []
    
    def get_records_by_modeltype(self, modeltype):
        """根據 modeltype 查詢記錄"""
        try:
            with duckdb.connect(database=self.db_file, read_only=True) as con:
                query = f"SELECT * FROM {self.table_name} WHERE modeltype = ?"
                result = con.execute(query, [modeltype]).fetchall()
                columns = [desc[0] for desc in con.description]
                return result, columns
        except Exception as e:
            print(f"❌ 查詢記錄失敗: {e}")
            return [], []
    
    def display_record_summary(self):
        """顯示記錄摘要"""
        print("=" * 80)
        print("📊 DuckDB 資料庫摘要")
        print("=" * 80)
        
        if not self.check_database_exists():
            return
        
        # 取得記錄數
        count = self.get_record_count()
        print(f"📈 總記錄數: {count}")
        
        if count == 0:
            print("📭 資料庫中沒有記錄")
            return
        
        # 取得表格結構
        schema = self.get_table_schema()
        print(f"📋 欄位數: {len(schema)}")
        
        # 顯示欄位資訊
        print("\n📋 欄位結構:")
        for i, (col_name, col_type, _, _, _, _) in enumerate(schema, 1):
            print(f"  {i:2d}. {col_name:<20} ({col_type})")
    
    def display_all_records(self, limit=10):
        """顯示所有記錄"""
        print("\n" + "=" * 80)
        print(f"📋 顯示前 {limit} 筆記錄")
        print("=" * 80)
        
        records, columns = self.get_all_records(limit)
        
        if not records:
            print("📭 沒有記錄可顯示")
            return
        
        # 顯示記錄
        for i, record in enumerate(records, 1):
            print(f"\n📄 記錄 {i}:")
            print("-" * 40)
            for j, (col_name, value) in enumerate(zip(columns, record)):
                # 限制顯示長度
                display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"  {col_name:<20}: {display_value}")
    
    def display_records_by_modeltype(self, modeltype):
        """顯示特定 modeltype 的記錄"""
        print(f"\n" + "=" * 80)
        print(f"📋 顯示 modeltype = '{modeltype}' 的記錄")
        print("=" * 80)
        
        records, columns = self.get_records_by_modeltype(modeltype)
        
        if not records:
            print(f"📭 沒有找到 modeltype = '{modeltype}' 的記錄")
            return
        
        print(f"📈 找到 {len(records)} 筆記錄")
        
        # 顯示記錄
        for i, record in enumerate(records, 1):
            print(f"\n📄 記錄 {i}:")
            print("-" * 40)
            for j, (col_name, value) in enumerate(zip(columns, record)):
                # 限制顯示長度
                display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"  {col_name:<20}: {display_value}")
    
    def export_to_csv(self, filename="duckdb_export.csv"):
        """匯出資料到 CSV 檔案"""
        try:
            with duckdb.connect(database=self.db_file, read_only=True) as con:
                df = con.execute(f"SELECT * FROM {self.table_name}").df()
                df.to_csv(filename, index=False, encoding='utf-8')
                print(f"✅ 資料已匯出到: {filename}")
                print(f"📊 匯出記錄數: {len(df)}")
        except Exception as e:
            print(f"❌ 匯出失敗: {e}")
    
    def interactive_mode(self):
        """互動模式"""
        while True:
            print("\n" + "=" * 50)
            print("🔍 DuckDB 檢視器 - 互動模式")
            print("=" * 50)
            print("1. 顯示資料庫摘要")
            print("2. 顯示所有記錄 (前10筆)")
            print("3. 顯示所有記錄 (自訂數量)")
            print("4. 根據 modeltype 查詢")
            print("5. 匯出資料到 CSV")
            print("6. 退出")
            print("-" * 50)
            
            choice = input("請選擇選項 (1-6): ").strip()
            
            if choice == "1":
                self.display_record_summary()
            elif choice == "2":
                self.display_all_records(10)
            elif choice == "3":
                try:
                    limit = int(input("請輸入要顯示的記錄數量: "))
                    self.display_all_records(limit)
                except ValueError:
                    print("❌ 請輸入有效的數字")
            elif choice == "4":
                modeltype = input("請輸入 modeltype (如: 960, 928): ").strip()
                if modeltype:
                    self.display_records_by_modeltype(modeltype)
                else:
                    print("❌ 請輸入有效的 modeltype")
            elif choice == "5":
                filename = input("請輸入 CSV 檔案名稱 (預設: duckdb_export.csv): ").strip()
                if not filename:
                    filename = "duckdb_export.csv"
                self.export_to_csv(filename)
            elif choice == "6":
                print("👋 再見！")
                break
            else:
                print("❌ 無效選項，請重新選擇")

def main():
    """主函數"""
    viewer = DuckDBViewer()
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "summary":
            viewer.display_record_summary()
        elif command == "list":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            viewer.display_all_records(limit)
        elif command == "search":
            if len(sys.argv) > 2:
                modeltype = sys.argv[2]
                viewer.display_records_by_modeltype(modeltype)
            else:
                print("❌ 請提供 modeltype 參數")
        elif command == "export":
            filename = sys.argv[2] if len(sys.argv) > 2 else "duckdb_export.csv"
            viewer.export_to_csv(filename)
        else:
            print("❌ 無效命令")
            print("可用命令: summary, list [limit], search <modeltype>, export [filename]")
    else:
        # 互動模式
        viewer.interactive_mode()

if __name__ == "__main__":
    main() 