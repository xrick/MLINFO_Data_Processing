import json
import os
from typing import Dict, List, Optional
from .models import ProcessRequest
from .strategies.concrete_strategies import RuleBasedStrategy

class Parser:
    def __init__(self, request: ProcessRequest):
        self.text = request.text_content
        self.temp_regex = request.temp_regex
        self.rules = self._merge_rules(request.custom_rules)
        self.strategy = RuleBasedStrategy()

    def _load_default_rules(self) -> Dict:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, 'default_rules.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def _merge_rules(self, custom_rules: Optional[Dict[str, List[str]]]) -> Dict:
        default_rules = self._load_default_rules()
        if custom_rules:
            for key, value in custom_rules.items():
                if key in default_rules and isinstance(value, list):
                    default_rules[key] = sorted(list(set(default_rules[key] + value)))
                else:
                    default_rules[key] = value
        return default_rules

    def run(self) -> List[Dict[str, str]]:
        parsed_data = self.strategy.parse(self.text, self.rules)
        if self.temp_regex:
            pass
        return parsed_data