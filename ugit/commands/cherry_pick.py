"""
Cherry-pick command implementation for ugit.

Applies commits from other branches to the current branch.
"""

import json
import os
from typing import Dict, List, Optional

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
)
from ..utils.validation import validate_sha
from .reflog import append_reflog


def cherry_pick(commit_sha: str, no_commit: bool = False) -> None:
    """
    Apply a commit from another branch to the current branch.

    Args:
        commit_sha: SHA of commit to cherry-pick
        no_commit: Don't create a commit, just stage changes
    """
    repo = ensure_repository()

    if not validate_sha(commit_sha):
        raise UgitError(f"Invalid commit SHA: {commit_sha}")

    # Get commit to cherry-pick
    try:
        commit_data = get_commit_data(commit_sha, repo=repo)
    except ValueError as e:
        raise UgitError(f"Cannot cherry-pick {commit_sha[:7]}: {e}")

    # Get current HEAD
    current_head = repo.get_head_ref()
    if not current_head:
        raise UgitError("No current commit - cannot cherry-pick")

    # Get tree from commit to cherry-pick
    tree_sha = commit_data["tree"]

    # Apply changes from that tree to working directory
    try:
        _apply_tree_to_working_dir(repo, tree_sha)
    except MergeConflictError as e:
        raise MergeConflictError(
            f"Cherry-pick conflict: {e}", conflicts=getattr(e, "conflicts", [])
        )

    if no_commit:
        print(f"Changes from {commit_sha[:7]} staged (no commit created)")
        return

    # Create new commit with same message and author
    # Stage all changes
    from .add import add
    from .commit import commit

    add(".")

    # Create commit
    commit_message = commit_data.get("message", f"Cherry-pick {commit_sha[:7]}")
    author = commit_data.get("author")

    # Create commit manually to preserve original author
    from ..core.repository import Index as RepoIndex

    index = RepoIndex(repo)
    index_data = index.read()

    if not index_data:
        print("No changes to commit")
        return

    # Create tree from index
    tree_entries = []
    for path, (sha, _, _) in sorted(index_data.items()):
        tree_entries.append([path, sha])

    tree_data = json.dumps(tree_entries, indent=2).encode()
    new_tree_sha = hash_object(tree_data, "tree", repo=repo)

    # Create commit object
    new_commit_data = {
        "tree": new_tree_sha,
        "parent": current_head,
        "author": author,
        "timestamp": commit_data.get("timestamp"),
        "message": f"Cherry-pick {commit_sha[:7]}: {commit_message}",
    }

    commit_bytes = json.dumps(new_commit_data, indent=2).encode()
    new_commit_sha = hash_object(commit_bytes, "commit", repo=repo)

    # Update current branch
    branch_name = get_current_branch_name(repo) or "HEAD"
    repo.set_head_ref(
        new_commit_sha,
        branch_name.split("/")[-1] if "/" in branch_name else branch_name,
    )

    # Update reflog
    append_reflog(
        repo,
        branch_name,
        current_head,
        new_commit_sha,
        f"cherry-pick: {commit_sha[:7]}",
    )

    print(f"Cherry-picked {commit_sha[:7]} as {new_commit_sha[:7]}")


def _apply_tree_to_working_dir(repo: Repository, tree_sha: str) -> None:
    """Apply tree contents to working directory."""
    try:
        entries = get_tree_entries(tree_sha, repo=repo)
        for mode, path, sha in entries:
            if mode.startswith("10"):  # File
                try:
                    obj_type, content = get_object(sha, repo=repo)
                    if obj_type == "blob":
                        # Create directory if needed
                        dir_path = os.path.dirname(path)
                        if dir_path:
                            os.makedirs(dir_path, exist_ok=True)

                        # Write file
                        with open(path, "wb") as f:
                            f.write(content)
                except (FileNotFoundError, ValueError, OSError) as e:
                    raise UgitError(f"Error applying file {path}: {e}")
    except ValueError as e:
        raise UgitError(f"Error applying tree: {e}")
