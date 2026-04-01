#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PostgreSQL database connector using psycopg2"""
__author__ = "Harald Stowasser"
import logging
from .connector import Connector
from .table import Table
from .column import Column
from .schema import Schema
from .reference import Reference

try:
    import psycopg2
    from psycopg2.extras import DictCursor
except ImportError:
    raise ImportError("psycopg2 is required for PostgreSQL support. Install with: pip install psycopg2-binary")

logger = logging.getLogger(__name__)


class PostgresqlConnector(Connector):
    """PostgreSQL connector using psycopg2."""

    con = None
    args = None

    def _build_args(self):
        """Build connection args from config."""
        if self.config:
            self.args = {
                'host': self.config.get('host', 'localhost'),
                'port': int(self.config.get('port', 5432)),
                'database': self.config.get('database', ''),
                'user': self.config.get('user', 'postgres'),
                'password': self.config.get('password', ''),
            }
            # Remove None/empty values
            self.args = {k: v for k, v in self.args.items() if v}

    def set_config(self, config):
        """Set configuration and build args."""
        logger.debug(f"set_config called with: {config}")
        super().set_config(config)
        logger.debug(f"After super().set_config(), self.config is: {self.config}")
        self._build_args()
        logger.debug(f"After _build_args(), self.args is: {self.args}")

    def get_cursor(self):
        """Get a cursor from the connection."""
        if self.con is None:
            self.connect()
        return self.con.cursor(cursor_factory=DictCursor)

    def connect(self):
        """Connect to PostgreSQL database."""
        logger.debug(f"connect() called. self.args = {self.args}")
        if not self.args:
            logger.error("self.args is None or empty! Trying to build args...")
            self._build_args()
            logger.debug(f"After _build_args(), self.args = {self.args}")

        logger.debug(f'Connecting to PostgreSQL {self.args.get("user", "unknown")}@{self.args.get("host", "unknown")}:{self.args.get("port", 5432)}/{self.args.get("database", "unknown")}')
        logger.debug(f'Used params: {", ".join(self.args.keys())}')
        logger.debug(f'Full args dict: {self.args}')

        try:
            self.con = psycopg2.connect(**self.args)
            logger.info("Successfully connected to PostgreSQL")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def get_schema(self):
        """Get all table names from the database."""
        cur = self.get_cursor()
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        table_names = [row['table_name'] for row in cur.fetchall()]
        cur.close()
        return Schema(self.args['database'], table_names)

    def get_table(self, table):
        """Get all column names from a table."""
        cur = self.get_cursor()
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        column_names = [row['column_name'] for row in cur.fetchall()]
        cur.close()
        return Table(table, "flat", column_names)

    def get_column(self, table, column):
        """Get detailed column information."""
        cur = self.get_cursor()

        # Get basic column info
        cur.execute("""
            SELECT
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        """, (table, column))

        result = cur.fetchone()
        if not result:
            cur.close()
            raise ValueError(f"Column {column} not found in table {table}")

        data_type = result['data_type']
        is_nullable = result['is_nullable'] == 'YES'
        column_default = result['column_default']
        length = result['character_maximum_length'] or result['numeric_precision'] or 0

        # Determine if it's a primary key
        is_pk = 'PRI'
        cur.execute("""
            SELECT constraint_type
            FROM information_schema.key_column_usage kcu
            JOIN information_schema.table_constraints tc
                ON kcu.constraint_name = tc.constraint_name
            WHERE kcu.table_schema = 'public' AND kcu.table_name = %s
            AND kcu.column_name = %s AND tc.constraint_type = 'PRIMARY KEY'
        """, (table, column))

        pk_result = cur.fetchone()
        if not pk_result:
            is_pk = None

        # Create Column object
        ret = Column(column, data_type, is_nullable, is_pk, column_default, length)

        # Get foreign key references (this table references others)
        # In PostgreSQL, we use constraint_column_usage to find what this column references
        cur.execute("""
            SELECT
                ccu.table_schema,
                ccu.table_name,
                ccu.column_name
            FROM information_schema.key_column_usage kcu
            JOIN information_schema.constraint_column_usage ccu
                ON kcu.constraint_name = ccu.constraint_name
                AND kcu.table_schema = ccu.table_schema
            WHERE kcu.table_schema = 'public' AND kcu.table_name = %s
            AND kcu.column_name = %s
            AND ccu.table_name IS NOT NULL
            AND ccu.table_name != kcu.table_name
        """, (table, column))

        for row in cur.fetchall():
            if row['table_name']:
                ret.add_ref_to(Reference(row['table_schema'] or 'public', row['table_name'], row['column_name']))

        # Get reverse foreign key references (other tables reference this)
        # Find all FK constraints that reference this table and column
        cur.execute("""
            SELECT DISTINCT
                kcu.table_schema,
                kcu.table_name,
                kcu.column_name
            FROM information_schema.key_column_usage kcu
            JOIN information_schema.constraint_column_usage ccu
                ON kcu.constraint_name = ccu.constraint_name
                AND kcu.table_schema = ccu.table_schema
            WHERE ccu.table_schema = 'public' AND ccu.table_name = %s
            AND ccu.column_name = %s
            AND kcu.table_name != ccu.table_name
        """, (table, column))

        for row in cur.fetchall():
            ret.add_ref_from(Reference(row['table_schema'] or 'public', row['table_name'], row['column_name']))

        cur.close()
        return ret
