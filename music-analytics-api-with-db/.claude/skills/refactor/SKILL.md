---
name: refactor
description: Safely refactor code while preserving behavior
---

# Safe Refactoring Skill

## When to Use
Use this skill when you need to refactor existing code, especially when extracting helpers, reorganizing functions, or improving structure without changing behavior.

## Before Making Changes
1. Identify existing tests for the code being modified
2. If no tests exist, write tests first to establish baseline behavior
3. Run tests to confirm they pass before changes
4. Understand the current behavior completely

## During Refactoring
1. Make small, incremental changes
2. Preserve all existing functionality
3. Extract helpers or reorganize without changing behavior
4. Add clear docstrings to new functions

## After Changes
1. Run tests again to verify behavior is preserved
2. Review the diff to confirm only intended changes
3. Suggest any additional tests if coverage gaps exist

## Example: Extracting a Helper Function

When extracting logic into a helper:
```python
# Before: Logic embedded in main function
def process_data(items):
    # Preparation logic here
    prepared = [transform(i) for i in items if valid(i)]
    # Main processing
    return calculate(prepared)

# After: Helper extracted
def prepare_items(items):
    """Prepare items for processing by filtering and transforming."""
    return [transform(i) for i in items if valid(i)]

def process_data(items):
    prepared = prepare_items(items)
    return calculate(prepared)
```

Always verify tests pass after extraction.