"""
FastAPI web server for ugit repository viewer.
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.responses import FileResponse

from ugit.core.repository import Repository
from ugit.core.objects import get_object
from ugit.commands import log, diff


class UgitWebServer:
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self.repo = Repository(self.repo_path)
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="ugit Repository Viewer",
            description="Web-based repository browser for ugit",
            version="1.0.0"
        )
        
        # Setup static files and templates
        web_dir = Path(__file__).parent
        self.app.mount("/static", StaticFiles(directory=str(web_dir / "static")), name="static")
        self.templates = Jinja2Templates(directory=str(web_dir / "templates"))
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all web routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            """Main repository view"""
            return self.templates.TemplateResponse("index.html", {
                "request": request,
                "repo_name": os.path.basename(self.repo_path),
                "repo_path": self.repo_path
            })
        
        @self.app.get("/api/files")
        async def list_files(path: str = "", commit: str = "HEAD"):
            """List files and directories from the committed tree (like GitHub)"""
            try:
                print(f"DEBUG: Requesting files for path='{path}', commit='{commit}'")
                
                # Get the current commit SHA
                if commit == "HEAD":
                    try:
                        head_file = os.path.join(self.repo_path, '.ugit', 'HEAD')
                        print(f"DEBUG: Reading HEAD file: {head_file}")
                        
                        with open(head_file, 'r') as f:
                            ref = f.read().strip()
                        print(f"DEBUG: HEAD content: {ref}")
                            
                        if ref.startswith('ref: '):
                            ref_path = ref[5:]
                            ref_file = os.path.join(self.repo_path, '.ugit', ref_path)
                            print(f"DEBUG: Reading ref file: {ref_file}")
                            if os.path.exists(ref_file):
                                with open(ref_file, 'r') as f:
                                    commit_sha = f.read().strip()
                                print(f"DEBUG: Found commit SHA: {commit_sha}")
                            else:
                                print("DEBUG: No commits found - ref file doesn't exist")
                                return {"files": [], "commit": None, "path": path}
                        else:
                            commit_sha = ref
                            print(f"DEBUG: Direct SHA reference: {commit_sha}")
                    except FileNotFoundError as e:
                        print(f"DEBUG: FileNotFoundError: {e}")
                        return {"files": [], "commit": None, "path": path}
                else:
                    commit_sha = commit
                    print(f"DEBUG: Using provided commit: {commit_sha}")
                
                # Get the commit object
                try:
                    print(f"DEBUG: Getting commit object for SHA: {commit_sha}")
                    obj_type, commit_data = get_object(commit_sha)
                    print(f"DEBUG: Object type: {obj_type}")
                    if obj_type != 'commit':
                        print(f"DEBUG: Invalid object type, expected 'commit', got '{obj_type}'")
                        return {"files": [], "commit": None, "path": path}
                    
                    commit_obj = json.loads(commit_data.decode('utf-8'))
                    tree_sha = commit_obj['tree']
                    print(f"DEBUG: Tree SHA: {tree_sha}")
                except Exception as e:
                    print(f"DEBUG: Error reading commit object: {e}")
                    return {"files": [], "commit": None, "path": path}
                
                # Get the tree contents (ugit uses flat structure with full paths)
                try:
                    print(f"DEBUG: Reading tree contents from SHA: {tree_sha}")
                    obj_type, tree_data = get_object(tree_sha)
                    if obj_type != 'tree':
                        print(f"DEBUG: Object is not a tree: {obj_type}")
                        return {"files": [], "commit": None, "path": path}
                    
                    tree_obj = json.loads(tree_data.decode('utf-8'))
                    print(f"DEBUG: Tree object loaded successfully, entries: {len(tree_obj)}")
                    print(f"DEBUG: Sample entries: {tree_obj[:3] if tree_obj else 'None'}")
                except Exception as e:
                    print(f"DEBUG: Error reading tree: {e}")
                    return {"files": [], "commit": None, "path": path}
                
                # ugit stores all files with full paths in a flat tree structure
                # We need to create virtual directories from these paths
                files = []
                directories = set()
                
                # Normalize the requested path
                current_path = path.rstrip('/') if path else ""
                current_depth = len(current_path.split('/')) if current_path else 0
                
                print(f"DEBUG: Current path: '{current_path}', depth: {current_depth}")
                
                # Process all entries in the flat tree
                for entry in tree_obj:
                    if len(entry) >= 2:
                        full_file_path = entry[0]  # This is the full path like 'src/utils.py'
                        file_sha = entry[1]
                        
                        print(f"DEBUG: Processing entry: {full_file_path}")
                        
                        # Check if this file belongs to the current path
                        if current_path:
                            if not full_file_path.startswith(current_path + '/'):
                                continue  # Not in this directory
                            # Get the relative path from current directory
                            relative_path = full_file_path[len(current_path) + 1:]
                        else:
                            relative_path = full_file_path
                        
                        print(f"DEBUG: Relative path: '{relative_path}'")
                        
                        # Split the path to see if it's directly in current directory
                        path_parts = relative_path.split('/')
                        
                        if len(path_parts) == 1:
                            # File is directly in current directory
                            file_name = path_parts[0]
                            
                            # Get file type and size
                            try:
                                obj_type, _ = get_object(file_sha)
                                file_type = obj_type
                            except:
                                file_type = 'blob'
                            
                            file_info = {
                                "name": file_name,
                                "type": file_type,
                                "sha": file_sha,
                                "size": None
                            }
                            
                            # Get size for blob files
                            if file_type == 'blob':
                                try:
                                    blob_type, blob_data = get_object(file_sha)
                                    if blob_type == 'blob':
                                        file_info['size'] = len(blob_data)
                                except:
                                    pass
                            
                            # Get last commit info for this specific file
                            try:
                                last_commit_info = self._get_last_commit_for_file(full_file_path, commit_sha)
                                if last_commit_info:
                                    file_info['commit_message'] = last_commit_info['message']
                                    file_info['commit_date'] = last_commit_info['timestamp']
                                    file_info['commit_sha'] = last_commit_info['sha']
                                    print(f"DEBUG: Got commit info for {full_file_path}: {last_commit_info['message']}")
                                else:
                                    print(f"DEBUG: No commit info found for {full_file_path}")
                            except Exception as e:
                                print(f"DEBUG: Error getting commit info for {full_file_path}: {e}")
                                import traceback
                                traceback.print_exc()
                            
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
                                    "size": None
                                }
                                
                                # Find the most recent commit that modified any file in this directory
                                try:
                                    # Look for any file that starts with subdir_name/ in the commit history
                                    dir_commit_info = self._get_last_commit_for_directory(subdir_name, commit_sha)
                                    if dir_commit_info:
                                        subdir_info['commit_message'] = dir_commit_info['message']
                                        subdir_info['commit_date'] = dir_commit_info['timestamp']
                                        subdir_info['commit_sha'] = dir_commit_info['sha']
                                        print(f"DEBUG: Got directory commit info for {subdir_name}: {dir_commit_info['message']}")
                                    else:
                                        # Fallback to current commit
                                        subdir_info['commit_message'] = commit_obj.get('message', 'No message')
                                        subdir_info['commit_date'] = commit_obj.get('timestamp', 0)
                                        subdir_info['commit_sha'] = commit_sha
                                        print(f"DEBUG: Using fallback commit info for directory {subdir_name}")
                                except Exception as e:
                                    print(f"DEBUG: Error getting directory commit info for {subdir_name}: {e}")
                                    # Fallback to current commit
                                    subdir_info['commit_message'] = commit_obj.get('message', 'No message')
                                    subdir_info['commit_date'] = commit_obj.get('timestamp', 0)
                                    subdir_info['commit_sha'] = commit_sha
                                    
                                files.append(subdir_info)
                
                # Sort: directories first, then files
                files.sort(key=lambda x: (x["type"] != "tree", x["name"].lower()))
                
                print(f"DEBUG: Final files list: {[f['name'] for f in files]}")
                
                # Get commit info for latest commit display
                commit_info = {
                    "sha": commit_sha,
                    "message": commit_obj.get('message', ''),
                    "author": commit_obj.get('author', ''),
                    "timestamp": commit_obj.get('timestamp', 0)
                }
                
                return {
                    "files": files, 
                    "commit": commit_info,
                    "path": path
                }
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/file")
        async def get_file_content(path: str, commit: str = "HEAD"):
            """Get content of a specific file from the committed tree"""
            try:
                print(f"DEBUG: Requesting file content for path='{path}', commit='{commit}'")
                
                # Get the current commit SHA
                if commit == "HEAD":
                    try:
                        with open(os.path.join(self.repo_path, '.ugit', 'HEAD'), 'r') as f:
                            ref = f.read().strip()
                            
                        if ref.startswith('ref: '):
                            ref_path = ref[5:]
                            ref_file = os.path.join(self.repo_path, '.ugit', ref_path)
                            if os.path.exists(ref_file):
                                with open(ref_file, 'r') as f:
                                    commit_sha = f.read().strip()
                            else:
                                raise HTTPException(status_code=404, detail="Repository has no commits")
                        else:
                            commit_sha = ref
                    except FileNotFoundError:
                        raise HTTPException(status_code=404, detail="Repository has no commits")
                else:
                    commit_sha = commit
                
                # Get the commit object and tree
                try:
                    obj_type, commit_data = get_object(commit_sha)
                    if obj_type != 'commit':
                        raise HTTPException(status_code=404, detail="Invalid commit")
                    
                    commit_obj = json.loads(commit_data.decode('utf-8'))
                    tree_sha = commit_obj['tree']
                    print(f"DEBUG: Tree SHA: {tree_sha}")
                except Exception:
                    raise HTTPException(status_code=404, detail="Invalid commit")
                
                # Get the tree contents (ugit uses flat structure with full paths)
                try:
                    obj_type, tree_data = get_object(tree_sha)
                    if obj_type != 'tree':
                        raise HTTPException(status_code=404, detail="Invalid tree")
                    
                    tree_obj = json.loads(tree_data.decode('utf-8'))
                    print(f"DEBUG: Tree loaded, looking for file: {path}")
                    print(f"DEBUG: Available files: {[entry[0] for entry in tree_obj if len(entry) >= 2]}")
                except Exception:
                    raise HTTPException(status_code=404, detail="Invalid tree")
                
                # Find the file in the flat tree structure
                file_sha = None
                for entry in tree_obj:
                    if len(entry) >= 2 and entry[0] == path:
                        file_sha = entry[1]
                        print(f"DEBUG: Found file with SHA: {file_sha}")
                        break
                
                if not file_sha:
                    print(f"DEBUG: File not found in tree")
                    raise HTTPException(status_code=404, detail="File not found")
                
                # Get the file content
                try:
                    obj_type, file_data = get_object(file_sha)
                    if obj_type != 'blob':
                        print(f"DEBUG: Object is not a blob: {obj_type}")
                        raise HTTPException(status_code=404, detail="Not a file")
                    print(f"DEBUG: Successfully loaded file content, size: {len(file_data)}")
                except Exception as e:
                    print(f"DEBUG: Error loading file content: {e}")
                    raise HTTPException(status_code=404, detail="Error reading file")
                
                # Check if file is binary
                is_binary = b'\x00' in file_data[:1024]
                
                if is_binary:
                    return {
                        "path": path,
                        "type": "binary",
                        "size": len(file_data),
                        "content": None,
                        "commit_sha": commit_sha
                    }
                
                # Try to decode text file
                try:
                    content = file_data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        content = file_data.decode('latin1')
                    except UnicodeDecodeError:
                        return {
                            "path": path,
                            "type": "binary",
                            "size": len(file_data),
                            "content": None,
                            "commit_sha": commit_sha
                        }
                
                return {
                    "path": path,
                    "type": "text",
                    "size": len(file_data),
                    "content": content,
                    "lines": len(content.split('\n')),
                    "commit_sha": commit_sha
                }
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/commits")
        async def get_commits(limit: int = 50, offset: int = 0):
            """Get commit history"""
            try:
                # Use ugit's log command to get commits
                commits_data = []
                commit_count = 0
                
                # Get current HEAD
                try:
                    with open(os.path.join(self.repo_path, '.ugit', 'HEAD'), 'r') as f:
                        ref = f.read().strip()
                        
                    if ref.startswith('ref: '):
                        ref_path = ref[5:]  # Remove 'ref: ' prefix
                        ref_file = os.path.join(self.repo_path, '.ugit', ref_path)
                        if os.path.exists(ref_file):
                            with open(ref_file, 'r') as f:
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
                to_visit = [current_sha]
                
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
                        if obj_type != 'commit':
                            continue
                            
                        # Parse commit object (JSON format)
                        commit_obj = json.loads(commit_data.decode('utf-8'))
                        
                        # Skip if we haven't reached the offset yet
                        if commit_count < offset:
                            commit_count += 1
                            # Add parents to continue traversal
                            if 'parent' in commit_obj:
                                parent = commit_obj['parent']
                                if parent and not parent.startswith('ref:') and len(parent) == 40:
                                    to_visit.append(parent)
                            continue
                        
                        # Format commit for API
                        commit_info = {
                            "sha": sha,
                            "message": commit_obj.get('message', ''),
                            "author": commit_obj.get('author', 'Unknown'),
                            "timestamp": commit_obj.get('timestamp', 0),  # JavaScript expects timestamp
                            "date": commit_obj.get('date', ''),  # Keep for compatibility
                            "parent": commit_obj.get('parent', ''),
                            "tree": commit_obj.get('tree', '')
                        }
                        
                        commits_data.append(commit_info)
                        commit_count += 1
                        
                        # Add parent for next iteration
                        if 'parent' in commit_obj:
                            parent = commit_obj['parent']
                            # Skip refs and only add valid SHAs
                            if parent and not parent.startswith('ref:') and len(parent) == 40:
                                to_visit.append(parent)
                            
                    except Exception as e:
                        print(f"Error processing commit {sha}: {e}")
                        continue
                
                return {
                    "commits": commits_data,
                    "total": len(commits_data),
                    "offset": offset,
                    "limit": limit
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/commit/{sha}")
        async def get_commit_details(sha: str):
            """Get details of a specific commit"""
            try:
                obj_type, commit_data = get_object(sha)
                if obj_type != 'commit':
                    raise HTTPException(status_code=404, detail="Commit not found")
                
                commit_obj = json.loads(commit_data.decode('utf-8'))
                
                return {
                    "sha": sha,
                    "message": commit_obj.get('message', ''),
                    "author": commit_obj.get('author', 'Unknown'),
                    "date": commit_obj.get('date', ''),
                    "parent": commit_obj.get('parent', ''),
                    "tree": commit_obj.get('tree', '')
                }
                
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid commit format")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def _get_last_commit_for_directory(self, dir_path: str, current_commit_sha: str) -> Optional[Dict[str, Any]]:
        """Find the last commit that modified any file in a specific directory"""
        try:
            print(f"DEBUG: Looking for last commit for directory: '{dir_path}' starting from {current_commit_sha}")
            
            # Start from current commit and walk backwards
            commit_sha = current_commit_sha
            visited = set()
            commit_count = 0
            previous_dir_file_shas = {}
            last_commit_with_change = None
            
            while commit_sha and commit_sha not in visited and commit_count < 20:  # Limit to prevent infinite loops
                visited.add(commit_sha)
                commit_count += 1
                
                try:
                    print(f"DEBUG: Checking commit {commit_sha} for directory {dir_path} (#{commit_count})")
                    
                    # Get commit object
                    obj_type, commit_data = get_object(commit_sha)
                    if obj_type != 'commit':
                        break
                        
                    commit_obj = json.loads(commit_data.decode('utf-8'))
                    commit_message = commit_obj.get('message', 'No message')
                    
                    # Get the tree for this commit
                    tree_sha = commit_obj['tree']
                    obj_type, tree_data = get_object(tree_sha)
                    if obj_type != 'tree':
                        break
                        
                    tree_obj = json.loads(tree_data.decode('utf-8'))
                    
                    # Get current file SHAs for this directory
                    current_dir_file_shas = {}
                    dir_has_files = False
                    
                    for entry in tree_obj:
                        if len(entry) >= 2 and entry[0].startswith(dir_path + '/'):
                            dir_has_files = True
                            current_dir_file_shas[entry[0]] = entry[1]
                            print(f"DEBUG: Found file in directory '{dir_path}': {entry[0]} ({entry[1][:7]})")
                    
                    if not dir_has_files:
                        # Directory doesn't exist in this commit
                        if last_commit_with_change:
                            print(f"DEBUG: Directory '{dir_path}' not found, returning last change: {last_commit_with_change['sha']}")
                            return last_commit_with_change
                        break
                    
                    # Check if this is the first time we're seeing this directory or if any files have changed
                    if not previous_dir_file_shas:
                        # First time seeing this directory
                        last_commit_with_change = {
                            'sha': commit_sha,
                            'message': commit_message,
                            'author': commit_obj.get('author', 'Unknown'),
                            'timestamp': commit_obj.get('timestamp', 0)
                        }
                        previous_dir_file_shas = current_dir_file_shas.copy()
                        print(f"DEBUG: First occurrence of directory '{dir_path}', marking commit {commit_sha}")
                        
                    else:
                        # Check if any file in the directory has changed
                        files_changed = False
                        
                        # Check for new files or changed files
                        for file_path, file_sha in current_dir_file_shas.items():
                            if file_path not in previous_dir_file_shas or previous_dir_file_shas[file_path] != file_sha:
                                files_changed = True
                                print(f"DEBUG: File changed in directory '{dir_path}': {file_path}")
                                break
                        
                        # Check for deleted files
                        if not files_changed:
                            for file_path in previous_dir_file_shas:
                                if file_path not in current_dir_file_shas:
                                    files_changed = True
                                    print(f"DEBUG: File deleted from directory '{dir_path}': {file_path}")
                                    break
                        
                        if files_changed:
                            # Files in directory changed! The previous commit was where it was last modified
                            print(f"DEBUG: Directory '{dir_path}' content changed!")
                            if last_commit_with_change:
                                return last_commit_with_change
                            break
                        else:
                            print(f"DEBUG: Directory '{dir_path}' content unchanged")
                    
                    # Update for next iteration
                    previous_dir_file_shas = current_dir_file_shas.copy()
                    last_commit_with_change = {
                        'sha': commit_sha,
                        'message': commit_message,
                        'author': commit_obj.get('author', 'Unknown'),
                        'timestamp': commit_obj.get('timestamp', 0)
                    }
                    
                    # Move to parent commit
                    parent = commit_obj.get('parent')
                    commit_sha = parent
                        
                except Exception as e:
                    print(f"DEBUG: Error processing commit {commit_sha} for directory {dir_path}: {e}")
                    break
            
            # If we've exhausted all commits, return the last commit where we found the directory
            if last_commit_with_change:
                print(f"DEBUG: Reached end of commit history, returning {last_commit_with_change['sha']} for directory '{dir_path}'")
                return last_commit_with_change
            
            print(f"DEBUG: No commit found for directory '{dir_path}' after checking {commit_count} commits")
            return None
            
        except Exception as e:
            print(f"DEBUG: Error in _get_last_commit_for_directory for '{dir_path}': {e}")
            return None

    def _get_last_commit_for_file(self, file_path: str, current_commit_sha: str) -> Optional[Dict[str, Any]]:
        """Find the last commit that modified a specific file (not just contained it)"""
        try:
            print(f"DEBUG: Looking for last commit that MODIFIED file: '{file_path}' starting from {current_commit_sha}")
            
            # Start from current commit and walk backwards
            commit_sha = current_commit_sha
            visited = set()
            commit_count = 0
            previous_file_sha = None
            last_commit_with_change = None
            
            while commit_sha and commit_sha not in visited and commit_count < 20:  # Limit to prevent infinite loops
                visited.add(commit_sha)
                commit_count += 1
                
                try:
                    print(f"DEBUG: Checking commit {commit_sha} (#{commit_count})")
                    
                    # Get commit object
                    obj_type, commit_data = get_object(commit_sha)
                    if obj_type != 'commit':
                        print(f"DEBUG: Object {commit_sha} is not a commit: {obj_type}")
                        break
                        
                    commit_obj = json.loads(commit_data.decode('utf-8'))
                    commit_message = commit_obj.get('message', 'No message')
                    print(f"DEBUG: Commit message: {commit_message}")
                    
                    # Get the tree for this commit
                    tree_sha = commit_obj['tree']
                    obj_type, tree_data = get_object(tree_sha)
                    if obj_type != 'tree':
                        print(f"DEBUG: Tree {tree_sha} is not a tree: {obj_type}")
                        break
                        
                    tree_obj = json.loads(tree_data.decode('utf-8'))
                    
                    # Check if this file exists in this commit's tree and get its SHA
                    current_file_sha = None
                    file_exists_in_commit = False
                    
                    for entry in tree_obj:
                        if len(entry) >= 2 and entry[0] == file_path:
                            file_exists_in_commit = True
                            current_file_sha = entry[1]
                            print(f"DEBUG: Found file '{file_path}' in commit {commit_sha} with SHA {current_file_sha}")
                            break
                    
                    if not file_exists_in_commit:
                        print(f"DEBUG: File '{file_path}' not found in commit {commit_sha}")
                        # File doesn't exist in this commit, so the previous commit where we found it was where it was last modified
                        if last_commit_with_change:
                            print(f"DEBUG: File was added/modified in commit {last_commit_with_change['sha']}")
                            return last_commit_with_change
                        break
                    
                    # Check if this is the first time we're seeing this file or if the content has changed
                    if previous_file_sha is None:
                        # First time seeing this file, this could be the last modification
                        last_commit_with_change = {
                            'sha': commit_sha,
                            'message': commit_message,
                            'author': commit_obj.get('author', 'Unknown'),
                            'timestamp': commit_obj.get('timestamp', 0)
                        }
                        previous_file_sha = current_file_sha
                        print(f"DEBUG: First occurrence of file, marking commit {commit_sha}")
                        
                    elif previous_file_sha != current_file_sha:
                        # File content has changed! The previous commit was where it was last modified
                        print(f"DEBUG: File content changed! Previous SHA: {previous_file_sha}, Current SHA: {current_file_sha}")
                        print(f"DEBUG: File was last modified in the previous commit we checked")
                        # Return the previously stored commit (the one where we last saw the file)
                        if last_commit_with_change:
                            return last_commit_with_change
                        break
                    else:
                        print(f"DEBUG: File content unchanged (SHA: {current_file_sha})")
                    
                    # Update for next iteration
                    previous_file_sha = current_file_sha
                    last_commit_with_change = {
                        'sha': commit_sha,
                        'message': commit_message,
                        'author': commit_obj.get('author', 'Unknown'),
                        'timestamp': commit_obj.get('timestamp', 0)
                    }
                    
                    # Move to parent commit
                    parent = commit_obj.get('parent')
                    if parent:
                        print(f"DEBUG: Moving to parent commit: {parent}")
                    else:
                        print(f"DEBUG: No parent commit found, this is the root")
                    commit_sha = parent
                        
                except Exception as e:
                    print(f"DEBUG: Error processing commit {commit_sha}: {e}")
                    import traceback
                    traceback.print_exc()
                    break
            
            # If we've exhausted all commits, return the last commit where we found the file
            if last_commit_with_change:
                print(f"DEBUG: Reached end of commit history, returning {last_commit_with_change['sha']}")
                return last_commit_with_change
            
            print(f"DEBUG: No commit found for file '{file_path}' after checking {commit_count} commits")
            return None
            
        except Exception as e:
            print(f"DEBUG: Error in _get_last_commit_for_file for '{file_path}': {e}")
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