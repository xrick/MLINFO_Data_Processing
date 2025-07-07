from abc import ABC, abstractmethod
from typing import List, Dict

class BaseParsingStrategy(ABC):
    @abstractmethod
    def parse(self, text: str, rules: Dict[str, List[str]]) -> List[Dict[str, str]]:
        pass