# Contributing to ugit

Thank you for your interest in contributing to ugit! This document provides guidelines and instructions for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of version control concepts

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/ugit.git
   cd ugit
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e .[dev]
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 🔧 Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow existing code style and patterns
   - Add docstrings to new functions and classes

3. **Add tests**
   - Write unit tests for new functionality
   - Ensure existing tests still pass
   - Aim for good test coverage

4. **Run quality checks**
   ```bash
   # Run tests
   pytest
   
   # Check code formatting
   black --check ugit/ tests/
   
   # Check import sorting
   isort --check-only ugit/ tests/
   
   # Type checking
   mypy ugit/
   
   # Linting
   flake8 ugit/ tests/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add support for branch switching
fix: handle missing objects gracefully
docs: update installation instructions
test: add tests for commit command
```

## 📋 Code Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Maximum line length: 88 characters (Black default)

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update README.md for user-facing changes
- Add inline comments for complex logic

Example docstring:
```python
def hash_object(data: bytes, type_: str = "blob", write: bool = True) -> str:
    """
    Compute SHA-1 hash of data and optionally store it.
    
    Args:
        data: The raw data to hash
        type_: Object type ('blob', 'tree', 'commit')  
        write: Whether to write the object to disk
        
    Returns:
        SHA-1 hash of the object
        
    Raises:
        ValueError: If data is invalid
    """
```

### Testing

- Write tests for all new functionality
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Use pytest fixtures for common setup

Example test:
```python
def test_hash_object_creates_correct_sha():
    """Test that hash_object creates the expected SHA-1 hash."""
    # Arrange
    data = b"hello world"
    
    # Act
    sha = hash_object(data, write=False)
    
    # Assert
    assert len(sha) == 40
    assert sha == "95d09f2b10159347eece71399a7e2e907ea3df4f"
```

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages (if any)

### Feature Requests

For feature requests, please:

- Describe the problem you're trying to solve
- Explain your proposed solution
- Consider the scope and complexity
- Check if similar features exist

## 📝 Pull Request Process

1. **Ensure your branch is up to date**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Create a pull request**
   - Use a descriptive title
   - Reference any related issues
   - Describe your changes clearly
   - Include screenshots if applicable

3. **Review process**
   - Automated checks must pass
   - At least one maintainer review required
   - Address any feedback promptly
   - Keep discussions constructive

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🏗️ Project Structure

Understanding the codebase:

```
ugit/
├── ugit/
│   ├── core/              # Core functionality
│   │   ├── objects.py     # Object storage and hashing
│   │   └── repository.py  # Repository management
│   ├── commands/          # Command implementations
│   │   ├── init.py        # Repository initialization
│   │   ├── add.py         # File staging
│   │   ├── commit.py      # Commit creation
│   │   └── ...
│   ├── utils/             # Utility functions
│   └── cli.py             # Command-line interface
├── tests/                 # Test suite
├── docs/                  # Documentation
└── ...
```

## 🔍 Code Review Guidelines

### For Contributors

- Keep changes focused and atomic
- Write clear commit messages
- Respond to feedback constructively
- Test your changes thoroughly

### For Reviewers

- Be constructive and respectful
- Focus on code quality and maintainability
- Check for edge cases and error handling
- Verify tests are adequate

## 🎯 Good First Issues

New contributors can look for issues labeled:

- `good first issue` - Perfect for newcomers
- `help wanted` - Community input desired
- `documentation` - Improve docs
- `testing` - Add or improve tests

## 📚 Resources

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Git Workflow](https://guides.github.com/introduction/flow/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Type Hints (PEP 484)](https://pep484.readthedocs.io/)

## 🤝 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## 💬 Getting Help

- Create an issue for bugs or feature requests
- Start a discussion for questions
- Join our community chat (if available)
- Check existing documentation

## 🙏 Recognition

Contributors are recognized in:

- Release notes
- Contributors section in README
- Special mentions for significant contributions

Thank you for contributing to ugit! 🎉