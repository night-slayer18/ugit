"""
Worktree command implementation for ugit.

Manage multiple working directories for the same repository.
"""

import os
import shutil
from typing import Optional

from ..core.exceptions import BranchNotFoundError, UgitError
from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_current_branch_name
from ..utils.validation import validate_branch_name


def worktree(
    command: Optional[str] = None,
    path: Optional[str] = None,
    branch: Optional[str] = None,
    list_worktrees: bool = False,
) -> None:
    """
    Manage worktrees (multiple working directories).

    Args:
        command: Command (add, remove, list)
        path: Path for worktree
        branch: Branch to checkout in worktree
        list_worktrees: List all worktrees
    """
    repo = ensure_repository()

    if list_worktrees or command == "list":
        _list_worktrees(repo)
    elif command == "add" and path:
        _add_worktree(repo, path, branch)
    elif command == "remove" and path:
        _remove_worktree(repo, path)
    else:
        _list_worktrees(repo)


def _list_worktrees(repo: Repository) -> None:
    """List all worktrees."""
    worktrees_file = os.path.join(repo.ugit_dir, "worktrees")
    if not os.path.exists(worktrees_file):
        print("No additional worktrees")
        return

    try:
        with open(worktrees_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        print(f"{parts[0]}\t{parts[1]}")
    except (IOError, OSError):
        print("No additional worktrees")


def _add_worktree(repo: Repository, path: str, branch: Optional[str] = None) -> None:
    """Add a new worktree."""
    abs_path = os.path.abspath(path)

    if os.path.exists(abs_path):
        raise UgitError(f"Path '{path}' already exists")

    # Get branch to checkout
    if branch:
        if not validate_branch_name(branch):
            raise UgitError(f"Invalid branch name: {branch}")

        branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch)
        if not os.path.exists(branch_path):
            raise BranchNotFoundError(f"Branch '{branch}' does not exist")
    else:
        branch = get_current_branch_name(repo) or "main"

    # Create worktree directory
    os.makedirs(abs_path, exist_ok=True)

    # Create .ugit link or copy
    worktree_ugit = os.path.join(abs_path, ".ugit")
    if os.name == "nt":  # Windows
        # Copy on Windows
        shutil.copytree(repo.ugit_dir, worktree_ugit)
    else:
        # Symlink on Unix
        os.symlink(repo.ugit_dir, worktree_ugit)

    # Checkout branch in worktree
    from .checkout import checkout

    original_cwd = os.getcwd()
    try:
        os.chdir(abs_path)
        checkout(branch)
    finally:
        os.chdir(original_cwd)

    # Record worktree
    worktrees_file = os.path.join(repo.ugit_dir, "worktrees")
    with open(worktrees_file, "a", encoding="utf-8") as f:
        f.write(f"{abs_path}\t{branch}\n")

    print(f"Added worktree at {abs_path} on branch {branch}")


def _remove_worktree(repo: Repository, path: str) -> None:
    """Remove a worktree."""
    abs_path = os.path.abspath(path)

    worktrees_file = os.path.join(repo.ugit_dir, "worktrees")
    if not os.path.exists(worktrees_file):
        raise UgitError(f"Worktree '{path}' not found")

    # Read and filter worktrees
    worktrees = []
    found = False
    with open(worktrees_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("\t")
                if len(parts) >= 1 and os.path.abspath(parts[0]) != abs_path:
                    worktrees.append(line)
                else:
                    found = True

    if not found:
        raise UgitError(f"Worktree '{path}' not found")

    # Remove directory
    if os.path.exists(abs_path):
        shutil.rmtree(abs_path)

    # Update worktrees file
    with open(worktrees_file, "w", encoding="utf-8") as f:
        for wt in worktrees:
            f.write(f"{wt}\n")

    print(f"Removed worktree at {path}")
