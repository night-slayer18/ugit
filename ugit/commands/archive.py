"""
Archive command implementation for ugit.

Create archive files (tar, zip) from repository commits.
"""

import os
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

from ..core.exceptions import UgitError
from ..core.objects import get_object
from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_commit_data, get_tree_entries
from ..utils.validation import validate_sha


def archive(
    output: str, commit: Optional[str] = None, format: Optional[str] = None
) -> None:
    """
    Create an archive from a commit.

    Args:
        output: Output file path
        commit: Commit to archive (default: HEAD)
        format: Archive format (tar, zip, or auto-detect from extension)
    """
    repo = ensure_repository()

    if commit is None:
        commit = repo.get_head_ref()
        if not commit:
            raise UgitError("No commits in repository")
    elif not validate_sha(commit):
        raise UgitError(f"Invalid commit SHA: {commit}")

    # Determine format from extension if not specified
    if format is None:
        if output.endswith(".zip"):
            format = "zip"
        elif output.endswith((".tar", ".tar.gz", ".tgz")):
            format = "tar"
        else:
            format = "tar"  # Default

    # Get commit tree
    try:
        commit_data = get_commit_data(commit, repo=repo)
        tree_sha = commit_data["tree"]
    except ValueError as e:
        raise UgitError(f"Invalid commit: {e}")

    # Create archive
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract tree to temporary directory
        _extract_tree(repo, tree_sha, tmpdir)

        # Create archive
        if format == "zip":
            _create_zip_archive(tmpdir, output)
        else:
            _create_tar_archive(tmpdir, output)

    print(f"Created archive: {output}")


def _extract_tree(repo: Repository, tree_sha: str, dest_dir: str) -> None:
    """Extract tree contents to directory."""
    try:
        entries = get_tree_entries(tree_sha, repo=repo)
        for mode, path, sha in entries:
            dest_path = os.path.join(dest_dir, path)

            if mode.startswith("10"):  # File
                try:
                    obj_type, content = get_object(sha, repo=repo)
                    if obj_type == "blob":
                        # Create directory if needed
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                        # Write file
                        with open(dest_path, "wb") as f:
                            f.write(content)
                except (FileNotFoundError, ValueError, OSError):
                    pass
            elif mode.startswith("40"):  # Directory
                os.makedirs(dest_path, exist_ok=True)
                _extract_tree(repo, sha, dest_path)
    except ValueError:
        pass


def _create_zip_archive(source_dir: str, output_path: str) -> None:
    """Create a ZIP archive."""
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)


def _create_tar_archive(source_dir: str, output_path: str) -> None:
    """Create a TAR archive."""
    if output_path.endswith(".gz"):
        mode = "w:gz"
    else:
        mode = "w"
    # tarfile.open has complex overloads, use type: ignore for mode parameter
    with tarfile.open(output_path, mode=mode) as tar:  # type: ignore[call-overload]
        tar.add(source_dir, arcname=".", recursive=True)
