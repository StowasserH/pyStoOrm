#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert MySQL Sample Database to SQLite Format

This script converts mysqlsampledatabase.sql (MySQL format) to
sqlightsampledatabase.sql (SQLite format).

Usage:
    python3 convert_mysql_to_sqlite.py
"""
import re
import sqlite3
from pathlib import Path


def convert_mysql_to_sqlite(input_file, output_file):
    """
    Convert MySQL SQL to SQLite SQL format.

    Args:
        input_file: Path to MySQL SQL file
        output_file: Path to output SQLite SQL file
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove MySQL-specific comments and statements
    content = re.sub(r'--.*?$', '', content, flags=re.MULTILINE)  # Remove -- comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)  # Remove /* */ comments
    content = re.sub(r'^\s*SET .*?;$', '', content, flags=re.MULTILINE | re.IGNORECASE)
    content = re.sub(r'^\s*USE .*?;$', '', content, flags=re.MULTILINE | re.IGNORECASE)
    content = re.sub(r'^\s*DROP DATABASE.*?;$', '', content, flags=re.MULTILINE | re.IGNORECASE)
    content = re.sub(r'^\s*CREATE DATABASE.*?;$', '', content, flags=re.MULTILINE | re.IGNORECASE)

    # Fix escaped quotes early (MySQL uses \' but SQLite uses '')
    content = content.replace(r"\'", "''")

    # Process line by line for more reliable conversion
    lines = content.split('\n')
    output_lines = []
    in_create_table = False
    create_table_lines = []

    for line in lines:
        line_stripped = line.strip()

        # Skip empty lines
        if not line_stripped:
            continue

        # Detect start of CREATE TABLE
        if re.search(r'^CREATE TABLE `\w+`', line_stripped, re.IGNORECASE):
            in_create_table = True
            create_table_lines = [line_stripped]
            continue

        # Collect CREATE TABLE lines
        if in_create_table:
            create_table_lines.append(line_stripped)
            # Check if this line ends the CREATE TABLE
            if line_stripped.rstrip().endswith(';'):
                # Process collected CREATE TABLE
                full_create = ' '.join(create_table_lines)
                processed = process_create_table(full_create)
                output_lines.append(processed)
                in_create_table = False
                create_table_lines = []
            continue

        # Handle other statements
        if re.search(r'^INSERT', line_stripped, re.IGNORECASE):
            # Clean INSERT statement
            line_stripped = re.sub(r'INSERT\s+INTO\s+`(\w+)`', r'INSERT INTO \1', line_stripped, flags=re.IGNORECASE)
            line_stripped = re.sub(r'`', '', line_stripped)  # Remove backticks
            # Fix escaped single quotes (MySQL escapes with \' but SQLite uses '')
            line_stripped = line_stripped.replace(r"\'", "''")
            output_lines.append(line_stripped)
        elif re.search(r'^DROP TABLE', line_stripped, re.IGNORECASE):
            line_stripped = re.sub(r'`(\w+)`', r'\1', line_stripped)  # Remove backticks from table names
            output_lines.append(line_stripped)
        elif line_stripped and not line_stripped.startswith('--'):
            output_lines.append(line_stripped)

    # Join and clean
    content = '\n'.join(output_lines)
    content = re.sub(r'\n\s*\n', '\n', content)  # Remove blank lines
    content = content.strip()

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Successfully converted MySQL to SQLite format")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")


def process_create_table(create_stmt):
    """
    Process a CREATE TABLE statement.

    Converts MySQL syntax to SQLite syntax.
    """
    # Extract table name and definition
    match = re.search(r'CREATE TABLE `(\w+)`\s*\((.*)\)', create_stmt, re.IGNORECASE | re.DOTALL)
    if not match:
        return create_stmt

    table_name = match.group(1)
    table_def = match.group(2)

    # Remove trailing MySQL clauses
    table_def = re.sub(r'\)\s*ENGINE.*$', '', table_def, flags=re.IGNORECASE | re.DOTALL)
    table_def = re.sub(r',\s*ENGINE.*$', '', table_def, flags=re.IGNORECASE)

    # Remove simple KEY constraints (but keep FOREIGN KEY)
    table_def = re.sub(r',\s*KEY\s+`\w+`\s*\([^)]+\)', '', table_def, flags=re.IGNORECASE)
    table_def = re.sub(r',\s*UNIQUE\s+KEY\s+`\w+`\s*\([^)]+\)', '', table_def, flags=re.IGNORECASE)
    table_def = re.sub(r',\s*INDEX\s+`\w+`\s*\([^)]+\)', '', table_def, flags=re.IGNORECASE)

    # Convert MySQL types
    table_def = re.sub(r'\bint\(\d+\)', 'INTEGER', table_def, flags=re.IGNORECASE)
    table_def = re.sub(r'\bvarchar\(\d+\)', 'TEXT', table_def, flags=re.IGNORECASE)
    table_def = re.sub(r'\bdecimal\(\d+,\d+\)', 'REAL', table_def, flags=re.IGNORECASE)
    table_def = re.sub(r'\b(datetime|date|timestamp)\b', 'TEXT', table_def, flags=re.IGNORECASE)
    table_def = re.sub(r'\benum\([^)]*\)', 'TEXT', table_def, flags=re.IGNORECASE)
    table_def = re.sub(r'\btext\b', 'TEXT', table_def, flags=re.IGNORECASE)
    table_def = re.sub(r'\bdouble\b', 'REAL', table_def, flags=re.IGNORECASE)

    # Remove MySQL column modifiers
    table_def = re.sub(r'\s+AUTO_INCREMENT', '', table_def, flags=re.IGNORECASE)
    table_def = re.sub(r'\s+CHARACTER SET\s+\w+', '', table_def, flags=re.IGNORECASE)
    table_def = re.sub(r'\s+COLLATE\s+\w+', '', table_def, flags=re.IGNORECASE)
    table_def = re.sub(r'\s+COMMENT\s+\'[^\']*\'', '', table_def, flags=re.IGNORECASE)

    # Remove backticks
    table_def = table_def.replace('`', '')
    table_name = table_name.replace('`', '')

    # Clean up
    table_def = table_def.strip()
    if table_def.endswith(','):
        table_def = table_def[:-1]

    return f'CREATE TABLE {table_name} ({table_def});'


if __name__ == '__main__':
    convert_mysql_to_sqlite(
        'mysqlsampledatabase.sql',
        'sqlightsampledatabase.sql'
    )
