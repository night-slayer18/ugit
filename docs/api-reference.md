# API Reference

This document provides detailed technical documentation for ugit's internal APIs and modules.

## Table of Contents

- [Core Modules](#core-modules)
- [Command Modules](#command-modules)
- [Utility Modules](#utility-modules)
- [Data Structures](#data-structures)
- [Error Handling](#error-handling)

## Core Modules

### `ugit.core.objects`

Handles object storage and retrieval for blobs, trees, and commits.

#### Functions

##### `hash_object(data: bytes, obj_type: str = "blob", write: bool = True) -> str`

Hash and optionally store an object.

**Parameters:**
- `data` (bytes): Raw object data
- `obj_type` (str): Object type ("blob", "tree", "commit")
- `write` (bool): Whether to write to disk

**Returns:**
- `str`: SHA-1 hash of the object

**Example:**
```python
from ugit.core.objects import hash_object

# Hash a blob
sha = hash_object(b"Hello, world!", "blob", True)
print(sha)  # e.g., "af5626b4a114abcb82d63db7c8082c3c4756e51b"
```

##### `get_object(sha: str) -> Tuple[str, bytes]`

Retrieve an object by its SHA-1 hash.

**Parameters:**
- `sha` (str): 40-character SHA-1 hash

**Returns:**
- `Tuple[str, bytes]`: Object type and raw data

**Raises:**
- `FileNotFoundError`: Object doesn't exist
- `ValueError`: Invalid SHA or object format

**Example:**
```python
from ugit.core.objects import get_object

obj_type, data = get_object("af5626b4a114abcb82d63db7c8082c3c4756e51b")
print(f"Type: {obj_type}, Data: {data}")
```

##### `object_exists(sha: str) -> bool`

Check if an object exists in storage.

**Parameters:**
- `sha` (str): SHA-1 hash to check

**Returns:**
- `bool`: True if object exists

### `ugit.core.repository`

Repository and index management.

#### Classes

##### `Repository`

Represents a ugit repository.

**Constructor:**
```python
Repository(path: str = ".")
```

**Methods:**

###### `is_repository() -> bool`

Check if the current directory is a ugit repository.

###### `get_head_ref() -> Optional[str]`

Get the current HEAD commit SHA.

**Returns:**
- `Optional[str]`: HEAD commit SHA or None

###### `set_head_ref(sha: str, branch: str = "main") -> None`

Update the HEAD reference.

**Parameters:**
- `sha` (str): Commit SHA
- `branch` (str): Branch name

##### `Index`

Manages the staging area.

**Constructor:**
```python
Index(repo: Repository)
```

**Methods:**

###### `read() -> Dict[str, Tuple[str, float, int]]`

Read the current index.

**Returns:**
- `Dict[str, Tuple[str, float, int]]`: Mapping of file paths to (SHA, mtime, size) tuples.

###### `write(index: Dict[str, Tuple[str, float, int]]) -> None`

Write the index to disk.

## Command Modules

This section provides an overview of the main functions in the `ugit/commands/` directory. Note that many of these functions now raise specific exceptions from `ugit.core.exceptions` on failure.

### `ugit.commands.init`

#### `init() -> None`

Initialize a new ugit repository.

### `ugit.commands.add`

#### `add(paths: List[str]) -> None`

Add files to the staging area.

### `ugit.commands.commit`

#### `commit(message: str, author: Optional[str] = None) -> None`

Create a new commit. Does not return a value but prints the commit SHA to stdout.

### `ugit.commands.status`

#### `status() -> None`

Display repository status.

### `ugit.commands.log`

#### `log(max_commits: Optional[int] = None, oneline: bool = False, graph: bool = False, since: Optional[str] = None, until: Optional[str] = None) -> None`

Display commit history with various filtering and formatting options.

### `ugit.commands.checkout`

#### `checkout(target: str, create_branch: bool = False) -> None`

Checkout a specific commit or switch to a branch.

### `ugit.commands.branch`

#### `branch(name: Optional[str] = None, list_branches: bool = False, delete: Optional[str] = None) -> None`

Manage branches.

### `ugit.commands.merge`

#### `merge(branch_name: str, no_ff: bool = False) -> None`

Merge a branch into current branch.

### `ugit.commands.diff`

#### `diff(staged: bool = False, commit1: Optional[str] = None, commit2: Optional[str] = None) -> None`

Show differences between commits, staged changes, or working directory.

### `ugit.commands.reset`

#### `reset(target: Optional[str] = None, hard: bool = False, soft: bool = False) -> None`

Reset current HEAD to specified state.

### `ugit.commands.stash`

#### `stash(message: Optional[str] = None, include_untracked: bool = False) -> None`

Stash changes in working directory.

#### `stash_pop(stash_id: int = 0) -> None`

Apply and remove stash.

### `ugit.commands.clone`

#### `clone(url: str, directory: Optional[str] = None) -> None`

Clone a repository.

### `ugit.commands.remote`

#### `remote(args: Any) -> None`

Manage remote repositories.

### `ugit.commands.fetch`

#### `fetch(remote: str = "origin", branch: Optional[str] = None) -> int`

Fetch from remote repository.

### `ugit.commands.pull`

#### `pull(remote: str = "origin", branch: Optional[str] = None) -> int`

Fetch and merge from remote repository.

### `ugit.commands.push`

#### `push(remote: str = "origin", branch: Optional[str] = None, force: bool = False) -> int`

Push to remote repository.

### `ugit.commands.config`

#### `config(key: Optional[str] = None, value: Optional[str] = None, list_all: bool = False) -> int`

Manage configuration.

### `ugit.commands.serve`

#### `serve(port: int = 8000, host: str = "127.0.0.1", open_browser: bool = True) -> Optional[int]`

Start web interface server.

## Utility Modules

### `ugit.utils.helpers`

Common utility functions.

#### `ensure_repository() -> Repository`

Ensure current directory is a ugit repository.

**Returns:**
- `Repository`: Repository instance

**Raises:**
- `NotInRepositoryError`: Not in a ugit repository

#### `format_timestamp(timestamp: str) -> str`

Format ISO timestamp for display.

#### `safe_read_file(path: str) -> bytes`

Safely read file contents.

#### `walk_files(directory: str = ".", ignore_patterns: list = None) -> Iterator[str]`

Walk files in directory with ignore patterns.

### `ugit.utils.config`

Configuration management.

#### `Config`

Manages ugit configuration.

**Methods:**

##### `get(key: str, default: str = None) -> str`

Get configuration value.

##### `set(key: str, value: str) -> None`

Set configuration value.

## Data Structures

### Commit Object

Commits are stored as JSON with the following structure:

```json
{
  "tree": "sha1_hash_of_tree_object",
  "parent": "sha1_hash_of_parent_commit",
  "author": "Author Name <email@example.com>",
  "timestamp": "2025-09-19T19:30:00Z",
  "message": "Commit message"
}
```

### Tree Object

Trees are stored as a JSON list of `[path, sha]` pairs.

```json
[
  ["file1.txt", "a1b2c3d4..."],
  ["src/app.py", "e5f6g7h8..."]
]
```

### Index Format

The index file (`.ugit/index`) is a plain text file where each line represents a staged file in the format:

`sha_hash mtime size path`

**Example:**
```
a1b2c3d4... 1663612800.0 123 file1.txt
e5f6g7h8... 1663612900.0 456 src/app.py
```

## Error Handling

Commands and core functions in `ugit` raise specific exceptions on failure, all inheriting from `UgitError`.

### Custom Exceptions

- **`UgitError`**: Base class for all custom errors.
- **`NotInRepositoryError`**: Raised when a command requires a repository but is not run inside one.
- **`BranchExistsError`**: Raised when trying to create a branch that already exists.
- **`BranchNotFoundError`**: Raised when a specified branch cannot be found.
- **`MergeConflictError`**: Raised when a merge results in conflicts. The exception object contains a `.conflicts` attribute with a list of conflicting file paths.
- **`InvalidRefError`**: Raised for invalid references (e.g., a non-existent commit SHA).
- **`NonFastForwardError`**: Raised on a rejected non-fast-forward push.

### Error Handling Example

```python
from ugit.commands import branch
from ugit.core.exceptions import BranchExistsError, UgitError

try:
    branch("existing-branch-name")
except BranchExistsError as e:
    print(f"Caught expected error: {e}")
except UgitError as e:
    print(f"A ugit error occurred: {e}")
```

## Usage Examples

### Creating a Commit Programmatically

```python
from ugit.core.repository import Repository, Index
from ugit.core.objects import hash_object
from ugit.commands.commit import commit

# Ensure we're in a repository
repo = Repository()
if not repo.is_repository():
    raise RuntimeError("Not in a repository")

# Add file to index
index = Index(repo)
current_index = index.read()

# Hash file content
with open("example.txt", "rb") as f:
    content = f.read()
sha = hash_object(content, "blob", True)

# Add to index
import os
import time
stat = os.stat("example.txt")
current_index["example.txt"] = (sha, stat.st_mtime, stat.st_size)
index.write(current_index)

# Create commit
commit("Add example.txt")
```

### Reading Repository State

```python
from ugit.core.repository import Repository
from ugit.commands.status import status

repo = Repository()
if repo.is_repository():
    head = repo.get_head_ref()
    print(f"Current HEAD: {head}")
    
    # Show status
    status()
else:
    print("Not in a ugit repository")
```

## Development and Extension

### Adding New Commands

1. Create a new module in `ugit/commands/`
2. Implement the command function
3. Add the command to `ugit/cli.py`
4. Add tests in `tests/`

### Extending Object Types

Object types are extensible. To add new object types:

1. Modify `hash_object()` to handle the new type
2. Update object validation in `get_object()`
3. Add serialization/deserialization logic

### Custom Storage Backends

The object storage system can be extended to support different backends by modifying the `ugit.core.objects` module.

## See Also

- [User Guide](user-guide.md) - For user-facing documentation
- [Developer Guide](developer-guide.md) - For contribution guidelines
- [Architecture](architecture.md) - For system design overview
