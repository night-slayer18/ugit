"""
FastAPI web server for ugit repository viewer.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ugit.core.objects import get_object
from ugit.core.repository import Repository


class UgitWebServer:
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self.repo = Repository(self.repo_path)

        # Initialize FastAPI app
        self.app = FastAPI(
            title="ugit Repository Viewer",
            description="Web-based repository browser for ugit",
            version="1.0.0",
        )

        # Setup static files and templates
        web_dir = Path(__file__).parent
        self.app.mount(
            "/static", StaticFiles(directory=str(web_dir / "static")), name="static"
        )
        self.templates = Jinja2Templates(directory=str(web_dir / "templates"))

        # Setup routes
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup all web routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def home(request: Request) -> HTMLResponse:
            """Main repository view"""
            return self.templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "repo_name": os.path.basename(self.repo_path),
                    "repo_path": self.repo_path,
                },
            )

        @self.app.get("/api/files")
        async def list_files(path: str = "", commit: str = "HEAD") -> Any:
            """List files and directories from the committed tree (repository view)"""
            try:
                # Get the current commit SHA
                if commit == "HEAD":
                    try:
                        head_file = os.path.join(self.repo_path, ".ugit", "HEAD")
                        with open(head_file, "r") as f:
                            ref = f.read().strip()

                        if ref.startswith("ref: "):
                            ref_path = ref[5:]
                            ref_file = os.path.join(self.repo_path, ".ugit", ref_path)
                            if os.path.exists(ref_file):
                                with open(ref_file, "r") as f:
                                    commit_sha = f.read().strip()
                            else:
                                return {"files": [], "commit": None, "path": path}
                        else:
                            commit_sha = ref
                    except FileNotFoundError:
                        return {"files": [], "commit": None, "path": path}
                else:
                    commit_sha = commit

                # Get the commit object
                try:
                    obj_type, commit_data = get_object(commit_sha)
                    if obj_type != "commit":
                        return {"files": [], "commit": None, "path": path}

                    commit_obj = json.loads(commit_data.decode("utf-8"))
                    tree_sha = commit_obj["tree"]
                except Exception as e:
                    sys.stderr.write(f"Error reading commit object: {e}\n")
                    return {"files": [], "commit": None, "path": path}

                # Get the tree contents (ugit uses flat structure with full paths)
                try:
                    obj_type, tree_data = get_object(tree_sha)
                    if obj_type != "tree":
                        return {"files": [], "commit": None, "path": path}

                    tree_obj = json.loads(tree_data.decode("utf-8"))
                except Exception as e:
                    sys.stderr.write(f"Error reading tree: {e}\n")
                    return {"files": [], "commit": None, "path": path}

                # ugit stores all files with full paths in a flat tree structure
                # We need to create virtual directories from these paths
                files = []
                directories = set()

                # Normalize the requested path
                current_path = path.rstrip("/") if path else ""

                # Process all entries in the flat tree
                for entry in tree_obj:
                    if len(entry) >= 2:
                        full_file_path = entry[0]
                        file_sha = entry[1]

                        # Check if this file belongs to the current path
                        if current_path:
                            if not full_file_path.startswith(current_path + "/"):
                                continue  # Not in this directory
                            # Get the relative path from current directory
                            relative_path = full_file_path[len(current_path) + 1 :]
                        else:
                            relative_path = full_file_path

                        # Split the path to see if it's directly in current directory
                        path_parts = relative_path.split("/")

                        if len(path_parts) == 1:
                            # File is directly in current directory
                            file_name = path_parts[0]

                            # Get file type and size
                            try:
                                obj_type, _ = get_object(file_sha)
                                file_type = obj_type
                            except Exception:
                                file_type = "blob"

                            file_info = {
                                "name": file_name,
                                "type": file_type,
                                "sha": file_sha,
                                "size": None,
                            }

                            # Get size for blob files
                            if file_type == "blob":
                                try:
                                    blob_type, blob_data = get_object(file_sha)
                                    if blob_type == "blob":
                                        file_info["size"] = len(blob_data)
                                except (FileNotFoundError, ValueError):
                                    # Skip files that can't be read
                                    pass

                            # Get last commit info for this specific file
                            try:
                                last_commit_info = self._get_last_commit_for_file(
                                    full_file_path, commit_sha
                                )
                                if last_commit_info:
                                    file_info["commit_message"] = last_commit_info[
                                        "message"
                                    ]
                                    file_info["commit_date"] = last_commit_info[
                                        "timestamp"
                                    ]
                                    file_info["commit_sha"] = last_commit_info["sha"]
                            except Exception as e:
                                sys.stderr.write(
                                    f"Error getting commit info for {full_file_path}: {e}\n"
                                )

                            files.append(file_info)
                        else:
                            # File is in a subdirectory, add the subdirectory
                            subdir_name = path_parts[0]
                            if subdir_name not in directories:
                                directories.add(subdir_name)

                                # Get commit info for the directory (find last commit that touched files in this directory)
                                subdir_info = {
                                    "name": subdir_name,
                                    "type": "tree",
                                    "sha": None,  # Virtual directory
                                    "size": None,
                                }

                                # Find the most recent commit that modified any file in this directory
                                try:
                                    full_subdir_path = (
                                        f"{current_path}/{subdir_name}"
                                        if current_path
                                        else subdir_name
                                    )
                                    # Look for any file that starts with subdir_name/ in the commit history
                                    dir_commit_info = (
                                        self._get_last_commit_for_directory(
                                            full_subdir_path, commit_sha
                                        )
                                    )
                                    if dir_commit_info:
                                        subdir_info["commit_message"] = dir_commit_info[
                                            "message"
                                        ]
                                        subdir_info["commit_date"] = dir_commit_info[
                                            "timestamp"
                                        ]
                                        subdir_info["commit_sha"] = dir_commit_info[
                                            "sha"
                                        ]
                                    else:
                                        # Fallback to current commit
                                        subdir_info["commit_message"] = commit_obj.get(
                                            "message", "No message"
                                        )
                                        subdir_info["commit_date"] = commit_obj.get(
                                            "timestamp", 0
                                        )
                                        subdir_info["commit_sha"] = commit_sha
                                except Exception as e:
                                    sys.stderr.write(
                                        f"Error getting directory commit info for {subdir_name}: {e}\n"
                                    )
                                    # Fallback to current commit
                                    subdir_info["commit_message"] = commit_obj.get(
                                        "message", "No message"
                                    )
                                    subdir_info["commit_date"] = commit_obj.get(
                                        "timestamp", 0
                                    )
                                    subdir_info["commit_sha"] = commit_sha

                                files.append(subdir_info)

                # Sort: directories first, then files
                files.sort(key=lambda x: (x["type"] != "tree", x["name"].lower()))

                # Get commit info for latest commit display
                commit_info = {
                    "sha": commit_sha,
                    "message": commit_obj.get("message", ""),
                    "author": commit_obj.get("author", ""),
                    "timestamp": commit_obj.get("timestamp", 0),
                }

                return {"files": files, "commit": commit_info, "path": path}

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/file")
        async def get_file_content(path: str, commit: str = "HEAD") -> Any:
            """Get content of a specific file from the committed tree"""
            try:
                # Get the current commit SHA
                if commit == "HEAD":
                    try:
                        with open(
                            os.path.join(self.repo_path, ".ugit", "HEAD"), "r"
                        ) as f:
                            ref = f.read().strip()

                        if ref.startswith("ref: "):
                            ref_path = ref[5:]
                            ref_file = os.path.join(self.repo_path, ".ugit", ref_path)
                            if os.path.exists(ref_file):
                                with open(ref_file, "r") as f:
                                    commit_sha = f.read().strip()
                            else:
                                raise HTTPException(
                                    status_code=404, detail="Repository has no commits"
                                )
                        else:
                            commit_sha = ref
                    except FileNotFoundError:
                        raise HTTPException(
                            status_code=404, detail="Repository has no commits"
                        )
                else:
                    commit_sha = commit

                # Get the commit object and tree
                try:
                    obj_type, commit_data = get_object(commit_sha)
                    if obj_type != "commit":
                        raise HTTPException(status_code=404, detail="Invalid commit")

                    commit_obj = json.loads(commit_data.decode("utf-8"))
                    tree_sha = commit_obj["tree"]
                except Exception:
                    raise HTTPException(status_code=404, detail="Invalid commit")

                # Get the tree contents (ugit uses flat structure with full paths)
                try:
                    obj_type, tree_data = get_object(tree_sha)
                    if obj_type != "tree":
                        raise HTTPException(status_code=404, detail="Invalid tree")

                    tree_obj = json.loads(tree_data.decode("utf-8"))
                except Exception:
                    raise HTTPException(status_code=404, detail="Invalid tree")

                # Find the file in the flat tree structure
                file_sha = None
                for entry in tree_obj:
                    if len(entry) >= 2 and entry[0] == path:
                        file_sha = entry[1]
                        break

                if not file_sha:
                    raise HTTPException(status_code=404, detail="File not found")

                # Get the file content
                try:
                    obj_type, file_data = get_object(file_sha)
                    if obj_type != "blob":
                        raise HTTPException(status_code=404, detail="Not a file")
                except Exception as e:
                    raise HTTPException(
                        status_code=404, detail=f"Error reading file: {e}"
                    )

                # Check if file is binary
                is_binary = b"\x00" in file_data[:1024]

                if is_binary:
                    return {
                        "path": path,
                        "type": "binary",
                        "size": len(file_data),
                        "content": None,
                        "commit_sha": commit_sha,
                    }

                # Try to decode text file
                try:
                    content = file_data.decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        content = file_data.decode("latin1")
                    except UnicodeDecodeError:
                        return {
                            "path": path,
                            "type": "binary",
                            "size": len(file_data),
                            "content": None,
                            "commit_sha": commit_sha,
                        }

                return {
                    "path": path,
                    "type": "text",
                    "size": len(file_data),
                    "content": content,
                    "lines": len(content.split("\n")),
                    "commit_sha": commit_sha,
                }

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/commits")
        async def get_commits(limit: int = 50, offset: int = 0) -> Any:
            """Get commit history"""
            try:
                # Use ugit's log command to get commits
                commits_data = []
                commit_count = 0

                # Get current HEAD
                try:
                    with open(os.path.join(self.repo_path, ".ugit", "HEAD"), "r") as f:
                        ref = f.read().strip()

                    if ref.startswith("ref: "):
                        ref_path = ref[5:]  # Remove 'ref: ' prefix
                        ref_file = os.path.join(self.repo_path, ".ugit", ref_path)
                        if os.path.exists(ref_file):
                            with open(ref_file, "r") as f:
                                current_sha = f.read().strip()
                        else:
                            current_sha = None
                    else:
                        # Direct SHA reference
                        if len(ref) == 40:  # ugit uses 40-character SHAs
                            current_sha = ref
                        else:
                            current_sha = None

                except (FileNotFoundError, IndexError):
                    current_sha = None

                if not current_sha:
                    return {"commits": [], "total": 0}

                # Traverse commit history
                visited = set()
                to_visit: List[Optional[str]] = [current_sha]

                while to_visit and commit_count < offset + limit:
                    sha = to_visit.pop(0)

                    # Skip if not a valid SHA (should be 40 characters for ugit)
                    if not sha or len(sha) != 40:
                        continue

                    if sha in visited:
                        continue
                    visited.add(sha)

                    try:
                        obj_type, commit_data = get_object(sha)
                        if obj_type != "commit":
                            continue

                        # Parse commit object (JSON format)
                        commit_obj = json.loads(commit_data.decode("utf-8"))

                        # Skip if we haven't reached the offset yet
                        if commit_count < offset:
                            commit_count += 1
                            # Add parents to continue traversal
                            if "parent" in commit_obj:
                                parent = commit_obj["parent"]
                                if (
                                    parent
                                    and not parent.startswith("ref:")
                                    and len(parent) == 40
                                ):
                                    to_visit.append(parent)
                            continue

                        # Format commit for API
                        commit_info = {
                            "sha": sha,
                            "message": commit_obj.get("message", ""),
                            "author": commit_obj.get("author", "Unknown"),
                            "timestamp": commit_obj.get(
                                "timestamp", 0
                            ),  # JavaScript expects timestamp
                            "date": commit_obj.get(
                                "date", ""
                            ),  # Keep for compatibility
                            "parent": commit_obj.get("parent", ""),
                            "tree": commit_obj.get("tree", ""),
                        }

                        commits_data.append(commit_info)
                        commit_count += 1

                        # Add parent for next iteration
                        if "parent" in commit_obj:
                            parent = commit_obj["parent"]
                            # Skip refs and only add valid SHAs
                            if (
                                parent
                                and not parent.startswith("ref:")
                                and len(parent) == 40
                            ):
                                to_visit.append(parent)

                    except Exception as e:
                        sys.stderr.write(f"Error processing commit {sha}: {e}\n")
                        continue

                return {
                    "commits": commits_data,
                    "total": len(commits_data),
                    "offset": offset,
                    "limit": limit,
                }

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/commit/{sha}")
        async def get_commit_details(sha: str) -> Any:
            """Get details of a specific commit"""
            try:
                obj_type, commit_data = get_object(sha)
                if obj_type != "commit":
                    raise HTTPException(status_code=404, detail="Commit not found")

                commit_obj = json.loads(commit_data.decode("utf-8"))

                return {
                    "sha": sha,
                    "message": commit_obj.get("message", ""),
                    "author": commit_obj.get("author", "Unknown"),
                    "date": commit_obj.get("date", ""),
                    "parent": commit_obj.get("parent", ""),
                    "tree": commit_obj.get("tree", ""),
                }

            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid commit format")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/latest-commit")
        async def get_latest_commit() -> Any:
            """Return basic info about the latest commit (used by frontend)."""
            try:
                # Read HEAD
                try:
                    with open(os.path.join(self.repo_path, ".ugit", "HEAD"), "r") as f:
                        ref = f.read().strip()

                    if ref.startswith("ref: "):
                        ref_path = ref[5:]
                        ref_file = os.path.join(self.repo_path, ".ugit", ref_path)
                        if os.path.exists(ref_file):
                            with open(ref_file, "r") as f:
                                commit_sha = f.read().strip()
                        else:
                            return {"commit": None}
                    else:
                        commit_sha = ref
                except FileNotFoundError:
                    return {"commit": None}

                # Read commit object
                try:
                    obj_type, commit_data = get_object(commit_sha)
                    if obj_type != "commit":
                        return {"commit": None}

                    commit_obj = json.loads(commit_data.decode("utf-8"))
                except Exception:
                    return {"commit": None}

                commit_info = {
                    "sha": commit_sha,
                    "message": commit_obj.get("message", ""),
                    "author": commit_obj.get("author", ""),
                    "timestamp": commit_obj.get("timestamp", 0),
                }

                return {"commit": commit_info}

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def _get_last_commit_for_directory(
        self, dir_path: str, current_commit_sha: str
    ) -> Optional[Dict[str, Any]]:
        """Find the last commit that modified any file in a specific directory"""
        try:
            # Start from current commit and walk backwards
            commit_sha: Optional[str] = current_commit_sha
            visited = set()
            commit_count = 0
            previous_dir_file_shas: Dict[str, str] = {}
            last_commit_with_change = None

            while commit_sha and commit_sha not in visited:
                visited.add(commit_sha)
                commit_count += 1

                try:
                    # Get commit object
                    obj_type, commit_data = get_object(commit_sha)
                    if obj_type != "commit":
                        break

                    commit_obj = json.loads(commit_data.decode("utf-8"))
                    commit_message = commit_obj.get("message", "No message")

                    # Get the tree for this commit
                    tree_sha = commit_obj["tree"]
                    obj_type, tree_data = get_object(tree_sha)
                    if obj_type != "tree":
                        break

                    tree_obj = json.loads(tree_data.decode("utf-8"))

                    # Get current file SHAs for this directory
                    current_dir_file_shas = {}
                    dir_has_files = False

                    for entry in tree_obj:
                        if len(entry) >= 2 and entry[0].startswith(dir_path + "/"):
                            dir_has_files = True
                            current_dir_file_shas[entry[0]] = entry[1]

                    if not dir_has_files:
                        # Directory doesn't exist in this commit
                        if last_commit_with_change:
                            return last_commit_with_change
                        break

                    # Check if this is the first time we're seeing this directory or if any files have changed
                    if not previous_dir_file_shas:
                        # First time seeing this directory
                        last_commit_with_change = {
                            "sha": commit_sha,
                            "message": commit_message,
                            "author": commit_obj.get("author", "Unknown"),
                            "timestamp": commit_obj.get("timestamp", 0),
                        }
                        previous_dir_file_shas = current_dir_file_shas.copy()

                    else:
                        # Check if any file in the directory has changed
                        files_changed = False

                        # Check for new files or changed files
                        for file_path, file_sha in current_dir_file_shas.items():
                            if (
                                file_path not in previous_dir_file_shas
                                or previous_dir_file_shas[file_path] != file_sha
                            ):
                                files_changed = True
                                break

                        # Check for deleted files
                        if not files_changed:
                            for file_path in previous_dir_file_shas:
                                if file_path not in current_dir_file_shas:
                                    files_changed = True
                                    break

                        if files_changed:
                            # Files in directory changed! The previous commit was where it was last modified
                            if last_commit_with_change:
                                return last_commit_with_change
                            break

                    # Update for next iteration
                    previous_dir_file_shas = current_dir_file_shas.copy()
                    last_commit_with_change = {
                        "sha": commit_sha,
                        "message": commit_message,
                        "author": commit_obj.get("author", "Unknown"),
                        "timestamp": commit_obj.get("timestamp", 0),
                    }

                    # Move to parent commit
                    parent = commit_obj.get("parent")
                    if parent and len(parent) == 40:
                        commit_sha = parent
                    else:
                        commit_sha = None

                except Exception as e:
                    sys.stderr.write(
                        f"Error processing commit {commit_sha} for directory {dir_path}: {e}\n"
                    )
                    break

            # If we've exhausted all commits, return the last commit where we found the directory
            if last_commit_with_change:
                return last_commit_with_change

            return None

        except Exception as e:
            sys.stderr.write(
                f"Error in _get_last_commit_for_directory for '{dir_path}': {e}\n"
            )
            return None

    def _get_last_commit_for_file(
        self, file_path: str, current_commit_sha: str
    ) -> Optional[Dict[str, Any]]:
        """Find the last commit that modified a specific file (not just contained it)"""
        try:
            # Start from current commit and walk backwards
            commit_sha: Optional[str] = current_commit_sha
            visited = set()
            commit_count = 0
            previous_file_sha = None
            last_commit_with_change = None

            while commit_sha and commit_sha not in visited:
                visited.add(commit_sha)
                commit_count += 1

                try:
                    # Get commit object
                    obj_type, commit_data = get_object(commit_sha)
                    if obj_type != "commit":
                        break

                    commit_obj = json.loads(commit_data.decode("utf-8"))
                    commit_message = commit_obj.get("message", "No message")

                    # Get the tree for this commit
                    tree_sha = commit_obj["tree"]
                    obj_type, tree_data = get_object(tree_sha)
                    if obj_type != "tree":
                        break

                    tree_obj = json.loads(tree_data.decode("utf-8"))

                    # Check if this file exists in this commit's tree and get its SHA
                    current_file_sha = None
                    file_exists_in_commit = False

                    for entry in tree_obj:
                        if len(entry) >= 2 and entry[0] == file_path:
                            file_exists_in_commit = True
                            current_file_sha = entry[1]
                            break

                    if not file_exists_in_commit:
                        # File doesn't exist in this commit, so the previous commit where we found it was where it was last modified
                        if last_commit_with_change:
                            return last_commit_with_change
                        break

                    # Check if this is the first time we're seeing this file or if the content has changed
                    if previous_file_sha is None:
                        # First time seeing this file, this could be the last modification
                        last_commit_with_change = {
                            "sha": commit_sha,
                            "message": commit_message,
                            "author": commit_obj.get("author", "Unknown"),
                            "timestamp": commit_obj.get("timestamp", 0),
                        }
                        previous_file_sha = current_file_sha

                    elif previous_file_sha != current_file_sha:
                        # File content has changed! The previous commit was where it was last modified
                        # Return the previously stored commit (the one where we last saw the file)
                        if last_commit_with_change:
                            return last_commit_with_change
                        break

                    # Update for next iteration
                    previous_file_sha = current_file_sha
                    last_commit_with_change = {
                        "sha": commit_sha,
                        "message": commit_message,
                        "author": commit_obj.get("author", "Unknown"),
                        "timestamp": commit_obj.get("timestamp", 0),
                    }

                    # Move to parent commit
                    parent = commit_obj.get("parent")
                    if parent and len(parent) == 40:
                        commit_sha = parent
                    else:
                        commit_sha = None

                except Exception as e:
                    sys.stderr.write(f"Error processing commit {commit_sha}: {e}\n")
                    import traceback

                    traceback.print_exc()
                    break

            # If we've exhausted all commits, return the last commit where we found the file
            if last_commit_with_change:
                return last_commit_with_change

            return None

        except Exception as e:
            sys.stderr.write(
                f"Error in _get_last_commit_for_file for '{file_path}': {e}\n"
            )
            import traceback

            traceback.print_exc()
            return None


def create_app(repo_path: str = ".") -> FastAPI:
    """Create and configure the FastAPI application"""
    server = UgitWebServer(repo_path)
    return server.app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
