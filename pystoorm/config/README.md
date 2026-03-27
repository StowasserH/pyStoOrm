# pyStoOrm Configuration System

This directory contains the hierarchical configuration system for pyStoOrm.

## 📁 Directory Structure

```
config/
├── defaults/                    ← Built-in default configurations
│   ├── bootstrap.yml           ← Output templates, logging (Level 1)
│   ├── naming-conventions.yml  ← PK/FK patterns (Level 2)
│   ├── attribute-hints.yml     ← Display column hints (Level 4)
│   └── style-guides/
│       └── python-pep8.yml     ← Python code style (Level 3)
│
├── projects/                    ← Project-specific configurations
│   └── example/
│       └── project.yml         ← Your database connection (Level 5)
│
├── loader.py                    ← ConfigLoader class
└── __init__.py
```

## 🔄 Configuration Loading Hierarchy

Configurations are loaded **in order** and each level can override the previous:

```
Level 1: bootstrap.yml
    ↓
Level 2: naming-conventions.yml
    ↓
Level 3: style-guides/python-pep8.yml
    ↓
Level 4: attribute-hints.yml
    ↓
Level 5: project.yml + optional project-specific overrides
    ↓
FINAL CONFIGURATION (all merged)
```

**Key Point:** Only values you specify override defaults. The rest stays the same.

## 🎯 What Each File Does

### 1. `bootstrap.yml` - Output & Logging
Defines where code is generated and logging configuration.

**Your most basic example:**
```yaml
logging:
  level: INFO

output:
  - from: ./pystoorm/templates/python/model.py
    to: ${project}/orm/model/[table].py
```

### 2. `naming-conventions.yml` - How Columns Are Identified
Patterns for detecting primary keys, foreign keys, and special columns.

**Example:**
```yaml
naming:
  primary_key:
    patterns: ["^id$", "^{table_singular}_id$"]

  table:
    case_in_code: "PascalCase"  # How to name classes
```

### 3. `style-guides/python-pep8.yml` - Code Formatting
Controls how generated Python code looks.

**Example:**
```yaml
style:
  class_naming:
    suffix: "Model"  # Creates "UserModel" not just "User"
  formatting:
    indent: 4
    use_type_hints: true
```

### 4. `attribute-hints.yml` - Display Columns
Which column should be shown in dropdowns/lists (the "attitüde").

**Example:**
```yaml
attribute_hints:
  defaults: ["name", "title"]
  overrides:
    users: ["last_name", "first_name"]
```

### 5. `projects/*/project.yml` - YOUR Configuration
**This is where YOU provide:**
- Database connection details
- Any overrides to defaults

**Example:**
```yaml
connections:
  - connection: mydb
    host: localhost
    username: root
    password: secret
    database: myapp
    connector: database.mysqlconnector.MysqlConnector

# Optional: override any defaults
naming:
  primary_key:
    patterns: ["^pk_{table}$"]  # Your custom pattern
```

## 🚀 How to Use (Users)

### Minimal Setup

1. Create `my_project/project.yml`:
```yaml
connections:
  - connection: mydb
    host: localhost
    username: root
    password: mypass
    database: mydb
    connector: database.mysqlconnector.MysqlConnector
```

2. Run:
```bash
python3 pystoorm.py my_project/project.yml
```

That's it! All defaults are applied automatically.

### Custom Setup

If you need custom naming or style:

1. Create `my_project/project.yml` with overrides:
```yaml
connections:
  - connection: mydb
    host: localhost
    database: mydb
    connector: database.mysqlconnector.MysqlConnector

# Override naming conventions
naming:
  primary_key:
    patterns: ["^id$", "^pk_{table}$"]

# Override style
style:
  class_naming:
    suffix: "Entity"  # Creates "UserEntity"
```

2. Run:
```bash
python3 pystoorm.py my_project/project.yml
```

## 💻 How to Use (Developers)

### Load Configuration in Code

```python
from pystoorm.config.loader import ConfigLoader, load_config

# Method 1: Using ConfigLoader
loader = ConfigLoader()
loader.load_defaults().load_project("my_project/project.yml")
config = loader.get_config()

# Method 2: Convenience function
config = load_config("my_project/project.yml")

# Access values
log_level = config['logging']['level']
naming_patterns = config['naming']['primary_key']['patterns']

# Or with dotted notation
log_level = loader.get('logging.level')
```

### Add New Configuration Options

1. Add to appropriate default file (e.g., `defaults/naming-conventions.yml`)
2. Load in ConfigLoader (already handles all files)
3. Access via config dict in your code

## 🔐 Security

### Password Management

**Option 1: Environment Variable** (Recommended)
```yaml
password_from_env: DB_PASSWORD
```
```bash
export DB_PASSWORD=mypassword
python3 pystoorm.py project.yml
```

**Option 2: File** (Recommended)
```yaml
password_from_file: ~/.credentials/db.pass
```

**Option 3: Direct** (Not Recommended)
```yaml
password: mypassword
```

## 📝 Examples

### Example 1: Override Naming Convention
Your database uses `pk_table` for primary keys:

```yaml
# project.yml
naming:
  primary_key:
    patterns: ["^pk_{table_singular}$"]
```

### Example 2: Override Style
You want classes named like `UserEntity`:

```yaml
# project.yml
style:
  class_naming:
    suffix: "Entity"
```

### Example 3: Override Display Attributes
You want `last_name` shown for users:

```yaml
# project.yml
attribute_hints:
  overrides:
    users: ["last_name", "first_name"]
```

### Example 4: Multiple Project Directories
All projects share the same defaults:

```
pystoorm/config/defaults/  ← Shared defaults
project_a/project.yml      ← Project A connection
project_b/project.yml      ← Project B connection
project_c/project.yml      ← Project C connection
```

## 🧪 Testing

```bash
python3 -m pytest tests/test_config_loader.py -v
```

**Expected output:**
```
16 passed in 0.16s
```

## 🔗 Related Files

- **CONFIG_QUICK_START.md** - User guide with examples
- **CONFIGURATION_STRATEGY.md** - Detailed architecture explanation
- **INTEGRATION_GUIDE.md** - How to integrate with templates
- **loader.py** - ConfigLoader implementation

## 🚀 Next Steps

1. Users: Create `project.yml` with database connection
2. Developers: Update Coordinator to use naming/style/hints from config
3. Developers: Update templates to accept configuration values

See **INTEGRATION_GUIDE.md** for detailed integration steps.
