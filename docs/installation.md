# Installation Guide

This guide will help you install ugit on your system with different feature sets.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

## Installation Options

ugit offers flexible installation options depending on your needs:

- **Basic Installation**: Core command-line functionality only
- **Web Interface**: Includes beautiful web interface for repository browsing
- **Development**: Full development environment with all tools

## Quick Installation

### Option 1: Basic Installation (CLI Only)
For users who only need command-line functionality:

```bash
pip install ugit-cli
```

### Option 2: Full Installation (CLI + Web Interface)  
For users who want the complete experience including the web interface:

```bash
pip install ugit-cli[web]
```

### Option 3: Development Installation
For contributors and developers:

```bash
pip install ugit-cli[dev,web]
```

## Detailed Installation Methods

### Method 1: Install from Source (Recommended for Development)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/night-slayer18/ugit.git
   cd ugit
   ```

2. **Choose your installation type:**

   **Basic installation:**
   ```bash
   pip install -e .
   ```

   **With web interface:**
   ```bash
   pip install -e .[web]
   ```

   **Development environment:**
   ```bash
   pip install -e .[dev,web]
   ```

3. **Verify installation:**
   ```bash
   ugit --help
   ```

### Method 2: Direct Installation

1. **Basic installation:**
   ```bash
   pip install git+https://github.com/night-slayer18/ugit.git
   ```

   **With web interface:**
   ```bash
   pip install "ugit[web] @ git+https://github.com/night-slayer18/ugit.git"
   ```

2. **Verify installation:**
   ```bash
   ugit --help
   ```

### Method 3: Manual Installation

1. **Download and extract the source code**
2. **Navigate to the project directory**
3. **Install using pip:**
   ```bash
   pip install .
   ```

## Post-Installation Setup

### Verify Core Installation

Test that ugit is working correctly:

```bash
# Check version and help
ugit --help
ugit --version

# Create a test repository
mkdir test-repo
cd test-repo
ugit init
echo "Hello ugit!" > test.txt
ugit add test.txt
ugit commit -m "Test commit"
ugit status
```

### Verify Web Interface (if installed)

If you installed the web interface dependencies, test the web server:

```bash
# In any ugit repository directory
ugit serve --help

# Start the server (this should work without errors)
ugit serve --no-browser --port 8080
```

If you see "Error: Web dependencies not installed", you need to install with the `[web]` option.

### Dependencies Overview

**Core Dependencies (always installed):**
- Python standard library only - no external dependencies!

**Web Interface Dependencies (optional):**
- `fastapi` - Modern web framework
- `uvicorn` - ASGI web server  
- `jinja2` - Template engine
- `python-multipart` - File upload support
- `aiofiles` - Async file operations

**Development Dependencies (optional):**
- `pytest` - Testing framework
- `black` - Code formatter
- `isort` - Import sorter
- `flake8` - Linter
- `mypy` - Type checker
- `pre-commit` - Git hooks

### Adding ugit to PATH

If you installed ugit with `--user` flag, you might need to add the installation directory to your PATH:

**On macOS/Linux:**
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add this line to your `~/.bashrc`, `~/.zshrc`, or equivalent shell configuration file.

**On Windows:**
Add `%APPDATA%\Python\Python3x\Scripts` to your system PATH.

### Verify Installation

Run the following command to ensure ugit is properly installed:

```bash
ugit --version
ugit --help
```

You should see the ugit help message and version information.

## Development Installation

For contributors and developers:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/night-slayer18/ugit.git
   cd ugit
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv ugit-env
   source ugit-env/bin/activate  # On Windows: ugit-env\Scripts\activate
   ```

3. **Install in editable mode with development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Troubleshooting

### Common Installation Issues

**Issue: `ugit: command not found`**
- Solution: Make sure the installation directory is in your PATH (see Post-Installation Setup above)

**Issue: `Permission denied` during installation**
- Solution: Use `--user` flag: `pip install --user ugit`

**Issue: `No module named 'ugit'`**
- Solution: Ensure you're using the correct Python environment where ugit was installed

**Issue: Python version compatibility**
- Solution: ugit requires Python 3.9+. Check your Python version with `python --version`

### Getting Help

If you encounter issues not covered here, please:
1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Search existing [GitHub issues](https://github.com/night-slayer18/ugit/issues)
3. Open a new issue with detailed information about your system and the error

## Next Steps

After successful installation, continue with the [User Guide](user-guide.md) to learn how to use ugit.