# Testing Guide for ugit

This document describes the comprehensive test suite for ugit.

## Test Structure

The test suite is organized into several files:

- `test_new_features.py` - Tests for all newly implemented features (tags, reflog, blame, etc.)
- `test_advanced_features.py` - Tests for advanced features (aliases, GPG, HTTP remotes, etc.)
- `test_ci_compatibility.py` - Cross-platform compatibility tests
- `test_commands.py` - Core command tests
- `test_integration.py` - Integration tests
- Other feature-specific test files

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_new_features.py -v
```

### Run with coverage
```bash
pytest --cov=ugit --cov-report=term tests/
```

### Run on specific platform
Tests are designed to work on Mac, Linux, and Windows. Some tests may be skipped on certain platforms (e.g., web interface tests on Windows).

## Platform Compatibility

All tests are designed to work across platforms:

- **Mac (Darwin)**: Full test suite
- **Linux**: Full test suite
- **Windows**: Most tests work; some web interface tests are skipped

## Test Categories

### Core Features
- Repository initialization
- File staging and commits
- Branching and merging
- Status and diff

### New Features (30+ features)
- Tags (lightweight and annotated)
- Reflog
- Blame
- Cherry-pick
- Grep
- Archive
- Aliases
- Stats
- Bisect
- Rebase
- Squash merge
- Merge strategies
- Garbage collection
- Fsck
- Worktree
- Hooks
- Interactive staging
- Commit templates
- Shallow clone
- GPG signing
- Pack files
- Delta compression
- HTTP remotes
- Web UI enhancements

### Cross-Platform Tests
- Path handling
- File operations
- Directory operations
- Unicode support
- Line endings
- File permissions
- Case sensitivity

## CI/CD

Tests run automatically on:
- Ubuntu (latest)
- Windows (latest)
- macOS (latest)

With Python versions: 3.9, 3.10, 3.11, 3.12

## Writing New Tests

When adding new features, follow these guidelines:

1. Use `unittest.TestCase` or `pytest` fixtures
2. Create temporary directories for each test
3. Clean up resources in `tearDown`
4. Use platform-agnostic path operations
5. Handle platform-specific behavior gracefully
6. Add tests to appropriate test file or create new one

## Test Fixtures

Common fixtures are available in `conftest.py`:
- `temp_repo` - Temporary directory for testing
- `initialized_repo` - Initialized ugit repository
- `repo_with_config` - Repository with user config

## Known Platform Differences

- **Windows**: File locking may require delays in cleanup
- **Mac**: Case-insensitive filesystem by default
- **Linux**: Case-sensitive filesystem

Tests handle these differences automatically.

