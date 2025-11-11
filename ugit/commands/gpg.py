"""
GPG signing implementation for ugit.

Allows signing commits and tags with GPG.
"""

import os
import subprocess  # nosec B404
from typing import Optional

from ..core.exceptions import UgitError
from ..core.repository import Repository
from ..utils.helpers import ensure_repository


def sign_commit(commit_sha: str, key_id: Optional[str] = None) -> str:
    """
    Sign a commit with GPG.

    Args:
        commit_sha: SHA of commit to sign
        key_id: GPG key ID (optional, uses default key if not provided)

    Returns:
        Signature string
    """
    repo = ensure_repository()

    # Get commit object
    from ..core.objects import get_object

    try:
        obj_type, commit_data = get_object(commit_sha, repo=repo)
        if obj_type != "commit":
            raise UgitError(f"Object {commit_sha} is not a commit")

        # Sign the commit data
        signature = _gpg_sign(commit_data, key_id)
        return signature
    except (FileNotFoundError, ValueError) as e:
        raise UgitError(f"Cannot sign commit {commit_sha[:7]}: {e}")


def sign_tag(tag_sha: str, key_id: Optional[str] = None) -> str:
    """
    Sign a tag with GPG.

    Args:
        tag_sha: SHA of tag to sign
        key_id: GPG key ID (optional, uses default key if not provided)

    Returns:
        Signature string
    """
    repo = ensure_repository()

    # Get tag object
    from ..core.objects import get_object

    try:
        obj_type, tag_data = get_object(tag_sha, repo=repo)
        if obj_type != "tag":
            raise UgitError(f"Object {tag_sha} is not a tag")

        # Sign the tag data
        signature = _gpg_sign(tag_data, key_id)
        return signature
    except (FileNotFoundError, ValueError) as e:
        raise UgitError(f"Cannot sign tag {tag_sha[:7]}: {e}")


def verify_signature(commit_sha: str, signature: str) -> bool:
    """
    Verify a GPG signature.

    Args:
        commit_sha: SHA of commit to verify
        signature: GPG signature

    Returns:
        True if signature is valid
    """
    repo = ensure_repository()

    # Get commit object
    from ..core.objects import get_object

    try:
        obj_type, commit_data = get_object(commit_sha, repo=repo)
        if obj_type != "commit":
            raise UgitError(f"Object {commit_sha} is not a commit")

        # Verify signature
        return _gpg_verify(commit_data, signature)
    except (FileNotFoundError, ValueError) as e:
        raise UgitError(f"Cannot verify commit {commit_sha[:7]}: {e}")


def _gpg_sign(data: bytes, key_id: Optional[str] = None) -> str:
    """Sign data with GPG."""
    try:
        cmd = ["gpg", "--detach-sign", "--armor"]
        if key_id:
            cmd.extend(["--default-key", key_id])
        cmd.append("-")

        process = subprocess.run(  # nosec B603
            cmd,
            input=data,
            capture_output=True,
            text=False,
            check=True,
        )

        return process.stdout.decode("utf-8", errors="replace")
    except subprocess.CalledProcessError as e:
        raise UgitError(
            f"GPG signing failed: {e.stderr.decode('utf-8', errors='replace')}"
        )
    except FileNotFoundError:
        raise UgitError("GPG not found. Please install GPG to use signing features.")


def _gpg_verify(data: bytes, signature: str) -> bool:
    """Verify GPG signature."""
    try:
        # Write signature to temp file
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".sig"
        ) as sig_file:
            sig_file.write(signature)
            sig_path = sig_file.name

        try:
            # Write data to temp file
            with tempfile.NamedTemporaryFile(delete=False) as data_file:
                data_file.write(data)
                data_path = data_file.name

            try:
                # Verify signature
                cmd = ["gpg", "--verify", sig_path, data_path]
                result = subprocess.run(  # nosec B603
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                return result.returncode == 0
            finally:
                os.unlink(data_path)
        finally:
            os.unlink(sig_path)
    except Exception as e:
        raise UgitError(f"GPG verification failed: {e}")


def has_gpg() -> bool:
    """Check if GPG is available."""
    try:
        # Use shutil.which to find full path, but gpg is standard system command
        subprocess.run(  # nosec B607 B603
            ["gpg", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
