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
        return schema
