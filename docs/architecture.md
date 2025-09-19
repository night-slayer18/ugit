# Architecture Overview

This document provides a high-level overview of ugit's architecture and design decisions.

## Table of Contents

- [Design Philosophy](#design-philosophy)
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Storage Format](#storage-format)
- [Design Patterns](#design-patterns)
- [Security Considerations](#security-considerations)

## Design Philosophy

### Goals

- **Simplicity**: Keep the codebase minimal and understandable
- **Educational**: Code should be readable and well-documented
- **Functional**: Core Git features should work correctly
- **Extensible**: Easy to add new features without breaking existing functionality

### Non-Goals

- **Complete Git compatibility**: ugit implements core features, not every Git command
- **Performance optimization**: Focus on correctness over speed
- **Complex workflows**: Advanced Git features (merge, rebase, etc.) are out of scope

### Design Principles

1. **Explicit over implicit**: Clear, readable code over clever shortcuts
2. **Fail fast**: Early validation and clear error messages
3. **Modular design**: Separate concerns into distinct modules
4. **Immutable objects**: Object storage is append-only and immutable

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │    cli.py   │  │  commands/  │  │   utils/    │          │
│  │             │  │   modules   │  │  helpers    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Core Layer                            │
│  ┌─────────────┐                    ┌─────────────┐         │
│  │ repository  │◄──────────────────►│   objects   │         │
│  │   .py       │                    │    .py      │         │
│  │             │                    │             │         │
│  │ • Repository│                    │ • hash_obj  │         │
│  │ • Index     │                    │ • get_obj   │         │
│  │ • refs      │                    │ • storage   │         │
│  └─────────────┘                    └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Storage Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   .ugit/    │  │   objects/  │  │    refs/    │          │
│  │   index     │  │  (blobs,    │  │   heads/    │          │
│  │             │  │ trees,      │  │    main     │          │
│  │             │  │ commits)    │  │             │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. CLI Layer (`ugit/cli.py`)

**Responsibility**: Command-line interface and argument parsing

**Key Functions**:
- Parse command-line arguments
- Route commands to appropriate handlers
- Handle global options and help
- Error handling and user feedback

### 2. Command Layer (`ugit/commands/`)

**Responsibility**: Implementation of individual ugit commands

**Modules**:
- `init.py`: Repository initialization
- `add.py`: File staging
- `commit.py`: Commit creation
- `status.py`: Working directory status
- `log.py`: Commit history
- `checkout.py`: Working directory restoration

**Common Pattern**:
```python
def command_name(args):
    repo = ensure_repository()  # Validate repository
    # Command-specific logic
    # Update repository state
```

### 3. Core Layer (`ugit/core/`)

#### Repository Management (`repository.py`)

**Classes**:
- `Repository`: Manages repository state and operations
- `Index`: Handles staging area operations

**Key Responsibilities**:
- Repository detection and validation
- HEAD reference management
- Index (staging area) operations
- Branch reference handling

#### Object Storage (`objects.py`)

**Key Functions**:
- `hash_object()`: Content hashing and storage
- `get_object()`: Object retrieval
- `object_exists()`: Existence checking

**Object Types**:
- **Blob**: File content
- **Tree**: Directory structure
- **Commit**: Commit metadata and references

### 4. Utility Layer (`ugit/utils/`)

**Modules**:
- `helpers.py`: Common utility functions
- `config.py`: Configuration management

**Key Functions**:
- Repository validation
- File operations
- Data formatting
- Error handling

## Data Flow

### Typical Command Flow

```
User Command
     │
     ▼
CLI Parsing (cli.py)
     │
     ▼
Command Router
     │
     ▼
Command Implementation
     │
     ▼
Repository Validation
     │
     ▼
Core Operations
     │
     ▼
Object Storage/Retrieval
     │
     ▼
File System Updates
     │
     ▼
User Feedback
```

### Example: `ugit add file.txt`

1. **CLI**: Parse command and filename
2. **add.py**: Validate repository and file
3. **helpers.py**: Read file content safely
4. **objects.py**: Hash content and store as blob
5. **repository.py**: Update index with file->SHA mapping
6. **CLI**: Display success message

### Example: `ugit commit -m "message"`

1. **CLI**: Parse command and message
2. **commit.py**: Validate repository and staging area
3. **repository.py**: Read current index
4. **objects.py**: Create tree object from index
5. **objects.py**: Create commit object
6. **repository.py**: Update HEAD reference
7. **CLI**: Display commit SHA

## Storage Format

### Repository Structure

```
.ugit/
├── objects/              # Object storage
│   ├── ab/              # First 2 chars of SHA
│   │   └── cdef123...   # Remaining 38 chars (compressed object)
│   └── ...
├── refs/                # Reference storage
│   └── heads/           # Branch references
│       └── main         # Contains SHA of latest commit
└── index               # Staging area (plain text)
```

### Object Storage Details

**File Path**: `.ugit/objects/{first2chars}/{remaining38chars}`

**Storage Format**: 
1. Object type + null byte + content
2. Compressed with zlib
3. Written to file named by SHA-1 hash

**Example**:
```
Content: "Hello, world!"
Type: "blob"
Raw: "blob\x00Hello, world!"
SHA: "af5626b4a114abcb82d63db7c8082c3c4756e51b"
Path: ".ugit/objects/af/5626b4a114abcb82d63db7c8082c3c4756e51b"
```

### Object Types

#### Blob Object
```
Type: "blob"
Content: Raw file content (bytes)
```

#### Tree Object
```
Type: "tree"
Content: JSON structure
{
  "entries": [
    {
      "name": "filename.txt",
      "sha": "blob_sha_hash",
      "type": "blob"
    }
  ]
}
```

#### Commit Object
```
Type: "commit"
Content: JSON structure
{
  "tree": "tree_object_sha",
  "parent": "parent_commit_sha",  // null for first commit
  "author": "Author Name <email@example.com>",
  "timestamp": "2025-09-19T19:30:00Z",
  "message": "Commit message"
}
```

### Index Format

Plain text file with format:
```
filename1.txt sha1_hash_of_blob
filename2.py sha1_hash_of_blob
directory/file.md sha1_hash_of_blob
```

## Design Patterns

### 1. Command Pattern

Each ugit command is implemented as a separate module with a main function:

```python
def command_name(args):
    """Command implementation."""
    pass
```

### 2. Repository Pattern

The `Repository` class encapsulates all repository operations:

```python
repo = Repository()
if repo.is_repository():
    head = repo.get_head_ref()
```

### 3. Content-Addressable Storage

Objects are stored by their content hash:
- Automatic deduplication
- Immutable storage
- Integrity verification

### 4. Separation of Concerns

- **CLI**: User interface
- **Commands**: Business logic
- **Core**: Data operations
- **Utils**: Common functionality

### 5. Fail-Fast Validation

Early validation prevents corruption:

```python
def ensure_repository():
    if not Repository().is_repository():
        raise RuntimeError("Not in a ugit repository")
    return Repository()
```

## Security Considerations

### Path Traversal Prevention

- All file paths are validated
- Relative paths are resolved safely
- Directory traversal attacks prevented

### Input Validation

- SHA hashes validated for correct format
- File paths sanitized
- JSON parsing with error handling

### Data Integrity

- SHA-1 hashing ensures content integrity
- Immutable object storage
- Atomic operations where possible

### Limitations

- No authentication or authorization
- Local file system only
- No encryption of stored data
- SHA-1 collision vulnerability (theoretical)

## Performance Characteristics

### Time Complexity

- Object storage: O(1) lookup by SHA
- Index operations: O(n) where n = number of files
- Log traversal: O(m) where m = number of commits

### Space Complexity

- Object storage: O(total content size)
- Index: O(number of tracked files)
- References: O(number of branches)

### Optimization Opportunities

1. **Delta compression**: Store diffs instead of full objects
2. **Pack files**: Combine small objects
3. **Index caching**: Cache index in memory
4. **Parallel operations**: Concurrent file processing

## Extensibility Points

### Adding New Commands

1. Create module in `ugit/commands/`
2. Add to CLI router in `cli.py`
3. Follow existing patterns

### New Object Types

1. Extend `hash_object()` function
2. Update type validation
3. Add serialization logic

### Alternative Storage

1. Abstract storage interface
2. Plugin architecture
3. Configuration options

## Future Architecture Considerations

### Scalability

- Large repository handling
- Network operations
- Concurrent access

### Compatibility

- Git interoperability
- Migration tools
- Import/export features

### User Experience

- Better error messages
- Progress indicators
- Interactive commands

This architecture provides a solid foundation for a minimal but functional version control system while maintaining simplicity and educational value.