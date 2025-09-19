"""
Object storage and management for ugit.

This module handles the core object storage functionality including
hashing, storing, and retrieving objects (blobs, trees, commits).
"""

import hashlib
import os
import zlib
from typing import Tuple, Union


def hash_object(data: bytes, type_: str = "blob", write: bool = True) -> str:
    """
    Compute SHA-1 hash of data and optionally store it.
    
    Args:
        data: The raw data to hash
        type_: Object type ('blob', 'tree', 'commit')  
        write: Whether to write the object to disk
        
    Returns:
        SHA-1 hash of the object
        
    Raises:
        ValueError: If type_ is invalid
        RuntimeError: If writing fails
    """
    if type_ not in ("blob", "tree", "commit"):
        raise ValueError(f"Invalid object type: {type_}")
    
    if not isinstance(data, bytes):
        raise ValueError("Data must be bytes")
    
    header = f"{type_} {len(data)}\0".encode()
    full_data = header + data
    sha = hashlib.sha1(full_data).hexdigest()
    
    if write:
        try:
            _write_object(sha, full_data)
        except (IOError, OSError) as e:
            raise RuntimeError(f"Failed to write object {sha}: {e}")
    
    return sha


def _write_object(sha: str, data: bytes) -> None:
    """Write object data to disk with compression."""
    object_dir = f".ugit/objects/{sha[:2]}"
    object_path = f"{object_dir}/{sha[2:]}"
    
    if os.path.exists(object_path):
        return  # Object already exists
    
    os.makedirs(object_dir, exist_ok=True)
    
    # Compress data to save space
    compressed_data = zlib.compress(data)
    
    with open(object_path, "wb") as f:
        f.write(compressed_data)


def get_object(sha: str) -> Tuple[str, bytes]:
    """
    Read object by SHA hash.
    
    Args:
        sha: SHA-1 hash of the object
        
    Returns:
        Tuple of (object_type, content)
        
    Raises:
        FileNotFoundError: If object doesn't exist
        ValueError: If object format is invalid or SHA is invalid
    """
    if len(sha) != 40:
        raise ValueError(f"Invalid SHA length: {len(sha)}")
    
    # Try both old flat structure and new hierarchical structure
    object_paths = [
        f".ugit/objects/{sha}",  # Old format
        f".ugit/objects/{sha[:2]}/{sha[2:]}"  # New format
    ]
    
    for object_path in object_paths:
        if os.path.exists(object_path):
            break
    else:
        raise FileNotFoundError(f"Object {sha} not found")
        
    try:
        with open(object_path, "rb") as f:
            compressed_data = f.read()
        
        # Try to decompress (new format) or use as-is (old format)
        try:
            data = zlib.decompress(compressed_data)
        except zlib.error:
            data = compressed_data  # Old uncompressed format
            
        null_pos = data.index(b'\x00')
        header = data[:null_pos].decode()
        content = data[null_pos+1:]
        
        type_, size = header.split()
        if int(size) != len(content):
            raise ValueError(f"Object {sha} has invalid size")
            
        return type_, content
    except (IOError, OSError) as e:
        raise FileNotFoundError(f"Cannot read object {sha}: {e}")
    except (ValueError, UnicodeDecodeError) as e:
        raise ValueError(f"Invalid object format for {sha}: {e}")


def object_exists(sha: str) -> bool:
    """Check if an object exists in the object store."""
    if len(sha) != 40:
        return False
    
    # Check both old and new formats
    return (os.path.exists(f".ugit/objects/{sha}") or 
            os.path.exists(f".ugit/objects/{sha[:2]}/{sha[2:]}"))