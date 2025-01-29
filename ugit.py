import os
import sys
import hashlib
import json
from datetime import datetime

# Helper: Create .ugit directory structure
def init():
    if os.path.exists(".ugit"):
        print("Already a ugit repository")
        return
    os.mkdir(".ugit")
    os.makedirs(".ugit/objects")  # Blobs, trees, commits
    os.makedirs(".ugit/refs/heads")  # Branches
    with open(".ugit/HEAD", "w") as f:
        f.write("ref: refs/heads/main")
    print("Initialized empty ugit repository")

# Helper: Compute SHA-1 hash of data
def hash_object(data, type_="blob", write=True):
    header = f"{type_} {len(data)}\0".encode()
    full_data = header + data
    sha = hashlib.sha1(full_data).hexdigest()
    if write:
        path = f".ugit/objects/{sha}"
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(full_data)
    return sha

# Helper: Read object by SHA
def get_object(sha):
    with open(f".ugit/objects/{sha}", "rb") as f:
        data = f.read()
    null_pos = data.index(b'\x00')
    header = data[:null_pos].decode()
    content = data[null_pos+1:]
    type_, size = header.split()
    assert int(size) == len(content)
    return type_, content

# ugit add: Stage files
def add(path):
    index = read_index()
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                add(os.path.join(root, file))
        return

    with open(path, "rb") as f:
        data = f.read()
    sha = hash_object(data, "blob")
    index[path] = sha  # Update index with new SHA
    write_index(index)
    print(f"Staged {path} ({sha[:6]})")

# Create tree object from current workspace
def write_tree():
    index = read_index()
    tree_entries = []
    for path, sha in index.items():
        tree_entries.append((path, sha))
    tree_data = json.dumps(tree_entries).encode()
    return hash_object(tree_data, "tree")

# ugit commit: Save snapshot
def commit(message, parent=None):
    tree_sha = write_tree()
    commit_data = {
        "tree": tree_sha,
        "parent": parent,
        "author": "Your Name <you@example.com>",
        "timestamp": datetime.now().isoformat(),
        "message": message
    }
    commit_bytes = json.dumps(commit_data).encode()
    commit_sha = hash_object(commit_bytes, "commit")
    # Update current branch (simplified: always "main")
    with open(".ugit/refs/heads/main", "w") as f:
        f.write(commit_sha)
    print(f"Committed {commit_sha[:6]}")

# ugit log: Show commit history
def log():
    current = open(".ugit/refs/heads/main").read().strip()
    while current:
        type_, data = get_object(current)
        assert type_ == "commit"
        commit = json.loads(data.decode())
        print(f"commit {current}")
        print(f"Author: {commit['author']}")
        print(f"Date:   {commit['timestamp']}")
        print(f"\n    {commit['message']}\n")
        current = commit.get("parent")

# ugit checkout: Restore files from a commit (simplified)
def checkout(commit_sha):
    type_, data = get_object(commit_sha)
    assert type_ == "commit"
    commit = json.loads(data.decode())
    tree_sha = commit["tree"]
    type_, tree_data = get_object(tree_sha)
    tree = json.loads(tree_data.decode())
    
    # Clear existing files (except .ugit and ugit.py)
    for root, dirs, files in os.walk(".", topdown=False):
        for file in files:
            path = os.path.relpath(os.path.join(root, file))
            if path == "ugit.py" or path.startswith(".ugit"):
                continue
            os.remove(path)
        for dir in dirs:
            dir_path = os.path.relpath(os.path.join(root, dir))
            if dir == ".ugit" or dir_path.startswith(".ugit"):
                continue
            if not os.listdir(dir_path):  # Delete empty dirs
                os.rmdir(dir_path)
    
    # Write files from the tree
    for path, sha in tree:
        dirname = os.path.dirname(path)
        if dirname:  # Only create directories if needed
            os.makedirs(dirname, exist_ok=True)
        type_, content = get_object(sha)
        with open(path, "wb") as f:
            f.write(content)
    print(f"Checked out commit {commit_sha[:6]}")


def read_index():
    index = {}
    if os.path.exists(".ugit/index"):
        with open(".ugit/index", "r") as f:
            for line in f:
                sha, path = line.strip().split(" ", 1)
                index[path] = sha
    return index

def write_index(index):
    with open(".ugit/index", "w") as f:
        for path, sha in index.items():
            f.write(f"{sha} {path}\n")

def status():
    index = read_index()
    head_sha = open(".ugit/refs/heads/main").read().strip() if os.path.exists(".ugit/refs/heads/main") else None
    tracked_files = set(index.keys())

    # Tracked files modified in workspace
    modified = []
    for path in tracked_files:
        if not os.path.exists(path):
            print(f"Deleted: {path}")  # Handle deletions
        else:
            with open(path, "rb") as f:
                data = f.read()
            current_sha = hash_object(data, "blob", write=False)
            if current_sha != index[path]:
                modified.append(path)

    # Untracked files
    untracked = []
    for root, dirs, files in os.walk("."):
        if ".ugit" in dirs:
            dirs.remove(".ugit")
        for file in files:
            path = os.path.relpath(os.path.join(root, file))
            if path not in tracked_files:
                untracked.append(path)

    print("\nChanges to be committed:")
    for path in tracked_files:
        if path in modified:
            print(f"  modified: {path}")
    print("\nUntracked files:")
    for path in untracked:
        print(f"  {path}")


# CLI Interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ugit <command> [args]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "init":
        init()
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Usage: ugit add <file>")
            sys.exit(1)
        add(sys.argv[2])
    elif cmd == "commit":
        if len(sys.argv) < 3 or "-m" not in sys.argv:
            print("Usage: ugit commit -m 'message'")
            sys.exit(1)
        message = sys.argv[sys.argv.index("-m") + 1]
        commit(message)
    elif cmd == "log":
        log()
    elif cmd == "checkout":
        if len(sys.argv) < 3:
            print("Usage: ugit checkout <commit>")
            sys.exit(1)
        checkout(sys.argv[2])
    elif cmd == "status":
        status()
    else:
        print(f"Unknown command: {cmd}")