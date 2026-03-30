#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration Test - pyStoOrm with SQLite

Tests the complete workflow:
1. Create a test SQLite database
2. Create test tables and columns
3. Load configuration
4. Run database analyzer
5. Run code generator
6. Verify generated output
"""

import unittest
import sqlite3
import tempfile
import os
import shutil

from pystoorm.config.loader import ConfigLoader
from pystoorm.analyzer.controller import Controller
from pystoorm.generator.coordinator import Coordinator
from pystoorm.database.sqliteconnector import SqliteConnector
import re


class TestIntegrationSqlite(unittest.TestCase):
    """Integration tests for pyStoOrm with SQLite backend"""

    @classmethod
    def setUpClass(cls):
        """Set up test database and temporary directory"""
        # Create temporary directory for test outputs
        cls.temp_dir = tempfile.mkdtemp(prefix="pystoorm_test_")
        cls.test_db_path = os.path.join(cls.temp_dir, "test.db")
        cls.output_dir = os.path.join(cls.temp_dir, "generated")

        # Create test database with sample tables
        cls._create_test_database(cls.test_db_path)

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary files"""
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)

    @staticmethod
    def _create_test_database(db_path):
        """Create a test SQLite database with sample schema.

        Creates:
        - users table (id, username, email, created_at)
        - products table (id, name, price)
        - orders table (id, user_id, product_id, order_date)
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create products table
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT
            )
        """)

        # Create orders table with foreign keys
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # Insert sample data
        cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)",
                       ("john_doe", "john@example.com"))
        cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)",
                       ("jane_smith", "jane@example.com"))

        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)",
                       ("Laptop", 999.99))
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)",
                       ("Mouse", 29.99))

        cursor.execute("""
            INSERT INTO orders (user_id, product_id, quantity)
            VALUES (?, ?, ?)
        """, (1, 1, 1))

        conn.commit()
        conn.close()

    def test_sqlite_connector_connection(self):
        """Test basic SQLite connector connection"""
        config = {'database': self.test_db_path}
        connector = SqliteConnector(config)
        connector.connect()
        self.assertIsNotNone(connector.con)
        connector.close()

    def test_sqlite_connector_get_schema(self):
        """Test getting schema from SQLite database"""
        config = {'database': self.test_db_path}
        connector = SqliteConnector(config)
        connector.connect()

        schema = connector.get_schema()

        self.assertIsNotNone(schema)
        self.assertEqual(len(schema.table_names), 3)
        self.assertIn('users', schema.table_names)
        self.assertIn('products', schema.table_names)
        self.assertIn('orders', schema.table_names)

        connector.close()

    def test_sqlite_connector_get_table(self):
        """Test getting table columns from SQLite"""
        config = {'database': self.test_db_path}
        connector = SqliteConnector(config)
        connector.connect()

        table = connector.get_table('users')

        self.assertIsNotNone(table)
        self.assertEqual(table.name, 'users')
        self.assertEqual(len(table.column_names), 4)
        self.assertIn('id', table.column_names)
        self.assertIn('username', table.column_names)
        self.assertIn('email', table.column_names)
        self.assertIn('created_at', table.column_names)

        connector.close()

    def test_sqlite_connector_get_column(self):
        """Test getting column details from SQLite"""
        config = {'database': self.test_db_path}
        connector = SqliteConnector(config)
        connector.connect()

        column = connector.get_column('users', 'id')

        self.assertIsNotNone(column)
        self.assertEqual(column.name, 'id')
        self.assertEqual(column.key, 'PRI')  # Primary key
        self.assertFalse(column.nullable)

        column = connector.get_column('users', 'email')
        self.assertEqual(column.name, 'email')
        self.assertFalse(column.nullable)

        column = connector.get_column('products', 'description')
        self.assertTrue(column.nullable)  # Optional column

        connector.close()

    def test_sqlite_connector_column_not_found(self):
        """Test error handling for non-existent column"""
        config = {'database': self.test_db_path}
        connector = SqliteConnector(config)
        connector.connect()

        with self.assertRaises(ValueError):
            connector.get_column('users', 'nonexistent_column')

        connector.close()

    def test_full_integration_load_config(self):
        """Test loading configuration with SQLite connector"""
        # Create project config for SQLite
        config = {
            'logging': {'level': 'DEBUG'},
            'connections': [{
                'connection': 'test_db',
                'database': self.test_db_path,
                'connector': 'database.sqliteconnector.SqliteConnector'
            }],
            'output': [],
            'naming': {
                'primary_key': {'patterns': ['^id$']},
                'table': {'case_in_code': 'PascalCase'}
            },
            'style': {
                'class_naming': {'case': 'PascalCase', 'suffix': 'Model'}
            },
            'attribute_hints': {
                'defaults': ['name', 'username', 'title'],
                'fallback': ['id']
            }
        }

        self.assertIn('connections', config)
        self.assertEqual(len(config['connections']), 1)
        self.assertEqual(config['connections'][0]['database'], self.test_db_path)

    def test_full_integration_analyze_database(self):
        """Test complete database analysis with SQLite"""
        config = {
            'logging': {'level': 'INFO'},
            'connections': [{
                'connection': 'test_db',
                'database': self.test_db_path,
                'connector': 'database.sqliteconnector.SqliteConnector'
            }],
            'output': [],
            'naming': {
                'primary_key': {'patterns': ['^id$']},
                'table': {'case_in_code': 'PascalCase'}
            },
            'style': {
                'class_naming': {'case': 'PascalCase', 'suffix': 'Model'}
            },
            'attribute_hints': {
                'defaults': ['name', 'username'],
                'fallback': ['id']
            }
        }

        # Run analyzer
        analyzer = Controller(config)
        analyzer.walk()

        # Verify schema was parsed
        self.assertIn('parsedSchema', config['connections'][0])
        schema = config['connections'][0]['parsedSchema']

        self.assertIsNotNone(schema)
        self.assertEqual(len(schema.table_names), 3)

        # Verify tables
        self.assertIn('users', schema.tables)
        self.assertIn('products', schema.tables)
        self.assertIn('orders', schema.tables)

        # Verify users table columns
        users_table = schema.tables['users']
        self.assertEqual(len(users_table.columns), 4)
        self.assertIn('id', users_table.columns)
        self.assertIn('username', users_table.columns)

        # Verify column types
        id_column = users_table.columns['id']
        self.assertEqual(id_column.key, 'PRI')

    def test_full_integration_with_config_loader(self):
        """Test integration with ConfigLoader"""
        # Create a temporary project config file
        project_config_path = os.path.join(self.temp_dir, 'project.yml')

        with open(project_config_path, 'w') as f:
            f.write(f"""
connections:
  - connection: test_db
    database: {self.test_db_path}
    connector: database.sqliteconnector.SqliteConnector

project_root: {self.temp_dir}
output_dir: {self.output_dir}
""")

        # Load config using ConfigLoader
        loader = ConfigLoader()
        loader.load_defaults()

        # Load project config
        config_data = loader._load_yaml(project_config_path)
        loader._merge_deep(loader.config, config_data)

        config = loader.get_config()

        # Verify configuration
        self.assertIn('connections', config)
        self.assertEqual(config['connections'][0]['database'], self.test_db_path)

        # Run analyzer with loaded config
        analyzer = Controller(config)
        analyzer.walk()

        # Verify analysis completed
        schema = config['connections'][0]['parsedSchema']
        self.assertIsNotNone(schema)
        self.assertEqual(len(schema.table_names), 3)


class TestSqliteConnectorEdgeCases(unittest.TestCase):
    """Test edge cases for SQLite connector"""

    def setUp(self):
        """Set up test database"""
        self.temp_dir = tempfile.mkdtemp(prefix="pystoorm_edge_")
        self.db_path = os.path.join(self.temp_dir, "edge_test.db")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table with various column types
        cursor.execute("""
            CREATE TABLE test_types (
                int_col INTEGER,
                text_col TEXT,
                real_col REAL,
                blob_col BLOB,
                bool_col BOOLEAN,
                varchar_col VARCHAR(100),
                numeric_col NUMERIC(10,2)
            )
        """)

        conn.commit()
        conn.close()

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_type_normalization(self):
        """Test type normalization for various SQLite types"""
        config = {'database': self.db_path}
        connector = SqliteConnector(config)
        connector.connect()

        # Test integer type
        col = connector.get_column('test_types', 'int_col')
        self.assertEqual(col.type, 'int')

        # Test text type
        col = connector.get_column('test_types', 'text_col')
        self.assertEqual(col.type, 'str')

        # Test real type
        col = connector.get_column('test_types', 'real_col')
        self.assertEqual(col.type, 'float')

        # Test varchar type
        col = connector.get_column('test_types', 'varchar_col')
        self.assertEqual(col.type, 'str')

        connector.close()

    def test_length_extraction(self):
        """Test extracting length from type declarations"""
        config = {'database': self.db_path}
        connector = SqliteConnector(config)
        connector.connect()

        col = connector.get_column('test_types', 'varchar_col')
        self.assertEqual(col.length, 100)

        col = connector.get_column('test_types', 'numeric_col')
        self.assertEqual(col.length, 10)

        connector.close()

    def test_in_memory_database(self):
        """Test connector with in-memory SQLite database"""
        config = {'database': ':memory:'}
        connector = SqliteConnector(config)
        connector.connect()

        # Create a table in memory
        cursor = connector.get_cursor()
        cursor.execute("""
            CREATE TABLE memory_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        connector.con.commit()

        # Test schema retrieval
        schema = connector.get_schema()
        self.assertIn('memory_table', schema.table_names)

        # Test table retrieval
        table = connector.get_table('memory_table')
        self.assertIn('id', table.column_names)
        self.assertIn('name', table.column_names)

        connector.close()


class TestTemplateGeneration(unittest.TestCase):
    """Test template generation with ERD diagram"""

    @classmethod
    def setUpClass(cls):
        """Set up test database and temporary directory"""
        cls.temp_dir = tempfile.mkdtemp(prefix="pystoorm_template_test_")
        cls.test_db_path = os.path.join(cls.temp_dir, "test.db")
        cls.output_dir = os.path.join(cls.temp_dir, "generated")

        # Create test database with sample tables
        cls._create_test_database(cls.test_db_path)

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary files"""
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)

    @staticmethod
    def _create_test_database(db_path):
        """Create a test SQLite database with sample schema"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)

        # Create posts table with foreign key
        cursor.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Create comments table with foreign keys
        cursor.execute("""
            CREATE TABLE comments (
                id INTEGER PRIMARY KEY,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def is_valid_graphviz(dot_content):
        """Check if content is valid Graphviz DOT format.

        Args:
            dot_content: Content to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        # Basic checks for valid Graphviz syntax
        if not dot_content.strip():
            return False, "Empty content"

        # Must start with digraph or graph
        if not re.search(r'\b(digraph|graph)\b', dot_content):
            return False, "Missing digraph or graph declaration"

        # Must have opening brace
        if '{' not in dot_content:
            return False, "Missing opening brace"

        # Must have closing brace
        if '}' not in dot_content:
            return False, "Missing closing brace"

        # Basic bracket matching
        open_count = dot_content.count('{')
        close_count = dot_content.count('}')
        if open_count != close_count:
            return False, f"Mismatched braces: {open_count} open, {close_count} close"

        return True, None

    def test_erd_template_with_coordinator(self):
        """Test ERD template generation with Coordinator"""
        config = {
            'logging': {'level': 'INFO'},
            'connections': [{
                'connection': 'test_db',
                'database': self.test_db_path,
                'connector': 'database.sqliteconnector.SqliteConnector'
            }],
            'project_root': self.temp_dir,
            'output_dir': self.output_dir,
            'naming': {
                'primary_key': {'patterns': ['^id$']},
                'table': {'case_in_code': 'PascalCase'}
            },
            'style': {
                'class_naming': {'case': 'PascalCase', 'suffix': 'Model'}
            },
            'attribute_hints': {
                'defaults': ['name', 'title'],
                'fallback': ['id']
            },
            'output': [
                {
                    'from': './pystoorm/templates/erd/graphviz.template',
                    'to': '${output_dir}/erd/[connection]_schema.dot',
                    'enabled': True,
                    'modus': 'schema'
                }
            ]
        }

        # Analyze database
        analyzer = Controller(config)
        analyzer.walk()

        # Verify schema was parsed
        self.assertIn('parsedSchema', config['connections'][0])
        schema = config['connections'][0]['parsedSchema']
        self.assertEqual(len(schema.table_names), 3)

        # Generate ERD diagram
        coordinator = Coordinator(config)
        coordinator.generate()

        # Verify output file was created
        expected_file = os.path.join(self.output_dir, 'erd', 'test_db_schema.dot')
        self.assertTrue(os.path.exists(expected_file), f"Expected file not found: {expected_file}")

        # Read and validate content
        with open(expected_file, 'r') as f:
            content = f.read()

        # Validate Graphviz syntax
        is_valid, error_msg = self.is_valid_graphviz(content)
        self.assertTrue(is_valid, f"Invalid Graphviz content: {error_msg}\n{content}")

    def test_graphviz_content_structure(self):
        """Test that generated Graphviz contains expected elements"""
        config = {
            'logging': {'level': 'INFO'},
            'connections': [{
                'connection': 'test_db',
                'database': self.test_db_path,
                'connector': 'database.sqliteconnector.SqliteConnector'
            }],
            'project_root': self.temp_dir,
            'output_dir': self.output_dir,
            'naming': {'primary_key': {'patterns': ['^id$']}},
            'style': {'class_naming': {'case': 'PascalCase', 'suffix': 'Model'}},
            'attribute_hints': {'defaults': ['name'], 'fallback': ['id']},
            'output': [
                {
                    'from': './pystoorm/templates/erd/graphviz.template',
                    'to': '${output_dir}/erd/schema.dot',
                    'enabled': True,
                    'modus': 'schema'
                }
            ]
        }

        analyzer = Controller(config)
        analyzer.walk()

        coordinator = Coordinator(config)
        coordinator.generate()

        # Read generated file
        output_file = os.path.join(self.output_dir, 'erd', 'schema.dot')
        with open(output_file, 'r') as f:
            content = f.read()

        # Check for table definitions
        self.assertIn('users', content, "Should contain 'users' table")
        self.assertIn('posts', content, "Should contain 'posts' table")
        self.assertIn('comments', content, "Should contain 'comments' table")

        # Check for column types
        self.assertIn('(PK)', content, "Should contain primary key indicator")
        self.assertIn('int', content, "Should contain column types")

        # Check for relationships
        self.assertIn('arrowhead=crow', content, "Should contain relationship arrows")

    def test_multiple_templates(self):
        """Test that multiple templates can be generated"""
        config = {
            'logging': {'level': 'INFO'},
            'connections': [{
                'connection': 'test_db',
                'database': self.test_db_path,
                'connector': 'database.sqliteconnector.SqliteConnector'
            }],
            'project_root': self.temp_dir,
            'output_dir': self.output_dir,
            'naming': {'primary_key': {'patterns': ['^id$']}},
            'style': {'class_naming': {'case': 'PascalCase'}},
            'attribute_hints': {'defaults': ['name']},
            'output': [
                {
                    'from': './pystoorm/templates/erd/graphviz.template',
                    'to': '${output_dir}/erd/database.dot',
                    'enabled': True,
                    'modus': 'schema'
                },
                {
                    'from': './pystoorm/templates/erd/graphviz.template',
                    'to': '${output_dir}/erd/database2.dot',
                    'enabled': True,
                    'modus': 'schema'
                }
            ]
        }

        analyzer = Controller(config)
        analyzer.walk()

        coordinator = Coordinator(config)
        coordinator.generate()

        # Both files should exist
        file1 = os.path.join(self.output_dir, 'erd', 'database.dot')
        file2 = os.path.join(self.output_dir, 'erd', 'database2.dot')

        self.assertTrue(os.path.exists(file1), "First template should generate file")
        self.assertTrue(os.path.exists(file2), "Second template should generate file")

    def test_disabled_template_not_generated(self):
        """Test that disabled templates are not generated"""
        config = {
            'logging': {'level': 'INFO'},
            'connections': [{
                'connection': 'test_db',
                'database': self.test_db_path,
                'connector': 'database.sqliteconnector.SqliteConnector'
            }],
            'project_root': self.temp_dir,
            'output_dir': self.output_dir,
            'naming': {'primary_key': {'patterns': ['^id$']}},
            'style': {'class_naming': {'case': 'PascalCase'}},
            'attribute_hints': {'defaults': ['name']},
            'output': [
                {
                    'from': './pystoorm/templates/erd/graphviz.template',
                    'to': '${output_dir}/erd/disabled.dot',
                    'enabled': False,  # Disabled!
                    'modus': 'schema'
                }
            ]
        }

        analyzer = Controller(config)
        analyzer.walk()

        coordinator = Coordinator(config)
        coordinator.generate()

        # File should NOT exist
        output_file = os.path.join(self.output_dir, 'erd', 'disabled.dot')
        self.assertFalse(os.path.exists(output_file), "Disabled template should not generate file")


if __name__ == '__main__':
    unittest.main()
