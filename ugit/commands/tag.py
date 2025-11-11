"""
Tag command implementation for ugit.

Handles lightweight and annotated tags for marking important commits.
"""

import json
import os
from datetime import datetime
from typing import Optional

from ..core.exceptions import InvalidRefError, UgitError
from ..core.objects import hash_object
from ..core.repository import Repository
from ..utils.atomic import atomic_write_text
from ..utils.config import Config
from ..utils.helpers import ensure_repository, get_commit_data
from ..utils.validation import validate_sha


def tag(
    tag_name: Optional[str] = None,
    list_tags: bool = False,
    delete: Optional[str] = None,
    annotated: bool = False,
    message: Optional[str] = None,
    commit: Optional[str] = None,
) -> None:
    """
    Create, list, or delete tags.

    Args:
        tag_name: Name of the tag to create
        list_tags: List all tags
        delete: Name of tag to delete
        annotated: Create annotated tag (default: lightweight)
        message: Tag message for annotated tags
        commit: Commit SHA to tag (default: HEAD)
    """
    repo = ensure_repository()

    if list_tags:
        _list_tags(repo)
    elif delete:
        _delete_tag(repo, delete)
    elif tag_name:
        if annotated:
            _create_annotated_tag(repo, tag_name, message, commit)
        else:
            _create_lightweight_tag(repo, tag_name, commit)
    else:
        _list_tags(repo)


def _list_tags(repo: Repository) -> None:
    """List all tags in the repository."""
    tags_dir = os.path.join(repo.ugit_dir, "refs", "tags")
    if not os.path.exists(tags_dir):
        print("No tags found")
        return

    tags = sorted(os.listdir(tags_dir))
    if not tags:
        print("No tags found")
        return

    for tag_name in tags:
        tag_path = os.path.join(tags_dir, tag_name)
        try:
            with open(tag_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            # Check if it's an annotated tag (starts with object SHA) or lightweight (direct commit SHA)
            if len(content) == 40 and validate_sha(content):
                # Lightweight tag - direct commit reference
                print(tag_name)
            else:
                # Annotated tag - contains tag object SHA
                print(f"{tag_name} (annotated)")
        except (IOError, OSError):
            print(tag_name)


def _create_lightweight_tag(
    repo: Repository, tag_name: str, commit: Optional[str] = None
) -> None:
    """
    Create a lightweight tag (direct reference to commit).

    Args:
        repo: Repository instance
        tag_name: Name of the tag
        commit: Commit SHA to tag (default: HEAD)
    """
    if not _is_valid_tag_name(tag_name):
        raise ValueError(f"Invalid tag name: '{tag_name}'")

    # Get commit to tag
    if commit is None:
        commit = repo.get_head_ref()
        if not commit:
            raise UgitError("No commits yet - cannot create tag")
    else:
        if not validate_sha(commit):
            raise InvalidRefError(f"Invalid commit SHA: {commit}")
        # Verify commit exists
        try:
            get_commit_data(commit, repo=repo)
        except ValueError:
            raise InvalidRefError(f"Commit {commit} does not exist")

    # Create tag reference
    tags_dir = os.path.join(repo.ugit_dir, "refs", "tags")
    os.makedirs(tags_dir, exist_ok=True)
    tag_path = os.path.join(tags_dir, tag_name)

    if os.path.exists(tag_path):
        raise UgitError(f"Tag '{tag_name}' already exists")

    atomic_write_text(tag_path, commit, create_dirs=True)
    print(f"Created lightweight tag '{tag_name}'")


def _create_annotated_tag(
    repo: Repository,
    tag_name: str,
    message: Optional[str] = None,
    commit: Optional[str] = None,
) -> None:
    """
    Create an annotated tag (tag object with metadata).

    Args:
        repo: Repository instance
        tag_name: Name of the tag
        message: Tag message
        commit: Commit SHA to tag (default: HEAD)
    """
    if not _is_valid_tag_name(tag_name):
        raise ValueError(f"Invalid tag name: '{tag_name}'")

    # Get commit to tag
    if commit is None:
        commit = repo.get_head_ref()
        if not commit:
            raise UgitError("No commits yet - cannot create tag")
    else:
        if not validate_sha(commit):
            raise InvalidRefError(f"Invalid commit SHA: {commit}")
        try:
            get_commit_data(commit, repo=repo)
        except ValueError:
            raise InvalidRefError(f"Commit {commit} does not exist")

    # Get tagger info
    config = Config(repo.path)
    tagger = config.get_author_string()

    # Create tag object
    tag_data = {
        "object": commit,
        "type": "commit",
        "tag": tag_name,
        "tagger": tagger,
        "timestamp": datetime.now().isoformat(),
        "message": message or f"Tagged commit {commit[:7]}",
    }

    tag_bytes = json.dumps(tag_data, indent=2).encode()
    tag_sha = hash_object(tag_bytes, "tag", repo=repo)

    # Create tag reference pointing to tag object
    tags_dir = os.path.join(repo.ugit_dir, "refs", "tags")
    os.makedirs(tags_dir, exist_ok=True)
    tag_path = os.path.join(tags_dir, tag_name)

    if os.path.exists(tag_path):
        raise UgitError(f"Tag '{tag_name}' already exists")

    atomic_write_text(tag_path, tag_sha, create_dirs=True)
    print(f"Created annotated tag '{tag_name}'")


def _delete_tag(repo: Repository, tag_name: str) -> None:
    """
    Delete a tag.

    Args:
        repo: Repository instance
        tag_name: Name of tag to delete
    """
    tag_path = os.path.join(repo.ugit_dir, "refs", "tags", tag_name)
    if not os.path.exists(tag_path):
        raise UgitError(f"Tag '{tag_name}' does not exist")

    os.remove(tag_path)
    print(f"Deleted tag '{tag_name}'")


def _is_valid_tag_name(name: str) -> bool:
    """
    Validate tag name.

    Args:
        name: Tag name to validate

    Returns:
        True if valid tag name
    """
    if not name or not isinstance(name, str):
        return False

    # Similar to branch names but can contain dots
    if name.startswith(".") or name.endswith(".lock"):
        return False

    if ".." in name:
        return False

    # Check for invalid characters
    invalid_chars = ["~", "^", ":", "?", "*", "[", " ", "\\", "@", "{", "}"]
    for char in invalid_chars:
        if char in name:
            return False

    # Check for control characters
    if any(ord(c) < 32 for c in name):
        return False

    return True


def get_tag_commit(repo: Repository, tag_name: str) -> str:
    """
    Get the commit SHA that a tag points to.

    Args:
        repo: Repository instance
        tag_name: Name of the tag

    Returns:
        Commit SHA
    """
    tag_path = os.path.join(repo.ugit_dir, "refs", "tags", tag_name)
    if not os.path.exists(tag_path):
        raise UgitError(f"Tag '{tag_name}' does not exist")

    with open(tag_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # If it's a lightweight tag, content is the commit SHA
    if len(content) == 40 and validate_sha(content):
        return content

    # If it's an annotated tag, content is the tag object SHA
    # We need to read the tag object to get the commit
    from ..core.objects import get_object

    try:
        tag_type, tag_data = get_object(content, repo=repo)
        if tag_type != "tag":
            raise UgitError(f"Tag '{tag_name}' points to invalid object")
        tag_obj = json.loads(tag_data.decode())
        result: str = tag_obj["object"]
        return result
    except (ValueError, KeyError, FileNotFoundError) as e:
        raise UgitError(f"Invalid tag object for '{tag_name}': {e}")
