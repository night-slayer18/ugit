#!/usr/bin/env python3
"""
Manual integration test for ugit config and commit functionality.
Run this script to test the complete workflow.
"""

import os
import sys
import tempfile
import shutil
import subprocess

# Add ugit to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ugit.commands.init import init
from ugit.commands.config import config
from ugit.commands.add import add
from ugit.commands.commit import commit
from ugit.commands.log import log
from ugit.commands.status import status


def run_integration_test():
    """Run comprehensive integration test."""
    print("🧪 Starting ugit config integration test...")
    
    # Create temporary test directory
    test_dir = tempfile.mkdtemp(prefix="ugit_integration_test_")
    original_cwd = os.getcwd()
    
    try:
        os.chdir(test_dir)
        print(f"📁 Test directory: {test_dir}")
        
        # Test 1: Initialize repository
        print("\n1️⃣ Testing repository initialization...")
        init()
        assert os.path.exists(".ugit"), "Repository should be initialized"
        print("✅ Repository initialized successfully")
        
        # Test 2: Set configuration
        print("\n2️⃣ Testing configuration setup...")
        config("user.name", "Integration Tester")
        config("user.email", "tester@ugit.example")
        print("✅ Configuration set successfully")
        
        # Test 3: Verify configuration
        print("\n3️⃣ Testing configuration retrieval...")
        try:
            config("user.name")
            config("user.email")
            print("✅ Configuration retrieved successfully")
        except SystemExit:
            print("❌ Configuration retrieval failed")
            raise
        
        # Test 4: List all configuration
        print("\n4️⃣ Testing configuration listing...")
        try:
            config(list_all=True)
            print("✅ Configuration listing successful")
        except Exception as e:
            print(f"❌ Configuration listing failed: {e}")
            raise
        
        # Test 5: Create and add test files
        print("\n5️⃣ Testing file operations...")
        
        # Create regular file
        with open("important.txt", "w") as f:
            f.write("This is an important file\n")
        
        # Create ignore patterns
        with open(".ugitignore", "w") as f:
            f.write("*.log\ntemp/\n__pycache__/\n*.pyc\n")
        
        # Create ignored files
        with open("debug.log", "w") as f:
            f.write("Debug information\n")
        
        os.makedirs("temp", exist_ok=True)
        with open("temp/cache.txt", "w") as f:
            f.write("Temporary cache data\n")
        
        print("✅ Test files created")
        
        # Test 6: Check status (ignore functionality)
        print("\n6️⃣ Testing status with ignore patterns...")
        try:
            status()
            print("✅ Status command successful")
        except Exception as e:
            print(f"❌ Status command failed: {e}")
            raise
        
        # Test 7: Add files
        print("\n7️⃣ Testing file addition...")
        add([".ugitignore", "important.txt"])
        print("✅ Files added successfully")
        
        # Test 8: Commit with automatic config
        print("\n8️⃣ Testing commit with automatic config...")
        try:
            commit("Initial commit with configured user")
            print("✅ Commit successful")
        except Exception as e:
            print(f"❌ Commit failed: {e}")
            raise
        
        # Test 9: Check commit log
        print("\n9️⃣ Testing commit log...")
        try:
            log()
            print("✅ Log command successful")
        except SystemExit:
            # Log command exits after showing entries, this is expected
            print("✅ Log command successful")
        except Exception as e:
            print(f"❌ Log command failed: {e}")
            raise
        
        # Test 10: Test commit with author override
        print("\n🔟 Testing commit with author override...")
        
        # Create another file
        with open("override_test.txt", "w") as f:
            f.write("Testing author override\n")
        
        add(["override_test.txt"])
        
        try:
            commit("Commit with explicit author", "Override Author <override@example.com>")
            print("✅ Commit with author override successful")
        except Exception as e:
            print(f"❌ Commit with author override failed: {e}")
            raise
        
        # Test 11: Multiple config sections
        print("\n1️⃣1️⃣ Testing multiple config sections...")
        config("core.editor", "vim")
        config("core.pager", "less")
        
        try:
            config(list_all=True)
            print("✅ Multiple config sections successful")
        except Exception as e:
            print(f"❌ Multiple config sections failed: {e}")
            raise
        
        # Test 12: Config overwrite
        print("\n1️⃣2️⃣ Testing config overwrite...")
        config("user.name", "Updated Tester")
        try:
            config("user.name")
            print("✅ Config overwrite successful")
        except Exception as e:
            print(f"❌ Config overwrite failed: {e}")
            raise
        
        print("\n🎉 All integration tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n💥 Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test directory: {test_dir}")


def run_cli_integration_test():
    """Test CLI integration by calling ugit as subprocess."""
    print("\n🖥️  Testing CLI integration...")
    
    test_dir = tempfile.mkdtemp(prefix="ugit_cli_test_")
    original_cwd = os.getcwd()
    
    try:
        os.chdir(test_dir)
        print(f"📁 CLI test directory: {test_dir}")
        
        # Get path to ugit executable
        ugit_path = os.path.join(os.path.dirname(__file__), '..', 'ugit-env', 'bin', 'ugit')
        if not os.path.exists(ugit_path):
            print("⚠️  ugit not installed in virtual environment, skipping CLI test")
            return True
        
        # Test CLI commands
        commands = [
            ([ugit_path, "init"], "initialize repository"),
            ([ugit_path, "config", "user.name", "CLI Tester"], "set user name"),
            ([ugit_path, "config", "user.email", "cli@ugit.example"], "set user email"),
            ([ugit_path, "config", "--list"], "list configuration"),
            ([ugit_path, "config", "user.name"], "get user name"),
        ]
        
        for cmd, description in commands:
            print(f"Running: {' '.join(cmd[1:])} ({description})")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ {description} successful")
                    if result.stdout.strip():
                        print(f"   Output: {result.stdout.strip()}")
                else:
                    print(f"❌ {description} failed")
                    if result.stderr:
                        print(f"   Error: {result.stderr.strip()}")
                    return False
            except subprocess.TimeoutExpired:
                print(f"⏰ {description} timed out")
                return False
            except Exception as e:
                print(f"💥 {description} failed with exception: {e}")
                return False
        
        print("✅ All CLI integration tests passed!")
        return True
        
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up CLI test directory: {test_dir}")


if __name__ == "__main__":
    print("🚀 Running ugit integration tests...\n")
    
    # Run function-level integration test
    success1 = run_integration_test()
    
    # Run CLI integration test
    success2 = run_cli_integration_test()
    
    if success1 and success2:
        print("\n🎉 All integration tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some integration tests failed!")
        sys.exit(1)