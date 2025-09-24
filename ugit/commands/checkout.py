"""
Checkout files from a specific commit or switch to a branch.
"""

import json
import os
import shutil
from typing import Dict, List, Tuple

from ..core.objects import get_object
from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_commit_data


def checkout(target: str, create_branch: bool = False) -> None:
    """
    Checkout files from a specific commit or switch to a branch.

    Args:
        target: Commit SHA or branch name to checkout
        create_branch: Create new branch if target is a branch name
    """
    repo = ensure_repository()

    # Check if target is a branch name
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", target)
    
    if os.path.exists(branch_path):
        # It's a branch - switch to it
        _switch_to_branch(repo, target)
    elif create_branch:
        # Create new branch and switch to it
        _create_and_switch_branch(repo, target)
    else:
        # Assume it's a commit SHA
        _checkout_commit(repo, target)


def _switch_to_branch(repo: Repository, branch_name: str) -> None:
    """Switch to an existing branch."""
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch_name)
    
    # Get the commit that the branch points to
    with open(branch_path, "r", encoding="utf-8") as f:
        commit_sha = f.read().strip()
    
    # Update HEAD to point to the branch
    head_path = os.path.join(repo.ugit_dir, "HEAD")
    with open(head_path, "w", encoding="utf-8") as f:
        f.write(f"ref: refs/heads/{branch_name}")
    
    # Checkout the commit
    _checkout_commit(repo, commit_sha)
    print(f"Switched to branch '{branch_name}'")


def _create_and_switch_branch(repo: Repository, branch_name: str) -> None:
    """Create a new branch and switch to it."""
    # Get current HEAD commit
    current_commit = repo.get_head_ref()
    if not current_commit:
        print("No commits yet - cannot create branch")
        return
    
    # Create refs/heads directory if it doesn't exist
    refs_heads_dir = os.path.join(repo.ugit_dir, "refs", "heads")
    os.makedirs(refs_heads_dir, exist_ok=True)
    
    # Create branch file pointing to current commit
    branch_path = os.path.join(refs_heads_dir, branch_name)
    with open(branch_path, "w", encoding="utf-8") as f:
        f.write(current_commit)
    
    # Switch to the new branch
    _switch_to_branch(repo, branch_name)
    print(f"Created and switched to branch '{branch_name}'")


def _checkout_commit(repo: Repository, commit_sha: str) -> None:
    """Checkout files from a specific commit."""
    try:
        # Get commit data using helper function
        commit = get_commit_data(commit_sha)
        tree_sha = commit["tree"]

        # Get tree object
        type_, tree_data = get_object(tree_sha)
        if type_ != "tree":
            print(f"Error: Invalid tree object in commit")
            return

        tree = json.loads(tree_data.decode())

        # Clear existing files (except .ugit and main files)
        _clear_working_directory()

        # Write files from the tree
        for path, sha in tree.items():
            _restore_file(path, sha)

        # Update HEAD to point directly to commit (detached HEAD)
        head_path = os.path.join(repo.ugit_dir, "HEAD")
        with open(head_path, "w", encoding="utf-8") as f:
            f.write(commit_sha)

        print(f"Checked out commit {commit_sha[:7]}")

    except ValueError as e:
        print(f"Error checking out commit {commit_sha}: {e}")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error checking out commit {commit_sha}: {e}")


def _clear_working_directory() -> None:
    """Clear working directory of tracked files."""
    for root, dirs, files in os.walk(".", topdown=False):
        # Skip .ugit directory
        if ".ugit" in dirs:
            dirs.remove(".ugit")

        for file in files:
            path = os.path.relpath(os.path.join(root, file))
            # Keep ugit-related files
            if not (path.startswith(".ugit") or path.endswith("ugit.py")):
                try:
                    os.remove(path)
                except OSError:
                    pass  # File might be read-only or in use

        # Remove empty directories
        for dir in dirs:
            dir_path = os.path.relpath(os.path.join(root, dir))
            if not dir_path.startswith(".ugit"):
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                except OSError:
                    pass


def _restore_file(path: str, sha: str) -> None:
    """Restore a single file from object storage."""
    try:
        # Create directory if needed
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        # Get file content and write to disk
        type_, content = get_object(sha)
        if type_ != "blob":
            print(f"Warning: Expected blob for {path}, got {type_}")
            return

        with open(path, "wb") as f:
            f.write(content)

    except (FileNotFoundError, OSError) as e:
        print(f"Error restoring {path}: {e}")
