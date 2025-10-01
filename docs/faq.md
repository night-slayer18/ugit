# Frequently Asked Questions (FAQ)

This document answers common questions about ugit usage, features, and troubleshooting.

## General Questions

### What is ugit?

ugit is a comprehensive Git implementation written in Python. It provides full version control functionality including repository initialization, file staging, commits, branching, merging, stashing, remote repositories, and a beautiful web interface.

### How is ugit different from Git?

ugit implements most core features of Git with some differences:

**Implemented Features:**
- Repository initialization and management
- File staging and commits with full metadata
- Complete branching and merging system, including conflict resolution
- Stash management (save, pop, apply, list, drop)
- Remote repositories (clone, fetch, pull, push for local protocols)
- Comprehensive diff and history viewing
- `.ugitignore` support for ignoring files
- Configuration system
- Beautiful web interface for repository browsing

**Key Differences:**
- Uses `.ugit` directory instead of `.git`
- Simplified object storage format (JSON and zlib compression)
- Remote operations currently limited to local file system protocols
- No sub-modules or other advanced Git features
- Educational focus with clear, readable code

### Is ugit compatible with Git?

No, ugit uses its own storage format (`.ugit` directory) and is not directly compatible with Git repositories. However, ugit provides similar functionality and workflow patterns, making it easy to transition between the two systems.

### Can I use ugit for real projects?

ugit is suitable for:
- ✅ Small to medium projects
- ✅ Learning version control concepts
- ✅ Team collaboration with remote repositories on a shared file system
- ✅ Personal and educational projects
- ✅ Projects requiring web-based repository browsing
- ⚠️ Large codebases (limited performance optimization)
- ❌ Integration with Git-specific tools and services

## Installation and Setup

### What are the system requirements?

- Python 3.9 or higher
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

ugit has a `reset` command for this.

```bash
# Go back to a previous commit, but keep the changes in your files
ugit reset <commit-sha>

# Go back to a previous commit and discard all changes since then
ugit reset --hard <commit-sha>
```

## Branching and Merging

### How do I create and use branches?

```bash
# Create a new branch
ugit branch feature-login

# Switch to the branch
ugit checkout feature-login

# Or create and switch in one command
ugit checkout -b feature-payment

# List all branches
ugit branch

# Delete a branch
ugit branch -d old-feature
```

### How do I merge branches?

```bash
# Switch to target branch (usually main)
ugit checkout main

# Merge feature branch
ugit merge feature-login

# Force merge commit (no fast-forward)
ugit merge feature-payment --no-ff
```

### What's the difference between fast-forward and no-ff merge?

- **Fast-forward**: Moves branch pointer forward (linear history)
- **No fast-forward (`--no-ff`)**: Creates explicit merge commit (branched history)

## Stashing

### What is stashing and when do I use it?

Stashing temporarily saves your changes without committing them. Use it when:
- Switching branches with uncommitted changes
- Pulling updates but having local modifications
- Quickly experimenting then returning to original work

### How do I use stash?

```bash
# Save current changes to stash
ugit stash
ugit stash save "Work in progress on login feature"

# List all stashes
ugit stash list

# Apply most recent stash
ugit stash pop

# Apply specific stash by index
ugit stash pop 1

# Apply stash without removing it
ugit stash apply

# Remove a stash without applying
ugit stash drop
```

## Remote Repositories

### How do I work with remote repositories?

```bash
# Clone a repository from a local path
ugit clone /path/to/remote/repo

# Add a remote to existing repository
ugit remote add origin /path/to/remote/repo

# List remotes
ugit remote -v

# Fetch changes from remote
ugit fetch origin

# Pull and merge changes
ugit pull origin main

# Push changes to remote
ugit push origin main
```

### What's the difference between fetch and pull?

- **`ugit fetch`**: Downloads changes but doesn't merge them
- **`ugit pull`**: Downloads changes AND merges them into current branch

### Can I use ugit with GitHub/GitLab?

No. `ugit`'s remote commands currently only support local file system paths (e.g., cloning from another folder on your computer). It does not support network protocols like HTTP or SSH, so it cannot interact with services like GitHub or GitLab.

## Web Interface

### How do I use the web interface?

```bash
# Install with web support
pip install ugit-cli[web]

# Start web interface
ugit serve

# Custom host and port
ugit serve --host 0.0.0.0 --port 8080

# Don't open browser automatically
ugit serve --no-browser
```

### What features does the web interface provide?

- Beautiful repository file browser
- Syntax-highlighted code viewing
- Interactive commit history timeline
- Responsive design for desktop and mobile
- Real-time repository exploration

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
# Checkout the main branch to return to the latest version
ugit checkout main
```

### Can I see what changed in a specific commit?

Yes, you can use `ugit diff` to compare a commit with its parent.

```bash
# Show changes from a specific commit
ugit diff <commit-sha>~1 <commit-sha>
```

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

Create a `.ugitignore` file in the root of your repository. Add file names, directory names, or patterns to this file, and `ugit` will ignore them.

**Example `.ugitignore`:**
```
# Ignore python cache
__pycache__/

# Ignore log files
*.log

# Ignore specific directory
build/
```

### Can I remove files from tracking?

ugit doesn't have a built-in `rm` command. To stop tracking a file:
1. Remove it from your working directory
2. Run `ugit add .` to stage the deletion
3. The next commit won't include the file.

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

ugit focuses on core version control features. Some advanced Git features are intentionally omitted to maintain simplicity, such as:
- Rebasing
- Submodules
- Git hooks
- Complex network protocols (only local file system remotes are supported)

## Comparison with Git

### When should I use ugit vs Git?

**Use ugit for**:
- Learning version control concepts
- Simple personal projects
- Educational purposes
- When you need minimal overhead

**Use Git for**:
- Team collaboration over a network
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
