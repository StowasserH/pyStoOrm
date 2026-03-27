#!/bin/bash
# pyStoOrm Sample Project - Batch Generator
#
# This script demonstrates the pyStoOrm workflow:
# 1. Prepares the SQLite database from SQL file
# 2. Runs pyStoOrm to generate ORM code
# 3. Shows the generated structure

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_FILE="$SCRIPT_DIR/classicmodels.db"
SQL_FILE="$SCRIPT_DIR/sqlightsampledatabase.sql"
PROJECT_YML="$SCRIPT_DIR/project.yml"
GENERATED_DIR="$SCRIPT_DIR/generated"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "==========================================="
echo "pyStoOrm Sample Project - Batch Generator"
echo "==========================================="
echo ""

# Step 1: Check if SQLite SQL file exists
echo "[1/3] Preparing SQLite database..."

if [ ! -f "$SQL_FILE" ]; then
    echo "      ✗ SQLite SQL file not found: $SQL_FILE"
    echo "      Run: python3 convert_mysql_to_sqlite.py"
    exit 1
fi

# Remove old database
rm -f "$DB_FILE"
echo "      ✓ Cleaned old database"

# Create database from SQL file using Python
python3 << PYTHON_EOF
import sqlite3

with open('$SQL_FILE', 'r', encoding='utf-8') as f:
    sql_content = f.read()

try:
    conn = sqlite3.connect('$DB_FILE')
    cursor = conn.cursor()

    # Execute all SQL statements
    cursor.executescript(sql_content)
    conn.commit()

    # Count tables
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    table_count = cursor.fetchone()[0]

    conn.close()
    print(f"      ✓ Database created with {table_count} tables")
except Exception as e:
    print(f"      ✗ Failed to create database: {e}")
    import sys
    sys.exit(1)
PYTHON_EOF
echo ""

# Step 2: Remove old generated files and generate code
echo "[2/3] Generating ORM code from schema..."
rm -rf "$GENERATED_DIR"

# Create temporary project.yml with absolute paths for templates
TEMPLATES_DIR="$PROJECT_ROOT/pystoorm/templates"
TEMP_YML=$(mktemp)

python3 << YAML_EOF
import yaml
import os

with open('$PROJECT_YML', 'r') as f:
    config = yaml.safe_load(f)

# Make output_dir and template paths absolute
config['output_dir'] = '$GENERATED_DIR'

if 'output' in config:
    for template in config['output']:
        if 'from' in template:
            rel_path = template['from']
            if not os.path.isabs(rel_path):
                # Extract template type and name
                parts = rel_path.split('/')
                template_name = parts[-1]
                template_type = parts[-2]
                template['from'] = os.path.join('$TEMPLATES_DIR', template_type, template_name)

with open('$TEMP_YML', 'w') as f:
    yaml.dump(config, f)
YAML_EOF

# Run pyStoOrm via CLI with absolute paths
python3 "$PROJECT_ROOT/pyStoOrm.py" "$TEMP_YML" || {
    rm -f "$TEMP_YML"
    echo "      ✗ Code generation failed"
    exit 1
}

rm -f "$TEMP_YML"
echo ""

# Step 3: Show generated structure
echo "[3/3] Generated files structure:"
echo ""

if [ -d "$GENERATED_DIR" ]; then
    tree "$GENERATED_DIR" 2>/dev/null || find "$GENERATED_DIR" -type f | sort | sed "s|$GENERATED_DIR||" | sed 's|^/||' | awk '{print "      " $0}'
    echo ""

    echo "Summary:"
    MODELS=$(find "$GENERATED_DIR/models" -name '*.py' 2>/dev/null | wc -l)
    REPOS=$(find "$GENERATED_DIR/repositories" -name '*.py' 2>/dev/null | wc -l)
    BUILDERS=$(find "$GENERATED_DIR/builders" -name '*.py' 2>/dev/null | wc -l)
    ERD=$(find "$GENERATED_DIR/erd" -name '*.dot' 2>/dev/null | wc -l)

    echo "  Models:       $MODELS files"
    echo "  Repositories: $REPOS files"
    echo "  Builders:     $BUILDERS files"
    echo "  ERD Diagram:  $ERD files"
else
    echo "      ✗ No generated files found"
fi

echo ""
echo "==========================================="
echo "✓ Sample project generation complete!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "  1. Review generated models in:   $GENERATED_DIR/models/"
echo "  2. Review generated repositories in: $GENERATED_DIR/repositories/"
echo "  3. Review generated builders in: $GENERATED_DIR/builders/"
echo "  4. View ER-diagram:              $GENERATED_DIR/erd/"
echo "  5. Run example_usage.py:         python3 example_usage.py"
echo "  6. Run test_sqlbuilder.py:       python3 test_sqlbuilder.py"
echo ""
