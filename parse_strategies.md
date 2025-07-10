# Parse Strategies Documentation

This document provides a comprehensive overview of the parsing strategies implemented in the MLINFO Data Processing application, designed for extracting and structuring laptop/notebook specifications from text files.

## Table of Contents

1. [Current Architecture Overview](#current-architecture-overview)
2. [Parsing Pipeline](#parsing-pipeline)
3. [Strategy Implementation Details](#strategy-implementation-details)
4. [Extension Points & Future Strategies](#extension-points--future-strategies)
5. [Performance & Optimization Considerations](#performance--optimization-considerations)
6. [Usage Examples](#usage-examples)

---

## Current Architecture Overview

The parsing system implements a **Strategy Pattern** combined with a **Template Method Pattern** to provide a flexible and extensible architecture for text processing.

### Core Components

#### 1. BaseParsingStrategy (Abstract Interface)
**Location**: `backend/app/strategies/base_strategy.py:4-8`

```python
class BaseParsingStrategy(ABC):
    @abstractmethod
    def parse(self, text: str, rules: Dict[str, List[str]]) -> List[Dict[str, str]]:
        """Parse text using the given rules and return structured data."""
        pass
```

**Purpose**: Defines the contract for all parsing strategies, ensuring consistency across implementations.

#### 2. ParseBase (Abstract Template)
**Location**: `backend/app/parser.py:9-76`

**Template Method Pattern**: Orchestrates the parsing workflow through three phases:
- `before_parse()`: Preparation and rule loading
- `in_parsing()`: Core parsing execution
- `end_parsing()`: Post-processing and cleanup

#### 3. Parser (Concrete Implementation)
**Location**: `backend/app/parser.py:78-157`

**Current Implementation**: Uses `RuleBasedStrategy` with JSON rule configuration.

### Rule System Architecture

#### Default Rules Structure
**Location**: `backend/app/default_rules.json`

```json
{
    "modelname": ["Model Information", "Model Names"],
    "cpu": ["CPU"],
    "gpu": ["GPU"],
    "memory": ["Memory"],
    "storage": ["Storage"],
    // ... 30+ fields mapping keywords to section headers
}
```

#### Rule Merging Logic
**Location**: `backend/app/parser.py:106-123`

- Loads default rules from JSON
- Merges with custom user rules
- Custom rules take precedence
- List values are combined and deduplicated

---

## Parsing Pipeline

### Three-Phase Processing

#### Phase 1: Before Parse (`before_parse()`)
**Location**: `backend/app/parser.py:134-139`

**Operations**:
1. Load default rules from `default_rules.json`
2. Merge with custom rules if provided
3. Initialize parsing strategy (currently `RuleBasedStrategy`)
4. Validate input parameters

#### Phase 2: In Parsing (`in_parsing()`)
**Location**: `backend/app/parser.py:141-148`

**Operations**:
1. Execute strategy's `parse()` method
2. Extract structured data from text
3. Apply field-specific extraction logic
4. Return list of model dictionaries

#### Phase 3: End Parsing (`end_parsing()`)
**Location**: `backend/app/parser.py:150-156`

**Operations**:
1. Apply temporary regex processing (TODO: Not implemented)
2. Final data transformations
3. Cleanup operations

### Data Flow

```
Input Text → Rule Loading → Strategy Selection → Field Extraction → Post-Processing → Structured Output
```

**Input**: Raw text content with embedded structure
**Output**: List of dictionaries with extracted model specifications

---

## Strategy Implementation Details

### RuleBasedStrategy (Current Implementation)
**Location**: `backend/app/strategies/concrete_strategies.py:5-56`

#### Core Algorithm

1. **Model Name Extraction** (`_extract_model_names()`)
   - **Primary Method**: Section-based extraction using `[Model Names]` sections
   - **Fallback Method**: Regex pattern matching for model-like strings (`[A-Z]{2,3}\d{3,4}[A-Z]*`)
   - **Returns**: Sorted list of unique model names

2. **Field Value Extraction** (`_extract_field_value()`)
   - **Section Detection**: Splits text by section headers `[Section Name]`
   - **Keyword Matching**: Searches for field keywords within sections
   - **Value Extraction**: Uses regex to find model-specific values
   - **Pattern**: `^-? *{model_name}.*?:([^\n]+)`

#### Text Structure Assumptions

The strategy assumes text follows this structure:
```
[Section Header]
- ModelName1: specification details
- ModelName2: specification details

[Another Section]
- ModelName1: different specification
```

#### Extraction Logic Flow

```python
# Simplified extraction flow
def parse(text, rules):
    models = extract_model_names(text, rules)
    for model in models:
        for field, keywords in rules.items():
            value = extract_field_value(text, model, keywords)
            model_data[field] = value
    return model_data_list
```

#### Regex Patterns Used

- **Section Detection**: `r'(\n\[.*?\]\n)'`
- **Model Name Extraction**: `r"-\s*([A-Z0-9]+)"`
- **Field Value Extraction**: `f"^-? *{re.escape(model_name)}.*?:([^\n]+)"`
- **Fallback Model Detection**: `r'\b([A-Z]{2,3}\d{3,4}[A-Z]*)\b'`

---

## Extension Points & Future Strategies

### Strategy Interface Implementation

To implement a new parsing strategy:

```python
from .base_strategy import BaseParsingStrategy

class MyCustomStrategy(BaseParsingStrategy):
    def parse(self, text: str, rules: Dict[str, List[str]]) -> List[Dict[str, str]]:
        # Implement custom parsing logic
        return parsed_data
```

### Potential Future Strategies

#### 1. ML-Based Strategy
**Concept**: Use machine learning models for entity extraction

```python
class MLBasedStrategy(BaseParsingStrategy):
    def __init__(self):
        self.model = load_pretrained_model()
    
    def parse(self, text: str, rules: Dict[str, List[str]]) -> List[Dict[str, str]]:
        # Use NLP model for entity extraction
        entities = self.model.extract_entities(text)
        return self._structure_entities(entities, rules)
```

**Advantages**:
- Better handling of unstructured text
- Adaptive to different text formats
- Can learn from training data

**Challenges**:
- Requires training data
- Model inference overhead
- Dependency on ML frameworks

#### 2. NLP-Based Strategy
**Concept**: Use natural language processing libraries (spaCy, NLTK)

```python
class NLPStrategy(BaseParsingStrategy):
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
    
    def parse(self, text: str, rules: Dict[str, List[str]]) -> List[Dict[str, str]]:
        doc = self.nlp(text)
        # Extract entities and relationships
        return self._extract_specifications(doc, rules)
```

#### 3. Hybrid Strategy
**Concept**: Combine multiple approaches for robust extraction

```python
class HybridStrategy(BaseParsingStrategy):
    def __init__(self):
        self.strategies = [
            RuleBasedStrategy(),
            MLBasedStrategy(),
            NLPStrategy()
        ]
    
    def parse(self, text: str, rules: Dict[str, List[str]]) -> List[Dict[str, str]]:
        results = []
        for strategy in self.strategies:
            result = strategy.parse(text, rules)
            results.append(result)
        return self._merge_results(results)
```

#### 4. Template-Based Strategy
**Concept**: Define templates for different text formats

```python
class TemplateBasedStrategy(BaseParsingStrategy):
    def __init__(self):
        self.templates = self._load_templates()
    
    def parse(self, text: str, rules: Dict[str, List[str]]) -> List[Dict[str, str]]:
        template = self._detect_template(text)
        return template.extract(text, rules)
```

### Integration Guidelines

#### 1. Strategy Registration
```python
# In parser.py
AVAILABLE_STRATEGIES = {
    'rule_based': RuleBasedStrategy,
    'ml_based': MLBasedStrategy,
    'nlp_based': NLPStrategy,
    'hybrid': HybridStrategy
}

def __init__(self, request: ProcessRequest):
    strategy_type = request.strategy_type or 'rule_based'
    self.strategy = AVAILABLE_STRATEGIES[strategy_type]()
```

#### 2. Configuration Extension
```python
# In models.py
class ProcessRequest(BaseModel):
    text_content: str
    strategy_type: Optional[str] = 'rule_based'
    strategy_config: Optional[Dict] = None
    custom_rules: Optional[Dict[str, List[str]]] = None
```

---

## Performance & Optimization Considerations

### Current Limitations

#### 1. Regex Performance
**Issue**: Complex regex patterns can be slow on large texts
**Location**: `backend/app/strategies/concrete_strategies.py:27-30`

**Current Pattern**:
```python
pattern = re.compile(f"^-? *{re.escape(model_name)}.*?:([^\n]+)", re.IGNORECASE | re.MULTILINE)
```

**Optimization Opportunities**:
- Pre-compile regex patterns
- Use more efficient string matching
- Implement caching for repeated patterns

#### 2. Memory Usage
**Issue**: Large text files can consume significant memory
**Current Approach**: Load entire text into memory

**Optimization Strategies**:
- Streaming processing for large files
- Chunked processing with overlap
- Memory-mapped file access

#### 3. Scalability Concerns
**Issue**: Sequential processing of multiple models
**Current Implementation**: Single-threaded extraction

**Optimization Opportunities**:
- Parallel processing of models
- Async processing for I/O operations
- Batch processing capabilities

### Performance Metrics

#### Current Benchmarks
- **Small Files** (< 1MB): ~100-200ms processing time
- **Medium Files** (1-10MB): ~1-5s processing time
- **Large Files** (> 10MB): May require optimization

#### Optimization Strategies

#### 1. Caching Strategy
```python
class CachedStrategy(BaseParsingStrategy):
    def __init__(self):
        self.cache = {}
    
    def parse(self, text: str, rules: Dict[str, List[str]]) -> List[Dict[str, str]]:
        cache_key = self._generate_cache_key(text, rules)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self._actual_parse(text, rules)
        self.cache[cache_key] = result
        return result
```

#### 2. Parallel Processing
```python
import concurrent.futures

class ParallelStrategy(BaseParsingStrategy):
    def parse(self, text: str, rules: Dict[str, List[str]]) -> List[Dict[str, str]]:
        models = self._extract_model_names(text, rules)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._process_model, text, model, rules): model 
                for model in models
            }
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        return results
```

#### 3. Memory Optimization
```python
def parse_streaming(self, text_stream, rules):
    """Process text in chunks to reduce memory usage"""
    chunk_size = 1024 * 1024  # 1MB chunks
    overlap = 1000  # Character overlap between chunks
    
    for chunk in self._read_chunks(text_stream, chunk_size, overlap):
        yield self._process_chunk(chunk, rules)
```

### Monitoring and Profiling

#### Performance Monitoring
```python
import time
import psutil

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def track_parsing(self, strategy_name, text_size):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        # ... parsing logic ...
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        self.metrics[strategy_name] = {
            'processing_time': end_time - start_time,
            'memory_usage': end_memory - start_memory,
            'text_size': text_size
        }
```

---

## Usage Examples

### Basic Usage
```python
from app.parser import Parser
from app.models import ProcessRequest

# Create request
request = ProcessRequest(
    text_content="[Model Names]\n- ABC123: specs here",
    custom_rules={"cpu": ["Processor", "CPU"]},
    temp_regex=None
)

# Parse
parser = Parser(request)
results = parser.run()

# Output: [{'modelname': 'ABC123', 'cpu': 'Intel i7', ...}]
```

### Custom Strategy Implementation
```python
class CustomStrategy(BaseParsingStrategy):
    def parse(self, text: str, rules: Dict[str, List[str]]) -> List[Dict[str, str]]:
        # Custom parsing logic
        return parsed_results

# Integration
parser = Parser(request)
parser.strategy = CustomStrategy()
results = parser.run()
```

### Rule Customization
```python
custom_rules = {
    "modelname": ["Product Models", "Device Names"],
    "cpu": ["Processor", "CPU", "Central Processing Unit"],
    "gpu": ["Graphics", "GPU", "Graphics Card"],
    "custom_field": ["Custom Section Header"]
}

request = ProcessRequest(
    text_content=text,
    custom_rules=custom_rules
)
```

### Error Handling
```python
try:
    parser = Parser(request)
    results = parser.run()
except Exception as e:
    # Handle parsing errors
    print(f"Parsing failed: {e}")
    results = []
```

---

## Conclusion

The current parsing architecture provides a solid foundation for extensible text processing with clear separation of concerns and well-defined interfaces. The Strategy Pattern allows for easy addition of new parsing approaches while maintaining backward compatibility.

Key strengths:
- **Flexibility**: Easy to add new parsing strategies
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Template method pattern supports customization
- **Rule-based**: Configurable extraction rules

Areas for improvement:
- **Performance**: Optimize regex patterns and memory usage
- **Scalability**: Add parallel processing capabilities
- **Error Handling**: Improve robustness and error recovery
- **Testing**: Add comprehensive strategy testing framework

This document serves as both technical documentation and a foundation for discussions about future parsing strategy enhancements.