# Installation Guide

This guide will help you install ugit on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Methods

### Method 1: Install from Source (Recommended for Development)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/night-slayer18/ugit.git
   cd ugit
   ```

2. **Install in development mode:**
   ```bash
   pip install -e .
   ```

3. **Verify installation:**
   ```bash
   ugit --help
   ```

### Method 2: Direct Installation

1. **Install directly from GitHub:**
   ```bash
   pip install git+https://github.com/night-slayer18/ugit.git
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
- Solution: ugit requires Python 3.8+. Check your Python version with `python --version`

### Getting Help

If you encounter issues not covered here, please:
1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Search existing [GitHub issues](https://github.com/night-slayer18/ugit/issues)
3. Open a new issue with detailed information about your system and the error

## Next Steps

After successful installation, continue with the [User Guide](user-guide.md) to learn how to use ugit.