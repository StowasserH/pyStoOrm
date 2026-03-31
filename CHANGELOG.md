# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-31

### Added

- Initial PyPI packaging configuration
- `pyproject.toml` with modern Python packaging standards
- `setup.py` for backward compatibility
- `MANIFEST.in` for including documentation and license files
- GitHub Actions workflows for testing and PyPI publication
- Publishing guide (`PUBLISHING.md`)
- Hierarchical configuration system
- Support for MySQL, PostgreSQL, and SQLite databases
- Code generator with customizable templates
- 33 comprehensive tests with 100% pass rate

### Features

- Database-first code generation approach
- Multi-language and multi-framework support
- Configuration validation and hierarchy
- Database schema analysis and parsing
- Template-based code generation
- Repository pattern support
- SQL builder generation
- ERD (Entity Relationship Diagram) generation

### Documentation

- Comprehensive README with examples
- Configuration quick start guide
- Configuration strategy documentation
- Integration guide for template authors
- Architecture documentation
- SQLite connector guide

## Unreleased

### Planned

- Enhanced error messages
- Extended template library
- Additional database support
- Performance optimizations

---

## How to use this changelog

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

When releasing a new version:
1. Create a new section with the version number and date
2. Move items from "Unreleased" to the new section
3. Update the version in `pystoorm/__init__.py` and `pyproject.toml`
4. Commit with message: `Release version X.Y.Z`
5. Create a git tag: `git tag vX.Y.Z`
