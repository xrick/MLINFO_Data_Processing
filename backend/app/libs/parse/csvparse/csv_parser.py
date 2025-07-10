import pandas as pd
import json
import re
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

# 導入父類別
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsebase import ParseBase

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVParser(ParseBase):
    """
    CSV 檔案解析器
    
    專門用於解析產品規格 CSV 檔案，提取模型資訊、硬體配置等資料
    """
    
    def __init__(self):
        """初始化 CSV 解析器"""
        super().__init__()
        self._df = None
        self._rules = None
        self._parsed_data = []
        self._rules_file = Path(__file__).parent / "csvparse_rules.json"
    
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
            # 載入解析規則
            if not self._load_rules():
                logger.error("無法載入解析規則")
                return False
            
            # 載入 CSV 資料
            if isinstance(data, str):
                # 如果是檔案路徑
                self._df = pd.read_csv(data, encoding='utf-8')
            elif isinstance(data, pd.DataFrame):
                # 如果已經是 DataFrame
                self._df = data
            else:
                logger.error("不支援的資料格式")
                return False
            
            # 儲存配置
            if config:
                self.config = config
            
            # 基本資料驗證
            if self._df.empty:
                logger.error("CSV 檔案為空")
                return False
            
            logger.info(f"成功載入 CSV 資料，共 {len(self._df)} 行")
            return True
            
        except Exception as e:
            logger.error(f"解析前準備失敗: {str(e)}")
            return False
    
    def inParse(self) -> List[Dict]:
        """
        主要解析邏輯
        
        Returns:
            List[Dict]: 解析結果列表
        """
        try:
            results = []
            
            # 1. 提取模型資訊
            model_data = self._extract_model_info()
            if model_data:
                results.extend(model_data)
            
            # 2. 提取版本資訊
            version_data = self._extract_version_info()
            if version_data:
                results.extend(version_data)
            
            # 3. 提取硬體配置
            hardware_data = self._extract_hardware_info()
            if hardware_data:
                results.extend(hardware_data)
            
            # 4. 提取顯示器資訊
            display_data = self._extract_display_info()
            if display_data:
                results.extend(display_data)
            
            # 5. 提取連接性資訊
            connectivity_data = self._extract_connectivity_info()
            if connectivity_data:
                results.extend(connectivity_data)
            
            # 6. 提取電池資訊
            battery_data = self._extract_battery_info()
            if battery_data:
                results.extend(battery_data)
            
            # 7. 提取尺寸資訊
            dimension_data = self._extract_dimension_info()
            if dimension_data:
                results.extend(dimension_data)
            
            # 8. 提取開發時程
            timeline_data = self._extract_timeline_info()
            if timeline_data:
                results.extend(timeline_data)
            
            # 9. 提取軟體資訊
            software_data = self._extract_software_info()
            if software_data:
                results.extend(software_data)
            
            # 10. 提取認證資訊
            cert_data = self._extract_certification_info()
            if cert_data:
                results.extend(cert_data)
            
            self._parsed_data = results
            logger.info(f"解析完成，共提取 {len(results)} 條記錄")
            return results
            
        except Exception as e:
            logger.error(f"解析過程發生錯誤: {str(e)}")
            return []
    
    def endParse(self) -> bool:
        """
        解析後處理工作
        
        Returns:
            bool: 後處理是否成功
        """
        try:
            # 資料清理
            self._clean_data()
            
            # 資料驗證
            if not self._validate_data():
                logger.warning("資料驗證失敗，但繼續處理")
            
            # 儲存解析結果
            self.data = self._parsed_data
            
            logger.info("解析後處理完成")
            return True
            
        except Exception as e:
            logger.error(f"解析後處理失敗: {str(e)}")
            return False
    
    def _load_rules(self) -> bool:
        """載入解析規則"""
        try:
            with open(self._rules_file, 'r', encoding='utf-8') as f:
                self._rules = json.load(f)
            return True
        except Exception as e:
            logger.error(f"載入規則檔案失敗: {str(e)}")
            return False
    
    def _extract_model_info(self) -> List[Dict]:
        """提取模型資訊"""
        results = []
        rules = self._rules['csv_parsing_rules']['model_extraction']
        
        for col in self._df.columns:
            if any(pattern.lower() in col.lower() for pattern in rules['model_name_patterns']):
                for idx, value in enumerate(self._df[col]):
                    if pd.notna(value) and str(value).strip():
                        # 使用正則表達式提取模型名稱
                        for regex in rules['model_regex']:
                            matches = re.findall(regex, str(value))
                            for match in matches:
                                results.append({
                                    'category': 'model_info',
                                    'type': 'model_name',
                                    'value': match,
                                    'source': f"{col}:{idx}",
                                    'raw_data': str(value)
                                })
        
        return results
    
    def _extract_version_info(self) -> List[Dict]:
        """提取版本資訊"""
        results = []
        rules = self._rules['csv_parsing_rules']['version_extraction']
        
        for col in self._df.columns:
            if any(pattern.lower() in col.lower() for pattern in rules['version_patterns']):
                for idx, value in enumerate(self._df[col]):
                    if pd.notna(value) and str(value).strip():
                        for regex in rules['version_regex']:
                            matches = re.findall(regex, str(value))
                            for match in matches:
                                results.append({
                                    'category': 'version_info',
                                    'type': 'version',
                                    'value': match,
                                    'source': f"{col}:{idx}",
                                    'raw_data': str(value)
                                })
        
        return results
    
    def _extract_hardware_info(self) -> List[Dict]:
        """提取硬體配置資訊"""
        results = []
        rules = self._rules['csv_parsing_rules']['hardware_extraction']
        
        for category, category_rules in rules.items():
            for col in self._df.columns:
                if any(pattern.lower() in col.lower() for pattern in category_rules.get('patterns', [])):
                    for idx, value in enumerate(self._df[col]):
                        if pd.notna(value) and str(value).strip():
                            for regex in category_rules.get('regex', []):
                                matches = re.findall(regex, str(value), re.IGNORECASE)
                                for match in matches:
                                    results.append({
                                        'category': 'hardware_info',
                                        'type': category.replace('_patterns', ''),
                                        'value': match,
                                        'source': f"{col}:{idx}",
                                        'raw_data': str(value)
                                    })
        
        return results
    
    def _extract_display_info(self) -> List[Dict]:
        """提取顯示器資訊"""
        results = []
        rules = self._rules['csv_parsing_rules']['display_extraction']
        
        for category, category_rules in rules.items():
            for col in self._df.columns:
                if any(pattern.lower() in col.lower() for pattern in category_rules.get('patterns', [])):
                    for idx, value in enumerate(self._df[col]):
                        if pd.notna(value) and str(value).strip():
                            for regex in category_rules.get('regex', []):
                                matches = re.findall(regex, str(value), re.IGNORECASE)
                                for match in matches:
                                    results.append({
                                        'category': 'display_info',
                                        'type': category.replace('_patterns', ''),
                                        'value': match,
                                        'source': f"{col}:{idx}",
                                        'raw_data': str(value)
                                    })
        
        return results
    
    def _extract_connectivity_info(self) -> List[Dict]:
        """提取連接性資訊"""
        results = []
        rules = self._rules['csv_parsing_rules']['connectivity_extraction']
        
        for category, category_rules in rules.items():
            for col in self._df.columns:
                if any(pattern.lower() in col.lower() for pattern in category_rules.get('patterns', [])):
                    for idx, value in enumerate(self._df[col]):
                        if pd.notna(value) and str(value).strip():
                            for regex in category_rules.get('regex', []):
                                matches = re.findall(regex, str(value), re.IGNORECASE)
                                for match in matches:
                                    results.append({
                                        'category': 'connectivity_info',
                                        'type': category.replace('_patterns', ''),
                                        'value': match,
                                        'source': f"{col}:{idx}",
                                        'raw_data': str(value)
                                    })
        
        return results
    
    def _extract_battery_info(self) -> List[Dict]:
        """提取電池資訊"""
        results = []
        rules = self._rules['csv_parsing_rules']['battery_extraction']
        
        for col in self._df.columns:
            if any(pattern.lower() in col.lower() for pattern in rules['battery_patterns']):
                for idx, value in enumerate(self._df[col]):
                    if pd.notna(value) and str(value).strip():
                        for regex in rules['battery_regex']:
                            matches = re.findall(regex, str(value))
                            for match in matches:
                                results.append({
                                    'category': 'battery_info',
                                    'type': 'battery_spec',
                                    'value': match,
                                    'source': f"{col}:{idx}",
                                    'raw_data': str(value)
                                })
        
        return results
    
    def _extract_dimension_info(self) -> List[Dict]:
        """提取尺寸資訊"""
        results = []
        rules = self._rules['csv_parsing_rules']['dimension_extraction']
        
        for col in self._df.columns:
            if any(pattern.lower() in col.lower() for pattern in rules['dimension_patterns']):
                for idx, value in enumerate(self._df[col]):
                    if pd.notna(value) and str(value).strip():
                        for regex in rules['dimension_regex']:
                            matches = re.findall(regex, str(value))
                            for match in matches:
                                results.append({
                                    'category': 'dimension_info',
                                    'type': 'dimension',
                                    'value': match,
                                    'source': f"{col}:{idx}",
                                    'raw_data': str(value)
                                })
        
        return results
    
    def _extract_timeline_info(self) -> List[Dict]:
        """提取開發時程資訊"""
        results = []
        rules = self._rules['csv_parsing_rules']['development_extraction']
        
        for col in self._df.columns:
            if any(pattern.lower() in col.lower() for pattern in rules['timeline_patterns']):
                for idx, value in enumerate(self._df[col]):
                    if pd.notna(value) and str(value).strip():
                        for regex in rules['timeline_regex']:
                            matches = re.findall(regex, str(value))
                            for match in matches:
                                results.append({
                                    'category': 'timeline_info',
                                    'type': 'development_stage',
                                    'value': match,
                                    'source': f"{col}:{idx}",
                                    'raw_data': str(value)
                                })
        
        return results
    
    def _extract_software_info(self) -> List[Dict]:
        """提取軟體資訊"""
        results = []
        rules = self._rules['csv_parsing_rules']['software_extraction']
        
        for col in self._df.columns:
            if any(pattern.lower() in col.lower() for pattern in rules['os_patterns']):
                for idx, value in enumerate(self._df[col]):
                    if pd.notna(value) and str(value).strip():
                        for regex in rules['os_regex']:
                            matches = re.findall(regex, str(value), re.IGNORECASE)
                            for match in matches:
                                results.append({
                                    'category': 'software_info',
                                    'type': 'operating_system',
                                    'value': match,
                                    'source': f"{col}:{idx}",
                                    'raw_data': str(value)
                                })
        
        return results
    
    def _extract_certification_info(self) -> List[Dict]:
        """提取認證資訊"""
        results = []
        rules = self._rules['csv_parsing_rules']['certification_extraction']
        
        for col in self._df.columns:
            if any(pattern.lower() in col.lower() for pattern in rules['cert_patterns']):
                for idx, value in enumerate(self._df[col]):
                    if pd.notna(value) and str(value).strip():
                        for regex in rules['cert_regex']:
                            matches = re.findall(regex, str(value), re.IGNORECASE)
                            for match in matches:
                                results.append({
                                    'category': 'certification_info',
                                    'type': 'certification',
                                    'value': match,
                                    'source': f"{col}:{idx}",
                                    'raw_data': str(value)
                                })
        
        return results
    
    def _clean_data(self):
        """清理解析後的資料"""
        if not self._parsed_data:
            return
        
        remove_patterns = self._rules['data_cleaning_rules']['remove_patterns']
        
        for item in self._parsed_data:
            # 移除不需要的值
            if item['value'] in remove_patterns:
                item['value'] = None
                continue
            
            # 清理空白字元
            if isinstance(item['value'], str):
                item['value'] = re.sub(r'\s+', ' ', item['value']).strip()
    
    def _validate_data(self) -> bool:
        """驗證解析後的資料"""
        if not self._parsed_data:
            return False
        
        valid_count = sum(1 for item in self._parsed_data if item['value'] is not None)
        total_count = len(self._parsed_data)
        
        logger.info(f"資料驗證: {valid_count}/{total_count} 條記錄有效")
        return valid_count > 0
    
    def get_parsed_data(self) -> List[Dict]:
        """獲取解析後的資料"""
        return self._parsed_data
    
    def export_to_json(self, output_path: str) -> bool:
        """匯出解析結果到 JSON 檔案"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self._parsed_data, f, ensure_ascii=False, indent=2)
            logger.info(f"解析結果已匯出到: {output_path}")
            return True
        except Exception as e:
            logger.error(f"匯出失敗: {str(e)}")
            return False 