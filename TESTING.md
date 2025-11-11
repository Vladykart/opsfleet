# Testing Guide

Comprehensive test suite for the OpsFleet Enhanced CLI.

## Test Coverage

### ✅ 37 Tests - All Passing

**Test Categories:**
1. CLI Initialization (4 tests)
2. Save Conversation (9 tests)
3. Export History (2 tests)
4. Command Handling (11 tests)
5. History Tracking (4 tests)
6. Data Integrity (3 tests)
7. File Naming (2 tests)
8. Error Handling (2 tests)

## Running Tests

### Run All Tests
```bash
source venv/bin/activate
pytest test_cli_enhanced.py -v
```

### Run Specific Test Class
```bash
pytest test_cli_enhanced.py::TestSaveConversation -v
```

### Run Single Test
```bash
pytest test_cli_enhanced.py::TestSaveConversation::test_save_csv_creates_file -v
```

### Run with Coverage
```bash
pytest test_cli_enhanced.py --cov=cli_enhanced --cov-report=html
```

## Test Details

### 1. CLI Initialization Tests
- ✅ Creates session directory
- ✅ Generates unique session ID
- ✅ Initializes empty history
- ✅ Has last_query_data attribute

### 2. Save Conversation Tests
- ✅ CSV format creates file
- ✅ JSON format creates file
- ✅ Excel format creates file
- ✅ Markdown format creates file
- ✅ Plain text format creates file
- ✅ Empty history shows warning
- ✅ Unknown format shows error
- ✅ CSV contains all required fields
- ✅ Data types are preserved

### 3. Export History Tests
- ✅ Creates text file
- ✅ Includes all queries

### 4. Command Handling Tests
- ✅ /help command works
- ✅ /history command works
- ✅ /stats command works
- ✅ /save command (default CSV)
- ✅ /save with format parameter
- ✅ /export command works
- ✅ /exit returns False
- ✅ /quit returns False
- ✅ Unknown command handled
- ✅ /schema command works
- ✅ /schema with table parameter

### 5. History Tracking Tests
- ✅ History starts empty
- ✅ Tracks queries correctly
- ✅ Contains required fields
- ✅ Tracks success/failure status

### 6. Data Integrity Tests
- ✅ CSV roundtrip preserves data
- ✅ JSON roundtrip preserves data
- ✅ Excel roundtrip preserves data

### 7. File Naming Tests
- ✅ Creates unique filenames
- ✅ Filename contains timestamp

### 8. Error Handling Tests
- ✅ Invalid format handled gracefully
- ✅ Empty history handled gracefully

## Test Fixtures

### `cli` Fixture
Creates a fresh CLI instance for each test.

```python
@pytest.fixture
def cli():
    cli = RichChatCLI()
    yield cli
    # Cleanup after test
```

### `cli_with_history` Fixture
Creates a CLI instance with sample conversation history.

```python
@pytest.fixture
def cli_with_history(cli):
    cli.history = [
        {
            "time": "10:00:00",
            "query": "How many users?",
            "response": "There are 100,000 users",
            "success": True,
            "elapsed": 2.5
        },
        # ... more entries
    ]
    return cli
```

## Test Data Structure

Each history entry contains:
```python
{
    "time": "HH:MM:SS",
    "query": "User question",
    "response": "Agent response",
    "success": True/False,
    "elapsed": 2.5  # seconds
}
```

## Continuous Integration

### GitHub Actions (Future)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: pytest test_cli_enhanced.py -v
```

## Test Output Example

```
test_cli_enhanced.py::TestCLIInitialization::test_cli_creates_session_directory PASSED [  2%]
test_cli_enhanced.py::TestCLIInitialization::test_cli_has_session_id PASSED [  5%]
test_cli_enhanced.py::TestSaveConversation::test_save_csv_creates_file PASSED [ 13%]
test_cli_enhanced.py::TestSaveConversation::test_save_json_creates_file PASSED [ 16%]
...
======= 37 passed, 10 warnings in 6.14s ========
```

## Adding New Tests

### Template for New Test
```python
class TestNewFeature:
    def test_feature_works(self, cli_with_history):
        # Arrange
        expected_result = "something"
        
        # Act
        result = cli_with_history.some_method()
        
        # Assert
        assert result == expected_result
```

### Best Practices
1. Use descriptive test names
2. Follow AAA pattern (Arrange, Act, Assert)
3. Test one thing per test
4. Use fixtures for setup
5. Clean up after tests
6. Test both success and failure cases

## Dependencies

- `pytest==8.0.0` - Testing framework
- `pandas==2.2.0` - Data manipulation
- `openpyxl==3.1.2` - Excel support

## Known Issues

### Warnings
- Google protobuf deprecation warnings (harmless)
- openpyxl datetime.utcnow() deprecation (harmless)

These warnings don't affect test results and will be addressed in future library updates.

## Test Maintenance

### When to Update Tests
- Adding new CLI commands
- Changing save formats
- Modifying data structure
- Adding new features
- Fixing bugs

### Test Coverage Goals
- Maintain 100% coverage of public methods
- Test all command handlers
- Test all export formats
- Test error conditions
- Test edge cases

## Troubleshooting

### Tests Fail on Import
```bash
# Ensure you're in the project directory
cd /path/to/opsfleet

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Session Directory Issues
Tests automatically clean up session files. If you see leftover files:
```bash
rm -rf sessions/conversation_*.* sessions/session_*.txt
```

### Timing Issues
Some tests use `time.sleep(1)` to ensure unique timestamps. If tests are slow, this is expected behavior.

## Future Test Additions

- [ ] Integration tests with actual BigQuery
- [ ] Performance tests for large conversations
- [ ] UI rendering tests
- [ ] Keyboard input simulation tests
- [ ] Schema analyzer tests
- [ ] Agent response tests
- [ ] Concurrent save tests
- [ ] Memory usage tests

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain test coverage
4. Update this documentation
5. Add examples for complex tests
