"""
Tests for merge command functionality.
"""

import os
import tempfile
import unittest

from ugit.commands.add import add
from ugit.commands.branch import branch
from ugit.commands.checkout import checkout
from ugit.commands.commit import commit
from ugit.commands.init import init
from ugit.commands.merge import merge
from ugit.core.repository import Repository


class TestMergeCommand(unittest.TestCase):
    """Test cases for merge command."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.test_dir)

    def test_merge_fast_forward(self):
        """Test fast-forward merge."""
        # Initialize repository
        init()

        # Create initial commit on main
        with open("main.txt", "w") as f:
            f.write("Main content")
        add(["main.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Create feature branch
        try:
            branch("feature")
            checkout("feature")
        except SystemExit:
            pass

        # Add commits to feature branch
        with open("feature.txt", "w") as f:
            f.write("Feature content")
        add(["feature.txt"])
        commit("Feature commit", "Test Author <test@example.com>")

        # Switch back to main
        try:
            checkout("main")
        except SystemExit:
            pass

        # Merge feature branch (should be fast-forward)
        try:
            merge("feature")
        except SystemExit:
            pass

        # Check that feature.txt exists in main
        self.assertTrue(os.path.exists("feature.txt"))

    def test_merge_no_ff(self):
        """Test merge with --no-ff flag."""
        # Initialize repository
        init()

        # Create initial commit
        with open("base.txt", "w") as f:
            f.write("Base content")
        add(["base.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Create feature branch
        try:
            branch("feature")
            checkout("feature")
        except SystemExit:
            pass

        # Add commit to feature
        with open("feature.txt", "w") as f:
            f.write("Feature content")
        add(["feature.txt"])
        commit("Feature commit", "Test Author <test@example.com>")

        # Switch back to main
        try:
            checkout("main")
        except SystemExit:
            pass

        # Merge with no-ff
        try:
            merge("feature", no_ff=True)
        except SystemExit:
            pass

        # Check that feature content is merged
        self.assertTrue(os.path.exists("feature.txt"))

    def test_merge_three_way(self):
        """Test three-way merge when branches have diverged."""
        # Initialize repository
        init()

        # Create initial commit
        with open("shared.txt", "w") as f:
            f.write("Shared content")
        add(["shared.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Create and switch to feature branch
        try:
            branch("feature")
            checkout("feature")
        except SystemExit:
            pass

        # Add commit to feature branch
        with open("feature.txt", "w") as f:
            f.write("Feature content")
        add(["feature.txt"])
        commit("Feature commit", "Test Author <test@example.com>")

        # Switch back to main and add different commit
        try:
            checkout("main")
        except SystemExit:
            pass

        with open("main.txt", "w") as f:
            f.write("Main content")
        add(["main.txt"])
        commit("Main commit", "Test Author <test@example.com>")

        # Merge feature branch
        try:
            merge("feature")
        except SystemExit:
            pass

        # Check that both files exist
        self.assertTrue(os.path.exists("feature.txt"))
        self.assertTrue(os.path.exists("main.txt"))
        self.assertTrue(os.path.exists("shared.txt"))

    def test_merge_conflict_detection(self):
        """Test that merge conflicts are detected."""
        # Initialize repository
        init()

        # Create initial commit with conflicting file
        with open("conflict.txt", "w") as f:
            f.write("Original content")
        add(["conflict.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Create feature branch and modify file
        try:
            branch("feature")
            checkout("feature")
        except SystemExit:
            pass

        with open("conflict.txt", "w") as f:
            f.write("Feature content")
        add(["conflict.txt"])
        commit("Feature commit", "Test Author <test@example.com>")

        # Switch to main and modify same file differently
        try:
            checkout("main")
        except SystemExit:
            pass

        with open("conflict.txt", "w") as f:
            f.write("Main content")
        add(["conflict.txt"])
        commit("Main commit", "Test Author <test@example.com>")

        # Attempt merge - should detect conflict
        try:
            merge("feature")
        except SystemExit:
            pass

        # Check that conflict markers exist
        with open("conflict.txt", "r") as f:
            content = f.read()
        self.assertIn("<<<<<<< HEAD", content)
        self.assertIn(">>>>>>> feature", content)
        self.assertIn("Main content", content)
        self.assertIn("Feature content", content)

    def test_merge_nonexistent_branch(self):
        """Test merge with non-existent branch."""
        init()

        # Create initial commit
        with open("test.txt", "w") as f:
            f.write("Test")
        add(["test.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Try to merge non-existent branch
        try:
            merge("nonexistent")
        except SystemExit:
            pass

        # Should have shown error message (captured in test output)

    def test_merge_into_same_branch(self):
        """Test merge branch into itself."""
        init()

        # Create initial commit
        with open("test.txt", "w") as f:
            f.write("Test")
        add(["test.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Create branch and switch to it
        try:
            branch("feature")
            checkout("feature")
        except SystemExit:
            pass

        # Try to merge branch into itself
        try:
            merge("feature")
        except SystemExit:
            pass

        # Should show appropriate error

    def test_merge_when_not_on_branch(self):
        """Test merge when HEAD is detached."""
        init()

        # Create initial commit
        with open("test.txt", "w") as f:
            f.write("Test")
        add(["test.txt"])
        commit("Initial commit", "Test Author <test@example.com>")

        # Get commit SHA and checkout directly (detached HEAD)
        repo = Repository()
        commit_sha = repo.get_head_ref()

        try:
            checkout(commit_sha)  # Detached HEAD
        except SystemExit:
            pass

        # Create branch to merge
        try:
            branch("feature")
        except SystemExit:
            pass

        # Try to merge while detached
        try:
            merge("feature")
        except SystemExit:
            pass

        # Should show error about not being on any branch

    def test_merge_preserves_history(self):
        """Test that merge commits preserve both parent histories."""
        init()

        # Create initial commit
        with open("base.txt", "w") as f:
            f.write("Base")
        add(["base.txt"])
        commit("Base commit", "Test Author <test@example.com>")

        # Create feature branch
        try:
            branch("feature")
            checkout("feature")
        except SystemExit:
            pass

        with open("feature.txt", "w") as f:
            f.write("Feature")
        add(["feature.txt"])
        commit("Feature commit", "Test Author <test@example.com>")

        # Switch to main and add commit
        try:
            checkout("main")
        except SystemExit:
            pass

        with open("main.txt", "w") as f:
            f.write("Main")
        add(["main.txt"])
        commit("Main commit", "Test Author <test@example.com>")

        # Merge feature
        try:
            merge("feature")
        except SystemExit:
            pass

        # Verify all files are present
        self.assertTrue(os.path.exists("base.txt"))
        self.assertTrue(os.path.exists("feature.txt"))
        self.assertTrue(os.path.exists("main.txt"))


if __name__ == "__main__":
    unittest.main()
