"""
Clone remote repositories.

This module handles cloning remote ugit repositories into local directories.
"""

import os
import shutil
from typing import Optional

from ..core.repository import Repository
from ..utils.config import Config
from .remote import add_remote


def clone(url: str, directory: Optional[str] = None) -> None:
    """
    Clone a remote repository.

    Args:
        url: Remote repository URL
        directory: Local directory name (optional)
    """
    # Determine local directory name
    if directory is None:
        directory = _get_repo_name_from_url(url)

    # Check if directory already exists
    if os.path.exists(directory):
        print(
            f"fatal: destination path '{directory}' already exists and is not an empty directory"
        )
        return

    # Check if source repository exists and is valid
    if not _is_valid_source(url):
        print(
            f"fatal: repository '{url}' does not exist or is not a valid ugit repository"
        )
        return

    # Store current directory
    original_cwd = os.getcwd()

    # Convert relative URL to absolute path before changing directory
    if _is_local_path(url) and not os.path.isabs(url):
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
        os.makedirs(os.path.join(repo.ugit_dir, "refs", "remotes"))

        # Copy objects from source repository
        if _is_local_path(url):
            _copy_local_repository(url, repo)
        else:
            print(f"fatal: remote protocols not yet supported: {url}")
            # Clean up on failure
            os.chdir(original_cwd)
            shutil.rmtree(directory)
            return

        # Add origin remote
        add_remote("origin", url)

        # Set up initial HEAD and checkout
        _setup_initial_checkout(repo, url)

        print(f"Cloning into '{directory}'...")
        print("done.")

    except Exception as e:
        # Clean up on error
        os.chdir(original_cwd)
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
            except (OSError, PermissionError) as cleanup_error:
                print(f"warning: could not remove {directory}: {cleanup_error}")
        print(f"fatal: failed to clone repository: {e}")
    finally:
        # Always return to original directory
        os.chdir(original_cwd)


def _get_repo_name_from_url(url: str) -> str:
    """
    Extract repository name from URL.

    Args:
        url: Repository URL

    Returns:
        Directory name to use
    """
    # Remove trailing slashes and .git suffix
    name = url.rstrip("/")
    if name.endswith(".git"):
        name = name[:-4]

    # Get basename
    name = os.path.basename(name)

    # Default fallback
    if not name or name == ".":
        name = "repository"

    return name


def _is_valid_source(url: str) -> bool:
    """
    Check if source URL points to a valid ugit repository.

    Args:
        url: Repository URL to check

    Returns:
        True if valid ugit repository
    """
    if _is_local_path(url):
        # Check if it's a ugit repository
        ugit_dir = os.path.join(url, ".ugit")
        return os.path.exists(ugit_dir) and os.path.isdir(ugit_dir)
    else:
        # For remote URLs, we'd need to implement HTTP/SSH checking
        # For now, assume they're valid if they follow URL patterns
        return url.startswith(("http://", "https://", "git://", "ssh://")) or "@" in url


def _is_local_path(url: str) -> bool:
    """
    Check if URL is a local filesystem path.

    Args:
        url: URL to check

    Returns:
        True if local path
    """
    return (
        os.path.isabs(url)
        or url.startswith("./")
        or url.startswith("../")
        or os.path.exists(url)  # Check if it's a relative path that exists
        or (
            not url.startswith(("http://", "https://", "git://", "ssh://"))
            and "@" not in url
        )
    )


def _copy_local_repository(source_url: str, dest_repo: Repository) -> None:
    """
    Copy objects and refs from local source repository.

    Args:
        source_url: Source repository path
        dest_repo: Destination repository
    """
    source_ugit_dir = os.path.join(source_url, ".ugit")

    # Copy objects
    source_objects_dir = os.path.join(source_ugit_dir, "objects")
    dest_objects_dir = os.path.join(dest_repo.ugit_dir, "objects")

    if os.path.exists(source_objects_dir):
        for root, dirs, files in os.walk(source_objects_dir):
            for file in files:
                source_file = os.path.join(root, file)
                # Calculate relative path
                rel_path = os.path.relpath(source_file, source_objects_dir)
                dest_file = os.path.join(dest_objects_dir, rel_path)

                # Create directory if needed
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)

                # Copy file
                shutil.copy2(source_file, dest_file)

    # Copy refs
    source_refs_dir = os.path.join(source_ugit_dir, "refs")
    dest_refs_dir = os.path.join(dest_repo.ugit_dir, "refs")

    if os.path.exists(source_refs_dir):
        # Copy to remotes/origin/
        dest_remote_refs_dir = os.path.join(dest_refs_dir, "remotes", "origin")
        os.makedirs(dest_remote_refs_dir, exist_ok=True)

        # Copy heads to remotes/origin/
        source_heads_dir = os.path.join(source_refs_dir, "heads")
        if os.path.exists(source_heads_dir):
            for branch_file in os.listdir(source_heads_dir):
                source_branch = os.path.join(source_heads_dir, branch_file)
                dest_branch = os.path.join(dest_remote_refs_dir, branch_file)
                if os.path.isfile(source_branch):
                    shutil.copy2(source_branch, dest_branch)


def _setup_initial_checkout(repo: Repository, source_url: str) -> None:
    """
    Set up initial HEAD and checkout the default branch.

    Args:
        repo: Repository instance
        source_url: Source repository URL
    """
    # Read HEAD from source to determine default branch
    if _is_local_path(source_url):
        source_head_path = os.path.join(source_url, ".ugit", "HEAD")
        default_branch = "main"  # fallback

        if os.path.exists(source_head_path):
            try:
                with open(source_head_path, "r") as f:
                    head_content = f.read().strip()
                    if head_content.startswith("ref: refs/heads/"):
                        default_branch = head_content[16:]  # Remove 'ref: refs/heads/'
            except (IOError, OSError):
                pass

        # Check if we have the branch in remotes/origin
        remote_branch_path = os.path.join(
            repo.ugit_dir, "refs", "remotes", "origin", default_branch
        )
        if os.path.exists(remote_branch_path):
            try:
                # Read the commit SHA
                with open(remote_branch_path, "r") as f:
                    commit_sha = f.read().strip()

                # Create local branch
                local_branch_path = os.path.join(
                    repo.ugit_dir, "refs", "heads", default_branch
                )
                os.makedirs(os.path.dirname(local_branch_path), exist_ok=True)
                with open(local_branch_path, "w") as f:
                    f.write(commit_sha)

                # Set HEAD to point to the branch
                head_path = os.path.join(repo.ugit_dir, "HEAD")
                with open(head_path, "w") as f:
                    f.write(f"ref: refs/heads/{default_branch}")

                # Perform checkout (simplified - just restore working directory)
                _checkout_commit(repo, commit_sha)

            except (IOError, OSError) as e:
                print(f"Warning: failed to checkout {default_branch}: {e}")


def _checkout_commit(repo: Repository, commit_sha: str) -> None:
    """
    Checkout files from a commit to working directory.

    Args:
        repo: Repository instance
        commit_sha: Commit SHA to checkout
    """
    import json

    from ..core.objects import get_object

    try:
        commit_type, commit_content = get_object(commit_sha)
        if commit_type != "commit":
            return

        # Parse commit JSON to get tree SHA
        try:
            commit_data = json.loads(commit_content.decode("utf-8"))
            tree_sha = commit_data.get("tree")
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fallback to Git-style parsing
            lines = commit_content.decode("utf-8").split("\n")
            tree_sha = None
            for line in lines:
                if line.startswith("tree "):
                    tree_sha = line[5:]
                    break

        if tree_sha:
            _checkout_tree(repo, tree_sha, ".")

    except Exception as e:
        print(f"Warning: failed to checkout working directory: {e}")


def _checkout_tree(repo: Repository, tree_sha: str, path: str) -> None:
    """
    Recursively checkout a tree object.

    Args:
        repo: Repository instance
        tree_sha: Tree SHA to checkout
        path: Path to checkout to
    """
    import json

    from ..core.objects import get_object

    try:
        tree_type, tree_content = get_object(tree_sha)
        if tree_type != "tree":
            print(f"Error: {tree_sha} is not a tree, it's a {tree_type}")
            return

        # Parse tree entries - our trees are JSON format
        try:
            tree_entries = json.loads(tree_content.decode("utf-8"))
            entries = []

            for entry in tree_entries:
                if len(entry) >= 2:
                    name = entry[0]
                    sha = entry[1]
                    # Assume regular file mode for now
                    entries.append(("100644", name, sha))

        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fallback to Git-style binary parsing
            entries = []
            content = tree_content

            while content:
                # Find null terminator for mode/name
                null_idx = content.find(b"\x00")
                if null_idx == -1:
                    break

                mode_name = content[:null_idx].decode("utf-8")
                sha_bytes = content[null_idx + 1 : null_idx + 21]

                if len(sha_bytes) < 20:
                    break

                sha = sha_bytes.hex()
                content = content[null_idx + 21 :]

                # Parse mode and name
                parts = mode_name.split(" ", 1)
                if len(parts) == 2:
                    mode, name = parts
                    entries.append((mode, name, sha))

        # Process each entry
        for mode, name, sha in entries:
            entry_path = os.path.join(path, name)

            if mode.startswith("10"):  # Regular file
                # Get file content and write it
                try:
                    file_type, file_content = get_object(sha)
                    if file_type == "blob":
                        # Only create directories if needed
                        dir_path = os.path.dirname(entry_path)
                        if dir_path and dir_path != ".":
                            os.makedirs(dir_path, exist_ok=True)
                        with open(entry_path, "wb") as f:
                            f.write(file_content)
                except (OSError, IOError, PermissionError) as e:
                    # Skip files that can't be written (e.g., permission issues)
                    continue

            elif mode.startswith("40"):  # Directory
                os.makedirs(entry_path, exist_ok=True)
                _checkout_tree(repo, sha, entry_path)

    except Exception as e:
        print(f"Warning: failed to checkout tree {tree_sha}: {e}")
