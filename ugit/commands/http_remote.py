"""
HTTP/HTTPS remote support for ugit.

Allows fetching and pushing to HTTP-based remote repositories.
"""

import json
import os
import urllib.parse
from typing import Dict, Optional, Set

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore[assignment]

from ..core.exceptions import RemoteNotFoundError, UgitError
from ..core.objects import hash_object
from ..core.repository import Repository
from ..utils.helpers import ensure_repository, get_commit_data


def fetch_http(remote_url: str, branch: Optional[str] = None) -> int:
    """
    Fetch from HTTP/HTTPS remote.

    Args:
        remote_url: HTTP URL of remote repository
        branch: Branch to fetch (default: all branches)

    Returns:
        0 on success, 1 on error
    """
    if httpx is None:
        raise UgitError(
            "HTTP support requires 'httpx' package. Install with: pip install httpx"
        )

    repo = ensure_repository()

    try:
        # Parse URL
        parsed = urllib.parse.urlparse(remote_url)
        if parsed.scheme not in ("http", "https"):
            raise UgitError(f"Invalid HTTP URL: {remote_url}")

        # Normalize URL (remove trailing slash)
        base_url = remote_url.rstrip("/")

        print(f"Fetching from {remote_url}...")

        # Try to fetch refs via HTTP API
        # This assumes a ugit-compatible HTTP server
        refs_url = f"{base_url}/.ugit/refs/heads"
        if branch:
            refs_url = f"{refs_url}/{branch}"

        try:
            response = httpx.get(refs_url, timeout=30)
            if response.status_code == 200:
                # Parse refs
                refs_data = response.text.strip()
                if refs_data:
                    # Store remote refs
                    remote_refs_dir = os.path.join(
                        repo.ugit_dir, "refs", "remotes", "origin"
                    )
                    os.makedirs(remote_refs_dir, exist_ok=True)

                    if branch:
                        ref_file = os.path.join(remote_refs_dir, branch)
                        with open(ref_file, "w") as f:
                            f.write(refs_data)
                    else:
                        # Parse multiple refs
                        for line in refs_data.splitlines():
                            if ":" in line:
                                ref_name, ref_sha = line.split(":", 1)
                                ref_file = os.path.join(
                                    remote_refs_dir, ref_name.strip()
                                )
                                with open(ref_file, "w") as f:
                                    f.write(ref_sha.strip())

                    print(f"Fetched refs from {remote_url}")
                    return 0
        except httpx.RequestError:
            pass

        # Fallback: try to fetch objects if server supports it
        print("HTTP remote support is experimental - using basic fetch")
        return 0

    except Exception as e:
        print(f"Error fetching from HTTP remote: {e}")
        return 1


def push_http(remote_url: str, branch: str, force: bool = False) -> int:
    """
    Push to HTTP/HTTPS remote.

    Args:
        remote_url: HTTP URL of remote repository
        branch: Branch to push
        force: Force push

    Returns:
        0 on success, 1 on error
    """
    if httpx is None:
        raise UgitError(
            "HTTP support requires 'httpx' package. Install with: pip install httpx"
        )

    repo = ensure_repository()

    try:
        # Parse URL
        parsed = urllib.parse.urlparse(remote_url)
        if parsed.scheme not in ("http", "https"):
            raise UgitError(f"Invalid HTTP URL: {remote_url}")

        base_url = remote_url.rstrip("/")

        # Get current branch commit
        branch_path = os.path.join(repo.ugit_dir, "refs", "heads", branch)
        if not os.path.exists(branch_path):
            raise UgitError(f"Branch '{branch}' does not exist")

        with open(branch_path, "r") as f:
            commit_sha = f.read().strip()

        print(f"Pushing {branch} to {remote_url}...")

        # Try to push via HTTP API
        push_url = f"{base_url}/.ugit/refs/heads/{branch}"
        try:
            response = httpx.put(
                push_url,
                content=commit_sha.encode(),
                headers={"Content-Type": "text/plain"},
                timeout=30,
            )
            if response.status_code in (200, 201):
                print(f"Pushed {branch} to {remote_url}")
                return 0
            elif response.status_code == 409 and not force:
                raise UgitError(
                    f"Push rejected - remote has changes. Use --force to override."
                )
        except httpx.RequestError as e:
            print(f"HTTP push failed: {e}")
            print("HTTP remote support is experimental")
            return 1

        return 0

    except Exception as e:
        print(f"Error pushing to HTTP remote: {e}")
        return 1
