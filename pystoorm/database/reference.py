#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Database reference/foreign key"""
__author__ = "Harald Stowasser"


class Reference(object):
    def __init__(self, ref_schema, ref_table, ref_column):
        self.ref_schema = ref_schema
        self.ref_table = ref_table
        self.ref_column = ref_column

    def __repr__(self):
        return f"Reference({self.ref_schema}.{self.ref_table}.{self.ref_column})"
