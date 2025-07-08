import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from .models import ProcessRequest
from .strategies.base_strategy import BaseParsingStrategy
from .strategies.concrete_strategies import RuleBasedStrategy

class ParseBase(ABC):
    """
    Abstract base class implementing template method pattern for parsing.
    
    This class defines the overall parsing workflow and requires subclasses
    to implement the three core phases: before_parse, in_parsing, and end_parsing.
    """
    
    def __init__(self, request: ProcessRequest):
        self.request = request
        self.text = request.text_content
        self.temp_regex = request.temp_regex
        self.custom_rules = request.custom_rules
        self.rules: Dict = {}
        self.strategy: Optional[BaseParsingStrategy] = None
        self.parsed_data: List[Dict[str, str]] = []
    
    def parse_template(self) -> List[Dict[str, str]]:
        """
        Template method that orchestrates the entire parsing workflow.
        
        This method defines the parsing algorithm structure and calls
        the three abstract methods in sequence.
        
        Returns:
            List[Dict[str, str]]: Parsed and processed data
        """
        self.before_parse()
        self.in_parsing()
        self.end_parsing()
        return self.parsed_data
    
    @abstractmethod
    def before_parse(self) -> None:
        """
        Preparation phase: Load rules, validate input, and setup parsing environment.
        
        This method should handle:
        - Loading default rules
        - Merging with custom rules
        - Input validation
        - Strategy initialization
        """
        pass
    
    @abstractmethod
    def in_parsing(self) -> None:
        """
        Core parsing phase: Execute the parsing strategy and extract structured data.
        
        This method should handle:
        - Strategy execution
        - Data extraction
        - Primary parsing logic
        """
        pass
    
    @abstractmethod
    def end_parsing(self) -> None:
        """
        Post-processing phase: Apply final transformations and cleanup.
        
        This method should handle:
        - Temporary regex processing
        - Final data transformations
        - Cleanup operations
        """
        pass

class Parser(ParseBase):
    """
    Concrete implementation of ParseBase using rule-based parsing strategy.
    
    This parser loads default rules from JSON, merges with custom rules,
    and uses RuleBasedStrategy for text parsing.
    """
    
    def __init__(self, request: ProcessRequest):
        super().__init__(request)
        # Initialization will be handled in before_parse()

    def _load_default_rules(self) -> Dict:
        """
        Load default parsing rules from JSON file.
        
        Returns:
            Dict: Default rules loaded from default_rules.json
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, 'default_rules.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading default rules: {e}")
            return {}

    def _merge_rules(self, custom_rules: Optional[Dict[str, List[str]]]) -> Dict:
        """
        Merge custom rules with default rules.
        
        Args:
            custom_rules: Optional custom rules to merge with defaults
            
        Returns:
            Dict: Merged rules with custom rules taking precedence
        """
        default_rules = self._load_default_rules()
        if custom_rules:
            for key, value in custom_rules.items():
                if key in default_rules and isinstance(value, list):
                    default_rules[key] = sorted(list(set(default_rules[key] + value)))
                else:
                    default_rules[key] = value
        return default_rules

    def run(self) -> List[Dict[str, str]]:
        """
        Main entry point for parsing. Uses the template method pattern.
        
        Returns:
            List[Dict[str, str]]: Parsed and processed data
        """
        return self.parse_template()
    
    def before_parse(self) -> None:
        """
        Preparation phase: Load and merge rules, initialize strategy.
        """
        self.rules = self._merge_rules(self.custom_rules)
        self.strategy = RuleBasedStrategy()
    
    def in_parsing(self) -> None:
        """
        Core parsing phase: Execute strategy to extract structured data.
        """
        if self.strategy:
            self.parsed_data = self.strategy.parse(self.text, self.rules)
        else:
            self.parsed_data = []
    
    def end_parsing(self) -> None:
        """
        Post-processing phase: Apply temporary regex processing if needed.
        """
        if self.temp_regex:
            # TODO: Implement temporary regex processing if needed
            pass
