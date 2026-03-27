#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""connects to a db"""
__author__ = "Harald Stowasser"
from clint.textui import puts, colored
from .connector import Connector
from .table import Table
from .column import Column
from .schema import Schema


# CREATE USER 'pystoorm'@'localhost' IDENTIFIED BY 'pystoormpw';

class NullConnector(Connector):
    def connect(self):
        puts(colored.green('connecting to nothing'))

    def get_schema(self):
        return Schema("test", ("users", "dummy"))

    def get_table(self, table):
        return Table(table, "flat", ("id", "users", "pass"))

    def get_column(self, table, column):
        # Type, Null, Key, Default, length
        return Column(column, "int", True, "pri", "Null", 11)
