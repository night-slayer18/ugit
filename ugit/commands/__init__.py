"""
Command implementations for ugit.
"""

from .add import add
from .alias import alias
from .archive import archive
from .bisect import bisect
from .blame import blame
from .branch import branch
from .checkout import checkout
from .cherry_pick import cherry_pick
from .clone import clone
from .commit import commit
from .config import config
from .diff import diff
from .fetch import fetch
from .fsck import fsck
from .gc import gc
from .gpg import (
    has_gpg,
    sign_commit,
    sign_tag,
    verify_signature,
)
from .grep import grep
from .init import init
from .log import log
from .merge import merge
from .pack import pack_objects, unpack_objects
from .pull import pull
from .push import push
from .rebase import rebase
from .reflog import reflog
from .remote import remote
from .reset import reset, unstage
from .serve import serve
from .shallow_clone import shallow_clone
from .stash import stash, stash_apply, stash_drop, stash_list, stash_pop
from .stats import stats
from .status import status
from .tag import tag
from .worktree import worktree

__all__ = [
    "init",
    "add",
    "commit",
    "config",
    "log",
    "checkout",
    "status",
    "diff",
    "branch",
    "reset",
    "unstage",
    "merge",
    "serve",
    "stash",
    "stash_apply",
    "stash_drop",
    "stash_list",
    "stash_pop",
    "clone",
    "remote",
    "fetch",
    "pull",
    "push",
    "tag",
    "reflog",
    "blame",
    "cherry_pick",
    "grep",
    "archive",
    "alias",
    "stats",
    "bisect",
    "rebase",
    "fsck",
    "gc",
    "worktree",
    "shallow_clone",
    "gpg",
    "sign_commit",
    "sign_tag",
    "verify_signature",
    "has_gpg",
    "pack_objects",
    "unpack_objects",
]
