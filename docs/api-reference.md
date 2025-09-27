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

###### `read() -> Dict[str, str]`

Read the current index.

**Returns:**
- `Dict[str, str]`: Mapping of file paths to SHA hashes

###### `write(index: Dict[str, str]) -> None`

Write the index to disk.

###### `add_file(path: str, sha: str) -> None`

Add a file to the index.

###### `remove_file(path: str) -> None`

Remove a file from the index.

## Command Modules

### `ugit.commands.init`

#### `init() -> None`

Initialize a new ugit repository.

Creates the `.ugit` directory structure:
```
.ugit/
├── objects/
├── refs/
│   └── heads/
└── index
```

### `ugit.commands.add`

#### `add(paths: List[str]) -> None`

Add files to the staging area.

**Parameters:**
- `paths` (List[str]): File paths to add

### `ugit.commands.commit`

#### `commit(message: str, author: str = None) -> str`

Create a new commit.

**Parameters:**
- `message` (str): Commit message
- `author` (str): Author information (optional)

**Returns:**
- `str`: SHA of the new commit

### `ugit.commands.status`

#### `status() -> None`

Display repository status.

Shows:
- Staged files
- Modified files
- Untracked files
- Deleted files

### `ugit.commands.log`

#### `log(max_commits: Optional[int] = None) -> None`

Display commit history.

**Parameters:**
- `max_commits` (Optional[int]): Maximum commits to show

### `ugit.commands.checkout`

#### `checkout(commit_sha: str) -> None`

Checkout a specific commit.

**Parameters:**
- `commit_sha` (str): SHA of commit to checkout

### `ugit.commands.branch`

#### `branch(name: Optional[str] = None, list_branches: bool = False, delete: Optional[str] = None) -> None`

Manage branches.

**Parameters:**
- `name` (Optional[str]): Branch name to create
- `list_branches` (bool): List all branches
- `delete` (Optional[str]): Branch name to delete

### `ugit.commands.merge`

#### `merge(branch_name: str, no_ff: bool = False) -> None`

Merge a branch into current branch.

**Parameters:**
- `branch_name` (str): Name of branch to merge
- `no_ff` (bool): Force creation of merge commit

### `ugit.commands.diff`

#### `diff(staged: bool = False, commit1: Optional[str] = None, commit2: Optional[str] = None) -> None`

Show differences between commits, staged changes, or working directory.

**Parameters:**
- `staged` (bool): Show staged changes vs last commit
- `commit1` (Optional[str]): First commit to compare
- `commit2` (Optional[str]): Second commit to compare

### `ugit.commands.reset`

#### `reset(target: Optional[str] = None, hard: bool = False, soft: bool = False) -> None`

Reset current HEAD to specified state.

**Parameters:**
- `target` (Optional[str]): Commit to reset to
- `hard` (bool): Reset working directory and index
- `soft` (bool): Reset only HEAD (keep changes)

### `ugit.commands.stash`

#### `stash(message: Optional[str] = None, include_untracked: bool = False) -> None`

Stash changes in working directory.

**Parameters:**
- `message` (Optional[str]): Stash message
- `include_untracked` (bool): Include untracked files

#### `stash_pop(stash_id: int = 0) -> None`

Apply and remove stash.

**Parameters:**
- `stash_id` (int): Index of stash to pop

#### `stash_list() -> None`

List all stashes.

#### `stash_apply(stash_id: int = 0) -> None`

Apply stash without removing it.

**Parameters:**
- `stash_id` (int): Index of stash to apply

#### `stash_drop(stash_id: int = 0) -> None`

Remove stash without applying.

**Parameters:**
- `stash_id` (int): Index of stash to drop

### `ugit.commands.clone`

#### `clone(url: str, directory: Optional[str] = None) -> None`

Clone a repository.

**Parameters:**
- `url` (str): Repository URL to clone
- `directory` (Optional[str]): Local directory name

### `ugit.commands.remote`

#### `remote(args: Any) -> None`

Manage remote repositories.

**Parameters:**
- `args` (Any): Parsed command arguments with subcommands (add, remove, show, list)

### `ugit.commands.fetch`

#### `fetch(remote: str = "origin", branch: Optional[str] = None) -> None`

Fetch from remote repository.

**Parameters:**
- `remote` (str): Remote name
- `branch` (Optional[str]): Branch to fetch

### `ugit.commands.pull`

#### `pull(remote: str = "origin", branch: Optional[str] = None) -> None`

Fetch and merge from remote repository.

**Parameters:**
- `remote` (str): Remote name
- `branch` (Optional[str]): Branch to pull

### `ugit.commands.push`

#### `push(remote: str = "origin", branch: Optional[str] = None, force: bool = False) -> None`

Push to remote repository.

**Parameters:**
- `remote` (str): Remote name
- `branch` (Optional[str]): Branch to push
- `force` (bool): Force push

### `ugit.commands.config`

#### `config(key: Optional[str] = None, value: Optional[str] = None, list_all: bool = False) -> None`

Manage configuration.

**Parameters:**
- `key` (Optional[str]): Configuration key
- `value` (Optional[str]): Configuration value
- `list_all` (bool): List all configuration

### `ugit.commands.serve`

#### `serve(port: int = 8000, host: str = "127.0.0.1", open_browser: bool = True) -> Optional[int]`

Start web interface server.

**Parameters:**
- `port` (int): Port to run server on
- `host` (str): Host to bind to
- `open_browser` (bool): Open browser automatically

**Returns:**
- `Optional[int]`: Exit code (0 for success)

## Utility Modules

### `ugit.utils.helpers`

Common utility functions.

#### `ensure_repository() -> Repository`

Ensure current directory is a ugit repository.

**Returns:**
- `Repository`: Repository instance

**Raises:**
- `RuntimeError`: Not in a ugit repository

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

Trees represent directory structures:

```json
{
  "entries": [
    {
      "name": "filename.txt",
      "sha": "sha1_hash_of_blob",
      "type": "blob"
    }
  ]
}
```

### Index Format

The index file contains staged files:

```
filename1.txt sha1_hash
filename2.py sha1_hash
directory/file.md sha1_hash
```

## Error Handling

### Common Exceptions

#### `RuntimeError`

Raised when:
- Not in a ugit repository
- Repository operations fail

#### `FileNotFoundError`

Raised when:
- Object doesn't exist
- Repository files missing

#### `ValueError`

Raised when:
- Invalid SHA format
- Malformed object data
- Invalid commit data

### Error Handling Example

```python
from ugit.utils.helpers import ensure_repository
from ugit.core.objects import get_object

try:
    repo = ensure_repository()
    obj_type, data = get_object("invalid_sha")
except RuntimeError as e:
    print(f"Repository error: {e}")
except ValueError as e:
    print(f"Invalid data: {e}")
except FileNotFoundError as e:
    print(f"Object not found: {e}")
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
current_index["example.txt"] = sha
index.write(current_index)

# Create commit
commit_sha = commit("Add example.txt")
print(f"Created commit: {commit_sha}")
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