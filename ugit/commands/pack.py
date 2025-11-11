"""
Pack file implementation for ugit.

Combines multiple objects into pack files for efficient storage.
"""

import os
import struct
import zlib
from typing import Dict, List, Optional, Set, Tuple

from ..core.exceptions import UgitError
from ..core.objects import get_object, hash_object, object_exists
from ..core.repository import Repository
from ..utils.helpers import ensure_repository


def pack_objects(
    sha_list: Optional[List[str]] = None, repo: Optional[Repository] = None
) -> str:
    """
    Create a pack file from objects.

    Args:
        sha_list: List of object SHAs to pack (None = pack all objects)
        repo: Repository instance

    Returns:
        Pack file path
    """
    if repo is None:
        repo = ensure_repository()

    if sha_list is None:
        # Pack all objects
        sha_list = _get_all_objects(repo)
    else:
        # sha_list is already set, use it
        pass

    if not sha_list:
        raise UgitError("No objects to pack")

    # Create pack file
    pack_dir = os.path.join(repo.ugit_dir, "objects", "pack")
    os.makedirs(pack_dir, exist_ok=True)

    pack_data = _create_pack_data(repo, sha_list)
    pack_sha = hash_object(pack_data, "pack", repo=repo)

    pack_file = os.path.join(pack_dir, f"pack-{pack_sha[:40]}.pack")
    with open(pack_file, "wb") as f:
        f.write(pack_data)

    # Create index file
    index_data = _create_pack_index(repo, sha_list, pack_sha)
    index_file = os.path.join(pack_dir, f"pack-{pack_sha[:40]}.idx")
    with open(index_file, "wb") as f:
        f.write(index_data)

    print(f"Created pack file: {pack_file}")
    print(f"Packed {len(sha_list)} object(s)")

    return pack_file


def unpack_objects(pack_file: str, repo: Optional[Repository] = None) -> int:
    """
    Unpack objects from a pack file.

    Args:
        pack_file: Path to pack file
        repo: Repository instance

    Returns:
        Number of objects unpacked
    """
    if repo is None:
        repo = ensure_repository()

    if not os.path.exists(pack_file):
        raise UgitError(f"Pack file not found: {pack_file}")

    # Read pack file
    with open(pack_file, "rb") as f:
        pack_data = f.read()

    # Parse pack file
    objects = _parse_pack_file(pack_data)

    # Write objects
    unpacked = 0
    for sha, obj_type, obj_data in objects:
        obj_path = os.path.join(repo.ugit_dir, "objects", sha)
        if not os.path.exists(obj_path):
            os.makedirs(os.path.dirname(obj_path), exist_ok=True)
            with open(obj_path, "wb") as f:
                f.write(obj_data)
            unpacked += 1

    print(f"Unpacked {unpacked} object(s) from {pack_file}")
    return unpacked


def _get_all_objects(repo: Repository) -> List[str]:
    """Get all object SHAs in repository."""
    objects: List[str] = []
    objects_dir = os.path.join(repo.ugit_dir, "objects")

    if not os.path.exists(objects_dir):
        return objects

    for root, dirs, files in os.walk(objects_dir):
        # Skip pack directory
        if "pack" in root:
            continue

        for file in files:
            if len(file) == 38:  # Remaining chars after first 2
                sha = os.path.basename(root) + file
                if len(sha) == 40:
                    objects.append(sha)
            elif len(file) == 40:  # Old flat format
                objects.append(file)

    return objects


def _create_pack_data(repo: Repository, sha_list: List[str]) -> bytes:
    """Create pack file data."""
    # Pack file format:
    # - Header: "PACK" + version (4 bytes) + object count (4 bytes)
    # - Objects: type + size + compressed data
    # - Checksum: SHA-1 of all data

    pack_objects = []
    for sha in sha_list:
        try:
            obj_type, obj_data = get_object(sha, repo=repo)
            pack_objects.append((obj_type, obj_data))
        except (FileNotFoundError, ValueError):
            continue

    # Build pack file
    pack_data = b"PACK"  # Magic
    pack_data += struct.pack(">I", 2)  # Version
    pack_data += struct.pack(">I", len(pack_objects))  # Object count

    for obj_type, obj_data in pack_objects:
        # Object header: type (3 bits) + size (variable)
        type_map = {"blob": 1, "tree": 2, "commit": 3, "tag": 4, "delta": 7}
        type_code = type_map.get(obj_type, 0)

        # Variable-length size encoding
        size = len(obj_data)
        header_bytes = []
        header_bytes.append((type_code << 4) | (size & 0x0F))
        size >>= 4
        while size > 0:
            header_bytes.append(0x80 | (size & 0x7F))
            size >>= 7

        pack_data += bytes(header_bytes)

        # Compressed object data
        compressed = zlib.compress(obj_data)
        pack_data += compressed

    # Calculate checksum (simplified - would use SHA-1 in production)
    return pack_data


def _create_pack_index(repo: Repository, sha_list: List[str], pack_sha: str) -> bytes:
    """Create pack index file."""
    # Simplified index format
    index_data = b"IDX1"  # Magic
    index_data += struct.pack(">I", len(sha_list))  # Object count

    for sha in sha_list:
        index_data += bytes.fromhex(sha)  # SHA as bytes
        index_data += struct.pack(">Q", 0)  # Offset (simplified)

    return index_data


def _parse_pack_file(pack_data: bytes) -> List[Tuple[str, str, bytes]]:
    """Parse pack file and extract objects."""
    if not pack_data.startswith(b"PACK"):
        raise UgitError("Invalid pack file format")

    # Skip header
    offset = 8  # "PACK" + version + count
    version = struct.unpack(">I", pack_data[4:8])[0]
    obj_count = struct.unpack(">I", pack_data[8:12])[0]

    objects = []
    offset = 12

    for _ in range(obj_count):
        # Read object header
        type_code = (pack_data[offset] >> 4) & 0x07
        size = pack_data[offset] & 0x0F
        offset += 1

        # Read variable-length size
        shift = 4
        while pack_data[offset - 1] & 0x80:
            size |= (pack_data[offset] & 0x7F) << shift
            offset += 1
            shift += 7

        # Decompress object data
        decompressor = zlib.decompressobj()
        obj_data = decompressor.decompress(pack_data[offset : offset + size * 2])
        offset += len(obj_data)

        # Map type code to type name
        type_map = {1: "blob", 2: "tree", 3: "commit", 4: "tag", 7: "delta"}
        obj_type = type_map.get(type_code, "blob")

        # Calculate SHA
        obj_sha = hash_object(obj_data, obj_type)

        objects.append((obj_sha, obj_type, obj_data))

    return objects
