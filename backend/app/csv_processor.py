import os
import tempfile
from typing import List, Dict, Optional
from pathlib import Path
import logging

from .libs.parse.csvparse2.csv_parser2 import CSVParser2

logger = logging.getLogger(__name__)

class CSVProcessor:
    """CSV 處理器，使用 csv_parser2 解析 CSV 檔案"""
    
    def __init__(self):
        self.parser = CSVParser2()
    
    def process_csv_content(self, csv_content: str, custom_rules: Optional[Dict] = None) -> List[Dict[str, str]]:
        """
        處理 CSV 內容並返回結構化資料
        
        Args:
            csv_content: CSV 檔案內容字串
            custom_rules: 自訂解析規則 (目前未使用，保留擴充性)
            
        Returns:
            List[Dict]: 解析後的結構化資料
        """
        try:
            # 創建臨時檔案存放 CSV 內容
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(csv_content)
                temp_file_path = temp_file.name
            
            try:
                # 使用 csv_parser2 解析
                logger.info(f"開始使用 csv_parser2 解析檔案: {temp_file_path}")
                
                # 執行解析流程
                success = self.parser.beforeParse(temp_file_path)
                if not success:
                    raise Exception("CSV 解析前準備失敗")
                
                # 執行主要解析
                parsed_data = self.parser.inParse()
                if not parsed_data:
                    raise Exception("CSV 解析無結果")
                
                # 執行後處理
                success = self.parser.endParse()
                if not success:
                    logger.warning("CSV 解析後處理失敗，但繼續執行")
                
                logger.info(f"CSV 解析完成，共解析 {len(parsed_data)} 筆記錄")
                return parsed_data
                
            finally:
                # 清理臨時檔案
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"CSV 處理失敗: {str(e)}")
            raise Exception(f"CSV 處理錯誤: {str(e)}")
    
    def process_csv_file(self, file_path: str, custom_rules: Optional[Dict] = None) -> List[Dict[str, str]]:
        """
        處理 CSV 檔案並返回結構化資料
        
        Args:
            file_path: CSV 檔案路徑
            custom_rules: 自訂解析規則
            
        Returns:
            List[Dict]: 解析後的結構化資料
        """
        try:
            if not os.path.exists(file_path):
                raise Exception(f"檔案不存在: {file_path}")
            
            logger.info(f"開始處理 CSV 檔案: {file_path}")
            
            # 執行解析流程
            success = self.parser.beforeParse(file_path)
            if not success:
                raise Exception("CSV 解析前準備失敗")
            
            # 執行主要解析
            parsed_data = self.parser.inParse()
            if not parsed_data:
                raise Exception("CSV 解析無結果")
            
            # 執行後處理
            success = self.parser.endParse()
            if not success:
                logger.warning("CSV 解析後處理失敗，但繼續執行")
            
            logger.info(f"CSV 檔案處理完成，共解析 {len(parsed_data)} 筆記錄")
            return parsed_data
            
        except Exception as e:
            logger.error(f"CSV 檔案處理失敗: {str(e)}")
            raise Exception(f"CSV 檔案處理錯誤: {str(e)}")
    
    def get_parser_info(self) -> Dict[str, any]:
        """
        獲取解析器資訊
        
        Returns:
            Dict: 解析器配置資訊
        """
        try:
            # 載入規則檔案獲取基本資訊
            rules_file = Path(__file__).parent / "libs/parse/csvparse2/rules.json"
            
            import json
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            config = rules[0][0] if rules and len(rules) > 0 and len(rules[0]) > 0 else {}
            rule_count = len(rules[1]) if len(rules) > 1 else 0
            
            return {
                "parser": "csv_parser2",
                "model_count": config.get("model_count", 0),
                "model_type": config.get("model_type", "unknown"),
                "rule_count": rule_count,
                "rules_file": str(rules_file),
                "default_output_path": config.get("default_output_path", "./output.csv")
            }
            
        except Exception as e:
            logger.error(f"獲取解析器資訊失敗: {str(e)}")
            return {
                "parser": "csv_parser2",
                "error": str(e)
            }