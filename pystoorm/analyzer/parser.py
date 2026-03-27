#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""connects to a db"""
__author__ = "Harald Stowasser"


# CREATE USER 'pystoorm'@'localhost' IDENTIFIED BY 'pystoormpw';

class Parser(object):
    con = None

    def __init__(self, connector):
        self.con = connector

    def parse(self):
        schema = self.con.get_schema()
        print(schema.name + " -> " + str(schema.table_names))
        for table_name in schema.table_names:
            table = self.con.get_table(table_name)
            schema.tables[table_name] = table
            print("  " + table.name + " -> " + str(table.column_names))
            for column_name in table.column_names:
                column = self.con.get_column(table_name, column_name)
                table.columns[column_name] = column
                print("    " + column.name + " -> " + str(column.type))
            # Load relationships (foreign keys)
            if hasattr(self.con, '_get_foreign_keys'):
                table.relationships = self.con._get_foreign_keys(table_name)
                # Mark columns that are foreign keys
                for rel in table.relationships:
                    local_col = rel.get('local_column')
                    if local_col in table.columns:
                        table.columns[local_col].is_foreign_key = True
        return schema
