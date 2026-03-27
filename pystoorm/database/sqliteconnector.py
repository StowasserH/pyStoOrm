#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SQLite Database Connector for pyStoOrm

Provides SQLite database connection and schema introspection.
"""
__author__ = "Harald Stowasser"

import logging
import sqlite3
from pathlib import Path
from .connector import Connector
from .table import Table
from .column import Column
from .schema import Schema

logger = logging.getLogger(__name__)


class SqliteConnector(Connector):
    """SQLite database connector implementing the Connector interface."""

    con = None

    # SQLite type mappings to Python types
    SQLITE_TYPE_MAP = {
        'INTEGER': 'int',
        'REAL': 'float',
        'TEXT': 'str',
        'BLOB': 'bytes',
        'NULL': 'None',
        'NUMERIC': 'float',
        'BOOLEAN': 'bool',
    }

    def get_cursor(self):
        """Get or create a database cursor.

        Returns:
            sqlite3.Cursor: Database cursor
        """
        if self.con is None:
            self.connect()
        return self.con.cursor()

    def connect(self):
        """Connect to SQLite database.

        Config keys:
            database: Path to SQLite database file (or ':memory:' for in-memory DB)

        Raises:
            sqlite3.Error: If connection fails
        """
        db_path = self.config.get('database', ':memory:')
        logger.info(f"Connecting to SQLite database: {db_path}")

        try:
            # For file-based databases, ensure directory exists
            if db_path != ':memory:':
                db_file = Path(db_path)
                db_file.parent.mkdir(parents=True, exist_ok=True)

            self.con = sqlite3.connect(db_path)
            # Enable foreign keys (important for some operations)
            self.con.execute("PRAGMA foreign_keys = ON")
            logger.info("Successfully connected to SQLite")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise

    def get_schema(self):
        """Get all table names from the database.

        Returns:
            Schema: Schema object containing database name and table names
        """
        cur = self.get_cursor()
        try:
            # Query SQLite master table for all user tables
            query = """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """
            cur.execute(query)
            table_names = [row[0] for row in cur.fetchall()]

            # Use config database name or default
            db_name = self.config.get('database', 'sqlite')
            if db_name == ':memory:':
                db_name = 'memory'

            logger.debug(f"Found {len(table_names)} tables: {table_names}")
            schema = Schema(db_name, table_names)

            # Populate tables with their columns and relationships
            for table_name in table_names:
                table = self.get_table(table_name)
                # Populate columns
                for col_name in table.column_names:
                    col = self.get_column(table_name, col_name)
                    table.columns[col_name] = col
                # Get relationships
                table.relationships = self._get_foreign_keys(table_name)
                schema.tables[table_name] = table

            return schema
        finally:
            cur.close()

    def get_table(self, table):
        """Get all column names for a table.

        Args:
            table: Table name

        Returns:
            Table: Table object containing column names and column details
        """
        cur = self.get_cursor()
        try:
            # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
            query = f"PRAGMA table_info({table})"
            cur.execute(query)

            columns = cur.fetchall()
            if not columns:
                raise ValueError(f"Table {table} not found")

            column_names = [col[1] for col in columns]
            logger.debug(f"Found {len(column_names)} columns in {table}: {column_names}")

            table_obj = Table(table, "flat", column_names)

            # Populate column details
            for col_name in column_names:
                col = self.get_column(table, col_name)
                table_obj.columns[col_name] = col

            # Get relationships
            table_obj.relationships = self._get_foreign_keys(table)

            return table_obj
        finally:
            cur.close()

    def get_column(self, table, column):
        """Get detailed information about a specific column.

        Args:
            table: Table name
            column: Column name

        Returns:
            Column: Column object with type, nullable, key info, etc.

        Raises:
            ValueError: If column not found
        """
        cur = self.get_cursor()
        try:
            # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
            query = f"PRAGMA table_info({table})"
            cur.execute(query)

            columns = cur.fetchall()
            if not columns:
                raise ValueError(f"Table {table} not found")

            # Find the requested column
            col_info = None
            for col in columns:
                if col[1] == column:
                    col_info = col
                    break

            if col_info is None:
                raise ValueError(f"Column {column} not found in table {table}")

            # Parse PRAGMA table_info result
            cid, col_name, col_type, not_null, default_value, is_pk = col_info

            # Determine the key type
            key_type = "PRI" if is_pk else ""

            # Normalize type name (SQLite is flexible with types)
            normalized_type = self._normalize_type(col_type)

            # Check for nullable (SQLite: not_null=0 means nullable, not_null=1 means NOT NULL)
            # Primary keys are always NOT NULL
            is_nullable = (not bool(not_null)) and (not is_pk)

            # Extract length from type (e.g., "VARCHAR(50)" -> 50)
            length = self._extract_length(col_type)

            logger.debug(
                f"Column: {col_name}, Type: {normalized_type}, "
                f"Nullable: {is_nullable}, Key: {key_type}, Length: {length}"
            )

            return Column(
                name=col_name,
                type=normalized_type,
                nullable=is_nullable,
                key=key_type,
                default=default_value,
                length=length
            )
        finally:
            cur.close()

    @staticmethod
    def _normalize_type(sqlite_type):
        """Normalize SQLite type to standard type name.

        SQLite is flexible with types and doesn't enforce them strictly.
        This function normalizes common type declarations.

        Args:
            sqlite_type: Type string from SQLite (e.g., "VARCHAR(50)", "INT")

        Returns:
            str: Normalized type name
        """
        if not sqlite_type:
            return 'TEXT'

        # Convert to uppercase for comparison
        type_upper = sqlite_type.upper()

        # Check for exact matches first
        for sqlite_type_key, python_type in SqliteConnector.SQLITE_TYPE_MAP.items():
            if type_upper.startswith(sqlite_type_key):
                return python_type

        # If no exact match, try to infer from type characteristics
        if 'INT' in type_upper:
            return 'int'
        elif 'CHAR' in type_upper or 'CLOB' in type_upper:
            return 'str'
        elif 'BLOB' in type_upper:
            return 'bytes'
        elif 'REAL' in type_upper or 'FLOA' in type_upper or 'DOUB' in type_upper:
            return 'float'
        else:
            # Default to string
            return 'str'

    @staticmethod
    def _extract_length(type_string):
        """Extract length from type declaration.

        For VARCHAR(50), returns 50.
        For NUMERIC(10,2), returns 10 (the precision).

        Args:
            type_string: Type declaration (e.g., "VARCHAR(50)", "NUMERIC(10,2)")

        Returns:
            int: Length if found, 0 otherwise
        """
        if not type_string:
            return 0

        import re
        # Match first number in parentheses
        match = re.search(r'\((\d+)', type_string)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                return 0

        return 0

    def _get_foreign_keys(self, table):
        """Get all foreign key relationships for a table.

        Args:
            table: Table name

        Returns:
            list: List of dicts with foreign key information
        """
        cur = self.get_cursor()
        try:
            # PRAGMA foreign_key_list returns:
            # (id, seq, table, from, to, on_delete, on_update, match)
            query = f"PRAGMA foreign_key_list({table})"
            cur.execute(query)
            fks = cur.fetchall()

            relationships = []
            for fk in fks:
                rel = {
                    'local_column': fk[3],      # from column
                    'foreign_table': fk[2],     # table
                    'foreign_column': fk[4],    # to column
                }
                relationships.append(rel)
                logger.debug(f"Found FK in {table}: {rel['local_column']} -> {rel['foreign_table']}.{rel['foreign_column']}")

            return relationships
        except sqlite3.Error as e:
            logger.debug(f"Could not get foreign keys for {table}: {e}")
            return []
        finally:
            cur.close()

    def close(self):
        """Close database connection."""
        if self.con:
            self.con.close()
            self.con = None
            logger.info("SQLite connection closed")

    def __del__(self):
        """Ensure connection is closed on object destruction."""
        self.close()
