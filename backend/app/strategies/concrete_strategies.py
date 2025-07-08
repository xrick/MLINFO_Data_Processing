import re
from typing import List, Dict
from .base_strategy import BaseParsingStrategy

class RuleBasedStrategy(BaseParsingStrategy):
    def parse(self, text: str, rules: Dict[str, List[str]]) -> List[Dict[str, str]]:
        model_names = self._extract_model_names(text, rules)
        if not model_names:
            return []

        all_models_data = []
        for model_name in model_names:
            model_data = {'modelname': model_name}
            for field, keywords in rules.items():
                if field == 'modelname': 
                    continue
                model_data[field] = self._extract_field_value(text, model_name, keywords)
            all_models_data.append(model_data)
        return all_models_data

    def _extract_field_value(self, text: str, model_name: str, keywords: List[str]) -> str:
        text_sections = re.split(r'(\n\[.*?\]\n)', text)
        for keyword in keywords:
            for i, section in enumerate(text_sections):
                if keyword.lower() in section.lower():
                    content_to_search = text_sections[i + 1] if i + 1 < len(text_sections) else ""
                    pattern = re.compile(f"^-? *{re.escape(model_name)}.*?:([^\n]+)", re.IGNORECASE | re.MULTILINE)
                    match = pattern.search(content_to_search)
                    if match:
                        return match.group(1).strip()
        return ""

    def _extract_model_names(self, text: str, rules: Dict[str, List[str]]) -> List[str]:
        model_keywords = rules.get('modelname', ['Model Names'])
        model_names = set()
        for keyword in model_keywords:
            try:
                section_pattern = re.compile(
                    f"^\\[{re.escape(keyword)}\\]$\\n([\\s\\S]*?)(?=\\n\\[|$)", 
                    re.MULTILINE | re.IGNORECASE
                )
                section_match = section_pattern.search(text)
                if section_match:
                    name_pattern = re.compile(r"-\s*([A-Z0-9]+)")
                    names = name_pattern.findall(section_match.group(1))
                    for name in names:
                        model_names.add(name)
            except re.error:
                continue
        
        if not model_names:
            potential_models = re.findall(r'\b([A-Z]{2,3}\d{3,4}[A-Z]*)\b', text)
            for model in potential_models:
                model_names.add(model)
        
        return sorted(list(model_names))
