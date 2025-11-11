# New Features Guide (v2.0.0)

This guide covers all the new features added in ugit v2.0.0.

## Table of Contents

1. [Tags](#tags)
2. [Reflog](#reflog)
3. [Blame](#blame)
4. [Cherry-pick](#cherry-pick)
5. [Grep](#grep)
6. [Archive](#archive)
7. [Aliases](#aliases)
8. [Stats](#stats)
9. [Bisect](#bisect)
10. [Rebase](#rebase)
11. [Squash Merge](#squash-merge)
12. [Merge Strategies](#merge-strategies)
13. [Garbage Collection](#garbage-collection)
14. [Fsck](#fsck)
15. [Worktree](#worktree)
16. [Hooks](#hooks)
17. [Interactive Staging](#interactive-staging)
18. [Commit Templates](#commit-templates)
19. [Shallow Clone](#shallow-clone)
20. [GPG Signing](#gpg-signing)
21. [Pack Files](#pack-files)
22. [Delta Compression](#delta-compression)
23. [HTTP Remotes](#http-remotes)
24. [Web UI Enhancements](#web-ui-enhancements)

## Tags

Tags allow you to mark specific commits for easy reference, typically for releases.

### Lightweight Tags

```bash
# Create a lightweight tag
ugit tag v1.0.0

# Tag a specific commit
ugit tag v1.0.0 <commit-sha>
```

### Annotated Tags

```bash
# Create an annotated tag with message
ugit tag -a v1.0.0 -m "Release version 1.0.0"

# List all tags
ugit tag -l

# Delete a tag
ugit tag -d v1.0.0
```

## Reflog

Reflog tracks all changes to HEAD and branches, allowing you to recover lost commits.

```bash
# View reflog for current branch
ugit reflog

# View reflog for specific branch
ugit reflog main

# Reflog is automatically created on:
# - Commits
# - Checkouts
# - Branch operations
```

## Blame

Blame shows who last modified each line of a file.

```bash
# Blame current version
ugit blame file.txt

# Blame specific commit
ugit blame file.txt <commit-sha>

# With line numbers (default)
ugit blame -L file.txt
```

## Cherry-pick

Apply commits from other branches to the current branch.

```bash
# Cherry-pick a commit
ugit cherry-pick <commit-sha>

# Cherry-pick without committing (just stage)
ugit cherry-pick -n <commit-sha>
```

## Grep

Search for patterns across the repository.

```bash
# Search for pattern
ugit grep "function_name"

# Case-insensitive search
ugit grep -i "pattern"

# Search in specific path
ugit grep "pattern" src/

# Search in specific commit
ugit grep "pattern" "" <commit-sha>
```

## Archive

Create archives (tar/zip) from commits.

```bash
# Create tar archive (default)
ugit archive output.tar

# Create zip archive
ugit archive --format zip output.zip

# Archive specific commit
ugit archive output.tar <commit-sha>
```

## Aliases

Create custom command shortcuts.

```bash
# Create alias
ugit alias st status
ugit alias co checkout
ugit alias br branch

# List all aliases
ugit alias -l

# Use alias
ugit st  # Same as ugit status
```

## Stats

View repository statistics.

```bash
# Show repository statistics
ugit stats

# Output includes:
# - Number of commits
# - Number of branches
# - Number of tags
# - Number of objects
# - Tracked files count
# - Repository size
```

## Bisect

Binary search for finding the commit that introduced a bug.

```bash
# Start bisect session
ugit bisect start

# Mark current commit as bad
ugit bisect bad

# Mark current commit as good
ugit bisect good

# Skip current commit
ugit bisect skip

# Reset bisect session
ugit bisect reset

# Start with known good and bad commits
ugit bisect start <bad-commit> <good-commit>
```

## Rebase

Reapply commits on top of another branch.

```bash
# Rebase current branch onto another branch
ugit rebase main

# Interactive rebase
ugit rebase -i main

# Rebase onto different base
ugit rebase --onto new-base old-base
```

## Squash Merge

Combine all commits from a branch into a single commit.

```bash
# Squash merge a branch
ugit merge --squash feature-branch

# This creates a single commit with all changes from the branch
```

## Merge Strategies

Control how merges are resolved.

```bash
# Keep our version (current branch)
ugit merge -s ours feature-branch

# Use their version (feature branch)
ugit merge -s theirs feature-branch
```

## Garbage Collection

Clean up unreachable objects to reclaim disk space.

```bash
# Run garbage collection
ugit gc

# Aggressive cleanup
ugit gc --aggressive
```

## Fsck

Check repository integrity.

```bash
# Basic integrity check
ugit fsck

# Full integrity check (verifies all objects)
ugit fsck --full
```

## Worktree

Work with multiple working directories for the same repository.

```bash
# Add a new worktree
ugit worktree add ../other-directory

# Add worktree on specific branch
ugit worktree add -b new-branch ../other-directory

# List all worktrees
ugit worktree list

# Remove worktree
ugit worktree remove ../other-directory
```

## Hooks

Execute custom scripts at various points in the workflow.

### Pre-commit Hook

Create `.ugit/hooks/pre-commit`:

```bash
#!/bin/sh
echo "Running pre-commit checks..."
# Your checks here
exit 0  # 0 = allow commit, non-zero = block commit
```

### Post-commit Hook

Create `.ugit/hooks/post-commit`:

```bash
#!/bin/sh
echo "Commit created: $1"
# Your post-commit actions here
```

## Interactive Staging

Selectively stage files with an interactive interface.

```bash
# Interactive staging
ugit add -i

# Interface allows you to:
# - Select files to stage
# - See file status (modified, untracked, deleted)
# - Toggle file selection
```

## Commit Templates

Use templates for commit messages.

### Set Template

```bash
# Set template via config
ugit config commit.template .ugit/COMMIT_TEMPLATE

# Or create .ugit/COMMIT_TEMPLATE directly
```

### Use Template

```bash
# Commit without -m will prompt with template
ugit commit

# Template will be shown, you can edit or use as-is
```

## Shallow Clone

Clone repository with limited history depth.

```bash
# Clone with depth 1 (only latest commit)
ugit clone --depth 1 <url>

# Clone with depth 5
ugit clone --depth 5 <url>
```

## GPG Signing

Sign commits and tags with GPG for verification.

### Prerequisites

```bash
# Install GPG (if not already installed)
# macOS: brew install gnupg
# Linux: sudo apt-get install gnupg
# Windows: Download from GnuPG website
```

### Signing

```bash
# Sign a commit
ugit gpg sign-commit <commit-sha>

# Sign with specific key
ugit gpg sign-commit <commit-sha> -k <key-id>

# Sign a tag
ugit gpg sign-tag <tag-sha>

# Verify signature
ugit gpg verify <object-sha>
```

## Pack Files

Pack multiple objects into efficient pack files.

```bash
# Pack all objects
ugit pack

# Pack specific objects
ugit pack <sha1> <sha2> <sha3>

# Unpack objects
ugit pack --unpack pack-file.pack
```

## Delta Compression

Store objects as deltas to save space.

```python
from ugit.commands.delta_compression import create_delta, apply_delta

# Create delta between two objects
delta = create_delta(base_sha, target_sha)

# Apply delta to reconstruct object
reconstructed = apply_delta(base_sha, delta)
```

## HTTP Remotes

Fetch and push to HTTP/HTTPS remote repositories (experimental).

### Prerequisites

```bash
pip install httpx
```

### Usage

```bash
# Fetch from HTTP remote
ugit fetch http://example.com/repo.git

# Push to HTTP remote
ugit push http://example.com/repo.git main
```

**Note**: HTTP remote support is experimental and requires a compatible server.

## Web UI Enhancements

The web interface now includes additional features.

### Blame View

Access blame information via the web interface:
- Navigate to a file
- View line-by-line authorship
- See commit information for each line

### Diff View

Compare commits via the web interface:
- View differences between commits
- Side-by-side comparison
- File-by-file diff navigation

### Search

Search repository content via the web interface:
- Full-text search across repository
- Filter by path
- Case-insensitive search option

## Performance Improvements

### Parallel Operations

Large file operations (like `ugit add` with many files) now use parallel processing automatically.

### Index Caching

Index reads are cached for better performance on large repositories.

### Progress Indicators

Long-running operations show progress bars.

## Security Enhancements

### Atomic Operations

All critical file operations (index, refs, config) use atomic writes to prevent corruption.

### Input Validation

Comprehensive validation for:
- SHA hashes
- File paths (prevents traversal attacks)
- Branch names
- Commit messages

### Path Sanitization

All paths are sanitized before processing to prevent security issues.

## Best Practices

1. **Use tags for releases** - Tag important commits
2. **Check reflog before panic** - Lost commits can often be recovered
3. **Use bisect for debugging** - Find bugs faster
4. **Run gc periodically** - Keep repository clean
5. **Use hooks for automation** - Automate checks and notifications
6. **Use aliases for efficiency** - Create shortcuts for common commands
7. **Use shallow clones for large repos** - Save time and space
8. **Sign important commits** - Use GPG for verification

## Migration Guide

If upgrading from v1.x:

1. All existing repositories are compatible
2. New features are opt-in (use commands as needed)
3. No breaking changes to existing commands
4. Reflog will be created automatically on next commit
5. Hooks directory will be created when needed

## Troubleshooting

### GPG not found

```bash
# Check if GPG is installed
gpg --version

# Install if missing
# macOS: brew install gnupg
# Linux: sudo apt-get install gnupg
```

### HTTP remote fails

```bash
# Ensure httpx is installed
pip install httpx

# Check remote URL format
# Should be: http:// or https://
```

### Pack file errors

```bash
# Verify pack file integrity
ugit fsck

# Unpack and repack if needed
ugit pack --unpack <file>
ugit pack
```

For more help, see [Troubleshooting Guide](troubleshooting.md).

