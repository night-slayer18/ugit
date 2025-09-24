#!/usr/bin/env python3
"""
Command-line interface for ugit.
"""

import argparse
import sys
from typing import List, Optional

from .commands import add, branch, checkout, checkout_branch, commit, diff, init, log, status


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
  ugit checkout <commit>        Checkout a specific commit
  ugit checkout <branch>        Switch to a branch
  ugit checkout -b <branch>     Create and switch to a branch
  ugit branch                   List branches
  ugit branch <name>            Create a branch
  ugit branch -d <name>         Delete a branch
  ugit diff                     Show changes in working directory
  ugit diff --staged            Show staged changes
  ugit diff <commit1> <commit2> Compare two commits
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a new repository")

    # add command
    add_parser = subparsers.add_parser("add", help="Add files to staging area")
    add_parser.add_argument("paths", nargs="+", help="Files or directories to add")

    # commit command
    commit_parser = subparsers.add_parser("commit", help="Create a commit")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
    commit_parser.add_argument("--author", help="Author information")

    # status command
    status_parser = subparsers.add_parser("status", help="Show repository status")

    # log command
    log_parser = subparsers.add_parser("log", help="Show commit history")
    log_parser.add_argument(
        "-n", "--max-count", type=int, help="Limit number of commits to show"
    )

    # checkout command
    checkout_parser = subparsers.add_parser("checkout", help="Checkout a commit or switch to a branch")
    checkout_parser.add_argument("target", help="Commit SHA or branch name to checkout")
    checkout_parser.add_argument("-b", "--branch", action="store_true", help="Create new branch")

    # branch command
    branch_parser = subparsers.add_parser("branch", help="List, create, or delete branches")
    branch_parser.add_argument("name", nargs="?", help="Branch name to create")
    branch_parser.add_argument("-l", "--list", action="store_true", help="List branches")
    branch_parser.add_argument("-d", "--delete", help="Delete a branch")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Show changes between files")
    diff_parser.add_argument("--staged", action="store_true", help="Show staged changes")
    diff_parser.add_argument("commit1", nargs="?", help="First commit to compare")
    diff_parser.add_argument("commit2", nargs="?", help="Second commit to compare")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the ugit CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "init":
            init()
        elif args.command == "add":
            add(args.paths)
        elif args.command == "commit":
            author = args.author or "Your Name <you@example.com>"
            commit(args.message, author)
        elif args.command == "status":
            status()
        elif args.command == "log":
            log(args.max_count)
        elif args.command == "checkout":
            checkout(args.target, args.branch)
        elif args.command == "branch":
            branch(args.name, args.list, args.delete)
        elif args.command == "diff":
            if args.commit1 and args.commit2:
                diff(commit1=args.commit1, commit2=args.commit2)
            else:
                diff(staged=args.staged)
        else:
            print(f"Unknown command: {args.command}")
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
