"""Tests for command implementations."""

import os
import tempfile
from pathlib import Path

from ugit.commands import add, commit, init, status
from ugit.core.repository import Repository


class TestInitCommand:
    """Test repository initialization."""

    def test_init_creates_repository_structure(self):
        """Test that init creates proper repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()

                # Check that .ugit directory and subdirectories exist
                assert os.path.exists(".ugit")
                assert os.path.exists(".ugit/objects")
                assert os.path.exists(".ugit/refs/heads")
                assert os.path.exists(".ugit/HEAD")

                # Check HEAD content
                with open(".ugit/HEAD", "r") as f:
                    head_content = f.read()
                assert head_content == "ref: refs/heads/main"

            finally:
                os.chdir(old_cwd)

    def test_init_in_existing_repository(self):
        """Test init in already initialized repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Initialize once
                init()

                # Initialize again - should detect existing repo
                # This would normally print "Already a ugit repository"
                init()  # Should not raise an error

            finally:
                os.chdir(old_cwd)


class TestAddCommand:
    """Test file staging."""

    def test_add_single_file(self):
        """Test adding a single file to staging area."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()

                # Create a test file
                test_file = Path("test.txt")
                test_file.write_text("Hello, World!")

                # Add the file
                add("test.txt")

                # Check that file is in index
                repo = Repository()
                from ugit.core.repository import Index

                index = Index(repo)
                index_data = index.read()

                assert "test.txt" in index_data
                assert len(index_data["test.txt"]) == 40  # SHA-1 length

            finally:
                os.chdir(old_cwd)

    def test_add_nonexistent_file(self):
        """Test adding non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()

                # Try to add non-existent file
                add("nonexistent.txt")  # Should handle gracefully

                # Index should be empty
                repo = Repository()
                from ugit.core.repository import Index

                index = Index(repo)
                index_data = index.read()

                assert len(index_data) == 0

            finally:
                os.chdir(old_cwd)


class TestCommitCommand:
    """Test commit creation."""

    def test_commit_with_staged_files(self):
        """Test creating a commit with staged files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()

                # Create and add a file
                test_file = Path("test.txt")
                test_file.write_text("Initial content")
                add("test.txt")

                # Create commit
                commit("Initial commit")

                # Check that commit was created
                repo = Repository()
                head_sha = repo.get_head_ref()
                assert head_sha is not None
                assert len(head_sha) == 40  # SHA-1 length

            finally:
                os.chdir(old_cwd)

    def test_commit_with_empty_index(self):
        """Test committing with no staged files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()

                # Try to commit without staging anything
                commit("Empty commit")  # Should handle gracefully

            finally:
                os.chdir(old_cwd)


class TestStatusCommand:
    """Test status reporting."""

    def test_status_clean_repository(self):
        """Test status on clean repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()
                status()  # Should not raise errors

            finally:
                os.chdir(old_cwd)

    def test_status_with_untracked_files(self):
        """Test status with untracked files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                init()

                # Create untracked file
                test_file = Path("untracked.txt")
                test_file.write_text("Untracked content")

                status()  # Should detect untracked file

            finally:
                os.chdir(old_cwd)
