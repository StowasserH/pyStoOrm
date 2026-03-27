# SQLite Connector for pyStoOrm

This module provides SQLite database support for pyStoOrm, enabling ORM code generation from SQLite databases.

## Features

✅ **Full Connector Interface** - Implements all methods from the base Connector class
✅ **Schema Introspection** - Read tables, columns, types, keys from SQLite
✅ **Type Mapping** - Convert SQLite types to Python types
✅ **In-Memory Support** - Works with in-memory databases (`:memory:`)
✅ **File-Based Support** - Works with file-based SQLite databases
✅ **Foreign Key Support** - Reads foreign key relationships
✅ **Nullable Detection** - Correctly identifies nullable columns

## Usage

### Configuration

In your `project.yml`:

```yaml
connections:
  - connection: mydb
    database: ./myapp.db           # File path or ':memory:'
    connector: database.sqliteconnector.SqliteConnector
```

### Python Code

```python
from pystoorm.config.loader import load_config
from pystoorm.analyzer.controller import Controller
from pystoorm.generator.coordinator import Coordinator

# Load configuration
config = load_config('project.yml')

# Analyze database
analyzer = Controller(config)
analyzer.walk()

# Generate code
coordinator = Coordinator(config)
coordinator.generate()
```

## API Reference

### `SqliteConnector(config)`

#### Methods

**`connect()`**
- Connects to the SQLite database
- Creates parent directories if needed
- Enables foreign key support

**`get_schema()`**
- Returns a Schema object with all table names
- Excludes SQLite internal tables (those starting with `sqlite_`)

**`get_table(table_name)`**
- Returns a Table object with all column names for the given table
- Raises `ValueError` if table not found

**`get_column(table_name, column_name)`**
- Returns a Column object with detailed information:
  - Column name
  - Type (normalized to Python type)
  - Nullable status
  - Key type (PRI for primary key)
  - Default value
  - Length (from type declaration)
- Raises `ValueError` if column not found

**`close()`**
- Closes the database connection

## Type Mapping

SQLite types are mapped to Python types as follows:

| SQLite Type | Python Type |
|------------|-------------|
| INTEGER | int |
| REAL | float |
| TEXT | str |
| BLOB | bytes |
| NUMERIC | float |
| BOOLEAN | bool |
| VARCHAR(n) | str |
| Other | str (default) |

## Examples

### Example 1: File-Based Database

```yaml
connections:
  - connection: production
    database: /var/data/myapp.db
    connector: database.sqliteconnector.SqliteConnector
```

### Example 2: In-Memory Database (Testing)

```yaml
connections:
  - connection: test_db
    database: ':memory:'
    connector: database.sqliteconnector.SqliteConnector
```

### Example 3: Relative Path

```yaml
connections:
  - connection: local
    database: ./data/app.db
    connector: database.sqliteconnector.SqliteConnector
```

The connector will create parent directories if they don't exist.

## Testing

Run the test suite:

```bash
python3 -m pytest tests/test_integration_sqlite.py -v
```

Test coverage includes:

- ✅ Connection and disconnection
- ✅ Schema retrieval
- ✅ Table structure reading
- ✅ Column details extraction
- ✅ Type normalization
- ✅ Length extraction from type declarations
- ✅ In-memory database support
- ✅ Edge cases (nullable, primary keys, foreign keys)
- ✅ Integration with ConfigLoader
- ✅ Integration with Controller and Coordinator

## Advantages Over MySQL/PostgreSQL for Development

✅ **No external database required** - Single file or in-memory
✅ **Fast for testing** - In-memory databases are instant
✅ **Easy CI/CD** - No Docker or external services needed
✅ **Cross-platform** - Works on all platforms with Python
✅ **Minimal setup** - No installation, no configuration

## Limitations

⚠️ **SQLite is flexible with types** - Type information is more limited than in other databases
⚠️ **Schema-only support** - Some advanced PostgreSQL/MySQL-specific features not supported
⚠️ **Not for production ORM** - Use MySQL/PostgreSQL for actual application data

## Implementation Details

### Type Normalization

SQLite is very flexible with type declarations. The connector:
1. Tries exact matches against known SQLite types
2. Falls back to keyword-based detection (INT→int, CHAR→str, etc.)
3. Defaults to `str` if type is unrecognized

Example: `VARCHAR(100)` → detected as `str` with length 100

### Nullable Detection

Columns are considered:
- **NOT NULL** if: `NOT NULL` constraint exists OR it's a primary key
- **NULLABLE** otherwise

### Length Extraction

For type declarations like:
- `VARCHAR(50)` → length = 50
- `NUMERIC(10,2)` → length = 10 (first number)
- `INT` → length = 0

## Related Files

- `sqliteconnector.py` - Main SQLite connector implementation
- `connector.py` - Abstract base class
- `../tests/test_integration_sqlite.py` - Integration tests
- `../config/projects/example/project.yml` - Example configuration
