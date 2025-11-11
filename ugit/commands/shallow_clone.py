"""
Shallow clone implementation for ugit.

Clone repository with limited history depth.
"""

import os
import shutil
from typing import Optional

from ..core.exceptions import UgitError
from ..core.objects import object_exists
from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_commit_data, is_local_path
from .clone import (
    _copy_local_repository,
    _get_repo_name_from_url,
    _setup_initial_checkout,
)
from .remote import add_remote


def shallow_clone(url: str, directory: Optional[str] = None, depth: int = 1) -> None:
    """
    Clone repository with limited history.

    Args:
        url: Repository URL
        directory: Target directory (default: repo name)
        depth: History depth to clone (default: 1)
    """
    import sys

    original_cwd = os.getcwd()

    if directory is None:
        directory = _get_repo_name_from_url(url)

    if os.path.exists(directory):
        raise UgitError(f"fatal: destination path '{directory}' already exists")

    if is_local_path(url):
        url = os.path.abspath(url)

    try:
        # Create directory
        os.makedirs(directory)

        # Initialize repository in the new directory
        os.chdir(directory)
        repo = Repository()

        # Create ugit directory structure
        os.makedirs(repo.ugit_dir)
        os.makedirs(os.path.join(repo.ugit_dir, "objects"))
        os.makedirs(os.path.join(repo.ugit_dir, "refs", "heads"))

        # Copy objects from source repository (limited depth)
        if is_local_path(url):
            _copy_shallow_repository(url, repo, depth)
        else:
            raise UgitError(f"fatal: remote protocols not yet supported: {url}")

        # Add origin remote
        add_remote("origin", url)

        # Set up initial HEAD and checkout
        _setup_initial_checkout(repo, url)

        # Mark as shallow clone
        shallow_file = os.path.join(repo.ugit_dir, "shallow")
        with open(shallow_file, "w") as f:
            f.write(str(depth))

        print(f"Cloning into '{directory}'...")
        print(f"Shallow clone (depth: {depth})")
        print("done.")

    except Exception as e:
        # Clean up on error
        os.chdir(original_cwd)
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
            except (OSError, PermissionError) as cleanup_error:
                sys.stderr.write(
                    f"warning: could not remove {directory}: {cleanup_error}\n"
                )
        raise UgitError(f"fatal: failed to shallow clone repository: {e}")
    finally:
        # Always return to original directory
        os.chdir(original_cwd)


def _copy_shallow_repository(
    source_path: str, dest_repo: Repository, depth: int
) -> None:
    """Copy repository objects with limited depth."""
    source_ugit_dir = os.path.join(source_path, ".ugit")
    if not os.path.exists(source_ugit_dir):
        raise UgitError(f"not a ugit repository: {source_path}")

    # Get HEAD from source
    source_head_path = os.path.join(source_ugit_dir, "HEAD")
    if not os.path.exists(source_head_path):
        raise UgitError("source repository has no HEAD")

    with open(source_head_path, "r") as f:
        head_content = f.read().strip()

    if head_content.startswith("ref: refs/heads/"):
        branch_name = head_content.replace("ref: refs/heads/", "")
        branch_path = os.path.join(source_ugit_dir, "refs", "heads", branch_name)
        if os.path.exists(branch_path):
            with open(branch_path, "r") as f:
                head_sha = f.read().strip()
        else:
            raise UgitError(f"branch '{branch_name}' not found in source")
    else:
        head_sha = head_content

    # Copy objects up to specified depth
    visited = set()
    queue = [(head_sha, 0)]  # (sha, depth)

    while queue:
        sha, current_depth = queue.pop(0)

        if sha in visited or current_depth >= depth:
            continue

        visited.add(sha)

        # Copy object
        source_obj_path = os.path.join(source_ugit_dir, "objects", sha)
        if os.path.exists(source_obj_path):
            dest_obj_dir = os.path.join(dest_repo.ugit_dir, "objects", sha[:2])
            os.makedirs(dest_obj_dir, exist_ok=True)
            dest_obj_path = os.path.join(dest_obj_dir, sha[2:])
            shutil.copy2(source_obj_path, dest_obj_path)

        # If it's a commit, add parent to queue
        if current_depth < depth - 1:
            try:
                commit_data = get_commit_data(sha, repo=Repository(source_path))
                if "tree" in commit_data:
                    tree_sha = commit_data["tree"]
                    if tree_sha not in visited:
                        queue.append((tree_sha, current_depth + 1))

                if "parent" in commit_data and commit_data["parent"]:
                    parent_sha = commit_data["parent"]
                    if parent_sha not in visited:
                        queue.append((parent_sha, current_depth + 1))
            except ValueError:
                pass

    # Copy refs
    source_refs_dir = os.path.join(source_ugit_dir, "refs", "heads")
    dest_refs_dir = os.path.join(dest_repo.ugit_dir, "refs", "heads")
    os.makedirs(dest_refs_dir, exist_ok=True)

    if os.path.exists(source_refs_dir):
        for branch_file in os.listdir(source_refs_dir):
            source_branch_path = os.path.join(source_refs_dir, branch_file)
            dest_branch_path = os.path.join(dest_refs_dir, branch_file)
            shutil.copy2(source_branch_path, dest_branch_path)
