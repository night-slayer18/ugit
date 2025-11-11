#!/usr/bin/env python3
"""
Command-line interface for ugit.
"""

import argparse
import sys
from typing import List, Optional

from .commands import (
    add,
    alias,
    archive,
    bisect,
    blame,
    branch,
    checkout,
    cherry_pick,
    clone,
    commit,
    config,
    diff,
    fetch,
    fsck,
    gc,
    gpg,
    grep,
    init,
    log,
    merge,
    pack,
    pull,
    push,
    rebase,
    reflog,
    remote,
    reset,
    serve,
    shallow_clone,
    stash,
    stash_apply,
    stash_drop,
    stash_list,
    stash_pop,
    stats,
    status,
    tag,
    worktree,
)
from .core.exceptions import UgitError


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for ugit CLI."""
    parser = argparse.ArgumentParser(
        prog="ugit",
        description="A minimal Git implementation in Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ugit init                     Initialize a new repository
  ugit add file.txt             Add file to staging area
  ugit add .                    Add all files to staging area
  ugit commit -m "message"      Create a commit
  ugit status                   Show repository status
  ugit log                      Show commit history
  ugit log --oneline            Show compact commit history
  ugit log --graph              Show commit graph
  ugit checkout <commit>        Checkout a specific commit
  ugit checkout <branch>        Switch to a branch
  ugit checkout -b <branch>     Create and switch to a branch
  ugit branch                   List branches
  ugit branch <name>            Create a branch
  ugit branch -d <name>         Delete a branch
  ugit merge <branch>           Merge a branch
  ugit diff                     Show changes in working directory
  ugit diff --staged            Show staged changes
  ugit diff <commit1> <commit2> Compare two commits
  ugit reset                    Unstage all files
  ugit reset --hard <commit>    Reset to commit (destructive)
  ugit stash                    Stash current changes
  ugit stash pop                Apply and remove most recent stash
  ugit stash list               List all stashes
  ugit clone <url> [dir]        Clone a repository
  ugit remote add <name> <url>  Add a remote repository
  ugit remote -v                List remotes with URLs
  ugit fetch [remote]           Fetch changes from remote
  ugit pull [remote] [branch]   Fetch and merge from remote
  ugit push [remote] [branch]   Push changes to remote
        """,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    subparsers.add_parser("init", help="Initialize a new repository")

    # add command
    add_parser = subparsers.add_parser("add", help="Add files to staging area")
    add_parser.add_argument("paths", nargs="*", help="Files or directories to add")
    add_parser.add_argument(
        "-i", "--interactive", action="store_true", help="Interactive staging"
    )

    # commit command
    commit_parser = subparsers.add_parser("commit", help="Create a commit")
    commit_parser.add_argument(
        "-m", "--message", help="Commit message (optional, will prompt if not provided)"
    )
    commit_parser.add_argument("--author", help="Author information")

    # status command
    subparsers.add_parser("status", help="Show repository status")

    # config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument(
        "--list", action="store_true", help="List all configuration options"
    )
    config_parser.add_argument(
        "key", nargs="?", help="Configuration key (section.option)"
    )
    config_parser.add_argument("value", nargs="?", help="Configuration value")

    # log command
    log_parser = subparsers.add_parser("log", help="Show commit history")
    log_parser.add_argument(
        "-n", "--max-count", type=int, help="Limit number of commits to show"
    )
    log_parser.add_argument(
        "--oneline", action="store_true", help="Show each commit on one line"
    )
    log_parser.add_argument("--graph", action="store_true", help="Show ASCII graph")
    log_parser.add_argument("--since", help="Show commits since date")
    log_parser.add_argument("--until", help="Show commits until date")

    # checkout command
    checkout_parser = subparsers.add_parser(
        "checkout", help="Checkout a commit or switch to a branch"
    )
    checkout_parser.add_argument("target", help="Commit SHA or branch name to checkout")
    checkout_parser.add_argument(
        "-b", "--branch", action="store_true", help="Create new branch"
    )

    # branch command
    branch_parser = subparsers.add_parser(
        "branch", help="List, create, or delete branches"
    )
    branch_parser.add_argument("name", nargs="?", help="Branch name to create")
    branch_parser.add_argument(
        "-l", "--list", action="store_true", help="List branches"
    )
    branch_parser.add_argument("-d", "--delete", help="Delete a branch")

    # merge command
    merge_parser = subparsers.add_parser(
        "merge", help="Merge a branch into current branch"
    )
    merge_parser.add_argument("branch", help="Branch name to merge")
    merge_parser.add_argument("--no-ff", action="store_true", help="Force merge commit")
    merge_parser.add_argument(
        "--squash", action="store_true", help="Squash all commits into one"
    )
    merge_parser.add_argument(
        "-s",
        "--strategy",
        choices=["ours", "theirs"],
        help="Merge strategy (ours: keep current, theirs: use theirs)",
    )

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Show changes between files")
    diff_parser.add_argument(
        "--staged", action="store_true", help="Show staged changes"
    )
    diff_parser.add_argument("commit1", nargs="?", help="First commit to compare")
    diff_parser.add_argument("commit2", nargs="?", help="Second commit to compare")

    # reset command
    reset_parser = subparsers.add_parser(
        "reset", help="Reset current HEAD to specified state"
    )
    reset_parser.add_argument(
        "target", nargs="?", help="Commit SHA or branch to reset to"
    )
    reset_parser.add_argument(
        "--hard", action="store_true", help="Reset working directory and staging area"
    )
    reset_parser.add_argument("--soft", action="store_true", help="Only move HEAD")

    # stash command
    stash_parser = subparsers.add_parser(
        "stash", help="Stash changes in working directory"
    )
    stash_subparsers = stash_parser.add_subparsers(
        dest="stash_command", help="Stash commands"
    )

    # stash (default - save)
    stash_save = stash_subparsers.add_parser("save", help="Save changes to stash")
    stash_save.add_argument("message", nargs="?", help="Stash message")
    stash_save.add_argument(
        "-u", "--include-untracked", action="store_true", help="Include untracked files"
    )

    # stash pop
    stash_pop_parser = stash_subparsers.add_parser(
        "pop", help="Apply and remove most recent stash"
    )
    stash_pop_parser.add_argument(
        "stash_id", nargs="?", type=int, default=0, help="Stash index"
    )

    # stash list
    stash_subparsers.add_parser("list", help="List all stashes")

    # stash apply
    stash_apply_parser = stash_subparsers.add_parser(
        "apply", help="Apply stash without removing it"
    )
    stash_apply_parser.add_argument(
        "stash_id", nargs="?", type=int, default=0, help="Stash index"
    )

    # stash drop
    stash_drop_parser = stash_subparsers.add_parser(
        "drop", help="Remove stash without applying"
    )
    stash_drop_parser.add_argument(
        "stash_id", nargs="?", type=int, default=0, help="Stash index"
    )

    # clone command
    clone_parser = subparsers.add_parser("clone", help="Clone a repository")
    clone_parser.add_argument("url", help="Repository URL to clone")
    clone_parser.add_argument("directory", nargs="?", help="Directory name (optional)")

    # remote command
    remote_parser = subparsers.add_parser("remote", help="Manage remote repositories")
    remote_parser.add_argument("-v", "--verbose", action="store_true", help="Show URLs")
    remote_subparsers = remote_parser.add_subparsers(
        dest="subcommand", help="Remote commands"
    )

    # remote add
    remote_add = remote_subparsers.add_parser("add", help="Add a remote")
    remote_add.add_argument("name", help="Remote name")
    remote_add.add_argument("url", help="Remote URL")

    # remote remove
    remote_remove = remote_subparsers.add_parser("remove", help="Remove a remote")
    remote_remove.add_argument("name", help="Remote name")

    # remote show
    remote_show = remote_subparsers.add_parser("show", help="Show remote details")
    remote_show.add_argument("name", help="Remote name")

    # remote list (default)
    remote_list = remote_subparsers.add_parser("list", help="List remotes")
    remote_list.add_argument("-v", "--verbose", action="store_true", help="Show URLs")

    # fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch from remote repository")
    fetch_parser.add_argument("remote", nargs="?", default="origin", help="Remote name")
    fetch_parser.add_argument("branch", nargs="?", help="Branch name")

    # pull command
    pull_parser = subparsers.add_parser("pull", help="Fetch and merge from remote")
    pull_parser.add_argument("remote", nargs="?", default="origin", help="Remote name")
    pull_parser.add_argument("branch", nargs="?", help="Branch name")

    # push command
    push_parser = subparsers.add_parser("push", help="Push to remote repository")
    push_parser.add_argument("remote", nargs="?", default="origin", help="Remote name")
    push_parser.add_argument("branch", nargs="?", help="Branch name")
    push_parser.add_argument("-f", "--force", action="store_true", help="Force push")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start web interface server")
    serve_parser.add_argument(
        "--port", type=int, default=8000, help="Port to run server on (default: 8000)"
    )
    serve_parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    serve_parser.add_argument(
        "--no-browser", action="store_true", help="Don't open browser automatically"
    )

    # tag command
    tag_parser = subparsers.add_parser("tag", help="Create, list, or delete tags")
    tag_parser.add_argument("name", nargs="?", help="Tag name")
    tag_parser.add_argument(
        "-a", "--annotated", action="store_true", help="Create annotated tag"
    )
    tag_parser.add_argument("-m", "--message", help="Tag message (for annotated tags)")
    tag_parser.add_argument("-d", "--delete", help="Delete a tag")
    tag_parser.add_argument(
        "-l", "--list", action="store_true", dest="list_tags", help="List tags"
    )
    tag_parser.add_argument("commit", nargs="?", help="Commit to tag (default: HEAD)")

    # reflog command
    reflog_parser = subparsers.add_parser("reflog", help="Show reflog entries")
    reflog_parser.add_argument("branch", nargs="?", help="Branch to show reflog for")

    # blame command
    blame_parser = subparsers.add_parser(
        "blame", help="Show who last modified each line"
    )
    blame_parser.add_argument("file", help="File to blame")
    blame_parser.add_argument(
        "commit", nargs="?", help="Commit to blame (default: HEAD)"
    )
    blame_parser.add_argument(
        "-L",
        "--line-numbers",
        action="store_true",
        default=True,
        help="Show line numbers",
    )

    # cherry-pick command
    cherry_pick_parser = subparsers.add_parser(
        "cherry-pick", help="Apply commits from another branch"
    )
    cherry_pick_parser.add_argument("commit", help="Commit to cherry-pick")
    cherry_pick_parser.add_argument(
        "-n", "--no-commit", action="store_true", help="Don't create a commit"
    )

    # grep command
    grep_parser = subparsers.add_parser("grep", help="Search for pattern in repository")
    grep_parser.add_argument("pattern", help="Search pattern (regex)")
    grep_parser.add_argument("path", nargs="?", help="Path to search in")
    grep_parser.add_argument(
        "commit", nargs="?", help="Commit to search in (default: HEAD)"
    )
    grep_parser.add_argument(
        "-i", "--ignore-case", action="store_true", help="Case-insensitive"
    )
    grep_parser.add_argument(
        "--no-recursive", action="store_true", help="Don't search recursively"
    )

    # archive command
    archive_parser = subparsers.add_parser("archive", help="Create archive from commit")
    archive_parser.add_argument("output", help="Output file path")
    archive_parser.add_argument(
        "commit", nargs="?", help="Commit to archive (default: HEAD)"
    )
    archive_parser.add_argument(
        "--format", choices=["tar", "zip"], help="Archive format"
    )

    # alias command
    alias_parser = subparsers.add_parser("alias", help="Manage command aliases")
    alias_parser.add_argument("name", nargs="?", help="Alias name")
    alias_parser.add_argument("command", nargs="?", help="Command to alias")
    alias_parser.add_argument(
        "-l", "--list", action="store_true", dest="list_aliases", help="List aliases"
    )

    # stats command
    subparsers.add_parser("stats", help="Show repository statistics")

    # bisect command
    bisect_parser = subparsers.add_parser("bisect", help="Binary search for bugs")
    bisect_subparsers = bisect_parser.add_subparsers(
        dest="bisect_command", help="Bisect commands"
    )
    bisect_subparsers.add_parser("start", help="Start bisect session")
    bisect_subparsers.add_parser("good", help="Mark current commit as good")
    bisect_subparsers.add_parser("bad", help="Mark current commit as bad")
    bisect_subparsers.add_parser("skip", help="Skip current commit")
    bisect_subparsers.add_parser("reset", help="Reset bisect session")
    bisect_parser.add_argument("bad", nargs="?", help="Mark commit as bad")
    bisect_parser.add_argument("good", nargs="?", help="Mark commit as good")

    # rebase command
    rebase_parser = subparsers.add_parser(
        "rebase", help="Reapply commits on top of another branch"
    )
    rebase_parser.add_argument("branch", help="Branch to rebase onto")
    rebase_parser.add_argument(
        "-i", "--interactive", action="store_true", help="Interactive rebase"
    )
    rebase_parser.add_argument("--onto", help="Alternative base branch")

    # fsck command
    fsck_parser = subparsers.add_parser("fsck", help="Check repository integrity")
    fsck_parser.add_argument("--full", action="store_true", help="Perform full check")

    # gc command
    gc_parser = subparsers.add_parser("gc", help="Run garbage collection")
    gc_parser.add_argument(
        "--aggressive", action="store_true", help="Aggressive cleanup"
    )

    # pack command
    pack_parser = subparsers.add_parser("pack", help="Pack objects into pack files")
    pack_parser.add_argument(
        "objects", nargs="*", help="Object SHAs to pack (default: all)"
    )
    pack_parser.add_argument(
        "--unpack", help="Unpack objects from pack file", metavar="PACK_FILE"
    )

    # gpg command
    gpg_parser = subparsers.add_parser("gpg", help="GPG signing operations")
    gpg_subparsers = gpg_parser.add_subparsers(dest="gpg_command", help="GPG commands")
    gpg_subparsers.add_parser("sign-commit", help="Sign a commit")
    gpg_subparsers.add_parser("sign-tag", help="Sign a tag")
    gpg_subparsers.add_parser("verify", help="Verify a signature")
    gpg_parser.add_argument("object", nargs="?", help="Object SHA to sign/verify")
    gpg_parser.add_argument("-k", "--key", help="GPG key ID")

    # worktree command
    worktree_parser = subparsers.add_parser(
        "worktree", help="Manage multiple working directories"
    )
    worktree_subparsers = worktree_parser.add_subparsers(
        dest="worktree_command", help="Worktree commands"
    )
    worktree_subparsers.add_parser("add", help="Add a new worktree")
    worktree_subparsers.add_parser("remove", help="Remove a worktree")
    worktree_subparsers.add_parser("list", help="List worktrees")
    worktree_parser.add_argument("path", nargs="?", help="Path for worktree")
    worktree_parser.add_argument(
        "-b", "--branch", help="Branch to checkout in worktree"
    )
    worktree_parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        dest="list_worktrees",
        help="List worktrees",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the ugit CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        result: Optional[int] = 0

        if args.command == "init":
            init()
        elif args.command == "add":
            if args.interactive:
                from .commands.add_interactive import add_interactive

                add_interactive()
            elif not args.paths:
                add(".")
            else:
                add(args.paths)
        elif args.command == "commit":
            commit(args.message, args.author)
        elif args.command == "config":
            result = config(args.key, args.value, args.list)
        elif args.command == "status":
            status()
        elif args.command == "log":
            log(args.max_count, args.oneline, args.graph, args.since, args.until)
        elif args.command == "checkout":
            checkout(args.target, args.branch)
        elif args.command == "branch":
            branch(args.name, args.list, args.delete)
        elif args.command == "merge":
            merge(args.branch, args.no_ff, args.squash, args.strategy)
        elif args.command == "diff":
            if args.commit1 and args.commit2:
                diff(commit1=args.commit1, commit2=args.commit2)
            else:
                diff(staged=args.staged)
        elif args.command == "reset":
            reset(args.target, args.hard, args.soft)
        elif args.command == "stash":
            if args.stash_command == "pop":
                stash_pop(args.stash_id)
            elif args.stash_command == "list":
                stash_list()
            elif args.stash_command == "apply":
                stash_apply(args.stash_id)
            elif args.stash_command == "drop":
                stash_drop(args.stash_id)
            elif args.stash_command == "save" or args.stash_command is None:
                message = getattr(args, "message", None)
                include_untracked = getattr(args, "include_untracked", False)
                stash(message, include_untracked)
            else:
                sys.stderr.write(f"Unknown stash command: {args.stash_command}\n")
                return 1
        elif args.command == "clone":
            if args.depth:
                shallow_clone(args.url, args.directory, args.depth)
            else:
                clone(args.url, args.directory)
        elif args.command == "remote":
            remote(args)
        elif args.command == "fetch":
            result = fetch(args.remote, args.branch)
        elif args.command == "pull":
            result = pull(args.remote, args.branch)
        elif args.command == "push":
            result = push(args.remote, args.branch, args.force)
        elif args.command == "serve":
            result = serve(args.port, args.host, not args.no_browser)
        elif args.command == "tag":
            tag(
                args.name,
                args.list_tags,
                args.delete,
                args.annotated,
                args.message,
                args.commit,
            )
        elif args.command == "reflog":
            reflog(branch=args.branch)
        elif args.command == "blame":
            blame(args.file, args.commit, args.line_numbers)
        elif args.command == "cherry-pick":
            cherry_pick(args.commit, args.no_commit)
        elif args.command == "grep":
            grep(
                args.pattern,
                args.path,
                args.commit,
                args.ignore_case,
                not args.no_recursive,
            )
        elif args.command == "archive":
            archive(args.output, args.commit, args.format)
        elif args.command == "alias":
            alias(args.name, args.command, args.list_aliases)
        elif args.command == "stats":
            stats()
        elif args.command == "bisect":
            bisect(
                args.bisect_command, args.bad, args.good, args.bisect_command == "reset"
            )
        elif args.command == "rebase":
            rebase(args.branch, args.interactive, args.onto)
        elif args.command == "fsck":
            result = fsck(args.full)
        elif args.command == "gc":
            gc(args.aggressive)
        elif args.command == "pack":
            if args.unpack:
                pack.unpack_objects(args.unpack)
            else:
                obj_list: Optional[List[str]] = args.objects if args.objects else None
                pack.pack_objects(obj_list)
        elif args.command == "worktree":
            worktree(args.worktree_command, args.path, args.branch, args.list_worktrees)
        elif args.command == "gpg":
            if args.gpg_command == "sign-commit" and args.object:
                signature = gpg.sign_commit(args.object, args.key)
                print(f"Signed commit {args.object[:7]}")
                print(f"Signature: {signature[:100]}...")
            elif args.gpg_command == "sign-tag" and args.object:
                signature = gpg.sign_tag(args.object, args.key)
                print(f"Signed tag {args.object[:7]}")
                print(f"Signature: {signature[:100]}...")
            elif args.gpg_command == "verify" and args.object:
                # For now, just check if GPG is available
                if gpg.has_gpg():
                    print("GPG is available")
                else:
                    print("GPG is not available")
            else:
                print("Usage: ugit gpg {sign-commit|sign-tag|verify} <object> [-k key]")
        else:
            sys.stderr.write(f"Unknown command: {args.command}\n")
            return 1

        return result if result is not None else 0

    except UgitError as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        sys.stderr.write(f"An unexpected error occurred: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
