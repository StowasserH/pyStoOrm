# pyStoOrm Configuration - Quick Start Guide

## 🚀 TL;DR - 5 Minute Setup

### 1. Create your project configuration file

```bash
mkdir -p my_project
cd my_project
```

**Create `project.yml`:**

```yaml
connections:
  - connection: mydb
    host: localhost
    username: root
    password: mypassword
    database: my_database
    connector: database.mysqlconnector.MysqlConnector
    port: 3306

project_root: .
output_dir: ./generated
```

### 2. Run pyStoOrm

```bash
cd /path/to/pystoorm
python3 pystoorm.py /path/to/my_project/project.yml
```

**That's it!** Your ORM code is generated in `./generated/orm/`

---

## 📚 Full Documentation

### Directory Structure

```
pystoorm/
├── config/
│   ├── defaults/                    # Built-in defaults
│   │   ├── bootstrap.yml            # Output templates, logging
│   │   ├── naming-conventions.yml   # PK/FK patterns
│   │   ├── attribute-hints.yml      # Display column hints
│   │   └── style-guides/
│   │       └── python-pep8.yml      # Python code style
│   └── projects/
│       └── example/
│           └── project.yml          # Example configuration
```

### What Each Configuration File Does

#### `bootstrap.yml` - Output & Logging
Controls where code is generated and logging level.

```yaml
logging:
  level: INFO  # DEBUG, INFO, WARN, ERROR

output:
  - from: ./pystoorm/templates/python/model.py
    to: ${project}/orm/model/[table].py
    enabled: true
```

#### `naming-conventions.yml` - How Columns Are Identified
Defines patterns for detecting primary keys, foreign keys, etc.

```yaml
naming:
  primary_key:
    patterns: ["^id$", "^{table_singular}_id$"]

  foreign_key:
    patterns: ["^{other_table}_id$", "^fk_.*"]

  table:
    case_in_code: "PascalCase"  # How table names appear in classes
```

#### `style-guides/python-pep8.yml` - Code Style
Controls generated Python code formatting.

```yaml
style:
  class_naming:
    case: "PascalCase"
    suffix: "Model"              # Creates "UserModel" not just "User"

  formatting:
    indent: 4
    use_type_hints: true
```

#### `attribute-hints.yml` - Display Columns
Which column to use in dropdowns, lists, etc. (the "attitüde").

```yaml
attribute_hints:
  defaults: ["name", "title", "{table_singular}_name"]
  overrides:
    users: ["last_name", "first_name", "email"]
```

#### `project.yml` - Your Project Settings
**This is where YOU add your database connection and custom settings.**

```yaml
connections:
  - connection: mydb
    host: localhost
    username: myuser
    password: mypass
    database: mydb
    connector: database.mysqlconnector.MysqlConnector

# Optional: Override defaults
naming:
  primary_key:
    patterns: ["^pk_{table}$"]  # Your custom PK pattern

style:
  class_naming:
    suffix: "Entity"            # Use "UserEntity" instead of "UserModel"

attribute_hints:
  defaults: ["label", "name"]
  overrides:
    users: ["full_name"]
```

---

## 🔄 Configuration Hierarchy

Configurations are loaded and merged in this order. Each level can override the previous:

```
1. bootstrap.yml (global output templates)
   ↓
2. naming-conventions.yml (default naming rules)
   ↓
3. style-guides/python-pep8.yml (default code style)
   ↓
4. attribute-hints.yml (default display hints)
   ↓
5. project.yml (YOUR custom settings override everything)
```

**Key Point:** Only values you specify in `project.yml` override defaults. The rest stays the same.

---

## 💡 Common Scenarios

### Scenario 1: Minimal Setup (Just Connect to Database)

**`project.yml`:**
```yaml
connections:
  - connection: mydb
    host: localhost
    username: root
    password: secret
    database: myapp
    connector: database.mysqlconnector.MysqlConnector
```

✅ Uses all defaults for naming, style, and attributes.

---

### Scenario 2: Custom Naming Conventions

Your database uses `pk_table_name` for primary keys:

**`project.yml`:**
```yaml
connections:
  - connection: mydb
    host: localhost
    database: myapp
    connector: database.mysqlconnector.MysqlConnector

# Override naming patterns
naming:
  primary_key:
    patterns: ["^pk_{table_singular}$", "^id$"]
```

---

### Scenario 3: Custom Code Style

You want generated classes to be named like `UserEntity` instead of `UserModel`:

**`project.yml`:**
```yaml
connections:
  - connection: mydb
    host: localhost
    database: myapp
    connector: database.mysqlconnector.MysqlConnector

# Override style
style:
  class_naming:
    suffix: "Entity"  # UserModel → UserEntity
```

---

### Scenario 4: Custom Display Attribute

You want the "last_name" column to be shown in dropdowns for the users table:

**`project.yml`:**
```yaml
connections:
  - connection: mydb
    host: localhost
    database: myapp
    connector: database.mysqlconnector.MysqlConnector

# Override attribute hints
attribute_hints:
  defaults: ["name", "title"]
  overrides:
    users: ["last_name", "first_name"]  # Try last_name first
    products: ["product_name", "sku"]
```

---

### Scenario 5: Multiple Database Connections

```yaml
connections:
  - connection: main_db
    host: prod.example.com
    database: production
    connector: database.mysqlconnector.MysqlConnector

  - connection: backup_db
    host: backup.example.com
    database: backup
    connector: database.mysqlconnector.MysqlConnector

# Settings apply to all connections
naming:
  table:
    case_in_code: "PascalCase"
```

---

## 🔐 Security - Password Management

### Option 1: Direct in config (⚠️ Not recommended)
```yaml
password: mypassword
```

### Option 2: Environment Variable (✅ Recommended)
```yaml
password_from_env: DB_PASSWORD
```

Then set before running:
```bash
export DB_PASSWORD=mypassword
python3 pystoorm.py project.yml
```

### Option 3: File (✅ Recommended)
```yaml
password_from_file: ~/.credentials/db.pass
```

Create `~/.credentials/db.pass`:
```
mypassword
```

---

## 🎯 Full Example: Real Database

Let's say you have a database with:
- `users` table (id, first_name, last_name, email)
- `orders` table (order_id, user_id, order_date)
- `products` table (product_id, product_name, price)

**Your `project.yml`:**

```yaml
# Database connection
connections:
  - connection: ecommerce
    host: localhost
    username: shop_user
    password_from_env: SHOP_DB_PASS
    database: ecommerce_db
    connector: database.mysqlconnector.MysqlConnector
    port: 3306

# Paths
project_root: /home/user/my-shop
output_dir: ${project_root}/app/orm

# Custom naming for your database
naming:
  primary_key:
    patterns: ["^{table_singular}_id$", "^id$"]

  table:
    case_in_code: "PascalCase"

# Custom style
style:
  class_naming:
    suffix: "Model"

# Display attributes
attribute_hints:
  defaults: ["name", "title"]
  overrides:
    users: ["last_name", "first_name"]  # Show "last_name" in dropdowns
    products: ["product_name"]
```

**Run it:**
```bash
export SHOP_DB_PASS=secret123
python3 pystoorm.py /home/user/my-shop/project.yml
```

**Output:**
```
app/orm/
├── model/
│   ├── User.py
│   ├── Order.py
│   └── Product.py
```

---

## 🛠️ Advanced: Project-Specific Overrides

You can create separate override files in your project directory:

```
my_project/
├── project.yml                    # Main config (required)
├── naming-conventions.yml         # Override naming (optional)
├── style-guide.yml               # Override style (optional)
└── attribute-hints.yml           # Override hints (optional)
```

**Example: `my_project/naming-conventions.yml`**
```yaml
naming:
  primary_key:
    patterns: ["^id$"]
  foreign_key:
    patterns: ["^{other_table}_id$"]
```

This file is loaded AFTER `project.yml` and overrides it.

---

## 🔍 Debugging

### See what configuration is loaded

Enable debug logging:

```yaml
# project.yml
logging:
  level: DEBUG
```

This will print all loaded configuration files.

### Pretty-print the configuration

In your code:
```python
from pystoorm.config.loader import ConfigLoader

loader = ConfigLoader()
loader.load_defaults().load_project("project.yml")
loader.pretty_print()  # Print entire configuration
```

---

## 📖 Configuration Reference

### `naming.primary_key`
```yaml
primary_key:
  patterns: [regex patterns]  # Match PK columns
  code_name_pattern: "{table_singular}_id"  # How to name in code
```

### `naming.table`
```yaml
table:
  singular_form_in_code: true   # Use singular in Python classes
  case_in_code: "PascalCase"    # PascalCase, camelCase, snake_case
  case_in_db: "snake_case"      # How it appears in database
```

### `style.class_naming`
```yaml
class_naming:
  case: "PascalCase"     # PascalCase, camelCase, snake_case
  suffix: "Model"        # Appended to class name
  prefix: ""             # Prepended to class name
```

### `attribute_hints`
```yaml
attribute_hints:
  defaults: [list of column names]     # Try in order
  overrides:
    table_name: [column names]         # Table-specific
  fallback: ["id"]                      # Final fallback
```

---

## 🆘 Troubleshooting

**Q: "Configuration file not found"**
- Make sure your `project.yml` path is correct
- Use absolute paths: `/full/path/to/project.yml`

**Q: "Error parsing YAML"**
- Check YAML syntax (indentation matters!)
- Use an online YAML validator

**Q: Database connection fails**
- Verify host, username, password
- Check port (default: 3306 for MySQL, 5432 for PostgreSQL)
- Make sure database exists

**Q: Generated class names are wrong**
- Check `naming.primary_key.patterns` matches your database
- Check `naming.table.case_in_code` setting
- Enable DEBUG logging to see pattern matching

---

## 📝 Next Steps

1. **Create your `project.yml`** with database connection
2. **Run pyStoOrm**: `python3 pystoorm.py project.yml`
3. **Check generated code** in output directory
4. **Customize** naming/style/hints if needed
5. **Use generated ORM** in your application

Happy coding! 🚀
