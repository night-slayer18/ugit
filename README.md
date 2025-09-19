# ugit 🚀

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A minimal Git implementation in Python that demonstrates the core concepts of version control systems. Perfect for learning how Git works under the hood!

## ✨ Features

- **Repository initialization** - Create new ugit repositories
- **File staging** - Add files to the staging area  
- **Committing** - Create commits from staged changes
- **History viewing** - Browse commit history
- **Checkout** - Restore files from specific commits
- **Status checking** - See which files are modified, staged, or untracked

## � Documentation

- **[Installation Guide](docs/installation.md)** - How to install and set up ugit
- **[User Guide](docs/user-guide.md)** - Complete guide to using ugit commands
- **[Examples](docs/examples.md)** - Practical examples and use cases
- **[API Reference](docs/api-reference.md)** - Technical documentation
- **[Developer Guide](docs/developer-guide.md)** - Guide for contributors
- **[Architecture](docs/architecture.md)** - System design overview
- **[FAQ](docs/faq.md)** - Frequently asked questions
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## �🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/night-slayer18/ugit.git
cd ugit

# Install in development mode
pip install -e .
```

### Basic Usage

```bash
# Initialize a new repository
ugit init

# Add files to staging area
ugit add file.txt
ugit add .

# Create a commit
ugit commit -m "Initial commit"

# Check repository status
ugit status

# View commit history
ugit log

# Checkout a specific commit
ugit checkout <commit-sha>
```

## 📁 Project Structure

```
ugit/
├── ugit/                   # Main package
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # Command-line interface
│   ├── core/              # Core functionality
│   │   ├── objects.py     # Object storage and hashing
│   │   └── repository.py  # Repository and index management
│   ├── commands/          # Command implementations
│   │   ├── init.py        # Repository initialization
│   │   ├── add.py         # File staging
│   │   ├── commit.py      # Commit creation
│   │   ├── log.py         # History viewing
│   │   ├── checkout.py    # File restoration
│   │   └── status.py      # Status checking
│   └── utils/             # Utility functions
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── main.py               # Entry point script
├── setup.py              # Package setup
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🔧 How It Works

ugit implements the core Git concepts:

### Object Storage
- **Blobs**: Store file contents
- **Trees**: Store directory structures  
- **Commits**: Store snapshots with metadata
- Objects are stored by SHA-1 hash in `.ugit/objects/`

### Repository Structure
```
.ugit/
├── objects/           # Object storage (blobs, trees, commits)
├── refs/heads/        # Branch references
├── HEAD              # Current branch pointer
└── index             # Staging area
```

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize repository | `ugit init` |
| `add` | Stage files | `ugit add file.txt` |
| `commit` | Create commit | `ugit commit -m "message"` |
| `status` | Show status | `ugit status` |
| `log` | Show history | `ugit log` |
| `checkout` | Restore files | `ugit checkout abc123` |

## 🧪 Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/night-slayer18/ugit.git
cd ugit
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ugit

# Run specific test file
pytest tests/test_commands.py
```

### Code Quality

```bash
# Format code
black ugit/ tests/

# Sort imports  
isort ugit/ tests/

# Type checking
mypy ugit/

# Linting
flake8 ugit/ tests/
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Format your code (`black .` and `isort .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to your branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📚 Learning Resources

- [Git Internals](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain)
- [Building Git by James Coglan](https://shop.jcoglan.com/building-git/)
- [Git from the Bottom Up](https://jwiegley.github.io/git-from-the-bottom-up/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the excellent Git internals documentation
- Built for educational purposes to understand version control systems
- Thanks to all contributors who help improve this project

## 📞 Support

- 📫 Create an [issue](https://github.com/night-slayer18/ugit/issues) for bug reports or feature requests
- 💬 Start a [discussion](https://github.com/night-slayer18/ugit/discussions) for questions
- ⭐ Star this repository if you find it helpful!

---