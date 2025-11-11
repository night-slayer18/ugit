"""
Rebase command implementation for ugit.

Reapply commits on top of another branch.
"""

import json
import os
from typing import List, Optional

from ..core.checkout import checkout_commit
from ..core.exceptions import MergeConflictError, UgitError
from ..core.objects import get_object, hash_object
from ..core.repository import Index, Repository
from ..utils.config import Config
from ..utils.helpers import (
    ensure_repository,
    get_commit_data,
    get_current_branch_name,
    get_tree_entries,
    is_ancestor,
)
from ..utils.validation import validate_sha
from .reflog import append_reflog


def rebase(branch: str, interactive: bool = False, onto: Optional[str] = None) -> None:
    """
    Rebase current branch onto another branch.

    Args:
        branch: Branch to rebase onto
        interactive: Interactive rebase (not fully implemented)
        onto: Alternative base branch
    """
    repo = ensure_repository()

    current_branch = get_current_branch_name(repo)
    if not current_branch:
        raise UgitError("Not on a branch - cannot rebase")

    if branch == current_branch:
        raise UgitError(f"Cannot rebase branch '{branch}' onto itself")

    # Get branch commit
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch)
    if not os.path.exists(branch_path):
        raise UgitError(f"Branch '{branch}' does not exist")

    with open(branch_path, "r", encoding="utf-8") as f:
        target_commit = f.read().strip()

    # Get current branch commit
    current_commit = repo.get_head_ref()
    if not current_commit:
        raise UgitError("No commits to rebase")

    # Find common ancestor
    common_ancestor = _find_common_ancestor(repo, current_commit, target_commit)
    if not common_ancestor:
        raise UgitError("No common ancestor found")

    # Get commits to rebase (from common ancestor to current)
    commits_to_rebase = _get_commits_between(repo, common_ancestor, current_commit)
    commits_to_rebase.reverse()  # Apply oldest first

    if not commits_to_rebase:
        print("Already up to date")
        return

    # Rebase each commit
    new_base = target_commit
    for commit_sha in commits_to_rebase:
        new_base = _rebase_commit(repo, commit_sha, new_base)

    # Update branch pointer
    repo.set_head_ref(new_base, current_branch)

    # Update reflog
    append_reflog(
        repo, current_branch, current_commit, new_base, f"rebase onto {branch}"
    )

    print(f"Rebased {len(commits_to_rebase)} commit(s) onto {branch}")


def _find_common_ancestor(
    repo: Repository, commit1: str, commit2: str
) -> Optional[str]:
    """Find common ancestor of two commits."""
    ancestors1 = _get_all_ancestors(repo, commit1)
    current = commit2

    while current:
        if current in ancestors1:
            return current
        try:
            commit_data = get_commit_data(current, repo=repo)
            parent = commit_data.get("parent")
            if parent is not None:
                current = parent
            else:
                break
        except ValueError:
            break

    return None


def _get_all_ancestors(repo: Repository, commit_sha: str) -> set:
    """Get all ancestors of a commit."""
    ancestors = set()
    current = commit_sha

    while current:
        ancestors.add(current)
        try:
            commit_data = get_commit_data(current, repo=repo)
            parent = commit_data.get("parent")
            if parent is not None:
                current = parent
            else:
                break
        except ValueError:
            break

    return ancestors


def _get_commits_between(repo: Repository, ancestor: str, descendant: str) -> List[str]:
    """Get commits between ancestor and descendant."""
    commits = []
    current = descendant
    visited = set()

    while current and current != ancestor and current not in visited:
        visited.add(current)
        commits.append(current)
        try:
            commit_data = get_commit_data(current, repo=repo)
            parent = commit_data.get("parent")
            if parent is not None:
                current = parent
            else:
                break
        except ValueError:
            break

    return commits


def _rebase_commit(repo: Repository, commit_sha: str, new_base: str) -> str:
    """Rebase a single commit onto new base."""
    try:
        commit_data = get_commit_data(commit_sha, repo=repo)
        tree_sha = commit_data["tree"]

        # Apply tree to working directory
        _apply_tree(repo, tree_sha)

        # Stage changes
        from .add import add

        add(".")

        # Create new commit
        index = Index(repo)
        index_data = index.read()

        tree_entries = []
        for path, (sha, _, _) in sorted(index_data.items()):
            tree_entries.append([path, sha])

        tree_data = json.dumps(tree_entries, indent=2).encode()
        new_tree_sha = hash_object(tree_data, "tree", repo=repo)

        new_commit_data = {
            "tree": new_tree_sha,
            "parent": new_base,
            "author": commit_data.get("author"),
            "timestamp": commit_data.get("timestamp"),
            "message": commit_data.get("message"),
        }

        commit_bytes = json.dumps(new_commit_data, indent=2).encode()
        new_commit_sha = hash_object(commit_bytes, "commit", repo=repo)

        return new_commit_sha
    except Exception as e:
        raise UgitError(f"Error rebasing commit {commit_sha[:7]}: {e}")


def _apply_tree(repo: Repository, tree_sha: str) -> None:
    """Apply tree contents to working directory."""
    try:
        entries = get_tree_entries(tree_sha, repo=repo)
        for mode, path, sha in entries:
            if mode.startswith("10"):  # File
                try:
                    obj_type, content = get_object(sha, repo=repo)
                    if obj_type == "blob":
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        with open(path, "wb") as f:
                            f.write(content)
                except (FileNotFoundError, ValueError, OSError):
                    pass
    except ValueError:
        pass
