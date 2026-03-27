# pyStoOrm - ORM Code Generator

[![Tests](https://img.shields.io/badge/tests-33%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.5%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**pyStoOrm** is a Python ORM code generator that analyzes your database schema and automatically generates Python ORM classes with a clean, configurable, hierarchical configuration system.

## 🎯 Key Features

✨ **Multiple Database Support**
- MySQL
- PostgreSQL
- SQLite (perfect for testing)

✨ **Smart Configuration System**
- Hierarchical, layered configuration
- Sensible defaults for everything
- Override only what you need
- Environment variable support

✨ **Customizable Generation**
- Naming conventions (primary keys, foreign keys, special columns)
- Code style guide (class naming, formatting, type hints)
- Display attributes (which column to show in dropdowns)
- Template-based output

✨ **Developer Friendly**
- 33 comprehensive tests, all passing
- Well-documented configuration
- CLI interface
- Python 3.5+ compatible

---

## 🚀 Quick Start (5 minutes)

### 1. Install pyStoOrm

```bash
pip install -e .
```

### 2. Create Your Configuration

Create `project.yml`:

```yaml
connections:
  - connection: mydb
    host: localhost
    username: root
    password: mypassword
    database: my_database
    connector: database.mysqlconnector.MysqlConnector
```

### 3. Generate ORM Code

```bash
python3 pystoorm.py project.yml
```

**Done!** Your ORM code is generated with all defaults applied. 🎉

---

## 📋 Supported Databases

| Database | Connector | Test Support | Status |
|----------|-----------|--------------|--------|
| MySQL | `database.mysqlconnector.MysqlConnector` | ✓ | Production-ready |
| PostgreSQL | `database.postgresqlconnector.PostgresqlConnector` | ✓ | Production-ready |
| SQLite | `database.sqliteconnector.SqliteConnector` | ✓ | Great for testing |

### Using Different Databases

**MySQL:**
```yaml
connector: database.mysqlconnector.MysqlConnector
host: localhost
database: myapp
```

**PostgreSQL:**
```yaml
connector: database.postgresqlconnector.PostgresqlConnector
host: localhost
database: myapp
```

**SQLite (Testing):**
```yaml
connector: database.sqliteconnector.SqliteConnector
database: ./myapp.db           # or ':memory:' for in-memory
```

---

## 🛠️ Installation

### Requirements

- Python 3.5+
- Your database client library (installed automatically)

### From Source

```bash
# Clone repository
git clone https://github.com/StowasserH/pystoorm.git
cd pystoorm

# Install in development mode
pip install -e .

# Run tests
python3 -m pytest tests/ -v
```

### Debian/Ubuntu

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-dev

git clone https://github.com/StowasserH/pystoorm.git
cd pystoorm
pip install -e .
```

---

## 📚 Configuration Guide

pyStoOrm uses a **hierarchical configuration system**:

1. **Defaults** (built-in, no config needed)
2. **Project Config** (you create this)

### Minimal Configuration

Just provide database connection:

```yaml
connections:
  - connection: mydb
    host: localhost
    username: root
    password: secret
    database: myapp
    connector: database.mysqlconnector.MysqlConnector
```

### Advanced Configuration

Customize naming, style, and display attributes:

```yaml
connections:
  - connection: mydb
    host: localhost
    database: myapp
    connector: database.mysqlconnector.MysqlConnector

# Custom naming conventions
naming:
  primary_key:
    patterns: ["^id$", "^pk_{table}$"]

# Custom code style
style:
  class_naming:
    suffix: "Entity"  # Creates "UserEntity" instead of "UserModel"

# Custom display attributes (for dropdowns, lists, etc.)
attribute_hints:
  overrides:
    users: ["last_name", "email"]
```

### Documentation

See detailed configuration documentation:
- **[CONFIG_QUICK_START.md](CONFIG_QUICK_START.md)** - 5-minute guide with examples
- **[CONFIGURATION_STRATEGY.md](CONFIGURATION_STRATEGY.md)** - Architecture and deep dive
- **[pystoorm/config/README.md](pystoorm/config/README.md)** - Configuration reference

---

## 📖 Documentation

### Core Documentation

| Document | Purpose |
|----------|---------|
| [CONFIGURATION_STRATEGY.md](CONFIGURATION_STRATEGY.md) | Configuration system architecture |
| [CONFIG_QUICK_START.md](CONFIG_QUICK_START.md) | User guide with examples |
| [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) | Developer guide for template integration |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Implementation overview |

### API Documentation

| Document | Purpose |
|----------|---------|
| [pystoorm/config/README.md](pystoorm/config/README.md) | Configuration system API |
| [pystoorm/database/README_SQLITE.md](pystoorm/database/README_SQLITE.md) | SQLite connector guide |

---

## 🧪 Testing

### Run All Tests

```bash
python3 -m pytest tests/ -v
```

### Run Specific Test Suite

```bash
# Configuration tests
python3 -m pytest tests/test_config_loader.py -v

# Integration tests (SQLite)
python3 -m pytest tests/test_integration_sqlite.py -v

# Basic data model tests
python3 -m pytest tests/test_basic.py -v
```

### Test Coverage

- **33 tests total**
- Configuration system: 16 tests
- SQLite integration: 11 tests
- Data models: 6 tests
- All passing ✅

---

## 💡 Use Cases

### Development
Perfect for rapid ORM generation during development:
```bash
# Create test database, generate ORM code
python3 pystoorm.py dev_project.yml
```

### Testing
SQLite connector makes testing easy:
```yaml
connections:
  - connection: test
    database: ':memory:'              # In-memory, no setup needed
    connector: database.sqliteconnector.SqliteConnector
```

### Multiple Projects
All projects can share default configuration:
```
pystoorm/
├── config/defaults/                 # Shared defaults
├── projects/
│   ├── project_a/project.yml       # Project-specific
│   └── project_b/project.yml       # Project-specific
```

### CI/CD Integration
SQLite support means no external database needed:
```bash
# GitHub Actions, GitLab CI, etc.
python3 -m pytest tests/test_integration_sqlite.py
```

---

## 🔄 Workflow

```
┌─────────────────┐
│ Create Database │
└────────┬────────┘
         │
┌────────▼────────────────┐
│ Create project.yml      │
│ (connection details)    │
└────────┬────────────────┘
         │
┌────────▼────────────────────────┐
│ Run: python pystoorm.py project │
└────────┬────────────────────────┘
         │
┌────────▼─────────────────────────┐
│ 1. Analyze database schema       │
│ 2. Read config (hierarchical)    │
│ 3. Apply naming conventions      │
│ 4. Generate ORM classes          │
│ 5. Save to output directory      │
└────────┬─────────────────────────┘
         │
┌────────▼──────────┐
│ ORM Code Ready!   │
│ Start coding 🚀   │
└───────────────────┘
```

---

## 🔧 Advanced Configuration

### Environment Variables

```yaml
connections:
  - connection: prod
    host: db.example.com
    username: prod_user
    password_from_env: DB_PASSWORD    # Read from environment variable
    database: production
```

```bash
export DB_PASSWORD=secret
python3 pystoorm.py project.yml
```

### File-Based Passwords

```yaml
password_from_file: ~/.credentials/db.pass
```

### Custom Naming Patterns

```yaml
naming:
  primary_key:
    patterns: ["^id$", "^pk_{table}$"]

  foreign_key:
    patterns: ["^fk_{other_table}$", "^{other_table}_id$"]

  table:
    case_in_code: "PascalCase"    # or "camelCase", "snake_case"
```

### Custom Style Guide

```yaml
style:
  class_naming:
    case: "PascalCase"
    suffix: "Model"              # or "Entity", "DAO", etc.
    prefix: ""                   # e.g., "I" for interfaces

  formatting:
    indent: 4
    use_type_hints: true
    line_length: 88
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) style guide
4. Add tests for new functionality
5. Commit changes (`git commit -m 'Add AmazingFeature'`)
6. Push to branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

---

## 📋 Project Status

### ✅ Completed

- [x] Hierarchical configuration system
- [x] MySQL connector
- [x] PostgreSQL connector
- [x] SQLite connector (for testing)
- [x] Configuration tests (16 tests)
- [x] Integration tests (11 tests)
- [x] Comprehensive documentation

### 🚧 In Progress

- [ ] Template integration with configuration
- [ ] Semantic column detection
- [ ] Enhanced code generation

### 📋 Planned

- [ ] Schema migration generation
- [ ] Relationship mapping options
- [ ] Additional database support

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Authors

* **Harald Stowasser** - *Initial work and current maintainer* - [StowasserH](https://github.com/StowasserH)

See also the list of [contributors](https://github.com/StowasserH/pystoorm/contributors) who participated in this project.

---

## 🆘 Support

### Getting Help

- Check [CONFIG_QUICK_START.md](CONFIG_QUICK_START.md) for common questions
- Review [CONFIGURATION_STRATEGY.md](CONFIGURATION_STRATEGY.md) for architecture details
- Browse existing [Issues](https://github.com/StowasserH/pystoorm/issues)

### Reporting Issues

If you find a bug, please [open an issue](https://github.com/StowasserH/pystoorm/issues) with:
- Description of the problem
- Steps to reproduce
- Your configuration (without sensitive data)
- Python and database versions

---

## 🎓 Learn More

- [Getting Started Guide](CONFIG_QUICK_START.md)
- [Configuration Deep Dive](CONFIGURATION_STRATEGY.md)
- [SQLite Connector Guide](pystoorm/database/README_SQLITE.md)
- [Integration Guide for Developers](INTEGRATION_GUIDE.md)
- [Architecture Documentation](ARCHITECTURE.md)
