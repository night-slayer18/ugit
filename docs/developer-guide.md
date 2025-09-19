# Developer Guide

Welcome to the ugit developer guide! This document will help you get started with contributing to ugit.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Contributing Guidelines](#contributing-guidelines)
- [Testing](#testing)
- [Code Style](#code-style)
- [Debugging](#debugging)
- [Release Process](#release-process)

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of version control concepts
- Familiarity with Python development

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ugit.git
   cd ugit
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv ugit-dev
   source ugit-dev/bin/activate  # On Windows: ugit-dev\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Verify setup:**
   ```bash
   python -m pytest tests/
   ugit --help
   ```

## Project Structure

```
ugit/
├── .github/                 # GitHub templates and workflows
│   ├── ISSUE_TEMPLATE/     # Issue templates
│   ├── workflows/          # CI/CD workflows
│   └── pull_request_template.md
├── docs/                   # Documentation
│   ├── README.md
│   ├── user-guide.md
│   ├── api-reference.md
│   └── ...
├── tests/                  # Test suite
│   ├── conftest.py
│   ├── test_commands.py
│   └── test_objects.py
├── ugit/                   # Main package
│   ├── __init__.py
│   ├── cli.py             # Command-line interface
│   ├── commands/          # Command implementations
│   │   ├── __init__.py
│   │   ├── init.py
│   │   ├── add.py
│   │   ├── commit.py
│   │   ├── log.py
│   │   ├── status.py
│   │   └── checkout.py
│   ├── core/              # Core functionality
│   │   ├── __init__.py
│   │   ├── objects.py     # Object storage
│   │   └── repository.py  # Repository management
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── config.py      # Configuration
│       └── helpers.py     # Helper functions
├── pyproject.toml         # Project configuration
├── README.md             # Project overview
├── CONTRIBUTING.md       # Contribution guidelines
└── LICENSE               # MIT License
```

### Module Responsibilities

- **`ugit.cli`**: Command-line argument parsing and main entry point
- **`ugit.commands`**: Individual command implementations
- **`ugit.core.objects`**: Object storage (blobs, trees, commits)
- **`ugit.core.repository`**: Repository and index management
- **`ugit.utils`**: Common utilities and helper functions

## Contributing Guidelines

### Before You Start

1. Check existing issues to see if your idea is already being discussed
2. Open an issue to discuss new features before implementing
3. Read through the codebase to understand the current architecture
4. Look at recent PRs to understand the review process

### Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clear, focused commits
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
   ```bash
   python -m pytest tests/
   python -m ugit.cli --help  # Test CLI
   ```

4. **Submit a pull request:**
   - Use the PR template
   - Include clear description of changes
   - Reference related issues

### Commit Guidelines

**Good commit messages:**
```
Add support for .ugitignore files

- Implement ignore pattern matching
- Add tests for ignore functionality
- Update documentation

Fixes #123
```

**Format:**
- Use present tense ("Add feature" not "Added feature")
- First line should be 50 characters or less
- Include body with details if needed
- Reference issues with "Fixes #123"

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=ugit

# Run specific test file
python -m pytest tests/test_commands.py

# Run specific test
python -m pytest tests/test_commands.py::test_init_command
```

### Writing Tests

Tests are located in the `tests/` directory. Use pytest conventions:

```python
def test_your_feature():
    """Test description."""
    # Arrange
    repo = Repository(".")
    
    # Act
    result = repo.some_method()
    
    # Assert
    assert result == expected_value
```

### Test Guidelines

- Test both success and failure cases
- Use descriptive test names
- Include docstrings for complex tests
- Mock external dependencies
- Use temporary directories for file operations

### Manual Testing

Create a test repository to manually verify functionality:

```bash
mkdir test-repo && cd test-repo
ugit init
echo "Hello" > file.txt
ugit add file.txt
ugit commit -m "Initial commit"
ugit status
ugit log
```

## Code Style

### Python Standards

- Follow PEP 8
- Use type hints for function signatures
- Include docstrings for public functions
- Use meaningful variable names

### Code Formatting

We use automated tools for consistent formatting:

```bash
# Format code
black ugit/ tests/

# Sort imports
isort ugit/ tests/

# Check formatting
flake8 ugit/ tests/

# Type checking
mypy ugit/
```

### Documentation Standards

- Include docstrings for all public functions
- Use Google-style docstrings
- Document parameters and return values
- Include examples for complex functions

Example:
```python
def hash_object(data: bytes, obj_type: str = "blob", write: bool = True) -> str:
    """
    Hash and optionally store an object.
    
    Args:
        data: Raw object data
        obj_type: Object type ("blob", "tree", "commit")
        write: Whether to write to disk
        
    Returns:
        SHA-1 hash of the object
        
    Example:
        >>> hash_object(b"Hello", "blob", True)
        'af5626b4a114abcb82d63db7c8082c3c4756e51b'
    """
```

## Debugging

### Common Debugging Techniques

1. **Add debug prints:**
   ```python
   print(f"Debug: current_sha = {current_sha}")
   ```

2. **Use Python debugger:**
   ```python
   import pdb; pdb.set_trace()
   ```

3. **Check object storage:**
   ```bash
   ls -la .ugit/objects/
   cat .ugit/refs/heads/main
   ```

4. **Validate JSON objects:**
   ```python
   import json
   with open('.ugit/objects/abc123...', 'rb') as f:
       data = json.loads(f.read())
       print(data)
   ```

### Testing in Isolation

Test individual components:

```python
# Test object storage
from ugit.core.objects import hash_object, get_object
sha = hash_object(b"test", "blob", True)
obj_type, data = get_object(sha)

# Test repository operations
from ugit.core.repository import Repository
repo = Repository()
print(repo.is_repository())
```

## Architecture Notes

### Object Storage

- Objects are stored in `.ugit/objects/` using SHA-1 hashes
- Files are compressed with zlib
- Three object types: blob, tree, commit

### Repository Structure

```
.ugit/
├── objects/           # Object storage
│   ├── ab/
│   │   └── cdef123... # Object files (first 2 chars as directory)
├── refs/
│   └── heads/
│       └── main       # Branch references
└── index             # Staging area
```

### Command Flow

1. CLI parsing (`cli.py`)
2. Command dispatch to appropriate module
3. Repository validation (`helpers.ensure_repository()`)
4. Command execution
5. Object storage updates
6. Index/reference updates

## Release Process

### Version Management

- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version in `pyproject.toml`
- Tag releases with `git tag v0.1.0`

### Release Checklist

1. Update version number
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation if needed
5. Create GitHub release
6. Announce release

## Getting Help

### Resources

- [API Reference](api-reference.md) - Technical documentation
- [User Guide](user-guide.md) - User-facing documentation
- [Architecture](architecture.md) - System design overview

### Community

- Open an issue for bugs or questions
- Start a discussion for general questions
- Join code reviews on pull requests

### Mentorship

New contributors are welcome! Don't hesitate to:
- Ask questions in issues or discussions
- Request code reviews
- Suggest improvements to documentation

## Common Tasks

### Adding a New Command

1. Create new file in `ugit/commands/`
2. Implement the command function
3. Add command to `cli.py`
4. Add tests
5. Update documentation

### Modifying Object Storage

1. Update `ugit/core/objects.py`
2. Ensure backward compatibility
3. Add migration code if needed
4. Thoroughly test changes

### Updating Documentation

1. Make changes to relevant `.md` files
2. Test documentation locally
3. Update cross-references
4. Check for broken links

Happy coding! 🚀