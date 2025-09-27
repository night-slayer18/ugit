# Examples

This document provides practical examples of using ugit for various version control scenarios.

## Table of Contents

- [Basic Workflows](#basic-workflows)
- [Branching Workflows](#branching-workflows)
- [Stash Management](#stash-management)
- [Remote Repository Workflows](#remote-repository-workflows)
- [File Management](#file-management)
- [Commit Strategies](#commit-strategies)
- [History Exploration](#history-exploration)
- [Project Scenarios](#project-scenarios)

## Basic Workflows

### Starting a New Project

```bash
# Create and navigate to project directory
mkdir my-awesome-project
cd my-awesome-project

# Initialize ugit repository
ugit init

# Create initial files
echo "# My Awesome Project" > README.md
echo "print('Hello, World!')" > main.py

# Add files to staging
ugit add README.md
ugit add main.py

# Create first commit
ugit commit -m "Initial project setup with README and main script"

# Check status
ugit status
```

### Daily Development Workflow

```bash
# Start of day - check current status
ugit status
ugit log --max-count 5

# Make changes to files
echo "def greet(name): return f'Hello, {name}!'" >> main.py

# Stage and commit changes
ugit add main.py
ugit commit -m "Add greet function to main.py"

# Continue development
echo "if __name__ == '__main__': print(greet('World'))" >> main.py
ugit add main.py
ugit commit -m "Add main execution block"

# Review recent work
ugit log -n 3
```

## Branching Workflows

### Feature Branch Development

```bash
# Start from main branch
ugit checkout main
ugit log --oneline -n 3

# Create and switch to feature branch
ugit checkout -b feature-user-auth

# Develop the feature
echo "class UserAuth:" > auth.py
echo "    def login(self, username, password):" >> auth.py
echo "        pass" >> auth.py

ugit add auth.py
ugit commit -m "Add UserAuth class skeleton"

# Continue feature development
echo "    def logout(self):" >> auth.py
echo "        pass" >> auth.py

ugit add auth.py
ugit commit -m "Add logout method to UserAuth"

# Switch back to main and merge
ugit checkout main
ugit merge feature-user-auth

# Clean up branch
ugit branch -d feature-user-auth

# Verify merge
ugit log --oneline -n 5
```

### Parallel Feature Development

```bash
# Create two feature branches
ugit checkout -b feature-database
echo "database setup" > db.py
ugit add db.py
ugit commit -m "Add database configuration"

ugit checkout main
ugit checkout -b feature-api
echo "API endpoints" > api.py
ugit add api.py
ugit commit -m "Add API endpoints"

# Merge both features
ugit checkout main
ugit merge feature-database
ugit merge feature-api

# Check final result
ugit log --oneline --graph -n 10
```

## Stash Management

### Quick Context Switch

```bash
# Working on feature A
echo "Feature A code" > feature_a.py
ugit add feature_a.py

# Urgent bug fix needed - stash current work
ugit stash save "Feature A implementation in progress"

# Check stash was saved
ugit stash list
ugit status  # Should be clean

# Work on urgent fix
echo "Critical bug fix" > hotfix.py
ugit add hotfix.py
ugit commit -m "Fix critical security vulnerability"

# Return to Feature A work
ugit stash pop
ugit status  # Should show feature_a.py changes

# Continue working
echo "More Feature A code" >> feature_a.py
ugit commit -m "Complete Feature A implementation"
```

### Multiple Stashes Workflow

```bash
# Start multiple pieces of work
echo "Experimental feature 1" > experiment1.py
ugit add experiment1.py
ugit stash save "Experiment 1 - new algorithm"

echo "Experimental feature 2" > experiment2.py
ugit add experiment2.py
ugit stash save "Experiment 2 - UI improvements"

# List all stashes
ugit stash list

# Apply specific stash without removing it
ugit stash apply 1  # Apply "Experiment 1"

# Work with it, then clean up
ugit reset --hard  # Discard changes
ugit stash drop 1  # Remove stash 1

# Apply and remove the other stash
ugit stash pop  # Apply and remove most recent (Experiment 2)
```

## Remote Repository Workflows

### Team Collaboration Setup

```bash
# Initial repository setup
ugit init
echo "# Team Project" > README.md
ugit add README.md
ugit commit -m "Initial project setup"

# Add remote repository
ugit remote add origin https://github.com/team/project.git

# Push initial code
ugit push origin main

# List remotes to verify
ugit remote -v
```

### Feature Development with Remote

```bash
# Clone existing repository
ugit clone https://github.com/team/project.git
cd project

# Check remote status
ugit remote show origin

# Create feature branch
ugit checkout -b feature-new-dashboard

# Develop feature
echo "dashboard code" > dashboard.py
ugit add dashboard.py
ugit commit -m "Add new dashboard component"

# Push feature branch to remote
ugit push origin feature-new-dashboard

# Later: sync with main branch
ugit checkout main
ugit pull origin main

# Merge feature locally
ugit merge feature-new-dashboard
ugit push origin main
```

### Collaborative Workflow

```bash
# Start of day: sync with team changes
ugit checkout main
ugit pull origin main

# Create personal feature branch
ugit checkout -b my-feature-branch

# Work and commit regularly
echo "my changes" > my_file.py
ugit add my_file.py
ugit commit -m "Add my feature implementation"

# Before pushing: sync with latest main
ugit checkout main
ugit pull origin main
ugit checkout my-feature-branch
ugit merge main  # or rebase if preferred

# Push feature branch
ugit push origin my-feature-branch
```

## File Management

### Adding Different File Types

```bash
# Add individual files
ugit add config.json
ugit add src/utils.py
ugit add docs/api.md

# Add all files at once
ugit add .

# Add multiple specific files
ugit add file1.txt file2.py file3.md
```

### Working with Different File States

```bash
# Create new files
echo "Configuration settings" > config.txt
echo "Documentation" > docs.md

# Modify existing file
echo "# Updated content" >> README.md

# Check what's changed
ugit status

# Output will show:
# Untracked files:
#   config.txt
#   docs.md
# 
# Modified files:
#   README.md

# Stage specific changes
ugit add config.txt
ugit add README.md

# Check status again
ugit status

# Commit staged changes
ugit commit -m "Add config file and update README"

# Add remaining files
ugit add docs.md
ugit commit -m "Add documentation file"
```

## Commit Strategies

### Atomic Commits

Each commit should represent a single logical change:

```bash
# Bad: Multiple unrelated changes
ugit add .
ugit commit -m "Fix bug and add feature and update docs"

# Good: Separate commits for each change
ugit add bug_fix.py
ugit commit -m "Fix null pointer exception in data processor"

ugit add new_feature.py
ugit commit -m "Add user authentication feature"

ugit add README.md
ugit commit -m "Update README with installation instructions"
```

### Descriptive Commit Messages

```bash
# Good commit messages
ugit commit -m "Add input validation for user registration form"
ugit commit -m "Fix memory leak in file processing module"
ugit commit -m "Update API documentation for authentication endpoints"

# Poor commit messages (avoid these)
ugit commit -m "fix"
ugit commit -m "update"
ugit commit -m "changes"
```

### Feature Development

```bash
# Working on a new feature
echo "class UserManager:" > user_manager.py
ugit add user_manager.py
ugit commit -m "Add UserManager class skeleton"

echo "    def create_user(self, name, email):" >> user_manager.py
echo "        pass" >> user_manager.py
ugit add user_manager.py
ugit commit -m "Add create_user method to UserManager"

echo "    def validate_email(self, email):" >> user_manager.py
echo "        return '@' in email" >> user_manager.py
ugit add user_manager.py
ugit commit -m "Implement basic email validation"
```

## History Exploration

### Viewing Commit History

```bash
# View all commits
ugit log

# View limited number of commits
ugit log --max-count 5

# Example output:
# commit a1b2c3d4e5f6789012345678901234567890abcd
# Author: Your Name <you@example.com>
# Date:   Fri Sep 19 19:30:00 2025
# 
#     Add user authentication feature
# 
# commit b2c3d4e5f6789012345678901234567890abcdef1
# Author: Your Name <you@example.com>
# Date:   Fri Sep 19 18:45:00 2025
# 
#     Fix input validation bug
```

### Exploring Specific Commits

```bash
# Checkout a specific commit to see the code at that point
ugit checkout a1b2c3d4e5f6789012345678901234567890abcd

# Look around, check files
ls -la
cat main.py

# Return to latest state (use the most recent commit SHA)
ugit checkout [latest-commit-sha]
```

## Project Scenarios

### Python Project Development

```bash
# Initialize project
mkdir python-calculator
cd python-calculator
ugit init

# Create project structure
echo "#!/usr/bin/env python3" > calculator.py
echo "class Calculator:" >> calculator.py
echo "    pass" >> calculator.py

echo "# Calculator Project" > README.md
echo "A simple calculator implementation in Python" >> README.md

echo "calculator.py" > .gitignore
echo "__pycache__/" >> .gitignore

# Initial commit
ugit add .
ugit commit -m "Initial project structure"

# Add basic functionality
cat << 'EOF' >> calculator.py
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
EOF

ugit add calculator.py
ugit commit -m "Add basic arithmetic operations"

# Add more features
cat << 'EOF' >> calculator.py
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
EOF

ugit add calculator.py
ugit commit -m "Add multiplication and division with error handling"

# Add tests
echo "import unittest" > test_calculator.py
echo "from calculator import Calculator" >> test_calculator.py
echo "" >> test_calculator.py
echo "class TestCalculator(unittest.TestCase):" >> test_calculator.py
echo "    def setUp(self):" >> test_calculator.py
echo "        self.calc = Calculator()" >> test_calculator.py

ugit add test_calculator.py
ugit commit -m "Add unit test structure"

# Check project history
ugit log
```

### Documentation Project

```bash
# Initialize documentation project
mkdir project-docs
cd project-docs
ugit init

# Create documentation structure
mkdir -p docs/api docs/guides docs/examples
echo "# Project Documentation" > README.md

echo "# API Reference" > docs/api/index.md
echo "# User Guides" > docs/guides/index.md
echo "# Examples" > docs/examples/index.md

ugit add .
ugit commit -m "Create initial documentation structure"

# Add content progressively
echo "## Installation" >> docs/guides/index.md
echo "pip install our-package" >> docs/guides/index.md

ugit add docs/guides/index.md
ugit commit -m "Add installation instructions"

echo "## Quick Start" >> docs/guides/index.md
echo "Here's how to get started..." >> docs/guides/index.md

ugit add docs/guides/index.md
ugit commit -m "Add quick start guide"
```

### Configuration Management

```bash
# Project with configuration files
mkdir web-app
cd web-app
ugit init

# Create configuration files
echo '{"port": 3000, "debug": false}' > config.json
echo 'DATABASE_URL=localhost:5432' > .env.example
echo 'SECRET_KEY=your-secret-here' >> .env.example

# Create application files
echo 'from flask import Flask' > app.py
echo 'app = Flask(__name__)' >> app.py

# Add configuration first
ugit add config.json .env.example
ugit commit -m "Add configuration files and environment template"

# Add application code
ugit add app.py
ugit commit -m "Add Flask application skeleton"

# Update configuration
cat << 'EOF' > config.json
{
  "port": 3000,
  "debug": false,
  "database": {
    "host": "localhost",
    "port": 5432
  }
}
EOF

ugit add config.json
ugit commit -m "Expand configuration with database settings"
```

## Advanced Scenarios

### Bug Fix Workflow

```bash
# Discover bug in existing code
ugit status
ugit log --max-count 3

# Create fix
echo "# Bug fix for issue #123" > bugfix.py
echo "def fixed_function():" >> bugfix.py
echo "    return 'Fixed!'" >> bugfix.py

ugit add bugfix.py
ugit commit -m "Fix critical bug in data processing (fixes #123)"

# Verify fix and update
echo "# Added error handling" >> bugfix.py
ugit add bugfix.py
ugit commit -m "Add error handling to bug fix"
```

### Refactoring Session

```bash
# Before refactoring - save current state
ugit status
ugit commit -m "Save work before refactoring"

# Refactor code
echo "# Refactored module" > refactored_module.py
echo "class RefactoredClass:" >> refactored_module.py
echo "    def new_method(self):" >> refactored_module.py
echo "        pass" >> refactored_module.py

ugit add refactored_module.py
ugit commit -m "Refactor legacy code into new module structure"

# Continue refactoring
echo "    def another_method(self):" >> refactored_module.py
echo "        return 'improved'" >> refactored_module.py

ugit add refactored_module.py
ugit commit -m "Add improved methods to refactored module"
```

### Collaborative Development Simulation

```bash
# Simulate receiving changes from team member
echo "# Team member's contribution" > team_feature.py
echo "def team_function():" >> team_feature.py
echo "    return 'team work'" >> team_feature.py

ugit add team_feature.py
ugit commit -m "Add feature developed by team member"

# Your own changes
echo "# My contribution" > my_feature.py
echo "def my_function():" >> my_feature.py
echo "    return 'my work'" >> my_feature.py

ugit add my_feature.py
ugit commit -m "Add my feature implementation"

# Integration
echo "from team_feature import team_function" > integration.py
echo "from my_feature import my_function" >> integration.py
echo "" >> integration.py
echo "def combined_feature():" >> integration.py
echo "    return team_function() + ' + ' + my_function()" >> integration.py

ugit add integration.py
ugit commit -m "Integrate team feature with my feature"
```

## Tips and Best Practices

### Commit Frequency

```bash
# Commit often with small, logical changes
echo "def helper_function():" > utils.py
ugit add utils.py
ugit commit -m "Add helper function skeleton"

echo "    return 'helper'" >> utils.py
ugit add utils.py
ugit commit -m "Implement helper function logic"

echo "def another_helper():" >> utils.py
ugit add utils.py
ugit commit -m "Add second helper function"
```

### Status Checking

```bash
# Check status frequently
ugit status

# Before committing
ugit status
ugit add file.py
ugit status  # Verify what's staged
ugit commit -m "Descriptive message"
```

### History Review

```bash
# Review recent work
ugit log --max-count 5

# Check current state
ugit status

# See what you've accomplished
ugit log --max-count 10
```

These examples demonstrate practical usage patterns for ugit and show how to maintain a clean, understandable project history.