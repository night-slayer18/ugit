# Changelog

All notable changes to ugit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-XX

### 🎉 Major Release - 30+ New Features

This is a major feature release with comprehensive enhancements to ugit, adding 30+ advanced features that bring ugit closer to production-grade version control.

### ✨ Added

#### Core Git Features
- **Tags** - Lightweight and annotated tags for marking releases
  - `ugit tag <name>` - Create lightweight tag
  - `ugit tag -a <name> -m <message>` - Create annotated tag
  - `ugit tag -l` - List all tags
  - `ugit tag -d <name>` - Delete tag

- **Reflog** - Complete history tracking for recovery
  - `ugit reflog` - View reflog entries
  - Automatic reflog creation on commits, checkouts, and branch operations
  - Recovery support for lost commits

- **Blame** - Line-by-line authorship tracking
  - `ugit blame <file>` - Show who changed each line
  - `ugit blame <file> <commit>` - Blame specific commit

- **Cherry-pick** - Apply commits from other branches
  - `ugit cherry-pick <commit>` - Apply commit to current branch
  - `ugit cherry-pick -n <commit>` - Apply without committing

- **Grep** - Search across repository
  - `ugit grep <pattern>` - Search for pattern
  - `ugit grep -i <pattern>` - Case-insensitive search
  - `ugit grep <pattern> <path>` - Search in specific path

- **Archive** - Create archives from commits
  - `ugit archive <output>` - Create archive
  - `ugit archive --format tar <output>` - Specify format (tar/zip)

- **Aliases** - Custom command shortcuts
  - `ugit alias <name> <command>` - Create alias
  - `ugit alias -l` - List all aliases

- **Stats** - Repository statistics
  - `ugit stats` - Show repository statistics (commits, branches, objects, size)

- **Bisect** - Binary search for bugs
  - `ugit bisect start` - Start bisect session
  - `ugit bisect good` - Mark commit as good
  - `ugit bisect bad` - Mark commit as bad
  - `ugit bisect reset` - Reset bisect session

- **Rebase** - Reapply commits on top of another branch
  - `ugit rebase <branch>` - Rebase current branch onto target
  - `ugit rebase -i <branch>` - Interactive rebase

- **Squash Merge** - Combine multiple commits
  - `ugit merge --squash <branch>` - Squash all commits into one

- **Merge Strategies** - Advanced merge options
  - `ugit merge -s ours <branch>` - Keep our version
  - `ugit merge -s theirs <branch>` - Use their version

- **Garbage Collection** - Clean up unreachable objects
  - `ugit gc` - Run garbage collection
  - `ugit gc --aggressive` - Aggressive cleanup

- **Fsck** - Repository integrity checks
  - `ugit fsck` - Check repository integrity
  - `ugit fsck --full` - Full integrity check

- **Worktree** - Multiple working directories
  - `ugit worktree add <path>` - Add new worktree
  - `ugit worktree list` - List worktrees
  - `ugit worktree remove <path>` - Remove worktree

- **Hooks System** - Pre and post-commit hooks
  - Support for `pre-commit` and `post-commit` hooks
  - Automatic hook execution on commits

- **Interactive Staging** - Selective file staging
  - `ugit add -i` - Interactive staging interface

- **Commit Templates** - Automatic commit message templates
  - Support for commit message templates
  - Template prompting when no message provided

- **Shallow Clone** - Limited history cloning
  - `ugit clone --depth <n> <url>` - Clone with limited history

#### Performance & Optimization
- **Parallel Operations** - Concurrent file processing
  - Automatic parallel processing for large file operations
  - Integrated into `add` command

- **Index Caching** - Performance optimization
  - LRU cache for index reads
  - Significant performance improvement for large repositories

- **Delta Compression** - Storage optimization framework
  - Framework for storing objects as deltas
  - Reduces storage requirements

- **Pack Files** - Efficient object storage
  - `ugit pack` - Pack objects into pack files
  - `ugit pack --unpack <file>` - Unpack objects from pack file

#### Security & Signing
- **GPG Signing** - Sign commits and tags
  - `ugit gpg sign-commit <commit>` - Sign commit
  - `ugit gpg sign-tag <tag>` - Sign tag
  - `ugit gpg verify <object>` - Verify signature

#### Network & Remotes
- **HTTP/HTTPS Remote Support** - Fetch and push via HTTP
  - Basic HTTP remote support (experimental)
  - Requires `httpx` package

#### Web UI Enhancements
- **Blame API** - `/api/blame` endpoint for web interface
- **Diff API** - `/api/diff` endpoint for comparing commits
- **Search API** - `/api/search` endpoint for repository search

#### Infrastructure
- **Progress Indicators** - Progress bars for long operations
- **Atomic File Operations** - Prevent corruption during writes
- **Input Validation** - Comprehensive validation for SHA, paths, branch names
- **Centralized Logging** - Improved logging system
- **Enhanced Type Hints** - Better type safety throughout codebase

### 🔧 Changed

- **Index Operations** - Now use atomic writes for data integrity
- **Reference Updates** - All ref updates use atomic operations
- **Config Updates** - Config file updates are atomic
- **Path Validation** - Enhanced path validation to prevent traversal attacks
- **Error Handling** - Improved error messages and handling throughout

### 🐛 Fixed

- Fixed potential data corruption during index writes
- Fixed path traversal vulnerabilities
- Improved cross-platform compatibility (Mac, Linux, Windows)
- Fixed edge cases in merge operations
- Improved error messages for better user experience

### 📚 Documentation

- Comprehensive test suite with 144+ tests
- Updated README with all new features
- Updated user guide with new commands
- Updated architecture documentation
- Added testing documentation
- Updated FAQ with new features

### 🧪 Testing

- Added 50+ new tests for all new features
- Cross-platform compatibility tests
- CI/CD configuration for Mac, Linux, Windows
- Test coverage for all major features

## [1.3.0] - Previous Release

### Added
- Web interface with beautiful dark mode
- Remote repository support
- Stash management
- Enhanced diff capabilities
- Configuration system

### Changed
- Improved error handling
- Better documentation

## [1.2.0] - Previous Release

### Added
- Branch management
- Merge functionality
- Status command improvements

## [1.1.0] - Previous Release

### Added
- Checkout functionality
- Log command with filtering
- Diff command

## [1.0.0] - Initial Release

### Added
- Repository initialization
- File staging
- Commit creation
- Basic history viewing

[2.0.0]: https://github.com/night-slayer18/ugit/releases/tag/v2.0.0
[1.3.0]: https://github.com/night-slayer18/ugit/releases/tag/v1.3.0

