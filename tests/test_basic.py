import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pystoorm.database.schema import Schema
from pystoorm.database.table import Table
from pystoorm.database.column import Column


class TestSchema(unittest.TestCase):
    def test_schema_initialization(self):
        """Test Schema class initialization"""
        table_names = ['users', 'posts']
        schema = Schema('test_db', table_names)
        self.assertEqual(schema.name, 'test_db')
        self.assertEqual(schema.table_names, table_names)
        self.assertEqual(schema.tables, {})

    def test_schema_mutable_defaults(self):
        """Test that Schema instances don't share tables dict"""
        schema1 = Schema('db1', [])
        schema2 = Schema('db2', [])
        schema1.tables['test'] = 'value1'
        self.assertNotIn('test', schema2.tables)


class TestTable(unittest.TestCase):
    def test_table_initialization(self):
        """Test Table class initialization"""
        column_names = ['id', 'name', 'email']
        table = Table('users', 'standard', column_names)
        self.assertEqual(table.name, 'users')
        self.assertEqual(table.type, 'standard')
        self.assertEqual(table.column_names, column_names)
        self.assertEqual(table.columns, {})

    def test_table_mutable_defaults(self):
        """Test that Table instances don't share columns dict"""
        table1 = Table('table1', 'type', [])
        table2 = Table('table2', 'type', [])
        table1.columns['test'] = 'value1'
        self.assertNotIn('test', table2.columns)


class TestColumn(unittest.TestCase):
    def test_column_initialization(self):
        """Test Column class initialization"""
        column = Column('id', 'INT', False, 'PRI', None, 11)
        self.assertEqual(column.name, 'id')
        self.assertEqual(column.type, 'INT')
        self.assertFalse(column.nullable)
        self.assertEqual(column.key, 'PRI')
        self.assertIsNone(column.default)
        self.assertEqual(column.length, 11)
        self.assertEqual(column.ref_to, [])
        self.assertEqual(column.ref_from, [])

    def test_column_references(self):
        """Test Column reference tracking"""
        from pystoorm.database.reference import Reference
        column = Column('user_id', 'INT', False, 'MUL', None, 11)
        ref = Reference('public', 'users', 'id')
        column.add_ref_to(ref)
        self.assertEqual(len(column.ref_to), 1)
        self.assertEqual(column.ref_to[0].ref_table, 'users')


if __name__ == '__main__':
    unittest.main()
