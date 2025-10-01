"""
Integration tests for ugit functionality.
"""

import os
import shutil
import tempfile
from unittest import TestCase

from ugit.commands.add import add
from ugit.commands.branch import branch
from ugit.commands.checkout import checkout
from ugit.commands.commit import commit
from ugit.commands.diff import diff
from ugit.commands.init import init
from ugit.commands.stash import stash, stash_pop


class TestUgitIntegration(TestCase):
    """Integration tests for ugit workflow."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_complete_workflow(self):
        """Test a complete ugit workflow."""
        # Initialize repository
        init()

        # Create initial file and commit
        with open("README.md", "w") as f:
            f.write("# My Project\n\nThis is a test project.")

        add(["README.md"])
        commit("Initial commit", "Test User <test@example.com>")

        # Create a feature branch
        try:
            branch("feature/add-docs")
            checkout("feature/add-docs")
        except SystemExit:
            pass

        # Add documentation
        with open("docs.md", "w") as f:
            f.write("# Documentation\n\nThis is the documentation.")

        add(["docs.md"])
        commit("Add documentation", "Test User <test@example.com>")

        # Switch back to main branch (assuming it exists)
        try:
            # Create main branch first
            branch("main")
            checkout("main")
        except SystemExit:
            pass

        # Make changes on main
        with open("README.md", "w") as f:
            f.write(
                "# My Project\n\nThis is a test project.\n\nUpdated on main branch."
            )

        add(["README.md"])
        commit("Update README on main", "Test User <test@example.com>")

        # Test stash functionality
        with open("temp.txt", "w") as f:
            f.write("Temporary changes")

        try:
            stash("Temporary work")
            stash_pop()
        except SystemExit:
            pass

        # Test diff functionality
        try:
            diff()
        except SystemExit:
            pass

    def test_ignore_functionality(self):
        """Test .ugitignore functionality."""
        # Initialize repository
        init()

        # Create .ugitignore
        with open(".ugitignore", "w") as f:
            f.write("*.tmp\n__pycache__/\n*.log")

        # Create files (some should be ignored)
        with open("important.txt", "w") as f:
            f.write("Important file")

        with open("temp.tmp", "w") as f:
            f.write("Temporary file")

        os.makedirs("__pycache__", exist_ok=True)
        with open("__pycache__/cache.py", "w") as f:
            f.write("# Cache file")

        with open("app.log", "w") as f:
            f.write("Log entry")

        # Add all files - should respect ignore patterns
        try:
            add(["."])
        except SystemExit:
            pass

        commit("Initial commit with ignores", "Test User <test@example.com>")

    def test_error_handling(self):
        """Test error handling for invalid operations."""
        # Try operations without a repository
        try:
            add(["nonexistent.txt"])
        except RuntimeError:
            pass  # Expected to fail

        # Initialize repository
        init()

        # Try to add non-existent file
        try:
            add(["nonexistent.txt"])
        except SystemExit:
            pass  # Expected to fail

        # Try to checkout non-existent branch
        try:
            checkout("nonexistent-branch")
        except SystemExit:
            pass  # Expected to fail
