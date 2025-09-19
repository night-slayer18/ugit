# Troubleshooting Guide

This guide helps you diagnose and fix common issues with ugit.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Repository Issues](#repository-issues)
- [Command Errors](#command-errors)
- [File System Issues](#file-system-issues)
- [Performance Issues](#performance-issues)
- [Data Corruption](#data-corruption)
- [Debug Information](#debug-information)

## Installation Issues

### `pip: command not found`

**Problem**: pip is not installed or not in PATH.

**Solutions**:
```bash
# Try python -m pip instead
python -m pip install ugit

# Install pip if missing (macOS)
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

# Install pip if missing (Ubuntu/Debian)
sudo apt update && sudo apt install python3-pip
```

### `ugit: command not found`

**Problem**: ugit installed but not in PATH.

**Diagnosis**:
```bash
# Check if ugit is installed
python -m pip list | grep ugit

# Find installation location
python -c "import ugit; print(ugit.__file__)"
```

**Solutions**:
```bash
# Option 1: Use full path
/Users/username/Library/Python/3.x/bin/ugit

# Option 2: Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Option 3: Use module syntax
python -m ugit.cli
```

### `Permission denied` during installation

**Problem**: Insufficient permissions for installation.

**Solutions**:
```bash
# Install for current user only
pip install --user ugit

# Use virtual environment (recommended)
python -m venv ugit-env
source ugit-env/bin/activate  # Windows: ugit-env\Scripts\activate
pip install ugit
```

### `Python version incompatibility`

**Problem**: Python version is too old.

**Diagnosis**:
```bash
python --version
```

**Solutions**:
- ugit requires Python 3.8 or higher
- Update Python or use a newer version
- Use pyenv to manage multiple Python versions

## Repository Issues

### `fatal: not a ugit repository`

**Problem**: Running ugit commands outside a repository.

**Diagnosis**:
```bash
# Check for .ugit directory
ls -la | grep ugit
pwd  # Verify current directory
```

**Solutions**:
```bash
# Option 1: Navigate to repository
cd /path/to/your/repository

# Option 2: Initialize new repository
ugit init

# Option 3: Check if you're in the right directory
find . -name ".ugit" -type d
```

### `Already a ugit repository`

**Problem**: Trying to initialize in existing repository.

**Diagnosis**:
```bash
ls -la .ugit/
```

**Solutions**:
- This is usually not an error - the repository already exists
- To start fresh, remove `.ugit` directory: `rm -rf .ugit`
- Navigate to a different directory for new repository

### Repository corruption

**Problem**: `.ugit` directory is damaged or incomplete.

**Diagnosis**:
```bash
# Check repository structure
ls -la .ugit/
ls -la .ugit/objects/
ls -la .ugit/refs/heads/

# Check for required files
test -f .ugit/index && echo "Index exists" || echo "Index missing"
test -f .ugit/refs/heads/main && echo "HEAD exists" || echo "HEAD missing"
```

**Solutions**:
```bash
# For missing index
touch .ugit/index

# For missing HEAD (if you have commits)
echo "your-commit-sha" > .ugit/refs/heads/main

# For complete corruption - start fresh
rm -rf .ugit
ugit init
# Re-add and commit your files
```

## Command Errors

### `No changes to commit`

**Problem**: Nothing staged for commit.

**Diagnosis**:
```bash
ugit status  # Check what's staged/modified
```

**Solutions**:
```bash
# Add files first
ugit add filename.txt
ugit add .  # Add all files

# Then commit
ugit commit -m "Your message"
```

### `Invalid SHA length: X`

**Problem**: Corrupted or invalid commit reference.

**Diagnosis**:
```bash
# Check HEAD reference
cat .ugit/refs/heads/main

# Check commit objects
ls .ugit/objects/
```

**Solutions**:
```bash
# If HEAD is corrupted, find a valid commit
ugit log  # Look for valid commits

# Manually fix HEAD reference
echo "valid-40-char-sha-hash" > .ugit/refs/heads/main

# If no valid commits, start fresh
rm -rf .ugit
ugit init
```

### `File not found` errors

**Problem**: ugit can't find specified files.

**Diagnosis**:
```bash
# Check file exists
ls -la filename.txt

# Check current directory
pwd

# Check for typos
ls | grep -i "partial-filename"
```

**Solutions**:
```bash
# Use correct filename (case-sensitive)
ugit add FileName.txt  # Not filename.txt

# Use relative or absolute paths
ugit add ./subdir/file.txt
ugit add /full/path/to/file.txt

# Check available files
ls -la
```

### `JSON decode error`

**Problem**: Corrupted object files.

**Diagnosis**:
```bash
# Find the problematic object
find .ugit/objects -type f -exec file {} \;

# Try to read a specific object (replace SHA)
python -c "
import zlib, json
with open('.ugit/objects/ab/cdef123...', 'rb') as f:
    data = zlib.decompress(f.read())
    print(data)
"
```

**Solutions**:
```bash
# Remove corrupted object (lose that commit/file)
rm .ugit/objects/ab/cdef123...

# Or start fresh repository
rm -rf .ugit
ugit init
```

## File System Issues

### `Permission denied` when reading files

**Problem**: Insufficient file system permissions.

**Diagnosis**:
```bash
# Check file permissions
ls -la filename.txt

# Check directory permissions
ls -la .ugit/
```

**Solutions**:
```bash
# Fix file permissions
chmod 644 filename.txt

# Fix directory permissions
chmod 755 .ugit/
chmod 644 .ugit/index

# Check disk space
df -h .
```

### Large file issues

**Problem**: ugit slow or failing with large files.

**Diagnosis**:
```bash
# Find large files
find . -type f -size +10M -exec ls -lh {} \;

# Check repository size
du -sh .ugit/
```

**Solutions**:
```bash
# Avoid large files
# Remove large files from repository
rm large-file.bin

# Use Git LFS for large files in production
# Consider file compression
```

### Path length issues (Windows)

**Problem**: Path too long on Windows.

**Solutions**:
- Move repository to shorter path
- Enable long path support in Windows
- Use shorter filenames

## Performance Issues

### Slow `ugit add` command

**Problem**: Adding files takes too long.

**Diagnosis**:
```bash
# Check number of files
find . -type f | wc -l

# Check file sizes
du -sh *
```

**Solutions**:
```bash
# Add files selectively
ugit add specific-file.txt

# Avoid adding large directories
# Split large operations into smaller ones
```

### Slow `ugit log` command

**Problem**: Log command is slow.

**Diagnosis**:
```bash
# Check number of commits
ugit log | grep "^commit" | wc -l

# Limit log output
ugit log --max-count 10
```

**Solutions**:
```bash
# Always use --max-count for large histories
ugit log --max-count 20

# Consider repository cleanup if too large
```

### Memory issues

**Problem**: ugit uses too much memory.

**Solutions**:
- Work with smaller files
- Process files in batches
- Restart ugit between large operations

## Data Corruption

### Detecting corruption

**Symptoms**:
- Invalid SHA errors
- JSON decode errors
- Missing files after checkout
- Inconsistent status output

**Diagnosis commands**:
```bash
# Check repository integrity
find .ugit -type f -name "*" -exec file {} \;

# Verify object format
python -c "
import os, zlib
for root, dirs, files in os.walk('.ugit/objects'):
    for file in files:
        path = os.path.join(root, file)
        try:
            with open(path, 'rb') as f:
                data = zlib.decompress(f.read())
                print(f'{path}: OK')
        except:
            print(f'{path}: CORRUPTED')
"
```

### Preventing corruption

**Best practices**:
```bash
# Regular backups
cp -r .ugit .ugit.backup

# Don't edit .ugit files manually
# Use ugit commands only

# Avoid interrupting ugit operations
# Let commands complete
```

### Recovery options

**For minor corruption**:
```bash
# Remove corrupted objects
rm .ugit/objects/corrupted-file

# Rebuild index
rm .ugit/index
ugit add .
```

**For major corruption**:
```bash
# Export files
cp -r . ../backup-without-ugit
rm -rf .ugit

# Start fresh
ugit init
ugit add .
ugit commit -m "Recovered repository"
```

## Debug Information

### Collecting debug information

When reporting issues, include:

```bash
# System information
uname -a  # Linux/macOS
ver       # Windows

# Python information
python --version
python -c "import sys; print(sys.executable)"

# ugit information
ugit --version  # If available
python -m pip list | grep ugit

# Repository state
ls -la .ugit/
ugit status
ugit log --max-count 3

# Error reproduction
# Include exact commands and error messages
```

### Common debug commands

```bash
# Verify repository structure
find .ugit -type f | sort

# Check object storage
ls -la .ugit/objects/*

# Verify index format
cat .ugit/index

# Check references
cat .ugit/refs/heads/main

# Test object reading
python -c "
from ugit.core.objects import get_object
try:
    print(get_object('commit-sha-here'))
except Exception as e:
    print(f'Error: {e}')
"
```

### Verbose output

For detailed debugging, you can add debug prints:

```python
# Add to ~/.ugitrc (if implemented) or modify source
DEBUG = True

# Or set environment variable
export UGIT_DEBUG=1
```

## Getting Additional Help

If this guide doesn't solve your issue:

1. **Search existing issues**: Check GitHub issues for similar problems
2. **Create minimal reproduction**: Provide exact steps to reproduce
3. **Include debug information**: Use the debug commands above
4. **Open an issue**: Use the bug report template on GitHub

### Information to include in bug reports

- Operating system and version
- Python version
- ugit version or commit hash
- Exact commands that cause the issue
- Complete error messages
- Repository state (if safe to share)

Remember: Most issues are related to environment setup, file permissions, or misunderstanding ugit's intended scope.