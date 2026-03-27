#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""connects to a db"""
__author__ = "Harald Stowasser"


# CREATE USER 'pystoorm'@'localhost' IDENTIFIED BY 'pystoormpw';

class Column(object):
    def __init__(self, name, type, nullable, key, default, length):
        self.name = name
        self.type = type
        self.nullable = nullable
        self.key = key
        self.default = default
        self.length = length
        self.ref_to = []
        self.ref_from = []
        self.is_foreign_key = False  # Flag to indicate this column is a foreign key

    def add_ref_to(self, ref):
        self.ref_to.append(ref)

    def add_ref_from(self, ref):
        self.ref_from.append(ref)
