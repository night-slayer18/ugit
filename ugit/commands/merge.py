"""
Merge command implementation for ugit.

This module handles merging branches.
"""

import json
import os
from typing import Dict, Optional, Set

from ..core.objects import get_object, hash_object
from ..core.repository import Repository
from ..utils.helpers import ensure_repository


def merge(branch_name: str, no_ff: bool = False) -> None:
    """
    Merge a branch into the current branch.

    Args:
        branch_name: Name of branch to merge
        no_ff: Force a merge commit even for fast-forward merges
    """
    repo = ensure_repository()

    # Get current branch
    current_branch = _get_current_branch(repo)
    if not current_branch:
        print("Not on any branch - cannot merge")
        return

    if branch_name == current_branch:
        print(f"Cannot merge branch '{branch_name}' into itself")
        return

    # Check if target branch exists
    branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch_name)
    if not os.path.exists(branch_path):
        print(f"Branch '{branch_name}' does not exist")
        return

    # Get commit SHAs
    with open(branch_path, "r", encoding="utf-8") as f:
        merge_commit = f.read().strip()

    current_commit = repo.get_head_ref()
    if not current_commit:
        print("No current commit to merge into")
        return

    # Check if it's a fast-forward merge
    if _is_ancestor(repo, current_commit, merge_commit):
        if no_ff:
            _create_merge_commit(repo, current_commit, merge_commit, branch_name)
        else:
            _fast_forward_merge(repo, merge_commit, branch_name)
    else:
        # Need to create a merge commit
        _three_way_merge(repo, current_commit, merge_commit, branch_name)


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


def _is_ancestor(repo: Repository, ancestor_sha: str, descendant_sha: str) -> bool:
    """Check if ancestor_sha is an ancestor of descendant_sha."""
    current = descendant_sha

    while current:
        if current == ancestor_sha:
            return True

        try:
            commit_type, commit_data = get_object(current)
            if commit_type != "commit":
                break

            commit = json.loads(commit_data.decode())
            current = commit.get("parent")
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            break

    return False


def _fast_forward_merge(repo: Repository, target_commit: str, branch_name: str) -> None:
    """Perform a fast-forward merge."""
    # Update current branch to point to target commit
    current_branch = _get_current_branch(repo)
    if current_branch is None:
        print("Error: Not on a branch (detached HEAD)")
        return
    current_branch_path = os.path.join(repo.ugit_dir, "refs", "heads", current_branch)

    with open(current_branch_path, "w", encoding="utf-8") as f:
        f.write(target_commit)

    # Checkout the target commit
    from .checkout import _checkout_commit

    _checkout_commit(repo, target_commit)

    print(f"Fast-forward merge of '{branch_name}' into '{current_branch}'")
    print(f"Updated {current_branch} to {target_commit[:7]}")


def _create_merge_commit(
    repo: Repository, parent1: str, parent2: str, branch_name: str
) -> None:
    """Create a merge commit with two parents."""
    current_branch = _get_current_branch(repo)
    if current_branch is None:
        print("Error: Not on a branch (detached HEAD)")
        return

    # Create merge commit
    import time

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    commit_data = {
        "tree": _get_commit_tree(repo, parent2),  # Use the merged branch's tree
        "parent": parent1,
        "parent2": parent2,  # Second parent for merge
        "author": "Merge Author <merge@ugit.com>",  # TODO: Get from config
        "timestamp": timestamp,
        "message": f"Merge branch '{branch_name}' into {current_branch}",
    }

    commit_json = json.dumps(commit_data, separators=(",", ":")).encode()
    commit_sha = hash_object(commit_json, "commit")

    # Update current branch
    current_branch_path = os.path.join(repo.ugit_dir, "refs", "heads", current_branch)
    with open(current_branch_path, "w", encoding="utf-8") as f:
        f.write(commit_sha)

    # Checkout the merged files
    from .checkout import _checkout_commit

    _checkout_commit(repo, parent2, update_head=False)

    print(f"Merge commit created: {commit_sha[:7]}")


def _three_way_merge(
    repo: Repository, current_commit: str, merge_commit: str, branch_name: str
) -> None:
    """Perform a three-way merge."""
    # Find common ancestor
    common_ancestor = _find_common_ancestor(repo, current_commit, merge_commit)

    if not common_ancestor:
        print("No common ancestor found - cannot merge")
        return

    # Get file trees for three-way merge
    try:
        ancestor_files = _get_commit_files(repo, common_ancestor)
        current_files = _get_commit_files(repo, current_commit)
        merge_files = _get_commit_files(repo, merge_commit)
    except ValueError as e:
        print(f"Error during merge: {e}")
        return

    # Perform merge
    merged_files, conflicts = _merge_files(ancestor_files, current_files, merge_files)

    # Always write merged files to working directory (including conflict markers)
    _write_merged_files(merged_files)

    if conflicts:
        print("Merge conflicts detected in:")
        for file_path in conflicts:
            print(f"  {file_path}")
        print("Please resolve conflicts and commit manually")
        return

    # Create merge commit only if no conflicts
    merged_tree_sha = _create_tree_from_files(merged_files)
    _create_merge_commit_with_tree(
        repo, current_commit, merge_commit, branch_name, merged_tree_sha
    )


def _find_common_ancestor(
    repo: Repository, commit1: str, commit2: str
) -> Optional[str]:
    """Find the common ancestor of two commits."""
    # Get all ancestors of commit1
    ancestors1 = _get_all_ancestors(repo, commit1)

    # Walk through ancestors of commit2 until we find one that's also in ancestors1
    current = commit2
    while current:
        if current in ancestors1:
            return current

        try:
            commit_type, commit_data = get_object(current)
            if commit_type != "commit":
                break

            commit = json.loads(commit_data.decode())
            current = commit.get("parent")
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            break

    return None


def _get_all_ancestors(repo: Repository, commit_sha: str) -> Set[str]:
    """Get all ancestors of a commit."""
    ancestors = set()
    current = commit_sha

    while current:
        ancestors.add(current)

        try:
            commit_type, commit_data = get_object(current)
            if commit_type != "commit":
                break

            commit = json.loads(commit_data.decode())
            current = commit.get("parent")
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            break

    return ancestors


def _get_commit_files(repo: Repository, commit_sha: str) -> Dict[str, str]:
    """Get all files from a commit."""
    try:
        commit_type, commit_data = get_object(commit_sha)
        if commit_type != "commit":
            raise ValueError(f"Object {commit_sha} is not a commit")

        commit = json.loads(commit_data.decode())
        tree_sha = commit["tree"]

        # For simplicity, assume tree is a dict of path->sha
        tree_type, tree_data = get_object(tree_sha)
        if tree_type != "tree":
            raise ValueError(f"Object {tree_sha} is not a tree")

        tree = json.loads(tree_data.decode())
        files = {}

        # Tree is a list of [path, sha] pairs
        for entry in tree:
            if isinstance(entry, list) and len(entry) == 2:
                path, sha = entry
                try:
                    obj_type, content = get_object(sha)
                    if obj_type == "blob":
                        files[path] = content.decode("utf-8", errors="replace")
                except (FileNotFoundError, UnicodeDecodeError):
                    files[path] = ""

        return files

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid commit {commit_sha}: {e}")


def _merge_files(
    ancestor_files: Dict[str, str],
    current_files: Dict[str, str],
    merge_files: Dict[str, str],
) -> tuple:
    """Perform three-way merge on file contents."""
    all_files = (
        set(ancestor_files.keys()) | set(current_files.keys()) | set(merge_files.keys())
    )
    merged_files = {}
    conflicts = []

    for file_path in all_files:
        ancestor_content = ancestor_files.get(file_path, "")
        current_content = current_files.get(file_path, "")
        merge_content = merge_files.get(file_path, "")

        if current_content == merge_content:
            # No conflict - both sides have same content
            merged_files[file_path] = current_content
        elif ancestor_content == current_content:
            # Current side unchanged, use merge side
            merged_files[file_path] = merge_content
        elif ancestor_content == merge_content:
            # Merge side unchanged, use current side
            merged_files[file_path] = current_content
        else:
            # Both sides changed - conflict
            conflicts.append(file_path)
            merged_files[file_path] = _create_conflict_marker(
                file_path, current_content, merge_content
            )

    return merged_files, conflicts


def _create_conflict_marker(
    file_path: str, current_content: str, merge_content: str
) -> str:
    """Create conflict markers in file content."""
    return f"""<<<<<<< HEAD
{current_content}=======
{merge_content}>>>>>>> feature
"""


def _write_merged_files(merged_files: Dict[str, str]) -> None:
    """Write merged files to working directory."""
    for file_path, content in merged_files.items():
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


def _create_tree_from_files(files: Dict[str, str]) -> str:
    """Create a tree object from files."""
    tree_data = {}

    for file_path, content in files.items():
        blob_sha = hash_object(content.encode(), "blob")
        tree_data[file_path] = blob_sha

    tree_json = json.dumps(tree_data, separators=(",", ":")).encode()
    return hash_object(tree_json, "tree")


def _create_merge_commit_with_tree(
    repo: Repository, parent1: str, parent2: str, branch_name: str, tree_sha: str
) -> None:
    """Create merge commit with specific tree."""
    current_branch = _get_current_branch(repo)
    if current_branch is None:
        print("Error: Not on a branch (detached HEAD)")
        return

    import time

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    commit_data = {
        "tree": tree_sha,
        "parent": parent1,
        "parent2": parent2,
        "author": "Merge Author <merge@ugit.com>",
        "timestamp": timestamp,
        "message": f"Merge branch '{branch_name}' into {current_branch}",
    }

    commit_json = json.dumps(commit_data, separators=(",", ":")).encode()
    commit_sha = hash_object(commit_json, "commit")

    # Update current branch
    current_branch_path = os.path.join(repo.ugit_dir, "refs", "heads", current_branch)
    with open(current_branch_path, "w", encoding="utf-8") as f:
        f.write(commit_sha)

    print(f"Merge completed: {commit_sha[:7]}")


def _get_commit_tree(repo: Repository, commit_sha: str) -> str:
    """Get tree SHA from commit."""
    try:
        commit_type, commit_data = get_object(commit_sha)
        if commit_type != "commit":
            raise ValueError(f"Not a commit: {commit_sha}")

        commit = json.loads(commit_data.decode())
        tree_sha: str = commit["tree"]
        return tree_sha

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid commit {commit_sha}: {e}")
