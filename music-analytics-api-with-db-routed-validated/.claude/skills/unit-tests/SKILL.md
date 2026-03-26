# Unit Testing Skill

## Overview
Write comprehensive unit tests for Python code using pytest.

## When to Use
Use this skill when you need to generate unit tests for functions, especially before refactoring.

## Safety Steps

### Before Writing Tests
1. Understand the function's purpose and expected behavior
2. Identify input parameters and return values
3. Consider edge cases and error conditions

### Writing Tests
1. Create test functions that cover normal cases
2. Test edge cases (empty inputs, boundary values, etc.)
3. Test error conditions when applicable
4. Use clear, descriptive test names
5. Include docstrings explaining what each test verifies

### After Writing Tests
1. Run all tests to ensure they pass with the current code
2. Verify test coverage includes the main code paths
3. Suggest additional tests if coverage gaps exist

## Example: Testing a Simple Function
```python
# Original function
def calculate_average_tracks(albums):
    """Calculate average number of tracks per album."""
    if not albums:
        return 0
    total = sum(album.get('track_count', 0) for album in albums)
    return total / len(albums)

# Unit tests
import pytest

def test_calculate_average_tracks_normal():
    """Test average calculation with normal input."""
    albums = [
        {'track_count': 10},
        {'track_count': 20},
        {'track_count': 30}
    ]
    result = calculate_average_tracks(albums)
    assert result == 20

def test_calculate_average_tracks_empty():
    """Test with empty album list."""
    result = calculate_average_tracks([])
    assert result == 0

def test_calculate_average_tracks_missing_count():
    """Test with missing track_count field."""
    albums = [{'title': 'Album 1'}, {'track_count': 10}]
    result = calculate_average_tracks(albums)
    assert result == 5
```

## Guidelines
- Test one thing per test function
- Use descriptive names: `test_function_scenario`
- Cover happy path, edge cases, and errors
- Keep tests simple and focused
- Run tests with: `pytest filename.py`