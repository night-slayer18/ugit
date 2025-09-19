# Frequently Asked Questions (FAQ)

This document answers common questions about ugit usage, features, and troubleshooting.

## General Questions

### What is ugit?

ugit is a minimal Git implementation written in Python. It provides core version control functionality including repository initialization, file staging, commits, history viewing, and basic checkout operations.

### How is ugit different from Git?

ugit implements only the core features of Git:
- **Similarities**: Repository initialization, file staging, commits, history, basic checkout
- **Differences**: No branches, merging, remotes, advanced features, or complete Git compatibility
- **Purpose**: Educational tool and minimal version control for simple projects

### Is ugit compatible with Git?

No, ugit uses its own storage format (`.ugit` directory) and is not compatible with Git repositories. ugit is designed as a standalone, simplified version control system.

### Can I use ugit for real projects?

ugit is suitable for:
- ✅ Small personal projects
- ✅ Learning version control concepts
- ✅ Simple file tracking
- ❌ Large codebases
- ❌ Team collaboration
- ❌ Production environments

## Installation and Setup

### What are the system requirements?

- Python 3.8 or higher
- Operating System: macOS, Linux, or Windows
- About 10MB of disk space

### How do I install ugit?

See our [Installation Guide](installation.md) for detailed instructions. Quick version:

```bash
pip install git+https://github.com/night-slayer18/ugit.git
```

### Why can't I run `ugit` command after installation?

This usually means the installation directory isn't in your PATH. Solutions:

1. **Use full path**: `/path/to/python/bin/ugit`
2. **Add to PATH**: Add the installation directory to your shell's PATH
3. **Use module syntax**: `python -m ugit.cli`

### How do I update ugit?

```bash
pip install --upgrade git+https://github.com/night-slayer18/ugit.git
```

## Basic Usage

### How do I create my first repository?

```bash
mkdir my-project
cd my-project
ugit init
echo "Hello, ugit!" > README.txt
ugit add README.txt
ugit commit -m "Initial commit"
```

### What's the difference between `ugit add` and `ugit commit`?

- **`ugit add`**: Stages files for the next commit (adds to staging area)
- **`ugit commit`**: Creates a permanent snapshot of staged files

Think of it as: `add` = prepare, `commit` = save.

### How do I see what files have changed?

```bash
ugit status
```

This shows:
- Files staged for commit (green)
- Modified but unstaged files (red)
- Untracked files (red)

### How do I view my commit history?

```bash
# All commits
ugit log

# Last 5 commits
ugit log --max-count 5
```

### Can I undo a commit?

ugit doesn't have built-in commit undoing. You can:
1. Checkout a previous commit: `ugit checkout <commit-sha>`
2. Make new changes and commit them
3. This effectively creates a new state without deleting history

## Advanced Usage

### How do I go back to a previous version?

```bash
# View history to find the commit you want
ugit log

# Checkout specific commit
ugit checkout abc123def456789

# Your working directory now matches that commit
```

**Warning**: This changes your working directory files.

### How do I get back to the latest version?

```bash
# Find the latest commit SHA from log
ugit log --max-count 1

# Checkout the latest commit
ugit checkout <latest-commit-sha>
```

### Can I see what changed in a specific commit?

ugit doesn't have a built-in diff command. You can:
1. Checkout the commit
2. Look at the files
3. Compare manually with previous versions

### How do I add all files at once?

```bash
ugit add .
```

This adds all files in the current directory and subdirectories.

### What happens if I run `ugit init` in an existing repository?

ugit will detect the existing repository and display "Already a ugit repository" without making changes.

## Troubleshooting

### "fatal: not a ugit repository"

This means you're not in a directory with a ugit repository. Solutions:
1. Navigate to a directory with a `.ugit` folder
2. Run `ugit init` to create a new repository
3. Check you're in the right directory with `ls -la`

### "File not found" errors

Common causes:
1. **Typo in filename**: Check spelling and case sensitivity
2. **Wrong directory**: Verify you're in the correct location
3. **File doesn't exist**: Use `ls` to see available files

### Commit SHA errors

If you see "Invalid SHA length" or similar:
1. Ensure you're using the full 40-character SHA from `ugit log`
2. Copy the SHA carefully without extra spaces
3. The repository might be corrupted - try creating a fresh one

### "No changes to commit"

This means no files are staged. Solutions:
1. Add files first: `ugit add filename`
2. Check status: `ugit status`
3. Verify files have actually changed

### Performance issues

ugit may be slow with:
- Very large files (>100MB)
- Many files (>1000)
- Deep directory structures

Consider using Git for large projects.

## File Management

### Which files should I track with ugit?

**Include**:
- Source code files
- Configuration files
- Documentation
- Small data files

**Exclude**:
- Large binary files
- Temporary files
- Build artifacts
- System files (`.DS_Store`, etc.)

### How do I ignore files?

ugit doesn't have built-in ignore functionality. Manually avoid adding files you don't want to track.

### Can I remove files from tracking?

ugit doesn't have a built-in `rm` command. To stop tracking a file:
1. Remove it from your working directory
2. The next commit won't include it

### What's the maximum file size ugit can handle?

ugit can theoretically handle any file size, but performance degrades with large files. Recommended limits:
- Individual files: <10MB
- Total repository: <100MB

## Error Messages

### "Permission denied"

Usually an OS-level permission issue:
1. Check file/directory permissions
2. Ensure you have write access to the directory
3. On Windows, try running as administrator

### "Invalid JSON" or parsing errors

This suggests repository corruption:
1. Check `.ugit/objects/` directory for corrupted files
2. Try creating a fresh repository
3. Restore from backups if available

### "SHA mismatch" or integrity errors

Object corruption has occurred:
1. The repository may be corrupted
2. Try `ugit status` to check repository state
3. Consider starting a fresh repository

## Development and Contributing

### How can I contribute to ugit?

1. Read the [Contributing Guide](../CONTRIBUTING.md)
2. Check the [Developer Guide](developer-guide.md)
3. Look at open issues on GitHub
4. Submit bug reports or feature requests

### How do I report bugs?

1. Use the [Bug Report template](../.github/ISSUE_TEMPLATE/bug_report.yml)
2. Include your Python version, OS, and ugit version
3. Provide steps to reproduce the issue
4. Include error messages and logs

### Can I add new features to ugit?

Yes! See our [Developer Guide](developer-guide.md) for:
- Setting up development environment
- Understanding the codebase
- Adding new commands
- Testing procedures

### Why isn't feature X implemented?

ugit focuses on core version control features. Some Git features are intentionally omitted:
- Branches and merging (complexity)
- Remote repositories (network code)
- Rebasing (advanced workflow)
- Patches (specialized use case)

## Comparison with Git

### When should I use ugit vs Git?

**Use ugit for**:
- Learning version control concepts
- Simple personal projects
- Educational purposes
- When you need minimal overhead

**Use Git for**:
- Team collaboration
- Large projects
- Open source development
- Production environments
- When you need advanced features

### Can I migrate from ugit to Git?

There's no automatic migration tool. To switch:
1. Export your files from ugit
2. Initialize a new Git repository
3. Copy files and recreate commits manually

### Can I migrate from Git to ugit?

Similar process:
1. Copy files from Git repository
2. Initialize ugit repository
3. Recreate commit history manually

## Getting Help

### Where can I find more help?

1. **Documentation**: Check the [docs/](README.md) directory
2. **GitHub Issues**: Search existing issues or create new ones
3. **GitHub Discussions**: Ask questions and discuss with the community

### How do I get support?

1. **Bug reports**: Use the bug report template
2. **Questions**: Use the question template or discussions
3. **Feature requests**: Use the feature request template

### Is there a community forum?

Use GitHub Discussions for:
- General questions
- Usage tips
- Feature discussions
- Community support

Remember: ugit is a volunteer project, so response times may vary.