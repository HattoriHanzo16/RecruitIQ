# RecruitIQ Test Suite

Comprehensive test suite for the RecruitIQ job market intelligence platform.

## Overview

This test suite provides comprehensive coverage for all RecruitIQ components including:

- **Database Models** - Testing ORM models and relationships
- **Core Analyzers** - Testing job market analysis algorithms  
- **CV Analyzer** - Testing AI-powered CV analysis and job matching
- **Web Scrapers** - Testing job data collection from multiple platforms
- **CLI Interface** - Testing command-line functionality
- **Utility Functions** - Testing helpers, validators, and tools

## Test Structure

```
tests/
├── conftest.py           # Pytest configuration and fixtures
├── pytest.ini           # Test runner configuration
├── run_tests.py         # Comprehensive test runner script
├── test_models.py       # Database model tests
├── test_analyzer.py     # Job market analyzer tests
├── test_cv_analyzer.py  # CV analysis tests
├── test_scrapers.py     # Web scraper tests
├── test_utils.py        # Utility function tests
├── test_cli.py          # CLI interface tests
└── README.md           # This file
```

## Quick Start

### Basic Test Execution

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=recruitiq --cov-report=html

# Run specific test categories
pytest tests/ -m "unit"        # Unit tests only
pytest tests/ -m "scraper"     # Scraper tests only
pytest tests/ -m "cv"          # CV analysis tests only
```

### Using the Test Runner Script

The `run_tests.py` script provides an easy way to run comprehensive test suites:

```bash
# Run all tests with coverage
python tests/run_tests.py

# Run specific test types
python tests/run_tests.py --type unit
python tests/run_tests.py --type scraper
python tests/run_tests.py --type cv

# Run tests with additional checks
python tests/run_tests.py --all-checks

# Generate comprehensive report
python tests/run_tests.py --report

# Run in parallel (faster)
python tests/run_tests.py --parallel
```

## Test Categories

### Unit Tests
Test individual components in isolation with mocked dependencies.

```bash
pytest tests/ -m "unit"
```

### Integration Tests
Test component interactions and end-to-end workflows.

```bash
pytest tests/ -m "integration"
```

### Component-Specific Tests

```bash
# Database and models
pytest tests/ -m "database"

# Web scrapers
pytest tests/ -m "scraper"

# Job market analysis
pytest tests/ -m "analyzer"

# CV analysis and AI integration
pytest tests/ -m "cv"

# CLI functionality
pytest tests/ -m "cli"
```

## Test Fixtures

The test suite includes comprehensive fixtures in `conftest.py`:

- **Database Fixtures**: In-memory SQLite database for testing
- **Sample Data**: Job postings, CV text, and mock responses
- **Mock Services**: OpenAI API, web scrapers, external services
- **Temporary Files**: CV files for testing file parsing

### Key Fixtures

```python
@pytest.fixture
def db_session():
    """Clean database session for each test"""

@pytest.fixture
def populated_db():
    """Database with sample job postings"""

@pytest.fixture
def mock_cv_text():
    """Sample CV text for testing"""

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""

@pytest.fixture
def temp_cv_file():
    """Temporary CV file for testing"""
```

## Mocking Strategy

Tests use comprehensive mocking to isolate components and avoid external dependencies:

- **External APIs**: OpenAI, job boards, web services
- **File System**: Temporary files and directories
- **Network Requests**: HTTP requests and responses
- **Database**: In-memory SQLite for isolation
- **WebDriver**: Selenium browser automation

## Coverage Requirements

The test suite maintains high code coverage standards:

- **Minimum Coverage**: 80% overall
- **Critical Components**: 90%+ coverage required
- **New Features**: 100% coverage for new code

### Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov=recruitiq --cov-report=html

# View report
open htmlcov/index.html

# Terminal coverage report
pytest tests/ --cov=recruitiq --cov-report=term-missing
```

## Running Specific Tests

### By File
```bash
pytest tests/test_analyzer.py
pytest tests/test_cv_analyzer.py
pytest tests/test_scrapers.py
```

### By Class
```bash
pytest tests/test_analyzer.py::TestJobAnalyzer
pytest tests/test_cv_analyzer.py::TestCVAnalyzer
```

### By Function
```bash
pytest tests/test_analyzer.py::TestJobAnalyzer::test_generate_summary_stats
pytest tests/test_cv_analyzer.py::TestCVAnalyzer::test_ai_analyze_cv_success
```

### By Pattern
```bash
pytest tests/ -k "test_scraper"
pytest tests/ -k "test_cv and not slow"
```

## Test Data

### Sample Job Postings
The test suite includes realistic job posting data:

```python
{
    'title': 'Senior Python Developer',
    'company_name': 'TechCorp Inc.',
    'location': 'San Francisco, CA',
    'salary_min': 120000,
    'salary_max': 160000,
    'job_description': 'Python developer with Django experience',
    'source_platform': 'Indeed'
}
```

### Mock CV Data
Sample CV text for testing analysis features:

```python
"""
John Doe - Senior Software Engineer
Skills: Python, Django, AWS, Docker
Experience: 8 years in web development
"""
```

## Performance Testing

### Slow Tests
Long-running tests are marked with `@pytest.mark.slow`:

```bash
# Skip slow tests
pytest tests/ -m "not slow"

# Run only slow tests
pytest tests/ -m "slow"
```

### Parallel Execution
```bash
# Run tests in parallel
pytest tests/ -n auto

# Using test runner
python tests/run_tests.py --parallel
```

## Continuous Integration

The test suite is designed for CI/CD environments:

### GitHub Actions Example
```yaml
- name: Run Tests
  run: |
    python tests/run_tests.py --all-checks
    python tests/run_tests.py --report
```

### Test Artifacts
- HTML coverage report: `htmlcov/`
- XML coverage: `coverage.xml`
- Test results: `test-results.xml`
- Test report: `test-report.html`

## Debugging Tests

### Verbose Output
```bash
pytest tests/ -v -s
```

### Debug Specific Test
```bash
pytest tests/test_cv_analyzer.py::TestCVAnalyzer::test_ai_analyze_cv_success -v -s
```

### PDB Debugging
```bash
pytest tests/ --pdb  # Drop into debugger on failure
```

### Print Statements
Use `capsys` fixture to capture print output:

```python
def test_function(capsys):
    function_that_prints()
    captured = capsys.readouterr()
    assert "expected output" in captured.out
```

## Test Environment Setup

### Dependencies
Install test dependencies:

```bash
pip install -r requirements.txt
```

Test-specific packages:
- `pytest>=7.4.0` - Test framework
- `pytest-mock>=3.11.1` - Mocking utilities
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-asyncio>=0.21.1` - Async test support
- `pytest-xdist>=3.3.1` - Parallel execution

### Environment Variables
```bash
# Optional: OpenAI API key for integration tests
export OPENAI_API_KEY="your-key-here"

# Database URL for tests (uses in-memory SQLite by default)
export TEST_DATABASE_URL="sqlite:///:memory:"
```

## Writing New Tests

### Test Structure
```python
class TestNewFeature:
    """Test new feature functionality"""
    
    def test_basic_functionality(self, db_session):
        """Test basic feature operation"""
        # Arrange
        setup_data = {"key": "value"}
        
        # Act
        result = new_feature_function(setup_data)
        
        # Assert
        assert result.is_successful
        assert result.data == expected_data
    
    @pytest.mark.slow
    def test_performance(self):
        """Test feature performance"""
        pass
    
    @patch('module.external_service')
    def test_with_mocking(self, mock_service):
        """Test with mocked dependencies"""
        mock_service.return_value = mock_response
        result = feature_using_service()
        assert result is not None
```

### Best Practices
1. **Descriptive Names**: Use clear, descriptive test names
2. **Isolated Tests**: Each test should be independent
3. **Mock External Dependencies**: Avoid real API calls in tests
4. **Use Fixtures**: Leverage pytest fixtures for setup
5. **Test Edge Cases**: Include boundary conditions and error cases
6. **Mark Appropriately**: Use markers for categorization

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure PYTHONPATH includes project root
2. **Database Conflicts**: Use `db_session` fixture for isolation
3. **Mock Failures**: Verify mock patch paths are correct
4. **Async Issues**: Use `pytest-asyncio` for async tests

### Getting Help

1. Check test output for detailed error messages
2. Use `-v` flag for verbose output
3. Review fixture documentation in `conftest.py`
4. Run specific failing tests in isolation

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure new tests pass
3. Maintain coverage above 80%
4. Add appropriate test markers
5. Update this README if needed

---

For more information about RecruitIQ, see the main [README](../README.md) and [documentation](../docs/). 