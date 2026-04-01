# pyStoOrm - ORM Code Generator

[![Tests](https://img.shields.io/badge/tests-33%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.5%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**pyStoOrm** is a database-first code generator that analyzes your database schema and generates code for **any language, any framework, any pattern**. From Python ORM models to Java entities, TypeScript types, REST APIs, documentation, or custom recordsets—all from a single source of truth: your database.

## 🎯 The Core Idea

**pyStoOrm inverts the traditional ORM approach:**

| Traditional ORMs | pyStoOrm |
|---|---|
| Learn a query language | Write SQL or use database tools |
| ORM abstraction is the "source of truth" | **Your database is the source of truth** |
| Limited to lowest common denominator across databases | Leverage specific database features (JSON, Window Functions, CTEs, etc.) |
| One pattern fits all (SQLAlchemy, Django ORM, Prisma) | **Generate any pattern**: ORM, Recordsets, Repositories, DataObjects, etc. |
| One language: Python/TypeScript/Java/etc. | **Generate any language**: Python, Java, PHP, TypeScript, Go, C#, etc. |
| Only generates code | **Generates anything**: Code, Documentation, ERD Diagrams, API Specs, etc. |

**No intermediate query language to learn.** Your database schema is the specification. Templates generate the code.

---

## 🎯 Key Features

✨ **Multiple Database Support**
- MySQL
- PostgreSQL
- SQLite (perfect for testing)
- tbd...

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

✨ **Language & Pattern Agnostic**
- Python ORM Models (Repository, SQLBuilder, Dataclasses)
- Java/PHP/TypeScript Objects
- REST API Specifications
- Database Documentation
- ERD Diagrams with relationships
- Custom Recordsets or Query Objects
- Migrations, Seeds, Fixtures
- Or create your own pattern!

✨ **Developer Friendly**
- 33 comprehensive tests, all passing
- Well-documented configuration
- CLI interface
- Python 3.5+ compatible

---

## 📋 Generate Anything from Your Database

One database. Many outputs. One configuration file.

```yaml
output:
  # Python: Repository Pattern with SQL metadata
  - from: templates/python/repository.py.template
    to: generated/repositories/[table]_repository.py
    modus: table

  # Python: SQLBuilder for custom queries
  - from: templates/python/sqlbuilder.py.template
    to: generated/builders/[table]_builder.py
    modus: table

  # TypeScript: API types for frontend
  - from: templates/typescript/types.ts.template
    to: generated/api/[table].ts
    modus: table

  # PHP: Doctrine entities
  - from: templates/php/entity.php.template
    to: generated/php/[table].php
    modus: table

  # Documentation: Schema reference
  - from: templates/markdown/schema.md.template
    to: generated/SCHEMA.md
    modus: schema

  # Visualization: Database diagram
  - from: templates/graphviz/erd.template
    to: generated/erd.dot
    modus: schema
```

Run once: `python pyStoOrm.py project.yml` → 6 different outputs!

---

## 🗄️ Your Database is the Source of Truth

**You don't learn a new query language.** You use SQL and your database directly.

### Why This Matters

**Traditional ORMs (SQLAlchemy, Django, Prisma):**
```python
# Learn the ORM query syntax
users = User.query.filter(User.age > 18).join(Order).all()
# Limited to what the ORM can express
# Can't use database-specific features easily
```

**pyStoOrm:**
```python
# Write actual SQL using generated SQL metadata
query = f"""
    SELECT {CustomersRepository.sql_select('c')}
    FROM {CustomersRepository.SQL_TABLE} c
    JOIN orders o ON o.customer_id = c.id
    WHERE c.country = ?
"""
cursor.execute(query, ['USA'])
customers = [Customers._from_row(row) for row in cursor]
```

**Benefits:**
- 📚 No new language to learn (you already know SQL)
- 🚀 Use database-specific features (PostgreSQL window functions, MySQL JSON, Oracle CTEs, etc.)
- 🎯 Not limited to the "lowest common denominator"
- 📊 Full access to your database's actual capabilities
- 🔍 Generated SQL metadata (`SQL_TABLE`, `SQL_COLS`, `SQL_IDX`) for queries
- 🛠️ Easy to optimize – you write the SQL, not the ORM

### Database Features: Fully Accessible

All without fighting the ORM abstraction.

---

## 🚀 Quick Start (5 minutes)

### 1. Install pyStoOrm

```bash
pip install pystoorm
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

### From PyPI (Recommended)

The easiest way to get started:

```bash
pip install pystoorm
```

Then create your configuration file and run:

```bash
python3 pystoorm.py project.yml
```

### From Source

For development or contributing:

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

# Option 1: From PyPI (recommended)
pip install pystoorm

# Option 2: From source
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

### Polyglot Development (Microservices)
Generate backend code in different languages from same database:

```yaml
output:
  - from: templates/python/repository.py.template
    to: services/python/models/[table].py

  - from: templates/java/entity.java.template
    to: services/java/src/models/[table].java

  - from: templates/typescript/types.ts.template
    to: services/frontend/types/[table].ts
```

All three services share the same database schema—no manual synchronization needed.

### API Documentation
Generate OpenAPI/Swagger specs directly from database:

```yaml
output:
  - from: templates/openapi/spec.yaml.template
    to: generated/openapi.yaml
    modus: schema
```

### Repository Pattern
Python ORM with Repository pattern:

```yaml
output:
  - from: templates/python/model.py.template
    to: models/[table].py

  - from: templates/python/repository.py.template
    to: repositories/[table]_repository.py

  - from: templates/python/sqlbuilder.py.template
    to: builders/[table]_builder.py
```

### Custom Recordset Pattern
If you prefer recordset/DAO pattern:

```yaml
output:
  - from: templates/php/recordset.php.template
    to: generated/[table]Recordset.php
```

### Database-First Documentation
Keep schema documentation always in sync:

```yaml
output:
  - from: templates/markdown/schema_docs.md.template
    to: docs/schema.md
    modus: schema
```

### Development
Perfect for rapid code generation during development:
```bash
# Generate all outputs from single config
python3 pystoorm.py dev_project.yml
```

### Testing
SQLite connector makes testing easy:
```yaml
connections:
  - connection: test
    database: ':memory:'
    connector: database.sqliteconnector.SqliteConnector
```

### CI/CD Integration
SQLite means no external database setup needed:
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
