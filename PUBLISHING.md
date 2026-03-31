# Publishing pyStoOrm to PyPI

This guide explains how to publish pyStoOrm to Python Package Index (PyPI).

## 🚀 Quick Start (TL;DR)

```bash
# 1. Update version
nano pystoorm/__init__.py  # Change __version__

# 2. Update changelog
nano CHANGELOG.md

# 3. Commit and tag
git commit -am "Release version 0.2.0"
git tag v0.2.0

# 4. Push (GitHub Actions publishes automatically)
git push origin main
git push origin v0.2.0

# 5. Check https://pypi.org/project/pystoorm/
```

That's it! No manual upload needed. ✨

## Prerequisites

- Python 3.5+ with pip
- A PyPI account at https://pypi.org
- `twine` installed for secure uploads (for manual publishing)

## Setup: GitHub Actions + OpenID Connect (Recommended)

The easiest and most secure way is to use GitHub Actions with PyPI's OpenID Connect support.

### 1. Register Trusted Publisher on PyPI

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Select "GitHub" and fill in:
   - **PyPI project name**: `pystoorm`
   - **Owner**: `StowasserH`
   - **Repository name**: `pyStoOrm`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi` (optional but recommended)
4. Click "Add"

### 2. Optional: Create GitHub Environment

For extra security, create a GitHub environment in your repository settings:

1. Go to GitHub repo Settings → Environments
2. Create new environment named `pypi`
3. Add protection rule (e.g., required reviewers)

### 3. That's it!

The workflow is already configured for OIDC. Just tag a release and it will auto-publish.

---

## Setup: Manual Publishing (Local)

If you want to publish manually from your computer:

### 1. Install Build Tools

```bash
pip install build twine
```

### 2. Create `~/.pypirc`

```ini
[distutils]
index-servers =
    pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = StowasserH
password = your_pypi_password
```

Or use keyring for safer password storage:

```bash
pip install keyring
keyring set https://upload.pypi.org/legacy/ StowasserH
twine upload dist/*
```

## Publishing Workflow

### Automatic Publishing via GitHub Actions (Recommended)

#### Step 1: Prepare Release

```bash
# 1. Update version in pystoorm/__init__.py
# 2. Update CHANGELOG.md
# 3. Commit changes
git add pystoorm/__init__.py CHANGELOG.md
git commit -m "Release version 0.2.0"

# 4. Create git tag
git tag v0.2.0

# 5. Push to GitHub
git push origin main
git push origin v0.2.0
```

#### Step 2: GitHub Actions Does the Rest

Once you push the tag starting with `v`, the workflow automatically:
- Checks out code
- Runs tests
- Builds distributions
- Validates with twine
- **Publishes to PyPI using OpenID Connect** ✅

No credentials needed! Check the Actions tab to see the progress.

---

### Manual Publishing (Local)

If you prefer to publish from your computer:

#### Step 1: Verify Tests Pass

```bash
python3 -m pytest tests/ -v
```

#### Step 2: Update Version

Edit `pystoorm/__init__.py`:

```python
__version__ = "0.2.0"  # Increment version
```

#### Step 3: Build Distribution Packages

```bash
python3 -m build
```

This creates:
- `dist/pystoorm-0.2.0.tar.gz` (source distribution)
- `dist/pystoorm-0.2.0-py3-none-any.whl` (wheel distribution)

#### Step 4: Verify Distributions

```bash
twine check dist/*
```

#### Step 5: Upload to PyPI Test Repository (Optional)

Test before uploading to production:

```bash
twine upload --repository testpypi dist/*
```

Then test installation:

```bash
pip install --index-url https://test.pypi.org/simple/ pystoorm
```

#### Step 6: Upload to PyPI Production

```bash
twine upload dist/*
```

## Verify Installation

After publishing, verify the package is available:

```bash
pip install pystoorm
python3 -c "import pystoorm; print(pystoorm.__version__)"
```

## Release Workflow Checklist

### Before Tagging

- [ ] Update version in `pystoorm/__init__.py`
- [ ] Update `CHANGELOG.md` with new features and fixes
- [ ] Run `python3 -m pytest tests/ -v` ✅ All tests pass
- [ ] Run `python3 -m build` locally to verify build works
- [ ] Run `twine check dist/*` to validate metadata

### Commit and Tag

- [ ] `git commit -m "Release version X.Y.Z"`
- [ ] `git tag vX.Y.Z`
- [ ] `git push origin main`
- [ ] `git push origin vX.Y.Z`

### Verify

- [ ] GitHub Actions workflow runs automatically
- [ ] Check Actions tab for success
- [ ] Verify on https://pypi.org/project/pystoorm/

## Troubleshooting

### GitHub Actions Workflow Fails

**Build fails:**
- Check the Actions tab for error details
- Most likely: test failure or metadata issue
- Fix locally with `python3 -m build` and `twine check`

**Authentication fails (403/401):**
- Verify trusted publisher is registered at https://pypi.org/manage/account/publishing/
- Check that values match exactly:
  - PyPI project: `pystoorm`
  - Owner: `StowasserH`
  - Repository: `pyStoOrm`
  - Workflow: `publish.yml`
- If using environment `pypi`, ensure it exists in GitHub repo settings

### `twine check` Fails

- Check that `README.md` exists and is referenced in `pyproject.toml`
- Validate TOML syntax in `pyproject.toml`
- Ensure all classifiers are valid

### Package Metadata Issues

- Clear build artifacts: `rm -rf dist/ build/ *.egg-info pystoorm.egg-info`
- Rebuild: `python3 -m build`
- Check: `twine check dist/*`

### Wrong Version Published

- Check `pystoorm/__init__.py` for correct `__version__`
- Verify git tag matches: `git tag -l`
- New release requires new tag/version

## Resources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging](https://packaging.python.org/)

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes (X.0.0)
- **MINOR**: New features, backward-compatible (0.X.0)
- **PATCH**: Bug fixes, backward-compatible (0.0.X)

Example progression: 0.1.0 → 0.2.0 → 1.0.0 → 1.1.0 → 1.1.1
