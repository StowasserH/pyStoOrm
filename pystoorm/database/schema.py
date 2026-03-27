#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""connects to a db"""
__author__ = "Harald Stowasser"


# CREATE USER 'pystoorm'@'localhost' IDENTIFIED BY 'pystoormpw';

class Schema(object):
    def __init__(self, name, table_names):
        self.name = name
        self.table_names = table_names
        self.tables = {}

