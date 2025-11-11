# Tests

Comprehensive test suite for OpsFleet Agent.

## Structure

```
tests/
├── __init__.py              # Package marker
├── README.md                # This file
├── test_agent.py            # Agent core tests
├── test_endpoints.py        # BigQuery endpoints tests
└── test_cli_enhanced.py     # CLI tests
```

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_agent.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Test Class
```bash
pytest tests/test_agent.py::TestConfig -v
```

### Run Specific Test
```bash
pytest tests/test_agent.py::TestConfig::test_config_from_env -v
```

## Test Coverage

### test_agent.py
- **TestConfig**: Configuration loading and defaults
- **TestExtractContent**: Content extraction from AI messages
- **TestLoadPrompt**: Prompt loading and formatting
- **TestRunAgent**: Agent execution and response handling
- **TestAgentState**: State structure validation

### test_endpoints.py
- **TestBigQueryConfig**: BigQuery configuration
- **TestCreateBigQueryClient**: Client creation with credentials
- **TestQueryBigQuery**: Query execution and error handling
- **TestAnalyzeSchema**: Schema analysis for tables and datasets

### test_cli_enhanced.py
- CLI initialization and banner display
- Command handling (/help, /history, /schema, etc.)
- Query processing and formatting
- Save functionality (CSV, JSON, Excel, Markdown)
- Session management
- History tracking

## Writing New Tests

### Test Structure
```python
"""Tests for module_name."""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch


class TestFeature:
    """Test specific feature."""
    
    def test_something(self):
        """Test description."""
        # Arrange
        expected = "result"
        
        # Act
        result = function_to_test()
        
        # Assert
        assert result == expected
```

### Best Practices

1. **Use descriptive names**: `test_config_from_env` not `test1`
2. **One assertion per test**: Focus on single behavior
3. **Use fixtures**: Share setup code across tests
4. **Mock external dependencies**: Don't call real APIs
5. **Test edge cases**: Empty inputs, None, errors
6. **Use parametrize**: Test multiple inputs efficiently

### Example with Parametrize
```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

## Continuous Integration

Tests run automatically on:
- Push to main branch
- Pull requests
- Pre-commit hooks (optional)

## Dependencies

Required for testing:
- pytest
- pytest-asyncio
- pytest-cov (for coverage)
- pytest-mock (for mocking)

Install with:
```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

## Troubleshooting

### Import Errors
Ensure the package is installed in editable mode:
```bash
pip install -e .
```

### Mock Issues
Use `patch` from `unittest.mock`:
```python
from unittest.mock import patch, Mock

@patch('module.function')
def test_something(mock_function):
    mock_function.return_value = "mocked"
    # test code
```

### Async Tests
Use `pytest-asyncio` for async functions:
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

## Coverage Goals

- **Target**: 80%+ code coverage
- **Critical paths**: 100% coverage
- **Focus areas**: Error handling, edge cases

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
