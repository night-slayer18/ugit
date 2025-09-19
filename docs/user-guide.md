# User Guide

This comprehensive guide will teach you how to use ugit for version control.

## Table of Contents

- [Getting Started](#getting-started)
- [Basic Commands](#basic-commands)
- [Working with Files](#working-with-files)
- [Commit History](#commit-history)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)

## Getting Started

### What is ugit?

ugit is a minimal Git implementation in Python that provides core version control functionality. It's designed to be simple, educational, and functional for basic version control needs.

### Your First Repository

1. **Create a new directory for your project:**
   ```bash
   mkdir my-project
   cd my-project
   ```

2. **Initialize a ugit repository:**
   ```bash
   ugit init
   ```

3. **Create your first file:**
   ```bash
   echo "Hello, ugit!" > README.txt
   ```

4. **Add the file to staging:**
   ```bash
   ugit add README.txt
   ```

5. **Create your first commit:**
   ```bash
   ugit commit -m "Initial commit"
   ```

Congratulations! You've created your first ugit repository.

## Basic Commands

### `ugit init`

Initialize a new ugit repository in the current directory.

```bash
ugit init
```

This creates a `.ugit` directory to store repository data.

### `ugit add <file>`

Add files to the staging area (index) to prepare them for commit.

```bash
# Add a specific file
ugit add filename.txt

# Add all files in current directory
ugit add .

# Add multiple files
ugit add file1.txt file2.py
```

### `ugit commit -m "message"`

Create a commit with the staged changes.

```bash
ugit commit -m "Add new feature"
```

**Commit Message Guidelines:**
- Use present tense ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Be descriptive but concise

### `ugit status`

Show the current state of your working directory and staging area.

```bash
ugit status
```

This displays:
- Files staged for commit
- Modified files not yet staged
- Untracked files
- Deleted files

### `ugit log`

View the commit history.

```bash
# Show all commits
ugit log

# Show limited number of commits
ugit log --max-count 5
```

### `ugit checkout <commit>`

Switch to a specific commit state.

```bash
ugit checkout abc123def456789
```

**Warning:** This will modify your working directory to match the specified commit.

## Working with Files

### Adding Files

```bash
# Add individual files
ugit add main.py
ugit add src/module.py

# Add all files
ugit add .

# Add all Python files
ugit add *.py
```

### Checking File Status

```bash
ugit status
```

File states:
- **Staged**: Ready to be committed (green)
- **Modified**: Changed but not staged (red)
- **Untracked**: New files not yet added (red)
- **Deleted**: Removed files (red)

### Making Commits

```bash
# Simple commit
ugit commit -m "Fix bug in user authentication"

# Multi-line commit message
ugit commit -m "Implement user registration

- Add registration form
- Add email validation
- Add password strength requirements"
```

## Commit History

### Viewing History

```bash
# Show all commits
ugit log

# Show limited commits
ugit log --max-count 10
```

Each commit shows:
- Commit hash (SHA)
- Author information
- Timestamp
- Commit message

### Understanding Commit Hashes

Commit hashes are unique identifiers for each commit. You can use them to:
- Reference specific commits
- Checkout previous states
- Compare changes

Example commit hash: `abc123def456789012345678901234567890abcd`

## Advanced Usage

### Working with Different States

1. **Make changes to files**
2. **Stage changes:** `ugit add file.txt`
3. **Review staged changes:** `ugit status`
4. **Commit changes:** `ugit commit -m "Description"`

### Repository Navigation

```bash
# Check current repository status
ugit status

# View recent commits
ugit log --max-count 5

# Go back to a previous commit
ugit checkout <commit-hash>

# Return to latest commit
ugit checkout <latest-commit-hash>
```

### File Management

```bash
# Add all modified files
ugit add .

# Check what will be committed
ugit status

# Create commit
ugit commit -m "Update multiple files"
```

## Best Practices

### Commit Messages

**Good commit messages:**
```
Add user authentication system
Fix memory leak in file parser
Update documentation for API endpoints
```

**Poor commit messages:**
```
fix
updated stuff
changes
```

### Commit Frequency

- Commit often with small, logical changes
- Each commit should represent a complete, working change
- Don't commit broken or incomplete code

### File Organization

- Use meaningful file and directory names
- Keep related files together
- Add `.ugitignore` for files you don't want to track (if implemented)

### Repository Hygiene

- Regularly check `ugit status` to stay aware of changes
- Review changes before committing
- Write descriptive commit messages
- Keep commits focused on single changes

## Common Workflows

### Basic Development Workflow

1. **Start working:**
   ```bash
   ugit status  # Check current state
   ```

2. **Make changes:**
   ```bash
   # Edit files as needed
   ```

3. **Stage changes:**
   ```bash
   ugit add .
   ```

4. **Review before commit:**
   ```bash
   ugit status
   ```

5. **Commit:**
   ```bash
   ugit commit -m "Descriptive message"
   ```

### Checking History

```bash
# See what you've been working on
ugit log --max-count 10

# Check current status
ugit status
```

### Exploring Previous Versions

```bash
# View commit history
ugit log

# Checkout specific commit
ugit checkout abc123def

# Look around, then return to latest
ugit checkout <latest-commit>
```

## Tips and Tricks

1. **Use descriptive commit messages** - Your future self will thank you
2. **Commit early and often** - Small commits are easier to understand
3. **Check status frequently** - Always know what state your repository is in
4. **Use meaningful file names** - Makes tracking changes easier
5. **Keep commits atomic** - One logical change per commit

## Next Steps

- Learn about [API Reference](api-reference.md) for advanced usage
- Check out [Examples](examples.md) for real-world scenarios  
- Read [Troubleshooting](troubleshooting.md) for common issues
- Explore [Developer Guide](developer-guide.md) to contribute to ugit