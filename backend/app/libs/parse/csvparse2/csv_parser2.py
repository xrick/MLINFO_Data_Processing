
# import pandas as pd
import json
# import re
from typing import Any, Dict, Optional
from pathlib import Path
import csv
# import argparse

import logging

# 導入父類別
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsebase import ParseBase

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVParser2(ParseBase):

    def __init__(self):
        super().__init__()
        self.rawcsv = None
        self.datalist = None
        self._rules = None
        self._rules_file = Path(__file__).parent / "rules.json"
        self.headers = None
        self.model_count = 0
        self.model_type = None
        self.processed_result = None
        self.default_output_path = None

    def beforeParse(self, data: Any, config: Optional[Dict] = None) -> bool:
        """
        解析前準備工作
        
        Args:
            data: CSV 檔案路徑或 DataFrame
            config: 解析配置參數
            
        Returns:
            bool: 準備工作是否成功
        """
        try:
            # 設置輸入資料
            self.rawcsv = data
            
            # 載入解析規則
            self._rules = self._load_rules()
            if not self._rules:
                logger.error("無法載入解析規則")
                return False
            
            # 載入 CSV
            self.datalist = self._load_csv(self.rawcsv)
            
            # 設置標題
            self.headers = [
                rule.get("column_name", f"欄位{i+1}")
                for i, rule in enumerate(self._rules[1])
            ]
            
            # 設置模型參數
            self.model_count = self._rules[0][0]["model_count"]
            self.model_type = self._rules[0][0]["model_type"]
            self.default_output_path = self._rules[0][0].get("default_output_path", "./output.csv")
            
            logger.info(f"解析前準備完成 - 模型數量: {self.model_count}, 類型: {self.model_type}")
            return True
            
        except Exception as e:
            logger.error(f"解析前準備失敗: {str(e)}")
            return False
         

    def inParse(self):
        """
        主要解析邏輯
        
        Returns:
            List[Dict]: 解析結果列表
        """
        self.collect_results()
        return self.processed_result

    
    def endParse(self) -> bool:
        """
        解析後處理工作
        
        Returns:
            bool: 後處理是否成功
        """
        try:
            if self.processed_result:
                self.write_csv()
                logger.info("解析後處理完成")
                return True
            else:
                logger.error("無解析結果可處理")
                return False
        except Exception as e:
            logger.error(f"解析後處理失敗: {str(e)}")
            return False
        
    
    def _load_rules(self):
        with open(self._rules_file, "r", encoding="utf-8") as f:
            return json.load(f)
        


    def _load_csv(self, file_path):
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            return list(csv.reader(f))



    def collect_results(self):
        result_rows = [[] for _ in range(self.model_count)]

        for rule_index, rule in enumerate(self._rules[1]):
            keywords = rule.get("keywords", [])
            logic = rule.get("logic", "OR").upper()
            rowspan = rule.get("rowspan", 1)
            column_name = rule.get("column_name", f"欄位{rule_index+1}")

            matched_blocks = []

            for i, row in enumerate(self.datalist):
                if logic == "AND":
                    match = True
                    for kw in keywords:
                        if not any(kw.lower() in str(cell).lower() for cell in row):
                            match = False
                            break
                else:
                    match = False
                    for kw in keywords:
                        if any(kw.lower() in str(cell).lower() for cell in row):
                            match = True
                            break

                if match:
                    block = self.datalist[i:i + rowspan]
                    matched_blocks.append((i, block))

            if len(matched_blocks) == 0:
                print(f"⚠️ 規則 {rule_index+1} - {column_name}: 找不到關鍵字 {keywords}，全欄填空白")
                for idx in range(self.model_count):
                    result_rows[idx].append("")
            else:
                if len(matched_blocks) > 1:
                    print(f"⚠️ 警告：規則 {rule_index+1} - {column_name} 找到超過一個匹配（共 {len(matched_blocks)} 個），僅使用第一筆！")
                first_index, block = matched_blocks[0]
                print(f"🔍 規則 {rule_index+1} - {column_name}: 找到關鍵字 {keywords} 於第 {first_index+1} 行")

                for idx in range(self.model_count):
                    col_index = 2 + idx
                    if all(col_index < len(row) for row in block):
                        lines = []
                        for r in block:
                            value = r[col_index].strip()
                            prefix_label = r[1].strip() if len(r) > 1 else ""
                            if prefix_label:
                                lines.append(f"{prefix_label}: {value}")
                            else:
                                lines.append(value)
                        result = "\n".join(lines).strip()
                        result_rows[idx].append(result)
                        print(f"  → 機種{idx+1}: {result}")
                    else:
                        result_rows[idx].append("")
                        print(f"  → 機種{idx+1}: ⚠️警告：該機種此處無資料")

        self.processed_result=result_rows
    

    # def write_csv(self, output_path, result_rows, headers, model_type):
    def write_csv(self):
        headers = ["modeltype"] + self.headers
        with open(self.default_output_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in self.processed_result:
                writer.writerow([self.model_type] + row)
        print(f"✅ 已輸出至：{self.default_output_path}")

# def main():
#     parser = argparse.ArgumentParser(description="根據 JSON 規則搜尋 CSV 並轉為每機種一列格式（v4 + prefix 每列讀取）")
#     parser.add_argument("csv_path", help="輸入CSV")
#     parser.add_argument("json_path", help="規則JSON")
#     parser.add_argument("--model_count", type=int, required=True, help="幾個機種")
#     parser.add_argument("--model_type", type=str, required=True, help="共用的 model type 字串")
#     parser.add_argument("--output_csv", required=True, help="輸出CSV檔名")

#     args = parser.parse_args()

#     reader = load_csv(args.csv_path)
#     rules = load_rules(args.json_path)
#     results = collect_results(reader, rules, args.model_count)

#     headers = [
#         rule.get("column_name").strip() if rule.get("column_name") and rule.get("column_name").strip() != "" else f"欄位{i+1}"
#         for i, rule in enumerate(rules)
#     ]
#     write_csv(args.output_csv, results, headers, args.model_type)

# if __name__ == "__main__":
#     main()