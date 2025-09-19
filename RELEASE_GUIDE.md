# Alternative CI Configuration Options

## Option 1: Disable Release Job Completely (Safest)
If you want to disable automatic releases entirely, change the release job condition to:

```yaml
release:
  if: false  # Disable automatic releases
  needs: build
  # ... rest of job
```

## Option 2: Manual Release Only
Only release when manually triggered or on git tags:

```yaml
release:
  if: github.event_name == 'workflow_dispatch' || (github.event_name == 'push' && startsWith(github.ref, 'refs/tags/'))
  # ... rest of job
```

## Option 3: Environment-based Release
Use GitHub environments to control releases:

```yaml
release:
  if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/')
  needs: build
  runs-on: ubuntu-latest
  environment: release  # Requires approval
  # ... rest of job
```

## Setting Up TestPyPI (When Ready)

### 🔐 IMPORTANT: Never Commit Tokens to Git!
**⚠️ Always use GitHub repository secrets - never put tokens in your code!**

### Step 1: Get Your TestPyPI Token
1. Create TestPyPI account: https://test.pypi.org/account/register/
2. Generate API token: https://test.pypi.org/manage/account/token/
3. Copy the token (starts with `pypi-`)

### Step 2: Add Token to GitHub Secrets
1. **Go to your repository**: https://github.com/night-slayer18/ugit
2. **Click "Settings"** tab (top of repository page)
3. **Navigate to secrets**: 
   - Click "Secrets and variables" in left sidebar
   - Click "Actions"
4. **Add the secret**:
   - Click "New repository secret"
   - **Name**: `TEST_PYPI_API_TOKEN`
   - **Secret**: Paste your TestPyPI token
   - Click "Add secret"

### Step 3: Enable Release Workflow
Uncomment the release job in `.github/workflows/ci.yml`:

```yaml
# Remove the comments from the release section
release:
  if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/')
  needs: build
  runs-on: ubuntu-latest
  # ... rest of release job
```

## Creating a Release

To create a release when ready:

```bash
# Tag a version
git tag v0.1.0
git push origin v0.1.0

# This will trigger the release workflow
```