"""
Fsck (file system check) command implementation for ugit.

Verify repository integrity and detect corruption.
"""

import json
import os
import zlib
from typing import List

from ..core.objects import get_object, object_exists
from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_commit_data, get_tree_entries
from ..utils.validation import validate_sha


def fsck(full: bool = False) -> int:
    """
    Check repository integrity.

    Args:
        full: Perform full check (verify all objects)

    Returns:
        Number of errors found
    """
    repo = ensure_repository()
    errors = []

    # Check HEAD
    head_sha = repo.get_head_ref()
    if head_sha and not validate_sha(head_sha):
        errors.append(f"Invalid HEAD SHA: {head_sha}")

    # Check branches
    heads_dir = os.path.join(repo.ugit_dir, "refs", "heads")
    if os.path.exists(heads_dir):
        for branch_file in os.listdir(heads_dir):
            branch_path = os.path.join(heads_dir, branch_file)
            try:
                with open(branch_path, "r") as f:
                    sha = f.read().strip()
                    if not validate_sha(sha):
                        errors.append(f"Invalid SHA in branch {branch_file}: {sha}")
                    elif not object_exists(sha, repo=repo):
                        errors.append(
                            f"Branch {branch_file} points to non-existent commit: {sha}"
                        )
            except (IOError, OSError) as e:
                errors.append(f"Error reading branch {branch_file}: {e}")

    # Check tags
    tags_dir = os.path.join(repo.ugit_dir, "refs", "tags")
    if os.path.exists(tags_dir):
        for tag_file in os.listdir(tags_dir):
            tag_path = os.path.join(tags_dir, tag_file)
            try:
                with open(tag_path, "r") as f:
                    sha = f.read().strip()
                    if not validate_sha(sha):
                        errors.append(f"Invalid SHA in tag {tag_file}: {sha}")
            except (IOError, OSError) as e:
                errors.append(f"Error reading tag {tag_file}: {e}")

    # Check objects if full check
    if full:
        objects_dir = os.path.join(repo.ugit_dir, "objects")
        if os.path.exists(objects_dir):
            for root, dirs, files in os.walk(objects_dir):
                for file in files:
                    if len(file) == 38:  # Remaining chars after first 2
                        sha = os.path.basename(root) + file
                        if len(sha) == 40:
                            try:
                                obj_type, content = get_object(sha, repo=repo)
                                # Verify object integrity
                                if obj_type not in ("blob", "tree", "commit", "tag"):
                                    errors.append(
                                        f"Unknown object type for {sha}: {obj_type}"
                                    )
                            except Exception as e:
                                errors.append(f"Corrupted object {sha}: {e}")

    # Check commit chain
    if head_sha:
        _check_commit_chain(repo, head_sha, errors)

    # Print results
    if errors:
        print(f"Found {len(errors)} error(s):")
        for error in errors:
            print(f"  ERROR: {error}")
        return len(errors)
    else:
        print("Repository integrity check passed")
        return 0


def _check_commit_chain(repo: Repository, commit_sha: str, errors: List[str]) -> None:
    """Check commit chain integrity."""
    visited = set()
    current = commit_sha

    while current and current not in visited:
        visited.add(current)
        try:
            commit_data = get_commit_data(current, repo=repo)

            # Check tree
            tree_sha = commit_data.get("tree")
            if tree_sha and not object_exists(tree_sha, repo=repo):
                errors.append(
                    f"Commit {current[:7]} references non-existent tree: {tree_sha}"
                )

            # Check parent
            parent = commit_data.get("parent")
            if parent and not validate_sha(parent):
                errors.append(f"Commit {current[:7]} has invalid parent SHA: {parent}")

            if parent is not None:
                current = parent
            else:
                break
        except ValueError as e:
            errors.append(f"Invalid commit {current[:7]}: {e}")
            break
