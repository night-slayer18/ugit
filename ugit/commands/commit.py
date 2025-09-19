"""
Create commits from staged changes.
"""

import json
from datetime import datetime
from typing import Optional
from ..core.repository import Repository, Index
from ..core.objects import hash_object
from ..utils.config import Config
from ..utils.helpers import ensure_repository


def commit(message: str, author: Optional[str] = None) -> None:
    """
    Create a commit from staged changes.
    
    Args:
        message: Commit message
        author: Author information (uses config if not provided)
    """
    repo = ensure_repository()
        
    if not message.strip():
        print("Error: Commit message cannot be empty")
        return
    
    # Get author from config if not provided
    if author is None:
        config = Config(repo.path)
        author = config.get_author_string()
        
    # Create tree from current index
    tree_sha = _write_tree(repo)
    if not tree_sha:
        print("Nothing to commit")
        return
        
    # Get parent commit
    parent = repo.get_head_ref()
    
    # Create commit object
    commit_data = {
        "tree": tree_sha,
        "parent": parent,
        "author": author,
        "timestamp": datetime.now().isoformat(),
        "message": message.strip()
    }
    
    commit_bytes = json.dumps(commit_data, indent=2).encode()
    commit_sha = hash_object(commit_bytes, "commit")
    
    # Update current branch
    repo.set_head_ref(commit_sha)
    
    print(f"Committed {commit_sha[:7]} - {message}")


def _write_tree(repo: Repository) -> Optional[str]:
    """
    Create a tree object from the current index.
    
    Args:
        repo: Repository instance
        
    Returns:
        SHA of the tree object, or None if index is empty
    """
    index = Index(repo)
    index_data = index.read()
    
    if not index_data:
        return None
        
    # Convert index to tree entries (sorted for consistency)
    tree_entries = []
    for path, sha in sorted(index_data.items()):
        tree_entries.append([path, sha])  # Use list for JSON serialization
        
    tree_data = json.dumps(tree_entries, indent=2).encode()
    return hash_object(tree_data, "tree")