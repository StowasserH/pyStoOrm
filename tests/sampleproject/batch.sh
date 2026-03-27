#!/bin/bash
# pyStoOrm Sample Project Batch Script
# This script demonstrates the complete pyStoOrm workflow:
# 1. Converts MySQL sample data to SQLite
# 2. Generates ORM models, repositories, and ER-diagrams
# 3. Shows structure of generated files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_FILE="$SCRIPT_DIR/classicmodels.db"
GENERATED_DIR="$SCRIPT_DIR/generated"
PROJECT_YML="$SCRIPT_DIR/project.yml"

echo "=========================================="
echo "pyStoOrm Sample Project - Batch Generator"
echo "=========================================="
echo ""

# Step 1: Remove old database and generated files
echo "[1/4] Cleaning up old files..."
rm -f "$DB_FILE"
rm -rf "$GENERATED_DIR"
echo "      ✓ Cleaned"
echo ""

# Step 2: Create SQLite database from MySQL sample data
echo "[2/4] Loading MySQL sample data into SQLite..."

python3 << 'SQL_EOF'
import sqlite3
import re

db_file = 'classicmodels.db'
sql_file = 'mysqlsampledatabase.sql'

try:
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()

    conn = sqlite3.connect(db_file)
    conn.isolation_level = None
    cursor = conn.cursor()

    # Extract and process CREATE TABLE statements
    create_table_pattern = r'CREATE TABLE `(\w+)`\s*\((.*?)\)\s*ENGINE'
    for match in re.finditer(create_table_pattern, content, re.IGNORECASE | re.DOTALL):
        table_name = match.group(1)
        table_def = match.group(2)

        # Clean column definitions
        # Remove simple KEY constraints (but keep CONSTRAINT FOREIGN KEY)
        table_def = re.sub(r',\s*KEY\s+`\w+`\s*\([^)]+\)', '', table_def, flags=re.IGNORECASE)

        # Convert types
        table_def = re.sub(r'\bint\(\d+\)', 'INTEGER', table_def, flags=re.IGNORECASE)
        table_def = re.sub(r'\bvarchar\(\d+\)', 'TEXT', table_def, flags=re.IGNORECASE)
        table_def = re.sub(r'\bdecimal\(\d+,\d+\)', 'REAL', table_def, flags=re.IGNORECASE)
        table_def = re.sub(r'\b(datetime|date)\b', 'TEXT', table_def, flags=re.IGNORECASE)
        table_def = re.sub(r'\benum\([^)]*\)', 'TEXT', table_def, flags=re.IGNORECASE)

        # Remove backticks
        table_def = table_def.replace('`', '')
        table_name = table_name.replace('`', '')

        sql_stmt = f'CREATE TABLE {table_name} ({table_def})'
        try:
            cursor.execute(sql_stmt)
        except sqlite3.Error as e:
            pass

    # Process INSERT statements more carefully
    # Split by "insert into" to find all insert blocks
    insert_blocks = re.split(r'insert\s+into', content, flags=re.IGNORECASE)

    for block in insert_blocks[1:]:  # Skip first split (before first insert)
        # Parse the table name and values
        match = re.match(r'\s+`?(\w+)`?\s*\([^)]+\)\s*values?\s*(.*)', block, re.IGNORECASE | re.DOTALL)
        if match:
            table_name = match.group(1)
            values_str = match.group(2)

            # Extract individual value tuples
            # This regex finds (val1, val2, ...) patterns
            value_pattern = r'\((?:[^()]*|(?:\([^()]*\)))*\)'
            for val_match in re.finditer(value_pattern, values_str):
                val_tuple = val_match.group(0)
                # Clean up
                val_tuple = val_tuple.replace('`', '')
                insert_stmt = f'INSERT INTO {table_name} VALUES {val_tuple}'
                try:
                    cursor.execute(insert_stmt)
                except sqlite3.Error:
                    # Continue on error - some inserts may fail
                    pass

    conn.close()

    # Verify tables
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    print('      ✓ Database created: ' + db_file)
    print('      ✓ Tables created: ' + str(len(tables)))
    if tables:
        print('      ✓ Tables: ' + ', '.join(tables))

except Exception as e:
    print('      ✗ Error: ' + str(e))
    import traceback
    traceback.print_exc()
    exit(1)
SQL_EOF
echo ""

# Step 3: Run pyStoOrm
echo "[3/4] Running pyStoOrm to generate models and repositories..."
cd "$SCRIPT_DIR"

# Get the absolute path to the project root
PROJECT_ROOT="$(cd ../../ && pwd)"
TEMPLATES_DIR="$PROJECT_ROOT/pystoorm/templates"

python3 << PYTHON_EOF
import sys
import os
sys.path.insert(0, '$PROJECT_ROOT')

# Load config
import yaml

config_file = '$PROJECT_YML'
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

# Make paths absolute
templates_dir = '$TEMPLATES_DIR'
project_abs_dir = '$SCRIPT_DIR'
db_path = os.path.join(project_abs_dir, 'classicmodels.db')

# Update database path to absolute
if 'connections' in config:
    for conn in config['connections']:
        if 'database' in conn:
            rel_db = conn['database']
            if not os.path.isabs(rel_db):
                conn['database'] = os.path.join(project_abs_dir, rel_db)

# Update output paths to absolute
if 'output_dir' in config:
    output_dir = config['output_dir']
    if '\${project_root}' in output_dir:
        config['output_dir'] = output_dir.replace('\${project_root}', project_abs_dir)
    elif not os.path.isabs(output_dir):
        config['output_dir'] = os.path.join(project_abs_dir, output_dir)

# Update template paths to absolute
if 'output' in config:
    for template in config['output']:
        if 'from' in template:
            rel_path = template['from']
            if not os.path.isabs(rel_path):
                template_name = os.path.basename(rel_path)
                template_type = os.path.dirname(rel_path).split('/')[-1]
                abs_path = os.path.join(templates_dir, template_type, template_name)
                template['from'] = abs_path
        if 'to' in template:
            to_path = template['to']
            if '\${output_dir}' in to_path:
                template['to'] = to_path.replace('\${output_dir}', config['output_dir'])
            elif '\${project_root}' in to_path:
                template['to'] = to_path.replace('\${project_root}', project_abs_dir)

# Write modified config to temp file
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
    yaml.dump(config, f)
    temp_config = f.name

sys.argv = ['pystoorm', '--config', temp_config]

# Import and run main
from pystoorm.pystoorm import main
try:
    main()
finally:
    os.unlink(temp_config)
PYTHON_EOF

echo "      ✓ Generation complete"
echo ""

# Step 4: Show generated structure
echo "[4/4] Generated files structure:"
echo ""

if [ -d "$GENERATED_DIR" ]; then
    tree "$GENERATED_DIR" 2>/dev/null || find "$GENERATED_DIR" -type f | sort | sed 's|'"$GENERATED_DIR"'||' | sed 's|^/||' | awk '{print "      " $0}'
    echo ""

    echo "Summary:"
    echo "  Models:       $(find $GENERATED_DIR/models -name '*.py' 2>/dev/null | wc -l) files"
    echo "  Repositories: $(find $GENERATED_DIR/repositories -name '*.py' 2>/dev/null | wc -l) files"
    echo "  ERD Diagram:  $(find $GENERATED_DIR/erd -name '*.dot' 2>/dev/null | wc -l) files"
else
    echo "      ✗ No generated files found"
fi

echo ""
echo "=========================================="
echo "✓ Sample project generation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Review generated models in:   $GENERATED_DIR/models/"
echo "  2. Review generated repositories in: $GENERATED_DIR/repositories/"
echo "  3. View ER-diagram:              $GENERATED_DIR/erd/"
echo "  4. Run example_usage.py:         python3 example_usage.py"
echo ""
