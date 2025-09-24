"""
Branch command implementation for ugit.

This module handles branch creation, listing, switching, and deletion.
"""

import os
from typing import Optional

from ..core.repository import Repository
from ..utils.helpers import ensure_repository


def branch(branch_name: str = None, list_branches: bool = False, delete: str = None, 
          create: bool = False) -> None:
    """
    Handle branch operations.
    
    Args:
        branch_name: Name of branch to create or switch to
        list_branches: List all branches
        delete: Branch name to delete
        create: Create new branch
    """
    repo = ensure_repository()
    
    if list_branches:
        _list_branches(repo)
    elif delete:
        _delete_branch(repo, delete)
    elif create and branch_name:
        _create_branch(repo, branch_name)
    elif branch_name:
        _create_branch(repo, branch_name)
    else:
        _list_branches(repo)


def checkout_branch(branch_name: str, create: bool = False) -> None:
    """
    Switch to a branch, optionally creating it.
    
    Args:
        branch_name: Name of branch to switch to
        create: Create branch if it doesn't exist
    """
    repo = ensure_repository()
    
    if create:
        _create_branch(repo, branch_name)
    
    _switch_to_branch(repo, branch_name)


def _list_branches(repo: Repository) -> None:
    """List all branches."""
    refs_dir = os.path.join(repo.ugit_dir, "refs", "heads")
    current_branch = _get_current_branch(repo)
    
    if not os.path.exists(refs_dir):
        print("No branches yet")
        return
    
    branches = []
    for branch_file in os.listdir(refs_dir):
        if os.path.isfile(os.path.join(refs_dir, branch_file)):
            branches.append(branch_file)
    
    if not branches:
        print("No branches yet")
        return
    
    for branch in sorted(branches):
        marker = "* " if branch == current_branch else "  "
        print(f"{marker}{branch}")


def _create_branch(repo: Repository, branch_name: str) -> None:
    """Create a new branch."""
    if not _is_valid_branch_name(branch_name):
        print(f"Invalid branch name: {branch_name}")
        return
    
    # Check if branch already exists
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch_name)
    if os.path.exists(branch_path):
        print(f"Branch '{branch_name}' already exists")
        return
    
    # Get current HEAD commit
    current_commit = repo.get_head_ref()
    if not current_commit:
        print("No commits yet - cannot create branch")
        return
    
    # Create refs/heads directory if it doesn't exist
    refs_heads_dir = os.path.join(repo.ugit_dir, "refs", "heads")
    os.makedirs(refs_heads_dir, exist_ok=True)
    
    # Create branch file pointing to current commit
    with open(branch_path, "w", encoding="utf-8") as f:
        f.write(current_commit)
    
    print(f"Created branch '{branch_name}'")


def _switch_to_branch(repo: Repository, branch_name: str) -> None:
    """Switch to an existing branch."""
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch_name)
    
    if not os.path.exists(branch_path):
        print(f"Branch '{branch_name}' does not exist")
        return
    
    # Update HEAD to point to the branch
    head_path = os.path.join(repo.ugit_dir, "HEAD")
    with open(head_path, "w", encoding="utf-8") as f:
        f.write(f"ref: refs/heads/{branch_name}")
    
    # Get the commit that the branch points to
    with open(branch_path, "r", encoding="utf-8") as f:
        commit_sha = f.read().strip()
    
    # Checkout the commit (update working directory)
    from .checkout import checkout
    checkout(commit_sha)
    
    print(f"Switched to branch '{branch_name}'")


def _delete_branch(repo: Repository, branch_name: str) -> None:
    """Delete a branch."""
    current_branch = _get_current_branch(repo)
    
    if branch_name == current_branch:
        print(f"Cannot delete current branch '{branch_name}'")
        return
    
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch_name)
    
    if not os.path.exists(branch_path):
        print(f"Branch '{branch_name}' does not exist")
        return
    
    os.remove(branch_path)
    print(f"Deleted branch '{branch_name}'")


def _get_current_branch(repo: Repository) -> Optional[str]:
    """Get the name of the current branch."""
    head_path = os.path.join(repo.ugit_dir, "HEAD")
    
    if not os.path.exists(head_path):
        return None
    
    try:
        with open(head_path, "r", encoding="utf-8") as f:
            head_content = f.read().strip()
        
        if head_content.startswith("ref: refs/heads/"):
            return head_content[16:]  # Remove "ref: refs/heads/" prefix
        
        return None  # Detached HEAD
    except (IOError, OSError):
        return None


def _is_valid_branch_name(name: str) -> bool:
    """Check if branch name is valid."""
    if not name or name.strip() != name:
        return False
    
    # Basic validation - no spaces, no special characters that cause issues
    invalid_chars = [" ", "\t", "\n", "..", "~", "^", ":", "?", "*", "[", "\\"]
    for char in invalid_chars:
        if char in name:
            return False
    
    # Cannot start with . or -
    if name.startswith(".") or name.startswith("-"):
        return False
    
    return True


def get_current_branch_name(repo: Repository = None) -> Optional[str]:
    """Get current branch name (utility function for other modules)."""
    if repo is None:
        repo = Repository()
        if not repo.is_repository():
            return None
    
    return _get_current_branch(repo)