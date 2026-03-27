#!/bin/bash
# pyStoOrm Sample Project - Code Generator
#
# Generates ORM code (models, repositories, builders) from database schema.
# Prerequisites: Python 3 and pyStoOrm
#
# Usage:
#   bash batch.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_YML="$SCRIPT_DIR/project.yml"
GENERATED_DIR="$SCRIPT_DIR/generated"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "==========================================="
echo "pyStoOrm Code Generator"
echo "==========================================="
echo ""

# Remove old generated files
echo "[1/2] Cleaning old generated files..."
rm -rf "$GENERATED_DIR"
echo "      ✓ Cleaned"
echo ""

# Run pyStoOrm
echo "[2/2] Generating ORM code..."
python3 "$PROJECT_ROOT/pyStoOrm.py" "$PROJECT_YML"
echo ""

# Show structure
echo "[3/2] Generated files structure:"
echo ""

if [ -d "$GENERATED_DIR" ]; then
    tree "$GENERATED_DIR" 2>/dev/null || find "$GENERATED_DIR" -type f | sort | sed "s|$GENERATED_DIR||" | sed 's|^/||' | awk '{print "      " $0}'
    echo ""

    MODELS=$(find "$GENERATED_DIR/models" -name '*.py' 2>/dev/null | wc -l)
    REPOS=$(find "$GENERATED_DIR/repositories" -name '*.py' 2>/dev/null | wc -l)
    BUILDERS=$(find "$GENERATED_DIR/builders" -name '*.py' 2>/dev/null | wc -l)
    ERD=$(find "$GENERATED_DIR/erd" -name '*.dot' 2>/dev/null | wc -l)

    echo "Summary:"
    echo "  Models:       $MODELS files"
    echo "  Repositories: $REPOS files"
    echo "  Builders:     $BUILDERS files"
    echo "  ERD Diagram:  $ERD files"
else
    echo "      ✗ No generated files found"
fi

echo ""
echo "==========================================="
echo "✓ Code generation complete!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "  1. Review generated code in: $GENERATED_DIR/"
echo "  2. Run example_usage.py:    python3 example_usage.py"
echo "  3. Run test_sqlbuilder.py:  python3 test_sqlbuilder.py"
echo ""
