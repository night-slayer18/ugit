"""
Garbage collection command implementation for ugit.

Clean up unreachable objects to reclaim disk space.
"""

import os
from typing import Set

from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_commit_data


def gc(aggressive: bool = False) -> None:
    """
    Run garbage collection to clean up unreachable objects.

    Args:
        aggressive: More aggressive cleanup (not implemented yet)
    """
    repo = ensure_repository()

    # Find all reachable objects
    reachable = _find_reachable_objects(repo)

    # Find all objects in repository
    all_objects = _find_all_objects(repo)

    # Find unreachable objects
    unreachable = all_objects - reachable

    # Delete unreachable objects
    deleted_count = 0
    for sha in unreachable:
        if _delete_object(repo, sha):
            deleted_count += 1

    print(f"Removed {deleted_count} unreachable object(s)")
    if deleted_count > 0:
        print(f"Repository size reduced")


def _find_reachable_objects(repo: Repository) -> Set[str]:
    """Find all reachable objects from refs."""
    reachable = set()

    # Start from all refs
    refs = []

    # HEAD
    head_sha = repo.get_head_ref()
    if head_sha:
        refs.append(head_sha)

    # Branches
    heads_dir = os.path.join(repo.ugit_dir, "refs", "heads")
    if os.path.exists(heads_dir):
        for branch_file in os.listdir(heads_dir):
            branch_path = os.path.join(heads_dir, branch_file)
            try:
                with open(branch_path, "r") as f:
                    refs.append(f.read().strip())
            except (IOError, OSError):
                pass

    # Tags
    tags_dir = os.path.join(repo.ugit_dir, "refs", "tags")
    if os.path.exists(tags_dir):
        for tag_file in os.listdir(tags_dir):
            tag_path = os.path.join(tags_dir, tag_file)
            try:
                with open(tag_path, "r") as f:
                    tag_ref = f.read().strip()
                    refs.append(tag_ref)
                    # If it's an annotated tag, also follow the tag object
                    try:
                        from ..core.objects import get_object

                        obj_type, tag_data = get_object(tag_ref, repo=repo)
                        if obj_type == "tag":
                            import json

                            tag_obj = json.loads(tag_data.decode())
                            if "object" in tag_obj:
                                refs.append(tag_obj["object"])
                    except (ValueError, FileNotFoundError):
                        pass
            except (IOError, OSError):
                pass

    # Traverse from all refs
    visited = set()
    stack = list(refs)

    while stack:
        sha = stack.pop()
        if sha in visited or not sha or len(sha) != 40:
            continue
        visited.add(sha)
        reachable.add(sha)

        try:
            from ..core.objects import get_object
            from ..utils.helpers import get_tree_entries

            obj_type, obj_data = get_object(sha, repo=repo)

            if obj_type == "commit":
                commit_data = get_commit_data(sha, repo=repo)
                if "tree" in commit_data:
                    stack.append(commit_data["tree"])
                if "parent" in commit_data and commit_data["parent"]:
                    stack.append(commit_data["parent"])
                if "parents" in commit_data:
                    stack.extend(p for p in commit_data["parents"] if p)
            elif obj_type == "tree":
                entries = get_tree_entries(sha, repo=repo)
                for _, _, entry_sha in entries:
                    stack.append(entry_sha)
            elif obj_type == "tag":
                import json

                tag_obj = json.loads(obj_data.decode())
                if "object" in tag_obj:
                    stack.append(tag_obj["object"])
        except (ValueError, FileNotFoundError):
            pass

    return reachable


def _find_all_objects(repo: Repository) -> Set[str]:
    """Find all objects in the repository."""
    objects: Set[str] = set()
    objects_dir = os.path.join(repo.ugit_dir, "objects")

    if not os.path.exists(objects_dir):
        return objects

    for root, dirs, files in os.walk(objects_dir):
        for file in files:
            if len(file) == 38:  # Remaining chars after first 2
                sha = os.path.basename(root) + file
                if len(sha) == 40:
                    objects.add(sha)
            elif len(file) == 40:  # Old flat format
                objects.add(file)

    return objects


def _delete_object(repo: Repository, sha: str) -> bool:
    """Delete an object from the repository."""
    object_paths = [
        os.path.join(repo.ugit_dir, "objects", sha),
        os.path.join(repo.ugit_dir, "objects", sha[:2], sha[2:]),
    ]

    for obj_path in object_paths:
        if os.path.exists(obj_path):
            try:
                os.remove(obj_path)
                return True
            except OSError:
                pass

    return False
