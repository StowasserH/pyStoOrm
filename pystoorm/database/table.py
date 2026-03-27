#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""connects to a db"""
__author__ = "Harald Stowasser"


# CREATE USER 'pystoorm'@'localhost' IDENTIFIED BY 'pystoormpw';

class Table(object):
    def __init__(self, name, type, column_names):
        self.name = name
        self.type = type
        self.column_names = column_names
        self.columns = {}
        self.relationships = []  # List of foreign key relationships
